"""Salud: vida y disponibilidad para las sondas de Container Apps (tech-stack §4)."""

from fastapi import APIRouter, Request, Response, status

router = APIRouter(tags=["salud"])


@router.get("/health")
async def health(request: Request) -> dict[str, str]:
    """Vida: el proceso responde."""
    return {"status": "ok", "environment": request.app.state.settings.environment}


@router.get("/ready")
async def ready(request: Request, response: Response) -> dict[str, str]:
    """Disponibilidad: el arranque terminó y la app puede atender."""
    if not getattr(request.app.state, "listo", False):
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "starting"}
    return {"status": "ready"}
