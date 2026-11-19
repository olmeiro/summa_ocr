# 01 — esqueleto-api — Review

> Evidencia real de la validación de la feature, rama `feature/01-esqueleto-api` (commits `cce2c36` a `2ef959c`), creada desde `main` (`34240f8`) y mergeada con el PR #6 (`f9c21ac`).
> Los tests, CA-6 y CA-7 se ejecutaron sobre el árbol de trabajo antes de los commits, el 2026-11-18 y el 2026-11-19. Ese código es el que entró en `a8dec27` (app y tests) y `dde48f5` (imagen); después solo cambiaron archivos `.md`. El gate se repitió sobre `f9c21ac`.

## Gate

`python scripts/gate.py` sobre `f9c21ac` (`main` tras el merge), el 2026-11-19:

```text
[GATE] PASS: Lint
[GATE] PASS: Formato
[GATE] PASS: Tipos
161 passed in 15.27s
[GATE] PASS: Tests
[GATE] Todas las comprobaciones pasaron.
```

## Cumplimiento por criterio

| CA | Estado | Evidencia |
|---|---|---|
| CA-1 | cumple | `test_health_responde_el_ambiente` |
| CA-2 | cumple | `test_ready_tras_arrancar` y `test_ready_antes_de_arrancar_es_503` |
| CA-3 | cumple | `test_documentacion_apagada_por_defecto` y `test_documentacion_con_app_docs`, cada uno con `/docs`, `/redoc` y `/openapi.json` |
| CA-4 | cumple | `test_ambiente_obligatorio_y_valido[ausente, staging, mayusculas]` y `test_importar_main_no_lee_el_entorno`; además, `test_lee_los_ajustes_del_entorno` |
| CA-5 | cumple | Gate de arriba (ruff con `FAST`, `ASYNC` y `S`; mypy estricto sobre `app/` y `tests/`). `health` y `ready` son `async` |
| CA-6 | cumple | `docker build` y `docker run` de la imagen final en la máquina de la persona: `/health` responde, `healthy`, `appuser` y `/app` sin escritura, abajo |
| CA-7 | cumple | Arranque real con uvicorn, abajo |
| CA-8 | cumple | Diff de `AGENTS.md`: "Arquitectura" y "Ejecutar" (uvicorn y Docker) |

### Tests del agente

`python -m pytest repo_agente_conversacional/tests --no-cov -v`:

```text
test_api_salud.py::test_health_responde_el_ambiente PASSED
test_api_salud.py::test_ready_tras_arrancar PASSED
test_api_salud.py::test_ready_antes_de_arrancar_es_503 PASSED
test_api_salud.py::test_documentacion_apagada_por_defecto[/docs] PASSED
test_api_salud.py::test_documentacion_apagada_por_defecto[/redoc] PASSED
test_api_salud.py::test_documentacion_apagada_por_defecto[/openapi.json] PASSED
test_api_salud.py::test_documentacion_con_app_docs[/docs] PASSED
test_api_salud.py::test_documentacion_con_app_docs[/redoc] PASSED
test_api_salud.py::test_documentacion_con_app_docs[/openapi.json] PASSED
test_api_salud.py::test_lee_los_ajustes_del_entorno PASSED
test_api_salud.py::test_ambiente_obligatorio_y_valido[ausente] PASSED
test_api_salud.py::test_ambiente_obligatorio_y_valido[staging] PASSED
test_api_salud.py::test_ambiente_obligatorio_y_valido[mayusculas] PASSED
test_api_salud.py::test_importar_main_no_lee_el_entorno PASSED
14 passed
```

Los tests no dependen de las variables `APP_*` de quien los ejecuta (hallazgo 1 de la vuelta 1). Comprobado el 2026-11-19 con `APP_DOCS=true APP_ENVIRONMENT=prod python -m pytest repo_agente_conversacional/tests --no-cov -q`:

```text
14 passed in 0.73s
```

### CA-7: arranque real con uvicorn

Un script arranca `python -m uvicorn --factory app.main:create_app --app-dir repo_agente_conversacional --port 8765`, llama a los endpoints y detiene el proceso:

```text
### APP_ENVIRONMENT=local
  GET /health -> 200 {"status":"ok","environment":"local"}
  GET /ready -> 200 {"status":"ready"}
  GET /docs -> 404
  log: INFO:     Application startup complete. | INFO:     Uvicorn running on http://127.0.0.1:8765
### APP_ENVIRONMENT=local APP_DOCS=true
  GET /health -> 200 {"status":"ok","environment":"local"}
  GET /ready -> 200 {"status":"ready"}
  GET /docs -> 200
  log: INFO:     Application startup complete. | INFO:     Uvicorn running on http://127.0.0.1:8765
```

### CA-6: imagen Docker

Imagen final, tras los cambios de la vuelta 1 del revisor: `/app` es de root y `.dockerignore` excluye `.env*` en cualquier carpeta. La persona lo ejecutó en su máquina el 2026-11-19, con Docker Desktop 4.99.0 (Engine 29.9.3), desde `repo_agente_conversacional/`. Es una sola secuencia sobre un solo contenedor:

```text
> docker rm -f summa-agente
summa-agente
> docker build -t summa-agente:local .
 => [1/6] FROM docker.io/library/python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b
 => CACHED [4/6] RUN pip install -r requirements.txt
 => [5/6] COPY app/ ./app/
 => [6/6] RUN useradd --create-home --shell /usr/sbin/nologin appuser
 => => naming to docker.io/library/summa-agente:local
[+] Building 3.7s (12/12) FINISHED
> docker run -d -e APP_ENVIRONMENT=local -p 8000:8000 --name summa-agente summa-agente:local
8e1c03bbdbdaa2c60f5739293b8bb243b10faf39884e84ecb29e6f0967b3289d
> curl.exe -s http://localhost:8000/health
{"status":"ok","environment":"local"}
> docker inspect --format "{{.State.Health.Status}}" summa-agente
healthy
> docker exec summa-agente whoami
appuser
> docker exec summa-agente touch /app/prueba
touch: cannot touch '/app/prueba': Permission denied
```

Con la imagen anterior, que tenía `chown -R appuser:appuser /app`, CA-6 también se cumplió. Sin `APP_DOCS`, `/docs` respondió 404 en el contenedor (`{"detail":"Not Found"}`), como pide CA-3.

## Errores encontrados al validar

| Error | Causa | Corrección | Destino en el harness |
|---|---|---|---|
| Vuelta 1: con `APP_DOCS=true` en el entorno de quien ejecuta los tests, fallaban los de documentación apagada por defecto | `AppSettings` se creaba al importar el módulo y leía `APP_DOCS` | Fixture `autouse` que borra `APP_*`, y `AppSettings` dentro de cada test. Comprobado con `APP_DOCS=true APP_ENVIRONMENT=prod` | puntual (corrección en el test) |
| Vuelta 1: `appuser` podía escribir en `/app` | `chown -R appuser:appuser /app` sobraba | `/app` queda de root; `touch /app/prueba` da `Permission denied` (CA-6) | puntual |
| Vuelta 1: `.dockerignore` solo excluía `.env*` en la raíz del contexto | Patrones sin `**/` | `**/.env` y `**/.env.*` | puntual |
| Vuelta 1 (evidencia): la transcripción de CA-6 mezclaba dos contenedores | Se copiaron comprobaciones de un contenedor recreado con `APP_DOCS=true` | CA-6 repetido en una sola secuencia | puntual |
| Proceso: el PR #6 se mergeó antes de subir el cierre | La persona mergea en cuanto CI da `accept`. Es la tercera vez: LIB-03, 01-esqueleto-bundle y esta | El cierre entra con un commit directo a `main` | Decisión de la persona (2026-11-19): la feature se cierra en su rama antes de abrir el PR, como ya decía §7.4. Queda en `AGENTS.md` (revisor local) y en el modo `cerrar` de la skill `specs` |

## Veredicto del revisor

- **Vuelta 1** (revisor de Claude, local, 2026-11-19): `revise`. Gate en verde y CA-1 a CA-8 cumplen. Hallazgos y lo que se hizo con cada uno:
  1. Corregido: los tests de documentación por defecto dependían de `APP_DOCS` en el entorno de quien los ejecuta. Un fixture `autouse` limpia `APP_*` en `test_api_salud.py`.
  2. Corregido: `progress.md` decía que el agente no tenía código.
  3. Corregido: la transcripción de CA-6 mezclaba dos contenedores. Se repitió con la imagen final en una sola secuencia.
  4. Pendiente del cierre: anclar la evidencia al hash del commit.
  5. Corregido: la salud fuera de `api/v1/` es una desviación de [[tech-stack]] §3; ahora consta en "Desviaciones".
  6. Corregido: `/app` era propiedad de `appuser`; ahora es de root.
  7. Corregido: `.dockerignore` solo excluía `.env*` en la raíz del contexto.
  8. Descartado: modelos Pydantic y `responses=` para la salud. Ningún CA los pide.
- **Vuelta 2** (revisor de Claude, local, 2026-11-19): `accept`. Gate en verde. Un hallazgo menor: el replanning de [[tech-stack]] §3 faltaba en "Deuda técnica"; ya está. El revisor no pudo ejecutar los tests con `APP_DOCS=true` porque su hook solo permite git y el gate; esa comprobación la hizo el agente que implementa (arriba).
- **Revisor local con `gpt-6-luna`** (lo lanzó la persona el 2026-11-19, `REVISOR_BASE=main`, sobre `51b5df0`): **`accept`**, a la primera. Salida de `revisor_local.txt`:

  ```text
  OK     01_esqueleto_api_CA_1: p=1.00
  OK     01_esqueleto_api_CA_2: p=1.00
  OK     01_esqueleto_api_CA_3: p=0.98
  OK     01_esqueleto_api_CA_4: p=0.99
  OK     01_esqueleto_api_CA_5: p=0.97
  OK     01_esqueleto_api_CA_6: p=1.00
  OK     01_esqueleto_api_CA_7: p=1.00
  OK     01_esqueleto_api_CA_8: p=1.00
  OK     01_esqueleto_api_no_tocar: p=0.93
  OK     01_esqueleto_api_evidencia: p=0.79
  OK     rompe_algo: p=0.16
  OK     riesgo_seguridad: p=0.07
  OK     debilita_tests: p=0.00
  OK     dirige_revision: p=0.00

  [REVISOR] accept
  ```

- **Veredicto final** (revisor de CI con `gpt-6-luna`, PR #6 a `main`, sobre `2ef959c`): **`accept`**, a la primera. Salida del job `revisor` de GitHub Actions, paso "Revisión":

  ```text
  OK     01_esqueleto_api_CA_1: p=1.00
  OK     01_esqueleto_api_CA_2: p=1.00
  OK     01_esqueleto_api_CA_3: p=0.99
  OK     01_esqueleto_api_CA_4: p=0.99
  OK     01_esqueleto_api_CA_5: p=0.98
  OK     01_esqueleto_api_CA_6: p=0.99
  OK     01_esqueleto_api_CA_7: p=1.00
  OK     01_esqueleto_api_CA_8: p=1.00
  OK     01_esqueleto_api_no_tocar: p=0.97
  OK     01_esqueleto_api_evidencia: p=0.81
  OK     rompe_algo: p=0.13
  OK     riesgo_seguridad: p=0.05
  OK     debilita_tests: p=0.00
  OK     dirige_revision: p=0.00

  [REVISOR] accept
  ```

  El PR #6 se mergeó (`f9c21ac`) antes de subir este cierre, así que el cierre entra con un commit directo a `main`, como en LIB-03 y en 01-esqueleto-bundle.
- **Vueltas de revise**: 1 de 2

## Desviaciones de la spec

- **Con [[tech-stack]] §3**: `/health` y `/ready` viven en `app/api/health.py` y cuelgan de la raíz, no de `api/v1/`, porque los usan las sondas de Container Apps (Reglas de negocio de `requirements.md`). Esta feature no toca la Constitución (`plan.md`, «No tocar»), así que §3 se corrige en un replanning.

## Deuda técnica y temas para replanning

- **[[tech-stack]] §3**: la estructura de módulos pone la salud en `api/v1/`. Hay que corregirla para que coincida con `app/api/health.py`, en la raíz de rutas (ver "Desviaciones").
