# CHANGELOG

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
