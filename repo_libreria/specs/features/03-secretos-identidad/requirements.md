# 03 — secretos-identidad — Requirements

> Contrato funcional: qué debe hacer la feature. El revisor valida el diff contra sus criterios de aceptación.

## Comportamiento esperado

1. `KeyVaultSecretProvider(vault_url)` lee los secretos de ese Key Vault con `DefaultAzureCredential`. `get_secret("AZURE_OPENAI_KEY")` pide el secreto `AZURE-OPENAI-KEY`.
2. Cada nombre se pide a Key Vault una sola vez por instancia del proveedor; las siguientes veces sale de su caché.
3. Un secreto inexistente o con valor vacío lanza `SecretNotFoundError` con el nombre de la referencia (con `_`). Cualquier otro error de Azure (credencial, permisos, red o un secreto deshabilitado) lanza `SecretError` con el nombre y el motivo resumido.
4. Con `secrets: {provider: azure_key_vault, vault_url: <https>}`, `load_config` resuelve las referencias con `KeyVaultSecretProvider(vault_url)`.
5. `load_config(path, schema, provider=<proveedor>)` usa ese proveedor en lugar del que declara el YAML.
6. Todo `SecretError` durante la carga se convierte en `ConfigError` con la ubicación de la referencia. Como en LIB-02, nunca muestra un valor secreto ni encadena la excepción original.

## Reglas de negocio

- **Nombres** (decisión de la persona, 2026-11-18): en Key Vault, cada `_` del nombre de la referencia se lee como `-`; las variables de entorno se leen tal cual. El mismo YAML sirve en local y en dev o prod.
- **Credencial**: `DefaultAzureCredential` sin configuración en el YAML. La identidad de cada ambiente la decide plataforma ([[tech-stack]] §6).
- **`vault_url`**: obligatoria con `azure_key_vault`; es una URL `http(s)` validada por pydantic. Con `env` no se usa.
- **API pública nueva**:
  - en `summa_ai_framework.security`, `KeyVaultSecretProvider` y `SecretError`;
  - en `summa_ai_framework.config`, el argumento `provider` de `load_config`.
- **Compatibilidad**: `SecretNotFoundError` sigue siendo `LookupError`, y `EnvSecretProvider` no cambia.

## Casos borde

- Mismo secreto referenciado en varios campos: una sola llamada a Key Vault.
- Sin ninguna credencial disponible (`CredentialUnavailableError`) o sin permiso de lectura (403): `SecretError`, y después `ConfigError` con la ubicación.
- `provider: azure_key_vault` sin `vault_url`: `ConfigError` en `secrets`.
- `vault_url` que no es URL: `ConfigError` en `secrets.vault_url`.
- Proveedor desconocido (`aws_secrets`): `ConfigError` en `secrets.provider`, que nombra los dos válidos.
- YAML con Key Vault y `provider` inyectado: no se construye ningún cliente de Azure.

## Restricciones

- [[decisions]] DEC-001: `azure-identity` y `azure-keyvault-secrets` son obligatorias; las dos plantillas leen Key Vault.
- [[decisions]] DEC-002: `security` no importa de `config`.
- El gate no llama a Azure: los tests usan un cliente doble y la integración real va fuera del gate.
- Se mantienen las reglas de LIB-02 ([[tech-stack]] §8).

## Criterios de aceptación

- [ ] **CA-1**: Dado un `KeyVaultSecretProvider` con un cliente doble que tiene `AZURE-OPENAI-KEY`, cuando se pide `AZURE_OPENAI_KEY` dos veces, entonces:
  - devuelve el valor las dos veces;
  - el cliente recibe una sola llamada, con el nombre `AZURE-OPENAI-KEY`.
- [ ] **CA-2**: Dado un cliente doble que lanza `ResourceNotFoundError` o devuelve un valor vacío, cuando se pide el secreto, entonces lanza `SecretNotFoundError`, que también es `SecretError` y `LookupError`. Si lanza otro error de Azure (`ClientAuthenticationError` o `HttpResponseError`), entonces lanza `SecretError` con el nombre y el tipo del error.
- [ ] **CA-3**: Dado `SecretsConfig`, entonces:
  - `env` sigue siendo el valor por defecto;
  - `azure_key_vault` con `vault_url` es válido;
  - `azure_key_vault` sin `vault_url`, o con un `vault_url` que no es URL, da `ConfigError` en `secrets`;
  - un proveedor desconocido da `ConfigError` en `secrets.provider`.
- [ ] **CA-4**: Dado un YAML con `azure_key_vault` y una referencia, cuando se carga sin inyectar proveedor, entonces `load_config` construye `KeyVaultSecretProvider` con la `vault_url` del YAML y resuelve la referencia con él. Lo verifica un doble que sustituye la clase.
- [ ] **CA-5**: Dado ese mismo YAML, cuando se carga con `provider=EnvSecretProvider()`, entonces la referencia se resuelve desde el entorno y no se construye ningún `KeyVaultSecretProvider`.
- [ ] **CA-6**: Dado un proveedor que lanza `SecretError` (acceso denegado), cuando se carga, entonces se lanza `ConfigError`. El error:
  - incluye la ubicación y el motivo;
  - no contiene ningún valor secreto en todo el traceback formateado;
  - no encadena la excepción original.
- [ ] **CA-7**: Dado el Key Vault de la persona con el secreto `SUMMA-PRUEBA-LIB-03` y `az login` hecho, cuando la persona ejecuta `python repo_libreria/scripts/integracion_keyvault.py`, entonces:
  - lee el secreto a través de `load_config` con la referencia `${SUMMA_PRUEBA_LIB_03}`;
  - una referencia a un secreto inexistente da `ConfigError`;
  - termina con código 0 sin imprimir ningún valor.
- [ ] **CA-8**: Dado el paquete, entonces:
  - `pyproject.toml` declara `azure-identity>=1.15,<2` y `azure-keyvault-secrets>=4.7,<5` como obligatorias;
  - el gate pasa con cobertura de al menos el 80 %;
  - el humo importa `security` y `config` con cada extra;
  - la suite de la librería pasa con las cotas inferiores (`azure-identity==1.15.0`, `azure-keyvault-secrets==4.7.0`, `pydantic==2.7.0` y `PyYAML==6.0.1`).
- [ ] **CA-9**: Dado el cambio de documentación, entonces:
  - [[tech-stack]] §5 añade las dos dependencias;
  - §6 dice que la credencial es `DefaultAzureCredential`;
  - §8 recoge la regla `_` → `-`;
  - "Ejecutar" de `AGENTS.md` incluye el comando de la integración.
