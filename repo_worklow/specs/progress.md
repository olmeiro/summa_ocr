# Progreso

> Continuidad entre sesiones. Cada sesión empieza leyendo este archivo y lo actualiza al terminar.
> Lo terminado lo registra git: aquí solo vive el estado actual. El registro guarda las últimas 10 sesiones; borra las más antiguas.

## Estado actual

- Constitución redactada (greenfield): `mission`, `tech-stack`, `alcance-inicial` y `roadmap`, en la rama `init/constitucion` del repo `summa_ocr`, carpeta `repo_worklow/specs/`. El afinado del 2026-11-13 está sin commit.
- La plantilla usa la librería `repo-libreria`. El roadmap tiene 16 features, todas en `not_started`, con dependencias `LIB-NN`; la primera es `01-esqueleto-bundle`, que no depende de la librería. Su §4 dice qué ofrece la base para cada una y qué cambia.
- Quedan 24 `PENDIENTE:` abiertos en la Constitución.
- Gate de `summa_ocr` en verde el 2026-11-12. Este repo todavía no tiene código ni harness propio.

## Siguiente paso

Confirmar lo marcado `[inferido]` el 2026-11-13 en [[tech-stack]] §2 y §8: tablas de nombre estable, steps como funciones, un ConfigFile por ambiente y manifest leído por la librería. Responder los `PENDIENTE:` que bloquean la feature 01: versión de Databricks Runtime, workspaces por ambiente y modelo de ramas ([[tech-stack]] §1, §7 y §12). Después, commit de la Constitución y rama `feature/01-esqueleto-bundle` para `/specs feature 01-esqueleto-bundle`.

## Bloqueos

- Crear el repo en Azure DevOps, mover el harness y portar el gate y el revisor a Azure Pipelines.
- API de Control Doc: credencial de servicio y endpoint de listado con fecha de modificación. El ejercicio EjOCR descargó con cookies de navegador; bloquea las features 10 y 11 para Control Doc.
- Contrato del índice con `repo-agente-conversacional` antes de la feature 09.

## Registro de sesiones

- 2026-11-13 — Specs afinadas contra el código de la base y de EjOCR: dependencias `LIB-NN` renumeradas, §4 del roadmap con el punto de partida de cada feature, convenciones que la base no cumple (tablas por ejecución, identidad por nombre de archivo, steps que ejecutan al importarse) y 4 `PENDIENTE` nuevos — pendiente de confirmación y commit.
- 2026-11-12 — Constitución ajustada a 3 repos: la lógica común pasa a `repo-libreria`, la plantilla sigue el diseño de bundle, manifest y steps del framework de referencia y los extras que SyN no pide quedan fuera — pendiente de respuestas y commit.
- 2026-11-12 — Constitución redactada a partir de SyN, del ejercicio de extracción EjOCR y de las decisiones de la persona (Azure DevOps, extracción con Content Understanding, conector genérico en el framework y el de Control Doc en el caso de uso).
