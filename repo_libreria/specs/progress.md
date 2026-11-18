# Progreso

> Continuidad entre sesiones. Cada sesión empieza leyendo este archivo y lo actualiza al terminar.
> Lo terminado lo registra git: aquí solo vive el estado actual. El registro guarda las últimas 10 sesiones; borra las más antiguas.

## Estado actual

- En GitHub (`origin/main`): Constitución (PR #1), LIB-01 (#2) y LIB-02 (#3), con merge commits. Mientras el CI solo mire `main`, las features van por PR directo a `main`; `develop` llega con Azure DevOps.
- Paquete `summa-ai-framework`, Python 3.12, cobertura mínima del 80 %; plataforma aprueba las versiones. Extras `workflow` y `agent`. El código vive en `repo_libreria/`, el gate de la raíz lo cubre y `requirements-dev.txt` lo instala editable.
- **LIB-01 y LIB-02 `accepted`** y en `main`:
  - `config`: `load_config`, `SummaConfig`, `ConfigModel`, `SecretRef` y `ConfigError`;
  - `security`: `EnvSecretProvider`;
  - referencias `${NOMBRE}` resueltas después de parsear; API y claves YAML en inglés.

  El revisor de CI (`gpt-6-luna`) ya encuentra las specs de cada proyecto.
- **LIB-03 `passing`**, sin commit, en `feature/03-secretos-identidad` (desde `279688c`):
  - `KeyVaultSecretProvider` (`DefaultAzureCredential`, `_` → `-` y caché), `SecretError`, `secrets.provider: azure_key_vault` con `vault_url` y `load_config(..., provider=...)`;
  - gate (124 tests, 100 %), humo y cotas mínimas en verde.

  Integración contra `kvema` en verde (CA-7). Falta la revisión.
- Roadmap con 17 features (`LIB-01` a `LIB-17`): 01 y 02 `accepted`, 03 `passing` y las demás en `not_started`. Su §4 dice qué ofrece la base para cada una y qué cambia.
- Decisiones vigentes: DEC-001 (una librería con extras), DEC-002 (módulos comunes, de workflow y de agente; confirmada) y DEC-003 (ciclo modelo ↔ herramientas con entidades previas).
- Quedan 2 `PENDIENTE:` en la Constitución, los dos del feed y con dueño plataforma ([[tech-stack]] §7 y §9).
- En esta máquina, uv necesita `UV_LINK_MODE=copy` para instalar paquetes nuevos de su caché (os error 396).

## Siguiente paso

1. La persona añade `SUMMA_PRUEBA_KEYVAULT_URL=` a `.env.template`.
2. Revisor de Claude en local; commits (spec, `security`, `config`, documentación y evidencia).
3. PR a `main`: el revisor de CI con `gpt-6-luna` da el veredicto final. Primera feature revisada de punta a punta en GitHub.

Antes de LIB-05, replanning de la comprobación negativa del humo (`features/01-esqueleto-paquete/review.md`, "Deuda técnica").

## Bloqueos

- Crear el repo en Azure DevOps, mover el harness y portar el gate y el revisor a Azure Pipelines. Al moverlo, el harness raíz (`AGENTS.md`, `README.md`, workflows de CI) debe pasar de `main` a `develop` como rama de integración ([[orden_spec]] §10).
- Feed de Azure Artifacts: no existe; lo crea el equipo de plataforma. Bloquea LIB-04.

## Registro de sesiones

- 2026-11-18 — PRs #1 a #3 mergeados en `main` (el revisor de CI del #3 falló por arranque: su arreglo viajaba en el propio PR). LIB-03: decisiones de la persona (`_` → `-` en Key Vault, prueba contra su Key Vault `kvema`, veredicto final del revisor de CI), spec, `KeyVaultSecretProvider` y proveedor inyectable, gate, humo y cotas en verde — sin commit; falta la integración.
- 2026-11-18 — LIB-02: decisiones de la persona (API y claves YAML en inglés, referencias solo como valor completo), spec, `config` y `security`, gate en verde, humo y cotas mínimas en verde (PyYAML sube a 6.0.1). Revisor: vuelta 1 `revise` (archivo no UTF-8, formato de ubicación, alias circulares), corregida; vuelta 2 `revise` (fecha imposible y anidamiento profundo en el parser), corregida. La persona elige `gpt-6-luna` para la vuelta 3: `revisor_ci.py` ya encuentra las specs de cada proyecto (CA-10). Vuelta 3 `accept`; 02 `accepted`, CHANGELOG y salida local en `revisor_local.txt`.
- 2026-11-18 — LIB-01: decisiones de la persona (código en `repo_libreria/`, extras `workflow` y `agent`, humo fuera del gate), spec, implementación, gate y humo en verde. Revisor: vuelta 1 `revise` (test de la raíz frágil ante submódulos, índice negativo en imports relativos, `build/` viejo en la wheel), corregida; vuelta 2 `block` por entorno (gate inaccesible para el revisor). La persona commitea hasta `19eb498` y pide arreglar el harness en esta rama: `gate.py` elige el Python del `.venv` (CA-7). Vuelta 3 `accept`; evidencia repetida sobre el código final; 01 `accepted` y CHANGELOG.
- 2026-11-13 — Respuestas de la persona a los `PENDIENTE`: Python 3.12, paquete `summa-ai-framework`, ramas con `develop`, aprobación de plataforma, claves en Key Vault, sin telemetría externa, gate + integración en dev para cerrar, cobertura 80 %, 1.0 al cerrar el roadmap, chunking con `langchain-text-splitters`, MCP fuera, DEC-003 — pendiente de commit.
- 2026-11-13 — Specs afinadas contra el código de la base y de EjOCR: roadmap de 16 a 18 features (almacenamiento en Unity Catalog y contexto de workflow, que el alcance pedía y ninguna feature entregaba), §4 del roadmap con el punto de partida de cada feature, DEC-002 y citas corregidas.
- 2026-11-12 — Validada la decisión de una sola librería y registrada en DEC-001 (extras por consumidor, fronteras de import, humo por extra). Nombres de SUMMA y primera versión `0.1.0`.
- 2026-11-12 — Constitución creada al decidir 3 repos (una librería y dos plantillas). Toma como guía de diseño el framework de referencia, sin copiar código y con el derecho de reutilización confirmado por la persona.
