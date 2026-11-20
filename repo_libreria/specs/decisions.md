# Decisiones técnicas

> Decisiones que aplican a **todo el proyecto**, no a una feature. Las features las citan con `[[decisions]]` y su `DEC-NNN` en lugar de repetir el razonamiento.
> Una decisión no se borra: se reemplaza con otra que indique `Reemplaza: DEC-NNN`.

Se añade una entrada cuando una decisión debe respetarse en varias features, copiando la estructura de DEC-001 con el siguiente número.

---

## DEC-001 — Una sola librería con extras por consumidor

- **Fecha**: 2026-11-12
- **Introducida en**: Constitución (`init/constitucion`)
- **Aplica a**: todo el paquete, su `pyproject.toml` y las dos plantillas que lo instalan
- **Estado**: vigente; la regla 3 y su verificación de fronteras están reemplazadas por DEC-002

### Contexto

La base de referencia separa el código común en dos librerías: core (configuración, seguridad, observabilidad y storage) y cognitive (LLM, embeddings, OCR, chunking, agentes, MCP y AI Search). SUMMA decidió una sola (decisión de la persona). Se validó si eso deja la librería demasiado cargada, midiendo la base:

- **Las dos plantillas de la base importan de las dos librerías.** El workflow usa config, storage, trazabilidad y logger de core, y LLM, embeddings, chunking, OCR y AI Search de cognitive. El agente usa config, auth y logger de core, y agentes, memoria, MCP y LLM de cognitive. Ningún consumidor instala solo una.
- **Tamaño**: core tiene 5.278 líneas y cognitive 7.335. Sin lo que SUMMA deja fuera (A2A, alertas, evaluación, PII y safety, SQL, Fabric, FinOps) quedan unas 10.000.
- **El peso está en las dependencias.** En la base, las dependencias obligatorias meten LangGraph, FastAPI, uvicorn, pytest e IPython también en el clúster de Databricks.
- **En la base, la separación obligó a coordinar dos líneas de versiones**: cognitive pide `core>=0.4.8` mientras el workflow fija core 0.4.1. SUMMA arranca sin versiones previas.

### Decisión

Una sola librería con estas reglas:

1. **Dependencias obligatorias mínimas** y un extra por consumidor: uno para el agente y otro para el workflow. El workflow no instala LangGraph, FastAPI ni MCP, y el agente no instala Content Understanding.
2. **Las herramientas de desarrollo** (pytest, ruff, IPython) van solo en `requirements-dev.txt`, nunca en las dependencias de ejecución.
3. **El `__init__.py` raíz no reexporta módulos.** Los módulos de datos (`extraction`, `processing`, `vectordb`, `sources`, `storage`) no importan los de agentes (`agents`, `mcp`), ni al revés.
4. **Se parte en dos librerías** solo por replanning, si:
   - otro equipo pasa a ser dueño de una de las mitades;
   - las cadencias de versión divergen;
   - el Databricks Runtime obliga a fijar versiones que chocan con las del agente.

   Respetando la regla 3, partirla cuesta poco.

### Alternativas descartadas

- **Dos librerías como la base**: no aligera a ningún consumidor, porque los dos necesitan ambas, y abre dos líneas de versiones que hay que coordinar.
- **Código común dentro de cada plantilla**: duplica el código y las mejoras no llegan a los casos de uso ya clonados.

### Cómo se verifica

- **Humo por extra**: en un entorno limpio, instalar la wheel con **solo** ese extra e importar los módulos que usa ese consumidor. Si un import necesita otro extra, la prueba falla. Lo introduce LIB-01.
- **Fronteras de import (regla 3)**: un test que recorre los imports de los módulos de datos y de agentes y falla si cruzan la frontera. Lo introduce LIB-01.
- **Dependencias**: el revisor comprueba en cada PR que `pyproject.toml` no añade al grupo obligatorio dependencias de un solo consumidor.

---

## DEC-002 — Fronteras de import: módulos comunes, de workflow y de agente

- **Fecha**: 2026-11-13
- **Introducida en**: Constitución (`init/constitucion`)
- **Aplica a**: `src/summa_ai_framework/`, los extras de `pyproject.toml` y el test de fronteras de LIB-01
- **Estado**: vigente; confirmada por la persona el 2026-11-13. La comprobación negativa del humo cambió el 2026-11-20 (`replanning/2026-11-20-orden-y-humo.md`)
- **Reemplaza**: la regla 3 de DEC-001 y su verificación de fronteras

### Contexto

La regla 3 de DEC-001 separa módulos de datos y de agentes y prohíbe los imports en los dos sentidos. Al contrastarla con la base de referencia no se sostiene:

- La herramienta RAG vive en `agents` y necesita `vectordb` y `embeddings` (`BaseRef/cognitive/agents/tools/retrieval.py:12-13`). Con la regla 3, LIB-17 no se puede implementar.
- La memoria del agente necesita Cosmos DB, que el tech-stack ubicaba en `storage`, un módulo de datos. En la base el cliente de Cosmos de la memoria vive con la memoria (`BaseRef/cognitive/agents/memory/cosmos_db.py`).
- El validador JWT de la base importa FastAPI desde la librería común (`BaseRef/core/security/authentication.py:6-7`): por eso FastAPI llega al clúster de Databricks.
- El LLM de la base depende de LangChain (`BaseRef/cognitive/llms/protocols.py`), que el workflow no necesita.

### Decisión

Tres grupos de módulos:

| Grupo | Módulos | Dependencias |
|---|---|---|
| Comunes | `config`, `security`, `observability`, `llms`, `embeddings`, `vectordb` | Solo las obligatorias |
| Workflow | `storage`, `workflow`, `extraction`, `processing`, `sources` | Extra del workflow |
| Agente | `auth`, `agents` | Extra del agente |

1. Los grupos de workflow y de agente importan de los comunes. Nunca se importan entre sí.
2. Los módulos comunes no importan de ninguno de los otros dos grupos.
3. Cosmos DB vive en `agents/memory`, no en `storage`. `storage` es solo Unity Catalog.
4. El validador JWT vive en `auth` y no importa el framework web: el middleware lo pone la plantilla.
5. `llms` y `embeddings` usan el SDK de `openai`. El modelo con herramientas para LangGraph se construye en `agents`.
6. `observability` es solo el logger. El registro de ejecución en Unity Catalog vive en `workflow`.

### Alternativas descartadas

- **Mantener la regla 3 y mover la herramienta RAG a la plantilla del agente**: cada caso de uso clonado quedaría con su copia, que es lo que la librería evita ([[mission]] §2).
- **Duplicar la consulta a AI Search en `agents`**: dos implementaciones del mismo servicio, contra [[mission]] §5.

### Cómo se verifica

- **Fronteras de import**: un test recorre los imports y falla si un módulo de workflow importa uno de agente o al revés, o si un módulo común importa de cualquiera de los dos. Lo introduce LIB-01.
- **Humo por extra** de DEC-001: con solo un extra instalado, no está instalada ninguna distribución exclusiva del otro extra (las que declara y no son obligatorias ni del extra propio). Cambiado en `replanning/2026-11-20-orden-y-humo.md`; antes comprobaba que los módulos del otro grupo no se pudieran importar, lo que falla con los módulos que solo usan dependencias comunes. Lo implementa LIB-06.

---

## DEC-003 — Orquestación del agente: ciclo modelo ↔ herramientas con entidades previas

- **Fecha**: 2026-11-13
- **Introducida en**: Constitución (`init/constitucion`)
- **Aplica a**: `agents` (LIB-15 y LIB-16) y la creación del agente en `repo-agente-conversacional` (sus features 05 y 06)
- **Estado**: vigente

### Contexto

SyN, etapa 6, pide un "orquestador de tools (planner + executor) en LangGraph" e identificar las entidades de la consulta antes de invocar herramientas. Hay dos lecturas: un nodo que arma un plan de pasos y otro que lo ejecuta, o el ciclo en que el modelo decide en cada turno si llama una herramienta o responde. La base implementa el ciclo (`BaseRef/cognitive/agents/graph_builder.py:61-82`) y deja el plan-and-execute como grafo propio de cada caso de uso (`BaseRef/agent/app/agent/graph.py`).

### Decisión

Decisión de la persona, 2026-11-13:

1. El grafo por defecto es el ciclo: el nodo del modelo decide qué herramientas llamar ("planner") y el nodo de herramientas las ejecuta y devuelve su resultado ("executor"), hasta que el modelo responde.
2. Antes del ciclo corre un paso fijo de identificación de entidades (LIB-16); las entidades encontradas se pasan al ciclo y la herramienta RAG las usa como filtros.
3. Un caso de uso puede reemplazar el grafo por uno propio desde el punto de extensión de la plantilla, sin cambiar la librería.

### Alternativas descartadas

- **Nodo planificador explícito**: más llamadas al modelo y más código, sin un caso de uso que lo pida hoy. Queda disponible como grafo propio.

### Cómo se verifica

- Tests de LIB-15 con el doble del modelo: una consulta sin herramientas responde en un turno; una que pide una herramienta pasa por el nodo de herramientas y vuelve al modelo.
- Test de LIB-16: las entidades se extraen antes del primer turno del modelo y llegan al estado del grafo.
