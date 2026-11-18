# 01 — esqueleto-bundle — Review

> Evidencia real de la validación de la feature, rama `feature/01-esqueleto-bundle`, creada desde `main` (`14ea118`).
> Toda la evidencia es de **`14ea118` más los cambios de la feature sin commit**, el 2026-11-18. Los commits los hace la persona; la spec va primero.

## Gate

`python scripts/gate.py`:

```text
[GATE] PASS: Lint
[GATE] PASS: Formato
[GATE] PASS: Tipos
147 passed
[GATE] PASS: Tests
[GATE] Todas las comprobaciones pasaron.
```

## Cumplimiento por criterio

| CA | Estado | Evidencia |
|---|---|---|
| CA-1 | cumple | `bundle validate` de `dev` y `prod`, abajo |
| CA-2 | cumple | `test_targets_dev_y_prod_sin_host`, `test_cluster_efimero_de_un_nodo_con_dbr_18`, `test_trigger_semanal_pausado_en_dev_y_activo_en_prod` y `test_la_tarea_de_humo_apunta_a_un_script_existente` |
| CA-3 | cumple | `test_version_de_la_libreria_en_un_solo_lugar` |
| CA-4 | cumple | `test_el_bundle_real_no_tiene_secretos`, `test_el_comprobador_detecta_cada_secreto` (9 casos: host, clave secreta, variable token, URL con `usuario:clave@`, con `:token@` y con `token@`, clave numérica, referencia con literal y `account.key` de storage) y `test_las_referencias_no_son_secretos` |
| CA-5 | cumple | `test_importar_no_imprime_nada`, `test_ejecutar_en_local`, `test_main_imprime_y_devuelve_cero` y `test_como_script_termina_sin_system_exit` |
| CA-6 | cumple | Variante serverless en `SUCCESS` en el workspace de pruebas, abajo. La ejecución en clásico con DBR 18 queda pendiente (ver "Deuda técnica") |
| CA-7 | cumple | Gate de arriba (incluye los 20 tests de `repo_worklow`) y diff de `pyproject.toml` y `.gitignore` (`.databricks/`) |
| CA-8 | cumple | Diff de `AGENTS.md`: "Arquitectura" y "Ejecutar" |

### CA-1: validación del bundle

Desde `repo_worklow/`, `databricks bundle validate -t dev -p <perfil>` y `-t prod -p <perfil>`, con el usuario y el host ocultos:

```text
Name: summa_workflow
Target: dev
Workspace:
  User: <usuario>
  Path: /Workspace/Users/<usuario>/.bundle/summa_workflow/dev

Validation OK!
exit=0

Name: summa_workflow
Target: prod
Workspace:
  User: <usuario>
  Path: /Workspace/Users/<usuario>/.bundle/summa_workflow/prod

Validation OK!
exit=0
```

### CA-6: ejecución en Databricks

**Primer intento, con el bundle real** (`databricks bundle deploy -t dev`): construyó y subió la wheel desde `../repo_libreria`, y después el workspace rechazó el job.

```text
Building summa_ai_framework...
Uploading ../repo_libreria/dist/summa_ai_framework-0.1.0-py3-none-any.whl...
Error: cannot create resources.jobs.summa_workflow: Only serverless compute is supported in the workspace. (400 INVALID_PARAMETER_VALUE)
```

**Variante serverless desechable**, fuera del repo, por decisión de la persona. Usa el mismo `s00_humo.py`, la misma wheel y `environment_version: "6"`, y añade como wheels lo que el environment no trae: `azure-keyvault-secrets` 4.7.0, `azure-common` 1.1.28 e `isodate` 0.7.2. Necesitó cuatro intentos fallidos, uno por aprendizaje (ver "Errores encontrados al validar"). El run correcto, leído con `databricks jobs get-run` y `get-run-output`:

```text
run 1073785562932193 — 2026-11-18 16:10:04 — SUCCESS
tarea: s00_humo | estado: SUCCESS | duración s: 30
[HUMO] ambiente: serverless
[HUMO] python: 3.12.3
[HUMO] runtime: client.6.5
[HUMO] summa_ai_framework: 0.1.0
```

En un notebook serverless (Standard v6), pip instaló las cuatro wheels **sin red**. Usó lo que el environment ya trae, todo dentro de los rangos de la librería:

- pydantic 2.13.3;
- PyYAML 6.0.3;
- azure-identity 1.25.3;
- azure-core 1.41.0;
- cryptography 46.0.3;
- msal 1.36.0.

## Errores encontrados al validar

| Error | Causa | Corrección | Destino en el harness |
|---|---|---|---|
| `Only serverless compute is supported in the workspace` al crear el job | El workspace de pruebas solo admite serverless; el bundle pide clúster clásico (tech-stack §1) | Prueba con una variante serverless desechable; el bundle real no cambia | replanning del workflow: clásico o serverless para SUMMA |
| `Library installation failed` en serverless | Sin salida a internet (`Temporary failure in name resolution` al pedir `/simple/azure-keyvault-secrets/`); el workspace no tiene repositorio de paquetes propio | Las dependencias que faltan van como wheels | dato para LIB-04 y el pendiente de tech-stack §9 de la librería: las dependencias llegan por el feed (PyPI como *upstream*) o empaquetadas |
| `Library installation failed` también con las wheels | `environment_version: "3"` no trae azure-identity ni sus dependencias; el notebook usaba Standard v6 | `environment_version: "6"` | si SUMMA usa serverless, el bundle fija `environment_version` como hoy fija `spark_version` |
| La tarea terminó en `FAILED` con `SystemExit: 0` después de imprimir todo bien | Databricks ejecuta el script en IPython: `sys.exit(main())` cuenta como excepción | `s00_humo` llama a `main()` sin `sys.exit`; test `test_como_script_termina_sin_system_exit` | regla en tech-stack §2 del workflow (todos los steps) + test |
| Una hipótesis equivocada: el orden de las dependencias | Se probó cambiar el orden; el fallo siguió | Descartada; la causa era el environment | puntual |
| Vuelta 1 (menor): `plan.md` no recogía el paso a serverless, y la sección "Desviaciones" decía que sí | Se actualizaron brief, requirements y validation, pero no el plan | Plan alineado: "Validación real", paso 4 de la secuencia, "Dependencias" y "Riesgos" | corrección de la spec |
| Vuelta 1 (menor): el comprobador de secretos no veía `https://:pat@`, `https://pat@`, claves numéricas, `${var.x}abc` ni `fs.azure.account.key.*` | Patrones demasiado estrechos | Cualquier userinfo en una URL, literal numérico, solo referencias completas y `account.key`. Cinco casos sintéticos más; CA-4 actualizado | corrección + test |
| Vuelta 1 (menor): el test de `main` solo miraba dos de las cuatro líneas | Aserción débil | Compara las cuatro líneas exactas | test |
| Vuelta 1 (proceso): el commit de la spec (`6ec4e12`) marca la 01 como `passing` en vez de `in_progress` | La spec se commiteó cuando la feature ya estaba validada | Sin reescribir el historial; el cierre la pasa a `accepted` | puntual |

## Veredicto del revisor

- **Vuelta 1** (revisor de Claude, local): **`accept`**. El revisor ejecutó el gate él mismo (142 passed). Da por cumplidos los ocho CA y respetado el «No tocar». Sus seis hallazgos menores están corregidos o anotados como deuda (filas "Vuelta 1"); el gate queda en 147 passed.
- **Veredicto final** (revisor de CI con `gpt-6-luna`, PR a `main`): pendiente.
- **Vueltas de revise**: 0 de 2

## Desviaciones de la spec

- CA-6 cambió (decisión de la persona, 2026-11-18): la ejecución en Databricks se valida con una variante serverless desechable, porque el workspace de pruebas no admite clásico. Brief, plan, requirements y validation ya lo recogen.
- CA-5 suma el caso de ejecutar el step como script sin `SystemExit`, y [[tech-stack]] §2 suma la regla. «No tocar» del plan lo permite.
- CA-4 amplía lo que cuenta como secreto (vuelta 1 del revisor).

## Deuda técnica y temas para replanning

- **Ejecución en clásico con DBR 18**: pendiente hasta tener un workspace con cómputo clásico, el de dev de SUMMA u otro de pruebas. El bundle real nunca ha corrido en Databricks.
- **Replanning: ¿clásico o serverless para SUMMA?** [[tech-stack]] §1 dice clásico con DBR 18, pero existen workspaces solo serverless. Con serverless no hay cuota de núcleos ni versión de DBR, y sí `environment_version`. Lo decide la persona con plataforma.
- **Para la librería (LIB-04)**: un workspace sin salida a internet no instala dependencias desde PyPI, así que el feed de Azure Artifacts debe hacer de *upstream* de PyPI, o las dependencias van empaquetadas.
- **El target `prod` no tiene `run_as` ni `permissions`** (hallazgo 1 de la vuelta 1). Si alguien despliega a prod antes de que plataforma resuelva la identidad del job (`PENDIENTE` de [[tech-stack]] §6), el job correría cada semana con la identidad personal de quien desplegó, y el clúster cuesta dinero. Debe quedar resuelto antes del primer despliegue a prod (feature 15, CI/CD).
- **Limpieza en el workspace de pruebas**: la persona decidió dejar por ahora el job de prueba y los archivos. Si el estado local del bundle desechable (en el scratchpad) desaparece, se borran a mano desde la interfaz.
