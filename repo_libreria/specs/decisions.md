# Decisiones técnicas

> Decisiones que aplican a **todo el proyecto**, no a una feature. Las features las citan con `[[decisions]]` y su `DEC-NNN` en lugar de repetir el razonamiento.
> Una decisión no se borra: se reemplaza con otra que indique `Reemplaza: DEC-NNN`.

Se añade una entrada cuando una decisión debe respetarse en varias features, copiando la estructura de DEC-001 con el siguiente número.

---

## DEC-001 — Una sola librería con extras por consumidor

- **Fecha**: 2026-11-12
- **Introducida en**: Constitución (`init/constitucion`)
- **Aplica a**: todo el paquete, su `pyproject.toml` y las dos plantillas que lo instalan
- **Estado**: vigente

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
