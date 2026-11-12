# Misión — Librería del framework de IA (repo-libreria)

> Constitución. Define **por qué** existe el proyecto, para quién y bajo qué restricciones. No elige tecnología: eso va en [[tech-stack]].

**Fuentes** (todas en `project-context/`, fuera de git):
- **SyN**: `situacion y necesidad actual.pdf`.
- **BaseRef**: `ejemplo-framework/`, un framework de referencia construido para otro cliente. Se usa solo como guía de diseño: no se copia código (decisión de la persona, que confirmó el derecho a reutilizarlo, 2026-11-12). Rutas abreviadas:
  - `BaseRef/core/…` y `BaseRef/cognitive/…` son el `src/<paquete>/` de sus dos librerías;
  - `BaseRef/agent/…` y `BaseRef/workflow/…` son sus dos plantillas.
- **EjOCR**: `summa-documentos-ocr-main/summa-documentos-ocr-main/`, ejercicio de extracción con Content Understanding.
- Decisiones de la persona del 2026-11-12.

Lo marcado `[inferido]` espera confirmación. `repo_libreria/` es un nombre provisional.

---

## 1. Propósito

Librería Python versionada con las capacidades comunes del framework de IA de SUMMA, consumida por las dos plantillas, `repo-workflow` y `repo-agente-conversacional`:

- configuración, secretos e identidad;
- clientes de servicios cognitivos: modelos, embeddings, extracción de documentos, chunking y búsqueda vectorial;
- piezas de agentes: grafo, memoria, herramientas, autenticación y MCP;
- trazabilidad de ejecuciones.

Así cada plantilla, y cada caso de uso clonado de ella, solo aporta configuración y puntos de extensión.

## 2. Problema que resuelve

- Sin una pieza común, las dos plantillas duplicarían configuración, seguridad y clientes de Azure, y cada caso de uso clonado quedaría congelado en la versión del momento en que se clonó.
- La necesidad de fondo es la de SyN: evitar esfuerzos aislados y garantizar reutilización, gobernanza y coherencia tecnológica entre iniciativas (SyN, "Situación actual y necesidad").
- La base de referencia resuelve esto separando librerías versionadas de plantillas que las instalan desde un feed privado (`BaseRef/workflow/docs/architecture.md`, "Paquetes internos del framework"). SUMMA adopta ese patrón con una sola librería (decisión de la persona).

## 3. Usuarios y consumidores

### Personas

- **Desarrolladores de las plantillas y de los casos de uso**: importan la librería, configuran sus servicios y extienden con herramientas, steps o grafos propios sin reimplementar lo común.
- **Equipo de plataforma**: publica versiones, decide cuándo los casos de uso las adoptan y mantiene la compatibilidad.

### Sistemas

- **`repo-workflow`** y sus clones: la usan en clústeres de Azure Databricks.
- **`repo-agente-conversacional`** y sus clones: la usan en la API desplegada en Azure Container Apps.
- **Feed de Azure Artifacts de SUMMA**: desde ahí se distribuye.

## 4. Postura arquitectónica

- Paquete Python instalable, sin estado ni despliegue propio. Se publica en un feed y cada consumidor fija la versión que usa.
- No conoce ningún dominio (contratos, Control Doc, facturas): recibe configuración y expone interfaces.
- Cada servicio externo se usa detrás de una interfaz con su fábrica, de modo que se puede sustituir por un doble de prueba. `[inferido]` del patrón `protocols.py` + `factory.py` de `BaseRef/cognitive/`.

## 5. Resultados esperados

- Las plantillas quedan delgadas: endpoints o steps, configuración y puntos de extensión.
- Una mejora o corrección llega a todos los casos de uso al subir la versión de la librería, sin reclonar plantillas.
- Hay una sola implementación probada por servicio de Azure, en lugar de una por repo.

## 6. Objetivos medibles

- PENDIENTE: ¿qué cobertura mínima de tests se exige a la librería?
- PENDIENTE: ¿qué condición marca la versión 1.0.0 (API pública estable)? No hay versiones previas: la librería arranca en `0.1.0`.

## 7. Restricciones

- **Ejecución**: debe funcionar tanto en Databricks como en un contenedor de Container Apps. Por eso las dependencias de cada consumidor van en extras opcionales, para que el agente no cargue Spark ni el workflow cargue FastAPI. `[inferido]` de `BaseRef/core/pyproject.toml`, extra `workflow`.
- **Integración**: solo servicios de Azure del alcance de SyN: Azure OpenAI y Content Understanding (AI Foundry), AI Search, Cosmos DB, Key Vault, Unity Catalog y ADLS.
- **Diseño**: entra solo lo que pide SyN (decisión de la persona). Las capacidades extra de la base quedan fuera; ver [[alcance-inicial]] §2.
- **Operación**: se publica con pipelines de Azure DevOps (decisión de la persona). Una versión publicada no se modifica.
- **Legales y éticas**: el paquete no contiene secretos ni datos de clientes. No se copia código de la base (decisión de la persona).

## 8. Principios rectores

1. **Sin dominio**: si un cambio menciona contratos, Control Doc u otro caso de uso, no va en la librería.
2. **Interfaces antes que implementaciones**: todo servicio externo tiene interfaz y doble de prueba; el gate no llama a Azure.
3. **Instalar solo lo que se usa**: cada consumidor declara su extra.
4. **Compatibilidad explícita**: desde la 1.0.0, romper la API pública exige una versión mayor; en `0.x`, una versión menor. Siempre con nota en el changelog. `[inferido]`
5. **Credenciales fuera del código**: identidad de Azure o Key Vault, nunca un valor en el paquete ni en la configuración versionada.

## Relación con otros documentos

- [[tech-stack]] — cómo se cumple esta misión técnicamente.
- [[alcance-inicial]] — qué entra y qué no.
- [[roadmap]] — en qué orden se entrega.
