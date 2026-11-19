# 01 — esqueleto-api — Plan

> Cómo se construye la feature. No repite los criterios de requirements.md.

## Enfoque

1. **`AppSettings(BaseSettings)`**, con `env_prefix="APP_"` y sin `env_file`:
   - `environment: Literal["local", "dev", "prod"]`, obligatoria, para que un despliegue sin ambiente falle al arrancar en vez de parecer `local`;
   - `docs: bool = False`.

   La app no lee `.env`. En local, la variable se pone en la terminal, y Docker la recibe con `-e`.
2. **`create_app(settings: AppSettings | None = None) -> FastAPI`**:
   - lee `AppSettings()` si no la recibe;
   - si `docs` es falso, pone `docs_url`, `redoc_url` y `openapi_url` a `None`;
   - registra el router de salud;
   - usa `lifespan`, que marca `app.state.listo = True` al arrancar.

   En la 02 el arranque cargará la configuración.
3. **Salud** (`app/api/health.py`, en la raíz y fuera de `/api/v1`, porque los usan las sondas):
   - `/health` devuelve `{"status": "ok", "environment": ...}`;
   - `/ready` devuelve 200 con `{"status": "ready"}` si `app.state.listo`, y 503 si no.
4. **Docker**:
   - `python:3.12-slim`, `PYTHONDONTWRITEBYTECODE` y `PYTHONUNBUFFERED`;
   - `pip install -r requirements.txt` y `COPY app/`;
   - usuario `appuser` sin privilegios, `EXPOSE 8000`;
   - `HEALTHCHECK` con `python -c` y `urllib`, sin instalar curl;
   - `CMD ["uvicorn", "--factory", "app.main:create_app", "--host", "0.0.0.0", "--port", "8000"]`.

   `.dockerignore` deja fuera `tests/`, `specs/`, `__pycache__/` y `.env*`.
5. **Gate de la raíz**:
   - mypy y pytest con `repo_agente_conversacional/app` y `tests`;
   - `pythonpath` con `repo_agente_conversacional`, para importar `app`;
   - `requirements-dev.txt` incluye `-r repo_agente_conversacional/requirements.txt` y `httpx`, que necesita `TestClient`.

## Archivos a crear o modificar

| Archivo | Cambio |
|---|---|
| `repo_agente_conversacional/app/__init__.py`, `app/api/__init__.py`, `app/core/__init__.py` | Nuevos, solo docstring |
| `repo_agente_conversacional/app/main.py` | Nuevo: `create_app` y `lifespan` |
| `repo_agente_conversacional/app/core/settings.py` | Nuevo: `AppSettings` |
| `repo_agente_conversacional/app/api/health.py` | Nuevo: `/health` y `/ready` |
| `repo_agente_conversacional/tests/test_api_salud.py` | Nuevo: salud, documentación, ajustes y fábrica |
| `repo_agente_conversacional/requirements.txt` | Nuevo: `fastapi`, `uvicorn` y `pydantic-settings`, con rango de versiones |
| `repo_agente_conversacional/Dockerfile`, `.dockerignore` | Nuevos |
| `pyproject.toml` (raíz) | mypy, pytest (`testpaths` y `pythonpath`) y `per-file-ignores` de los tests |
| `requirements-dev.txt` (raíz) | `-r repo_agente_conversacional/requirements.txt` y `httpx` |
| `AGENTS.md` | "Arquitectura" y "Ejecutar" (uvicorn y Docker) |
| `repo_agente_conversacional/specs/roadmap.md`, `progress.md` | Estado y continuidad |

## Secuencia

1. **Spec**, con la 01 en `in_progress`. Commit `docs(specs): define la spec de 01-esqueleto-api`.
2. **App y gate**: settings, fábrica, salud, tests y dependencias. Commit `feat(api): esqueleto FastAPI con endpoints de salud`.
3. **Docker**: `Dockerfile` y `.dockerignore`, construidos y ejecutados en local cuando haya Docker. Commit `feat(api): imagen Docker sin privilegios con healthcheck`.
4. **Documentación y cierre**: `AGENTS.md`, evidencia, revisor de Claude, PR con revisor de CI, y el cierre dentro del PR **antes** del merge.

## Dependencias

- Ninguna feature previa. La librería todavía no se usa; entra en la 02.
- Nuevas: `fastapi>=0.115,<1`, `uvicorn>=0.30,<1` y `pydantic-settings>=2.4,<3` (ejecución), y `httpx` (desarrollo, para `TestClient`).
- Docker en la máquina de la persona para CA-6. Hoy no está instalado (2026-11-18).

## Riesgos

- **Docker no disponible**: CA-6 queda pendiente. → El resto se valida con uvicorn en local; el `Dockerfile` lo revisan los revisores.
- **`pydantic-settings` lee variables `APP_*` del entorno de quien ejecuta los tests.** → Los tests construyen `AppSettings` explícitamente o con `monkeypatch`.
- **El nombre de paquete `app` es genérico.** → Ningún otro proyecto del repo usa `app`. Si choca al mover el código a su repo, se renombra allí.

## No tocar

- `repo_libreria/` y `repo_worklow/`.
- El harness de la raíz (`scripts/`, `.claude/`, `.github/workflows/`, `tests/`). `pyproject.toml`, `requirements-dev.txt` y `AGENTS.md` solo cambian como dice la tabla.
- Los `.env*`. La app no lee `.env`, y `.env.template` no cambia porque las variables `APP_*` las pone quien ejecuta.
- La Constitución del agente, salvo el estado en [[roadmap]] y [[progress]].
