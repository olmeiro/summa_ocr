# CHANGELOG

## 2026-11-20 — Cómputo serverless

### Changed
- El job corre en un environment serverless (`environment_version: "6"`) en vez de un clúster clásico efímero ([[decisions]] DEC-002, que reemplaza a DEC-001). La wheel de la librería pasa a ser dependencia del environment. `bundle validate` pasa en dev y prod.

### Notes
- Primera ejecución en serverless en `dbr-analitica-summa-aba-qa`: run `386609408515617` del 2026-11-20, `SUCCESS` en unos 40 s, con Python 3.12.3, runtime `client.6.5` y la librería 0.1.0. Desplegado desde una exportación sin `.git`.

## 2026-11-19 — Nodo sin discos Premium

### Fixed
- El clúster efímero pasa de `Standard_D4ds_v5` a `Standard_D4d_v4`. La Azure Policy de discos de SUMMA rechazaba el disco Premium que Databricks pone a las VM que lo admiten, y el clúster no llegaba a crearse ([[decisions]] DEC-001).

### Notes
- Primera ejecución en clásico: el job de humo corre en `SUCCESS` en `dbr-analitica-summa-aba-qa`, con DBR 18.3, Python 3.12.3 y la librería 0.1.0.

## 2026-11-18 — 01-esqueleto-bundle

### Added
- `repo_worklow/` es un Databricks Asset Bundle: `databricks.yml` con los targets `dev` y `prod`, y `resources/workflow.yml` con el job `summa_workflow`. El job tiene:
  - un clúster efímero de un nodo `Standard_D4ds_v5` con DBR 18 LTS;
  - un trigger semanal, los lunes a las 02:00 `America/Bogota`, pausado en dev y activo en prod;
  - el step de humo `s00_humo`.
- La versión de `summa-ai-framework` se fija en un solo lugar (`libreria_version`). Mientras no exista el feed, la wheel se construye desde `../repo_libreria` al desplegar.
- El workspace sale del perfil del CLI de Databricks: ningún host ni secreto va en el bundle. Lo comprueban tests del gate.

### Changed
- [[tech-stack]] §2: los steps no llaman a `sys.exit`. Databricks ejecuta el script en IPython, y hasta `sys.exit(0)` marca la tarea como fallida.

### Notes
- Probado en el workspace de pruebas de la persona, que es solo serverless. Con una variante serverless del job, el step corre en `SUCCESS` con Python 3.12.3 y la librería 0.1.0.
- La ejecución en clásico con DBR 18 queda pendiente.
- Queda pendiente un replanning: ¿clásico o serverless para SUMMA?
- Para LIB-04: sin salida a internet, las dependencias de la librería tienen que llegar por el feed o empaquetadas.
