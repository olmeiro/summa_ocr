# Roadmap — Framework de procesamiento e indexación (repo-workflow)

> Constitución. Secuencia de features pequeñas, implementables y verificables, con su estado.

Derivado de [[mission]], [[alcance-inicial]], SyN (etapas 4 y 5), EjOCR y BaseRef. `LIB-NN` es la feature NN del roadmap de `repo-libreria`.

---

## 1. Principios de secuenciación

1. **Base antes que features**: configuración, contratos y el gate en verde van primero.
2. **La primera feature es manejable, no la más riesgosa**: sirve para probar el flujo y la arquitectura.
3. **Cada feature deja el sistema funcionando** y es verificable por sí sola.
4. **Replanning entre fases**: se revisa si el plan sigue siendo válido.
5. **Un recorrido completo y delgado antes de ensanchar**: primero un documento llega de bronze al índice con una sola estrategia de cada cosa; después se añaden fuentes, formatos y calidad.
6. **La plantilla no reimplementa la librería**: si falta una capacidad genérica, se pide como feature de `repo-libreria`.
7. **El contrato del índice se acuerda con `repo-agente-conversacional` antes de la feature 09.** Su forma es el esquema de definición del índice de la librería (LIB-11).

## 2. Fases

### Fase 0 — Constitución

`mission`, `tech-stack`, `alcance-inicial` y este roadmap. **Salida**: base documental versionada.

### Fase 1 — Base de la plantilla

Bundle, manifest, configuración y logs. **Salida**: un job de ejemplo con dos steps encadenados por `requires`/`provides` se despliega en dev, lee su ConfigFile con secretos de Key Vault y deja su ejecución en la tabla de logs con `run_id`.

### Fase 2 — Recorrido mínimo hasta el índice

Descubrimiento, extracción con Content Understanding, chunking, embeddings e indexación. **Salida**: un PDF dejado en bronze queda en silver con su markdown y sus campos, y se indexa en Azure AI Search con su origen (documento y página) y sus campos filtrables. Ejecutar el job dos veces deja el mismo resultado.

### Fase 3 — Fuentes, formatos y calidad

Fuente por API, incremental, métricas de calidad, Excel y OpenAI. **Salida**: una fuente por API se sincroniza de forma incremental (incluidos los eliminados) y cada ejecución reporta la completitud y la confianza de la extracción.

### Fase 4 — Despliegue y adopción

Pipelines de Azure DevOps y guía de onboarding. **Salida**: el bundle se despliega en dev y prod desde Azure DevOps, y un repo de caso de uso puede clonar la plantilla siguiendo la guía.

## 3. Features

| ID | Nombre | Fase | Depende de | Estado | Carpeta |
|---|---|---|---|---|---|
| 01 | esqueleto-bundle: estructura del repo, `databricks.yml` (dev, prod) y `resources/workflow.yml` con un job mínimo, su trigger semanal (activo en prod, pausado en dev) y la versión de la librería en un solo lugar | 1 | — | accepted | `features/01-esqueleto-bundle/` |
| 02 | manifest-dag: `workflow_manifest.yaml` con `requires`/`provides`, patrón común de step y test que compara el manifest con las dependencias del job | 1 | 01, LIB-06 | not_started | `features/02-manifest-dag/` |
| 03 | configuracion: `config_<ambiente>.yaml` por iniciativa con secretos de Key Vault, cargado con la librería | 1 | 02, LIB-03 | not_started | `features/03-configuracion/` |
| 04 | logs-auditoria: tarea que crea y mantiene los esquemas de la iniciativa y sus tablas de logs en Unity Catalog, y registro por ejecución, step y documento con `run_id`, timestamps y causa | 1 | 03, LIB-07 | not_started | `features/04-logs-auditoria/` |
| 05 | descubrimiento: clasificación de los archivos de bronze por tipo; lo no soportado queda registrado | 2 | 04, LIB-05 | not_started | `features/05-descubrimiento/` |
| 06 | extraccion-content-understanding: analizador creado desde el esquema del caso de uso; PDF, escaneados, imágenes y Word a silver con markdown, campos, confianza, página y marca de confianza baja | 2 | 05, LIB-09 | not_started | `features/06-extraccion-content-understanding/` |
| 07 | chunking: step con la estrategia elegida en el ConfigFile, con trazabilidad a documento y página | 2 | 06, LIB-10 | not_started | `features/07-chunking/` |
| 08 | embeddings: vectores con Azure OpenAI | 2 | 07, LIB-08 | not_started | `features/08-embeddings/` |
| 09 | indexacion-ai-search: índice desde el ConfigFile, upsert idempotente, retiro de los chunks sobrantes de un documento reprocesado y campos filtrables | 2 | 08, LIB-11 | not_started | `features/09-indexacion-ai-search/` |
| 10 | fuente-api: step que lista y descarga binario y metadatos a bronze con el cliente HTTP de la librería | 3 | 04, LIB-12, API de Control Doc | not_started | `features/10-fuente-api/` |
| 11 | incremental: estado por documento; nuevos, modificados y eliminados, reflejados en silver y en el índice | 3 | 09, 10, API de Control Doc | not_started | `features/11-incremental/` |
| 12 | calidad-extraccion: completitud y confianza por documento, categoría y campo | 3 | 06 | not_started | `features/12-calidad-extraccion/` |
| 13 | excel-estructurado: cada hoja de Excel a una tabla Delta en silver o gold; no se indexa | 3 | 04, LIB-05 | not_started | `features/13-excel-estructurado/` |
| 14 | process-files-openai: prompt configurable sobre el markdown de silver; salida en silver, declarable como campo del índice | 3 | 06, LIB-08 | not_started | `features/14-process-files-openai/` |
| 15 | cicd-azure-devops: validación y despliegue del bundle dev → prod, trigger, validación y rollback | 4 | 01, LIB-04 | not_started | `features/15-cicd-azure-devops/` |
| 16 | onboarding: documentación técnica, lineamientos de chunking y guía para crear un caso de uso desde la plantilla | 4 | 11, 12, 15 | not_started | `features/16-onboarding/` |

Estados: `not_started → in_progress → passing → accepted` (ver [[orden_spec]] §6). Una feature solo pasa a `accepted` con el veredicto `accept` del revisor.

- La feature 15 también depende de que la IaC transversal y la arquitectura de datos (SyN, etapas 1 y 2) estén desplegadas en dev; si eso llega antes, puede adelantarse a la fase 1.
- Las features 10 y 11 están bloqueadas hasta que TI de SUMMA entregue la API de Control Doc con listado, fecha de modificación y credencial de servicio. Se espera la API; no se construye una fuente sobre la exportación en Excel (decisión de la persona, 2026-11-13; ver [[alcance-inicial]] §4).
- Mientras no exista el feed (LIB-04), la librería se instala desde una ruta local en desarrollo.

## 4. Punto de partida de cada feature

Qué ofrece la base para cada feature y qué debe resolver su spec. Se usa como guía de diseño, sin copiar código ([[mission]]). Las rutas sin prefijo son de `BaseRef/workflow/`. Para la capacidad de librería de cada feature, ver el §4 del roadmap de `repo-libreria`.

| ID | Referencia | Lo que cambia respecto a la referencia |
|---|---|---|
| 01 | `databricks.yml`, `resources/workflow.yml` | Tiene targets dev, qa y prod con un clúster efímero por job (`databricks.yml:57-247`); aquí, dev y prod. Fija la librería tarea por tarea (`resources/workflow.yml:81`, `109-111`) y con otra versión en `requirements_qa.txt:4-5`. Lleva credenciales en claro en las variables del clúster (`databricks.yml:109-112`): no es guía; ver [[tech-stack]] §6. Ofrece los triggers como bloques comentados (`resources/workflow.yml:23-58`); aquí se activa el programado, semanal. |
| 02 | `config/workflow_manifest.yaml`; `docs/architecture.md`, "Patron de ejecucion de un step" | Su manifest solo resuelve de dónde lee y dónde escribe cada step; el orden está repetido a mano en `depends_on` (`resources/workflow.yml:89`, `119`). Sus steps ejecutan al importarse (`src/steps/s05_indexing.py:13-54`) y por eso sus tests sustituyen la librería entera (`tests/test_steps/test_s05_indexing.py:11-31`). |
| 03 | `config/config.yaml` | Un solo archivo, con los endpoints y el Key Vault de un ambiente (`config.yaml:9-11`); aquí, uno por ambiente. Secciones útiles: `global_settings`, `secrets`, `llms`, `embeddings`, `vector_stores` y `processing`. |
| 04 | `BaseRef/core/observability/workflow_tracker.py` | La base no trae la creación ni el mantenimiento de sus tablas de logs, y SyN, etapa 5, los pide. No registra por documento. Sus tablas son transversales; aquí, de la iniciativa. |
| 05 | `src/steps/s00_discovery.py:64-90`: grupos por extensión | Copia cada archivo a un volumen nuevo en cada ejecución (`:92-118`). Lo que no reconoce va a un grupo `others` (`:90`) sin registro por archivo. |
| 06 | EjOCR `src/extractor.py`; `src/steps/s01_textual_ingestion.py` | La base lleva a silver solo texto plano por OCR (`s01_textual_ingestion.py:152`). Identifica el documento por el nombre del archivo (`:134`); aquí, por su identificador en la fuente. EjOCR solo envió PDF con un analizador hecho a mano (`src/extractor.py:40-42`). |
| 07 | `src/steps/s02_chunking.py` | Lleva todo a pandas en el driver (`:113`). El id del chunk es el nombre del archivo más el índice (`:142`); no guarda la página. |
| 08 | `src/steps/s04_embeddings.py:497-703` | Lotes según el `batch_size` de la configuración (`:696`). No se traen los embeddings de imágenes. |
| 09 | `src/steps/s05_indexing.py` | Indexa dos metadatos fijos, `file_name` y `source_path` (`:89-107`). Hace upsert sin retirar los chunks que sobran cuando un documento cambia. |
| 10 | Sin referencia en la base. EjOCR `src/api_client.py` es el contraejemplo | Diseño nuevo desde SyN, etapa 4. |
| 11 | Sin referencia: la base reprocesa todo en cada ejecución, en tablas nuevas | Diseño nuevo desde SyN, etapa 4. EjOCR salta lo ya procesado mirando si existe el archivo de salida (`main.py:17-23`). |
| 12 | EjOCR `output/resumen_*.csv` e `informe_extraccion_por_documento.Rmd` | Hoy se calcula aparte, en R, sobre los JSON. Un campo sin valor llega con confianza: completitud y confianza se miden por separado. |
| 13 | `src/steps/s01_tabular_ingestion.py`: lectura con pandas | Exige una columna `content` en cada hoja (`:137`) e indexa ese texto; aquí la hoja se guarda como tabla y no se indexa. |
| 14 | `src/steps/s01_structured_ingestion.py`, `src/steps/s02_image_captioning.py` | Son los usos de un LLM sobre archivos que tiene la base; ninguno corresponde a la tarea de SyN. Aquí es un prompt configurable sobre el markdown, que ya trae el texto: no se lee el binario de nuevo. |
| 15 | `Pipeline/workflow-pipeline.yml`, `Pipeline/variables/*.yml`, `docs/deployment.md` | El pipeline solo declara ramas y variables por ambiente (host del workspace, Key Vault, target y política de clúster); sus pasos están en una plantilla externa que no está en `project-context/`: se escriben desde cero. |
| 16 | `docs/`: `overview`, `getting-started`, `configuration`, `customization`, `deployment`, `pipeline-steps` y `triggers` | Sirve de índice de temas. |

## 5. Cierre del roadmap

- Todas las features en `accepted`.
- El repo del caso de uso Control Doc, clonado de esta plantilla, indexa en dev los contratos activos y los mantiene actualizados de forma incremental.
- Los objetivos medibles de [[mission]] §6 tienen umbral y se cumplen.
