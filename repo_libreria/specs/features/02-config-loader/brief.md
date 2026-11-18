# 02 — config-loader — Brief

> Ficha ejecutiva: qué problema resuelve la feature y por qué ahora. Sin diseño técnico ni tareas.

## Problema

Las dos plantillas leen un `config/config_<ambiente>.yaml` con los secretos referenciados por nombre: el `tech-stack` de `repo-workflow` en su §8 y el de `repo-agente-conversacional` en su §8. Hoy la librería no sabe cargarlo. Sin un loader común, cada plantilla y cada caso de uso clonado escribiría el suyo, con tres riesgos:

- resolver los secretos sobre el texto antes de parsear el YAML, como hace la base (`BaseRef/core/config/loader.py:21-36`, `134`), de modo que un secreto con `:` o `#` altera la estructura;
- guardar las claves como `str`, que se imprimen en logs;
- dejar que pydantic muestre el valor del secreto al fallar una validación. Comprobado con pydantic 2.14: `str(ValidationError)` incluye la entrada.

## Por qué ahora

Es la siguiente del [[roadmap]] y su única dependencia, la 01, está `accepted`. Todo servicio de las features 03 a 17 recibe su configuración por aquí. Es también lo primero que una plantilla puede importar y probar en local.

## Decisión de diseño

- Decisiones de la persona del 2026-11-18:
  - nombres de la API pública y claves del YAML en inglés; docstrings y mensajes de error en español;
  - una referencia `${NOMBRE}` ocupa siempre el valor completo; si aparece dentro de un texto, es un error.
- El loader resuelve las referencias **después** de parsear el YAML y entrega cada valor resuelto como `SecretStr`.
- Los esquemas declaran sus credenciales con el tipo `SecretRef`, que solo acepta un valor venido de una referencia. Así nunca hay credenciales en claro en el YAML versionado ([[mission]], principio 5), y un secreto solo puede caer en un campo que lo enmascara.
- La última vuelta de revisión la hace el evaluador `gpt-6-luna` (`scripts/revisor_ci.py`) en local, para que quien evalúa sea un modelo distinto del que implementa. Hasta ahora ese script solo encontraba specs en la raíz; se arregla en esta rama para que encuentre las de `<proyecto>/specs/features/` (decisión de la persona, 2026-11-18).
- Esquema raíz `SummaConfig` en la librería, como la base (`BaseRef/core/config/schemas/solution.py`). Hoy solo tiene `secrets`; cada feature añade su sección y cada plantilla lo extiende con una subclase para sus secciones propias.

## Incluye

- Módulo `summa_ai_framework.config`:
  - `ConfigModel`, la base de los esquemas, que rechaza claves desconocidas;
  - `SecretsConfig`, `SummaConfig` y el tipo `SecretRef`;
  - `load_config(path, schema)` y `ConfigError`.
- Módulo `summa_ai_framework.security`: interfaz `SecretProvider`, `EnvSecretProvider` (variables de entorno) y `SecretNotFoundError`.
- Dependencias obligatorias `pydantic` y `PyYAML`; `types-PyYAML` en desarrollo.
- [[tech-stack]] §2 (idioma de los nombres), §5 (dependencias añadidas) y §8 (reglas de las referencias).
- Harness: `scripts/revisor_ci.py` encuentra las specs de cualquier proyecto del repo, y `AGENTS.md` explica cómo ejecutarlo en local.

## No incluye

- Proveedor de Key Vault e identidad de Azure: LIB-03. Hasta entonces, `secrets.provider` solo acepta `env`.
- Cómo se nombran los secretos en Key Vault (la base cambia `_` por `-`, `secrets.py:85`): LIB-03.
- Secciones de servicios (`llms`, `embeddings`, índice…): las añade la feature de cada servicio.
- Ajustes globales (iniciativa, ambiente, nivel de log): los añade la feature que los use (LIB-05, LIB-07).
- Leer archivos `.env`: es cosa de cada plantilla. La librería solo lee las variables ya presentes en el entorno.
- La validación contra un registro de soluciones en Cosmos de la base (`loader.py:39-106`).

## Resultado esperado

Una plantilla define `class WorkflowConfig(SummaConfig)` con sus secciones, exporta `AZURE_OPENAI_KEY` en su entorno local y llama a `load_config("config/config_dev.yaml", WorkflowConfig)`. Obtiene la configuración validada, con la clave como `SecretStr`. Si falta un secreto, sobra una clave o una credencial va en claro, recibe un `ConfigError` que dice dónde está el problema sin mostrar ningún valor secreto.
