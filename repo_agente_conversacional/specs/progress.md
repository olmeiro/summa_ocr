# Progreso

> Continuidad entre sesiones. Cada sesión empieza leyendo este archivo y lo actualiza al terminar.
> Lo terminado lo registra git: aquí solo vive el estado actual. El registro guarda las últimas 10 sesiones; borra las más antiguas.

## Estado actual

- Constitución redactada (greenfield) en la rama `init/constitucion` del repo `summa_ocr`, carpeta `repo_agente_conversacional/specs/`. Las respuestas del 2026-11-13 están sin commit.
- La plantilla usa la librería `summa-ai-framework` (`repo-libreria`). El roadmap tiene 10 features, todas en `not_started`, con dependencias `LIB-NN`; la primera es `01-esqueleto-api`, que no depende de la librería. MCP salió y entró `08-canal-teams`. Su §4 dice qué ofrece la base para cada una y qué cambia.
- Decidido el 2026-11-13: Python 3.12, tokens de Bot Framework, la sesión nace con el primer mensaje, todos ven todo el índice, historial de 90 días, solo logs, ramas con `develop`, umbrales iniciales en [[mission]] §6.
- Quedan 3 `PENDIENTE:` en la Constitución, todos con dueño: identidad del Container App y nombres de recursos (plataforma) e IaC (SUMMA).
- Gate de `summa_ocr` en verde el 2026-11-13. Este repo todavía no tiene código ni harness propio.

## Siguiente paso

Commit de la Constitución. Después, crear `develop`, la rama `feature/01-esqueleto-api` desde ella y ejecutar `/specs feature 01-esqueleto-api`.

## Bloqueos

- Crear el repo en Azure DevOps, mover el harness y portar el gate y el revisor a Azure Pipelines (con `develop` como rama de integración).
- Contrato del índice con `repo-workflow` antes de la feature 07.
- App Registration del bot y Azure Bot Service con el canal Teams (TI de SUMMA) antes de la feature 08.

## Registro de sesiones

- 2026-11-13 — Respuestas de la persona a los `PENDIENTE`: adaptador de Teams en la plantilla (feature 08), MCP fuera, sesión al primer mensaje, token de Bot Framework, umbrales iniciales; de 19 a 3 `PENDIENTE` con dueño — pendiente de commit.
- 2026-11-13 — Specs afinadas contra el código de la base: dependencias `LIB-NN` renumeradas, §4 del roadmap con el punto de partida de cada feature, valores por defecto seguros y respuesta con fuentes como datos.
- 2026-11-12 — Constitución ajustada a 3 repos: la lógica común pasa a `repo-libreria`, la plantilla sigue el diseño del framework de referencia y los extras que SyN no pide quedan fuera.
- 2026-11-12 — Constitución redactada a partir de SyN y de las decisiones de la persona (Azure DevOps, FastAPI en Container Apps, caso de uso Control Doc fuera de este repo).
