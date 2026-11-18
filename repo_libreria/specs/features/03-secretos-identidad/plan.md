# 03 — secretos-identidad — Plan

> Cómo se construye la feature. No repite los criterios de requirements.md.

## Enfoque

1. **`KeyVaultSecretProvider(vault_url, client=None)`** cumple la interfaz `SecretProvider` de LIB-02.
   - Sin `client`, crea un `SecretClient(vault_url, DefaultAzureCredential())`. Ninguno de los dos llama a la red al construirse: la credencial se resuelve en la primera lectura.
   - Con `client`, los tests usan un doble que cumple un `Protocol` mínimo (`get_secret(name)` que devuelve algo con `.value`). Así no hay que simular Azure ni construir sus tipos.
2. **`get_secret(name)`**:
   - pide `name.replace("_", "-")` y guarda el valor en una caché del proveedor, que dura lo que dura una carga;
   - convierte `ResourceNotFoundError` o un valor vacío en `SecretNotFoundError(name)`;
   - convierte cualquier otro `AzureError` (credencial, permisos, red) en `SecretError` con el nombre y el tipo y el mensaje del error de Azure. Ese mensaje no puede contener el valor, porque no se llegó a leer.
3. **Errores**: `SecretError(Exception)` es la base y `SecretNotFoundError(SecretError, LookupError)`; se conserva `LookupError` por compatibilidad con LIB-02. El loader captura `SecretError` y lo convierte en `ConfigError` con la ubicación y `from None`.
4. **`SecretsConfig`**:
   - `provider: Literal["env", "azure_key_vault"]`;
   - `vault_url: HttpUrl | None`;
   - un validador exige `vault_url` cuando el proveedor es Key Vault.
5. **`load_config(path, schema, *, provider=None)`**: si recibe `provider`, lo usa en lugar del que declara el YAML; si no, lo elige `_proveedor(SecretsConfig)`. Así la plantilla prueba su `config_dev.yaml` real sin Azure.
6. **Integración**: `repo_libreria/scripts/integracion_keyvault.py` lee `SUMMA_PRUEBA_KEYVAULT_URL`, escribe un YAML temporal con `${SUMMA_PRUEBA_LIB_03}` y lo carga con la credencial real.
   - Comprueba que se lee el secreto y que uno inexistente da `ConfigError`.
   - Nunca imprime el valor, solo su longitud.
   - Lo ejecuta la persona con `az login`, porque necesita su identidad y su `.env`.

## Archivos a crear o modificar

| Archivo | Cambio |
|---|---|
| `repo_libreria/src/summa_ai_framework/security/secrets.py` | `SecretError`, `SecretNotFoundError(SecretError, LookupError)` y `KeyVaultSecretProvider` |
| `repo_libreria/src/summa_ai_framework/security/__init__.py` | `__all__` con `KeyVaultSecretProvider` y `SecretError` |
| `repo_libreria/src/summa_ai_framework/config/models.py` | `SecretsConfig.provider` con `azure_key_vault`, `vault_url` y su validador |
| `repo_libreria/src/summa_ai_framework/config/loader.py` | `_proveedor()`, argumento `provider` y `SecretError` → `ConfigError` |
| `repo_libreria/tests/test_security.py` | Proveedor de Key Vault con un cliente doble |
| `repo_libreria/tests/test_config.py` | YAML con Key Vault, proveedor inyectado y errores de acceso. El caso `proveedor-no-soportado` cambia de `azure_key_vault` a otro proveedor, porque `azure_key_vault` ya es válido |
| `repo_libreria/scripts/integracion_keyvault.py` | Nuevo: prueba contra Key Vault real, fuera del gate |
| `repo_libreria/pyproject.toml` | `azure-identity>=1.15,<2` y `azure-keyvault-secrets>=4.7,<5` |
| `AGENTS.md` | "Ejecutar": comando de la prueba de integración |
| `.env.template` | Lo cambia la persona, no un agente: una línea `SUMMA_PRUEBA_KEYVAULT_URL=` sin valor (`AGENTS.md`, "Variables de entorno") |
| `repo_libreria/specs/tech-stack.md` | §5 dependencias; §6 credencial; §8 nombres en Key Vault |
| `repo_libreria/specs/roadmap.md`, `progress.md` | Estado y continuidad |

## Secuencia

1. **Spec**, con la 03 en `in_progress`. Commit `docs(specs): define la spec de 03-secretos-identidad`.
2. **Proveedor**: `security/` con sus tests y las dependencias. Commit `feat(security): añade el proveedor de secretos de Key Vault`.
3. **Loader**: `config/` con sus tests. Commit `feat(config): elige el proveedor de secretos desde el YAML o por inyección`.
4. **Integración y documentación**: el script, [[tech-stack]] y `AGENTS.md`. Commit `docs: prueba de integración con Key Vault y reglas de nombres`.
5. **Cierre**:
   - la persona ejecuta la integración;
   - revisor de Claude en local;
   - PR a `main`, donde el revisor de CI (`gpt-6-luna`) da el veredicto final;
   - `/specs cerrar 03-secretos-identidad`.

## Dependencias

- LIB-02 (`accepted`): `SecretProvider`, `load_config` y `SecretsConfig`.
- [[decisions]] DEC-001: `azure-identity` y `azure-keyvault-secrets` son obligatorias, porque los dos consumidores leen Key Vault ([[tech-stack]] §5). DEC-002: `security` sigue sin importar de `config`.
- Las cotas inferiores (`azure-identity==1.15.0`, `azure-keyvault-secrets==4.7.0`) se prueban con la suite, como en LIB-02.
- Key Vault `kvema` de la persona, con el secreto `SUMMA-PRUEBA-LIB-03`. La URL va en su `.env` como `SUMMA_PRUEBA_KEYVAULT_URL`, y en `.env.template` sin valor, que añade la persona.

## Riesgos

- **`DefaultAzureCredential` prueba varias credenciales y puede tardar o fallar con un mensaje largo** si no hay ninguna. → El error se resume en `SecretError` (tipo y primera línea), sin traza encadenada.
- **El revisor de CI evalúa sobre `main`.** El arreglo de las specs anidadas ya está en `main` (`279688c`), así que esta es la primera feature que revisa de punta a punta en GitHub.
- **Mensajes de Azure en el error**: pueden incluir el nombre del vault o del secreto, pero nunca el valor. → Se acepta, porque ayuda a diagnosticar permisos.
- **El humo y las cotas inferiores necesitan red** para instalar los paquetes de Azure. → Fuera del gate, como en LIB-01 y LIB-02.

## No tocar

- La interfaz `SecretProvider` y `EnvSecretProvider` (LIB-02).
- Las reglas de las referencias de [[tech-stack]] §8 (valor completo, `SecretRef`, `secrets` sin resolver).
- El harness de la raíz (`scripts/`, `.claude/`, `.github/workflows/`, `tests/`). `AGENTS.md` solo cambia en "Ejecutar".
- `repo_worklow/` y `repo_agente_conversacional/`.
- `.env` (no se versiona). De `.env.template` solo cambia la línea `SUMMA_PRUEBA_KEYVAULT_URL=` sin valor, que añade la persona porque los agentes no pueden editarlo (`AGENTS.md`, "Variables de entorno"). No puede llevar ningún valor.
- La Constitución, salvo [[tech-stack]] §5, §6 y §8, el estado en [[roadmap]] y [[progress]].
