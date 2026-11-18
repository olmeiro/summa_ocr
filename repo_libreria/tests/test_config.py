"""Carga de configuración: referencias resueltas tras parsear y errores sin valores secretos."""

import traceback
from pathlib import Path

import pytest
import summa_ai_framework.config.loader as loader
from summa_ai_framework.config import (
    ConfigError,
    ConfigModel,
    SecretRef,
    SummaConfig,
    load_config,
)
from summa_ai_framework.security import EnvSecretProvider, SecretError

SECRETO = "s3cr3t-no-debe-verse"


class Servicio(ConfigModel):
    endpoint: str
    api_key: SecretRef
    timeout: int = 30


class Fuente(ConfigModel):
    name: str
    token: SecretRef


class PlantillaConfig(SummaConfig):
    """Como la extendería una plantilla con sus secciones propias."""

    service: Servicio | None = None
    sources: list[Fuente] = []
    note: str = ""


def yaml_en(tmp_path: Path, texto: str) -> Path:
    ruta = tmp_path / "config_dev.yaml"
    ruta.write_text(texto, encoding="utf-8")
    return ruta


def cargar_con_error(ruta: Path) -> ConfigError:
    with pytest.raises(ConfigError) as error:
        load_config(ruta, PlantillaConfig)
    return error.value


def sin_excepcion_original(error: ConfigError) -> bool:
    """La excepción de origen (pydantic, yaml, unicode) puede llevar valores: no debe viajar."""
    return error.__cause__ is None and (error.__context__ is None or error.__suppress_context__)


SERVICIO = "service:\n  endpoint: https://x.openai.azure.com/\n  api_key: ${CLAVE}\n"


def test_resuelve_la_referencia_y_no_la_muestra(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CLAVE", SECRETO)
    config = load_config(str(yaml_en(tmp_path, SERVICIO)), PlantillaConfig)
    assert config.service is not None
    assert config.service.api_key.get_secret_value() == SECRETO
    for salida in (repr(config), str(config), str(config.model_dump()), config.model_dump_json()):
        assert SECRETO not in salida


def test_un_secreto_con_sintaxis_yaml_llega_literal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    raro = "a: b # c\n- d \"e\" 'f'"
    monkeypatch.setenv("CLAVE", raro)
    config = load_config(yaml_en(tmp_path, SERVICIO + "note: intacta\n"), PlantillaConfig)
    assert config.service is not None
    assert config.service.api_key.get_secret_value() == raro
    assert config.service.endpoint == "https://x.openai.azure.com/"
    assert config.service.timeout == 30
    assert config.note == "intacta"


@pytest.mark.parametrize(
    ("texto", "entorno", "esperado"),
    [
        (SERVICIO, {}, "service.api_key: no se encontró el secreto 'CLAVE'"),
        (SERVICIO, {"CLAVE": ""}, "service.api_key: no se encontró el secreto 'CLAVE'"),
        (
            "service:\n  endpoint: ${CLAVE}\n  api_key: ${CLAVE}\n",
            {"CLAVE": SECRETO},
            "service.endpoint: Input should be a valid string (recibe una referencia a secreto: "
            "el campo debe declararse SecretRef)",
        ),
        (
            f"service:\n  endpoint: https://x\n  api_key: {SECRETO}\n",
            {},
            "service.api_key: Value error, debe ser una referencia a secreto",
        ),
        (
            SERVICIO + "  timeout: ${CLAVE}\n",
            {"CLAVE": SECRETO},
            "service.timeout: Input should be a valid integer (recibe una referencia a secreto",
        ),
    ],
    ids=["ausente", "vacio", "en-campo-str", "en-claro", "en-campo-int"],
)
def test_los_errores_no_muestran_el_secreto(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    texto: str,
    entorno: dict[str, str],
    esperado: str,
) -> None:
    monkeypatch.delenv("CLAVE", raising=False)
    for nombre, valor in entorno.items():
        monkeypatch.setenv(nombre, valor)
    error = cargar_con_error(yaml_en(tmp_path, texto))
    assert esperado in str(error)
    assert sin_excepcion_original(error)
    assert SECRETO not in "".join(traceback.format_exception(error))


def test_una_referencia_parcial_es_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CLAVE", SECRETO)
    error = cargar_con_error(yaml_en(tmp_path, "note: Bearer ${CLAVE}\n"))
    assert "note: una referencia a secreto debe ocupar el valor completo" in str(error)


@pytest.mark.parametrize(
    ("texto", "esperado"),
    [
        (None, "No se pudo leer la configuración"),
        (b"note: caf\xe9\n", "el archivo no está en UTF-8"),  # cp1252, habitual en Windows
        ("note: [1, 2\n", "YAML inválido"),
        ("note: 2024-02-30\n", "YAML inválido"),  # PyYAML lanza ValueError, no YAMLError
        ("note: " + "[" * 3000 + "]" * 3000 + "\n", "YAML inválido"),  # RecursionError al parsear
        ("- a\n- b\n", "la raíz del YAML debe ser un mapa"),
        ("solo-texto\n", "la raíz del YAML debe ser un mapa"),
        ("note: &a [*a]\n", "el YAML tiene alias circulares"),
        ("otra: 1\n", "- otra: Extra inputs are not permitted"),
        (
            "secrets:\n  provider: aws_secrets\n",
            "- secrets.provider: Input should be 'env' or 'azure_key_vault'",
        ),
        (
            "secrets:\n  provider: azure_key_vault\n",
            "- secrets: Value error, vault_url es obligatoria con provider: azure_key_vault",
        ),
        (
            "secrets:\n  provider: azure_key_vault\n  vault_url: kvema\n",
            "- secrets.vault_url: Input should be a valid URL",
        ),
    ],
    ids=[
        "inexistente",
        "no-utf8",
        "mal-formado",
        "fecha-imposible",
        "anidamiento-profundo",
        "raiz-lista",
        "raiz-escalar",
        "alias-circular",
        "clave-desconocida",
        "proveedor-no-soportado",
        "key-vault-sin-url",
        "key-vault-url-invalida",
    ],
)
def test_archivos_invalidos(tmp_path: Path, texto: str | bytes | None, esperado: str) -> None:
    ruta = tmp_path / "config_dev.yaml"
    if isinstance(texto, bytes):
        ruta.write_bytes(texto)
    elif texto is not None:
        ruta.write_text(texto, encoding="utf-8")
    error = cargar_con_error(ruta)
    assert esperado in str(error)
    assert str(ruta) in str(error)
    assert sin_excepcion_original(error)


@pytest.mark.parametrize("texto", ["", "# solo comentarios\n"], ids=["cero-bytes", "comentarios"])
def test_un_archivo_vacio_da_los_valores_por_defecto(tmp_path: Path, texto: str) -> None:
    config = load_config(yaml_en(tmp_path, texto), SummaConfig)
    assert config.secrets.provider == "env"


LISTA = "sources:\n  - name: a\n    token: ${T1}\n  - name: b\n    token: ${T2}\n"


def test_resuelve_referencias_en_listas(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("T1", "uno")
    monkeypatch.setenv("T2", "dos")
    config = load_config(yaml_en(tmp_path, LISTA), PlantillaConfig)
    assert [f.token.get_secret_value() for f in config.sources] == ["uno", "dos"]


def test_la_ubicacion_incluye_el_indice(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("T1", "uno")
    monkeypatch.delenv("T2", raising=False)
    error = cargar_con_error(yaml_en(tmp_path, LISTA))
    assert "sources[1].token: no se encontró el secreto 'T2'" in str(error)


VAULT_URL = "https://kv-prueba.vault.azure.net/"
KEY_VAULT = f"secrets:\n  provider: azure_key_vault\n  vault_url: {VAULT_URL}\n" + SERVICIO


def test_con_key_vault_usa_la_vault_url_del_yaml(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    creados: list[str] = []

    class KeyVaultDoble:
        def __init__(self, vault_url: str) -> None:
            creados.append(vault_url)

        def get_secret(self, name: str) -> str:
            return SECRETO

    monkeypatch.setattr(loader, "KeyVaultSecretProvider", KeyVaultDoble)
    config = load_config(yaml_en(tmp_path, KEY_VAULT), PlantillaConfig)
    assert creados == [VAULT_URL]
    assert config.service is not None
    assert config.service.api_key.get_secret_value() == SECRETO


class ProveedorQueSeEvaluaFalso(EnvSecretProvider):
    """Un proveedor válido aunque `bool()` dé False (p. ej. uno basado en un dict vacío)."""

    def __bool__(self) -> bool:
        return False


@pytest.mark.parametrize(
    "proveedor",
    [EnvSecretProvider(), ProveedorQueSeEvaluaFalso()],
    ids=["entorno", "se-evalua-falso"],
)
def test_el_proveedor_inyectado_sustituye_al_del_yaml(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, proveedor: EnvSecretProvider
) -> None:
    class NoDebeConstruirse:
        def __init__(self, vault_url: str) -> None:
            raise AssertionError("con provider inyectado no se construye Key Vault")

    monkeypatch.setattr(loader, "KeyVaultSecretProvider", NoDebeConstruirse)
    monkeypatch.setenv("CLAVE", SECRETO)
    config = load_config(yaml_en(tmp_path, KEY_VAULT), PlantillaConfig, provider=proveedor)
    assert config.service is not None
    assert config.service.api_key.get_secret_value() == SECRETO


def test_un_fallo_de_acceso_es_config_error_sin_valores(tmp_path: Path) -> None:
    class PermisoParcial:
        """Resuelve CLAVE y falla con OTRA: el error llega con un secreto ya leído en memoria."""

        def get_secret(self, name: str) -> str:
            if name == "CLAVE":
                return SECRETO
            raise SecretError(f"No se pudo leer el secreto '{name}' de Key Vault (Forbidden)")

    texto = KEY_VAULT + "sources:\n  - name: a\n    token: ${OTRA}\n"
    with pytest.raises(ConfigError) as error:
        load_config(yaml_en(tmp_path, texto), PlantillaConfig, provider=PermisoParcial())
    esperado = "sources[0].token: No se pudo leer el secreto 'OTRA' de Key Vault (Forbidden)"
    assert esperado in str(error.value)
    assert sin_excepcion_original(error.value)
    assert SECRETO not in "".join(traceback.format_exception(error.value))
