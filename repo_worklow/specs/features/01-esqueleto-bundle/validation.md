# 01 — esqueleto-bundle — Validation

> Cómo se comprueba cada criterio de aceptación y qué evidencia se guarda. Se escribe antes de programar.

## Verificación por criterio

| CA | Cómo se verifica | Tipo | Evidencia |
|---|---|---|---|
| CA-1 | Desde `repo_worklow/`, `databricks bundle validate -t dev -p <perfil>` y `-t prod -p <perfil>` | comando, fuera del gate | Salida de los dos comandos, sin el host |
| CA-2 | `repo_worklow/tests/test_bundle.py` | automática, en el gate | Salida de `python -m pytest repo_worklow/tests --no-cov -v` |
| CA-3 | `test_bundle.py`: versión frente a `pyproject.toml`, ruta de la wheel y búsqueda de la versión literal | automática, en el gate | Ídem |
| CA-4 | `test_bundle.py`: el comprobador de secretos sobre los YAML reales y sobre un YAML sintético con cada caso prohibido | automática, en el gate | Ídem |
| CA-5 | `repo_worklow/tests/test_s00_humo.py`: importación silenciosa (`capsys`), `ejecutar` y `main` | automática, en el gate | Ídem |
| CA-6 | La persona despliega y ejecuta la variante serverless desechable (`databricks bundle deploy` y `run`, fuera del repo) en el workspace de pruebas. El agente lee el resultado con `databricks jobs get-run` y `get-run-output` | manual + comando, en el workspace de pruebas | Estado de la tarea, sus líneas `[HUMO]` y la definición del environment, sin URLs del workspace |
| CA-7 | `python scripts/gate.py` y lectura del diff de `pyproject.toml` y `.gitignore` | automática + revisión | Salida del gate y diff |
| CA-8 | Lectura del diff de `AGENTS.md` | revisión | Diff |

## Validación técnica

- [ ] `python scripts/gate.py` en verde.
- [ ] `bundle validate` en verde para `dev` y `prod`.
- [ ] Ejecución del step en Databricks en `SUCCESS` ([[tech-stack]] §11): la variante serverless en el workspace de pruebas; en clásico, pendiente.
- [ ] `git status` sin `.databricks/`, `dist/` ni `build/`.

## Evidencia requerida para cerrar

En `review.md`, con el commit en que se obtuvo cada una:

- el gate;
- los tests de `repo_worklow`;
- los dos `bundle validate`;
- el `deploy` y el `run`, con las líneas `[HUMO]`.

**Veredicto final**: el revisor de CI (`gpt-6-luna`) en el PR a `main`. Antes, el revisor de Claude en local. El cierre va dentro del PR, antes del merge.
