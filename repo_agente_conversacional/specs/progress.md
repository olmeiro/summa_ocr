# Progreso

> Continuidad entre sesiones. Cada sesión empieza leyendo este archivo y lo actualiza al terminar.
> Lo terminado lo registra git: aquí solo vive el estado actual. El registro guarda las últimas 10 sesiones; borra las más antiguas.

## Estado actual

- Constitución en `main` (PR #1). La librería `summa-ai-framework` ya tiene LIB-01 a LIB-03 en `main` (configuración y Key Vault).
- **01-esqueleto-api `accepted`**, en `main` con el PR #6 (`f9c21ac`). Ya existen la app FastAPI con `create_app`, `/health` y `/ready`, `AppSettings` (`APP_ENVIRONMENT` obligatoria y `APP_DOCS`), la imagen Docker sin privilegios y la cobertura del gate de la raíz. Revisor de Claude: `accept` en la vuelta 2; revisor de CI con `gpt-6-luna`: `accept`. El cierre entra con un commit directo a `main`, porque el PR se mergeó antes.
- El roadmap tiene 10 features: la 01 `accepted` y las demás `not_started`, con dependencias `LIB-NN`. Su §4 dice qué ofrece la base para cada una y qué cambia.
- Decidido el 2026-11-13: Python 3.12, tokens de Bot Framework, la sesión nace con el primer mensaje, todos ven todo el índice, historial de 90 días, solo logs, ramas con `develop`, umbrales iniciales en [[mission]] §6.
- Quedan 3 `PENDIENTE:` en la Constitución, todos con dueño: identidad del Container App y nombres de recursos (plataforma) e IaC (SUMMA).
- El agente todavía no tiene harness propio: lo cubren el gate, los hooks y el revisor de `summa_ocr`.

## Siguiente paso

1. La persona commitea el cierre de 01-esqueleto-api en `main` y lo sube.
2. Replanning de [[tech-stack]] §3: la salud vive en la raíz de rutas, no en `api/v1/` (deuda de 01-esqueleto-api).
3. Spec de 02-configuracion (`/specs feature 02-configuracion`), en `feature/02-configuracion`. Depende de 01 y de LIB-03, y las dos están en `main`.

## Bloqueos

- Crear el repo en Azure DevOps, mover el harness y portar el gate y el revisor a Azure Pipelines (con `develop` como rama de integración).
- Contrato del índice con `repo-workflow` antes de la feature 07.
- App Registration del bot y Azure Bot Service con el canal Teams (TI de SUMMA) antes de la feature 08.

## Registro de sesiones

- 2026-11-19 — Docker Desktop instalado en la máquina de la persona (antes hubo que activar "Virtual Machine Platform" con `wsl --install` como administrador); CA-6 de 01-esqueleto-api en verde. Revisor de Claude: `revise` en la vuelta 1 (tests dependientes de `APP_DOCS`, imagen endurecida) y `accept` en la vuelta 2. `accept` de `gpt-6-luna` en local y en CI; PR #6 mergeado y cierre en `main`. Decidido: desde ahora la feature se cierra en su rama antes de abrir el PR (`AGENTS.md` y skill `specs`).
- 2026-11-13 — Respuestas de la persona a los `PENDIENTE`: adaptador de Teams en la plantilla (feature 08), MCP fuera, sesión al primer mensaje, token de Bot Framework, umbrales iniciales; de 19 a 3 `PENDIENTE` con dueño — pendiente de commit.
- 2026-11-13 — Specs afinadas contra el código de la base: dependencias `LIB-NN` renumeradas, §4 del roadmap con el punto de partida de cada feature, valores por defecto seguros y respuesta con fuentes como datos.
- 2026-11-12 — Constitución ajustada a 3 repos: la lógica común pasa a `repo-libreria`, la plantilla sigue el diseño del framework de referencia y los extras que SyN no pide quedan fuera.
- 2026-11-12 — Constitución redactada a partir de SyN y de las decisiones de la persona (Azure DevOps, FastAPI en Container Apps, caso de uso Control Doc fuera de este repo).
