# 03 — secretos-identidad — Validation

> Cómo se comprueba cada criterio de aceptación y qué evidencia se guarda. Se escribe antes de programar.

## Verificación por criterio

| CA | Cómo se verifica | Tipo | Evidencia |
|---|---|---|---|
| CA-1 | `repo_libreria/tests/test_security.py`: cliente doble que cuenta las llamadas y registra los nombres | automática, en el gate | Salida de `python -m pytest repo_libreria/tests --no-cov -v` |
| CA-2 | `test_security.py`, un caso por error: `ResourceNotFoundError`, valor vacío, `ClientAuthenticationError` y `HttpResponseError` | automática, en el gate | Ídem |
| CA-3 | `repo_libreria/tests/test_config.py`: casos en `test_archivos_invalidos` y una carga válida con Key Vault | automática, en el gate | Ídem |
| CA-4 | `test_config.py`: `monkeypatch` sustituye `KeyVaultSecretProvider` en el loader por un doble que guarda la `vault_url` | automática, en el gate | Ídem |
| CA-5 | `test_config.py`: YAML con Key Vault, `provider=EnvSecretProvider()` y un doble que falla si se construye | automática, en el gate | Ídem |
| CA-6 | `test_config.py`: proveedor doble que lanza `SecretError`. Comprueba la ubicación, el motivo, que el valor no está en el traceback formateado y que no hay excepción encadenada | automática, en el gate | Ídem |
| CA-7 | La persona ejecuta `python repo_libreria/scripts/integracion_keyvault.py` con `az login` y `SUMMA_PRUEBA_KEYVAULT_URL` cargada desde su `.env` | manual, fuera del gate | Salida completa que pega la persona, con el código de salida |
| CA-8 | `python scripts/gate.py`, `python repo_libreria/scripts/humo_extras.py` y la suite en un `uv venv` aparte con las cotas inferiores, como en LIB-02 | automática + comando | Salidas del gate, del humo y de la suite con cotas |
| CA-9 | Lectura del diff de `repo_libreria/specs/tech-stack.md` y de `AGENTS.md` | revisión | Diff |

## Validación técnica

- [ ] `python scripts/gate.py` en verde, con cobertura ≥ 80 %.
- [ ] `python repo_libreria/scripts/humo_extras.py` en verde.
- [ ] Prueba de integración contra Key Vault en verde (CA-7, [[tech-stack]] §11).
- [ ] `git status` sin archivos de build ni `.env*` versionados.

## Evidencia requerida para cerrar

En `review.md`, con el commit en que se obtuvo cada una:

- el gate;
- los tests de la librería;
- el humo;
- la suite con las cotas inferiores;
- la integración que pega la persona.

**Veredicto final**: el revisor de CI (`gpt-6-luna`) en el PR a `main`, con su salida copiada de GitHub Actions. Antes, una vuelta con el revisor de Claude en local.
