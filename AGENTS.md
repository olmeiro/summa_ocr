# AGENTS.md

Framework de IA de SUMMA: la librería `summa-ai-framework` y dos plantillas (workflow en Databricks y agente conversacional), que acabarán en repos propios de Azure DevOps. Mientras tanto comparten este repo (`OlmeDK/summa_framework_v0` en GitHub) y su harness.

## Ejecutar

```
uv venv && .venv\Scripts\activate
uv pip install -r requirements-dev.txt   # incluye requirements.txt y la librería en modo editable
python scripts/gate.py
python repo_libreria/scripts/humo_extras.py   # humo por extra; necesita uv y red, fuera del gate
python repo_libreria/scripts/integracion_keyvault.py   # Key Vault real (LIB-03): lo ejecuta la persona con az login y SUMMA_PRUEBA_KEYVAULT_URL del .env
```

Bundle del workflow, desde `repo_worklow/`. El workspace sale del perfil del CLI de Databricks (`databricks auth login`); ningún host va en el repo.

```
databricks bundle validate -t dev -p <perfil>   # solo lee; también -t prod
databricks bundle deploy -t dev -p <perfil>     # construye la wheel de ../repo_libreria y crea el job; lo lanza la persona
databricks bundle run summa_workflow -t dev -p <perfil>   # corre en serverless: cuesta, lo lanza la persona
```

API del agente, desde `repo_agente_conversacional/`. La app no lee `.env`: las variables `APP_*` las pone quien la ejecuta. `APP_ENVIRONMENT` es obligatoria (`local`, `dev` o `prod`), y `APP_DOCS=true` activa `/docs`.

```
$env:APP_ENVIRONMENT = "local"; $env:APP_DOCS = "true"
uvicorn --factory app.main:create_app --port 8000          # http://localhost:8000/health y /docs
docker build -t summa-agente:local .
docker run -d -e APP_ENVIRONMENT=local -p 8000:8000 --name summa-agente summa-agente:local
```

## Arquitectura

- `repo_libreria/`: librería `summa-ai-framework` (`src/summa_ai_framework/`, `tests/`, `scripts/`). El gate de la raíz la cubre, con cobertura mínima del 80 %; para ejecutar un solo test, `--no-cov`.
- `repo_worklow/`: plantilla del workflow. Es la raíz de un Databricks Asset Bundle (`databricks.yml`, `resources/`, `src/steps/`, `tests/`). El gate de la raíz cubre sus tests, que importan los steps como `steps.sNN_nombre`.
- `repo_agente_conversacional/`: plantilla del agente. Es una API FastAPI (`app/`: `main.py` con la fábrica `create_app`, `core/settings.py` y `api/`), con `tests/`, `requirements.txt` y `Dockerfile`. El gate de la raíz cubre sus tests, que importan la API como `app`.
- Cada proyecto tiene sus specs en `<proyecto>/specs/`: allí están su `progress.md`, su `decisions.md` y sus features. Donde este archivo dice `specs/`, léase la del proyecto que tocas.
- `specs/prerrequisitos-azure.md` (raíz) es transversal: recursos, identidades y permisos de Azure de los tres proyectos, y el orden para desplegar pronto.
- Fronteras de import de la librería: `repo_libreria/specs/decisions.md` (DEC-002). Un módulo nuevo se añade a un grupo en `repo_libreria/scripts/fronteras.py`.

## Variables de entorno

`.env` está en `.gitignore`; `.env.template` sí se versiona. Los agentes no pueden leer ni editar ningún `.env*`, tampoco el template: al introducir una variable nueva, pide a la persona que la añada a `.env.template`.

## Definición de terminado

1. `python scripts/gate.py` en verde (lint, formato, tipos y tests). Si falla, corrige y repite.
2. Revisión independiente (otro agente o una persona) contra la spec de la feature (`specs/features/NN-nombre/`) o, si no hay feature, contra lo pedido, con el diff y la salida del gate. Responde `accept`, `revise` o `block`. Solo `accept` cierra la tarea; `revise` admite 2 vueltas; con `block` o a la tercera vuelta, para y pregunta.
3. Reporta las comprobaciones ejecutadas y su resultado.

## Specs y continuidad

- Método SDD en `specs/orden_spec.md`; cada feature vive en `specs/features/NN-nombre/`, copiada de `_plantilla/`.
- Al empezar una sesión: lee `specs/progress.md`, mira `git log --oneline -10` y ejecuta el gate antes de tocar nada. Al terminar, actualiza `specs/progress.md`.
- Lo terminado lo registra git. Un error que se repite se convierte en una línea de este archivo, en una skill o, si puede costar datos, dinero o seguridad, en un hook o una regla del gate (`specs/orden_spec.md` §8).

## Harness

- Qué revisa el gate (rutas, reglas, umbrales) está en `pyproject.toml`. `scripts/`, `.claude/` y `.github/workflows/` se copian igual a otros proyectos.
- Dependencias: `requirements.txt` para ejecutar y `requirements-dev.txt` (la incluye) para el gate.
- `tests/test_harness.py` prueba que los hooks bloquean lo que prometen.
- Commits y push los hace la persona. No los ejecutes si no te lo pidió para ese cambio: prepara los archivos y propón el mensaje. Si lo intentas, las reglas `ask` de `settings.json` le piden confirmación también en modo auto ([permisos de Claude Code](https://code.claude.com/docs/en/permissions); comprobado en la práctica el 2026-11-11), y `validar_comando.py` cubre las variantes que esas reglas no ven.
- En cada PR, `.github/workflows/revisor.yml` ejecuta `scripts/revisor_ci.py`. Primero un filtro determinista rechaza el título, la descripción o los `CA-N` que intentan dirigir la revisión (órdenes al revisor, comentarios HTML, caracteres invisibles). Después la Decisions API de Azure OpenAI (deployment `gpt-6-luna`) responde preguntas de sí o no: una por cada `CA-N` de la spec más si respeta el «No tocar» de `plan.md` y si `review.md` tiene la evidencia de `validation.md` (o una sobre lo pedido, si no hay feature), y una por cada riesgo fijo. La feature se detecta por los archivos de `[<proyecto>/]specs/features/` que toca el PR o por su rama `feature/NN-nombre`. El código decide con un umbral, así que los detalles de estilo no tumban un PR. Si algo falla y está definida `AZURE_OPENAI_EVALUATOR_EXPLAINER_DEPLOYMENT` (p. ej. `gpt-5.2`), ese modelo explica en el Summary por qué falló cada pregunta, sin cambiar la decisión. Variables: `AZURE_OPENAI_EVALUATOR_*` (endpoint y clave como *secrets*, deployments como *variables* del repo). Corre con `pull_request_target`, así que workflow y revisor salen siempre de `main`; por eso nunca debe ejecutar código del PR, solo leerlo con git. Solo es obligatorio si `gate` y `revisor` son *required checks* de `main` (Settings → Rules). En `OlmeDK/summa_framework_v0` no lo son: GitHub no impide el merge aunque `gate` o `revisor` fallen (plan gratuito, repo privado), así que la regla la cumple quien mergea: no se mergea hasta que los dos estén en verde.
- El mismo revisor se ejecuta en local para que evalúe un modelo distinto del que implementa. Lo lanza la persona, nunca un agente, porque necesita las credenciales del `.env`:
  - antes, commitear la feature: solo lee lo commiteado;
  - cargar las variables `AZURE_OPENAI_EVALUATOR_*` en la sesión, porque el script no lee `.env`: `Get-Content .env | ForEach-Object { if ($_ -match '^\s*(AZURE_OPENAI_EVALUATOR_\w+)\s*=\s*(.*?)\s*$') { Set-Item "env:$($Matches[1])" $Matches[2].Trim('"', "'") } }`;
  - `REVISOR_BASE=<rama de la que sale la feature>`, `REVISOR_RAMA=feature/NN-nombre` y `python scripts/revisor_ci.py | Tee-Object revisor_local.txt`. `revisor_local.txt` está en `.gitignore`: el agente lo lee desde ahí y lo copia al `review.md` de la feature, que es el registro versionado.

  Termina en `[REVISOR] accept` o `revise`. Con `accept`, la feature se cierra en su rama (`/specs cerrar NN-nombre`) antes de abrir el PR. Así el PR ya lleva el cierre y se puede mergear en cuanto pasa CI. Si CI da `revise`, se corrige en la misma rama.
