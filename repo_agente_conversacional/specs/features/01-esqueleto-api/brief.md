# 01 — esqueleto-api — Brief

> Ficha ejecutiva: qué problema resuelve la feature y por qué ahora. Sin diseño técnico ni tareas.

## Problema

La plantilla del agente no tiene código. No hay API que arrancar, ni endpoints de salud para las validaciones posteriores al despliegue, ni imagen que publicar. Las features 02 a 10 (configuración, autenticación, sesiones, conversación, RAG y canal Teams) necesitan una app FastAPI donde colgarse.

La base de referencia trae un esqueleto, pero con valores por defecto inseguros:

- `debug` activo, y con él la documentación interactiva (`BaseRef/agent/app/core/settings.py:45-46`);
- CORS abierto con credenciales (`settings.py:72` y `main.py:43-45`);
- la app se crea al importar `main.py` y carga `.env` antes de cualquier import (`main.py:5-6`);
- la credencial del feed entra a la imagen como `ARG`, que queda en el historial de la imagen (`Dockerfile:6`).

## Por qué ahora

Es la primera feature del [[roadmap]] y no depende de nada. La persona la prioriza después de la 01 del workflow (2026-11-18). Es el paso previo a la 02, la primera prueba local de punta a punta del agente con la librería.

## Decisión de diseño

Decisiones de la persona del 2026-11-18:

- **Ubicación**: el código vive en `repo_agente_conversacional/`, como la librería y el workflow. El gate de la raíz cubre sus tests.
- **Documentación interactiva**: apagada por defecto. `APP_DOCS=true` la activa en local para explorar la API.
- **Docker**: la imagen se construye y se ejecuta en local con Docker. Mientras Docker no esté disponible en la máquina, ese criterio queda pendiente.

Además:

- **Valores de producción por defecto** ([[tech-stack]] §2): sin CORS, y la app no lee `.env`. Las variables llegan del entorno.
- **La app se crea con una fábrica**, `create_app()`, que uvicorn llama con `--factory`. Importar `app.main` no crea nada.

## Incluye

- `app/main.py`: `create_app(settings=None)` con el ciclo de vida, y la documentación solo si `APP_DOCS=true`.
- `app/core/settings.py`: `AppSettings` con prefijo `APP_`. `APP_ENVIRONMENT` es obligatoria (`local`, `dev` o `prod`) y `APP_DOCS` vale `false` por defecto.
- `app/api/health.py`:
  - `GET /health` (vida), con el estado y el ambiente;
  - `GET /ready` (disponibilidad), que responde 503 hasta que termina el arranque.
- `requirements.txt` (FastAPI, uvicorn y pydantic-settings), `Dockerfile` y `.dockerignore`.
- Tests del gate con `TestClient` y gate de la raíz extendido a `repo_agente_conversacional/`.
- `AGENTS.md`: "Arquitectura" y "Ejecutar".

## No incluye

- `config/config_<ambiente>.yaml`, `APP_CONFIG_PATH` y la librería: es la 02.
- Autenticación (03), sesiones (04), conversación (05) y el resto de features.
- Manejo global de errores: entra con el primer endpoint de negocio (05).
- `/metrics` y telemetría: fuera de alcance ([[tech-stack]] §10).
- Pipeline, ACR y Container Apps: es la 09.

## Resultado esperado

- Con `APP_ENVIRONMENT=local` en la terminal, `uvicorn --factory app.main:create_app` arranca, y `GET /health` responde `{"status": "ok", "environment": "local"}`.
- `docker build` y `docker run -e APP_ENVIRONMENT=local` producen una imagen que arranca como usuario sin privilegios y cuyo `HEALTHCHECK` pasa a `healthy`.
