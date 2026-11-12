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
7. **El contrato del índice se acuerda con `repo-agente-conversacional` antes de la feature 09.**

## 2. Fases

### Fase 0 — Constitución

`mission`, `tech-stack`, `alcance-inicial` y este roadmap. **Salida**: base documental versionada.

### Fase 1 — Base de la plantilla

Bundle, manifest, configuración y logs. **Salida**: un job de ejemplo con dos steps encadenados por `requires`/`provides` se despliega en dev, lee su ConfigFile con secretos de Key Vault y deja su ejecución en la tabla de logs con `run_id`.

### Fase 2 — Recorrido mínimo hasta el índice

Descubrimiento, extracción con Content Understanding, chunking, embeddings e indexación. **Salida**: un PDF dejado en bronze queda en silver con su markdown y sus campos, y se indexa en Azure AI Search con su origen (documento y página) y sus campos filtrables.

### Fase 3 — Fuentes, formatos y calidad

Fuente por API, incremental, métricas de calidad, Excel y OpenAI. **Salida**: una fuente por API se sincroniza de forma incremental (incluidos los eliminados) y cada ejecución reporta la completitud y la confianza de la extracción.

### Fase 4 — Despliegue y adopción

Pipelines de Azure DevOps y guía de onboarding. **Salida**: el bundle se despliega en dev y prod desde Azure DevOps, y un repo de caso de uso puede clonar la plantilla siguiendo la guía.

## 3. Features

| ID | Nombre | Fase | Depende de | Estado | Carpeta |
|---|---|---|---|---|---|
| 01 | esqueleto-bundle: estructura del repo, `databricks.yml` (dev, prod), `resources/workflow.yml` con un job mínimo | 1 | — | not_started | `features/01-esqueleto-bundle/` |
| 02 | manifest-dag: `workflow_manifest.yaml` con `requires`/`provides` y patrón común de step | 1 | 01 | not_started | `features/02-manifest-dag/` |
| 03 | configuracion: `config.yaml` por iniciativa con secretos de Key Vault, cargado con la librería | 1 | 02, LIB-03 | not_started | `features/03-configuracion/` |
| 04 | logs-auditoria: tablas de logs en Unity Catalog con `run_id`, timestamps y causa por ejecución y documento | 1 | 03, LIB-05 | not_started | `features/04-logs-auditoria/` |
| 05 | descubrimiento: clasificación de los archivos de bronze por tipo | 2 | 04 | not_started | `features/05-descubrimiento/` |
| 06 | extraccion-content-understanding: PDF nativos, escaneados e imágenes a silver con markdown, campos, confianza y página | 2 | 05, LIB-07 | not_started | `features/06-extraccion-content-understanding/` |
| 07 | chunking: step con la estrategia elegida en el ConfigFile, con trazabilidad a documento y página | 2 | 06, LIB-08 | not_started | `features/07-chunking/` |
| 08 | embeddings: vectores con Azure OpenAI | 2 | 07, LIB-06 | not_started | `features/08-embeddings/` |
| 09 | indexacion-ai-search: índice desde el ConfigFile, upsert idempotente y campos filtrables | 2 | 08, LIB-09 | not_started | `features/09-indexacion-ai-search/` |
| 10 | fuente-api: step que descarga binario y metadatos a bronze con el cliente HTTP de la librería | 3 | 04, LIB-10 | not_started | `features/10-fuente-api/` |
| 11 | incremental: nuevos, modificados y eliminados, reflejados en el índice | 3 | 09, 10 | not_started | `features/11-incremental/` |
| 12 | calidad-extraccion: completitud y confianza por documento, categoría y campo | 3 | 06 | not_started | `features/12-calidad-extraccion/` |
| 13 | excel-estructurado: procesamiento de Excel | 3 | 09 | not_started | `features/13-excel-estructurado/` |
| 14 | process-files-openai: tarea de procesamiento de archivos con Azure OpenAI | 3 | 06, LIB-06 | not_started | `features/14-process-files-openai/` |
| 15 | cicd-azure-devops: validación y despliegue del bundle dev → prod, trigger, validación y rollback | 4 | 01, LIB-04 | not_started | `features/15-cicd-azure-devops/` |
| 16 | onboarding: documentación técnica, lineamientos de chunking y guía para crear un caso de uso desde la plantilla | 4 | 11, 12, 15 | not_started | `features/16-onboarding/` |

Estados: `not_started → in_progress → passing → accepted` (ver [[orden_spec]] §6). Una feature solo pasa a `accepted` con el veredicto `accept` del revisor.

- La feature 15 también depende de que la IaC transversal y la arquitectura de datos (SyN, etapas 1 y 2) estén desplegadas en dev; si eso llega antes, puede adelantarse a la fase 1.
- La feature 06 necesita resueltos los `PENDIENTE` de [[alcance-inicial]] §2 sobre el analizador y los documentos Word. La 11 necesita la API de listado de Control Doc o de la fuente de prueba.
- Mientras no exista el feed (LIB-04), la librería se instala desde una ruta local en desarrollo.

## 4. Cierre del roadmap

- Todas las features en `accepted`.
- El repo del caso de uso Control Doc, clonado de esta plantilla, indexa en dev los contratos activos y los mantiene actualizados de forma incremental.
- Los objetivos medibles de [[mission]] §6 tienen umbral y se cumplen.
