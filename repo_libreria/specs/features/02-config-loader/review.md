# 02 — config-loader — Review

> Evidencia real de la validación de la feature, rama `feature/02-config-loader`, creada desde `e80bcf0` (cierre de LIB-01).
> Toda la evidencia es de **`e80bcf0` más los cambios de la feature sin commit, tras las correcciones del revise 2**, el 2026-11-18. Los commits los hace la persona (`AGENTS.md`, "Harness"); la spec va primero, como pide `plan.md` §Secuencia.

## Gate

`python scripts/gate.py`:

```text
[GATE] PASS: Lint
[GATE] PASS: Formato
[GATE] PASS: Tipos
Required test coverage of 80% reached. Total coverage: 100.00%
112 passed in 12.32s
[GATE] PASS: Tests
[GATE] Todas las comprobaciones pasaron.
```

## Cumplimiento por criterio

| CA | Estado | Evidencia |
|---|---|---|
| CA-1 | cumple | `test_resuelve_la_referencia_y_no_la_muestra` |
| CA-2 | cumple | `test_un_secreto_con_sintaxis_yaml_llega_literal` |
| CA-3 | cumple | `test_los_errores_no_muestran_el_secreto[ausente, vacio, en-campo-str, en-claro, en-campo-int]`: ubicación, sin excepción original encadenada y el secreto ausente del traceback formateado entero |
| CA-4 | cumple | `test_una_referencia_parcial_es_error` |
| CA-5 | cumple | `test_archivos_invalidos` (10 casos, incluidos `no-utf8`, `fecha-imposible`, `anidamiento-profundo`, `alias-circular` y `raiz-escalar`) y `test_un_archivo_vacio_da_los_valores_por_defecto[cero-bytes, comentarios]` |
| CA-6 | cumple | `test_resuelve_referencias_en_listas` y `test_la_ubicacion_incluye_el_indice` (`sources[1].token`) |
| CA-7 | cumple | `test_devuelve_la_variable` y `test_ausente_o_vacia_es_error[ausente, vacia]` |
| CA-8 | cumple | `pyproject.toml`, el gate (fronteras incluidas), el humo y la suite con las cotas inferiores, abajo |
| CA-9 | cumple | Diff de `repo_libreria/specs/tech-stack.md`: §2 (idioma), §5 (tabla "Añadidas por features") y §8 (reglas de las referencias, incluida la de los campos `Any`) |
| CA-10 | cumple | Abajo: 7 tests de detección de features (3 nuevos y 4 anteriores sin cambios) y el contexto real de la feature 01. Diff de `AGENTS.md`, sección "Harness" |

### Tests de la librería

`python -m pytest repo_libreria/tests --no-cov -v`:

```text
test_config.py::test_resuelve_la_referencia_y_no_la_muestra PASSED
test_config.py::test_un_secreto_con_sintaxis_yaml_llega_literal PASSED
test_config.py::test_los_errores_no_muestran_el_secreto[ausente] PASSED
test_config.py::test_los_errores_no_muestran_el_secreto[vacio] PASSED
test_config.py::test_los_errores_no_muestran_el_secreto[en-campo-str] PASSED
test_config.py::test_los_errores_no_muestran_el_secreto[en-claro] PASSED
test_config.py::test_los_errores_no_muestran_el_secreto[en-campo-int] PASSED
test_config.py::test_una_referencia_parcial_es_error PASSED
test_config.py::test_archivos_invalidos[inexistente] PASSED
test_config.py::test_archivos_invalidos[no-utf8] PASSED
test_config.py::test_archivos_invalidos[mal-formado] PASSED
test_config.py::test_archivos_invalidos[fecha-imposible] PASSED
test_config.py::test_archivos_invalidos[anidamiento-profundo] PASSED
test_config.py::test_archivos_invalidos[raiz-lista] PASSED
test_config.py::test_archivos_invalidos[raiz-escalar] PASSED
test_config.py::test_archivos_invalidos[alias-circular] PASSED
test_config.py::test_archivos_invalidos[clave-desconocida] PASSED
test_config.py::test_archivos_invalidos[proveedor-no-soportado] PASSED
test_config.py::test_un_archivo_vacio_da_los_valores_por_defecto[cero-bytes] PASSED
test_config.py::test_un_archivo_vacio_da_los_valores_por_defecto[comentarios] PASSED
test_config.py::test_resuelve_referencias_en_listas PASSED
test_config.py::test_la_ubicacion_incluye_el_indice PASSED
test_fronteras.py (15 casos de LIB-01) PASSED
test_paquete.py (2 casos de LIB-01) PASSED
test_security.py::test_devuelve_la_variable PASSED
test_security.py::test_ausente_o_vacia_es_error[ausente] PASSED
test_security.py::test_ausente_o_vacia_es_error[vacia] PASSED
42 passed (los mismos más `fecha-imposible` y `anidamiento-profundo`)
```

### CA-8: humo por extra

`python repo_libreria/scripts/humo_extras.py`, que instala pydantic y PyYAML desde PyPI en cada entorno limpio:

```text
[HUMO] Wheel: summa_ai_framework-0.1.0-py3-none-any.whl
[HUMO] PASS: agent (importa summa_ai_framework, summa_ai_framework.config, summa_ai_framework.security)
[HUMO] PASS: workflow (importa summa_ai_framework, summa_ai_framework.config, summa_ai_framework.security)
[HUMO] Todas las comprobaciones pasaron.
exit=0
```

### CA-8: cotas inferiores

Entorno aparte: `uv venv --python 3.12`, con `pydantic==2.7.0`, `PyYAML==6.0.1` y `pytest`, más `uv pip install --no-deps -e ./repo_libreria`. Después, `python -m pytest repo_libreria/tests -q -o addopts=""`:

```text
pydantic 2.7.0 | PyYAML 6.0.1
........................................                                 [100%]
42 passed in 1.55s
exit=0
```

### CA-10: el revisor de CI encuentra las specs de cada proyecto

`python -m pytest tests/test_revisor_ci.py --no-cov -v -k features` (los cuatro primeros son los tests anteriores, sin cambios):

```text
test_revisor_ci.py::test_features_solo_carpetas_de_feature PASSED
test_revisor_ci.py::test_features_por_rama[feature/03-pagos-esperado0] PASSED
test_revisor_ci.py::test_features_por_rama[chore/ask-git-commit-esperado1] PASSED
test_revisor_ci.py::test_features_por_rama[feature/../../etc-esperado2] PASSED
test_revisor_ci.py::test_features_en_specs_de_un_proyecto PASSED
test_revisor_ci.py::test_features_por_rama_busca_en_el_arbol[feature/02-config-esperado0] PASSED
test_revisor_ci.py::test_features_por_rama_busca_en_el_arbol[feature/09-otra-esperado1] PASSED
7 passed, 20 deselected
```

Sobre el repo real, sin llamar al modelo: `REVISOR_BASE=develop`, y `REVISOR_HEAD` y `REVISOR_RAMA` con `feature/01-esqueleto-paquete`. Después, `revisor_ci.contexto("")`:

```text
criterios: 9
   01_esqueleto_paquete_CA_1 … 01_esqueleto_paquete_CA_7
   01_esqueleto_paquete_no_tocar
   01_esqueleto_paquete_evidencia
contexto: 184027 caracteres
```

Antes del cambio, esa misma llamada no encontraba la spec: buscaba `specs/features/01-esqueleto-paquete` en la raíz y salía «FALLA la spec no tiene criterios **CA-N**».

## Errores encontrados al validar

| Error | Causa | Corrección | Destino en el harness |
|---|---|---|---|
| `PyYAML>=6.0` no se puede instalar en Python 3.12 (Windows) | 6.0 no tiene wheel para 3.12 y su build desde fuente falla (`'build_ext' object has no attribute 'cython_sources'`) | Cota a `PyYAML>=6.0.1`, comprobada con la suite completa | corrección + prueba de cotas en `review.md` |
| El error de la sección `secrets` salía sin el prefijo `secrets.` en su ubicación | Se validaba `SecretsConfig` por separado | `_describir` recibe un prefijo de ubicación; caso `proveedor-no-soportado` | corrección + test |
| Lint: orden de imports en los tests nuevos | Ruff trata `summa_ai_framework` como paquete instalado | `ruff check --fix` | puntual |
| Revise 1: un YAML que no está en UTF-8 lanzaba `UnicodeDecodeError` sin ruta, con los bytes del archivo en `.object` | `UnicodeDecodeError` es `ValueError`, no `OSError` | Rama propia con `from None`; caso `no-utf8` (cp1252) | corrección + test |
| Revise 1: la ubicación salía `sources.1.token` y la spec dice `clave[índice]` | `_texto` unía todo con puntos | Índices como `[i]`: `sources[1].token` | corrección + test |
| Revise 1: alias circulares (`a: &a [*a]`) daban `RecursionError` | `_resolver` recorre la estructura sin detectar ciclos | `RecursionError` → `ConfigError`, con un `shortcut:` para las cadenas acíclicas | corrección + test |
| Revise 1: el aviso "debe declararse SecretRef" sustituía el motivo de pydantic | `_describir` reemplazaba el mensaje | Se conserva el motivo y se añade la pista | corrección + test |
| Revise 1: tech-stack §8 no reflejaba los campos `Any` | Redacción | §8 y los casos borde de requirements alineados con el código | corrección de la spec |
| Revise 1: faltaban la raíz escalar y el archivo de cero bytes | Cobertura de casos | `raiz-escalar` y `cero-bytes` | test |
| Revise 1: el revisor no pudo ejecutar el gate | Se lanzó en la misma tanda que el `cd` a la raíz y arrancó en `repo_libreria/specs` | El revisor se lanza en un turno aparte, después del `cd` | puntual; segunda vez que pasa (LIB-01 vuelta 1). Si se repite, que `solo_lectura.py` acepte la ruta absoluta del gate |
| Revise 1: `progress.md` sin actualizar | El cierre aún no había llegado a ese paso | Actualizado en esta vuelta | corrección |
| Revise 2: una fecha imposible (`2024-02-30`) escapaba como `ValueError`, sin ruta | PyYAML lanza `ValueError` y no `yaml.YAMLError` al construir fechas (comprobado ejecutándolo) | `_leer` convierte en `ConfigError` todo `ValueError` del parseo; caso `fecha-imposible` | corrección + test |
| Revise 2: un anidamiento muy profundo escapaba como `RecursionError` | El composer de PyYAML es recursivo, y el `RecursionError` de `load_config` solo cubría la resolución | Mismo `except` en `_leer`; caso `anidamiento-profundo` | corrección + test |
| Revise 2 (patrón): dos vueltas seguidas con una excepción del parser que escapaba sin ruta | Se capturaban las excepciones conocidas una a una | Se cierra la frontera del parseo entera (`YAMLError`, `ValueError` y `RecursionError`) | se repite: una línea en `AGENTS.md` si vuelve a pasar en otro loader |
| Revise 2: `brief.md` decía `load_config(ruta, esquema)` | Redacción anterior a la decisión de nombres en inglés | `load_config(path, schema)` | corrección de la spec |
| Revise 2: `strerror` puede ser `None` y una clave bool (`on:`) se escribía como índice `[True]` | Cosmético | `strerror or type(e).__name__`; `type(p) is int` en `_texto` | corrección |
| Revise 2 (observación): el motivo de pydantic va en inglés y tech-stack pide mensajes en español | Pydantic da sus mensajes en inglés | Regla en requirements: los mensajes propios en español y el motivo de pydantic tal cual | corrección de la spec; lo confirma la persona |

## Veredicto del revisor

- **Vuelta 1**: `revise`. Obligatorio: el archivo no UTF-8. A decidir: el formato de la ubicación (se ajusta el código a la spec). Recomendados: alias circulares, motivo original, tech-stack §8 y dos tests. Todo corregido (filas "Revise 1").
- **Vuelta 2**: `revise`. El revisor ejecutó el gate él mismo (107 passed, 100 %) y da por cumplidos todos los CA salvo un caso de CA-5: la fecha imposible. Todo corregido (filas "Revise 2").
- **Vuelta 3**: **`accept`**. Evaluador `gpt-6-luna` (Decisions API de Azure OpenAI, `scripts/revisor_ci.py`), un modelo distinto del que implementó (decisión de la persona, 2026-11-18). Lo ejecutó la persona en local sobre `896d698`, con `REVISOR_BASE=feature/01-esqueleto-paquete` y `REVISOR_RAMA=feature/02-config-loader`:

  ```text
  OK     02_config_loader_CA_1: p=0.99
  OK     02_config_loader_CA_2: p=0.98
  OK     02_config_loader_CA_3: p=0.95
  OK     02_config_loader_CA_4: p=1.00
  OK     02_config_loader_CA_5: p=0.97
  OK     02_config_loader_CA_6: p=0.99
  OK     02_config_loader_CA_7: p=1.00
  OK     02_config_loader_CA_8: p=0.97
  OK     02_config_loader_CA_9: p=1.00
  OK     02_config_loader_CA_10: p=0.94
  OK     02_config_loader_no_tocar: p=0.97
  OK     02_config_loader_evidencia: p=0.82
  OK     rompe_algo: p=0.37
  OK     riesgo_seguridad: p=0.14
  OK     debilita_tests: p=0.01
  OK     dirige_revision: p=0.02

  [REVISOR] accept
  ```

  Antes, sobre el mismo commit, el gate seguía en verde (112 passed).
- **Vueltas de revise**: 2 de 2

## Desviaciones de la spec

- La verificación de la cota inferior pasó de comprobar solo `errors(include_input=False)` a ejecutar la suite completa con pydantic 2.7.0 y PyYAML 6.0.1. Es más fuerte y descubrió la cota de PyYAML. `plan.md`, `requirements.md` (CA-8) y `validation.md` ya lo recogen.
- CA-5 suma tres casos (no UTF-8, alias circulares y raíz escalar) y requirements suma tres casos borde (los mismos más los campos `Any`), a raíz del revise 1. El revise 2 añade la fecha imposible y el anidamiento profundo.
- Después del accept, a petición de la persona: el comando local del evaluador guarda su salida con `Tee-Object` en `revisor_local.txt`, que se añade a `.gitignore`. Cambia la documentación (`AGENTS.md`, "Harness"), no el código del script.
- Cambio de alcance (decisión de la persona): la feature también arregla `scripts/revisor_ci.py` para que la vuelta 3 la haga `gpt-6-luna`. Resuelve la deuda "Revisor de CI" de LIB-01. Brief, plan ("No tocar" enmendado), requirements (comportamiento 7 y CA-10) y validation ya lo recogen.

## Deuda técnica y temas para replanning

- **Umbral del evaluador sin calibrar** (`UMBRAL = 0.5`, `shortcut:` en `revisor_ci.py`). `rompe_algo` dio 0,37, el riesgo más alto, probablemente por los cambios del harness dentro de la feature. Conviene calibrarlo con varios PRs cuyo resultado correcto se conozca antes de hacerlo *required check*.
- **Salida del evaluador local**: se guarda con `Tee-Object` en `revisor_local.txt` (ignorado por git) y se copia a `review.md`, que es el registro versionado (`AGENTS.md`, "Harness").
- **Cadenas de alias acíclicas** (tipo *billion laughs*): `_resolver` las recorre enteras. Es un límite aceptado (`shortcut:` en `loader.py`) porque el YAML lo versiona el equipo. Si algún día llega de fuera, hay que limitar los alias.
- **Campos `Any` u `object`** aceptan una referencia como `SecretStr` sin aviso. Está documentado en tech-stack §8; las secciones de la librería no deben usarlos para credenciales.
