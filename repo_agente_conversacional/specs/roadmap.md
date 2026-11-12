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
6. **El contrato del índice se acuerda con `repo-workflow` antes de la feature 07.**

## 2. Fases

### Fase 0 — Constitución

`mission`, `tech-stack`, `alcance-inicial` y este roadmap. **Salida**: base documental versionada.

### Fase 1 — Servicio base

API FastAPI con configuración, autenticación y sesiones. **Salida**: el servicio arranca en local y en contenedor, carga su YAML con secretos de Key Vault, rechaza peticiones sin JWT válido y guarda y recupera el historial de una sesión; gate en verde.

### Fase 2 — Agente y herramientas

Conversación, entidades, herramienta RAG y MCP. **Salida**: una conversación pasa por el agente, invoca la herramienta RAG contra un índice de prueba y responde con citas; una herramienta propia se añade en `app/agent/` sin tocar el resto.

### Fase 3 — Despliegue y adopción

Pipelines de Azure DevOps y guía de onboarding. **Salida**: la plantilla se despliega en dev y prod desde Azure DevOps, y un repo de caso de uso puede clonarla siguiendo la guía.

## 3. Features

| ID | Nombre | Fase | Depende de | Estado | Carpeta |
|---|---|---|---|---|---|
| 01 | esqueleto-api: app FastAPI (`main.py`, `settings.py`), endpoints de salud, `Dockerfile`, `app/` en el gate | 1 | — | not_started | `features/01-esqueleto-api/` |
| 02 | configuracion: `config_<ambiente>.yaml` con referencias a Key Vault, cargado con la librería | 1 | 01, LIB-03 | not_started | `features/02-configuracion/` |
| 03 | auth-jwt: middleware que valida JWT y rechaza sin token válido | 1 | 02, LIB-11 | not_started | `features/03-auth-jwt/` |
| 04 | sesiones: endpoints de sesiones e historial en Cosmos DB | 1 | 03, LIB-12 | not_started | `features/04-sesiones/` |
| 05 | conversacion: endpoint de mensaje, punto único de creación del agente, prompt Jinja y puntos de extensión | 2 | 04, LIB-13 | not_started | `features/05-conversacion/` |
| 06 | entidades-consulta: configuración de las entidades que se identifican antes de invocar herramientas | 2 | 05, LIB-14 | not_started | `features/06-entidades-consulta/` |
| 07 | rag: herramienta RAG configurada (índice, filtros y citas) y respuesta con fuentes | 2 | 06, LIB-15 | not_started | `features/07-rag/` |
| 08 | mcp: servidores MCP declarados en la configuración | 2 | 05, LIB-16 | not_started | `features/08-mcp/` |
| 09 | cicd-azure-devops: build con la librería del feed, push a ACR, despliegue en Container Apps dev → prod, triggers, validación y rollback | 3 | 01, LIB-04 | not_started | `features/09-cicd-azure-devops/` |
| 10 | onboarding: documentación técnica y guía para crear un caso de uso desde la plantilla | 3 | 07, 08, 09 | not_started | `features/10-onboarding/` |

Estados: `not_started → in_progress → passing → accepted` (ver [[orden_spec]] §6). Una feature solo pasa a `accepted` con el veredicto `accept` del revisor.

- La feature 09 también depende de que la IaC transversal haya desplegado dev; si eso llega antes, puede adelantarse a la fase 1.
- Mientras no exista el feed (LIB-04), la librería se instala desde una ruta local en desarrollo.

## 4. Cierre del roadmap

- Todas las features en `accepted`.
- El repo del caso de uso Control Doc, clonado de esta plantilla, responde en dev con la herramienta RAG sobre el índice real de `repo-workflow`.
- Los objetivos medibles de [[mission]] §6 tienen umbral y se cumplen.
