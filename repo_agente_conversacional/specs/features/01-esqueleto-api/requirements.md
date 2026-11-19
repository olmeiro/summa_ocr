# 01 — esqueleto-api — Requirements

> Contrato funcional: qué debe hacer la feature. El revisor valida el diff contra sus criterios de aceptación.

## Comportamiento esperado

1. `create_app()` devuelve una app FastAPI configurada con `AppSettings`, que lee las variables `APP_*` del entorno. Importar `app.main` no crea la app ni lee el entorno.
2. `GET /health` responde 200 con `{"status": "ok", "environment": <APP_ENVIRONMENT>}`.
3. `GET /ready` responde 200 con `{"status": "ready"}` cuando el arranque de la app terminó, y 503 antes.
4. Con `APP_DOCS` sin definir o `false`, no existen `/docs`, `/redoc` ni `/openapi.json`: los tres devuelven 404. Con `APP_DOCS=true`, los tres responden 200.
5. Sin `APP_ENVIRONMENT`, o con un valor distinto de `local`, `dev` o `prod`, `create_app()` falla con un error de validación que nombra la variable.
6. La imagen Docker arranca uvicorn con la fábrica en el puerto 8000, como usuario sin privilegios, y su `HEALTHCHECK` llama a `/health`.

## Reglas de negocio

- **Valores de producción por defecto** ([[tech-stack]] §2):
  - documentación apagada;
  - sin middleware CORS;
  - ningún `debug`.
- **Entorno**: la app no lee archivos `.env`. Las variables llegan del entorno del proceso: la terminal en local, `-e` en Docker y el Container App en Azure.
- **Salud fuera de `/api/v1`**: `/health` y `/ready` cuelgan de la raíz, porque los usan las sondas de Container Apps y no son API de negocio.
- **Imagen**:
  - sin secretos ni `ARG` con credenciales (la base deja la del feed en el historial, `Dockerfile:6`);
  - sin `tests/` ni `specs/`;
  - basada en `python:3.12-slim` ([[tech-stack]] §1).

## Casos borde

- `APP_ENVIRONMENT=PROD` en mayúsculas: inválido, porque los valores son en minúsculas, y falla al arrancar.
- `APP_DOCS=1` o `APP_DOCS=yes`: pydantic los interpreta como verdadero. Es el comportamiento estándar de `pydantic-settings`.
- Petición a `/ready` antes de que termine el arranque: 503. En la práctica, uvicorn no atiende hasta que el `lifespan` termina; el test lo comprueba con la app sin arrancar.
- Variables `APP_*` desconocidas en el entorno: se ignoran.

## Restricciones

- [[tech-stack]] §1: Python 3.12 e imagen `python:3.12-slim`.
- [[tech-stack]] §2: endpoints `async`; reglas `FAST`, `ASYNC` y `S` del gate.
- El gate no necesita Docker ni Azure.

## Criterios de aceptación

- [ ] **CA-1**: Dado `APP_ENVIRONMENT=local`, cuando se pide `GET /health` a la app creada con `create_app()`, entonces responde 200 con `{"status": "ok", "environment": "local"}`.
- [ ] **CA-2**: Dada la app arrancada (su `lifespan` ejecutado), cuando se pide `GET /ready`, entonces responde 200 con `{"status": "ready"}`. Con la app sin arrancar, responde 503.
- [ ] **CA-3**: Dado `APP_DOCS` sin definir, cuando se piden `/docs`, `/redoc` y `/openapi.json`, entonces los tres responden 404. Con `APP_DOCS=true`, responden 200.
- [ ] **CA-4**: Dado un entorno sin `APP_ENVIRONMENT`, o con `APP_ENVIRONMENT=staging`, cuando se llama a `create_app()`, entonces falla con un `ValidationError` que menciona `environment`. Importar `app.main` no falla aunque falte la variable.
- [ ] **CA-5**: Dado el código, cuando corre el gate, entonces lint (incluidas las reglas `FAST` y `ASYNC`), formato, tipos y tests incluyen `repo_agente_conversacional/`, y los endpoints son `async`.
- [ ] **CA-6**: Dado Docker en la máquina de la persona, cuando ejecuta `docker build` y `docker run -e APP_ENVIRONMENT=local -p 8000:8000` en `repo_agente_conversacional/`, entonces:
  - `GET http://localhost:8000/health` responde como en CA-1;
  - `docker inspect` muestra el estado de salud `healthy`;
  - `whoami` en el contenedor no es `root`.
- [ ] **CA-7**: Dado el entorno local con uvicorn, cuando se ejecuta `uvicorn --factory app.main:create_app` con `APP_ENVIRONMENT=local`, entonces `GET /health` responde como en CA-1. Con `APP_DOCS=true`, `/docs` muestra la documentación.
- [ ] **CA-8**: Dado `AGENTS.md`, entonces:
  - "Arquitectura" describe `repo_agente_conversacional/`;
  - "Ejecutar" lista el arranque con uvicorn y con Docker.
