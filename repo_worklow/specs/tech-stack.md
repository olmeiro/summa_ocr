# Tech-stack — Framework de procesamiento e indexación (repo-workflow)

> Constitución. Define el **marco técnico común**. Cualquier desviación se registra en [[decisions]] o en `replanning/`.

**Fuentes**: SyN, EjOCR y BaseRef (ver [[mission]]), el harness de este repo y decisiones de la persona del 2026-11-12.

---

## 1. Lenguaje y framework

- **Lenguaje y versión**: Python en Azure Databricks, con la misma versión mínima que `repo-libreria`. PENDIENTE: ¿versión de Databricks Runtime? La base usa 17.3 (`BaseRef/workflow/databricks.yml`).
- **Framework**: Databricks Jobs desplegados con Databricks Asset Bundles (SyN, arquitectura §1 y etapa 5). Cada step es un script Python ejecutado como tarea del job, en un clúster efímero compartido por todas las tareas. `[inferido]` de `BaseRef/workflow/docs/architecture.md`.
- **Librería del framework**: `repo-libreria` con su extra del workflow, en una versión fija instalada en el clúster desde el feed de Azure Artifacts de SUMMA (decisión de la persona).
- **Gestor de dependencias**: `uv` con `requirements.txt` y `requirements-dev.txt` para el desarrollo local y el gate (`AGENTS.md`); en el clúster, las librerías que declara el job.

## 2. Convenciones de código

- Lint, formato, tipos y tests los verifica el gate: `python scripts/gate.py`, configurado en `pyproject.toml`. `src` se añade a `[tool.mypy] files`.
- Cada step declara en el manifest sus entradas y salidas (`requires`/`provides`, SyN, etapa 5). La base las llama `inputs`/`outputs` (`BaseRef/workflow/config/workflow_manifest.yaml`).
- El orden del DAG sale de esas declaraciones. Databricks exige las dependencias entre tareas escritas en el bundle (`depends_on`), así que un test del gate comprueba que coinciden con el manifest. `[inferido]`: en la base las dos listas se mantienen a mano y nada las compara (`BaseRef/workflow/resources/workflow.yml:89`, `119`).
- Todos los steps siguen el mismo patrón: leer el manifest y la config, abrir la trazabilidad de la ejecución, procesar, escribir la salida y cerrar la trazabilidad. `[inferido]` de `BaseRef/workflow/docs/architecture.md`, "Patron de ejecucion de un step".
- Un step no ejecuta nada al importarse: expone una función que recibe sus argumentos y los servicios de la librería, y el script solo la llama. Así el gate lo prueba con los dobles de la librería. `[inferido]`: los steps de la base ejecutan al importarse y sus tests sustituyen la librería entera (`BaseRef/workflow/tests/test_steps/test_s05_indexing.py:11-31`).
- Las tablas de salida tienen nombre estable y cada fila lleva el `run_id` y el identificador del documento. `[inferido]`: la base crea tablas nuevas en cada ejecución, con el `run_id` en el nombre (`BaseRef/core/devops/workflow.py:158`), lo que impide el incremental y hace que re-ejecutar no sea idempotente ([[mission]] §8, principio 2).
- El identificador de un documento es el que tiene en su fuente, y el de un chunk se deriva de él y de su posición. `[inferido]`: la base usa el nombre del archivo (`BaseRef/workflow/src/steps/s01_textual_ingestion.py:134`, `s02_chunking.py:142`), que no es único ni estable.
- Un documento que falla se registra con su causa y no detiene a los demás; el step termina en error si los fallos superan el umbral que fije su spec. `[inferido]`: la base solo cuenta los fallos como métrica (`BaseRef/workflow/src/steps/s01_textual_ingestion.py:232-242`).
- Un step no reimplementa lo que la librería ya ofrece.
- Imports, `config.yaml`, manifest, bundle y recursos usan nombres de SUMMA. Nada importa paquetes de la base ni conserva sus nombres (decisión de la persona, 2026-11-12).
- Ningún secreto, cookie ni token en el código ni en `databricks.yml`.
- Docstrings, mensajes de error y commits en español (`orden_spec.md` §11).

## 3. Estructura de módulos

SyN, etapa 5, pide `bundle.yml`, ConfigFiles, step registry, manifest/DAG y tablas de logs. La disposición es `[inferido]` de `BaseRef/workflow/`:

```text
databricks.yml            # bundle (el bundle.yml de SyN): targets dev/prod, clúster efímero, variables
resources/workflow.yml    # job: tareas, dependencias, librerías, timeouts y trigger
config/
├─ config_<ambiente>.yaml # ConfigFile: fuente, extracción, chunking, embeddings e índice
└─ workflow_manifest.yaml # manifest: requires/provides de cada step y zona medallion
src/steps/                # un script por step: sNN_nombre.py (registro de steps)
tests/
```

La lectura del manifest, el contexto de cada step y la validación del DAG los entrega la librería (LIB-06); aquí viven el manifest y los steps.

## 4. Interfaces expuestas

- **Job de Databricks**, con los parámetros y el trigger definidos en el bundle (SyN, etapa 5).
- **ConfigFile y manifest**: contrato con cada caso de uso.
- **Índices de Azure AI Search**: contrato con `repo-agente-conversacional` (campos, campo de enlace al documento, página, campos filtrables y modelo de embeddings). Se escribe como la sección de definición del índice del ConfigFile, validada por el esquema de la librería que también usa el agente (LIB-11).
- **Tablas Delta en Unity Catalog**: volúmenes en bronze; tablas en silver y gold; tablas de logs y auditoría (`BaseRef/workflow/docs/architecture.md`, "Arquitectura Medallion"). Convención de la base: un esquema `<iniciativa>_<capa>` por iniciativa dentro del catálogo (`BaseRef/core/storage/unity.py:73-80`). PENDIENTE: ¿los esquemas los crea el job, como en la base, o la arquitectura de datos (SyN, etapa 2)?

## 5. Dependencias

### Base

- La librería del framework, con su extra del workflow: trae Content Understanding, Azure OpenAI, AI Search, chunking, fuentes HTTP y trazabilidad.
- `pandas` y `openpyxl` para Excel. `[inferido]` de `BaseRef/workflow/requirements_qa.txt`.
- Las versiones se fijan en la feature que las introduce.

### Añadidas por features

Ninguna todavía.

## 6. Servicios externos

| Servicio | Uso | Autenticación |
|---|---|---|
| Azure Databricks + Unity Catalog | Ejecución de jobs, gobierno, volúmenes, tablas y logs | PENDIENTE: ¿service principal o identidad del workspace para ejecutar los jobs? |
| Azure Data Lake Storage Gen2 | Capas bronze, silver y gold | Storage Credential y External Location de Unity Catalog (SyN, etapa 2) |
| Azure AI Content Understanding (AI Foundry) | OCR y extracción de campos con un analizador por iniciativa; también devuelve el markdown (decisión de la persona; EjOCR, `src/extractor.py`) | Vía la librería; credencial en Key Vault |
| Azure AI Document Intelligence | Solo si Content Understanding no cubre un formato (SyN: "si es necesario") | Ídem |
| Azure OpenAI (AI Foundry) | Embeddings y la tarea "Process Files con OpenAI" (SyN, etapa 5). PENDIENTE: ¿qué deployments? | Ídem |
| Azure AI Search | Creación y carga de índices | Ídem |
| Azure Key Vault | Credenciales de las fuentes y de los servicios | Identidad del clúster `[inferido]` |
| Azure Artifacts | Instalación de la librería en el clúster | PENDIENTE en el `tech-stack.md` §9 de `repo-libreria`. La base deja la credencial del feed en claro en el bundle (`BaseRef/workflow/databricks.yml:109`): no es guía |
| Fuentes por API (Control Doc la primera) | Documentos y metadatos, en solo lectura | Las define cada caso de uso; para Control Doc, API Key (SyN, etapa 1) |

## 7. Entornos

| Entorno | Recursos | Notas |
|---|---|---|
| dev | Workspace de Databricks, catálogo de Unity Catalog, Storage y AI Search de desarrollo | Desarrollo y pruebas |
| prod | Los mismos recursos, de producción | Procesa los documentos autorizados (SyN, componente C) |

PENDIENTE: ¿un workspace de Databricks por ambiente o uno compartido con catálogos separados? La base usa un workspace para dev y qa y otro para prod (`BaseRef/workflow/databricks.yml`). ¿Nombres de recursos?

## 8. Configuración y secretos

- Parámetros de ejecución en `databricks.yml` por target (dev, prod). Configuración de la iniciativa en `config/config_<ambiente>.yaml` y `config/workflow_manifest.yaml` (SyN, etapa 5).
- Cada target del bundle pasa a los steps el ConfigFile de su ambiente. `[inferido]`: la base tiene un solo `config.yaml` con los endpoints y el Key Vault de un ambiente (`BaseRef/workflow/config/config.yaml:9-11`, `resources/workflow.yml:70-71`), lo que no cumple la separación por ambiente de [[mission]] §7.
- La versión de la librería se fija en un solo lugar del bundle y un test del gate comprueba que `requirements.txt` coincide. `[inferido]`: la base la repite en cada tarea y difiere de su `requirements` (`BaseRef/workflow/resources/workflow.yml:81`, `requirements_qa.txt:4-5`).
- El trigger del job (programado, periódico o por llegada de archivos) se declara en el bundle y se pausa o activa por target; no va en el ConfigFile (`BaseRef/workflow/resources/workflow.yml:23-58`, `docs/triggers.md`).
- Las credenciales (AI Search, OpenAI, Content Understanding y la de cada fuente) se referencian por nombre en Key Vault y las resuelve la librería (SyN, etapas 1 y 5).
- En local, `.env` fuera de git. Los agentes no leen ni editan ningún `.env*`: cada variable nueva la añade la persona a `.env.template` (`AGENTS.md`).

## 9. Seguridad

- **Red**: Service Endpoints en el firewall del Storage Account y subredes de Databricks autorizadas (SyN, etapa 2).
- **Permisos**: lectura y escritura en ADLS solo a través de Unity Catalog (SyN, etapa 2).
- **Fuentes**: acceso de solo lectura con credencial de servicio, nunca con cookies ni sesión de un usuario (EjOCR, `src/api_client.py:26-28`, es lo que no se repite).
- **Bundle**: `databricks.yml` y `resources/` no contienen credenciales; el gate o la revisión lo comprueban.
- **Datos sensibles**: ver [[mission]] §7.

## 10. Observabilidad

- **Requisito de SyN, etapa 5**: tablas de logs en Unity Catalog con esquema y particionado definidos, `run_id`, timestamps y causa de error por ejecución y por documento, con scripts de creación y mantenimiento. Las define y las escribe la trazabilidad de la librería (LIB-07); la plantilla aporta la tarea que las crea y las mantiene.
- PENDIENTE: ¿las tablas de logs son transversales, en un esquema compartido por todas las iniciativas como en la base (`transversal_schema` en `BaseRef/workflow/config/workflow_manifest.yaml:3`), o cada iniciativa tiene las suyas? De eso depende quién las crea.
- PENDIENTE (decisión de la persona, 2026-11-12): ¿se envía además telemetría a Azure Monitor y se configuran alertas?

## 11. Testing

- **Unitarias**: pytest dentro del gate, para la lógica de cada step con los dobles de prueba de la librería. PENDIENTE: ¿Spark local en los tests o solo lógica en Python puro? En la base los steps usan Spark solo para leer y escribir tablas y procesan en pandas en el driver (`BaseRef/workflow/src/steps/s02_chunking.py:113`, `s05_indexing.py:87`), y sus tests no levantan Spark.
- **Coherencia del bundle**: tests del gate para manifest frente a `depends_on` y para la versión de la librería (§2 y §8).
- **Integración o contrato**: pruebas punto a punto Databricks ↔ ADLS ↔ AI Search (SyN, etapa 2).
- **Humo en el entorno desplegado**: ejecutar el job tras cada despliegue y validar logs y resultados en el workspace (SyN, etapa 5).
- **Evidencia aceptada para cerrar una feature**: PENDIENTE: ¿basta el gate local o se exige una ejecución del job en dev para las features que tocan Databricks?

## 12. CI/CD y despliegue

- **Plataforma**: Azure DevOps, para repos y pipelines (decisión de la persona). El gate y el revisor del harness se portan a Azure Pipelines al mover el harness.
- **Pipelines** (SyN, etapa 5; `BaseRef/workflow/docs/deployment.md`): validación del bundle, despliegue automático (dev → prod), validación de los jobs tras desplegar y rollback si falla. El pipeline de la base solo declara ramas y variables por ambiente; sus pasos están en una plantilla externa que no está en `project-context/` (`BaseRef/workflow/Pipeline/workflow-pipeline.yml:28-38`): este se escribe desde cero.
- **Ramas**: el harness usa `feature/NN-nombre` → `main`; las librerías de la base usan `Develop`, `Integration` y `master` para dev, qa y prod; SyN pide triggers feature → develop → prod. PENDIENTE: ¿qué modelo de ramas se usa?
- **Aprobación de producción**: PENDIENTE: ¿quién aprueba el paso a prod?

## Relación con otros documentos

- [[mission]] — el porqué que justifica este stack.
- [[alcance-inicial]] — dependencias externas y punto de partida.
- [[roadmap]] — en qué orden entran estos componentes.
- [[decisions]] — decisiones técnicas que complementan este documento.
