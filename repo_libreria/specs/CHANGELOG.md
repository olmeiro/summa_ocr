# CHANGELOG

## 2026-11-18 — 03-secretos-identidad

### Added
- `KeyVaultSecretProvider` en `summa_ai_framework.security`. Lee secretos de Azure Key Vault con `DefaultAzureCredential`: `az login` en local, identidad administrada o service principal en cada ambiente. Pide cada secreto una sola vez por carga.
- `SecretError`, base de los errores de secretos; `SecretNotFoundError` hereda de ella y sigue siendo `LookupError`.
- `secrets.provider: azure_key_vault` con `vault_url` en el YAML, y `load_config(..., provider=...)` para que una plantilla pruebe su YAML de Key Vault sin Azure.
- Dependencias obligatorias `azure-identity>=1.15,<2` y `azure-keyvault-secrets>=4.7,<5`, con las cotas inferiores probadas.
- `repo_libreria/scripts/integracion_keyvault.py`: prueba contra un Key Vault real, fuera del gate.

### Changed
- En Key Vault, cada `_` de una referencia se lee como `-`: `${AZURE_OPENAI_KEY}` es el secreto `AZURE-OPENAI-KEY`. El mismo YAML sirve en local y en dev o prod ([[tech-stack]] §8).
- Un fallo de acceso a Key Vault (credencial, permisos, red o dominio) es `ConfigError` con la ubicación, sin valores.

### Notes
- Integración probada contra el Key Vault de la persona (`kv en azure`), porque el de dev de SUMMA aún no existe.
- Primera feature que el revisor de CI (`gpt-6-luna`) evalúa en GitHub de punta a punta. Su primera vuelta encontró una contradicción en «No tocar» de la spec.

## 2026-11-18 — 02-config-loader

### Added
- `summa_ai_framework.config`: `load_config(path, schema)` carga el YAML de la plantilla y resuelve las referencias `${NOMBRE}` después de parsear. También trae `SummaConfig` (raíz que extiende cada plantilla), `ConfigModel` (rechaza claves desconocidas), `SecretRef` y `ConfigError`.
- `summa_ai_framework.security`: interfaz `SecretProvider` y `EnvSecretProvider` (variables de entorno). Key Vault llega en LIB-03.
- Dependencias obligatorias `pydantic>=2.7,<3` y `PyYAML>=6.0.1,<7`, con las cotas inferiores probadas.

### Changed
- API pública y claves del YAML en inglés; mensajes y docstrings en español ([[tech-stack]] §2).
- Las credenciales se declaran `SecretRef`: una clave en claro en el YAML, o una referencia en un campo `str`, es un error. Los errores nunca muestran valores secretos ([[tech-stack]] §8).
- Harness: `scripts/revisor_ci.py` encuentra las specs de cada proyecto (`<proyecto>/specs/features/`) y se puede ejecutar en local con `gpt-6-luna`.

### Notes
- Primera feature evaluada por un modelo distinto del que la implementó: vuelta 3 con `gpt-6-luna`, `accept`.

## 2026-11-18 — 01-esqueleto-paquete

### Added
- Paquete `summa-ai-framework` `0.1.0` en `repo_libreria/`: Python ≥3.12, sin dependencias de ejecución, extras `workflow` y `agent` (vacíos por ahora) y `py.typed`.
- Test de fronteras de import de DEC-002 en el gate. Un módulo de primer nivel nuevo debe asignarse a un grupo en `repo_libreria/scripts/fronteras.py`.
- Humo por extra fuera del gate (`python repo_libreria/scripts/humo_extras.py`, necesita uv y red): construye la wheel y la instala con solo un extra en un entorno limpio.
- Cobertura mínima del 80 % sobre `summa_ai_framework` en el gate de la raíz. La librería se instala en modo editable con `requirements-dev.txt`.

### Changed
- Las plantillas instalan la librería con `uv pip install -e <ruta>/repo_libreria[workflow]` o `[agent]` mientras no exista el feed (LIB-04).
- [[tech-stack]] §4 define la API pública: el `__all__` de cada módulo de primer nivel, el nombre de la distribución y sus extras.
- Harness: `scripts/gate.py` usa el Python del `.venv` de la raíz aunque no esté activado. El hook Stop delega en él.

### Notes
- Replanning pendiente antes de LIB-05: la comprobación negativa del humo de DEC-002 fallará con módulos de workflow o de agente que solo usen dependencias comunes ([[01-esqueleto-paquete/review]], "Deuda técnica").
