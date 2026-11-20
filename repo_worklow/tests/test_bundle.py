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

CLAVE_SENSIBLE = re.compile(
    r"secret|password|passwd|token|api_key|account\.key", re.IGNORECASE
)  # account.key: fs.azure.account.key.* en spark_conf
# Cualquier userinfo en una URL: usuario:clave@, :token@ o token@ (como el token de un feed)
URL_CON_CREDENCIAL = re.compile(r"://[^/\s@]*@")
REFERENCIA = re.compile(r"\$\{[^}]+\}|\{\{secrets/[^}]+\}\}")


def _literal(valor: object) -> bool:
    """Un valor escrito tal cual. Solo una referencia completa (`${var.x}` o `{{secrets/...}}`)
    no lo es: `${var.x}abc` lleva un literal pegado."""
    if isinstance(valor, bool) or valor is None:
        return False
    if isinstance(valor, int | float):
        return True
    return isinstance(valor, str) and bool(valor) and not REFERENCIA.fullmatch(valor)


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


def test_tareas_en_serverless_sin_cluster() -> None:
    assert "job_clusters" not in JOB  # DEC-002
    (entorno,) = JOB["environments"]
    assert entorno["spec"]["environment_version"] == "${var.environment_version}"
    assert VARIABLES["environment_version"] == "6"
    for tarea in JOB["tasks"]:
        assert tarea["environment_key"] == entorno["environment_key"]
        assert not {"job_cluster_key", "new_cluster", "existing_cluster_id"} & tarea.keys()


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
    (entorno,) = JOB["environments"]
    wheel = "../../repo_libreria/dist/summa_ai_framework-${var.libreria_version}-py3-none-any.whl"
    assert entorno["spec"]["dependencies"] == [wheel]
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
        ({"env": {"PIP_EXTRA_INDEX_URL": "https://:pat@pkgs.dev.azure.com/x"}}, "URL"),
        ({"env": {"PIP_EXTRA_INDEX_URL": "https://pat@pkgs.dev.azure.com/x"}}, "URL"),
        ({"env": {"DB_PASSWORD": 12345}}, "DB_PASSWORD"),
        ({"env": {"AZURE_CLIENT_SECRET": "${var.prefijo}clave"}}, "AZURE_CLIENT_SECRET"),
        (
            {"spark_conf": {"fs.azure.account.key.cuenta.dfs.core.windows.net": "clave"}},
            "account.key",
        ),
    ],
    ids=[
        "host",
        "clave-secreta",
        "variable-token",
        "url-con-credencial",
        "url-con-token-sin-usuario",
        "url-con-token-como-usuario",
        "clave-numerica",
        "referencia-con-literal",
        "account-key-de-storage",
    ],
)
def test_el_comprobador_detecta_cada_secreto(bundle: dict[str, Any], esperado: str) -> None:
    (hallazgo,) = secretos(bundle)
    assert esperado in hallazgo


def test_las_referencias_no_son_secretos() -> None:
    assert secretos({"env": {"AZURE_CLIENT_SECRET": "{{secrets/kv/cliente}}"}}) == []
    assert secretos({"variables": {"api_token": {"default": "${var.otra}"}}}) == []
    assert secretos({"env": {"PIP_INDEX_URL": "https://pypi.org/simple"}}) == []
