# 03 — secretos-identidad — Review

> Evidencia real de la validación de la feature, rama `feature/03-secretos-identidad`, creada desde `279688c` (merge de LIB-02 en `main`).
> Toda la evidencia es de **`279688c` más los cambios de la feature sin commit**, el 2026-11-18. Los commits los hace la persona; la spec va primero, como pide `plan.md` §Secuencia.

## Gate

`python scripts/gate.py`:

```text
[GATE] PASS: Lint
[GATE] PASS: Formato
[GATE] PASS: Tipos
Required test coverage of 80% reached. Total coverage: 100.00%
127 passed in 9.93s
[GATE] PASS: Tests
[GATE] Todas las comprobaciones pasaron.
```

## Cumplimiento por criterio

| CA | Estado | Evidencia |
|---|---|---|
| CA-1 | cumple | `test_key_vault_traduce_el_nombre_y_cachea`: una sola llamada al cliente, con `AZURE-OPENAI-KEY` |
| CA-2 | cumple | `test_key_vault_inexistente_o_vacio` (sin secreto, `""` y `None`) y `test_key_vault_otros_errores_son_secret_error[sin-credencial, sin-permiso]` |
| CA-3 | cumple | `test_archivos_invalidos[proveedor-no-soportado, key-vault-sin-url, key-vault-url-invalida]`, `test_un_archivo_vacio_da_los_valores_por_defecto` (`env` por defecto) y la carga válida de CA-4 |
| CA-4 | cumple | `test_con_key_vault_usa_la_vault_url_del_yaml` y `test_sin_cliente_usa_secret_client_del_vault` |
| CA-5 | cumple | `test_el_proveedor_inyectado_sustituye_al_del_yaml`: el doble de Key Vault falla si se construye |
| CA-6 | cumple | `test_un_fallo_de_acceso_es_config_error_sin_valores` |
| CA-7 | cumple | Abajo: integración contra el Key Vault `kvema`, ejecutada por la persona |
| CA-8 | cumple | `pyproject.toml`, el gate de arriba (fronteras incluidas), el humo y la suite con las cotas inferiores, abajo |
| CA-9 | cumple | Diff de `repo_libreria/specs/tech-stack.md` §5, §6 y §8 y de `AGENTS.md` ("Ejecutar") |

### Tests de la feature

`python -m pytest repo_libreria/tests/test_security.py repo_libreria/tests/test_config.py --no-cov -v` (extracto de LIB-03; los 40 pasan):

```text
test_security.py::test_key_vault_traduce_el_nombre_y_cachea PASSED
test_security.py::test_key_vault_inexistente_o_vacio[secretos0] PASSED
test_security.py::test_key_vault_inexistente_o_vacio[secretos1] PASSED
test_security.py::test_key_vault_inexistente_o_vacio[secretos2] PASSED
test_security.py::test_key_vault_otros_errores_son_secret_error[sin-credencial] PASSED
test_security.py::test_key_vault_otros_errores_son_secret_error[sin-permiso] PASSED
test_security.py::test_key_vault_otros_errores_son_secret_error[dominio-distinto] PASSED
test_security.py::test_un_cliente_inyectado_que_se_evalua_falso_se_usa_igual PASSED
test_security.py::test_sin_cliente_usa_secret_client_del_vault PASSED
test_config.py::test_archivos_invalidos[proveedor-no-soportado] PASSED
test_config.py::test_archivos_invalidos[key-vault-sin-url] PASSED
test_config.py::test_archivos_invalidos[key-vault-url-invalida] PASSED
test_config.py::test_con_key_vault_usa_la_vault_url_del_yaml PASSED
test_config.py::test_el_proveedor_inyectado_sustituye_al_del_yaml[entorno] PASSED
test_config.py::test_el_proveedor_inyectado_sustituye_al_del_yaml[se-evalua-falso] PASSED
test_config.py::test_un_fallo_de_acceso_es_config_error_sin_valores PASSED
40 passed
```

### CA-8: humo por extra

`UV_LINK_MODE=copy python repo_libreria/scripts/humo_extras.py`:

```text
[HUMO] Wheel: summa_ai_framework-0.1.0-py3-none-any.whl
[HUMO] PASS: agent (importa summa_ai_framework, summa_ai_framework.config, summa_ai_framework.security)
[HUMO] PASS: workflow (importa summa_ai_framework, summa_ai_framework.config, summa_ai_framework.security)
[HUMO] Todas las comprobaciones pasaron.
exit=0
```

### CA-8: cotas inferiores

`uv venv --python 3.12` aparte, con las cotas inferiores y pytest, y `--no-deps -e ./repo_libreria`. Después, `python -m pytest repo_libreria/tests -q -o addopts=""`:

```text
pydantic 2.7.0 | PyYAML 6.0.1 | azure-identity 1.15.0 | azure-keyvault-secrets 4.7.0 | azure-core 1.41.0
......................................................                   [100%]
57 passed in 1.89s
exit=0
```

`azure-core` no es dependencia directa: entra la versión que resuelve `azure-identity`.

### CA-7: integración con Key Vault

La persona la ejecutó el 2026-11-18 en su máquina, sobre `279688c` más los cambios de la feature, con `az login` y `SUMMA_PRUEBA_KEYVAULT_URL=https://kvema.vault.azure.net/` cargada desde su `.env`. `python repo_libreria/scripts/integracion_keyvault.py`:

```text
[INTEGRACION] PASS: SUMMA-PRUEBA-LIB-03 leído de Key Vault (16 caracteres)
[INTEGRACION] PASS: un secreto inexistente da ConfigError
C:\Users\...\Temp\tmprsm6b0hp\config_prueba.yaml: prueba.api_key: no se encontró el secreto 'SUMMA_NO_EXISTE_LIB_03' o está vacío
[INTEGRACION] Todas las comprobaciones pasaron.
```

`DefaultAzureCredential` usó la sesión de `az login`. La referencia `${SUMMA_PRUEBA_LIB_03}` se resolvió como el secreto `SUMMA-PRUEBA-LIB-03` (regla `_` → `-`), y el valor no aparece en la salida, solo su longitud.

- **Código de salida**: la persona no lo pegó. Que es 0 se deduce del código: la última línea solo se imprime justo antes de `return 0`, y cualquier fallo sale antes por `sys.exit(<mensaje>)` con código 1.
- **Key Vault personal**: [[tech-stack]] §11 pide integración "contra los servicios de dev". El Key Vault de dev de SUMMA no existe todavía (IaC transversal pendiente), así que la persona decidió usar el suyo, `kvema` (2026-11-18). La librería no depende del vault: lo que se prueba es la credencial, la regla de nombres y los errores.
- **Versión del código**: la ejecución fue antes de las correcciones de la vuelta 1, que no tocan el camino feliz ni el de "no encontrado".

## Errores encontrados al validar

| Error | Causa | Corrección | Destino en el harness |
|---|---|---|---|
| El humo y la instalación de las cotas fallaron con «La operación de nube no se puede realizar en un archivo con vínculos permanentes incompatibles» (os error 396) | uv enlaza con vínculos duros desde su caché, y Windows lo rechaza para un archivo nuevo de la caché (`annotated-types` 0.8.0) | `UV_LINK_MODE=copy` en esas ejecuciones | puntual (entorno de la máquina); si se repite, `UV_LINK_MODE=copy` en `AGENTS.md`, "Ejecutar" |
| `requirements.md` prometía `SecretNotFoundError` para un secreto deshabilitado | Key Vault no responde con «no encontrado» para un secreto deshabilitado | Pasa a `SecretError` con el mensaje de Azure, antes de programar | corrección de la spec |
| Vuelta 1 (menor): la aserción de CA-6 sobre el traceback no podía fallar | Ningún secreto llegaba a resolverse antes del error | El test resuelve `CLAVE` y falla con `OTRA` (`sources[0].token`) | test reforzado |
| Vuelta 1 (menor): `provider or …` y `client or …` descartaban un inyectado que se evalúa falso | Se comprobaba si era verdadero y no si era `None` | `is not None`; casos `se-evalua-falso` y `test_un_cliente_inyectado_que_se_evalua_falso_se_usa_igual` | corrección + test |
| Vuelta 1 (menor): un `ValueError` del SDK de Key Vault escaparía sin ser `ConfigError` | La política de autenticación de `azure-keyvault-secrets` lanza `ValueError` (comprobado en `_shared/challenge_auth_policy.py`: 4 `raise ValueError`) | Se captura `(AzureError, ValueError)`; caso `dominio-distinto` | corrección + test |
| Vuelta 1 (menor): el comentario de `pyproject.toml` atribuía las cotas solo a LIB-02 | Comentario desactualizado | Ahora cita LIB-02 y LIB-03 | corrección |
| Vuelta 2 (CI): `no_tocar` falló (p=0,17) porque el PR cambia `.env.template` | Contradicción de la spec: "No tocar" prohibía los `.env*`, mientras "Dependencias" y `AGENTS.md` piden que la persona añada la variable a `.env.template` | "No tocar" y la tabla de archivos de `plan.md` permiten esa línea sin valor, añadida por la persona | corrección de la spec. Al escribir un plan, "No tocar" no puede contradecir lo que el propio plan pide: lo comprueba el paso 4 de `/specs feature` (coherencia) |

## Veredicto del revisor

- **Vuelta 1** (revisor de Claude, local): **`accept`**. El revisor ejecutó el gate él mismo (124 passed, 100 %) y da por cumplidos los nueve CA. Sus cuatro hallazgos menores están corregidos (filas "Vuelta 1"); el gate queda en 127 passed y la suite con cotas inferiores en 57.
- **Vuelta 2** (revisor de CI con `gpt-6-luna`, PR #4 a `main`, sobre `54fadce`): **`revise`**. Pasan CA-1 a CA-9, la evidencia (0,61) y los cuatro riesgos (`rompe_algo` 0,22, `riesgo_seguridad` 0,10, `debilita_tests` 0,01, `dirige_revision` 0,00). Falla solo `03_secretos_identidad_no_tocar` (0,17). El explicador lo atribuye al cambio de `.env.template`, que el "No tocar" prohibía. Corregido en la spec (fila "Vuelta 2"); el código no cambia.
- **Vuelta 3** (revisor de CI, tras el push de la corrección): pendiente. Según el método, otro `revise` sería el segundo; un tercero se trata como `block`.
- **Vueltas de revise**: 1 de 2

## Desviaciones de la spec

- "No tocar" de `plan.md` corregido en la vuelta 2: `.env.template` recibe `SUMMA_PRUEBA_KEYVAULT_URL=` sin valor, como ya pedían "Dependencias" y `AGENTS.md`.

## Deuda técnica y temas para replanning

- **`.env.template`**: la persona añadió `SUMMA_PRUEBA_KEYVAULT_URL=` (commit `54fadce`). Ningún agente lo ha leído: `validar_comando.py` bloqueó el intento de ver su diff. La persona mostró el archivo en una captura: la línea va sin valor, y el explicador del revisor de CI la cita igual.
