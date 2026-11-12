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

- **Configuración**: esquemas pydantic y loader de YAML por ambiente con referencias a Key Vault.
- **Seguridad**: credenciales de Azure, lectura de secretos de Key Vault y validador de JWT por OIDC.
- **Trazabilidad**: logger y registro de ejecución con `run_id`, timestamps, métricas y causa de error, persistible en tablas de Unity Catalog (SyN, etapa 5).
- **Storage**: lectura y escritura de tablas y volúmenes de Unity Catalog por capa bronze/silver/gold; cliente de Cosmos DB.
- **LLM y embeddings**: clientes de Azure OpenAI.
- **Extracción**: cliente de Content Understanding que analiza un binario con el analizador indicado y devuelve el markdown y los campos con su confianza y su página (EjOCR, `src/extractor.py:39-49`).
- **Chunking**: estrategias por tokens, por estructura del documento (markdown) y semántica, con trazabilidad a documento y página, y lineamientos de cuándo usar cada una (SyN, etapa 5).
- **Búsqueda vectorial**: crear o actualizar un índice desde su definición, upsert, borrado por id y consulta híbrida con filtros. `[inferido]` de `BaseRef/cognitive/vectordb/azure_search.py:146-285`.
- **Fuentes HTTP**: cliente genérico con autenticación por API Key u OAuth, paginación, reintentos y respeto del rate limit (SyN, etapa 4).
- **Agentes**: grafo planner + executor sobre LangGraph, registro de herramientas, prompt principal desde plantilla Jinja e identificación de entidades antes de invocar herramientas (SyN, etapa 6).
- **Memoria**: historial y sesiones en Cosmos DB (SyN, etapa 6).
- **Herramienta RAG genérica**: consulta al índice con filtros por metadatos y devuelve las fuentes para citar (SyN, etapa 6).
- **MCP**: cliente MCP que expone las herramientas de un servidor como herramientas del agente (SyN, etapa 1).

### No entra

- **Capacidades de la base que SyN no pide** (decisión de la persona; quedan para replanning):
  - A2A entre agentes, herramienta SQL y almacenamiento en Fabric o SQL;
  - alertas, métricas Prometheus y FinOps;
  - evaluación con ragas o deepeval y datasets de fairness;
  - sanitización PII y Content Safety, salvo que lo exija la respuesta al `PENDIENTE` sobre datos personales de `repo-workflow` (su `mission.md` §7).
- **OCR con Document Intelligence**: solo si Content Understanding no cubre algún formato (SyN: "si es necesario").
- **Endpoints HTTP, jobs, steps y pipelines de despliegue**: son de las plantillas.
- **Conectores, esquemas, prompts o filtros de un dominio concreto**: son de los casos de uso.

## 3. Dependencias externas

| Dependencia | Quién la provee | Entorno o recurso | Notas |
|---|---|---|---|
| Feed de Azure Artifacts | SUMMA (Azure DevOps) | Un feed | PENDIENTE en [[tech-stack]] §7 |
| Servicios de Azure de dev para las pruebas de integración | IaC transversal | dev | SyN, etapa 1 |
| Workspace de Databricks para probar storage y trazabilidad | Arquitectura de datos | dev | SyN, etapa 2 |

## 4. Punto de partida

### Greenfield: activos heredados

Ninguno se copia. Los siguientes son guía de diseño (decisión de la persona):

| Activo de referencia | Guía para |
|---|---|
| `BaseRef/core/config/loader.py:110` y `config/schemas/` | Loader YAML y esquemas de configuración |
| `BaseRef/core/security/authentication.py:27-66` | Validación JWT por OIDC con JWKS |
| `BaseRef/core/observability/workflow_tracker.py:25` | Registro de ejecución |
| `BaseRef/core/storage/unity.py:25-222` | Tablas y volúmenes de Unity Catalog por capa |
| `BaseRef/cognitive/processing/chunking.py:14-128` | Interfaz de chunker y estrategias |
| `BaseRef/cognitive/vectordb/azure_search.py:30-325` | Índice, upsert, borrado y búsqueda híbrida |
| `BaseRef/cognitive/agents/graph_builder.py:20` | Construcción del grafo del agente |
| `BaseRef/cognitive/agents/memory/cosmos_db.py:94-218` | Memoria de conversación y sesiones |
| `BaseRef/cognitive/agents/tools/retrieval.py:44` | Herramienta RAG desde configuración |
| `BaseRef/cognitive/mcp/client.py:103` | Cliente MCP |
| EjOCR, `src/extractor.py` | Llamada a Content Understanding |

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
