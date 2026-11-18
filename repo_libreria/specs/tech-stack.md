# Tech-stack — Librería del framework de IA (repo-libreria)

> Constitución. Define el **marco técnico común**. Cualquier desviación se registra en [[decisions]] o en `replanning/`.

**Fuentes**: SyN, BaseRef y EjOCR (ver [[mission]]), el harness de este repo y decisiones de la persona del 2026-11-12 y 2026-11-13.

---

## 1. Lenguaje y framework

- **Lenguaje y versión**: Python 3.12, `requires-python = ">=3.12"` (decisión de la persona, 2026-11-13). Los Databricks Runtime vigentes (17.3 LTS, 18 LTS y 19) traen Python 3.12.3 (Microsoft Learn, notas de versión de Databricks Runtime), y la imagen del agente usa `python:3.12-slim`. La versión exacta del runtime la fija `repo-workflow`.
- **Empaquetado**: `pyproject.toml` con `[project]`, código en `src/summa_ai_framework/` y distribución como wheel (`BaseRef/core/pyproject.toml`). Una sola librería con extras por consumidor ([[decisions]] DEC-001 y DEC-002). Nombre del paquete: `summa-ai-framework`, import `summa_ai_framework` (decisión de la persona, 2026-11-13).
- **Nombres**: el paquete, los módulos y las claves de configuración llevan nombres de SUMMA. El código no importa paquetes de la base ni conserva sus nombres (decisión de la persona, 2026-11-12).
- **Gestor de dependencias**: `uv` en desarrollo; el gate usa `requirements-dev.txt` (`AGENTS.md`).

## 2. Convenciones de código

- Lint, formato, tipos y tests los verifica el gate: `python scripts/gate.py`, configurado en `pyproject.toml`. `src` se añade a `[tool.mypy] files`.
- Cada servicio externo tiene una interfaz (`Protocol`), una o más implementaciones y una fábrica que elige según la configuración. `[inferido]` de `BaseRef/cognitive/*/protocols.py` y `factory.py`.
- La API pública se exporta en el `__init__.py` de cada módulo; lo demás es interno.
- El `__init__.py` raíz no reexporta módulos. Los módulos de workflow y los de agente importan de los comunes y nunca entre sí ([[decisions]] DEC-002).
- Ningún valor externo se interpola en SQL ni en filtros: los identificadores de Unity Catalog se validan y los filtros de búsqueda se construyen desde una estructura. La base interpola ambos (`BaseRef/core/storage/unity.py:79-80`, `BaseRef/core/observability/workflow_tracker.py:292-311`).
- Un fallo al escribir el registro de ejecución hace fallar el step. La base lo deja en un warning y la auditoría se pierde sin aviso (`BaseRef/core/observability/workflow_tracker.py:286`, `368`).
- Docstrings, mensajes de error y commits en español, como el harness (`orden_spec.md` §11).

## 3. Estructura de módulos

Derivada de la unión de `BaseRef/core/` y `BaseRef/cognitive/`, recortada al alcance de SyN y agrupada según [[decisions]] DEC-002:

```text
src/summa_ai_framework/
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
└─ agents/         # grafo del agente (DEC-003), registro de herramientas, entidades, memoria en Cosmos DB, herramienta RAG
tests/
```

ADLS no tiene cliente propio: se accede a través de las tablas y los volúmenes de Unity Catalog (SyN, etapa 2).

## 4. Interfaces expuestas

- **API pública de Python**: los nombres del `__all__` del `__init__.py` de cada módulo de primer nivel de §3 (`summa_ai_framework.<módulo>`), el nombre de la distribución y sus extras. Los submódulos y los nombres con `_` son internos y pueden cambiar sin aviso. Versionado semántico (definida en LIB-01).
- **Versiones**: la primera versión publicada es `0.1.0` y las plantillas fijan la versión exacta. Mientras sea `0.x`, la API pública puede cambiar entre versiones menores, con nota en el changelog. `[inferido]`
- **Extras por consumidor**: `workflow` para `repo-workflow` y `agent` para `repo-agente-conversacional`, con el mismo nombre que su grupo de módulos de [[decisions]] DEC-002 (decisión de la persona, 2026-11-18).
- **Esquemas de configuración** (pydantic): contrato con los archivos YAML de las plantillas. La definición del índice de AI Search (campos, filtrables, enlace al documento, página, deployment de embeddings, dimensiones y configuración semántica) es un solo esquema que usan las dos plantillas: es el contrato del índice entre ellas. El framework no fija modelos: cada caso de uso elige sus deployments en su configuración, y el de embeddings debe ser el mismo al indexar y al consultar (decisión de la persona, 2026-11-13). En la base, quien crea el índice y quien lo consulta no comparten esa definición (`BaseRef/cognitive/vectordb/azure_search.py:146-204` frente a `:325`).

## 5. Dependencias

### Base

Previstas `[inferido]` de `BaseRef/core/pyproject.toml` y `BaseRef/cognitive/pyproject.toml`; se fijan con versión en la feature que las introduce:

- **Comunes**: `pydantic`, `pyyaml`, `azure-identity`, `azure-keyvault-secrets`, `openai`, `azure-search-documents`, `tenacity`.
- **Extra del agente**: `langgraph`, `langchain-openai`, `azure-cosmos`, `jinja2`, un cliente HTTP para JWKS y una librería de JWT (la base usa `httpx` y `python-jose`).
- **Extra del workflow**: `azure-ai-contentunderstanding` (EjOCR, `src/extractor.py:7`), `langchain-text-splitters` y `langchain-experimental` (estrategia semántica) para el chunking (decisión de la persona, 2026-11-13), `tiktoken` para el chunking por tokens y un cliente HTTP para las fuentes. PySpark y Delta los provee el clúster.
- **Desarrollo**: pytest, ruff, mypy e IPython solo en `requirements-dev.txt`, nunca en las dependencias de ejecución ([[decisions]] DEC-001).

### Añadidas por features

Ninguna todavía.

## 6. Servicios externos

| Servicio | Uso | Autenticación |
|---|---|---|
| Azure OpenAI (AI Foundry) | Chat y embeddings | Clave de API guardada en Key Vault; la identidad del servicio solo se usa para llegar a Key Vault (decisión de la persona, 2026-11-13; igual que la base, `BaseRef/workflow/config/config.yaml:9-18`) |
| Azure AI Content Understanding (AI Foundry) | Extracción de documentos | Ídem |
| Azure AI Search | Índices y consultas | Ídem |
| Azure Cosmos DB | Historial y sesiones del agente | Ídem |
| Azure Key Vault | Secretos referenciados desde la configuración | Identidad de Azure (`azure-identity`) |
| Unity Catalog y ADLS | Tablas y volúmenes del workflow | Contexto del clúster de Databricks |
| Azure Artifacts | Publicación del paquete | Service connection de Azure DevOps |

## 7. Entornos

La librería no se despliega: cada plantilla instala una versión publicada en su ambiente (dev o prod). El feed de Azure Artifacts no existe todavía y lo crea el equipo de plataforma (decisión de la persona, 2026-11-13). PENDIENTE (dueño: plataforma): ¿nombre del feed, y se separan versiones preliminares de las estables?

## 8. Configuración y secretos

- La librería no lee variables de entorno propias, salvo las de identidad de Azure. Recibe la configuración ya cargada por la plantilla.
- Los YAML de configuración referencian secretos por nombre (`${NOMBRE}`) y el loader los resuelve al cargar, con el proveedor que indique el propio YAML: variables de entorno o Key Vault. `[inferido]` de `BaseRef/core/config/loader.py:110-144` y `BaseRef/core/security/secrets.py:24-112`.
- El proveedor por variables de entorno es el que usan los tests y el desarrollo local: el gate no llama a Key Vault.
- Los valores resueltos son secretos: no aparecen en logs ni en mensajes de error.

## 9. Seguridad

- **JWT**: validación OIDC con emisor, audiencia y llaves JWKS en caché, configurables. `[inferido]` de `BaseRef/core/security/authentication.py:26-131`. El agente lo usa con los tokens que firma Bot Framework (decisión de la persona, 2026-11-13; ver el tech-stack de `repo-agente-conversacional` §9). No hay modo sin autenticación ni usuario de desarrollo: la base lo trae (`authentication.py:76-79`) y aquí no entra ([[mission]] de `repo-agente-conversacional`, principio 3).
- **Sin secretos en el paquete**: ni en el código, ni en los ejemplos, ni en los tests.
- **Feed desde Databricks**: PENDIENTE (dueño: plataforma; se resuelve en LIB-04): ¿cómo instalan los clústeres el paquete del feed privado sin poner credenciales en `databricks.yml`? La base no lo resuelve: deja la credencial del feed en claro en las variables del clúster (`BaseRef/workflow/databricks.yml:109`). Opciones: que el pipeline publique la wheel en un volumen de Unity Catalog y el job la declare como librería, o que el clúster lea la credencial de un secret scope.
- Toda entrada que llega a filtros de AI Search u OData, o a SQL de Unity Catalog, se valida o se escapa en la librería (§2).

## 10. Observabilidad

- **Logger**: común a las dos plantillas (`BaseRef/core/observability/logger.py:8-157`).
- **Registro de ejecución**: `run_id`, timestamps y causa de error por ejecución, step y documento, en tablas de Unity Catalog. Lo usa solo el workflow (SyN, etapa 5; `BaseRef/core/observability/workflow_tracker.py:25`). La base registra por ejecución y por step, no por documento.
- **Sin telemetría externa por ahora**: ni OpenTelemetry, ni Azure Monitor, ni medición de tokens o costo (decisión de la persona, 2026-11-13). La base exporta con OpenTelemetry a consola u OTLP; entra por replanning.

## 11. Testing

- **Unitarias**: pytest dentro del gate, con dobles de cada interfaz; nada llama a Azure. Cobertura mínima del 80 % (`--cov-fail-under=80`) (decisión de la persona, 2026-11-13).
- **Integración o contrato**: por cada implementación, contra los servicios de dev, fuera del gate. Se ejecuta al cerrar la feature que la introduce o la cambia, y su salida va a `review.md`.
- **Humo**: por cada extra, instalar la wheel con **solo** ese extra en un entorno limpio e importar los módulos de ese consumidor ([[decisions]] DEC-001).
- **Fronteras de import**: un test falla si los módulos de workflow y los de agente se importan entre sí, o si un módulo común importa de ellos ([[decisions]] DEC-002).
- **Dobles**: cada interfaz trae su doble en el paquete, para que las plantillas prueben sin Azure ni Spark. La base solo lo tiene para la memoria (`BaseRef/cognitive/agents/memory/in_memory.py`); para probar sus steps sustituye la librería entera (`BaseRef/workflow/tests/test_steps/test_s05_indexing.py:11-31`).
- **Evidencia aceptada para cerrar una feature**: el gate siempre, y la prueba de integración contra dev si la feature toca un servicio de Azure (decisión de la persona, 2026-11-13).

## 12. CI/CD y despliegue

- **Plataforma**: Azure DevOps (decisión de la persona). El gate y el revisor del harness se portan a Azure Pipelines al mover el harness.
- **Pipeline**: gate → build de la wheel → publicación en el feed al integrar en la rama principal con una versión nueva. `[inferido]`: los pipelines de la base solo declaran ramas y variables; sus pasos están en una plantilla externa que no está en `project-context/` (`BaseRef/core/Pipeline/main-pipeline.yml:30-41`), así que este se escribe desde cero.
- **Ramas**: `feature/NN-nombre` → `develop` (se prueba en dev) → `main` (producción) (decisión de la persona, 2026-11-13). Las versiones estables se publican desde `main`.
- **Aprobación de versiones**: el equipo de plataforma aprueba publicar una versión, con una aprobación por grupo en el pipeline de Azure DevOps (decisión de la persona, 2026-11-13).

## Relación con otros documentos

- [[mission]] — el porqué que justifica este stack.
- [[alcance-inicial]] — dependencias externas y punto de partida.
- [[roadmap]] — en qué orden entran estos componentes.
- [[decisions]] — decisiones técnicas que complementan este documento.
