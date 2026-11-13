# Misión — Framework de procesamiento e indexación (repo-workflow)

> Constitución. Define **por qué** existe el proyecto, para quién y bajo qué restricciones. No elige tecnología: eso va en [[tech-stack]].

**Fuentes** (todas en `project-context/`, fuera de git):
- **SyN**: `situacion y necesidad actual.pdf`.
- **EjOCR**: `summa-documentos-ocr-main/summa-documentos-ocr-main/`, ejercicio de extracción sobre una muestra de Control Doc.
- **Metadatos CD**: `Control Doc/METADATA CONTROL DOC.xlsx`.
- **BaseRef**: `ejemplo-framework/`, un framework de referencia construido para otro cliente. Se usa solo como guía de diseño, sin copiar código (decisión de la persona, 2026-11-12). `BaseRef/workflow/…` es su plantilla de workflow; `BaseRef/core/…` y `BaseRef/cognitive/…` son el `src/<paquete>/` de sus librerías.
- Decisiones de la persona del 2026-11-12.

Lo marcado `[inferido]` se deriva de esas fuentes y espera confirmación. La carpeta del repo se llama `repo_worklow/`; el componente, `repo-workflow`.

---

## 1. Propósito

Plantilla de repositorio, reutilizable y configurable, para construir en Azure Databricks los pipelines que llevan información desde fuentes externas hasta índices consultables por agentes:

- extracción y almacenamiento por capas;
- procesamiento de documentos estructurados y no estructurados;
- extracción de campos;
- segmentación, embeddings e indexación en Azure AI Search.

Todo se configura por iniciativa, no por código (SyN, arquitectura §1).

## 2. Problema que resuelve

- SUMMA aborda varias iniciativas de IA con esfuerzos aislados, dependencias técnicas y tiempos largos hasta producción (SyN, "Situación actual y necesidad").
- Cada caso de uso documental tendría que reconstruir conexión a la fuente, OCR, extracción, chunking, embeddings, indexación, trazabilidad y despliegue.
- El primer caso de uso lo muestra. Control Doc guarda número de expediente y metadatos básicos, pero no permite consultar ni analizar el contenido de los contratos (SyN, "Situación actual"). Al 30 de septiembre había 1.828 consecutivos, de los cuales 824 están por procesar: 737 vigentes y 87 vencidos (Metadatos CD, hoja "Estadistica Inicial").
- El ejercicio de extracción mostró el costo de hacerlo a mano: descarga con sesión de navegador, trazabilidad en archivos locales y métricas de calidad calculadas aparte (EjOCR, `src/api_client.py:22-36`, `src/auditor.py`).

## 3. Usuarios y consumidores

### Personas

- **Ingenieros de datos y científicos de datos** que crean el pipeline de un caso de uso: escriben configuración (fuente, esquema de extracción, chunking, índice), no infraestructura (SyN, arquitectura §5).
- **Equipo de plataforma y DevOps**: despliega y opera los jobs en desarrollo y producción.
- **Dueños del dato** de cada caso de uso, como la Gerencia de Abastecimiento para contratos: consultan la calidad de lo extraído (completitud y confianza) antes de confiar en ello (`Control Doc/Campo Extraccion de Contratos.xlsx`, hoja "Caso de Uso", Actores).

### Sistemas

- **Fuentes por API**, en solo lectura; la primera es Control Doc (SyN, "Alcance").
- **Agentes** construidos con `repo-agente-conversacional`, que consultan los índices de Azure AI Search que este repo publica.
- **Unity Catalog**: tablas de datos procesados, logs y auditoría.

## 4. Postura arquitectónica

- Plantilla de repositorio de procesos batch: cada caso de uso clona el repo y configura sus propios jobs (SyN, etapa 7).
- La lógica común vive en la librería versionada `repo-libreria`: clientes de Azure, extracción, chunking, búsqueda vectorial, fuentes HTTP y trazabilidad. La plantilla aporta el bundle, el manifest, los steps que la orquestan y la configuración (decisión de la persona, 2026-11-12; patrón de `BaseRef/workflow/docs/architecture.md`).
- Es el productor del ecosistema: deja la información disponible, procesada, actualizada e indexada; no responde consultas (SyN, "La distinción arquitectónica más importante").
- Almacenar lo procesado y publicar el índice son dos responsabilidades distintas dentro del mismo pipeline (SyN, §4 "Dos aspectos que conviene precisar").

## 5. Resultados esperados

- Un caso de uso nuevo solo escribe su conector o configuración de fuente, su esquema de extracción y la configuración de su índice (SyN, "¿Qué significa esto para futuros casos de uso?").
- Cada ejecución periódica incorpora en la base de conocimiento los documentos nuevos y modificados y retira los eliminados (SyN, arquitectura §3).
- Las mejoras del framework llegan a los pipelines ya creados subiendo la versión de la librería, sin reclonar la plantilla.
- Cada ejecución y cada documento dejan rastro: `run_id`, tiempos, causa de error, y para cada campo extraído su confianza y la página de origen (SyN, etapa 5; EjOCR, `data/processed/*.json`).

## 6. Objetivos medibles

Umbrales iniciales, que se revisan en cada replanning (decisión de la persona, 2026-11-13). Línea base del ejercicio de extracción con 76 campos sobre 35 documentos: completitud mediana del 38 % (máxima 65 %) y confianza promedio mediana de 0,71 (EjOCR, `output/resumen_documentos.csv`).

- **Cobertura por ejecución**: al menos el 98 % de los documentos que entrega la fuente queda indexado; el resto queda registrado con su causa en las tablas de logs.
- **Duración**: la ejecución semanal termina en 4 horas o menos.
- **Calidad de extracción**: completitud y confianza se miden por campo y por documento en cada ejecución, sin bloquearla. Meta: confianza promedio por documento de 0,70 o más.
- **Tiempo para un pipeline nuevo**: no se mide por ahora; se mide al hacer el segundo caso de uso.

## 7. Restricciones

- **Ejecución**: todo el proceso corre en Azure Databricks, sin Azure Data Factory (SyN, componente A). Hay dos ambientes independientes, desarrollo/pruebas y producción: código común; datos, índices y configuración separados (SyN, componente C).
- **Integración**: las fuentes se leen sin modificarlas (SyN, "Alcance": "sin modificar el sistema Control Doc"). Lo procesado se guarda en Azure Data Lake Storage por capas bronze, silver y gold, y los índices viven en Azure AI Search (SyN, arquitectura §1).
- **Diseño**: los componentes genéricos se separan de cada caso de uso; el framework no se acopla a Control Doc (SyN, arquitectura §4).
- **Operación**: la base de conocimiento solo se actualiza al ejecutar el pipeline (SyN, "Fuera de alcance"). Código y pipelines en Azure DevOps (decisión de la persona). Gobierno de datos con Unity Catalog y secretos en Key Vault (SyN, componente A).
- **Legales y éticas**: los contratos son información interna y contienen datos personales (nombres y documentos de identidad de firmantes; `Control Doc/Campo Extraccion de Contratos.xlsx`, categoría 1). PENDIENTE (dueño: legal / protección de datos de SUMMA): ¿se enmascaran o excluyen datos personales antes de indexar? Mientras no se responda, el acceso a lo indexado se limita a los usuarios de la app de Teams del caso de uso.

## 8. Principios rectores

1. **Configuración por iniciativa**: un caso de uso nuevo se define con archivos de configuración (manifest/DAG, ConfigFiles y esquema de extracción) sin tocar el núcleo (SyN, etapa 5).
2. **Re-ejecutar es seguro**: procesar dos veces el mismo documento no duplica registros ni chunks en el índice. `[inferido]` de SyN, estrategia incremental.
3. **Nada se descarta en silencio**: cada documento que no se descarga, no se procesa o no se indexa queda registrado con su causa. `[inferido]` de SyN, etapa 5 (trazas SLA/auditoría).
4. **Trazabilidad hasta la página**: cada chunk y cada campo extraído conserva el documento y la página de origen. `[inferido]` de EjOCR (`source` y `spans` en `data/processed/*.json`).
5. **La fuente es de solo lectura** (SyN, "Alcance").

## Relación con otros documentos

- [[tech-stack]] — cómo se cumple esta misión técnicamente.
- [[alcance-inicial]] — qué entra y qué no.
- [[roadmap]] — en qué orden se entrega.
