# Roadmap — Librería del framework de IA (repo-libreria)

> Constitución. Secuencia de features pequeñas, implementables y verificables, con su estado.

Derivado de [[mission]], [[alcance-inicial]] y SyN (etapas 4 a 6). Las plantillas citan estas features como `LIB-NN`.

---

## 1. Principios de secuenciación

1. **Base antes que features**: configuración, contratos y el gate en verde van primero.
2. **La primera feature es manejable, no la más riesgosa**: sirve para probar el flujo y la arquitectura.
3. **Cada feature deja el sistema funcionando** y es verificable por sí sola: termina con una versión publicable.
4. **Replanning entre fases**: se revisa si el plan sigue siendo válido.
5. **El orden lo marcan las plantillas**: primero lo que necesita el recorrido mínimo del workflow (documento → índice) y después lo del agente.
6. **Cada capacidad nace con su interfaz y su doble de prueba**, para que las plantillas puedan probar sin Azure.

## 2. Fases

### Fase 0 — Constitución

`mission`, `tech-stack`, `alcance-inicial` y este roadmap. **Salida**: base documental versionada.

### Fase 1 — Paquete base

Estructura, configuración, secretos y publicación. **Salida**: la versión `0.1.0` está publicada en el feed. Instalada con **solo** un extra en un entorno limpio, importa los módulos de ese consumidor ([[decisions]] DEC-001) y carga un YAML con un secreto de Key Vault.

### Fase 2 — Servicios para el workflow

Trazabilidad, LLM y embeddings, extracción, chunking, búsqueda vectorial y fuentes HTTP. **Salida**: con solo la librería se puede llevar un documento de prueba a un índice de AI Search, con trazas de la ejecución.

### Fase 3 — Piezas del agente

Autenticación, memoria, grafo, entidades, herramienta RAG y MCP. **Salida**: con solo la librería se arma un agente que valida el JWT, recuerda la sesión, invoca la herramienta RAG y responde con fuentes.

## 3. Features

| ID | Nombre | Fase | Depende de | Estado | Carpeta |
|---|---|---|---|---|---|
| 01 | esqueleto-paquete: `pyproject.toml`, `src/`, extras, build de la wheel, humo por extra y test de fronteras de import (DEC-001) | 1 | — | not_started | `features/01-esqueleto-paquete/` |
| 02 | config-loader: esquemas pydantic y loader YAML por ambiente | 1 | 01 | not_started | `features/02-config-loader/` |
| 03 | secretos-identidad: credenciales de Azure y resolución de referencias a Key Vault en el loader | 1 | 02 | not_started | `features/03-secretos-identidad/` |
| 04 | publicacion-feed: pipeline de Azure DevOps (gate, build y publicación en el feed) | 1 | 01 | not_started | `features/04-publicacion-feed/` |
| 05 | trazabilidad-ejecuciones: logger y registro de ejecución con persistencia en Unity Catalog | 2 | 02 | not_started | `features/05-trazabilidad-ejecuciones/` |
| 06 | llm-embeddings: clientes de Azure OpenAI para chat y embeddings | 2 | 03 | not_started | `features/06-llm-embeddings/` |
| 07 | extraccion-content-understanding: análisis de binario a markdown y campos con confianza y página | 2 | 03 | not_started | `features/07-extraccion-content-understanding/` |
| 08 | chunking: estrategias por tokens, por estructura y semántica, con lineamientos | 2 | 06 | not_started | `features/08-chunking/` |
| 09 | busqueda-vectorial: índice desde su definición, upsert, borrado y consulta híbrida con filtros | 2 | 03 | not_started | `features/09-busqueda-vectorial/` |
| 10 | fuentes-http: cliente genérico con auth, paginación, reintentos y rate limit | 2 | 03 | not_started | `features/10-fuentes-http/` |
| 11 | auth-jwt: validador OIDC (emisor, audiencia y JWKS) | 3 | 02 | not_started | `features/11-auth-jwt/` |
| 12 | memoria-cosmos: historial y sesiones en Cosmos DB | 3 | 03 | not_started | `features/12-memoria-cosmos/` |
| 13 | grafo-agente: planner + executor, registro de herramientas y prompt Jinja | 3 | 06 | not_started | `features/13-grafo-agente/` |
| 14 | entidades-consulta: identificación de entidades antes de invocar herramientas | 3 | 13 | not_started | `features/14-entidades-consulta/` |
| 15 | herramienta-rag: consulta al índice con filtros y fuentes para citar | 3 | 09, 13 | not_started | `features/15-herramienta-rag/` |
| 16 | cliente-mcp: herramientas de servidores MCP en el registro del agente | 3 | 13 | not_started | `features/16-cliente-mcp/` |

Estados: `not_started → in_progress → passing → accepted` (ver [[orden_spec]] §6). Una feature solo pasa a `accepted` con el veredicto `accept` del revisor.

La feature 04 depende de que exista el feed. Mientras tanto, las plantillas pueden instalar la librería desde una ruta local en desarrollo.

## 4. Cierre del roadmap

- Todas las features en `accepted` y publicadas en el feed.
- `repo-workflow` y `repo-agente-conversacional` usan una versión publicada de la librería, sin código duplicado de ella.
- Los objetivos medibles de [[mission]] §6 tienen umbral y se cumplen.
