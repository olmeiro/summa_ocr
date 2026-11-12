# Tech-stack — Framework de agentes conversacionales (repo-agente-conversacional)

> Constitución. Define el **marco técnico común**. Cualquier desviación se registra en [[decisions]] o en `replanning/`.

**Fuentes**: SyN y BaseRef (ver [[mission]]), el harness de este repo y decisiones de la persona del 2026-11-12.

---

## 1. Lenguaje y framework

- **Lenguaje y versión**: Python, la misma versión mínima que `repo-libreria` (PENDIENTE allí).
- **Framework**: FastAPI para la API HTTP (decisión de la persona). LangGraph para la orquestación, a través de la librería (SyN, etapa 6).
- **Librería del framework**: `repo-libreria` con su extra del agente, en una versión fija instalada desde el feed de Azure Artifacts de SUMMA (decisión de la persona).
- **Gestor de dependencias**: `uv` con `requirements.txt` (ejecución) y `requirements-dev.txt` (gate), como define `AGENTS.md`.

## 2. Convenciones de código

- Lint, formato, tipos y tests los verifica el gate: `python scripts/gate.py`, configurado en `pyproject.toml` (ruff con reglas `FAST`, `ASYNC` y `S`; mypy en modo estricto; pytest). Al crear `app/`, se añade a `[tool.mypy] files`.
- La capa API no tiene lógica de negocio: valida, delega en el agente y responde (`BaseRef/agent/docs/architecture.md`, "Capa API").
- El agente se crea en un solo punto, que usan los endpoints y cualquier script. `[inferido]` de `BaseRef/agent/app/core/agent_builder.py`.
- Endpoints `async`; nada bloqueante dentro del event loop (regla `ASYNC` del gate).
- Imports, `config_<ambiente>.yaml`, prompts y pipelines usan nombres de SUMMA. Nada importa paquetes de la base ni conserva sus nombres (decisión de la persona, 2026-11-12).
- Docstrings, mensajes de error y commits en español (`orden_spec.md` §11). El formato de errores HTTP se decide en la feature que lo introduce y se registra en [[decisions]].

## 3. Estructura de módulos

SyN, etapa 6, pide `app/`, `main.py`, `settings.py`, `requirements.txt` y `Dockerfile`. La subdivisión es `[inferido]` de `BaseRef/agent/docs/architecture.md`:

```text
app/
├─ main.py         # crea la app FastAPI, middleware y ciclo de vida
├─ api/v1/         # endpoints: conversación, sesiones y salud; esquemas de request/response
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

- **Conversación**: endpoint que recibe un mensaje de una sesión y devuelve la respuesta con sus fuentes. Lo consume el canal (Teams vía Azure Bot Service; SyN, etapa 8).
- **Sesiones**: crear, listar y leer el historial de una sesión (`BaseRef/agent/docs/architecture.md`, `sessions.py`).
- **Salud**: endpoints de vida y disponibilidad para las validaciones posteriores al despliegue (SyN, etapa 6).
- **Contrato**: el OpenAPI que genera FastAPI. Las rutas concretas se fijan en cada feature.

## 5. Dependencias

### Base

- La librería del framework, con su extra del agente: trae LangGraph, Azure OpenAI, AI Search, Cosmos DB, Key Vault, JWT y MCP.
- `fastapi`, un servidor ASGI y `pydantic-settings` para las variables de entorno (`BaseRef/agent/requirements.txt`).
- Las versiones se fijan en la feature 01.

### Añadidas por features

Ninguna todavía.

## 6. Servicios externos

| Servicio | Uso | Autenticación |
|---|---|---|
| Azure OpenAI (vía Azure AI Foundry) | LLM del orquestador y embeddings de la consulta | Según el `tech-stack.md` §6 de `repo-libreria`. PENDIENTE: ¿qué deployments de chat y embeddings? |
| Azure AI Search | Recuperación sobre los índices de `repo-workflow` | Ídem |
| Azure Cosmos DB | Historial de conversación por sesión | Ídem |
| Azure Key Vault | Secretos referenciados desde `config_<ambiente>.yaml` | PENDIENTE: ¿identidad administrada del Container App? |
| Azure Container Registry | Imágenes del agente | Service connection de Azure DevOps |
| Azure Container Apps | Hosting del backend (decisión de la persona) | — |
| Azure Artifacts | Instalación de la librería en el build | Service connection de Azure DevOps |
| Azure Bot Service + Microsoft Teams | Canal con el usuario final | App Registration con permisos de Microsoft Graph (SyN, etapa 0) |

## 7. Entornos

| Entorno | Recursos | Notas |
|---|---|---|
| dev | Grupo de recursos transversal de desarrollo, desplegado por la IaC transversal (SyN, etapa 1) | Desarrollo y pruebas. PENDIENTE: nombres de recursos |
| prod | Grupo de recursos transversal de producción (SyN, etapa 1) | Atiende a los usuarios finales. PENDIENTE: nombres de recursos |

## 8. Configuración y secretos

- Variables de entorno mínimas en `app/core/settings.py` (ambiente y ruta del YAML). El resto va en `config/config_<ambiente>.yaml`, con los secretos referenciados por nombre en Key Vault y resueltos por la librería. `[inferido]` de `BaseRef/agent/docs/architecture.md` (`APP_CONFIG_PATH`, `${KV-*}`).
- En local, `.env` fuera de git. Los agentes no leen ni editan ningún `.env*`: cada variable nueva la añade la persona a `.env.template` (`AGENTS.md`).

## 9. Seguridad

- **Autenticación**: middleware que valida tokens JWT en cada petición con el validador OIDC de la librería (SyN, etapa 6). PENDIENTE: ¿emisor y audiencia del token (Entra ID, Bot Service)?
- **Autorización**: PENDIENTE: ¿se restringen las respuestas según el usuario o el área que pregunta, o todos ven todo el índice?
- **Sin endpoints de depuración en producción**: la base trae un emisor de tokens para desarrollo (`BaseRef/agent/docs/architecture.md`, `auth.py`); aquí no se incluye.
- **Validación de entrada**: modelos de FastAPI en cada endpoint; nada del usuario llega sin validar a filtros de búsqueda ni a herramientas.
- **Prompt injection**: se prueba antes de producción (SyN, etapa 8).
- **Red**: VNet, subredes, Service Endpoints y NSG de la IaC transversal (SyN, etapa 1).
- **Datos sensibles**: contratos e historial de conversación; ver retención en [[mission]] §7.

## 10. Observabilidad

PENDIENTE (decisión de la persona, 2026-11-12): ¿destino de logs, trazas y métricas del agente, y se registran tokens y costo por consulta? La base usa OpenTelemetry con exportación a consola u OTLP según el ambiente (`BaseRef/agent/docs/observability.md`).

## 11. Testing

- **Unitarias**: pytest dentro del gate, con los dobles de prueba de la librería; nada llama a Azure.
- **Integración o contrato**: contra los servicios de dev. PENDIENTE: ¿qué features exigen prueba de integración?
- **Humo en el entorno desplegado**: validación posterior a cada despliegue en dev y prod (SyN, etapa 6).
- **Evidencia aceptada para cerrar una feature**: PENDIENTE: ¿basta el gate local o se exige humo en dev para las features que tocan servicios de Azure?

## 12. CI/CD y despliegue

- **Plataforma**: Azure DevOps, para repos y pipelines (decisión de la persona). El gate y el revisor del harness se portan a Azure Pipelines al mover el harness.
- **Pipelines** (SyN, etapa 6; `BaseRef/agent/docs/deployment.md`):
  - build de la imagen Docker (instalando la librería desde el feed) y publicación en Azure Container Registry;
  - despliegue automático en Azure Container Apps (dev → prod);
  - triggers por rama;
  - validación posterior al despliegue y rollback si falla.
  - Variables por ambiente en archivos del pipeline.
- **Ramas**: el harness usa `feature/NN-nombre` → `main`; la base usa `Integration` → `master`; SyN, etapa 5, habla de feature → develop → prod. PENDIENTE: ¿qué modelo de ramas se usa?
- **Aprobación de producción**: PENDIENTE: ¿quién aprueba el paso a prod?

## Relación con otros documentos

- [[mission]] — el porqué que justifica este stack.
- [[alcance-inicial]] — dependencias externas y punto de partida.
- [[roadmap]] — en qué orden entran estos componentes.
- [[decisions]] — decisiones técnicas que complementan este documento.
