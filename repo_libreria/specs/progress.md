# Progreso

> Continuidad entre sesiones. Cada sesión empieza leyendo este archivo y lo actualiza al terminar.
> Lo terminado lo registra git: aquí solo vive el estado actual. El registro guarda las últimas 10 sesiones; borra las más antiguas.

## Estado actual

- Constitución redactada (greenfield) en la rama `init/constitucion` del repo `summa_ocr`, carpeta `repo_libreria/specs/` (nombre provisional). Las respuestas del 2026-11-13 están sin commit.
- Paquete `summa-ai-framework`, Python 3.12, cobertura mínima del 80 %, ramas `feature/NN-nombre` → `develop` → `main`; plataforma aprueba las versiones.
- Roadmap con 17 features (`LIB-01` a `LIB-17`), todas en `not_started`; la primera es `01-esqueleto-paquete`. El cliente MCP salió del roadmap. Su §4 dice qué ofrece la base para cada una y qué cambia.
- Decisiones vigentes: DEC-001 (una librería con extras), DEC-002 (módulos comunes, de workflow y de agente; confirmada) y DEC-003 (ciclo modelo ↔ herramientas con entidades previas).
- Quedan 2 `PENDIENTE:` en la Constitución, los dos del feed y con dueño plataforma ([[tech-stack]] §7 y §9).
- Gate de `summa_ocr` en verde el 2026-11-13. Este repo todavía no tiene código ni harness propio.

## Siguiente paso

Commit de la Constitución. Después, crear `develop`, la rama `feature/01-esqueleto-paquete` desde ella y ejecutar `/specs feature 01-esqueleto-paquete`. Los `PENDIENTE` del feed no bloquean la 01, solo la 04.

## Bloqueos

- Crear el repo en Azure DevOps, mover el harness y portar el gate y el revisor a Azure Pipelines. Al moverlo, el harness raíz (`AGENTS.md`, `README.md`, workflows de CI) debe pasar de `main` a `develop` como rama de integración ([[orden_spec]] §10).
- Feed de Azure Artifacts: no existe; lo crea el equipo de plataforma. Bloquea LIB-04.

## Registro de sesiones

- 2026-11-13 — Respuestas de la persona a los `PENDIENTE`: Python 3.12, paquete `summa-ai-framework`, ramas con `develop`, aprobación de plataforma, claves en Key Vault, sin telemetría externa, gate + integración en dev para cerrar, cobertura 80 %, 1.0 al cerrar el roadmap, chunking con `langchain-text-splitters`, MCP fuera, DEC-003 — pendiente de commit.
- 2026-11-13 — Specs afinadas contra el código de la base y de EjOCR: roadmap de 16 a 18 features (almacenamiento en Unity Catalog y contexto de workflow, que el alcance pedía y ninguna feature entregaba), §4 del roadmap con el punto de partida de cada feature, DEC-002 y citas corregidas.
- 2026-11-12 — Validada la decisión de una sola librería y registrada en DEC-001 (extras por consumidor, fronteras de import, humo por extra). Nombres de SUMMA y primera versión `0.1.0`.
- 2026-11-12 — Constitución creada al decidir 3 repos (una librería y dos plantillas). Toma como guía de diseño el framework de referencia, sin copiar código y con el derecho de reutilización confirmado por la persona.
