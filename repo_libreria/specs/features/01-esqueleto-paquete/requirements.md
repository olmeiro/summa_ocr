# 01 — esqueleto-paquete — Requirements

> Contrato funcional: qué debe hacer la feature. El revisor valida el diff contra sus criterios de aceptación.

## Comportamiento esperado

1. `repo_libreria/` se construye como una wheel `summa_ai_framework-0.1.0-py3-none-any.whl`:
   - con la distribución `summa-ai-framework` y el paquete `summa_ai_framework`;
   - con `Requires-Python: >=3.12`, sin dependencias de ejecución y con los extras `workflow` y `agent`.
2. La wheel contiene solo el paquete (con `py.typed`) y su `dist-info`, sin `tests/` ni `scripts/`.
3. El `__init__.py` raíz no importa nada del propio paquete.
4. El comprobador de fronteras recorre los `.py` del paquete. Devuelve:
   - una línea `archivo:línea: motivo` por cada import que viola DEC-002;
   - una línea `archivo: motivo` por cada archivo de un módulo de primer nivel sin grupo.
5. El humo construye la wheel en un directorio temporal y comprueba su contenido. Por cada extra:
   - crea un entorno limpio con Python 3.12 e instala la wheel con solo ese extra;
   - importa `summa_ai_framework` y los módulos existentes de su grupo y de los comunes;
   - comprueba que los módulos existentes del otro grupo no se pueden importar.
6. El gate de la raíz aplica lint, formato y tipos a `repo_libreria/`, ejecuta sus tests y exige el 80 % de cobertura sobre `summa_ai_framework`.
7. `requirements-dev.txt` instala la librería en modo editable.

## Reglas de negocio

- **Grupos** ([[decisions]] DEC-002):

  | Grupo | Módulos de primer nivel | Puede importar de |
  |---|---|---|
  | `comunes` | `config`, `security`, `observability`, `llms`, `embeddings`, `vectordb` | `comunes` |
  | `workflow` | `storage`, `workflow`, `extraction`, `processing`, `sources` | `comunes`, `workflow` |
  | `agent` | `auth`, `agents` | `comunes`, `agent` |
  | `__init__.py` raíz | — | nada del paquete |

- Cada extra se llama igual que su grupo: `workflow` lo instala `repo-workflow` y `agent`, `repo-agente-conversacional`.
- Un módulo de primer nivel nuevo (subpaquete o `.py` directo) debe añadirse a un grupo en `scripts/fronteras.py` en la misma feature que lo crea.
- Todos los imports del archivo cuentan: los de nivel de módulo, los de dentro de funciones y los de bajo `if TYPE_CHECKING:`.
- Importar la raíz vacía (`import summa_ai_framework`) está permitido desde cualquier módulo.
- **API pública**: los nombres del `__all__` del `__init__.py` de cada módulo de primer nivel, el nombre de la distribución y sus extras. Los submódulos y los nombres con `_` son internos.

## Casos borde

- **Imports dinámicos** (`importlib.import_module`): el comprobador no los ve. El humo los cubre cuando el módulo importado falta en el entorno del extra.
- **Import relativo que sale del paquete**: no se reporta como frontera. Python ya falla al ejecutarlo.
- **Un solo test**: la cobertura en `addopts` hace fallar `pytest <archivo>`. En ejecuciones parciales se añade `--no-cov`.
- **Sin red o sin uv**: el humo falla en el build o en la instalación con el error de uv y código distinto de 0. No hay modo offline.
- **Extra no declarado**: si la wheel no trae `Provides-Extra` para un extra, el humo falla aunque `pip` solo avisaría.
- **PySpark**: no está en ningún extra porque lo provee el clúster. Cómo lo trata el humo lo decide LIB-05.

## Restricciones

- [[decisions]] DEC-001: ninguna dependencia de ejecución en esta feature, y las herramientas de desarrollo solo en `requirements-dev.txt`.
- [[decisions]] DEC-002: tabla de grupos de arriba.
- Python 3.12 ([[tech-stack]] §1). Sin acceso a Azure ni secretos.
- El harness compartido (`scripts/`, `.claude/`, `.github/workflows/` de la raíz) no cambia ([[plan]], "No tocar").

## Criterios de aceptación

- [ ] **CA-1**: Dado `repo_libreria/`, cuando se construye la wheel, entonces:
  - se llama `summa_ai_framework-0.1.0-py3-none-any.whl`;
  - su `METADATA` declara `Name: summa-ai-framework`, `Requires-Python: >=3.12`, ningún `Requires-Dist` y `Provides-Extra` para `workflow` y `agent`;
  - solo contiene `summa_ai_framework/` (con `py.typed`) y su `dist-info`.
- [ ] **CA-2**: Dada la wheel, cuando `python repo_libreria/scripts/humo_extras.py` la instala en un entorno limpio con solo `workflow` y después con solo `agent`, entonces:
  - importa en cada entorno los módulos que le tocan;
  - comprueba que no se importan los del otro grupo;
  - termina con código 0 y una línea `PASS` por extra.

  Ante cualquier fallo, termina con código distinto de 0 y nombra el extra y el módulo.
- [ ] **CA-3**: Dado un paquete con un import que la tabla de grupos no permite, cuando corre el comprobador de fronteras, entonces reporta `archivo:línea` y el módulo importado. Esto vale:
  - para workflow ↔ agente, común → workflow o agente, y el `__init__.py` raíz → submódulo;
  - en forma absoluta o relativa, y también bajo `TYPE_CHECKING`.

  También reporta un módulo de primer nivel sin grupo y no reporta los imports permitidos. Sobre el `src/summa_ai_framework/` real devuelve una lista vacía.
- [ ] **CA-4**: Dado el `.venv` de la raíz con `requirements-dev.txt` instalado, cuando se ejecuta `python scripts/gate.py`, entonces:
  - lint, formato y tipos incluyen `repo_libreria/`;
  - los tests incluyen `repo_libreria/tests/`;
  - pytest falla si la cobertura de `summa_ai_framework` no llega al 80 %.
- [ ] **CA-5**: Dado `uv pip install -r requirements-dev.txt`, cuando se importa `summa_ai_framework`, entonces se carga desde `repo_libreria/src/` (instalación editable).
- [ ] **CA-6**: Dado el cambio de documentación, entonces:
  - [[tech-stack]] §4 nombra los extras `workflow` y `agent` y define la API pública como en las reglas de arriba;
  - la sección "Arquitectura" de `AGENTS.md` dice dónde vive cada proyecto y sus specs.
