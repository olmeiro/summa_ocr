"""Fábrica de la app FastAPI. Importar este módulo no crea la app ni lee el entorno.

Arranque: uvicorn --factory app.main:create_app
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import health
from app.core.settings import AppSettings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Arranque y apagado; la feature 02 cargará aquí la configuración."""
    app.state.listo = True
    yield
    app.state.listo = False


def create_app(settings: AppSettings | None = None) -> FastAPI:
    """Crea la app con los ajustes dados o con los del entorno (variables APP_*)."""
    if settings is None:
        settings = AppSettings()  # type: ignore[call-arg]  # environment sale del entorno
    docs = settings.docs
    app = FastAPI(
        title="Agente conversacional de SUMMA",
        lifespan=lifespan,
        docs_url="/docs" if docs else None,
        redoc_url="/redoc" if docs else None,
        openapi_url="/openapi.json" if docs else None,
    )
    app.state.settings = settings
    app.state.listo = False
    app.include_router(health.router)
    return app
