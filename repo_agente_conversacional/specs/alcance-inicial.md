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
                       Azure Key Vault (secretos)
```

Cada caso de uso clona este repo y despliega su propia instancia (SyN, etapa 7).

## 2. Alcance funcional

### Entra

La plantilla aporta endpoints, configuración y puntos de extensión. La lógica común la entrega `repo-libreria` (decisión de la persona). Lo pide SyN, etapa 6, salvo donde se indica:

- **Estructura base**: `app/`, `main.py`, `settings.py`, `requirements.txt` y `Dockerfile`, con la librería en versión fija.
- **Configuración**: `config/config_<ambiente>.yaml` con secretos referenciados en Key Vault.
- **Autenticación**: middleware que valida los tokens de Bot Framework y rechaza las peticiones sin token válido.
- **Canal Teams**: adaptador de Bot Framework que recibe las actividades de Teams y responde en la conversación, reutilizable por todos los casos de uso (decisión de la persona, 2026-11-13).
- **Sesiones**: la sesión nace con el primer mensaje, con el identificador de conversación del canal (decisión de la persona, 2026-11-13); endpoints para listar sesiones y leer su historial, persistido en Cosmos DB con 90 días de retención. Cada usuario accede solo a sus sesiones. `[inferido]` de `BaseRef/agent/app/api/v1/sessions.py:81-84`.
- **Conversación**: endpoint que recibe un mensaje, ejecuta el agente (entidades y luego el ciclo modelo ↔ herramientas, DEC-003 de `repo-libreria`) con el historial de la sesión y devuelve la respuesta con sus fuentes como datos (documento, página y enlace), para que el canal arme la cita (SyN, arquitectura §3 y etapa 8).
- **Prompt principal** en `config/prompts/`, parametrizable por caso de uso.
- **Identificación de entidades** antes de invocar herramientas, configurable por caso de uso.
- **Herramienta RAG** configurada desde el YAML: índice, filtros por metadatos y campos de cita y enlace (SyN, arquitectura §3).
- **Puntos de extensión** en `app/agent/` para herramientas y grafo propios del caso de uso. `[inferido]` de `BaseRef/agent/docs/architecture.md`, "Capa Agente".
- **Salud**: endpoints de vida y disponibilidad.
- **Pipelines de Azure DevOps**: imagen Docker en Container Registry, despliegue en Container Apps (dev → prod), triggers por rama, validación posterior al despliegue y rollback.
- **Documentación** técnica y guía de onboarding para nuevos casos de uso (SyN, etapa 1).

### No entra

- **Lógica genérica**: grafo, memoria, clientes de Azure y validador JWT están en `repo-libreria`.
- **Servidores MCP**: fuera por ahora (decisión de la persona, 2026-11-13); entran por replanning.
- **Lo que hace `repo-workflow`**: ingesta, procesamiento, extracción, chunking, embeddings de documentos e indexación. Tampoco crear o actualizar índices.
- **El caso de uso Control Doc**: prompt de contratos, filtros por metadatos de contratos y citación al documento de Control Doc. Va en su propio repo, clonado de este (SyN, etapa 7; decisión de la persona).
- **Lo propio de cada app de Teams**: el App Manifest, el registro del bot en Azure Bot Service y las tarjetas adaptativas con el enlace al documento son del caso de uso (SyN, etapa 8). El adaptador genérico sí entra.
- **Capacidades de la base que SyN no pide** (decisión de la persona; quedan para replanning):
  - voto de respuestas, A2A y herramienta SQL;
  - métricas Prometheus, alertas, OpenTelemetry y medición de tokens o costo;
  - evaluación automática con golden set, fairness y ragas o deepeval, y endpoint de tokens de desarrollo (el golden set se evalúa a mano en QA);
  - el modo sin autenticación con usuario falso y el driver ODBC de su imagen;
  - filtrar las respuestas por usuario o área.
- **Canales distintos de Teams**: web, móvil, WhatsApp (SyN, "Fuera de alcance").
- **Infraestructura como código de los recursos transversales** (SyN, etapa 1).
- **Pruebas de calidad de respuestas y de carga del caso de uso** (SyN, etapa 8).
- **Interpretación legal** y dashboards (SyN, "Fuera de alcance").

### Decidido el 2026-11-13

- **Sesión**: nace con el primer mensaje, como la crea la librería de la base (`BaseRef/cognitive/agents/implementation.py:87-96`), y no con un endpoint previo como su plantilla (`BaseRef/agent/app/api/v1/chat.py:44-45`).
- **Orquestación**: entidades y luego el ciclo modelo ↔ herramientas (DEC-003 de `repo-libreria`).
- **Canal**: el adaptador de Teams entra en la plantilla; MCP sale.

## 3. Dependencias externas

| Dependencia | Quién la provee | Entorno o recurso | Notas |
|---|---|---|---|
| Librería del framework, versión publicada | `repo-libreria` | Feed de Azure Artifacts | Ver la columna "Depende de" de [[roadmap]] |
| Suscripción Azure y grupo de recursos con permisos contributor | SUMMA | dev y prod | SyN, etapa 0 |
| Recursos transversales: Key Vault, AI Search, Cosmos DB, Container Registry, Container Apps Environment, AI Foundry, VNet | IaC transversal | dev y prod | SyN, etapa 1. PENDIENTE (dueño: SUMMA): ¿en qué repo y con qué herramienta vive la IaC? |
| Índices de Azure AI Search | `repo-workflow` | uno por caso de uso | Su esquema es el contrato entre las dos plantillas |
| Deployments de modelos (chat y embeddings) | AI Foundry de SUMMA | dev y prod | El modelo de embeddings debe ser el mismo con el que `repo-workflow` indexó |
| App Registration del bot y recurso de Azure Bot Service, con el canal Teams | TI de SUMMA | dev y prod | SyN, etapas 0 y 8. Bloquea la feature 08 |
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
