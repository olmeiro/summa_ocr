# Alcance inicial — Framework de agentes conversacionales (repo-agente-conversacional)

> Constitución. Define qué entra y qué no, de qué depende el proyecto y desde dónde arranca.

**Fuentes**: SyN y BaseRef (ver [[mission]]) y decisiones de la persona del 2026-11-12.

---

## 1. Posición del componente

```text
Usuario ─► Microsoft Teams ─► Azure Bot Service ─► [ API del agente: este repo, en Container Apps ]
                                                         │  usa la librería repo-libreria (feed)
                       ┌─────────────────────────────────┼──────────────────────────┐
                       ▼                                 ▼                          ▼
             Azure OpenAI (AI Foundry)          Azure AI Search             Azure Cosmos DB
             LLM y embeddings de consulta       índices publicados          historial por sesión
                                                por repo-workflow
                       Azure Key Vault (secretos) · servidores MCP (herramientas externas)
```

Cada caso de uso clona este repo y despliega su propia instancia (SyN, etapa 7).

## 2. Alcance funcional

### Entra

La plantilla aporta endpoints, configuración y puntos de extensión. La lógica común la entrega `repo-libreria` (decisión de la persona). Lo pide SyN, etapa 6, salvo donde se indica:

- **Estructura base**: `app/`, `main.py`, `settings.py`, `requirements.txt` y `Dockerfile`, con la librería en versión fija.
- **Configuración**: `config/config_<ambiente>.yaml` con secretos referenciados en Key Vault.
- **Autenticación**: middleware que valida tokens JWT y rechaza las peticiones sin token válido.
- **Sesiones**: endpoints para crear, listar y leer el historial, persistido en Cosmos DB. Cada usuario accede solo a sus sesiones. `[inferido]` de `BaseRef/agent/app/api/v1/sessions.py:81-84`.
- **Conversación**: endpoint que recibe un mensaje, ejecuta el agente (planner + executor) con el historial de la sesión y devuelve la respuesta con sus fuentes como datos (documento, página y enlace), para que el canal arme la cita (SyN, arquitectura §3 y etapa 8).
- **Prompt principal** en `config/prompts/`, parametrizable por caso de uso.
- **Identificación de entidades** antes de invocar herramientas, configurable por caso de uso.
- **Herramienta RAG** configurada desde el YAML: índice, filtros por metadatos y campos de cita y enlace (SyN, arquitectura §3).
- **Puntos de extensión** en `app/agent/` para herramientas y grafo propios del caso de uso. `[inferido]` de `BaseRef/agent/docs/architecture.md`, "Capa Agente".
- **Servidores MCP** declarados en la configuración (SyN, etapa 1).
- **Salud**: endpoints de vida y disponibilidad.
- **Pipelines de Azure DevOps**: imagen Docker en Container Registry, despliegue en Container Apps (dev → prod), triggers por rama, validación posterior al despliegue y rollback.
- **Documentación** técnica y guía de onboarding para nuevos casos de uso (SyN, etapa 1).

### No entra

- **Lógica genérica**: grafo, memoria, clientes de Azure, validador JWT y cliente MCP están en `repo-libreria`.
- **Lo que hace `repo-workflow`**: ingesta, procesamiento, extracción, chunking, embeddings de documentos e indexación. Tampoco crear o actualizar índices.
- **El caso de uso Control Doc**: prompt de contratos, filtros por metadatos de contratos y citación al documento de Control Doc. Va en su propio repo, clonado de este (SyN, etapa 7; decisión de la persona).
- **La extensión de Teams** (App Manifest, configuración de Azure Bot Service, tarjetas adaptativas): es del caso de uso (SyN, etapa 8). PENDIENTE: ¿el adaptador del canal Bot Framework/Teams va en el framework para reutilizarlo, o en cada caso de uso? La base no lo trae.
- **Capacidades de la base que SyN no pide** (decisión de la persona; quedan para replanning):
  - voto de respuestas, A2A y herramienta SQL;
  - métricas Prometheus y alertas;
  - evaluación con golden set, fairness y ragas o deepeval, y endpoint de tokens de desarrollo;
  - el modo sin autenticación con usuario falso y el driver ODBC de su imagen.
- **Canales distintos de Teams**: web, móvil, WhatsApp (SyN, "Fuera de alcance").
- **Infraestructura como código de los recursos transversales** (SyN, etapa 1).
- **Pruebas de calidad de respuestas y de carga del caso de uso** (SyN, etapa 8).
- **Interpretación legal** y dashboards (SyN, "Fuera de alcance").

### Por decidir

- PENDIENTE: ¿una sesión nace con un endpoint propio antes del primer mensaje, como en la plantilla de la base (`BaseRef/agent/app/api/v1/chat.py:44-45`), o al primer mensaje con el identificador de conversación que traiga el canal? La librería de la base la crea si falta (`BaseRef/cognitive/agents/implementation.py:87-96`), así que sus dos capas no coinciden.
- El significado de "planner + executor" está como `PENDIENTE` en el alcance de `repo-libreria` (§2): el grafo de la base es un ciclo agente ↔ herramientas.

## 3. Dependencias externas

| Dependencia | Quién la provee | Entorno o recurso | Notas |
|---|---|---|---|
| Librería del framework, versión publicada | `repo-libreria` | Feed de Azure Artifacts | Ver la columna "Depende de" de [[roadmap]] |
| Suscripción Azure y grupo de recursos con permisos contributor | SUMMA | dev y prod | SyN, etapa 0 |
| Recursos transversales: Key Vault, AI Search, Cosmos DB, Container Registry, Container Apps Environment, AI Foundry, VNet | IaC transversal | dev y prod | SyN, etapa 1. PENDIENTE: ¿en qué repo y con qué herramienta vive la IaC? |
| Índices de Azure AI Search | `repo-workflow` | uno por caso de uso | Su esquema es el contrato entre las dos plantillas |
| Deployments de modelos (chat y embeddings) | AI Foundry de SUMMA | dev y prod | El modelo de embeddings debe ser el mismo con el que `repo-workflow` indexó |
| App Registration con permisos de Microsoft Graph para Teams | SUMMA | — | SyN, etapa 0 |
| Proyecto de Azure DevOps: repos, pipelines y service connections | SUMMA | — | Decisión de la persona |

## 4. Punto de partida

### Greenfield: activos heredados

- **Harness** (`scripts/`, `.claude/`, `specs/`, `AGENTS.md`): se mueve desde la raíz de `summa_ocr`; el gate y el revisor se portan a Azure Pipelines.
- **SyN**: arquitectura, alcance y plan de trabajo de referencia.
- **BaseRef**: guía de diseño, sin copiar código (decisión de la persona). Qué cambia en cada activo está en [[roadmap]] §4.

| Activo de referencia | Guía para |
|---|---|
| `BaseRef/agent/docs/architecture.md` | Capas API, core, agente y middleware; punto único de creación del agente |
| `BaseRef/agent/app/core/agent_builder.py:121-196` y `dependencies.py:78-170` | Creación del agente y ciclo de vida de los servicios |
| `BaseRef/agent/app/api/v1/` (`chat.py`, `sessions.py`, `health.py`, `schemas.py`) | Endpoints de conversación, sesiones y salud |
| `BaseRef/agent/app/core/settings.py` y `config/` | Settings por variables de entorno y YAML por ambiente |
| `BaseRef/agent/app/agent/` (`tools.py`, `graph.py`) | Puntos de extensión del caso de uso |
| `BaseRef/agent/Dockerfile`, `Pipeline/` y `docs/deployment.md` | Imagen, pipeline a ACR y Container Apps, y variables por ambiente |

## 5. Coordinación con otros equipos o sistemas

- **`repo-libreria`**: cada feature que necesita una capacidad nueva depende de la feature `LIB-NN` que la entrega y de su publicación.
- **`repo-workflow`**: contrato del índice (campos, campo de enlace al documento, página, campos filtrables, modelo de embeddings) antes de la feature 07. Se acuerda como la definición del índice que valida la librería (LIB-11) y que las dos plantillas copian en su configuración.
- **Plataforma e IaC**: nombres de recursos, identidades administradas, red y permisos por ambiente.
- **TI de SUMMA**: App Registration, permisos de Graph y publicación de la app en Teams.

## 6. Principios del alcance

- Entra lo que sirve a cualquier agente. Lo específico de un dominio va al repo del caso de uso, y lo genérico reutilizable fuera de la API va a `repo-libreria`.
- Nada que obligue a modificar `repo-workflow`, Control Doc ni la IaC transversal sin acordarlo antes.
- Teams es el único canal de este alcance.

## Relación con otros documentos

- [[mission]] — por qué existe el proyecto.
- [[tech-stack]] — con qué se construye.
- [[roadmap]] — en qué orden se entrega este alcance.
