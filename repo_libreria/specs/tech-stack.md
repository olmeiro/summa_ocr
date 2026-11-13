# Tech-stack — Librería del framework de IA (repo-libreria)

> Constitución. Define el **marco técnico común**. Cualquier desviación se registra en [[decisions]] o en `replanning/`.

**Fuentes**: SyN, BaseRef y EjOCR (ver [[mission]]), el harness de este repo y decisiones de la persona del 2026-11-12.

---

## 1. Lenguaje y framework

- **Lenguaje y versión**: Python. PENDIENTE: ¿versión mínima? Debe coincidir con la del Databricks Runtime que use `repo-workflow` (la base usa 17.3; `BaseRef/workflow/databricks.yml:66`) y con la imagen del agente. La base declara `>=3.10` (`BaseRef/core/pyproject.toml:12`) y su imagen del agente usa 3.12 (`BaseRef/agent/Dockerfile:4`).
- **Empaquetado**: `pyproject.toml` con `[project]`, código en `src/<paquete>/` y distribución como wheel (`BaseRef/core/pyproject.toml`). Una sola librería con extras por consumidor ([[decisions]] DEC-001 y DEC-002). PENDIENTE: ¿nombre del paquete?
- **Nombres**: el paquete, los módulos y las claves de configuración llevan nombres de SUMMA. El código no importa paquetes de la base ni conserva sus nombres (decisión de la persona, 2026-11-12).
- **Gestor de dependencias**: `uv` en desarrollo; el gate usa `requirements-dev.txt` (`AGENTS.md`).

## 2. Convenciones de código

- Lint, formato, tipos y tests los verifica el gate: `python scripts/gate.py`, configurado en `pyproject.toml`. `src` se añade a `[tool.mypy] files`.
- Cada servicio externo tiene una interfaz (`Protocol`), una o más implementaciones y una fábrica que elige según la configuración. `[inferido]` de `BaseRef/cognitive/*/protocols.py` y `factory.py`.
- La API pública se exporta en el `__init__.py` de cada módulo; lo demás es interno.
- El `__init__.py` raíz no reexporta módulos. Los módulos de workflow y los de agente importan de los comunes y nunca entre sí ([[decisions]] DEC-002).
- Ningún valor externo se interpola en SQL ni en filtros: los identificadores de Unity Catalog se validan y los filtros de búsqueda se construyen desde una estructura. La base interpola ambos (`BaseRef/core/storage/unity.py:79-80`, `BaseRef/core/observability/workflow_tracker.py:292-311`).
- Un fallo al escribir el registro de ejecución hace fallar el step. `[inferido]`: la base lo deja en un warning y la auditoría se pierde sin aviso (`BaseRef/core/observability/workflow_tracker.py:286`, `368`).
- Docstrings, mensajes de error y commits en español, como el harness (`orden_spec.md` §11).

## 3. Estructura de módulos

`[inferido]` de la unión de `BaseRef/core/` y `BaseRef/cognitive/`, recortada al alcance de SyN y agrupada según [[decisions]] DEC-002:

```text
src/<paquete>/
│  Comunes
├─ config/         # esquemas pydantic y loader YAML con referencias a secretos
├─ security/       # identidad de Azure y proveedores de secretos (entorno y Key Vault)
├─ observability/  # logger
├─ llms/           # Azure OpenAI (chat) con el SDK de openai
├─ embeddings/     # Azure OpenAI (embeddings)
├─ vectordb/       # Azure AI Search: definición del índice, upsert, borrado y consulta con filtros
│  Workflow
├─ storage/        # tablas y volúmenes de Unity Catalog por capa
├─ workflow/       # manifest requires/provides, contexto de step y registro de ejecución
├─ extraction/     # Content Understanding: markdown + campos con confianza y página
├─ processing/     # chunking
├─ sources/        # cliente genérico de fuentes HTTP (paginación, reintentos, rate limit)
│  Agente
├─ auth/           # validación JWT (OIDC)
├─ agents/         # grafo planner + executor, registro de herramientas, entidades, memoria en Cosmos DB, herramienta RAG
└─ mcp/            # cliente MCP
tests/
```

ADLS no tiene cliente propio: se accede a través de las tablas y los volúmenes de Unity Catalog (SyN, etapa 2).

## 4. Interfaces expuestas

- **API pública de Python**: módulos y fábricas de §3. Versionado semántico; la feature 01 define qué cuenta como API pública.
- **Versiones**: la primera versión publicada es `0.1.0` y las plantillas fijan la versión exacta. Mientras sea `0.x`, la API pública puede cambiar entre versiones menores, con nota en el changelog. `[inferido]`
- **Extras por consumidor**: uno para el agente y otro para el workflow. Los nombres se fijan en la feature 01.
- **Esquemas de configuración** (pydantic): contrato con los archivos YAML de las plantillas. La definición del índice de AI Search (campos, filtrables, enlace al documento, página, dimensiones y configuración semántica) es un solo esquema que usan las dos plantillas: es el contrato del índice entre ellas. `[inferido]`: en la base, quien crea el índice y quien lo consulta no comparten esa definición (`BaseRef/cognitive/vectordb/azure_search.py:146-204` frente a `:325`).

## 5. Dependencias

### Base

Previstas `[inferido]` de `BaseRef/core/pyproject.toml` y `BaseRef/cognitive/pyproject.toml`; se fijan con versión en la feature que las introduce:

- **Comunes**: `pydantic`, `pyyaml`, `azure-identity`, `azure-keyvault-secrets`, `openai`, `azure-search-documents`, `tenacity`.
- **Extra del agente**: `langgraph`, `langchain-openai`, `azure-cosmos`, `jinja2`, `mcp`, un cliente HTTP para JWKS y una librería de JWT (la base usa `httpx` y `python-jose`).
- **Extra del workflow**: `azure-ai-contentunderstanding` (EjOCR, `src/extractor.py:7`), `tiktoken` para el chunking por tokens y un cliente HTTP para las fuentes. PySpark y Delta los provee el clúster. La librería de particionado de texto depende del `PENDIENTE` de [[alcance-inicial]] §2.
- **Desarrollo**: pytest, ruff, mypy e IPython solo en `requirements-dev.txt`, nunca en las dependencias de ejecución ([[decisions]] DEC-001).

### Añadidas por features

Ninguna todavía.

## 6. Servicios externos

| Servicio | Uso | Autenticación |
|---|---|---|
| Azure OpenAI (AI Foundry) | Chat y embeddings | Clave en Key Vault o identidad. PENDIENTE: ¿cuál de las dos? La base usa clave de API guardada en Key Vault para todos los servicios, e identidad solo para llegar a Key Vault (`BaseRef/workflow/config/config.yaml:9-18`) |
| Azure AI Content Understanding (AI Foundry) | Extracción de documentos | Ídem |
| Azure AI Search | Índices y consultas | Ídem |
| Azure Cosmos DB | Historial y sesiones del agente | Ídem |
| Azure Key Vault | Secretos referenciados desde la configuración | Identidad de Azure (`azure-identity`) |
| Unity Catalog y ADLS | Tablas y volúmenes del workflow | Contexto del clúster de Databricks |
| Azure Artifacts | Publicación del paquete | Service connection de Azure DevOps |

## 7. Entornos

La librería no se despliega: cada plantilla instala una versión publicada en su ambiente (dev o prod). PENDIENTE: ¿nombre del feed de Azure Artifacts, y se separan versiones preliminares de las estables?

## 8. Configuración y secretos

- La librería no lee variables de entorno propias, salvo las de identidad de Azure. Recibe la configuración ya cargada por la plantilla.
- Los YAML de configuración referencian secretos por nombre (`${NOMBRE}`) y el loader los resuelve al cargar, con el proveedor que indique el propio YAML: variables de entorno o Key Vault. `[inferido]` de `BaseRef/core/config/loader.py:110-144` y `BaseRef/core/security/secrets.py:24-112`.
- El proveedor por variables de entorno es el que usan los tests y el desarrollo local: el gate no llama a Key Vault.
- Los valores resueltos son secretos: no aparecen en logs ni en mensajes de error.

## 9. Seguridad

- **JWT**: validación OIDC con emisor, audiencia y llaves JWKS en caché. `[inferido]` de `BaseRef/core/security/authentication.py:26-131`. No hay modo sin autenticación ni usuario de desarrollo: la base lo trae (`authentication.py:76-79`) y aquí no entra ([[mission]] de `repo-agente-conversacional`, principio 3).
- **Sin secretos en el paquete**: ni en el código, ni en los ejemplos, ni en los tests.
- **Feed desde Databricks**: PENDIENTE: ¿cómo instalan los clústeres el paquete del feed privado sin poner credenciales en `databricks.yml`? La base no lo resuelve: deja la credencial del feed en claro en las variables del clúster (`BaseRef/workflow/databricks.yml:109`). Opciones: que el pipeline publique la wheel en un volumen de Unity Catalog y el job la declare como librería, o que el clúster lea la credencial de un secret scope.
- Toda entrada que llega a filtros de AI Search u OData, o a SQL de Unity Catalog, se valida o se escapa en la librería (§2).

## 10. Observabilidad

- **Logger**: común a las dos plantillas (`BaseRef/core/observability/logger.py:8-157`).
- **Registro de ejecución**: `run_id`, timestamps y causa de error por ejecución, step y documento, en tablas de Unity Catalog. Lo usa solo el workflow (SyN, etapa 5; `BaseRef/core/observability/workflow_tracker.py:25`). La base registra por ejecución y por step, no por documento.
- PENDIENTE (decisión de la persona, 2026-11-12): ¿destino de trazas y métricas del agente? La base exporta con OpenTelemetry a consola u OTLP.

## 11. Testing

- **Unitarias**: pytest dentro del gate, con dobles de cada interfaz; nada llama a Azure.
- **Integración o contrato**: por cada implementación, contra los servicios de dev, fuera del gate. PENDIENTE: ¿dónde y cuándo se ejecutan?
- **Humo**: por cada extra, instalar la wheel con **solo** ese extra en un entorno limpio e importar los módulos de ese consumidor ([[decisions]] DEC-001).
- **Fronteras de import**: un test falla si los módulos de workflow y los de agente se importan entre sí, o si un módulo común importa de ellos ([[decisions]] DEC-002).
- **Dobles**: cada interfaz trae su doble en el paquete, para que las plantillas prueben sin Azure ni Spark. La base solo lo tiene para la memoria (`BaseRef/cognitive/agents/memory/in_memory.py`); para probar sus steps sustituye la librería entera (`BaseRef/workflow/tests/test_steps/test_s05_indexing.py:11-31`).
- **Evidencia aceptada para cerrar una feature**: PENDIENTE: ¿basta el gate o se exige la prueba de integración de la implementación tocada?

## 12. CI/CD y despliegue

- **Plataforma**: Azure DevOps (decisión de la persona). El gate y el revisor del harness se portan a Azure Pipelines al mover el harness.
- **Pipeline**: gate → build de la wheel → publicación en el feed al integrar en la rama principal con una versión nueva. `[inferido]`: los pipelines de la base solo declaran ramas y variables; sus pasos están en una plantilla externa que no está en `project-context/` (`BaseRef/core/Pipeline/main-pipeline.yml:30-41`), así que este se escribe desde cero.
- **Ramas**: el harness usa `feature/NN-nombre` → `main`; la base usa `Develop`, `Integration` y `master` para dev, qa y prod (`BaseRef/core/Pipeline/main-pipeline.yml:1-23`). PENDIENTE: ¿qué modelo de ramas se usa?
- **Aprobación de versiones**: PENDIENTE: ¿quién aprueba publicar una versión?

## Relación con otros documentos

- [[mission]] — el porqué que justifica este stack.
- [[alcance-inicial]] — dependencias externas y punto de partida.
- [[roadmap]] — en qué orden entran estos componentes.
- [[decisions]] — decisiones técnicas que complementan este documento.
