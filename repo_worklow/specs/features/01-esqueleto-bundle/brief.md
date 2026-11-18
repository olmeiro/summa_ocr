# 01 — esqueleto-bundle — Brief

> Ficha ejecutiva: qué problema resuelve la feature y por qué ahora. Sin diseño técnico ni tareas.

## Problema

La plantilla del workflow no tiene código: no hay bundle que desplegar, ni job, ni sitio para los steps. Ninguna feature del [[roadmap]] puede probarse en Databricks hasta que exista el esqueleto. Ese esqueleto tiene que cumplir ya las reglas de la Constitución que la base de referencia incumple:

- un clúster efímero que quepa en la cuota ([[tech-stack]] §1);
- un trigger semanal pausado en dev y activo en prod (§8);
- la versión de la librería en un solo lugar (§8);
- ningún secreto en el bundle (§9). La base lleva credenciales en claro (`BaseRef/workflow/databricks.yml:109-112`).

## Por qué ahora

Es la primera feature del [[roadmap]] y no depende de nada. La persona la prioriza sobre la plantilla del agente para descubrir pronto los obstáculos de Databricks, que está aprendiendo (2026-11-18).

## Decisión de diseño

Decisiones de la persona del 2026-11-18:

- **Ubicación**: el código vive en `repo_worklow/`, dentro de `summa_ocr`, como la librería en `repo_libreria/`. El gate de la raíz cubre sus tests.
- **Librería sin feed**: mientras no exista LIB-04, el bundle construye la wheel de `summa-ai-framework` desde `../repo_libreria` al desplegar, y el job la instala. Así se prueba de verdad que la librería y sus dependencias funcionan en DBR 18. Con el feed se cambiará por la instalación desde Azure Artifacts.
- **Clúster**: un solo nodo `Standard_D4ds_v5` (4 núcleos, 16 GB). El tipo de nodo es una variable del bundle.
- **Trigger**: lunes a las 02:00, `America/Bogota`, con día y hora como variables.
- **Workspace de pruebas**: el workspace de dev de SUMMA no está disponible, así que se usa uno de pruebas de la persona. El target `dev` no lleva `workspace.host`: lo toma del perfil local del CLI. Ningún dato de ese workspace entra al repo, y el mismo bundle servirá con el de SUMMA.
- **Prueba en serverless**: el workspace de pruebas resultó ser solo serverless y rechazó el clúster clásico al crear el job. La persona decidió probar en serverless, solo como prueba (2026-11-18):
  - una variante desechable del job, fuera del repo, con el mismo step y la misma wheel;
  - sus aprendizajes pasan a las specs;
  - el bundle real sigue con clúster clásico y DBR 18, que tendrá su ejecución cuando haya un workspace que lo permita.

## Incluye

- `repo_worklow/databricks.yml`:
  - targets `dev` (modo development) y `prod` (modo production);
  - variables del runtime (`18.x-scala2.13`), del tipo de nodo, del trigger y de la versión de la librería;
  - el artefacto de la wheel.
- `repo_worklow/resources/workflow.yml`: un job con su clúster efímero de un nodo, el trigger semanal y una tarea `s00_humo`.
- `repo_worklow/src/steps/s00_humo.py`: comprueba en el clúster el ambiente, Python, el runtime y la versión instalada de la librería, e importa sus módulos `config` y `security`. No ejecuta nada al importarse.
- Tests del gate: estructura del bundle, versión de la librería en un solo lugar, ausencia de secretos y el step.
- Ejecución del step y de la librería en Databricks, con la variante serverless del job en el workspace de pruebas.
- Regla en [[tech-stack]] §2: los steps no llaman a `sys.exit`.
- Gate de la raíz extendido a `repo_worklow/`. `.databricks/` en `.gitignore`.

## No incluye

- Manifest `requires`/`provides` y patrón de step: es la 02, que espera LIB-06.
- ConfigFile por ambiente y Key Vault: es la 03.
- Unity Catalog, esquemas y tablas: features 04 en adelante.
- Pipelines de Azure DevOps: es la 15.
- Instalación desde el feed y `requirements.txt` con la versión fijada: llegan con LIB-04.

## Resultado esperado

- `databricks bundle validate -t dev` y `-t prod` pasan con el perfil del CLI.
- En Databricks, el step `s00_humo` instala e importa `summa-ai-framework 0.1.0` con Python 3.12 y termina en `SUCCESS`. En el workspace de pruebas se ejecuta en serverless; en clásico con DBR 18, cuando haya workspace.
