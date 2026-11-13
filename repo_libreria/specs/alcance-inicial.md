# Alcance inicial — Librería del framework de IA (repo-libreria)

> Constitución. Define qué entra y qué no, de qué depende el proyecto y desde dónde arranca.

**Fuentes**: SyN, BaseRef y EjOCR (ver [[mission]]) y decisiones de la persona del 2026-11-12.

---

## 1. Posición del componente

```text
                 [ repo-libreria ] ──build──► wheel ──► feed de Azure Artifacts de SUMMA
                                                             │
                     ┌───────────────────────────────────────┴──────────────────┐
                     ▼                                                          ▼
   repo-workflow y sus clones (Databricks)              repo-agente-conversacional y sus clones
   extra del workflow                                   (Container Apps), extra del agente
```

## 2. Alcance funcional

### Entra

Capacidades genéricas que piden SyN (etapas 5 y 6) y las decisiones de la persona:

- **Configuración**: esquemas pydantic y loader de YAML con referencias a secretos. Cada plantilla elige el archivo de su ambiente.
- **Seguridad**: credenciales de Azure, proveedores de secretos (variables de entorno y Key Vault) y validador de JWT por OIDC.
- **Storage**: lectura y escritura de tablas y volúmenes de Unity Catalog por capa bronze/silver/gold, con escritura idempotente por clave.
- **Contexto de workflow**: lectura del manifest `requires`/`provides`, contexto de cada step (de dónde lee, dónde escribe y con qué `run_id`) y validación del DAG (SyN, etapa 5). En la base vive en la librería (`BaseRef/core/devops/workflow.py:11-346`); si quedara en la plantilla, cada caso de uso clonado tendría su copia (confirmado por la persona, 2026-11-13).
- **Trazabilidad**: logger y registro por ejecución, step y documento, con `run_id`, timestamps, métricas y causa de error, en tablas de Unity Catalog de cada iniciativa cuya definición (esquema y particionado) y creación entrega la librería (SyN, etapa 5; tablas por iniciativa, decisión de la persona, 2026-11-13).
- **LLM y embeddings**: clientes de Azure OpenAI con reintentos; el de embeddings ofrece también llamada asíncrona para el agente. Los deployments los elige cada caso de uso en su configuración.
- **Extracción**: cliente de Content Understanding que crea o actualiza un analizador desde su definición versionada y analiza un binario (PDF, Word o imagen, con el tipo de contenido según la extensión) para devolver el markdown y los campos con su confianza y su página (EjOCR, `src/extractor.py:39-49`; analizador desde esquema y Word directo, decisiones de la persona, 2026-11-13).
- **Chunking**: estrategias por tokens, por estructura del documento (markdown) y semántica, con trazabilidad a documento y página, y lineamientos de cuándo usar cada una (SyN, etapa 5).
- **Búsqueda vectorial**: crear o actualizar un índice desde su definición, upsert, borrado por id y por documento, y consulta híbrida con filtros estructurados. Derivada de `BaseRef/cognitive/vectordb/azure_search.py:146-285`; el borrado por documento lo exige el incremental de `repo-workflow` y la base no lo tiene.
- **Fuentes HTTP**: cliente genérico con autenticación por API Key u OAuth, paginación, reintentos y respeto del rate limit (SyN, etapa 4).
- **Agentes**: grafo sobre LangGraph en que el modelo elige herramientas en cada turno, precedido por la identificación de entidades de la consulta ([[decisions]] DEC-003); registro de herramientas y prompt principal desde plantilla Jinja (SyN, etapa 6).
- **Memoria**: historial y sesiones en Cosmos DB, con su cliente y un tiempo de retención configurable (SyN, etapa 6).
- **Herramienta RAG genérica**: consulta al índice con filtros por metadatos y devuelve las fuentes como datos (documento, página y enlace), no solo como texto (SyN, etapa 6 y arquitectura §3).

### No entra

- **Capacidades de la base que SyN no pide** (decisión de la persona; quedan para replanning):
  - A2A entre agentes, herramienta SQL y almacenamiento en Fabric o SQL;
  - alertas, métricas Prometheus y FinOps;
  - evaluación con ragas o deepeval y datasets de fairness;
  - sanitización PII y Content Safety, salvo que lo exija la respuesta al `PENDIENTE` sobre datos personales de `repo-workflow` (su `mission.md` §7);
  - telemetría con OpenTelemetry y medición de tokens o costo.
- **Cliente MCP**: fuera por ahora (decisión de la persona, 2026-11-13). SyN, etapa 1, pide un "MCP client stub"; entra por replanning cuando un caso de uso lo necesite. Guía para entonces: `BaseRef/cognitive/mcp/client.py:103-946`.
- **OCR con Document Intelligence**: solo si Content Understanding no cubre algún formato (SyN: "si es necesario").
- **Endpoints HTTP, jobs, steps y pipelines de despliegue**: son de las plantillas.
- **Conectores, esquemas, prompts o filtros de un dominio concreto**: son de los casos de uso.
- **De la base, además**: el registro central de soluciones que su loader consulta en Cosmos (`BaseRef/core/config/loader.py:39-106`), el voto de respuestas, el registro de artefactos y el costo de DBU de su trazabilidad.

### Decidido el 2026-11-13

- **Orquestación**: el modelo elige herramientas en cada turno, como el grafo de la base (`BaseRef/cognitive/agents/graph_builder.py:61-82`), con la identificación de entidades como paso fijo previo ([[decisions]] DEC-003).
- **Chunking**: `langchain-text-splitters` y `langchain-experimental` en el extra del workflow, como la base.
- **MCP**: fuera por ahora (ver "No entra").

## 3. Dependencias externas

| Dependencia | Quién la provee | Entorno o recurso | Notas |
|---|---|---|---|
| Feed de Azure Artifacts | Equipo de plataforma (Azure DevOps) | Un feed | No existe todavía; ver [[tech-stack]] §7 |
| Servicios de Azure de dev para las pruebas de integración | IaC transversal | dev | SyN, etapa 1 |
| Workspace de Databricks para probar storage y trazabilidad | Arquitectura de datos | dev | SyN, etapa 2 |

## 4. Punto de partida

### Greenfield: activos heredados

Ninguno se copia. Los siguientes son guía de diseño (decisión de la persona). Qué cambia en cada uno está en [[roadmap]] §4:

| Activo de referencia | Guía para |
|---|---|
| `BaseRef/core/config/loader.py:110` y `config/schemas/` | Loader YAML y esquemas de configuración |
| `BaseRef/core/security/secrets.py:24-112` | Proveedores de secretos |
| `BaseRef/core/security/authentication.py:26-131` | Validación JWT por OIDC con JWKS |
| `BaseRef/core/devops/workflow.py:11-346` | Manifest y contexto de step |
| `BaseRef/core/observability/workflow_tracker.py:25` | Registro de ejecución |
| `BaseRef/core/storage/unity.py:25-234` | Tablas y volúmenes de Unity Catalog por capa |
| `BaseRef/cognitive/processing/chunking.py:14-128` | Interfaz de chunker y estrategias |
| `BaseRef/cognitive/vectordb/azure_search.py:30-325` | Índice, upsert, borrado y búsqueda híbrida |
| `BaseRef/cognitive/agents/graph_builder.py:20` | Construcción del grafo del agente |
| `BaseRef/cognitive/agents/memory/cosmos_db.py:94-218` | Memoria de conversación y sesiones |
| `BaseRef/cognitive/agents/tools/retrieval.py:44` | Herramienta RAG desde configuración |
| EjOCR, `src/extractor.py` y `data/processed/*.json` | Llamada a Content Understanding y forma de su resultado |

Sin referencia en la base: el cliente de fuentes HTTP, la identificación de entidades, la creación del analizador de Content Understanding, el registro por documento, el chunking por tokens y la página de cada chunk.

## 5. Coordinación con otros equipos o sistemas

- **`repo-workflow` y `repo-agente-conversacional`**: cada feature de una plantilla que necesita una capacidad nueva depende de la feature de la librería que la entrega y de su publicación en el feed. Los cambios de API pública se anuncian en el changelog.
- **Plataforma**: feed, permisos de publicación y acceso desde Databricks y Container Apps.

## 6. Principios del alcance

- Entra lo que necesitan dos o más casos de uso y no depende de un dominio.
- Lo que solo personaliza una plantilla (endpoints, steps, prompts) se queda en la plantilla.
- Nada que SyN no pida: las capacidades nuevas entran por replanning.

## Relación con otros documentos

- [[mission]] — por qué existe el proyecto.
- [[tech-stack]] — con qué se construye.
- [[roadmap]] — en qué orden se entrega este alcance.
