# Progreso

> Continuidad entre sesiones. Cada sesión empieza leyendo este archivo y lo actualiza al terminar.
> Lo terminado lo registra git: aquí solo vive el estado actual. El registro guarda las últimas 10 sesiones; borra las más antiguas.

## Estado actual

- Constitución en `main` (PR #1). La librería `summa-ai-framework` (`repo-libreria`) ya tiene LIB-01 a LIB-03 en `main`.
- **01-esqueleto-bundle `accepted`** (revisor de Claude y revisor de CI con `gpt-6-luna`, a la primera) y en `main` (PR #5, `bb8909d`); el cierre, en commit directo a `main`. Contenido:
  - `repo_worklow/` es un Databricks Asset Bundle (`databricks.yml`, `resources/workflow.yml`, `src/steps/s00_humo.py` y `tests/`), con clúster clásico de un nodo y DBR 18, trigger semanal y la versión de la librería en un solo lugar;
  - `bundle validate` en verde para dev y prod;
  - en el workspace de pruebas de la persona, que es solo serverless, el step corre en serverless en `SUCCESS` con la librería 0.1.0;
  - en SUMMA (`dbr-analitica-summa-aba-qa`) corre en clásico en `SUCCESS` desde el 2026-11-19, con `Standard_D4d_v4`: la política de discos de SUMMA rechaza los tamaños con Premium (DEC-001).
- Roadmap con 16 features: 01 `accepted` y las demás en `not_started`, con dependencias `LIB-NN`. Su §4 dice qué ofrece la base para cada una y qué cambia.
- Decidido el 2026-11-13: Python 3.12 y Databricks Runtime 18 LTS (cuota de unos 10 núcleos en el workspace), un workspace por ambiente, trigger semanal, ramas con `develop`, logs por iniciativa (los crea el job), analizador desde el esquema versionado, Word directo, Excel como tabla, umbrales iniciales en [[mission]] §6.
- Quedan 5 `PENDIENTE:` en la Constitución, todos con dueño: identidad del job y nombres de prod (plataforma), IaC (SUMMA), datos personales (legal) y API de Control Doc (TI).
- Gate de `summa_ocr` en verde el 2026-11-18 (147 tests, 20 del workflow). Harness compartido con la raíz.

## Siguiente paso

1. Replanning corto: ¿clásico o serverless para SUMMA? Datos del 2026-11-19: los dos llegan a los servicios; serverless arranca en 5 s (el clásico, en unos 8 min) y no le afecta la política de discos. Falta además que SUMMA y plataforma elijan el workspace del framework.
2. La 02 (`manifest-dag`) espera LIB-06.
3. Hito 0: ver una extracción real con Content Understanding (por ejemplo `prebuilt-contract`) desde un job serverless.

## Bloqueos

- Crear el repo en Azure DevOps, mover el harness y portar el gate y el revisor a Azure Pipelines (con `develop` como rama de integración).
- API de Control Doc: endpoint de listado con fecha de modificación y credencial de servicio sin WAF (TI de SUMMA). Se espera la API: bloquea las features 10 y 11 ([[alcance-inicial]] §4).
- Contrato del índice con `repo-agente-conversacional` antes de la feature 09.
- **Red del workspace de SUMMA** (antes de la 03): el cómputo de Databricks tiene que llegar a Entra ID, Key Vault, Azure OpenAI, AI Search y Content Understanding, con private endpoints y DNS privado o con una lista de salidas permitidas. Es tarea de plataforma o de la IaC, SyN etapas 1 y 2.
  - **Prueba del 2026-11-18**: un notebook serverless del workspace de pruebas no resolvió por DNS ni `login.microsoftonline.com`, ni `*.vault.azure.net`, ni `management.azure.com`, ni `pypi.org`.
  - **La librería respondió bien**: devolvió `ConfigError` con la ubicación y el motivo, sin valores.
  - **Ese workspace solo sirve** para pruebas que no salen de Databricks.
  - **2026-11-19, en `dbr-analitica-summa-aba-qa`**: el clúster clásico arranca, instala la wheel con sus dependencias y ejecuta el step. Una prueba de red sin credenciales llegó, desde clásico y desde serverless, a Entra ID, Key Vault, Foundry (OpenAI y Content Understanding), AI Search, Cosmos DB, PyPI y Azure DevOps, siempre por IP pública. En dev la red ya no bloquea; la red privada sigue siendo tarea de la IaC. Con las claves en un scope temporal, un job serverless generó un embedding (3072 dimensiones) y creó, consultó y borró un índice vectorial en AI Search. Falta leer las claves de Key Vault: la identidad del job y el firewall del vault.

  Sigue abierta también la identidad del job (tech-stack §6): en Databricks no hay `az login`.

## Registro de sesiones

- 2026-11-19 — Primera ejecución en SUMMA (`dbr-analitica-summa-aba-qa`). Con `Standard_D4ds_v5` falló al crear el clúster por la política de discos Premium; con `Standard_D4d_v4`, `SUCCESS` en clásico con DBR 18.3. Nuevo valor por defecto y DEC-001. Prueba de red sin credenciales: clásico y serverless llegan a todos los servicios por IP pública. Con claves, embeddings y AI Search funcionan desde serverless. Content Understanding funciona en la región con la API GA. Para dev se usa `text-embedding-3-large`.
- 2026-11-18 — 01-esqueleto-bundle. Decisiones de la persona:
  - código en `repo_worklow/`, wheel construida al desplegar, nodo único `D4ds_v5` y trigger los lunes a las 02:00 Bogotá;
  - prueba en serverless, solo como prueba.

  Aprendizajes: workspace solo serverless, serverless sin salida a internet, `environment_version`, `sys.exit` en IPython. Revisor de Claude `accept`; revisor de CI `accept` a la primera; PR #5 mergeado; cierre en commit directo a `main`.
- 2026-11-13 — Respuestas de la persona a los `PENDIENTE` y confirmación de las convenciones inferidas; hallazgos de la API de Control Doc anotados; umbrales iniciales en la misión; runtime fijado en 18 LTS tras revisar el workspace; de 24 a 5 `PENDIENTE` con dueño — pendiente de commit.
- 2026-11-13 — Specs afinadas contra el código de la base y de EjOCR: dependencias `LIB-NN` renumeradas, §4 del roadmap con el punto de partida de cada feature, convenciones que la base no cumple (tablas por ejecución, identidad por nombre de archivo, steps que ejecutan al importarse).
- 2026-11-12 — Constitución ajustada a 3 repos: la lógica común pasa a `repo-libreria`, la plantilla sigue el diseño de bundle, manifest y steps del framework de referencia y los extras que SyN no pide quedan fuera.
- 2026-11-12 — Constitución redactada a partir de SyN, del ejercicio de extracción EjOCR y de las decisiones de la persona (Azure DevOps, extracción con Content Understanding, conector genérico en el framework y el de Control Doc en el caso de uso).
