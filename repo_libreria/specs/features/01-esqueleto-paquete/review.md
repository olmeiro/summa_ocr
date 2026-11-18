# 01 — esqueleto-paquete — Review

> Evidencia real de la validación de la feature, rama `feature/01-esqueleto-paquete`.
> Toda la evidencia es de `a337366` más los cambios sin commit: los commits los hace la persona (`AGENTS.md`, "Harness") y se hacen después de este cierre, en el orden de `plan.md` §Secuencia.

## Gate

2026-11-18, vuelta 2 (tras las correcciones del revise 1), `python scripts/gate.py`:

```text
[GATE] PASS: Lint
[GATE] PASS: Formato
[GATE] PASS: Tipos
Required test coverage of 80% reached. Total coverage: 100.00%
84 passed in 8.00s
[GATE] PASS: Tests
[GATE] Todas las comprobaciones pasaron.
```

## Cumplimiento por criterio

| CA | Estado | Evidencia |
|---|---|---|
| CA-1 | cumple | Abajo: listado de la wheel y `METADATA` |
| CA-2 | cumple | Abajo: humo en verde y ejecuciones de la rama de fallo |
| CA-3 | cumple | Abajo: 15 tests de fronteras |
| CA-4 | cumple | Gate de arriba y, abajo, la ejecución por debajo del umbral |
| CA-5 | cumple | Abajo: `test_se_instala_editable_desde_src` y `test_la_raiz_no_reexporta_nada` |
| CA-6 | cumple | Diff de `repo_libreria/specs/tech-stack.md` §4 (extras y API pública) y de `AGENTS.md` (introducción, humo y "Arquitectura") |

### CA-1: wheel

`uv build --wheel repo_libreria -o <tmp>` y `python -m zipfile -l <wheel>`:

```text
summa_ai_framework-0.1.0-py3-none-any.whl
summa_ai_framework/__init__.py
summa_ai_framework/py.typed
summa_ai_framework-0.1.0.dist-info/METADATA
summa_ai_framework-0.1.0.dist-info/WHEEL
summa_ai_framework-0.1.0.dist-info/top_level.txt
summa_ai_framework-0.1.0.dist-info/RECORD

Metadata-Version: 2.4
Name: summa-ai-framework
Version: 0.1.0
Summary: Capacidades comunes del framework de IA de SUMMA para sus plantillas de workflow y de agente.
Requires-Python: >=3.12
Provides-Extra: workflow
Provides-Extra: agent
```

### CA-2: humo por extra

`python repo_libreria/scripts/humo_extras.py` (vuelta 2, borra `build/` antes de construir):

```text
[HUMO] Wheel: summa_ai_framework-0.1.0-py3-none-any.whl
[HUMO] PASS: agent (importa summa_ai_framework)
[HUMO] PASS: workflow (importa summa_ai_framework)
[HUMO] Todas las comprobaciones pasaron.
exit=0
```

Rama de fallo, sobre copias de `repo_libreria/` en un directorio temporal con un módulo `agents` añadido. Primero, `agents/__init__.py` importa una dependencia que no está instalada:

```text
ModuleNotFoundError: No module named 'dependencia_del_extra_agent'
[HUMO] FAIL: agent: no importa summa_ai_framework.agents
exit=1
```

Después, `agents/__init__.py` está vacío, así que se importa también con solo `workflow`:

```text
[HUMO] PASS: agent (importa summa_ai_framework, summa_ai_framework.agents)
[HUMO] FAIL: workflow: importa summa_ai_framework.agents, que es de agent
exit=1
```

### CA-3 y CA-5: tests de la librería

`python -m pytest repo_libreria/tests --no-cov -v`:

```text
test_fronteras.py::test_el_paquete_real_respeta_las_fronteras PASSED
test_fronteras.py::test_ningun_modulo_esta_en_dos_grupos PASSED
test_fronteras.py::test_imports_permitidos[workflow-a-comun] PASSED
test_fronteras.py::test_imports_permitidos[agente-relativo] PASSED
test_fronteras.py::test_imports_permitidos[comun-a-comun] PASSED
test_fronteras.py::test_imports_permitidos[raiz-vacia] PASSED
test_fronteras.py::test_imports_permitidos[relativo-fuera-del-paquete] PASSED
test_fronteras.py::test_imports_prohibidos[workflow-a-agente] PASSED
test_fronteras.py::test_imports_prohibidos[agente-a-workflow] PASSED
test_fronteras.py::test_imports_prohibidos[relativo-workflow-a-agente] PASSED
test_fronteras.py::test_imports_prohibidos[comun-a-workflow] PASSED
test_fronteras.py::test_imports_prohibidos[type-checking] PASSED
test_fronteras.py::test_imports_prohibidos[raiz-reexporta] PASSED
test_fronteras.py::test_imports_prohibidos[subpaquete-sin-grupo] PASSED
test_fronteras.py::test_imports_prohibidos[modulo-sin-grupo] PASSED
test_paquete.py::test_se_instala_editable_desde_src PASSED
test_paquete.py::test_la_raiz_no_reexporta_nada PASSED
17 passed
```

### CA-4: umbral de cobertura

`python -m pytest -q tests/test_revisor_ci.py`, que no importa el paquete:

```text
ERROR: Coverage failure: total of 0 is less than fail-under=80
FAIL Required test coverage of 80% not reached. Total coverage: 0.00%
24 passed in 2.01s
exit=1
```

## Errores encontrados al validar

| Error | Causa | Corrección | Destino en el harness |
|---|---|---|---|
| Cobertura 0 % con todos los tests en verde | El test de fronteras lee el AST y no importa el paquete, así que coverage no recoge datos | `test_paquete.py` importa el paquete y comprueba la instalación editable (CA-5 pasa a ser automático) | corrección + test |
| El gate marcó formato tras editar con Claude | `post_edit.py` busca `ruff` en el PATH y el `.venv` no estaba activado: omite el formato en silencio (su `shortcut:`) | `ruff format` a mano | puntual; si se repite, `AGENTS.md` o que el hook use el Python del `.venv`, como ya hace `gate_al_parar.py` |
| `--cov-fail-under=101` no sirve para probar el umbral | pytest-cov solo acepta valores de 0 a 100 | `validation.md` usa una ejecución que no importa el paquete | corrección de la spec |
| Revise 1: `test_la_raiz_no_reexporta_nada` fallaría en cuanto un test importe un submódulo | El sistema de imports pone cada submódulo importado como atributo de la raíz, y `vars()` lo veía | Se ignoran los atributos de tipo `ModuleType` y se comprueba que la raíz no define `__all__` | corrección |
| Revise 1: un import relativo que sale del paquete se resolvía mal | Índice negativo en `partes[: len - level]` | `max(..., 0)` y caso `relativo-fuera-del-paquete` | corrección + test |
| Revise 1: el test del paquete real pasaría con una ruta inexistente | `rglob` sobre una ruta que no existe devuelve vacío | Se comprueba que existe `__init__.py` antes de revisar | corrección |
| Revise 1: archivos viejos de `build/lib` podrían colarse en la wheel | setuptools reutiliza `build/` del árbol de fuentes | El humo borra `repo_libreria/build/` antes de construir | corrección |
| Revise 1: sin uv, el humo salía con traceback | `subprocess.run` lanza `FileNotFoundError` | El humo comprueba `shutil.which("uv")` antes de empezar | corrección |
| Revise 1: el revisor no pudo ejecutar el gate | La sesión quedó con el cwd en `repo_libreria/specs` y `solo_lectura.py` solo admite `python scripts/gate.py` literal | El revisor se relanza con el cwd en la raíz. No bastó: ver la fila "Block 2" | ver "Block 2" |
| Block 2: el revisor tampoco pudo ejecutar el gate desde la raíz | El `python` del PATH es el del sistema (`…\Python312\python.exe`), sin ruff, mypy ni pytest, porque el `.venv` no está activado en la shell de Claude Code. `gate.py` usa `sys.executable` | Lo decide la persona: revisor desde una terminal con el `.venv` activado, o gate ejecutado por la persona | se repite (2 vueltas): hook o regla del harness, que `gate.py` use el Python del `.venv` como `gate_al_parar.py`. Cambio aparte, el harness está en "No tocar" |
| Block 2: el aviso de módulo sin grupo no tiene línea y sale por archivo | La spec pedía `archivo:línea` también en ese caso | Se corrige la spec (`requirements.md`, comportamiento 4) | corrección de la spec |
| Block 2: el filtro de archivos de la wheel admitía `summa_ai_framework-*.data/` | Prefijo `summa_ai_framework-` demasiado amplio | Solo se admite el directorio `dist-info` del `METADATA` | corrección |
| Revise 1: `progress.md` sin actualizar | El cierre aún no había llegado a ese paso | Actualizado en esta vuelta | corrección |

## Veredicto del revisor

- **Vuelta 1**: `revise`. Hallazgos en las filas "Revise 1" de arriba, más el rango contra `main` y el revisor de CI (ver "Deuda técnica").
- **Vuelta 2**: `block`. No encuentra defectos que obliguen a cambiar el código y da CA-1, CA-3, CA-5 y CA-6 por cumplidos. CA-2 y CA-4 los da por buenos leyendo el código, pero no pudo verificarlos ejecutándolos: no pudo ejecutar el gate (fila "Block 2"). Se para y decide la persona.
- **Vueltas de revise**: 1 de 2

## Desviaciones de la spec

- CA-5 se verifica con un test del gate (`test_paquete.py`) en vez de un comando manual. La razón está en la primera fila de "Errores encontrados al validar". `plan.md` y `validation.md` ya lo recogen.
- `AGENTS.md` también recibe la introducción y el comando del humo en "Ejecutar", no solo "Arquitectura". `plan.md` ya lo recoge.

## Deuda técnica y temas para replanning

- **Rango contra `main`**: `main` solo tiene el commit inicial. Hasta mergear `init/constitucion` en `main` por PR, `git diff main...HEAD`, el revisor local y un PR de esta rama arrastran los commits de la Constitución y de `876a101` (harness). Lo decide la persona.
- **Revisor de CI**: `scripts/revisor_ci.py:67-76` busca `specs/features/NN-nombre` en la raíz y no encontrará `repo_libreria/specs/features/…`, así que revisaría sin `CA-N`. Es un cambio del harness, que esta feature tiene en "No tocar": va en un cambio aparte o se resuelve al mover cada proyecto a su repo.
- **Harness y `.venv` sin activar**: `gate.py` (y con él el revisor) y `post_edit.py` usan el Python o el `ruff` del PATH. Si el `.venv` no está activado, el revisor no puede ejecutar el gate y el formato se omite en silencio. `gate_al_parar.py` ya lo resuelve buscando el `.venv`. Cambio del harness, aparte de esta feature.
- **Documentación de dependencias**: [[tech-stack]] §5 no menciona `pytest-cov` (desarrollo) ni `setuptools>=69` (build).
- **Nombres de test**: `tests/` y `repo_libreria/tests/` no tienen `__init__.py`. Un archivo de test con el mismo nombre en las dos rompería la recolección de pytest y mypy. Hoy no hay colisiones.
