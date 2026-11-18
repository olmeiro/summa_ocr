# Tech-stack — Framework de agentes conversacionales (repo-agente-conversacional)

> Constitución. Define el **marco técnico común**. Cualquier desviación se registra en [[decisions]] o en `replanning/`.

**Fuentes**: SyN y BaseRef (ver [[mission]]), el harness de este repo y decisiones de la persona del 2026-11-12 y 2026-11-13.

---

## 1. Lenguaje y framework

- **Lenguaje y versión**: Python 3.12, como `repo-libreria`; imagen base `python:3.12-slim` (decisión de la persona, 2026-11-13).
- **Framework**: FastAPI para la API HTTP (decisión de la persona). LangGraph para la orquestación, a través de la librería (SyN, etapa 6).
- **Librería del framework**: `summa-ai-framework` (`repo-libreria`) con su extra del agente, en una versión fija instalada desde el feed de Azure Artifacts de SUMMA (decisión de la persona).
- **Gestor de dependencias**: `uv` con `requirements.txt` (ejecución) y `requirements-dev.txt` (gate), como define `AGENTS.md`.

## 2. Convenciones de código

- Lint, formato, tipos y tests los verifica el gate: `python scripts/gate.py`, configurado en `pyproject.toml` (ruff con reglas `FAST`, `ASYNC` y `S`; mypy en modo estricto; pytest). Al crear `app/`, se añade a `[tool.mypy] files`.
- La capa API no tiene lógica de negocio: valida, delega en el agente y responde (`BaseRef/agent/docs/architecture.md`, "Capa API").
- El agente se crea en un solo punto, que usan los endpoints y cualquier script. `[inferido]` de `BaseRef/agent/app/core/agent_builder.py:121-196`. Los servicios se crean al arrancar la app y se cierran al apagarla (`BaseRef/agent/app/core/dependencies.py:78-170`).
- Endpoints `async`; nada bloqueante dentro del event loop (regla `ASYNC` del gate). La herramienta RAG de la base calcula el embedding de la consulta de forma síncrona (`BaseRef/cognitive/agents/tools/retrieval.py:83`).
- Los valores por defecto son los de producción: sin modo debug, sin documentación interactiva y sin CORS abierto. `[inferido]`: en la base `debug` viene activo y CORS acepta cualquier origen con credenciales (`BaseRef/agent/app/core/settings.py:45-46`, `72`). El canal llama de servidor a servidor.
- Un error interno responde con un mensaje genérico y deja el detalle en el log. `[inferido]`: el endpoint de conversación de la base devuelve el texto de la excepción (`BaseRef/agent/app/api/v1/chat.py:70`).
- Imports, `config_<ambiente>.yaml`, prompts y pipelines usan nombres de SUMMA. Nada importa paquetes de la base ni conserva sus nombres (decisión de la persona, 2026-11-12).
- Docstrings, mensajes de error y commits en español (`orden_spec.md` §11). El formato de errores HTTP se decide en la feature que lo introduce y se registra en [[decisions]].

## 3. Estructura de módulos

SyN, etapa 6, pide `app/`, `main.py`, `settings.py`, `requirements.txt` y `Dockerfile`. La subdivisión es `[inferido]` de `BaseRef/agent/docs/architecture.md`:

```text
app/
├─ main.py         # crea la app FastAPI, middleware y ciclo de vida
├─ api/v1/         # endpoints: conversación, sesiones y salud; esquemas de request/response
├─ channels/       # adaptador de Bot Framework / Teams
├─ core/           # settings, creación del agente e inyección de dependencias
├─ agent/          # puntos de extensión: herramientas propias y grafo propio
└─ middleware/     # autenticación y manejo global de errores
config/
├─ config_<ambiente>.yaml   # configuración por ambiente con referencias a Key Vault
└─ prompts/                 # prompt principal en Jinja
tests/
Dockerfile
requirements.txt
```

## 4. Interfaces expuestas

- **Canal Teams**: endpoint de mensajes de Bot Framework que recibe las actividades de Teams vía Azure Bot Service y responde en la conversación (decisión de la persona, 2026-11-13).
- **Conversación**: endpoint que recibe un mensaje y el identificador de conversación, y devuelve la respuesta con sus fuentes como datos (documento, página y enlace). Si la sesión no existe, se crea con ese identificador (decisión de la persona, 2026-11-13). Lo usan el adaptador de Teams y las pruebas. La respuesta de la base solo trae el texto (`BaseRef/agent/app/api/v1/schemas.py:18-22`).
- **Sesiones**: listar las sesiones del usuario y leer el historial de una (`BaseRef/agent/app/api/v1/sessions.py:55-112`). No hay endpoint para crearlas: nacen con el primer mensaje. Una sesión solo la lee y la usa su dueño.
- **Salud**: endpoints de vida y disponibilidad para las validaciones posteriores al despliegue (SyN, etapa 6).
- **Contrato**: el OpenAPI que genera FastAPI. Las rutas concretas se fijan en cada feature.

## 5. Dependencias

### Base

- La librería del framework, con su extra del agente: trae LangGraph, Azure OpenAI, AI Search, Cosmos DB, Key Vault y JWT.
- `fastapi`, un servidor ASGI y `pydantic-settings` para las variables de entorno (`BaseRef/agent/requirements.txt`).
- El SDK de Bot Framework para Python, para el adaptador de Teams; la base no lo trae y se fija en la feature 08.
- Las versiones se fijan en la feature 01.

### Añadidas por features

Ninguna todavía.

## 6. Servicios externos

| Servicio | Uso | Autenticación |
|---|---|---|
| Azure OpenAI (vía Azure AI Foundry) | LLM del orquestador y embeddings de la consulta. Los deployments los elige cada caso de uso en su configuración; el de embeddings es el del contrato del índice (decisión de la persona, 2026-11-13) | Clave de API en Key Vault (decisión de la persona, 2026-11-13) |
| Azure AI Search | Recuperación sobre los índices de `repo-workflow` | Ídem |
| Azure Cosmos DB | Historial de conversación por sesión | Ídem |
| Azure Key Vault | Claves de API de los servicios, referenciadas desde `config_<ambiente>.yaml` | PENDIENTE (dueño: plataforma): ¿identidad administrada del Container App para llegar a Key Vault? La base usa un service principal cuyo secreto inyecta el pipeline (`BaseRef/agent/Pipeline/variables/qa-vars.yml:12`) |
| Azure Container Registry | Imágenes del agente | Service connection de Azure DevOps |
| Azure Container Apps | Hosting del backend (decisión de la persona) | — |
| Azure Artifacts | Instalación de la librería en el build | Service connection de Azure DevOps |
| Azure Bot Service + Microsoft Teams | Canal con el usuario final; el adaptador vive en esta plantilla | App Registration del bot (SyN, etapa 0); tokens de Bot Framework (§9) |

## 7. Entornos

| Entorno | Recursos | Notas |
|---|---|---|
| dev | Grupo de recursos transversal de desarrollo (SyN, etapa 1) | Desarrollo y pruebas; recibe lo que entra a `develop` |
| prod | Grupo de recursos transversal de producción (SyN, etapa 1) | Atiende a los usuarios finales; recibe `main` |

PENDIENTE (dueño: plataforma): nombres de los recursos de cada ambiente.

## 8. Configuración y secretos

- Variables de entorno mínimas en `app/core/settings.py` (ambiente y ruta del YAML). El resto va en `config/config_<ambiente>.yaml`, con los secretos referenciados por nombre en Key Vault y resueltos por la librería. `[inferido]` de `BaseRef/agent/docs/architecture.md` (`APP_CONFIG_PATH`, `${KV-*}`).
- En local, `.env` fuera de git. Los agentes no leen ni editan ningún `.env*`: cada variable nueva la añade la persona a `.env.template` (`AGENTS.md`).

## 9. Seguridad

- **Autenticación**: middleware que valida en cada petición el JWT que firma Bot Framework (emisor de Bot Framework, audiencia = App ID del bot) con el validador OIDC de la librería (SyN, etapa 6) (decisión de la persona, 2026-11-13). Los endpoints de salud quedan fuera. El token identifica al servicio del canal; el usuario dueño de la sesión es el AAD object id que trae la actividad de Teams. La base lo tomaba del `oid` del token del usuario (`BaseRef/core/security/authentication.py:116`).
- **Autorización**: una sesión solo la lee y la usa su dueño: 404 si no existe y 403 si es de otro (`[inferido]` de `BaseRef/agent/app/api/v1/sessions.py:81-84`). Todos los usuarios con acceso a la app de Teams ven todo el índice; filtrar por área entra por replanning (decisión de la persona, 2026-11-13).
- **Sin modo sin autenticación ni endpoints de depuración**: la base trae un emisor de tokens para desarrollo (`BaseRef/agent/app/api/v1/auth.py`) y un usuario administrador falso cuando la autenticación está desactivada (`BaseRef/agent/app/core/dependencies.py:244-252`); aquí no se incluyen. En los tests se sustituye el validador por su doble.
- **Imagen**: la credencial del feed no se pasa como `ARG` del build, porque queda en el historial de la imagen (`BaseRef/agent/Dockerfile:6`). `[inferido]`
- **Validación de entrada**: modelos de FastAPI en cada endpoint; nada del usuario llega sin validar a filtros de búsqueda ni a herramientas.
- **Prompt injection**: se prueba antes de producción (SyN, etapa 8).
- **Red**: VNet, subredes, Service Endpoints y NSG de la IaC transversal (SyN, etapa 1).
- **Datos sensibles**: contratos e historial de conversación; el historial expira a los 90 días ([[mission]] §7).

## 10. Observabilidad

Solo logs del servicio por ahora: sin OpenTelemetry, Azure Monitor ni medición de tokens o costo (decisión de la persona, 2026-11-13). Cada respuesta deja en el log su latencia, con la que se mide el p95 de [[mission]] §6. La base usa OpenTelemetry con exportación a consola u OTLP (`BaseRef/agent/docs/observability.md`); entra por replanning.

## 11. Testing

- **Unitarias**: pytest dentro del gate, con los dobles de prueba de la librería; nada llama a Azure.
- **Integración o contrato**: contra los servicios de dev, en las features que tocan un servicio de Azure o el canal (decisión de la persona, 2026-11-13).
- **Humo en el entorno desplegado**: validación posterior a cada despliegue en dev y prod (SyN, etapa 6).
- **Evidencia aceptada para cerrar una feature**: el gate siempre, y humo en dev (una llamada real al endpoint, con su salida en `review.md`) para las features que tocan servicios de Azure (decisión de la persona, 2026-11-13).

## 12. CI/CD y despliegue

- **Plataforma**: Azure DevOps, para repos y pipelines (decisión de la persona). El gate y el revisor del harness se portan a Azure Pipelines al mover el harness.
- **Pipelines** (SyN, etapa 6; `BaseRef/agent/docs/deployment.md`). El pipeline de la base solo declara ramas y variables por ambiente; sus pasos están en una plantilla externa que no está en `project-context/` (`BaseRef/agent/Pipeline/main-pipeline.yml:21-30`), así que estos se escriben desde cero:
  - build de la imagen Docker (instalando la librería desde el feed) y publicación en Azure Container Registry;
  - despliegue automático en Azure Container Apps (dev → prod);
  - triggers por rama;
  - validación posterior al despliegue y rollback si falla.
  - Variables por ambiente en archivos del pipeline.
- **Ramas**: `feature/NN-nombre` → `develop`, que despliega en dev → `main`, que despliega en prod (decisión de la persona, 2026-11-13). La base usa `Develop`, `Integration` y `master` (`BaseRef/agent/Pipeline/main-pipeline.yml:1-20`).
- **Aprobación de producción**: el equipo de plataforma aprueba el paso a prod, con una aprobación por grupo en el pipeline (decisión de la persona, 2026-11-13).

## Relación con otros documentos

- [[mission]] — el porqué que justifica este stack.
- [[alcance-inicial]] — dependencias externas y punto de partida.
- [[roadmap]] — en qué orden entran estos componentes.
- [[decisions]] — decisiones técnicas que complementan este documento.
