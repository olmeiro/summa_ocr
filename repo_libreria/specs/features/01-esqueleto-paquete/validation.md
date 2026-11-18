# 01 — esqueleto-paquete — Validation

> Cómo se comprueba cada criterio de aceptación y qué evidencia se guarda. Se escribe antes de programar.

## Verificación por criterio

| CA | Cómo se verifica | Tipo | Evidencia |
|---|---|---|---|
| CA-1 | `humo_extras.py` revisa la wheel: archivos ajenos al paquete, `py.typed` y `Provides-Extra` de cada extra. Además, `uv build --wheel repo_libreria -o <tmp>` y `python -m zipfile -l <wheel>`, más el `METADATA` | automática + comando | Nombre de la wheel, listado de archivos y `METADATA` |
| CA-2 | `python repo_libreria/scripts/humo_extras.py` | automática, fuera del gate | Salida completa con `[HUMO] PASS: agent`, `[HUMO] PASS: workflow` y el código de salida |
| CA-3 | `repo_libreria/tests/test_fronteras.py`: paquete real, imports permitidos y un caso por cada violación de la regla | automática, en el gate | Salida de `python -m pytest repo_libreria/tests --no-cov -v` |
| CA-4 | `python scripts/gate.py` y, para probar el umbral, `python -m pytest -q tests/test_revisor_ci.py`: no importa el paquete, la cobertura queda en 0 % y debe fallar | automática | Salida del gate con `Required test coverage of 80% reached`, y `Coverage failure` con código 1 en la otra ejecución |
| CA-5 | `repo_libreria/tests/test_paquete.py`: el paquete importado está en `repo_libreria/src/` y su raíz no expone nombres públicos | automática, en el gate | Salida de `python -m pytest repo_libreria/tests --no-cov -v` |
| CA-6 | Lectura del diff de `repo_libreria/specs/tech-stack.md` §4 y de `AGENTS.md` | revisión | Diff |

## Validación técnica

- [ ] `python scripts/gate.py` en verde.
- [ ] `python repo_libreria/scripts/humo_extras.py` en verde en la máquina local con uv.
- [ ] `git status` sin `build/`, `dist/` ni `*.egg-info` versionados.

## Evidencia requerida para cerrar

En `review.md`:

- la salida del gate;
- la del humo;
- la de la ejecución que no llega al umbral de cobertura;
- el listado y el `METADATA` de la wheel;
- la salida de los tests de `repo_libreria/tests` (fronteras e instalación editable).

Cada una, con el commit en el que se obtuvo. No hay prueba de integración contra Azure: la feature no toca ningún servicio ([[tech-stack]] §11).
