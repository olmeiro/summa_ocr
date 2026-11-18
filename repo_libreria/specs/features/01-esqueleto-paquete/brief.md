# 01 — esqueleto-paquete — Brief

> Ficha ejecutiva: qué problema resuelve la feature y por qué ahora. Sin diseño técnico ni tareas.

## Problema

La librería `summa-ai-framework` no existe todavía: no hay paquete que instalar ni lugar donde poner el código de las features 02 a 17. Tampoco hay nada que haga cumplir las reglas que la Constitución fija para todas ellas:

- un extra por consumidor, para que el workflow no cargue dependencias del agente ni al revés ([[decisions]] DEC-001);
- fronteras de import entre módulos comunes, de workflow y de agente ([[decisions]] DEC-002);
- cobertura mínima del 80 % ([[mission]] §6).

Sin ese esqueleto, cada feature resolvería por su cuenta el empaquetado y las fronteras, y las plantillas no tendrían nada que instalar desde una ruta local.

## Por qué ahora

Es la primera feature del [[roadmap]] y no depende de ninguna. Todas las demás (`LIB-02` a `LIB-17`) la necesitan, y es manejable: sirve para probar el flujo SDD y el harness con poco riesgo ([[roadmap]] §1, principio 2).

## Decisión de diseño

Decisiones de la persona del 2026-11-18:

- Mientras no exista el repo en Azure DevOps, la librería vive en `repo_libreria/` dentro de `summa_ocr`. Es un proyecto autocontenido (su `pyproject.toml`, `src/` y `tests/`) que se mueve tal cual a su repo. Hasta entonces la cubre el gate de la raíz.
- Los extras se llaman `workflow` y `agent`.
- El humo por extra es un script fuera del gate: se ejecuta al cerrar cada feature y, desde LIB-04, en el pipeline.
- `scripts/gate.py` usa el Python del `.venv` de la raíz aunque nadie lo haya activado. Se arregla en esta feature y en esta rama: el revisor no podía ejecutar el gate y la revisión quedó bloqueada (`review.md`, "Block 2").

Los módulos de [[tech-stack]] §3 no se crean vacíos: cada feature crea el suyo, y el test de fronteras obliga a asignarlo a un grupo.

## Incluye

- `repo_libreria/pyproject.toml`: paquete `summa-ai-framework` `0.1.0`, `requires-python >=3.12`, sin dependencias obligatorias y con los extras `workflow` y `agent` vacíos.
- `src/summa_ai_framework/` con `__init__.py`, que no reexporta nada, y `py.typed`, para que las plantillas lo tipen con mypy estricto.
- Build de la wheel.
- Test de fronteras de import (DEC-002) dentro del gate.
- Script de humo por extra (DEC-001 y DEC-002) fuera del gate.
- Gate de la raíz extendido a `repo_libreria`, con cobertura mínima del 80 % sobre `summa_ai_framework`.
- Instalación editable de la librería en el `.venv` de la raíz.
- Definición de API pública y nombres de los extras en [[tech-stack]] §4.
- Sección "Arquitectura" de `AGENTS.md`: dónde vive cada proyecto y sus specs.
- `scripts/gate.py` elige el Python del `.venv`. El hook Stop deja de resolverlo por su cuenta.

## No incluye

- Módulos de [[tech-stack]] §3 (`config`, `security`…): los crea la feature que los introduce.
- Dependencias de ejecución: se fijan en la feature que las usa ([[tech-stack]] §5).
- Pipeline de Azure DevOps y publicación en el feed (LIB-04).
- Repo propio y copia del harness dentro de `repo_libreria/` (bloqueo de [[progress]]).

## Resultado esperado

- `python scripts/gate.py` revisa lint, formato, tipos, tests y cobertura de la librería.
- `python repo_libreria/scripts/humo_extras.py` construye la wheel `summa_ai_framework-0.1.0`. Después la instala, con solo un extra cada vez, en un entorno limpio, y termina en verde.
- Una plantilla puede ejecutar `uv pip install -e <ruta>/repo_libreria[workflow]` e importar `summa_ai_framework`.
