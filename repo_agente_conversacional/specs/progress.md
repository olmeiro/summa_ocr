# Progreso

> Continuidad entre sesiones. Cada sesión empieza leyendo este archivo y lo actualiza al terminar.
> Lo terminado lo registra git: aquí solo vive el estado actual. El registro guarda las últimas 10 sesiones; borra las más antiguas.

## Estado actual

- Constitución redactada (greenfield): `mission`, `tech-stack`, `alcance-inicial` y `roadmap`, en la rama `init/constitucion` del repo `summa_ocr`, carpeta `repo_agente_conversacional/specs/`. Sin commit.
- La plantilla usa la librería `repo-libreria`. El roadmap tiene 10 features, todas en `not_started`, con dependencias `LIB-NN`; la primera es `01-esqueleto-api`, que no depende de la librería.
- Quedan 18 `PENDIENTE:` abiertos en la Constitución.
- Gate de `summa_ocr` en verde el 2026-11-12. Este repo todavía no tiene código ni harness propio.

## Siguiente paso

Responder los `PENDIENTE:` que bloquean la feature 01: versión de Python (en `repo-libreria`) y modelo de ramas ([[tech-stack]] §12). Después, commit de la Constitución y rama `feature/01-esqueleto-api` para `/specs feature 01-esqueleto-api`.

## Bloqueos

- Crear el repo en Azure DevOps, mover el harness y portar el gate y el revisor a Azure Pipelines.
- Contrato del índice con `repo-workflow` antes de la feature 07.

## Registro de sesiones

- 2026-11-12 — Constitución ajustada a 3 repos: la lógica común pasa a `repo-libreria`, la plantilla sigue el diseño del framework de referencia y los extras que SyN no pide quedan fuera — pendiente de respuestas y commit.
- 2026-11-12 — Constitución redactada a partir de SyN y de las decisiones de la persona (Azure DevOps, FastAPI en Container Apps, caso de uso Control Doc fuera de este repo).
