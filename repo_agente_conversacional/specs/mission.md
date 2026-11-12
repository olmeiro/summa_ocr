# Misión — Framework de agentes conversacionales (repo-agente-conversacional)

> Constitución. Define **por qué** existe el proyecto, para quién y bajo qué restricciones. No elige tecnología: eso va en [[tech-stack]].

**Fuentes** (en `project-context/`, fuera de git):
- **SyN**: `situacion y necesidad actual.pdf`.
- **BaseRef**: `ejemplo-framework/`, un framework de referencia construido para otro cliente. Se usa solo como guía de diseño, sin copiar código (decisión de la persona, 2026-11-12). `BaseRef/agent/…` es su plantilla de agente; `BaseRef/core/…` y `BaseRef/cognitive/…` son el `src/<paquete>/` de sus librerías.
- Decisiones de la persona del 2026-11-12.

Lo marcado `[inferido]` espera confirmación.

---

## 1. Propósito

Plantilla de repositorio, reutilizable y parametrizable, para construir y operar agentes conversacionales de SUMMA: orquestación de herramientas, conexión con modelos de lenguaje, recuperación sobre índices semánticos, historial de conversación, seguridad y despliegue ya resueltos, de modo que cada caso de uso se concentre en sus prompts, sus herramientas y su configuración (SyN, "Agentic Framework by Dataknow").

## 2. Problema que resuelve

- SUMMA aborda varias iniciativas de IA con esfuerzos aislados, dependencias técnicas y tiempos largos hasta producción (SyN, "Situación actual y necesidad").
- Cada agente nuevo reconstruye autenticación, persistencia, conexión con modelos, orquestación y despliegue (SyN, arquitectura §2).
- El primer caso de uso lo muestra: los contratos de Control Doc solo se consultan con procesos manuales, lentos y reactivos, sin búsqueda sobre su contenido (SyN, "Situación actual").
- No resolverlo implica repetir ese esfuerzo en cada caso de uso, con soluciones incoherentes y sin gobierno común.

## 3. Usuarios y consumidores

### Personas

- **Desarrolladores y científicos de datos** que crean un agente a partir de la plantilla: necesitan enfocarse en prompts, semántica de la conversación e integración de herramientas, sin ocuparse de infraestructura, sesiones, despliegue ni monitoreo (SyN, "Agentic Framework").
- **Equipo de plataforma y DevOps**: despliega y opera los agentes en desarrollo y producción con pipelines comunes.
- **Usuarios finales**, de forma indirecta: áreas legal, abastecimiento y otras unidades que consultan en lenguaje natural desde Microsoft Teams a través de los agentes de cada caso de uso (SyN, "Necesidad").

### Sistemas

- **Canal Microsoft Teams**, a través de Azure Bot Service, que llama a los endpoints HTTP del agente (SyN, etapa 8).
- **Repos de caso de uso**, que clonan esta plantilla; el primero es el RAG sobre contratos de Control Doc (SyN, etapa 7).
- **Índices semánticos** que publica el framework de procesamiento e indexación (`repo-workflow`): el agente los consume, no los crea.

## 4. Postura arquitectónica

- Plantilla de repositorio, no servicio central: cada caso de uso clona el repo y obtiene su propio servicio backend HTTP, contenerizado y desplegado de forma independiente (SyN, etapa 7).
- La lógica común (grafo, memoria, herramientas, autenticación, clientes de Azure) vive en la librería versionada `repo-libreria`. La plantilla aporta los endpoints, la configuración y los puntos de extensión (decisión de la persona, 2026-11-12; patrón de `BaseRef/agent/docs/architecture.md`).
- Es la capa de consulta del ecosistema. La ingesta, el procesamiento y la indexación pertenecen a `repo-workflow`.
- No se limita a RAG: admite herramientas adicionales, como APIs externas, clasificadores o procesos especializados (SyN, arquitectura §2).

## 5. Resultados esperados

- Un caso de uso nuevo arranca con autenticación, persistencia, conexión con modelos, orquestación, recuperación y despliegue ya funcionando, y su equipo solo escribe prompts, herramientas y configuración (SyN, arquitectura §5).
- Las respuestas se fundamentan en la información recuperada e incluyen referencias y enlace al documento original (SyN, arquitectura §3).
- Las mejoras del framework llegan a los agentes ya creados subiendo la versión de la librería, sin reclonar la plantilla.
- Todas las iniciativas comparten tecnología, seguridad y forma de despliegue, lo que reduce el time-to-value (SyN, "Situación actual y necesidad").

## 6. Objetivos medibles

Los umbrales se definirán con el levantamiento de preguntas frecuentes y casos prioritarios (SyN, etapa 0).

- PENDIENTE: ¿en cuántas horas o días debe un equipo tener un agente nuevo, clonado de la plantilla, respondiendo en desarrollo?
- PENDIENTE: ¿cuál es el p95 aceptable de respuesta del endpoint de conversación, y dónde se mide?
- PENDIENTE: ¿qué porcentaje mínimo de respuestas basadas en recuperación debe incluir al menos una cita a la fuente?
- PENDIENTE: ¿qué acierto mínimo debe lograr el agente sobre un conjunto de preguntas de referencia (golden set), y quién lo construye?

## 7. Restricciones

- **Ejecución**: servicios de Microsoft Azure en la suscripción de SUMMA, con dos ambientes independientes: desarrollo/pruebas y producción. El código es común; datos, índices y configuración se mantienen separados (SyN, componente C).
- **Integración**: en este alcance el único canal es Microsoft Teams (SyN, "Fuera de alcance"). El agente consume índices de Azure AI Search producidos por `repo-workflow`.
- **Diseño**: los componentes reutilizables se mantienen separados de cada caso de uso; el framework no se acopla a Control Doc (SyN, arquitectura §4).
- **Operación**: código y pipelines en Azure DevOps (SyN, componente C; decisión de la persona). Los secretos viven en Azure Key Vault.
- **Legales y éticas**: el agente no interpreta jurídicamente más allá del contenido indexado (SyN, "Fuera de alcance"). Los contratos y las conversaciones son información interna y pueden contener datos personales. PENDIENTE: ¿cuánto tiempo se conserva el historial de conversación y quién puede consultarlo?

## 8. Principios rectores

1. **Configuración antes que código**: lo que cambia entre casos de uso (prompts, herramientas activas, índice, filtros) se parametriza; el núcleo no conoce el dominio. `[inferido]` de SyN, "plataforma parametrizable".
2. **Sin evidencia no hay respuesta**: si la recuperación no trae fundamento, el agente lo dice en lugar de inventar, y toda respuesta basada en recuperación cita su fuente. `[inferido]` de SyN, etapas 7 y 8 (ausencia de alucinaciones).
3. **Fallar cerrado en seguridad**: sin token válido no hay respuesta, y los secretos solo se leen de Key Vault. `[inferido]` de SyN, etapa 6.
4. **Herramientas intercambiables**: añadir una herramienta no obliga a modificar el orquestador. `[inferido]` de SyN, arquitectura §2.
5. **Ambientes aislados**: nada de desarrollo lee ni escribe datos de producción (SyN, componente C).

## Relación con otros documentos

- [[tech-stack]] — cómo se cumple esta misión técnicamente.
- [[alcance-inicial]] — qué entra y qué no.
- [[roadmap]] — en qué orden se entrega.
