# 03 — secretos-identidad — Brief

> Ficha ejecutiva: qué problema resuelve la feature y por qué ahora. Sin diseño técnico ni tareas.

## Problema

Desde LIB-02, `load_config` resuelve las referencias `${NOMBRE}` solo desde variables de entorno. Eso sirve en local, pero no en dev ni en prod. Ahí las claves de Azure OpenAI, AI Search, Content Understanding y Cosmos DB viven en Key Vault ([[tech-stack]] §6), y las dos plantillas las referencian desde su `config_<ambiente>.yaml`: el §8 del `tech-stack` de cada plantilla. Sin un proveedor de Key Vault, ninguna plantilla puede ejecutarse fuera de un portátil.

## Por qué ahora

Es la siguiente del [[roadmap]] y su dependencia, la 02, está `accepted`. La fase 1 termina cuando el paquete carga un YAML con un secreto de Key Vault ([[roadmap]] §2), y las features `configuracion` de las dos plantillas (03 del workflow y 02 del agente) dependen de esta.

## Decisión de diseño

- Credencial: `DefaultAzureCredential`, como la base (`BaseRef/core/security/secrets.py:46-79`). Usa la identidad que haya en cada sitio:
  - `az login` en local;
  - identidad administrada en Container Apps;
  - service principal por variables de entorno en Databricks.

  Así la librería no depende de los `PENDIENTE` de plataforma sobre qué identidad usa cada ambiente.
- Nombres: el YAML usa `${AZURE_OPENAI_KEY}`. En local se lee la variable `AZURE_OPENAI_KEY` y en Key Vault el secreto `AZURE-OPENAI-KEY`: `_` se lee como `-`, como en la base (`secrets.py:85`). El mismo YAML sirve con los dos proveedores (decisión de la persona, 2026-11-18).
- `load_config` acepta un proveedor inyectado que sustituye al del YAML. Así una plantilla prueba su `config_dev.yaml` real, que declara Key Vault, sin Azure ([[tech-stack]] §11, "Dobles").
- Revisión: primero el revisor de Claude en local y después, como veredicto final, el revisor de CI con `gpt-6-luna` en el PR de GitHub (decisión de la persona, 2026-11-18).

## Incluye

- `summa_ai_framework.security`:
  - `KeyVaultSecretProvider`, con caché por carga y `_` → `-`;
  - `SecretError`, base de los errores de secretos (`SecretNotFoundError` pasa a heredar de ella).
- `summa_ai_framework.config`:
  - `SecretsConfig` acepta `provider: azure_key_vault` con `vault_url`;
  - `load_config(..., provider=...)`;
  - un fallo de acceso a Key Vault es `ConfigError`.
- Dependencias obligatorias `azure-identity` y `azure-keyvault-secrets`.
- Script de integración `repo_libreria/scripts/integracion_keyvault.py`, fuera del gate, que la persona ejecuta contra su Key Vault.
- [[tech-stack]] §5 (dependencias), §6 (credencial) y §8 (nombres en Key Vault).

## No incluye

- Secret scopes de Databricks (`dbutils.secrets`). Si `repo-workflow` no puede usar `DefaultAzureCredential` en el clúster, entra por replanning.
- Elegir la identidad de cada ambiente: es de plataforma.
- Rotación o recarga de secretos en caliente: se leen al cargar la configuración.
- Escribir secretos en Key Vault.

## Resultado esperado

- Con `secrets: {provider: azure_key_vault, vault_url: https://<vault>.vault.azure.net/}` en el YAML y `az login` hecho, `load_config` devuelve la configuración con los secretos leídos de Key Vault.
- Sin permiso, sin red o sin el secreto, lanza `ConfigError` con la ubicación y el motivo, sin ningún valor secreto.
- Una plantilla prueba ese mismo YAML sin Azure con `load_config(ruta, Esquema, provider=EnvSecretProvider())`.
