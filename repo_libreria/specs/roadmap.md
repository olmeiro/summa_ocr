# Roadmap — Librería del framework de IA (repo-libreria)

> Constitución. Secuencia de features pequeñas, implementables y verificables, con su estado.

Derivado de [[mission]], [[alcance-inicial]] y SyN (etapas 4 a 6). Las plantillas citan estas features como `LIB-NN`.

---

## 1. Principios de secuenciación

1. **Base antes que features**: configuración, contratos y el gate en verde van primero.
2. **La primera feature es manejable, no la más riesgosa**: sirve para probar el flujo y la arquitectura.
3. **Cada feature deja el sistema funcionando** y es verificable por sí sola: termina con una versión publicable.
4. **Replanning entre fases**: se revisa si el plan sigue siendo válido.
5. **El orden lo marcan las plantillas**: primero lo que necesita el recorrido mínimo del workflow (documento → índice) y después lo del agente.
6. **Cada capacidad nace con su interfaz y su doble de prueba**, para que las plantillas puedan probar sin Azure.

## 2. Fases

### Fase 0 — Constitución

`mission`, `tech-stack`, `alcance-inicial` y este roadmap. **Salida**: base documental versionada.

### Fase 1 — Paquete base

Estructura, configuración, secretos y publicación. **Salida**: la versión `0.1.0` está publicada en el feed. Instalada con **solo** un extra en un entorno limpio, importa los módulos de ese consumidor ([[decisions]] DEC-001 y DEC-002) y carga un YAML con un secreto de Key Vault.

### Fase 2 — Servicios para el workflow

Almacenamiento en Unity Catalog, contexto de workflow, trazabilidad, LLM y embeddings, extracción, chunking, búsqueda vectorial y fuentes HTTP. **Salida**: con solo la librería se puede llevar un documento de prueba a un índice de AI Search, con el registro de la ejecución en tablas de Unity Catalog.

### Fase 3 — Piezas del agente

Autenticación, memoria, grafo, entidades y herramienta RAG. **Salida**: con solo la librería se arma un agente que valida el JWT, recuerda la sesión, invoca la herramienta RAG y responde con fuentes.

## 3. Features

| ID | Nombre | Fase | Depende de | Estado | Carpeta |
|---|---|---|---|---|---|
| 01 | esqueleto-paquete: `pyproject.toml`, `src/`, extras, build de la wheel, humo por extra y test de fronteras de import (DEC-001, DEC-002) | 1 | — | accepted | `features/01-esqueleto-paquete/` |
| 02 | config-loader: esquemas pydantic y loader de YAML; las referencias a secretos las resuelve un proveedor, aquí el de variables de entorno | 1 | 01 | accepted | `features/02-config-loader/` |
| 03 | secretos-identidad: credenciales de Azure y proveedor de secretos de Key Vault para el loader | 1 | 02 | not_started | `features/03-secretos-identidad/` |
| 04 | publicacion-feed: pipeline de Azure DevOps (gate, build y publicación en el feed) | 1 | 01 | not_started | `features/04-publicacion-feed/` |
| 05 | almacenamiento-unity: lectura y escritura de tablas y volúmenes de Unity Catalog por capa, con escritura idempotente por clave | 2 | 02 | not_started | `features/05-almacenamiento-unity/` |
| 06 | contexto-workflow: manifest `requires`/`provides`, contexto de step (entradas, salidas y `run_id`) y validación del DAG | 2 | 02 | not_started | `features/06-contexto-workflow/` |
| 07 | trazabilidad-ejecuciones: logger y registro por ejecución, step y documento en tablas de Unity Catalog de la iniciativa, con su definición y su creación si no existen | 2 | 05, 06 | not_started | `features/07-trazabilidad-ejecuciones/` |
| 08 | llm-embeddings: clientes de Azure OpenAI para chat y embeddings, con reintentos | 2 | 03 | not_started | `features/08-llm-embeddings/` |
| 09 | extraccion-content-understanding: crear o actualizar un analizador desde su definición, y analizar PDF, Word o imagen a markdown y campos con confianza y página | 2 | 03 | not_started | `features/09-extraccion-content-understanding/` |
| 10 | chunking: estrategias por tokens, por estructura y semántica, con documento y página por chunk, y lineamientos | 2 | 08 | not_started | `features/10-chunking/` |
| 11 | busqueda-vectorial: índice desde su definición, upsert, borrado por id y por documento, y consulta híbrida con filtros estructurados | 2 | 03 | not_started | `features/11-busqueda-vectorial/` |
| 12 | fuentes-http: cliente genérico con auth, paginación, reintentos y rate limit | 2 | 03 | not_started | `features/12-fuentes-http/` |
| 13 | auth-jwt: validador OIDC (emisor, audiencia y JWKS), sin depender del framework web; debe aceptar los tokens de Bot Framework que recibe el agente | 3 | 02 | not_started | `features/13-auth-jwt/` |
| 14 | memoria-cosmos: historial y sesiones en Cosmos DB, con retención configurable (TTL) | 3 | 03 | not_started | `features/14-memoria-cosmos/` |
| 15 | grafo-agente: ciclo modelo ↔ herramientas (DEC-003), registro de herramientas y prompt Jinja | 3 | 08 | not_started | `features/15-grafo-agente/` |
| 16 | entidades-consulta: paso previo al ciclo que identifica las entidades de la consulta (DEC-003) | 3 | 15 | not_started | `features/16-entidades-consulta/` |
| 17 | herramienta-rag: consulta al índice con filtros y fuentes estructuradas para citar | 3 | 11, 15 | not_started | `features/17-herramienta-rag/` |

Estados: `not_started → in_progress → passing → accepted` (ver [[orden_spec]] §6). Una feature solo pasa a `accepted` con el veredicto `accept` del revisor.

- La feature 04 depende de que exista el feed. Mientras tanto, las plantillas pueden instalar la librería desde una ruta local en desarrollo.
- El cliente MCP salió del roadmap el 2026-11-13 (decisión de la persona); entra por replanning ([[alcance-inicial]] §2).

## 4. Punto de partida de cada feature

Qué ofrece la base para cada feature y qué debe resolver su spec. Se usa como guía de diseño, sin copiar código ([[mission]]). `core/…` y `cognitive/…` abrevian `BaseRef/core/…` y `BaseRef/cognitive/…`. Lo que aquí "no se trae" está fuera de alcance ([[alcance-inicial]] §2).

| ID | Referencia | Lo que cambia respecto a la referencia |
|---|---|---|
| 01 | `core/pyproject.toml`, `cognitive/pyproject.toml`: setuptools, `src/`, `requires-python >=3.10` | Aquí `summa-ai-framework` con `requires-python >=3.12` y `--cov-fail-under=80` en el gate ([[tech-stack]] §1 y §11). Sus dependencias obligatorias incluyen FastAPI, pytest e IPython (`core/pyproject.toml:54-63`): es lo que evita DEC-001. |
| 02 | `core/config/loader.py:110-144`; `core/config/base.py` (campos desconocidos prohibidos); `core/config/schemas/solution.py`: un esquema raíz con secciones opcionales por consumidor | Sustituye `${NOMBRE}` sobre el texto antes de parsear el YAML (`loader.py:21-36`, `134`): un secreto con caracteres de YAML altera la estructura; aquí se resuelve sobre los valores ya parseados. No se trae la validación contra un registro de soluciones en Cosmos (`loader.py:39-106`). Las claves son `str` en sus esquemas: aquí, un tipo que no se imprima en logs. |
| 03 | `core/security/secrets.py:24-112`: interfaz, proveedor por variables de entorno y proveedor de Key Vault con `DefaultAzureCredential` | El proveedor por entorno ya existe desde la 02 y sirve de doble. La base cambia `_` por `-` al buscar el secreto (`secrets.py:85`). |
| 04 | `BaseRef/*/Pipeline/main-pipeline.yml` | Solo declaran ramas y variables por ambiente. Los pasos de build y publicación están en una plantilla externa que no está en `project-context/`: se escriben desde cero. |
| 05 | `core/storage/unity.py:25-234` | Esquemas `<iniciativa>_<capa>` y volúmenes en `/Volumes/<catálogo>/<iniciativa>_<capa>/`, creados al arrancar (`unity.py:73-80`). Solo sobrescribe o añade: falta la escritura por clave que pide el incremental. Los identificadores llegan a SQL sin validar. No se trae la escritura para Fabric (`unity.py:111-128`). No tiene doble: los tests de la base simulan Spark. |
| 06 | `core/devops/workflow.py:11-346`; manifest de ejemplo en `BaseRef/workflow/config/workflow_manifest.yaml` | Llama `inputs`/`outputs` a lo que SyN llama `requires`/`provides`. Pone el `run_id` en el nombre de cada tabla (`workflow.py:158`), así que nada persiste entre ejecuciones; aquí los nombres son estables. No valida el manifest ni deduce el orden. Pasa rutas entre tareas con TaskValues de Databricks (`workflow.py:313-346`). |
| 07 | `core/observability/workflow_tracker.py:25-735`, `logger.py:8-157`, `core/utils/errors.py:8-131` | Escribe en cinco tablas de un esquema transversal y no trae su definición. No registra por documento. Un fallo al escribir queda en un warning (`workflow_tracker.py:286`, `368`, `616`). Arma SQL con valores interpolados (`:292-311`). No se traen alertas, costo de DBU ni registro de artefactos (`:402`, `:619`, `:667`). Aquí las tablas son de cada iniciativa, no transversales, y la librería las crea si no existen ([[alcance-inicial]] §2). |
| 08 | `cognitive/llms/protocols.py`, `llms/azure_openai.py:14-213`, `embeddings/azure_foundry.py:9-87` | Solo clave de API y sin reintentos. `embed_query` es síncrono y la herramienta RAG lo llama desde código asíncrono (`cognitive/agents/tools/retrieval.py:83`). Su LLM depende de LangChain (`bind_tools`): aquí el cliente común usa el SDK de `openai`, y el modelo con herramientas se arma en la 15 (DEC-002). No se trae la generación con imagen. |
| 09 | EjOCR `src/extractor.py:39-49`. En la base solo hay OCR a texto plano (`cognitive/ocr/azure_doc_intel.py:10-61`) | Forma del resultado (EjOCR, `data/processed/*.json`): `contents[0].markdown`; `fields` anidados por categoría; cada campo con `confidence`, `source` (`D(página,…)`) y `spans` sobre el markdown. Un campo sin valor llega con `confidence` y sin valor. EjOCR fija el tipo `application/pdf` (`extractor.py:42`); aquí el tipo sale de la extensión, porque Word va directo. EjOCR usa un analizador creado a mano (`extractor.py:40`); aquí se crea o actualiza desde su definición versionada en el caso de uso. |
| 10 | `cognitive/processing/chunking.py:14-157` | `split_text` devuelve solo textos, sin documento ni página. Mide en caracteres: no hay estrategia por tokens. Usa `langchain-text-splitters` y `langchain_experimental`, que aquí también se usan ([[tech-stack]] §5). La página no sale sola del markdown: un documento de 30 páginas trae 27 marcas `<!-- PageBreak -->` y `pages[]` sin `spans` (EjOCR, `data/processed/82325.json`). `tiktoken` descarga su codificación en el primer uso; la base la precarga en su imagen (`BaseRef/agent/Dockerfile:60`). |
| 11 | `cognitive/vectordb/protocols.py`, `azure_search.py:30-375` | Esquema fijo `id`, `content`, `content_vector` y `metadata_json`, más los campos declarados (`:146-204`); analizador `es.microsoft` fijo (`:161`). Filtros como texto OData libre (`:263`, `:285`). Solo borra por id (`:258`). `create_index` no crea la configuración semántica que la consulta usa (`:325`). Cliente síncrono para indexar (`:133`) y asíncrono para consultar (`:309`). |
| 12 | Sin referencia en la base. EjOCR `src/api_client.py:22-36` es el contraejemplo: cookies de una sesión en el código | Diseño nuevo desde SyN, etapa 4. |
| 13 | `core/security/authentication.py:26-131` | Importa FastAPI y lanza sus errores HTTP (`:6-7`, `:125-131`): aquí el validador no conoce el framework y el middleware queda en la plantilla. Con la autenticación desactivada devuelve un usuario falso (`:76-79`): no se trae. Usa por defecto el emisor de la versión 1 con los metadatos de la versión 2 (`core/config/schemas/security.py:105-111`). |
| 14 | `cognitive/agents/memory/protocols.py:11-72`, `cosmos_db.py:94-501`; doble en `in_memory.py` | Dos interfaces, historial y sesiones; contenedores `sessions` y `messages` con partición por `session_id`. No se trae el voto (`cosmos_db.py:363`), el contenedor de alertas ni las estadísticas de tokens y costo por sesión ([[tech-stack]] §10). El historial expira por TTL; el agente usa 90 días. |
| 15 | `cognitive/agents/graph_builder.py:16-242`, `factory.py:41-210`, `implementation.py:13-231`, `tools/base.py`, `cognitive/utils/prompts.py:87-119` | Su ciclo agente ↔ herramientas (`graph_builder.py:61-82`) es el que adopta DEC-003. Sirven de guía el registro de herramientas, el nodo que las ejecuta y captura sus errores, y el envoltorio memoria ↔ grafo. No se traen métricas, alertas, A2A ni SQL. |
| 16 | Sin referencia en la base | Diseño nuevo desde SyN, etapa 6. Las entidades llegan al estado del grafo y la herramienta RAG las usa como filtros (DEC-003). |
| 17 | `cognitive/agents/tools/retrieval.py:44-123` | No acepta filtros, devuelve un texto sin fuentes estructuradas y abre un cliente por llamada (`:66-93`). |

## 5. Cierre del roadmap

- Todas las features en `accepted` y publicadas en el feed.
- `repo-workflow` y `repo-agente-conversacional` usan una versión publicada de la librería, sin código duplicado de ella.
- Los objetivos medibles de [[mission]] §6 tienen umbral y se cumplen.
