# 02 — config-loader — Validation

> Cómo se comprueba cada criterio de aceptación y qué evidencia se guarda. Se escribe antes de programar.

## Verificación por criterio

| CA | Cómo se verifica | Tipo | Evidencia |
|---|---|---|---|
| CA-1 | `repo_libreria/tests/test_config.py`: carga con la variable puesta con `monkeypatch`. Comprueba `get_secret_value()` y que el valor no aparece en `repr`, `str`, `model_dump` ni `model_dump_json` | automática, en el gate | Salida de `python -m pytest repo_libreria/tests --no-cov -v` |
| CA-2 | `test_config.py`: secreto con `: `, `#`, `- `, comillas y `\n`, y otra clave del mismo YAML que no cambia | automática, en el gate | Ídem |
| CA-3 | `test_config.py`, un caso por fallo. Cada uno comprueba el tipo, la ubicación, `valor not in str(error)`, `error.__cause__ is None` y `error.__suppress_context__` | automática, en el gate | Ídem |
| CA-4 | `test_config.py`: `Bearer ${TOKEN}` con `TOKEN` definida | automática, en el gate | Ídem |
| CA-5 | `test_config.py`: `test_archivos_invalidos` con un caso por situación (incluidos no UTF-8, fecha imposible, anidamiento profundo, alias circular y raíz escalar) y `test_un_archivo_vacio_da_los_valores_por_defecto` con cero bytes y con solo comentarios | automática, en el gate | Ídem |
| CA-6 | `test_config.py`: subclase con una lista de mapas con referencias; caso feliz y secreto ausente en `[1]` | automática, en el gate | Ídem |
| CA-7 | `repo_libreria/tests/test_security.py`: nombre presente, ausente y vacío | automática, en el gate | Ídem |
| CA-8 | `python scripts/gate.py` y `python repo_libreria/scripts/humo_extras.py`. Para las cotas inferiores, `uv venv` aparte con `pydantic==2.7.0`, `PyYAML==6.0.1`, pytest y la librería editable sin dependencias, donde se ejecuta `pytest repo_libreria/tests -o addopts=""` | automática + comando | Salida del gate, del humo (importa `config` y `security` con cada extra) y de la suite con las cotas inferiores |
| CA-9 | Lectura del diff de `repo_libreria/specs/tech-stack.md` | revisión | Diff |
| CA-10 | En el gate, `tests/test_revisor_ci.py`: `test_features_en_specs_de_un_proyecto`, `test_features_por_rama_busca_en_el_arbol` y los tests anteriores sin cambios. Fuera del gate, `contexto("")` sobre el repo real con `REVISOR_BASE=develop` y `REVISOR_RAMA`/`REVISOR_HEAD=feature/01-esqueleto-paquete`, sin llamar al modelo. Además, lectura del diff de `AGENTS.md` | automática + comando + revisión | Salida de los tests y lista de criterios que arma el contexto |

## Validación técnica

- [ ] `python scripts/gate.py` en verde, con cobertura ≥ 80 %.
- [ ] `python repo_libreria/scripts/humo_extras.py` en verde.
- [ ] `git status` sin archivos de build versionados.

## Evidencia requerida para cerrar

En `review.md`, con el commit en que se obtuvo cada una:

- la salida del gate;
- la de `pytest repo_libreria/tests --no-cov -v`;
- la del humo;
- la de la suite con las cotas inferiores.

No hay prueba de integración contra Azure: el proveedor de entorno no toca ningún servicio ([[tech-stack]] §11). Key Vault llega en LIB-03.
