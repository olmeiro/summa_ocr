# 01 — esqueleto-api — Validation

> Cómo se comprueba cada criterio de aceptación y qué evidencia se guarda. Se escribe antes de programar.

## Verificación por criterio

| CA | Cómo se verifica | Tipo | Evidencia |
|---|---|---|---|
| CA-1 | `repo_agente_conversacional/tests/test_api_salud.py` con `TestClient` | automática, en el gate | Salida de `python -m pytest repo_agente_conversacional/tests --no-cov -v` |
| CA-2 | `test_api_salud.py`: con `TestClient` como contexto (arranca el `lifespan`) y sin él | automática, en el gate | Ídem |
| CA-3 | `test_api_salud.py`: los tres endpoints con `docs=False` y con `docs=True` | automática, en el gate | Ídem |
| CA-4 | `test_api_salud.py`: `monkeypatch` sin la variable y con un valor inválido; importación de `app.main` sin la variable | automática, en el gate | Ídem |
| CA-5 | `python scripts/gate.py` y lectura de `health.py` | automática + revisión | Salida del gate |
| CA-6 | La persona ejecuta `docker build -t summa-agente:local .`, `docker run -d -e APP_ENVIRONMENT=local -p 8000:8000 --name summa-agente summa-agente:local`, `curl http://localhost:8000/health`, `docker inspect --format "{{.State.Health.Status}}" summa-agente` y `docker exec summa-agente whoami` | manual, con Docker | Salida de cada comando |
| CA-7 | El agente arranca uvicorn en local en segundo plano, llama a `/health` y a `/docs` (con `APP_DOCS=true`) y lo detiene | comando | Salida de las llamadas |
| CA-8 | Lectura del diff de `AGENTS.md` | revisión | Diff |

## Validación técnica

- [ ] `python scripts/gate.py` en verde.
- [ ] Arranque local con uvicorn (CA-7).
- [ ] Imagen construida y `healthy` (CA-6), o pendiente y anotado en `review.md` si no hay Docker.
- [ ] `git status` sin `.env*` ni `__pycache__/` versionados.

## Evidencia requerida para cerrar

En `review.md`, con el commit en que se obtuvo cada una:

- el gate;
- los tests del agente;
- el arranque con uvicorn;
- los comandos de Docker, o la constancia de que siguen pendientes.

**Veredicto final**: el revisor de CI (`gpt-6-luna`) en el PR a `main`. Antes, el revisor de Claude en local. El commit de cierre se sube **antes** del merge.
