# Roadmap — Framework de agentes conversacionales (repo-agente-conversacional)

> Constitución. Secuencia de features pequeñas, implementables y verificables, con su estado.

Derivado de [[mission]], [[alcance-inicial]] y SyN, etapa 6. `LIB-NN` es la feature NN del roadmap de `repo-libreria`.

---

## 1. Principios de secuenciación

1. **Base antes que features**: configuración, contratos y el gate en verde van primero.
2. **La primera feature es manejable, no la más riesgosa**: sirve para probar el flujo y la arquitectura.
3. **Cada feature deja el sistema funcionando** y es verificable por sí sola.
4. **Replanning entre fases**: se revisa si el plan sigue siendo válido.
5. **La plantilla no reimplementa la librería**: si falta una capacidad genérica, se pide como feature de `repo-libreria`.
6. **El contrato del índice se acuerda con `repo-workflow` antes de la feature 07.** Su forma es el esquema de definición del índice de la librería (LIB-11).

## 2. Fases

### Fase 0 — Constitución

`mission`, `tech-stack`, `alcance-inicial` y este roadmap. **Salida**: base documental versionada.

### Fase 1 — Servicio base

API FastAPI con configuración, autenticación y sesiones. **Salida**: el servicio arranca en local y en contenedor, carga su YAML con secretos de Key Vault, rechaza peticiones sin un JWT de Bot Framework válido y guarda y recupera el historial de una sesión; gate en verde.

### Fase 2 — Agente, herramientas y canal

Conversación, entidades, herramienta RAG y canal Teams. **Salida**: un mensaje enviado desde Teams pasa por el agente, invoca la herramienta RAG contra un índice de prueba y responde con citas; una herramienta propia se añade en `app/agent/` sin tocar el resto.

### Fase 3 — Despliegue y adopción

Pipelines de Azure DevOps y guía de onboarding. **Salida**: la plantilla se despliega en dev y prod desde Azure DevOps, y un repo de caso de uso puede clonarla siguiendo la guía.

## 3. Features

| ID | Nombre | Fase | Depende de | Estado | Carpeta |
|---|---|---|---|---|---|
| 01 | esqueleto-api: app FastAPI (`main.py`, `settings.py`), endpoints de salud, `Dockerfile`, `app/` en el gate | 1 | — | accepted | `features/01-esqueleto-api/` |
| 02 | configuracion: `config_<ambiente>.yaml` con referencias a Key Vault, cargado con la librería | 1 | 01, LIB-03 | not_started | `features/02-configuracion/` |
| 03 | auth-jwt: middleware que valida el JWT de Bot Framework con el validador de la librería y rechaza sin token válido | 1 | 02, LIB-13 | not_started | `features/03-auth-jwt/` |
| 04 | sesiones: la sesión nace con el primer mensaje; endpoints para listar sesiones y leer su historial en Cosmos DB, con 90 días de retención; cada usuario accede solo a las suyas | 1 | 03, LIB-14 | not_started | `features/04-sesiones/` |
| 05 | conversacion: endpoint de mensaje, punto único de creación del agente (ciclo modelo ↔ herramientas, DEC-003 de la librería), prompt Jinja y puntos de extensión | 2 | 04, LIB-15 | not_started | `features/05-conversacion/` |
| 06 | entidades-consulta: configuración de las entidades que se identifican antes de invocar herramientas | 2 | 05, LIB-16 | not_started | `features/06-entidades-consulta/` |
| 07 | rag: herramienta RAG configurada (índice, filtros y citas) y respuesta con fuentes en el contrato del endpoint | 2 | 06, LIB-17 | not_started | `features/07-rag/` |
| 08 | canal-teams: adaptador de Bot Framework que recibe las actividades de Teams y responde con el texto y las fuentes | 2 | 07 | not_started | `features/08-canal-teams/` |
| 09 | cicd-azure-devops: build con la librería del feed, push a ACR, despliegue en Container Apps dev → prod, triggers, validación y rollback | 3 | 01, LIB-04 | not_started | `features/09-cicd-azure-devops/` |
| 10 | onboarding: documentación técnica y guía para crear un caso de uso desde la plantilla | 3 | 08, 09 | not_started | `features/10-onboarding/` |

Estados: `not_started → in_progress → passing → accepted` (ver [[orden_spec]] §6). Una feature solo pasa a `accepted` con el veredicto `accept` del revisor.

- La feature 09 también depende de que la IaC transversal haya desplegado dev; si eso llega antes, puede adelantarse a la fase 1.
- La feature 08 también depende de la App Registration del bot y del recurso de Azure Bot Service con el canal Teams (TI de SUMMA; SyN, etapa 0).
- MCP salió del roadmap el 2026-11-13 (decisión de la persona); entra por replanning.
- Mientras no exista el feed (LIB-04), la librería se instala desde una ruta local en desarrollo.

## 4. Punto de partida de cada feature

Qué ofrece la base para cada feature y qué debe resolver su spec. Se usa como guía de diseño, sin copiar código ([[mission]]). Las rutas sin prefijo son de `BaseRef/agent/`. Para la capacidad de librería de cada feature, ver el §4 del roadmap de `repo-libreria`.

| ID | Referencia | Lo que cambia respecto a la referencia |
|---|---|---|
| 01 | `app/main.py`, `app/core/settings.py:24-87`, `app/api/v1/health.py`, `Dockerfile` | Sirven de guía `/health`, `/ready` y `/live` (`health.py:14-44`), las variables con prefijo `APP_`, la imagen `python:3.12-slim` con usuario sin privilegios y `HEALTHCHECK` (`Dockerfile:4`, `58`, `68`). No se trae: `debug` activo por defecto (`settings.py:45-46`), CORS abierto con credenciales (`settings.py:72`, `main.py:43-45`), `/metrics` (`health.py:47`) ni el driver ODBC de la herramienta SQL (`Dockerfile:28`). La base recibe la credencial del feed como `ARG` (`Dockerfile:6`), que queda en el historial de la imagen. |
| 02 | `app/core/settings.py:95-121`, `config/config_qa.yaml`, `config/config_prod.yaml` | El YAML se elige con `APP_CONFIG_PATH`. De sus secciones no se traen `observability.alerts`, `evaluation`, A2A ni SQL. Para llegar a Key Vault la base usa un service principal por variables de entorno (`Pipeline/variables/qa-vars.yml:12`). |
| 03 | `app/core/dependencies.py:61-70`, `192-261` | Es una dependencia por endpoint, no un middleware global, que es lo que pide SyN. Valida tokens de Entra ID del usuario; aquí, los de Bot Framework. Con la autenticación desactivada devuelve un usuario administrador falso (`dependencies.py:244-252`): no se trae. Tampoco el emisor de tokens de desarrollo (`app/api/v1/auth.py`, `main.py:60`). El usuario sale del `oid` del token (`BaseRef/core/security/authentication.py:116`). |
| 04 | `app/api/v1/sessions.py:22-112`, `app/api/v1/schemas.py` | Crear, listar y leer una sesión y sus mensajes; responde 404 si no existe y 403 si es de otro usuario (`sessions.py:81-84`). Aquí no hay endpoint de crear: la sesión nace con el primer mensaje. No se trae el voto (`app/api/v1/chat.py:77-119`). |
| 05 | `app/api/v1/chat.py:27-70`, `app/core/agent_builder.py:28-196`, `app/agent/tools.py`, `app/agent/graph.py`, `config/prompts/system_prompt.j2` | Su respuesta no lleva fuentes (`schemas.py:18-22`). Exige que la sesión exista (`chat.py:44-45`); aquí se crea si falta, como hace su librería (`BaseRef/cognitive/agents/implementation.py:87-96`). Devuelve al cliente el texto de la excepción (`chat.py:70`). El prompt se renderiza una vez al arrancar (`agent_builder.py:69-79`). El grafo propio se activa con una clave de configuración (`agent_builder.py:180`). |
| 06 | Sin referencia en la base | Diseño nuevo desde SyN, etapa 6. |
| 07 | `config/config_qa.yaml:100-106` | Configura índice, `top_k` y tipo de búsqueda; no hay filtros ni campos de cita o enlace. |
| 08 | Sin referencia en la base | Diseño nuevo desde SyN, etapa 8: el adaptador traduce la actividad de Teams (conversación, usuario, texto) al endpoint de conversación y devuelve texto y fuentes. Las tarjetas adaptativas con el enlace al documento son del caso de uso. |
| 09 | `Pipeline/main-pipeline.yml`, `Pipeline/variables/*.yml`, `docs/deployment.md` | El pipeline solo declara ramas y variables por ambiente (registro, service connections, Container App, grupo de recursos y ruta del YAML); sus pasos están en una plantilla externa que no está en `project-context/`: se escriben desde cero. |
| 10 | `docs/`: `overview`, `getting-started`, `configuration`, `customization`, `api-reference`, `deployment` y `observability` | Sirve de índice de temas. |

## 5. Cierre del roadmap

- Todas las features en `accepted`.
- El repo del caso de uso Control Doc, clonado de esta plantilla, responde en dev con la herramienta RAG sobre el índice real de `repo-workflow`.
- Los objetivos medibles de [[mission]] §6 tienen umbral y se cumplen.
