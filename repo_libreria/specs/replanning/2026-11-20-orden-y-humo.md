# Replanning — 2026-11-20 — Orden de LIB-05 y LIB-06, y comprobación negativa del humo

## Contexto

- LIB-01 a LIB-03 están `accepted` y LIB-04 está bloqueada por el feed. Según [[progress]], la siguiente era LIB-05, después de este replanning.
- La feature 02 del workflow (`manifest-dag`) espera LIB-06, y detrás vienen la 03 y la 04 de su roadmap.
- La deuda «comprobación negativa del humo (DEC-002)» de `features/01-esqueleto-paquete/review.md` pedía pasar por replanning antes de LIB-05.
- El workflow decidió serverless el mismo día (`repo_worklow/specs/replanning/2026-11-20-serverless-y-repo.md`, DEC-002 del workflow).

## Aprendizajes

- Lo que salió bien: LIB-02 y LIB-03 ya sirven a las plantillas sin cambios, y en serverless la wheel se instala con lo que trae el environment más tres wheels: `azure-keyvault-secrets`, `azure-common` e `isodate` (`repo_worklow/specs/features/01-esqueleto-bundle/review.md`).
- Lo que no salió bien: la comprobación negativa del humo supone que un módulo de un grupo solo se puede importar con su extra, y eso no se cumple para los módulos que solo usan dependencias comunes.
- Sorpresas técnicas:
  - serverless no da identidad de Azure al cómputo. `DefaultAzureCredential` en un job necesita un service principal o una *service credential* de Unity Catalog, salvo que los secretos se lean por un secret scope (`specs/prerrequisitos-azure.md` §6.1, en la raíz);
  - la opción C de instalación de la librería (`PIP_EXTRA_INDEX_URL` desde un secreto) solo funciona en clúster clásico, así que no sirve con serverless (`specs/prerrequisitos-azure.md` §6.3).

## Errores que se repiten

Se revisaron los `review.md` de LIB-01 a LIB-03.

| Error | Veces | Destino |
|---|---|---|
| El cierre de la feature llegaba después del merge del PR | 3 (LIB-03 y las 01 de las dos plantillas) | Ya resuelto: línea en `AGENTS.md` y modo `cerrar` de la skill `specs` |

## Decisiones tomadas

1. **LIB-06 va antes de LIB-05.** Solo depende de LIB-02, que está `accepted`, y es la siguiente pieza del recorrido del workflow. LIB-07 sigue necesitando las dos.
2. **La comprobación negativa del humo mira las distribuciones instaladas, no los imports.**
   - Con solo un extra instalado, el humo falla si está instalada alguna distribución exclusiva del otro extra: las que declara el otro extra y no son obligatorias ni del extra propio. Se leen de los metadatos de la wheel.
   - Es lo que pide la regla 1 de DEC-001.
   - La comprobación positiva no cambia: con su extra, cada grupo importa sus módulos y los comunes.
   - Las fronteras entre grupos las sigue comprobando el test de fronteras (`scripts/fronteras.py`).
3. **El cambio entra en LIB-06**, el primer módulo de workflow que solo usa dependencias comunes: con la comprobación actual, el humo del extra del agente fallaría al poder importarlo. Cambia el «Cómo se verifica» de [[decisions]] DEC-002.

## Decisiones diferidas

- **La identidad de los jobs y la lectura de Key Vault en serverless**: secret scope o `DefaultAzureCredential` con un service principal. Es `PENDIENTE` de plataforma (`tech-stack.md` del workflow, §6). Si gana el scope, en serverless el secreto solo se lee con `dbutils.secrets.get`, que no es el proveedor de variables de entorno de LIB-02: cómo llega a la librería está por resolver (`specs/prerrequisitos-azure.md` §6.1), y cambiaría el §6 de [[tech-stack]].

## Riesgos identificados

- **Mientras ningún extra declare dependencias**, la comprobación negativa nueva no detecta nada. Hoy los dos extras están vacíos. LIB-06 debe probarla con un caso que falle, por ejemplo con unos metadatos de wheel de prueba.

## Próximos pasos

1. LIB-06 (`/specs feature 06-contexto-workflow`) en `feature/06-contexto-workflow`, con el cambio del humo en su plan.
2. LIB-05.

## Referencias

- Features afectadas: LIB-05, LIB-06 y LIB-07; la 02 del workflow.
- Documentos de la Constitución que cambian: [[decisions]] (DEC-002, «Cómo se verifica»).
