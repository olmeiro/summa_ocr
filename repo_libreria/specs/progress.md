# Progreso

> Continuidad entre sesiones. Cada sesión empieza leyendo este archivo y lo actualiza al terminar.
> Lo terminado lo registra git: aquí solo vive el estado actual. El registro guarda las últimas 10 sesiones; borra las más antiguas.

## Estado actual

- Constitución commiteada en `init/constitucion` (`a337366`), sin mergear a `main`. `develop` y `feature/01-esqueleto-paquete` creadas en local desde ella el 2026-11-18.
- Paquete `summa-ai-framework`, Python 3.12, cobertura mínima del 80 %, ramas `feature/NN-nombre` → `develop` → `main`; plataforma aprueba las versiones. Extras `workflow` y `agent`.
- **LIB-01 `accepted`** (revisor, vuelta 3). El código vive en `repo_libreria/` (`pyproject.toml`, `src/`, `tests/`, `scripts/`), el gate de la raíz lo cubre y `requirements-dev.txt` lo instala editable. Las plantillas pueden instalarla con `uv pip install -e <ruta>/repo_libreria[workflow]` o `[agent]`.
- Commiteado hasta `19eb498`. Quedan sin commit el arreglo del gate (CA-7) y el cierre (review, roadmap, CHANGELOG y progress).
- Roadmap con 17 features (`LIB-01` a `LIB-17`); 01 `accepted` y las demás en `not_started`. Su §4 dice qué ofrece la base para cada una y qué cambia.
- Decisiones vigentes: DEC-001 (una librería con extras), DEC-002 (módulos comunes, de workflow y de agente; confirmada) y DEC-003 (ciclo modelo ↔ herramientas con entidades previas).
- Quedan 2 `PENDIENTE:` en la Constitución, los dos del feed y con dueño plataforma ([[tech-stack]] §7 y §9).
- Gate de `summa_ocr` en verde el 2026-11-18 (84 tests, 100 % de cobertura de la librería) y humo por extra en verde.

## Siguiente paso

1. Dos commits: `fix(harness): …` (`scripts/gate.py`, `.claude/hooks/gate_al_parar.py`, `tests/test_harness.py` y la spec enmendada) y `docs(specs): …` (cierre).
2. Mergear `init/constitucion` en `main` y después `feature/01-esqueleto-paquete` en `develop`.
3. `feature/02-config-loader` desde `develop` y `/specs feature 02-config-loader`.

Antes de LIB-05, replanning de la comprobación negativa del humo (`features/01-esqueleto-paquete/review.md`, "Deuda técnica").

## Bloqueos

- Crear el repo en Azure DevOps, mover el harness y portar el gate y el revisor a Azure Pipelines. Al moverlo, el harness raíz (`AGENTS.md`, `README.md`, workflows de CI) debe pasar de `main` a `develop` como rama de integración ([[orden_spec]] §10).
- Feed de Azure Artifacts: no existe; lo crea el equipo de plataforma. Bloquea LIB-04.

## Registro de sesiones

- 2026-11-18 — LIB-01: decisiones de la persona (código en `repo_libreria/`, extras `workflow` y `agent`, humo fuera del gate), spec, implementación, gate y humo en verde. Revisor: vuelta 1 `revise` (test de la raíz frágil ante submódulos, índice negativo en imports relativos, `build/` viejo en la wheel), corregida; vuelta 2 `block` por entorno (gate inaccesible para el revisor). La persona commitea hasta `19eb498` y pide arreglar el harness en esta rama: `gate.py` elige el Python del `.venv` (CA-7). Vuelta 3 `accept`; evidencia repetida sobre el código final; 01 `accepted` y CHANGELOG.
- 2026-11-13 — Respuestas de la persona a los `PENDIENTE`: Python 3.12, paquete `summa-ai-framework`, ramas con `develop`, aprobación de plataforma, claves en Key Vault, sin telemetría externa, gate + integración en dev para cerrar, cobertura 80 %, 1.0 al cerrar el roadmap, chunking con `langchain-text-splitters`, MCP fuera, DEC-003 — pendiente de commit.
- 2026-11-13 — Specs afinadas contra el código de la base y de EjOCR: roadmap de 16 a 18 features (almacenamiento en Unity Catalog y contexto de workflow, que el alcance pedía y ninguna feature entregaba), §4 del roadmap con el punto de partida de cada feature, DEC-002 y citas corregidas.
- 2026-11-12 — Validada la decisión de una sola librería y registrada en DEC-001 (extras por consumidor, fronteras de import, humo por extra). Nombres de SUMMA y primera versión `0.1.0`.
- 2026-11-12 — Constitución creada al decidir 3 repos (una librería y dos plantillas). Toma como guía de diseño el framework de referencia, sin copiar código y con el derecho de reutilización confirmado por la persona.
