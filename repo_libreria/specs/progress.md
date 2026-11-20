# Progreso

> Continuidad entre sesiones. Cada sesión empieza leyendo este archivo y lo actualiza al terminar.
> Lo terminado lo registra git: aquí solo vive el estado actual. El registro guarda las últimas 10 sesiones; borra las más antiguas.

## Estado actual

- El repo vive en GitHub, en `OlmeDK/summa_framework_v0`, temporal hasta Azure DevOps; ahí GitHub no impide el merge aunque `gate` o `revisor` fallen (plan gratuito, repo privado), así que la regla la cumple quien mergea: no se mergea hasta que los dos estén en verde. Los PRs #1 a #9 quedaron en el repo anterior: Constitución (PR #1), LIB-01 (#2), LIB-02 (#3) y LIB-03 (#4), con merge commits. El cierre de la 03 va como commit directo a `main` (decisión de la persona). Mientras el CI solo mire `main`, las features van por PR directo a `main`; `develop` llega con Azure DevOps.
- Paquete `summa-ai-framework`, Python 3.12, cobertura mínima del 80 %; plataforma aprueba las versiones. Extras `workflow` y `agent`. El código vive en `repo_libreria/`, el gate de la raíz lo cubre y `requirements-dev.txt` lo instala editable.
- **LIB-01, LIB-02 y LIB-03 `accepted`** y en `main`. **Fase 1 completa salvo LIB-04**, bloqueada por el feed:
  - `config`: `load_config(path, schema, *, provider=None)`, `SummaConfig`, `ConfigModel`, `SecretRef` y `ConfigError`;
  - `security`: `EnvSecretProvider`, `KeyVaultSecretProvider` (`DefaultAzureCredential`, `_` → `-`), `SecretError` y `SecretNotFoundError`;
  - referencias `${NOMBRE}` resueltas después de parsear; API y claves YAML en inglés.
- Revisión: el revisor de Claude en local busca fallos concretos y el revisor de CI con `gpt-6-luna` da el veredicto final en el PR. Desde LIB-03 funciona de punta a punta en GitHub. El cierre de cada feature va dentro de su PR, antes del merge (`features/03-secretos-identidad/review.md`, "Deuda técnica").
- Roadmap con 17 features (`LIB-01` a `LIB-17`): 01, 02 y 03 `accepted`, 04 bloqueada y las demás en `not_started`. Su §4 dice qué ofrece la base para cada una y qué cambia.
- Decisiones vigentes: DEC-001 (una librería con extras), DEC-002 (módulos comunes, de workflow y de agente; confirmada) y DEC-003 (ciclo modelo ↔ herramientas con entidades previas).
- Quedan 2 `PENDIENTE:` en la Constitución, los dos del feed y con dueño plataforma ([[tech-stack]] §7 y §9).
- En esta máquina, uv necesita `UV_LINK_MODE=copy` para instalar paquetes nuevos de su caché (os error 396).

## Siguiente paso

LIB-06 (`/specs feature 06-contexto-workflow`), en `feature/06-contexto-workflow`. Se adelanta a LIB-05 y su plan incluye el cambio de la comprobación negativa del humo (`replanning/2026-11-20-orden-y-humo.md`). Después, LIB-05.

## Bloqueos

- Crear el repo en Azure DevOps, mover el harness y portar el gate y el revisor a Azure Pipelines. Mientras tanto se trabaja en `OlmeDK/summa_framework_v0`. Al moverlo, el harness raíz (`AGENTS.md`, `README.md`, workflows de CI) debe pasar de `main` a `develop` como rama de integración ([[orden_spec]] §10).
- Feed de Azure Artifacts: no existe; lo crea el equipo de plataforma. Bloquea LIB-04.

## Registro de sesiones

- 2026-11-20 — Replanning: LIB-06 antes de LIB-05, y la comprobación negativa del humo mira las distribuciones instaladas (`replanning/2026-11-20-orden-y-humo.md`). El repo pasa, temporalmente, a `OlmeDK/summa_framework_v0`.
- 2026-11-18 — LIB-03 cerrada: el revisor de CI con `gpt-6-luna` dio `revise` por una contradicción de la spec en «No tocar» (`.env.template`) y `accept` tras corregirla. PR #4 mergeado; cierre en commit directo a `main`. Siguiente: las plantillas.
- 2026-11-18 — PRs #1 a #3 mergeados en `main` (el revisor de CI del #3 falló por arranque: su arreglo viajaba en el propio PR). LIB-03: decisiones de la persona (`_` → `-` en Key Vault, prueba contra su Key Vault `kvema`, veredicto final del revisor de CI), spec, `KeyVaultSecretProvider` y proveedor inyectable, gate, humo y cotas en verde — sin commit; falta la integración.
- 2026-11-18 — LIB-02: decisiones de la persona (API y claves YAML en inglés, referencias solo como valor completo), spec, `config` y `security`, gate en verde, humo y cotas mínimas en verde (PyYAML sube a 6.0.1). Revisor: vuelta 1 `revise` (archivo no UTF-8, formato de ubicación, alias circulares), corregida; vuelta 2 `revise` (fecha imposible y anidamiento profundo en el parser), corregida. La persona elige `gpt-6-luna` para la vuelta 3: `revisor_ci.py` ya encuentra las specs de cada proyecto (CA-10). Vuelta 3 `accept`; 02 `accepted`, CHANGELOG y salida local en `revisor_local.txt`.
- 2026-11-18 — LIB-01: decisiones de la persona (código en `repo_libreria/`, extras `workflow` y `agent`, humo fuera del gate), spec, implementación, gate y humo en verde. Revisor: vuelta 1 `revise` (test de la raíz frágil ante submódulos, índice negativo en imports relativos, `build/` viejo en la wheel), corregida; vuelta 2 `block` por entorno (gate inaccesible para el revisor). La persona commitea hasta `19eb498` y pide arreglar el harness en esta rama: `gate.py` elige el Python del `.venv` (CA-7). Vuelta 3 `accept`; evidencia repetida sobre el código final; 01 `accepted` y CHANGELOG.
- 2026-11-13 — Respuestas de la persona a los `PENDIENTE`: Python 3.12, paquete `summa-ai-framework`, ramas con `develop`, aprobación de plataforma, claves en Key Vault, sin telemetría externa, gate + integración en dev para cerrar, cobertura 80 %, 1.0 al cerrar el roadmap, chunking con `langchain-text-splitters`, MCP fuera, DEC-003 — pendiente de commit.
- 2026-11-13 — Specs afinadas contra el código de la base y de EjOCR: roadmap de 16 a 18 features (almacenamiento en Unity Catalog y contexto de workflow, que el alcance pedía y ninguna feature entregaba), §4 del roadmap con el punto de partida de cada feature, DEC-002 y citas corregidas.
- 2026-11-12 — Validada la decisión de una sola librería y registrada en DEC-001 (extras por consumidor, fronteras de import, humo por extra). Nombres de SUMMA y primera versión `0.1.0`.
- 2026-11-12 — Constitución creada al decidir 3 repos (una librería y dos plantillas). Toma como guía de diseño el framework de referencia, sin copiar código y con el derecho de reutilización confirmado por la persona.
