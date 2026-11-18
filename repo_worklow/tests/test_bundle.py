"""Bundle del workflow: estructura, versión de la librería en un solo lugar y ausencia de secretos.

Lee los YAML con PyYAML: no necesita el CLI de Databricks ni acceso a Azure.
"""

import re
import tomllib
from pathlib import Path
from typing import Any

import pytest
import yaml

WORKFLOW = Path(__file__).resolve().parents[1]
RECURSOS = WORKFLOW / "resources"
BUNDLE: dict[str, Any] = yaml.safe_load((WORKFLOW / "databricks.yml").read_text(encoding="utf-8"))
RECURSOS_YAML: dict[str, Any] = yaml.safe_load(
    (RECURSOS / "workflow.yml").read_text(encoding="utf-8")
)
JOB: dict[str, Any] = RECURSOS_YAML["resources"]["jobs"]["summa_workflow"]
VARIABLES = {nombre: v["default"] for nombre, v in BUNDLE["variables"].items()}

CLAVE_SENSIBLE = re.compile(r"secret|password|passwd|token|api_key", re.IGNORECASE)
URL_CON_CREDENCIAL = re.compile(r"://[^/\s:@]+:[^/\s@]+@")


def _literal(valor: object) -> bool:
    """Un valor escrito tal cual; `${var.x}` y `{{secrets/...}}` son referencias, no secretos."""
    return isinstance(valor, str) and bool(valor) and not valor.startswith(("${", "{{secrets/"))


def secretos(datos: object, ruta: str = "") -> list[str]:
    """Ubicaciones del YAML con un secreto o un host de workspace escritos en el bundle."""
    if isinstance(datos, list):
        return [h for i, v in enumerate(datos) for h in secretos(v, f"{ruta}[{i}]")]
    if isinstance(datos, str):
        return [f"{ruta}: URL con credenciales"] if URL_CON_CREDENCIAL.search(datos) else []
    if not isinstance(datos, dict):
        return []
    hallazgos = []
    for clave, valor in datos.items():
        sub = f"{ruta}.{clave}" if ruta else str(clave)
        if clave == "host" and ruta.endswith("workspace"):
            hallazgos.append(f"{sub}: host del workspace en el bundle")
        elif CLAVE_SENSIBLE.search(str(clave)) and (
            _literal(valor) or (isinstance(valor, dict) and _literal(valor.get("default")))
        ):
            hallazgos.append(f"{sub}: valor literal en una clave sensible")
        hallazgos += secretos(valor, sub)
    return hallazgos


def test_targets_dev_y_prod_sin_host() -> None:
    targets = BUNDLE["targets"]
    assert set(targets) == {"dev", "prod"}
    assert targets["dev"]["mode"] == "development" and targets["dev"]["default"] is True
    assert targets["prod"]["mode"] == "production"
    assert all("host" not in t.get("workspace", {}) for t in targets.values())


def test_cluster_efimero_de_un_nodo_con_dbr_18() -> None:
    (cluster,) = JOB["job_clusters"]
    nuevo = cluster["new_cluster"]
    assert nuevo["spark_version"] == "${var.spark_version}"
    assert VARIABLES["spark_version"] == "18.x-scala2.13"
    assert nuevo["node_type_id"] == "${var.node_type_id}"
    assert VARIABLES["node_type_id"] == "Standard_D4ds_v5"
    assert nuevo["num_workers"] == 0
    assert nuevo["spark_conf"]["spark.databricks.cluster.profile"] == "singleNode"


def test_trigger_semanal_pausado_en_dev_y_activo_en_prod() -> None:
    assert JOB["schedule"] == {
        "quartz_cron_expression": "${var.trigger_cron}",
        "timezone_id": "${var.trigger_zona}",
        "pause_status": "${var.trigger_pausa}",
    }
    assert VARIABLES["trigger_cron"] == "0 0 2 ? * MON"
    assert VARIABLES["trigger_zona"] == "America/Bogota"
    pausa = {nombre: t["variables"]["trigger_pausa"] for nombre, t in BUNDLE["targets"].items()}
    assert pausa == {"dev": "PAUSED", "prod": "UNPAUSED"}


def test_la_tarea_de_humo_apunta_a_un_script_existente() -> None:
    (tarea,) = JOB["tasks"]
    assert tarea["task_key"] == "s00_humo"
    assert (RECURSOS / tarea["spark_python_task"]["python_file"]).resolve().is_file()


def test_version_de_la_libreria_en_un_solo_lugar() -> None:
    pyproject = WORKFLOW.parent / "repo_libreria" / "pyproject.toml"
    version = tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"]["version"]
    assert VARIABLES["libreria_version"] == version
    (tarea,) = JOB["tasks"]
    wheel = "../../repo_libreria/dist/summa_ai_framework-${var.libreria_version}-py3-none-any.whl"
    assert tarea["libraries"] == [{"whl": wheel}]
    textos = [
        p.read_text(encoding="utf-8")
        for p in [WORKFLOW / "databricks.yml", *RECURSOS.glob("*.yml")]
    ]
    assert sum(texto.count(version) for texto in textos) == 1  # solo el default de la variable


def test_el_bundle_real_no_tiene_secretos() -> None:
    assert secretos(BUNDLE) == []
    assert secretos(RECURSOS_YAML) == []


@pytest.mark.parametrize(
    ("bundle", "esperado"),
    [
        (
            {"targets": {"dev": {"workspace": {"host": "https://adb-1.azuredatabricks.net"}}}},
            "host",
        ),
        ({"spark_env_vars": {"AZURE_CLIENT_SECRET": "abc"}}, "AZURE_CLIENT_SECRET"),
        ({"variables": {"api_token": {"default": "xyz"}}}, "api_token"),
        ({"env": {"PIP_EXTRA_INDEX_URL": "https://build:clave@pkgs.dev.azure.com/x"}}, "URL"),
    ],
    ids=["host", "clave-secreta", "variable-token", "url-con-credencial"],
)
def test_el_comprobador_detecta_cada_secreto(bundle: dict[str, Any], esperado: str) -> None:
    (hallazgo,) = secretos(bundle)
    assert esperado in hallazgo


def test_las_referencias_no_son_secretos() -> None:
    assert secretos({"env": {"AZURE_CLIENT_SECRET": "{{secrets/kv/cliente}}"}}) == []
    assert secretos({"variables": {"api_token": {"default": "${var.otra}"}}}) == []
