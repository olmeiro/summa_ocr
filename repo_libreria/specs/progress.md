# Progreso

> Continuidad entre sesiones. Cada sesión empieza leyendo este archivo y lo actualiza al terminar.
> Lo terminado lo registra git: aquí solo vive el estado actual. El registro guarda las últimas 10 sesiones; borra las más antiguas.

## Estado actual

- Constitución redactada (greenfield): `mission`, `tech-stack`, `alcance-inicial` y `roadmap`, en la rama `init/constitucion` del repo `summa_ocr`, carpeta `repo_libreria/specs/` (nombre provisional). El afinado del 2026-11-13 está sin commit.
- Roadmap con 18 features (`LIB-01` a `LIB-18`), todas en `not_started`; la primera es `01-esqueleto-paquete`. Las dos plantillas dependen de estas features. Su §4 dice qué ofrece la base para cada una y qué cambia.
- DEC-002 reemplaza la regla 3 de DEC-001: módulos comunes, de workflow y de agente.
- Quedan 15 `PENDIENTE:` abiertos en la Constitución.
- Gate de `summa_ocr` en verde el 2026-11-12. Este repo todavía no tiene código ni harness propio.

## Siguiente paso

Confirmar lo marcado `[inferido]` el 2026-11-13: DEC-002 y las features nuevas 05 y 06. Responder los `PENDIENTE:` que bloquean la feature 01: versión de Python, nombre del paquete y modelo de ramas ([[tech-stack]] §1 y §12). Después, commit de la Constitución y rama `feature/01-esqueleto-paquete` para `/specs feature 01-esqueleto-paquete`.

## Bloqueos

- Crear el repo en Azure DevOps, mover el harness y portar el gate y el revisor a Azure Pipelines.
- Feed de Azure Artifacts de SUMMA, que bloquea LIB-04.

## Registro de sesiones

- 2026-11-13 — Specs afinadas contra el código de la base y de EjOCR: roadmap de 16 a 18 features (almacenamiento en Unity Catalog y contexto de workflow, que el alcance pedía y ninguna feature entregaba), §4 del roadmap con el punto de partida de cada feature, DEC-002 y citas corregidas — pendiente de confirmación y commit.
- 2026-11-12 — Validada la decisión de una sola librería y registrada en DEC-001 (extras por consumidor, fronteras de import, humo por extra). Nombres de SUMMA y primera versión `0.1.0` — pendiente de commit.
- 2026-11-12 — Constitución creada al decidir 3 repos (una librería y dos plantillas). Toma como guía de diseño el framework de referencia, sin copiar código y con el derecho de reutilización confirmado por la persona — pendiente de respuestas y commit.
