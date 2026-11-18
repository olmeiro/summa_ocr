# 01 — esqueleto-bundle — Plan

> Cómo se construye la feature. No repite los criterios de requirements.md.

## Enfoque

1. **Bundle mínimo con dos archivos**, como la base (`BaseRef/workflow/databricks.yml` y `resources/workflow.yml`), pero sin sus problemas:
   - una sola versión de la librería;
   - sin credenciales;
   - sin el host del workspace en el YAML.
2. **Variables** en `databricks.yml`:
   - `libreria_version` (`0.1.0`);
   - `spark_version` (`18.x-scala2.13`);
   - `node_type_id` (`Standard_D4ds_v5`);
   - `trigger_cron` (`0 0 2 ? * MON`, en formato Quartz);
   - `trigger_zona` (`America/Bogota`);
   - `trigger_pausa`: `PAUSED` en dev y `UNPAUSED` en prod, fijado por target. El modo `development` ya pausa los triggers, pero declararlo hace la regla visible y comprobable en el gate.
3. **Librería**:
   - un artefacto `whl` con `path: ../repo_libreria` y `build: uv build --wheel`;
   - la tarea la declara como `whl: ../../repo_libreria/dist/summa_ai_framework-${var.libreria_version}-py3-none-any.whl`;
   - la versión aparece en el nombre del archivo, así que una variable que no coincida con la librería rompe el despliegue y lo detecta el gate.
4. **Clúster de un nodo**: `num_workers: 0`, `spark.databricks.cluster.profile: singleNode`, `spark.master: local[*]`, la etiqueta `ResourceClass: SingleNode`, `ON_DEMAND_AZURE` y `SINGLE_USER`. Pasar a varios nodos supone cambiar la definición del clúster, no solo una variable.
5. **Step `s00_humo`**:
   - `ejecutar(ambiente)` devuelve un dict con el ambiente, la versión de Python, `DATABRICKS_RUNTIME_VERSION` y la versión de `summa-ai-framework` (`importlib.metadata`), e importa `summa_ai_framework.config` y `.security`;
   - `main()` parsea `--ambiente` e imprime cada valor con el prefijo `[HUMO]`.

   No usa Spark: el gate lo prueba en Python puro ([[tech-stack]] §11).
6. **Tests del gate**: leen los YAML con PyYAML (ya está en la librería) y la versión de `repo_libreria/pyproject.toml` con `tomllib`. No necesitan el CLI de Databricks.
7. **Validación real**:
   - `bundle validate` de los dos targets, que puede lanzar el agente porque solo lee;
   - `bundle deploy` y `bundle run` en dev, que lanza la persona: crean recursos y cuestan dinero.

## Archivos a crear o modificar

| Archivo | Cambio |
|---|---|
| `repo_worklow/databricks.yml` | Nuevo: bundle, variables, artefacto `whl`, `sync.exclude` (specs y tests) y targets `dev` y `prod` |
| `repo_worklow/resources/workflow.yml` | Nuevo: job `summa_workflow` con el clúster efímero, el `schedule` y la tarea `s00_humo` |
| `repo_worklow/src/steps/__init__.py` | Nuevo, vacío: paquete de steps |
| `repo_worklow/src/steps/s00_humo.py` | Nuevo: step de humo |
| `repo_worklow/tests/test_bundle.py` | Nuevo: estructura, versión en un solo lugar y ausencia de secretos |
| `repo_worklow/tests/test_s00_humo.py` | Nuevo: el step en Python puro |
| `pyproject.toml` (raíz) | mypy y pytest con `repo_worklow/src` y `repo_worklow/tests`; `pythonpath` con `repo_worklow/src`; `per-file-ignores` de sus tests |
| `.gitignore` | `.databricks/`, el estado local del CLI |
| `AGENTS.md` | "Arquitectura": `repo_worklow/` ya tiene código. "Ejecutar": comandos del bundle |
| `repo_worklow/specs/tech-stack.md` | §2: regla nueva, los steps no llaman a `sys.exit` (aprendizaje de la prueba en serverless) |
| `repo_worklow/specs/roadmap.md`, `progress.md` | Estado y continuidad |

## Secuencia

1. **Spec**, con la 01 en `in_progress`. Commit `docs(specs): define la spec de 01-esqueleto-bundle`.
2. **Bundle y step**: los YAML, el step, los tests y el gate en verde. Commit `feat(bundle): esqueleto del bundle con job de humo`.
3. **Validación**: `bundle validate` de los dos targets. Si Databricks pide ajustes, se corrigen aquí, que es lo que se quiere descubrir. Commit de lo que cambie.
4. **Despliegue y ejecución en dev**, que lanza la persona. La salida va a `review.md`.
5. **Documentación** (`AGENTS.md`) y cierre:
   - revisor de Claude;
   - commits;
   - PR a `main`, con el revisor de CI;
   - el cierre dentro del propio PR.

## Dependencias

- Ninguna feature previa. La librería (LIB-01 a LIB-03) ya está en `main` y se construye desde `../repo_libreria`.
- CLI de Databricks (v1.26 en la máquina de la persona) con el perfil de su workspace de pruebas. Allí se verificó (2026-11-18) que hay DBR 18 LTS, `Standard_D4ds_v5` y cuota de vCPU, y que la persona es administradora.
- uv en la máquina que despliega, porque construye la wheel. En esta máquina, `UV_LINK_MODE=copy`.

## Riesgos

- **El artefacto está fuera de la raíz del bundle** (`../repo_libreria`), y Databricks puede no aceptar rutas fuera de ella. → Se ve en `bundle validate` y `deploy`. Alternativa: construir la wheel dentro de `repo_worklow/dist/` con `--out-dir`.
- **Las dependencias de la librería chocan con las de DBR 18** (pydantic o el SDK de Azure preinstalados en otra versión). → Es justo lo que prueba el humo. Si choca, el arreglo va a `repo-libreria` (rangos de versiones) por replanning.
- **Una wheel con `whl:` no instala extras.** El extra `workflow` está vacío hoy. → Al llegar el feed se usará `pypi: summa-ai-framework[workflow]==...`.
- **Restos de `build/` en `repo_libreria`** pueden colarse en la wheel, igual que en el humo de LIB-01. → El nombre exacto de la wheel evita usar una equivocada. El humo de la librería sigue limpiando `build/`.
- **Costo**: cada ejecución levanta un nodo unos minutos. → Solo se lanza a mano en dev; el trigger va pausado.

## No tocar

- `repo_libreria/` (código, specs y scripts) y `repo_agente_conversacional/`.
- El harness de la raíz (`scripts/`, `.claude/`, `.github/workflows/`, `tests/`). `pyproject.toml`, `.gitignore` y `AGENTS.md` solo cambian como dice la tabla de arriba.
- Los `.env*`.
- La Constitución del workflow, salvo el estado en [[roadmap]] y [[progress]] y la regla de `sys.exit` en [[tech-stack]] §2. La decisión clásico o serverless de §1 no se toca aquí: va a replanning.
