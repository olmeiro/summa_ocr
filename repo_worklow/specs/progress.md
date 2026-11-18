# Progreso

> Continuidad entre sesiones. Cada sesión empieza leyendo este archivo y lo actualiza al terminar.
> Lo terminado lo registra git: aquí solo vive el estado actual. El registro guarda las últimas 10 sesiones; borra las más antiguas.

## Estado actual

- Constitución redactada (greenfield) en la rama `init/constitucion` del repo `summa_ocr`, carpeta `repo_worklow/specs/`. Las respuestas del 2026-11-13 están sin commit.
- La plantilla usa la librería `summa-ai-framework` (`repo-libreria`). El roadmap tiene 16 features, todas en `not_started`, con dependencias `LIB-NN`; la primera es `01-esqueleto-bundle`, que no depende de la librería. Su §4 dice qué ofrece la base para cada una y qué cambia.
- Decidido el 2026-11-13: Python 3.12 y Databricks Runtime 18 LTS (cuota de unos 10 núcleos en el workspace), un workspace por ambiente, trigger semanal, ramas con `develop`, logs por iniciativa (los crea el job), analizador desde el esquema versionado, Word directo, Excel como tabla, umbrales iniciales en [[mission]] §6.
- Quedan 5 `PENDIENTE:` en la Constitución, todos con dueño: identidad del job y nombres de prod (plataforma), IaC (SUMMA), datos personales (legal) y API de Control Doc (TI).
- Gate de `summa_ocr` en verde el 2026-11-13. Este repo todavía no tiene código ni harness propio.

## Siguiente paso

Commit de la Constitución. Después, rama `feature/01-esqueleto-bundle` desde `develop` y `/specs feature 01-esqueleto-bundle`, con DBR 18 LTS y un clúster que quepa en la cuota de núcleos ([[tech-stack]] §1).

## Bloqueos

- Crear el repo en Azure DevOps, mover el harness y portar el gate y el revisor a Azure Pipelines (con `develop` como rama de integración).
- API de Control Doc: endpoint de listado con fecha de modificación y credencial de servicio sin WAF (TI de SUMMA). Se espera la API: bloquea las features 10 y 11 ([[alcance-inicial]] §4).
- Contrato del índice con `repo-agente-conversacional` antes de la feature 09.

## Registro de sesiones

- 2026-11-13 — Respuestas de la persona a los `PENDIENTE` y confirmación de las convenciones inferidas; hallazgos de la API de Control Doc anotados; umbrales iniciales en la misión; runtime fijado en 18 LTS tras revisar el workspace; de 24 a 5 `PENDIENTE` con dueño — pendiente de commit.
- 2026-11-13 — Specs afinadas contra el código de la base y de EjOCR: dependencias `LIB-NN` renumeradas, §4 del roadmap con el punto de partida de cada feature, convenciones que la base no cumple (tablas por ejecución, identidad por nombre de archivo, steps que ejecutan al importarse).
- 2026-11-12 — Constitución ajustada a 3 repos: la lógica común pasa a `repo-libreria`, la plantilla sigue el diseño de bundle, manifest y steps del framework de referencia y los extras que SyN no pide quedan fuera.
- 2026-11-12 — Constitución redactada a partir de SyN, del ejercicio de extracción EjOCR y de las decisiones de la persona (Azure DevOps, extracción con Content Understanding, conector genérico en el framework y el de Control Doc en el caso de uso).
