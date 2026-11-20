# Replanning — 2026-11-20 — Serverless y repo de la organización

## Contexto

- **Cómputo**: la feature 01 dejó abierta la pregunta «¿clásico o serverless para SUMMA?» (`features/01-esqueleto-bundle/review.md`, "Deuda técnica"). El 2026-11-19 los dos corrieron en `dbr-analitica-summa-aba-qa` ([[progress]]; `specs/prerrequisitos-azure.md` §6.4 y §7, en la raíz).
- **Repo**: el 2026-11-20 el repo pasó a `OlmeDK/summa_framework_v0`, en la organización de GitHub, con todo su historial.
- **Orden**: la feature 02 espera LIB-06, y la librería tenía previsto seguir con LIB-05.

## Aprendizajes

- Lo que salió bien: probar pronto en el workspace real. El job de humo, la red, los embeddings y AI Search quedaron comprobados en un día, antes de escribir los steps.
- Lo que no salió bien: el bundle quedó escrito para clásico, con DBR 18, tipo de nodo y cuota de núcleos, antes de saber qué cómputo admitía cada workspace. Hubo que cambiar el nodo por la política de discos (DEC-001).
- Sorpresas técnicas:
  - el workspace de pruebas solo admite serverless, y SUMMA admite los dos;
  - serverless arranca en unos 5 s y el clásico en unos 8 min;
  - la política de discos Premium de SUMMA no afecta a serverless, que no crea VMs en su suscripción;
  - en SUMMA, serverless llega a los mismos servicios que el clásico, incluido PyPI;
  - el revisor de CI juzga un PR sin feature contra su título y su descripción. Un título que prometía una prueba de Content Understanding que no se hizo le valió un `revise` (PR #9).

## Errores que se repiten

Se revisaron los `review.md` de las features cerradas de los tres proyectos.

| Error | Veces | Destino |
|---|---|---|
| El cierre de la feature llegaba después del merge del PR | 3 (LIB-03, 01 del workflow, 01 del agente) | Ya resuelto: línea en `AGENTS.md` y modo `cerrar` de la skill `specs` |
| El título de un PR sin feature promete más de lo que hace el diff | 1 (PR #9) | Puntual: se corrigió el título. Si se repite, línea en `AGENTS.md` |
| `sys.exit` en un step marca la tarea como fallida | 1 | Ya resuelto: regla en [[tech-stack]] §2 y test |

## Decisiones tomadas

1. **El job corre en cómputo serverless** (decisión de la persona, 2026-11-20). Queda en [[decisions]] DEC-002, que reemplaza a DEC-001; cambia [[tech-stack]] §1, §3, §6 y §9, y [[alcance-inicial]].
2. **El repo de GitHub de la organización es temporal** (decisión de la persona, 2026-11-20). Se trabaja en `OlmeDK/summa_framework_v0` mientras no exista Azure DevOps, que sigue siendo el destino ([[tech-stack]] §12). Ahí `gate` y `revisor` corren en cada PR, pero GitHub no impide el merge aunque fallen (plan gratuito, repo privado), así que la regla la cumple quien mergea: no se mergea hasta que los dos estén en verde.
3. **La librería adelanta LIB-06 a LIB-05**. LIB-06 solo depende de LIB-02, que ya está `accepted`, y desbloquea la 02 de este roadmap. La comprobación negativa del humo de la librería se resuelve en LIB-06 (replanning de `repo_libreria` de la misma fecha).

## Decisiones diferidas

- **El workspace del framework**: `dbr-analitica-summa-aba-qa` u otro. Lo eligen SUMMA y plataforma.
- **La identidad del job y la lectura de Key Vault** (`PENDIENTE` de [[tech-stack]] §6). Serverless no da identidad de Azure al cómputo, así que pesa más el camino del secret scope respaldado por Key Vault (`specs/prerrequisitos-azure.md` §6.1). Decide plataforma.

## Riesgos identificados

- **La salida a internet de serverless la controlan las políticas de red de la cuenta de Databricks**, no la red de SUMMA. Si plataforma la cierra, como estaba en el workspace de pruebas, el job no instala dependencias desde PyPI ni llega a los servicios. Mitigación: que plataforma fije las políticas de red de la cuenta en la IaC, con los servicios y PyPI (o el feed) permitidos. `[inferido]`: el acceso privado a los recursos de Azure es otra pieza, la network connectivity configuration (NCC).
- **Coste**: serverless se cobra por DBU de serverless y no hay cuota de núcleos que lo limite. El job sigue siendo semanal y de un solo `max_concurrent_runs`.
- **La versión del environment** fija las versiones que trae el entorno (Python, pydantic, azure-identity). Al subirla, el humo debe volver a pasar.

## Próximos pasos

1. **Bundle a serverless**, en esta misma rama: el revisor de CI daba `revise` mientras la documentación decía serverless y el bundle seguía en clásico (decisión de la persona, 2026-11-20):
   - `resources/workflow.yml` cambia `job_clusters` por un `environment` con `environment_version: "6"` y la wheel como dependencia;
   - `databricks.yml` pierde `spark_version` y `node_type_id`, y gana `environment_version`;
   - `tests/test_bundle.py` lo comprueba.

   `bundle validate` pasa en dev y prod. La persona hizo `deploy` y `run` en `dbr-analitica-summa-aba-qa`: run `386609408515617` del 2026-11-20, `SUCCESS` en unos 40 s, con Python 3.12.3, runtime `client.6.5` y la librería 0.1.0.
2. **LIB-06** (`/specs feature 06-contexto-workflow` en `repo_libreria`) y después la 02 de este roadmap.
3. **Hito 0**: la extracción real con Content Understanding, desde un job serverless.

## Referencias

- Features afectadas: 01 (bundle), 02 (espera LIB-06) y 15 (CI/CD, sigue esperando Azure DevOps).
- Documentos de la Constitución que cambian: [[tech-stack]], [[alcance-inicial]] y [[decisions]].
