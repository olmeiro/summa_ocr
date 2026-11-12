# Alcance inicial — Framework de procesamiento e indexación (repo-workflow)

> Constitución. Define qué entra y qué no, de qué depende el proyecto y desde dónde arranca.

**Fuentes**: SyN, EjOCR, Metadatos CD y BaseRef (ver [[mission]]) y decisiones de la persona del 2026-11-12.

---

## 1. Posición del componente

```text
Fuente por API ──► [ Job de Databricks: este repo + librería repo-libreria ] ──► ADLS bronze · silver · gold
(Control Doc, …)              │        │                                          Unity Catalog: tablas y logs
                              │        └─► Content Understanding · Azure OpenAI
                              ▼
                      Azure AI Search (índice) ──► agentes de repo-agente-conversacional
```

Cada caso de uso clona este repo y configura sus propios jobs (SyN, etapa 7).

## 2. Alcance funcional

### Entra

La plantilla aporta bundle, manifest, steps y configuración. La lógica común la entrega `repo-libreria` (decisión de la persona). Lo pide SyN (arquitectura §1 y etapa 5), salvo donde se indica:

- **Bundle**: `databricks.yml` con targets dev y prod y clúster efímero, y `resources/workflow.yml` con las tareas, sus dependencias y la librería en versión fija.
- **Manifest/DAG**: `requires`/`provides` de cada step y zona medallion; el registro de steps es la carpeta `src/steps/`.
- **ConfigFile** por iniciativa: fuente, extracción, chunking, embeddings e índice.
- **Logs y auditoría**: tablas de logs en Unity Catalog con esquema y particionado definidos, `run_id`, timestamps y causa de error por ejecución y por documento.
- **Descubrimiento**: clasificación de los archivos que llegan a bronze por tipo, en textual, tabular e imágenes. `[inferido]` de `BaseRef/workflow/docs/pipeline-steps.md`, `s00_discovery`.
- **Fuente por API** (decisión de la persona): step que usa el cliente HTTP de la librería para descargar el binario y los metadatos a bronze. El conector concreto de cada fuente es configuración del caso de uso.
- **Estrategia incremental**: detección de documentos nuevos, modificados y eliminados, y su reflejo en el índice (SyN, etapa 4). La base no lo trae.
- **Extracción con Content Understanding** (decisión de la persona): PDF nativos, escaneados e imágenes van al analizador de la iniciativa. A silver llegan el markdown y los campos con su confianza y su página (EjOCR, `src/extractor.py:39-49`).
- **Métricas de calidad** de la extracción por documento, categoría y campo (completitud y confianza), como las que el ejercicio calculó aparte (EjOCR, `output/resumen_*.csv`). `[inferido]`
- **Excel**: procesamiento de datos estructurados.
- **"Process Files con OpenAI"**: procesamiento de archivos con un modelo de Azure OpenAI.
- **Chunking** con la estrategia que elija el ConfigFile: por tokens, por estructura o semántica.
- **Embeddings** con Azure OpenAI.
- **Indexación en Azure AI Search**: crear o actualizar el índice desde el ConfigFile, upsert idempotente y campos filtrables con los metadatos de la fuente y los campos extraídos que elija el caso de uso. `[inferido]` de SyN, etapa 7 (filtros por tipo, partes, fecha e ID).
- **Trigger** del job según el ConfigFile: programado, periódico o por llegada de archivos (`BaseRef/workflow/docs/triggers.md`).
- **Pipelines de Azure DevOps**, documentación técnica y guía de onboarding (SyN, etapas 1 y 5).

### No entra

- **Clientes de servicios y lógica genérica**: Content Understanding, chunking, AI Search, fuentes HTTP y trazabilidad están en `repo-libreria`.
- **El conector concreto de Control Doc**, su configuración y su esquema de contratos: van en el repo del caso de uso (decisión de la persona; SyN, etapa 7).
- **Indexar el corpus de Control Doc** y ajustar su chunking y su perfil de scoring (SyN, etapa 7).
- **Validación humana** de los campos extraídos y su carga en sistemas destino (`Control Doc/Campo Extraccion de Contratos.xlsx`, hoja "Caso de Uso", Alcance).
- **Capacidades de la base que SyN no pide** (decisión de la persona; quedan para replanning): sanitización PII y Content Safety, descripción de imágenes con LLM y escritura para consumo desde Fabric.
- **Infraestructura transversal**: networking y configuración del metastore, Storage Credential y External Location (SyN, etapas 1 y 2). Aquí son dependencias.
- **Azure Data Factory** (SyN, componente A). Tampoco responder consultas, que es de `repo-agente-conversacional`.
- **Actualizar la base de conocimiento sin ejecutar el pipeline**, digitalizar documentos físicos, procesar el histórico no activo y hacer dashboards (SyN, "Fuera de alcance").

### Por decidir

- PENDIENTE: ¿el framework crea o actualiza el analizador de Content Understanding desde el archivo de esquema versionado, o el analizador se administra en el portal y el job solo recibe su ID, como en el ejercicio (EjOCR, `src/extractor.py:40`)?
- PENDIENTE: ¿qué pasa con un campo extraído con confianza baja: se indexa igual, se marca o se descarta? ¿Con qué umbral?
- PENDIENTE: ¿los documentos Word van directo a Content Understanding o se convierten antes a PDF? El ejercicio solo envió PDF (EjOCR, `src/extractor.py:42`).
- PENDIENTE: ¿la ejecución es programada (con qué frecuencia), periódica o por llegada de archivos? SyN, §4, lo deja abierto.

## 3. Dependencias externas

| Dependencia | Quién la provee | Entorno o recurso | Notas |
|---|---|---|---|
| Librería del framework, versión publicada | `repo-libreria` | Feed de Azure Artifacts | Ver la columna "Depende de" de [[roadmap]] |
| Workspace de Databricks, metastore de Unity Catalog, Storage Credential y External Location | Arquitectura de datos | dev y prod | SyN, etapa 2 |
| ADLS Gen2, AI Search, AI Foundry (Content Understanding y OpenAI), Key Vault y red | IaC transversal | dev y prod | SyN, etapa 1. PENDIENTE: ¿en qué repo y con qué herramienta vive la IaC? |
| Analizador de Content Understanding por iniciativa | Caso de uso | dev y prod | El ejercicio usó uno llamado `Sommacontentunderstanding` (EjOCR, `output/resumen_documentos.csv`) |
| API de Control Doc con credencial de servicio y documentación (autenticación, endpoints, paginación, rate limits) | TI de SUMMA | — | SyN, etapas 1 y 4. Ver §4 |
| Proyecto de Azure DevOps y service connections | SUMMA | — | Decisión de la persona |

## 4. Punto de partida

### Greenfield: activos heredados

- **Harness** (`scripts/`, `.claude/`, `specs/`, `AGENTS.md`): se mueve desde la raíz de `summa_ocr`; el gate y el revisor se portan a Azure Pipelines.
- **BaseRef**, guía de diseño sin copiar código (decisión de la persona):

| Activo de referencia | Guía para |
|---|---|
| `BaseRef/workflow/docs/architecture.md` | Job como DAG de tareas en clúster efímero, medallion y patrón de ejecución de un step |
| `BaseRef/workflow/databricks.yml` y `resources/workflow.yml` | Bundle por targets y definición del job |
| `BaseRef/workflow/config/workflow_manifest.yaml` y `config.yaml` | Manifest `requires`/`provides` y ConfigFile |
| `BaseRef/workflow/src/steps/` y `docs/pipeline-steps.md` | Steps de discovery, ingesta, chunking, embeddings e indexación |
| `BaseRef/workflow/docs/triggers.md` | Opciones de trigger del job |

- **EjOCR** (referencia para el step de extracción y para el caso de uso):
  - `src/extractor.py`: llamada a Content Understanding con un analizador por ID.
  - `schema_contratos.json`: ejemplo del formato de esquema (12 categorías, 76 campos). El esquema real es del caso de uso.
  - `src/auditor.py` y `logs/trazabilidad_extraccion.json`: estado por documento → se reemplaza por las tablas de logs.
  - `output/resumen_*.csv` e `informe_extraccion_por_documento.Rmd`: completitud y confianza → métricas de calidad.
  - `src/api_client.py`: descarga con cookies de una sesión de navegador frente a un WAF, a partir de IDs tomados de un Excel. No sirve como base.
- **Diccionario de campos**: `Control Doc/Campo Extraccion de Contratos.xlsx` → insumo del esquema del caso de uso.
- PENDIENTE: ¿qué endpoints ofrece Control Doc para listar expedientes y documentos con sus metadatos y fecha de modificación (necesaria para el incremental), y qué credencial de servicio usará el conector?

## 5. Coordinación con otros equipos o sistemas

- **`repo-libreria`**: cada step que necesita una capacidad nueva depende de la feature `LIB-NN` que la entrega y de su publicación.
- **`repo-agente-conversacional`**: contrato del índice (campos, enlace al documento, campos filtrables y modelo de embeddings) antes de la feature 09.
- **TI de SUMMA y administradores de Control Doc**: credencial de servicio, documentación de la API y límites de uso.
- **Plataforma y arquitectura de datos**: workspace, catálogos, permisos y red por ambiente.

## 6. Principios del alcance

- Entra lo que sirve a cualquier fuente o caso de uso documental. Lo específico de Control Doc va a su repo, y lo genérico reutilizable va a `repo-libreria`.
- Nada que escriba en la fuente.
- Nada que requiera Azure Data Factory.

## Relación con otros documentos

- [[mission]] — por qué existe el proyecto.
- [[tech-stack]] — con qué se construye.
- [[roadmap]] — en qué orden se entrega este alcance.
