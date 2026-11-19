"""Esqueleto de la API: salud, documentación apagada por defecto y ajustes del entorno."""

import importlib
import sys

import pytest
from app.core.settings import AppSettings
from app.main import create_app
from fastapi.testclient import TestClient
from pydantic import ValidationError


@pytest.fixture(autouse=True)
def entorno_limpio(monkeypatch: pytest.MonkeyPatch) -> None:
    """Las variables APP_* de quien ejecuta los tests no cambian los valores por defecto."""
    for nombre in ("APP_ENVIRONMENT", "APP_DOCS"):
        monkeypatch.delenv(nombre, raising=False)


def local() -> AppSettings:
    return AppSettings(environment="local")


def test_health_responde_el_ambiente() -> None:
    with TestClient(create_app(local())) as cliente:
        respuesta = cliente.get("/health")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"status": "ok", "environment": "local"}


def test_ready_tras_arrancar() -> None:
    with TestClient(create_app(local())) as cliente:  # el contexto ejecuta el lifespan
        respuesta = cliente.get("/ready")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"status": "ready"}


def test_ready_antes_de_arrancar_es_503() -> None:
    respuesta = TestClient(create_app(local())).get("/ready")  # sin contexto: sin lifespan
    assert respuesta.status_code == 503


@pytest.mark.parametrize("ruta", ["/docs", "/redoc", "/openapi.json"])
def test_documentacion_apagada_por_defecto(ruta: str) -> None:
    assert TestClient(create_app(local())).get(ruta).status_code == 404


@pytest.mark.parametrize("ruta", ["/docs", "/redoc", "/openapi.json"])
def test_documentacion_con_app_docs(ruta: str) -> None:
    app = create_app(AppSettings(environment="local", docs=True))
    assert TestClient(app).get(ruta).status_code == 200


def test_lee_los_ajustes_del_entorno(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENVIRONMENT", "dev")
    monkeypatch.setenv("APP_DOCS", "true")
    with TestClient(create_app()) as cliente:
        assert cliente.get("/health").json()["environment"] == "dev"
        assert cliente.get("/docs").status_code == 200


@pytest.mark.parametrize(
    "valor", [None, "staging", "PROD"], ids=["ausente", "staging", "mayusculas"]
)
def test_ambiente_obligatorio_y_valido(monkeypatch: pytest.MonkeyPatch, valor: str | None) -> None:
    if valor is not None:
        monkeypatch.setenv("APP_ENVIRONMENT", valor)
    with pytest.raises(ValidationError, match="environment"):
        create_app()


def test_importar_main_no_lee_el_entorno() -> None:
    sys.modules.pop("app.main", None)
    importlib.import_module("app.main")  # sin APP_ENVIRONMENT no falla: no crea la app
