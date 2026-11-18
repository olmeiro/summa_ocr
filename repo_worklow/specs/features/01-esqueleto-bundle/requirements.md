# 01 — esqueleto-bundle — Requirements

> Contrato funcional: qué debe hacer la feature. El revisor valida el diff contra sus criterios de aceptación.

## Comportamiento esperado

1. `repo_worklow/` es la raíz de un Databricks Asset Bundle con dos targets:
   - `dev`, en modo `development`, el target por defecto;
   - `prod`, en modo `production`.
2. Ningún target declara `workspace.host`: el workspace sale del perfil del CLI (`-p <perfil>` o `DATABRICKS_CONFIG_PROFILE`).
3. El bundle declara un job con:
   - un clúster efímero de un nodo, con DBR `18.x-scala2.13` y el tipo de nodo `Standard_D4ds_v5`, los dos como variables;
   - un trigger semanal: los lunes a las 02:00, `America/Bogota`, `PAUSED` en dev y `UNPAUSED` en prod;
   - una tarea `s00_humo`.
4. Al desplegar, el bundle construye la wheel de `summa-ai-framework` desde `../repo_libreria`, y la tarea la instala.
5. La tarea `s00_humo` imprime, con el prefijo `[HUMO]`, el ambiente (el target), la versión de Python, la del runtime de Databricks y la de `summa-ai-framework`. Importa `summa_ai_framework.config` y `summa_ai_framework.security`, y termina con código 0.

## Reglas de negocio

- **Versión de la librería en un solo lugar**: la variable `libreria_version` de `databricks.yml`. Ningún otro archivo del bundle escribe una versión de la librería. Debe coincidir con la versión de `repo_libreria/pyproject.toml` mientras la wheel se construya desde ahí.
- **Sin secretos en el bundle**:
  - ni credenciales;
  - ni variables `AZURE_CLIENT_SECRET` o de token;
  - ni URLs con credenciales, como el token de un feed en `PIP_EXTRA_INDEX_URL` ([[tech-stack]] §2 y §9).
- **Sin datos del workspace de pruebas** en el repo: ni su host, ni su perfil, ni sus políticas de clúster.
- **El step no ejecuta nada al importarse**: expone `ejecutar(ambiente)` y solo `main()` lee los argumentos ([[tech-stack]] §2).
- **El step no llama a `sys.exit`**: Databricks ejecuta el script dentro de IPython, donde hasta `sys.exit(0)` marca la tarea como fallida (visto en serverless, 2026-11-18). Un fallo se señala con una excepción. La regla pasa a [[tech-stack]] §2 para todos los steps.
- **Nombres de SUMMA**: bundle y job `summa_workflow`.

## Casos borde

- `databricks bundle validate` sin perfil ni host: falla con el error del CLI. Así se documenta, porque no hay un host por defecto que oculte el problema.
- `libreria_version` distinta de la versión de la librería: lo detecta el gate, y además el despliegue fallaría porque no existe esa wheel.
- `DATABRICKS_RUNTIME_VERSION` ausente, como ocurre al ejecutar en local: el step lo informa como `local` en vez de fallar.
- Un bundle que ya está desplegado se actualiza en el sitio: `deploy` es idempotente para el job.

## Restricciones

- [[tech-stack]] §1: DBR 18 LTS, y un clúster que quepa en la cuota.
- [[tech-stack]] §8: trigger en el bundle, pausado en dev y activo en prod; ConfigFile fuera del alcance de esta feature.
- [[tech-stack]] §11: el gate prueba en Python puro, sin Spark. La evidencia de cierre incluye una ejecución del job en dev.
- El gate no necesita el CLI de Databricks ni acceso a Azure.

## Criterios de aceptación

- [ ] **CA-1**: Dado el bundle, cuando la persona o el agente ejecutan `databricks bundle validate -t dev` y `-t prod` con el perfil del workspace de pruebas, entonces los dos terminan sin errores.
- [ ] **CA-2**: Dados los YAML del bundle, cuando corre `test_bundle.py`, entonces comprueba:
  - los targets `dev` (development, por defecto) y `prod` (production);
  - que ningún target lleva `workspace.host`;
  - el clúster de un nodo con `${var.spark_version}` = `18.x-scala2.13` y `${var.node_type_id}` = `Standard_D4ds_v5`;
  - el `schedule` con `0 0 2 ? * MON` en `America/Bogota`;
  - la pausa: `PAUSED` en dev y `UNPAUSED` en prod;
  - la tarea `s00_humo`, cuyo `python_file` existe.
- [ ] **CA-3**: Dado el bundle, cuando corre el gate, entonces:
  - `libreria_version` es igual a la versión de `repo_libreria/pyproject.toml`;
  - la ruta de la wheel de la tarea usa `${var.libreria_version}`;
  - ningún otro texto del bundle contiene esa versión literal.
- [ ] **CA-4**: Dados los YAML del bundle, cuando corre el gate, entonces falla si aparece cualquiera de estos:
  - una clave con `secret`, `password`, `token`, `api_key` o `account.key` (p. ej. `fs.azure.account.key.*`) y un valor literal, sea texto o número. Una referencia completa (`${var.x}` o `{{secrets/...}}`) no es literal; `${var.x}abc` sí;
  - una URL con credenciales en la parte de usuario: `://usuario:clave@`, `://:token@` o `://token@`;
  - un `workspace.host`.

  El test se prueba con un YAML sintético que contiene cada uno.
- [ ] **CA-5**: Dado `s00_humo`, cuando se importa, entonces no imprime nada. Cuando se llama a `ejecutar("dev")` en local, devuelve:
  - `ambiente="dev"`;
  - la versión de Python;
  - `runtime="local"`;
  - la versión instalada de `summa-ai-framework`.

  `main(["--ambiente", "dev"])` imprime esas líneas con `[HUMO]` y devuelve 0. Ejecutado como script (`__main__`, como lo lanza Databricks), termina sin `SystemExit`.
- [ ] **CA-6**: Dado el workspace de pruebas, que solo admite cómputo serverless, cuando la persona despliega y ejecuta una variante serverless desechable del job, fuera del repo, entonces la ejecución termina en `SUCCESS`. Esa variante usa:
  - el mismo `s00_humo.py`;
  - la misma wheel de `summa-ai-framework`;
  - las dependencias que el environment no trae, como wheels.

  Su log muestra `[HUMO]` con un ambiente, Python 3.12, el runtime y `summa_ai_framework: 0.1.0`. La ejecución del bundle real (`-t dev`, clúster clásico con DBR 18) queda pendiente hasta tener un workspace con cómputo clásico (decisión de la persona, 2026-11-18).
- [ ] **CA-7**: Dado el gate de la raíz, entonces lint, formato, tipos y tests incluyen `repo_worklow/`, y `.databricks/` está en `.gitignore`.
- [ ] **CA-8**: Dado `AGENTS.md`, entonces:
  - "Arquitectura" dice que `repo_worklow/` contiene el bundle;
  - "Ejecutar" lista `bundle validate`, `deploy` y `run` con `-p <perfil>`.
