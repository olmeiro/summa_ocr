# CHANGELOG

## 2026-11-19 — 01-esqueleto-api

### Added
- `repo_agente_conversacional/` es una API FastAPI que arranca con la fábrica `create_app` (`uvicorn --factory app.main:create_app`):
  - `/health` devuelve el ambiente. `/ready` responde 503 hasta que termina el arranque. Los dos cuelgan de la raíz, para las sondas de Container Apps;
  - `APP_ENVIRONMENT` (`local`, `dev` o `prod`) es obligatoria, y la app no lee `.env`;
  - `/docs`, `/redoc` y `/openapi.json` solo existen con `APP_DOCS=true`.
- Imagen Docker sobre `python:3.12-slim`, sin secretos. Corre como `appuser`, sin permiso de escritura sobre su código, y su `HEALTHCHECK` llama a `/health`.
- El gate de la raíz cubre `app/` y `tests/` del agente: ruff con `FAST`, `ASYNC` y `S`, y mypy estricto.

### Notes
- Probado con uvicorn en local y con Docker Desktop en la máquina de la persona.
- La salud vive fuera de `api/v1/`, en contra de [[tech-stack]] §3. Queda pendiente un replanning para corregir la Constitución.
