# 01 — esqueleto-paquete — Plan

> Cómo se construye la feature. No repite los criterios de requirements.md.

## Enfoque

- **Proyecto autocontenido en `repo_libreria/`.**
  - Su `pyproject.toml` solo tiene `[build-system]` y `[project]`. Las reglas de ruff, mypy y pytest siguen en el `pyproject.toml` de la raíz, que es el del harness.
  - Al mover la librería a su repo, sus secciones `[tool.*]` se copian con el harness.
- **Build con setuptools y layout `src/`**, como la referencia (`BaseRef/core/pyproject.toml`). Desde la 69, setuptools incluye `py.typed` sin configuración extra; el humo lo comprueba.
- **Fronteras con `ast` de la librería estándar**, sin añadir dependencias como import-linter.
  - `scripts/fronteras.py` guarda la tabla de grupos de DEC-002 y la función que encuentra violaciones.
  - El test la ejecuta sobre el `src/` real y sobre paquetes sintéticos en `tmp_path`: mientras no haya módulos, solo así se prueba que detecta lo que promete.
- **Humo con uv**: `uv build --wheel`, después un `uv venv` por extra y `uv pip install "<wheel>[extra]"`. Las importaciones se hacen con el Python de ese entorno, desde un directorio temporal. uv ya es la herramienta de desarrollo ([[tech-stack]] §1).
- **Cobertura con `pytest-cov`** en `addopts`, medida solo sobre `summa_ai_framework`. Así los tests del harness no cuentan.
- **Instalación editable** con una línea `-e ./repo_libreria` en `requirements-dev.txt`. El gate local, el de CI y las plantillas instalan la librería igual que lo hará un consumidor.

## Archivos a crear o modificar

| Archivo | Cambio |
|---|---|
| `repo_libreria/pyproject.toml` | Nuevo: `[build-system]` setuptools y `[project]` con nombre, versión `0.1.0`, `requires-python`, `dependencies = []` y extras `workflow` y `agent` vacíos |
| `repo_libreria/src/summa_ai_framework/__init__.py` | Nuevo: solo docstring |
| `repo_libreria/src/summa_ai_framework/py.typed` | Nuevo, vacío |
| `repo_libreria/scripts/fronteras.py` | Nuevo: `PAQUETE`, `GRUPOS` (tabla de DEC-002) y `violaciones(paquete)` |
| `repo_libreria/scripts/humo_extras.py` | Nuevo: build, revisión de la wheel e instalación e imports por extra |
| `repo_libreria/tests/test_fronteras.py` | Nuevo: paquete real y paquetes sintéticos, permitidos y prohibidos |
| `repo_libreria/tests/test_paquete.py` | Nuevo: instalación editable desde `src/` y raíz sin nombres públicos. Además, importa el paquete: sin eso la cobertura no tiene datos y queda en 0 % |
| `pyproject.toml` (raíz) | `[tool.mypy] files` y `[tool.pytest.ini_options] testpaths` con las rutas de `repo_libreria`; `addopts` con cobertura; `per-file-ignores` para sus `tests/` y `scripts/` |
| `requirements-dev.txt` (raíz) | `pytest-cov` y `-e ./repo_libreria` |
| `AGENTS.md` | Introducción, comando del humo en "Ejecutar" y sección "Arquitectura": dónde vive cada proyecto y sus specs |
| `repo_libreria/specs/tech-stack.md` | §4: nombres de los extras y definición de API pública |
| `repo_libreria/specs/roadmap.md`, `progress.md` | Estado de la feature y continuidad |

## Secuencia

1. **Spec**: esta carpeta, con la 01 en `in_progress`. Commit `docs(specs): define la spec de 01-esqueleto-paquete`.
2. **Paquete y gate**: `pyproject.toml` de la librería, `src/` y los cambios de la raíz. Después `uv pip install -r requirements-dev.txt` y el gate en verde. Commit `feat(paquete): crea el esqueleto de summa-ai-framework`.
3. **Fronteras**: `fronteras.py` y su test, con el gate en verde. Commit `test(paquete): verifica las fronteras de import de DEC-002`.
4. **Humo**: `humo_extras.py`, ejecutado en local. Commit `feat(paquete): añade el humo por extra`.
5. **Documentación**: [[tech-stack]] §4 y `AGENTS.md`. Commit `docs: fija extras, API pública y arquitectura local`.
6. **Cierre**: `/specs cerrar 01-esqueleto-paquete`.

## Dependencias

- Features previas: ninguna.
- Decisiones: [[decisions]] DEC-001 y DEC-002, y las de la persona del 2026-11-18 recogidas en el brief.
- Herramientas nuevas: `pytest-cov`, solo en desarrollo, y `setuptools>=69`, solo para el build. Ninguna dependencia de ejecución.
- uv 0.13 o superior en la máquina que ejecuta el humo.

## Riesgos

- **El humo necesita red**: descarga setuptools y, desde LIB-02, las dependencias de cada extra. → Queda fuera del gate y su salida va a `review.md` al cerrar cada feature.
- **setuptools omite un extra vacío en los metadatos** y `pip install pkg[extra]` solo avisa. → El humo comprueba que la wheel declara `Provides-Extra` para cada extra.
- **Patrones de `per-file-ignores` relativos a la raíz**: `tests/**` no cubre `repo_libreria/tests/`. → Se añaden entradas explícitas.
- **La cobertura en `addopts` hace fallar la ejecución de un solo test.** → En ejecuciones parciales se usa `--no-cov`, y está anotado en requirements.
- **El revisor compara con `main`**, que no tiene la Constitución (`git diff main...HEAD` incluiría sus commits). → Antes del cierre, mergear `init/constitucion` en `main` o avisar al revisor del rango.
- **PySpark lo provee el clúster** y no está en ningún extra, así que importar `storage` en un entorno limpio fallará. → Lo resuelve la spec de LIB-05; aquí no aplica.

## No tocar

- `scripts/`, `.claude/` y `.github/workflows/` de la raíz: son el harness compartido (`AGENTS.md`, "Harness").
- `tests/` de la raíz: los tests del harness quedan igual.
- `repo_worklow/` y `repo_agente_conversacional/`.
- La Constitución de la librería, salvo [[tech-stack]] §4, [[roadmap]] (estado) y [[progress]].
