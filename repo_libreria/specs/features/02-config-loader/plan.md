# 02 — config-loader — Plan

> Cómo se construye la feature. No repite los criterios de requirements.md.

## Enfoque

1. `load_config` hace todo en una sola pasada sobre el YAML:
   - lee el archivo y lo parsea con `yaml.safe_load`;
   - comprueba que la raíz es un mapa;
   - valida la sección `secrets` con `SecretsConfig`;
   - recorre el resto de los valores y, donde un texto es `${NOMBRE}` entero, lo cambia por `SecretStr(proveedor.get_secret(NOMBRE))`;
   - guarda la ubicación (`loc`) de cada referencia resuelta;
   - valida el resultado con el esquema que recibe (`SummaConfig` o una subclase).
2. **El secreto viaja como `SecretStr` desde que se resuelve.** Hay dos casos:
   - Un campo `str` normal rechaza un `SecretStr`, porque pydantic no lo convierte. Ese error, en una ubicación resuelta, se traduce a «este campo recibe una referencia y debe ser `SecretRef`».
   - `SecretRef` es `Annotated[SecretStr, BeforeValidator(...)]`: rechaza cualquier entrada que no sea ya un `SecretStr`, es decir, un valor en claro.

   No hace falta recorrer el modelo después de validar.
3. **Errores sin valores.** Todo `ValidationError` se convierte en `ConfigError` con `errors(include_url=False, include_input=False)`, solo `loc` y `msg`, y `raise … from None` para que el error original, que sí lleva la entrada, no viaje en `__cause__` ni en `__context__`. Lo mismo con `SecretNotFoundError`, `OSError` y `yaml.YAMLError`.
4. **`secrets` no se resuelve**: dice cómo resolver el resto. Así se evita la dependencia circular de la base (`vault_url` desde un secreto).
5. **Proveedor**: con `provider: env` (el único `Literal` hasta LIB-03), `EnvSecretProvider`. Sin fábrica: la elección se escribe cuando haya dos opciones (LIB-03).
6. `config` importa de `security`, los dos comunes (DEC-002). `security` no importa de `config`, así que no se repite el ciclo de la base (`security/secrets.py` ↔ `config/schemas`).

## Archivos a crear o modificar

| Archivo | Cambio |
|---|---|
| `repo_libreria/src/summa_ai_framework/security/__init__.py` | Nuevo: `__all__` con `SecretProvider`, `EnvSecretProvider` y `SecretNotFoundError` |
| `repo_libreria/src/summa_ai_framework/security/secrets.py` | Nuevo: interfaz `Protocol`, proveedor de entorno y su error |
| `repo_libreria/src/summa_ai_framework/config/__init__.py` | Nuevo: `__all__` con `ConfigError`, `ConfigModel`, `SecretRef`, `SecretsConfig`, `SummaConfig` y `load_config` |
| `repo_libreria/src/summa_ai_framework/config/models.py` | Nuevo: `ConfigModel`, `SecretRef`, `SecretsConfig` y `SummaConfig` |
| `repo_libreria/src/summa_ai_framework/config/loader.py` | Nuevo: `load_config`, `ConfigError`, resolución y traducción de errores |
| `repo_libreria/tests/test_config.py` | Nuevo: carga, resolución, errores sin valores y extensión por subclase |
| `repo_libreria/tests/test_security.py` | Nuevo: proveedor de entorno |
| `repo_libreria/pyproject.toml` | `dependencies`: `pydantic>=2.7,<3` y `PyYAML>=6.0.1,<7` |
| `requirements-dev.txt` (raíz) | `types-PyYAML` para mypy estricto |
| `repo_libreria/specs/tech-stack.md` | §2 idioma de los nombres; §5 dependencias añadidas, también las de LIB-01 (`pytest-cov` y `setuptools>=69`); §8 reglas de las referencias |
| `repo_libreria/specs/roadmap.md`, `progress.md` | Estado y continuidad |
| `scripts/revisor_ci.py` | `features()` encuentra `specs/features/NN-nombre` en cualquier nivel. Para la rama la busca entre los directorios del árbol del cambio (`git ls-tree -r -d`); sin ellos, sigue suponiendo la raíz |
| `tests/test_revisor_ci.py` | Casos con specs dentro de un proyecto, por archivos tocados y por rama |
| `AGENTS.md` | Ruta de las specs que detecta el revisor y cómo se ejecuta en local |

## Secuencia

1. **Spec**: esta carpeta, con la 02 en `in_progress`. Commit `docs(specs): define la spec de 02-config-loader`.
2. **Proveedor**: `security/` con sus tests, más las dependencias. Commit `feat(security): añade el proveedor de secretos por variables de entorno`.
3. **Loader**: `config/` con sus tests y la reinstalación del `.venv` (`uv pip install -r requirements-dev.txt`), con el gate en verde. Commit `feat(config): carga YAML con referencias a secretos resueltas tras parsear`.
4. **Documentación**: [[tech-stack]] §2, §5 y §8. Commit `docs(specs): fija idioma de la API y reglas de secretos`.
5. **Revisor con otro modelo**: `revisor_ci.py` encuentra las specs de los proyectos. Commit `fix(harness): el revisor de CI encuentra las specs de cada proyecto`.
6. **Cierre**: humo con las dependencias nuevas y `/specs cerrar 02-config-loader`. La última vuelta la ejecuta la persona con `gpt-6-luna`, sobre los commits.

## Dependencias

- Feature 01 (`accepted`).
- [[decisions]] DEC-001: `pydantic` y `PyYAML` son obligatorias porque los dos consumidores cargan configuración. DEC-002: `config` y `security` son comunes.
- Librerías nuevas: `pydantic>=2.7,<3` y `PyYAML>=6.0.1,<7` (ejecución) y `types-PyYAML` (desarrollo). Las cotas inferiores (pydantic 2.7.0 y PyYAML 6.0.1) se comprueban en un entorno aparte con la suite de la librería. PyYAML 6.0 queda fuera porque no tiene wheel para Python 3.12.

## Riesgos

- **Fuga de secretos en errores.** Pydantic incluye la entrada en `str(ValidationError)`. → `include_input=False` y `from None`. Tests que buscan el valor del secreto en `str(error)`, en `repr(modelo)` y en los dumps del modelo.
- **Versión de pydantic del clúster**: Databricks puede traer otra versión instalada. → Rango amplio (`>=2.7,<3`), comprobado en su cota inferior. Si choca, lo resuelve `repo-workflow` al fijar el runtime.
- **El humo necesita red** para instalar pydantic y PyYAML en los entornos limpios. → Ya está fuera del gate (LIB-01).
- **Una plantilla con una sección que transforma la estructura** (validadores propios) podría dejar sin coincidir la `loc` de un error con la de la referencia. → El mensaje genérico de pydantic se mantiene; solo se pierde la pista de `SecretRef`.

## No tocar

- `repo_libreria/scripts/` y los tests de LIB-01: `config` y `security` ya están en el grupo de comunes.
- El harness de la raíz (`scripts/`, `.claude/`, `.github/workflows/`, `tests/`), salvo `scripts/revisor_ci.py`, `tests/test_revisor_ci.py` y la sección "Harness" de `AGENTS.md`. Esos cambian por decisión de la persona (2026-11-18) para que la última vuelta la haga `gpt-6-luna`. El workflow de CI no cambia, y ningún test existente del revisor se modifica ni se debilita.
- `repo_worklow/` y `repo_agente_conversacional/`.
- La Constitución, salvo [[tech-stack]] §2, §5 y §8, el estado en [[roadmap]] y [[progress]].
