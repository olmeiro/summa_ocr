# Prerrequisitos de Azure del framework

> Guía transversal a los tres proyectos (librería, workflow y agente). Dice qué recursos, identidades y permisos de Azure necesita el framework, cómo llega cada pieza a su ambiente y en qué orden conviene tenerlos: primero un despliegue mínimo (el hito 0, §7) y después las mejoras (§8).
>
> - **Alcance**: el ambiente de dev/test de SUMMA. Prod queda pendiente: sus recursos y nombres los define plataforma (§9).
> - **Mandan las Constituciones**: esta guía cita sus decisiones y sus `PENDIENTE`. Lo que propone para resolver un `PENDIENTE` lo marca como propuesta.
> - **Fuentes**:
>   - el documento de prerrequisitos de DataKnow (`project-context/Seguimiento Prerrequisitos.pdf`, que no se versiona);
>   - las Constituciones de los tres proyectos;
>   - una verificación de solo lectura en la suscripción de dev/test de SUMMA, el 2026-11-19, con `az` y el CLI de Databricks y la cuenta de SUMMA del equipo.
> - Aquí no van hosts, identificadores ni correos: solo nombres de recursos. Los riesgos de seguridad que se detectan en los recursos de SUMMA no se versionan: se entregan a TI por un canal privado.

## 1. Qué usa hoy el framework de Azure

| Pieza | Qué hay en `main` | Qué necesita de Azure hoy | Qué necesitará después |
|---|---|---|---|
| Librería `summa-ai-framework` 0.1.0 | Configuración YAML y secretos de Key Vault (LIB-01 a LIB-03) | Key Vault, con `DefaultAzureCredential` | Azure OpenAI (LIB-08), Content Understanding (LIB-09), AI Search (LIB-11), Unity Catalog (LIB-05 y LIB-07), Cosmos DB (LIB-14) |
| Workflow | Bundle con un job de humo en clúster clásico DBR 18 (01) | Un workspace de Databricks | Unity Catalog, Key Vault, ADLS y los servicios de IA |
| Agente | API FastAPI con `/health` y `/ready`, e imagen Docker (01) | Nada todavía | ACR, Container Apps, Key Vault, Azure OpenAI, AI Search, Cosmos DB y Bot Service |

La librería todavía no habla con modelos, embeddings ni índices: eso llega con la fase 2 de su roadmap.

## 2. Cómo llega cada pieza a su ambiente

```text
repo-libreria ──pipeline──▶ feed de Azure Artifacts ──pip──▶ Databricks · imagen del agente · dev local
repo-workflow ──bundle────▶ workspace de Databricks (job + wheel) ──▶ Key Vault, Unity Catalog, servicios de IA
repo-agente  ──docker─────▶ ACR ──▶ Container App ──▶ Key Vault, OpenAI, AI Search, Cosmos DB
```

## 3. Inventario en SUMMA (dev/test)

- Suscripción `Microsoft Enterprise Dev/Test Lab Summa`. Casi todo está en East US 2; Foundry está en East US y AI Search en West US.
- El grupo `rg-framework-transversal-dev` que propone el PDF no existe: los recursos están repartidos en cuatro grupos.
- Según el PDF (§5), en Azure DevOps ya están creadas la service connection de ARM «Arm celula ia» y la de Docker Registry hacia `pocopenaicontainerregistry`. Es decir, hay un proyecto de DevOps, pero el equipo todavía no tiene acceso a él (§9).

| Recurso | Para qué | Nombre (grupo) | Estado el 2026-11-19 | Falta |
|---|---|---|---|---|
| Databricks | Workflow | `dbr-analitica-summa-aba-qa` (`rg-analitica-summa-aba-qa`) | Premium, con Unity Catalog (catálogo `main`) y DBR 18 LTS. No tiene VNet propia y sus nodos no tienen IP pública. Tiene el secret scope `akv-summa-analitica-scope`, respaldado por el Key Vault. La persona es admin, y el job de humo ya corre ahí (§7) | Decidir si es el workspace del framework (§9) |
| | | `dbr-celula-ia` (`rg-celula-ia`) | Premium, **sin metastore de Unity Catalog** y vacío | Es el que nombra el `tech-stack.md` del workflow (§1 y §7). Sin Unity Catalog no sirve |
| Key Vault | Secretos | `kv-comparido-devtest` (`RecursosCompartidosQA`) | Existe, porque el scope de Databricks lo lee. Lo comparten otros proyectos. El equipo no ve su grupo, así que no sabe si usa RBAC o directivas de acceso, ni cómo tiene la red | Permisos (§4) y decisión sobre un vault dedicado (§9) |
| ACR | Imagen del agente | `pocopenaicontainerregistry` (`rg-celula-ia`) | Basic, con el usuario admin activo. Según el PDF, la service connection de Docker de DevOps apunta aquí | Elegir entre los dos ACR (§9) |
| | | `summacontainerregistryqa` (`RecursosCompartidosQA`) | El equipo no lo ve | |
| Container Apps Environment | Hosting del agente | `cae-summa-agentsfw-dev` (`rg-celula-ia`) | Sin VNet, con los logs en Log Analytics | La red privada que pide el `tech-stack.md` del agente (en su §9) solo se fija al crear el entorno: llegado el momento habrá que recrearlo (§8) |
| Container App | Agente | `ca-summa-agentsfw-dev` (`rg-celula-ia`) | Sirve la imagen de ejemplo de Microsoft, con ingress público al puerto 80 y **sin identidad** | La imagen del agente, el puerto 8000 y una identidad (§4) |
| Azure AI Foundry (AIServices) | LLM, embeddings y Content Understanding | `aifcelulaiaqa0282309147` (`rg-celula-ia`, East US) | Deployments `gpt-4o-mini`, `gpt-4o`, `gpt-5.2` y `text-embedding-3-large`. Red pública activa | Qué deployments se ofrecen en dev (§9) |
| Document Intelligence | Respaldo si Content Understanding no cubre un formato (`tech-stack.md` del workflow, §6) | `di-celula-ia` (`rg-celula-ia`) | SKU F0 (gratuito) | Un SKU de pago, si llega a usarse |
| Cosmos DB | Memoria del agente | `cosmos-summa-agentsfw` (`rg-celula-ia`) | Serverless, API NoSQL, con autenticación por clave. Red pública activa | — |
| AI Search | Índice | `srch-summa-agentsfw` (`rg-celula-ia`, West US) | Basic. Acepta clave o Entra ID. Red pública activa | — |
| ADLS Gen2 | Capas bronze, silver y gold | `dlsummaqa` (`rg-analitica-summa-qa`) | Existe | Conectarlo a Unity Catalog (§6.2) |
| Bot Service y App Registration del bot | Canal de Teams | — | No existen; el PDF da el Bot Service por pendiente | Los crea TI de SUMMA antes de la feature 08 del agente (`roadmap.md` del agente) |
| App Service | — | `app-summa-agentsfw` (`rg-celula-ia`) | Detenido y sin identidad | Ninguno: el framework no lo usa, porque el agente va en Container Apps |

## 4. Identidades y permisos

- El equipo tiene **Contributor** en `rg-celula-ia`, `rg-analitica-summa-aba-qa` y `rg-analitica-summa-qa`, y ningún acceso a `RecursosCompartidosQA`. Con Contributor puede crear y configurar recursos, por ejemplo activar la identidad de un Container App, pero **no puede asignar roles**. Las asignaciones de roles de Azure de esta sección las hace TI de SUMMA, con el rol Owner o User Access Administrator. Los permisos de Databricks y de Unity Catalog (fila del service principal) no son roles de Azure: los da un admin del workspace, y los del catálogo su dueño o un metastore admin.
- **Key Vault compartido.** Mientras el vault sea `kv-comparido-devtest`, ningún rol de esta tabla se asigna sobre el vault entero, porque daría acceso a los secretos de otros proyectos:
  - si el vault usa RBAC, los roles se asignan secreto por secreto. Crear un secreto exige permiso sobre el vault entero, así que en el compartido los crea TI y el grupo solo recibe el rol sobre cada uno para cambiar su valor;
  - si usa directivas de acceso, no se pueden limitar a unos secretos, y hace falta un vault dedicado (§9);
  - los roles por secreto no sirven para el secret scope de Databricks, que expone el vault entero (§6.1).
- Las identidades de la tabla son **propuestas**. Las que leen Key Vault responden a dos `PENDIENTE` de plataforma: la del agente (`tech-stack.md` del agente, §6) y la de los jobs (`tech-stack.md` del workflow, §6).

| Identidad (propuesta) | Sobre | Rol | Para qué | Cuándo |
|---|---|---|---|---|
| Identidad administrada (system-assigned) de `ca-summa-agentsfw-dev` | ACR | `AcrPull` | Bajar la imagen sin credenciales | Al desplegar el agente |
| La misma | Los secretos del agente en el vault | `Key Vault Secrets User` | Leer las claves de los servicios (LIB-03) | Feature 02 del agente |
| Grupo de desarrolladores | El vault dedicado; en el compartido, solo los secretos que cree TI | `Key Vault Secrets Officer` | Crear (en el dedicado) y mantener los secretos de prueba y de dev | Antes del paso 4 del §7 |
| Grupo de desarrolladores | `RecursosCompartidosQA`, o los recursos que se reutilicen | `Reader` | Ver lo que usa el framework | Ya |
| Service principal de Databricks (PDF §7) | Workspace y catálogo | Usuario del workspace con permiso para crear clústeres; `USE CATALOG` y `CREATE SCHEMA` en el catálogo, porque el job crea los esquemas de su iniciativa y sus tablas de logs (`tech-stack.md` del workflow, §4) | `run_as` de los jobs de prod | Antes del primer despliegue a prod |
| Access Connector de Databricks | ADLS `dlsummaqa` | `Storage Blob Data Contributor` | External location de Unity Catalog | Fase 2 del workflow |
| Identidad del pipeline: service connection de ARM con Workload Identity Federation | Grupos de recursos del framework y ACR | `Contributor` y `AcrPush` | Desplegar | CI/CD |

Las claves de API de Azure OpenAI, Content Understanding, AI Search y Cosmos DB van en Key Vault, y la identidad solo se usa para llegar a Key Vault (decisión del 2026-11-13, `tech-stack.md` de la librería, §6). Por eso las identidades no necesitan los roles de datos que lista el PDF (`Cognitive Services OpenAI User` y `Search Index Data Contributor`). Pasar de claves a Entra ID sería un replanning.

## 5. La librería como paquete de Azure DevOps

1. **Feed.** Un feed de Azure Artifacts de proyecto, con **PyPI como upstream**: así un solo índice sirve la librería y sus dependencias. Su nombre, y si las versiones preliminares van a una vista aparte (`@Prerelease`), es un `PENDIENTE` de plataforma (`tech-stack.md` de la librería, §7).
2. **Publicación** (LIB-04). El pipeline del repo de la librería pasa el gate, construye la wheel y la sube con `twine` (tarea `TwineAuthenticate@1`). La identidad `<proyecto> Build Service` necesita el rol *Feed Publisher (Contributor)* en el feed. Una versión publicada no se puede reemplazar, así que cada cambio sube la versión.
3. **Instalación.** Cada consumidor se autentica de una forma:

   | Consumidor | Cómo se autentica |
   |---|---|
   | Dev local | `artifacts-keyring`, con inicio de sesión interactivo, o un PAT con permiso *Packaging (Read)* |
   | Build de la imagen del agente, en el pipeline | `PipAuthenticate@1` deja la URL del índice con token. Se pasa a `docker build` como secreto de BuildKit (`--secret`), nunca como `ARG`, que quedaría en el historial de la imagen (`tech-stack.md` del agente, §9) |
   | Databricks | Ver §6.3 |

Mientras no exista el feed:
- el bundle del workflow construye la wheel desde `../repo_libreria` al desplegar (feature 01 del workflow);
- el agente todavía no usa la librería.

## 6. Databricks y los recursos de Azure

### 6.1 Secretos

Hay dos caminos, y elegir uno responde al `PENDIENTE` de plataforma sobre la identidad de los jobs (`tech-stack.md` del workflow, §6):

- **Secret scope respaldado por Key Vault** (propuesta).
  - Un scope expone **todo** su vault: los secretos los lee Databricks con sus propios permisos sobre el vault, no la identidad del job, así que los roles por secreto del §4 no lo limitan. Por eso este camino exige un vault dedicado al framework, con un scope propio sobre él.
  - El job lee el secreto con `dbutils.secrets.get` o, en clúster clásico, con `{{secrets/<scope>/<clave>}}` en `spark_env_vars`. Así sirve el proveedor de variables de entorno de la librería, y el clúster no necesita identidad de Azure.
  - Pero cambia lo que dice el `tech-stack.md` de la librería (§6): ahí Key Vault se lee con `DefaultAzureCredential` en cada ambiente. Por eso hace falta una decisión, no basta con esta propuesta (§9).
- **`DefaultAzureCredential` desde el clúster**, con el proveedor de Key Vault de LIB-03. Necesita una identidad en el clúster, y Databricks no le da una por defecto. Las opciones son un service principal, cuyo secreto también habría que guardar en algún sitio, o una *service credential* de Unity Catalog sobre un Access Connector (hay que comprobar que el workspace la ofrece).

Leer un secreto por el scope no prueba que el clúster llegue a Key Vault: esa lectura la hace el plano de control de Databricks.

### 6.2 Datos

- **Catálogo.** Los esquemas `<iniciativa>_<capa>` ya están decididos (`tech-stack.md` del workflow, §4). Falta el catálogo: hoy solo existe `main` (§9).
- **ADLS.** Para conectar `dlsummaqa` a Unity Catalog hacen falta una storage credential (un Access Connector con `Storage Blob Data Contributor`) y una external location. Las crea un metastore admin.
- **Red del Storage.** El `tech-stack.md` del workflow, en su §9, pide autorizar las subredes de Databricks en el firewall del Storage. Un workspace sin VNet propia, como `dbr-analitica-summa-aba-qa`, no tiene subredes que autorizar, y eso también pesa al elegir el workspace (§9).

### 6.3 Instalación de la librería

Son propuestas para el `PENDIENTE` de plataforma sobre cómo instalar el paquete del feed en Databricks (`tech-stack.md` de la librería, §9):

| Opción | Cómo | Credenciales en ejecución |
|---|---|---|
| A. Wheel en un volumen (la recomendada para empezar) | El pipeline copia la wheel a `/Volumes/<catálogo>/<esquema>/libs/` y el job la declara como `whl`. Las dependencias salen de PyPI | Ninguna |
| B. Feed como índice del workspace | En *Configuración → Cómputo → Repositorios de paquetes default* se pone la URL del feed con token, que se guarda en el scope `databricks-package-management`. Sustituye al proxy de PyPI de Databricks, así que el feed necesita PyPI como upstream | Un PAT con *Packaging (Read)*, que hay que rotar. El token de un service principal dura alrededor de una hora y no sirve como valor fijo |
| C. Índice extra en el clúster | `PIP_EXTRA_INDEX_URL` desde un secreto (`{{secrets/…}}`). Solo funciona en clúster clásico | El mismo PAT |

### 6.4 Red y cómputo

- **Clásico.** `dbr-analitica-summa-aba-qa` no tiene VNet propia, y sus nodos no tienen IP pública (*secure cluster connectivity*), así que salen a internet por la NAT que gestiona Databricks. El paso 1 del §7 probó que el clúster arranca, instala la wheel con sus dependencias y ejecuta el step. El paso 2 probó, sin credenciales, que llega por red a Entra ID, Key Vault, Foundry (OpenAI y Content Understanding), AI Search, Cosmos DB, PyPI y Azure DevOps, siempre por IP pública. **Falta la autenticación**: es el paso 4.
- **Red pública de los servicios.** Foundry, AI Search y Cosmos DB la tienen activa. La del Key Vault no se sabe, porque el equipo no ve su grupo.
- **Política de discos.** La Azure Policy «Restringir Discos Premium (SSD)» de SUMMA rechaza los discos cuya SKU no está en una lista permitida; su descripción da como ejemplo `Standard_LRS` y `StandardSSD_LRS`. El 2026-11-19 tumbó el job de humo al crear el clúster: con `Standard_D4ds_v5`, el disco del sistema operativo del nodo era Premium. Hay dos salidas:
  - un tamaño de VM sin almacenamiento Premium de los que ofrece el workspace: `Standard_D4d_v4`, `Standard_D3_v2` o `Standard_F4`. Con `Standard_D4d_v4`, el job de humo corrió en `SUCCESS` el 2026-11-19, y es el valor por defecto del bundle (DEC-001 del workflow);
  - que TI exima de la política al grupo de recursos administrado del workspace.

  Serverless no crea VMs en la suscripción de SUMMA, así que esta política no le afecta.
- **Serverless.** Según la configuración del workspace, pip pasa por el proxy de PyPI de Databricks. En SUMMA la salida a internet está abierta: el paso 2 llegó a los mismos servicios que el clásico, con un arranque de 5 segundos frente a unos 8 minutos. Esa salida la controlan las políticas de red de la cuenta de Databricks, así que plataforma podría cerrarla, como estaba en el workspace de pruebas de DataKnow.
- **Cuota.** En East US 2 hay 10 vCPU libres en cada familia candidata (24 en Dv2), y el job de humo usa 4.

## 7. Desplegar pronto: el hito 0

La idea es desplegar ya lo que hay, aunque haga poco, y crecer sobre algo que corre en Azure. Cada paso prueba un tramo del camino del §2.

| Paso | Qué demuestra | Estado, o lo que falta | Lo lanza |
|---|---|---|---|
| 1. Workflow de humo en `dbr-analitica-summa-aba-qa` | Bundle, clúster clásico DBR 18 e instalación de la librería con sus dependencias. Cierra la deuda de clásico de 01-esqueleto-bundle | **Hecho el 2026-11-19**: `SUCCESS` con `Standard_D4d_v4` (§6.4) | La persona |
| 2. Prueba de red desde el clúster | Que el clúster resuelve por DNS y abre HTTPS, sin credenciales, contra Entra ID, Key Vault, Foundry, AI Search, Cosmos DB y PyPI | **Hecho el 2026-11-19**: desde clásico y desde serverless responden todos, y también Azure DevOps, por IP pública. La prueba no usa credenciales | La persona |
| 3. Agente en `ca-summa-agentsfw-dev` | Imagen en el ACR, Container App y `/health` público | La imagen y el puerto 8000. Para bajar la imagen, `AcrPull` (lo asigna TI) o, como atajo, el usuario admin del ACR | La persona |
| 4. Un secreto de prueba de punta a punta | El workflow y el agente leen un secreto del Key Vault | Un vault dedicado si se lee por el scope (§6.1), o roles por secreto si no (§4); decidir las identidades (§9); y el secreto de prueba, que en el vault compartido crea TI | La persona, después de TI |
| 5. Librería desde el feed | Publicación (LIB-04) e instalación desde el feed | Acceso al proyecto de DevOps, el feed y su pipeline | Plataforma y la persona |

Los pasos 2 y 3 no necesitan a TI. LIB-04 ya es la siguiente feature de la librería. Lo que sí cambia el orden de los roadmaps, y por eso es un replanning, es adelantar los CI/CD (feature 15 del workflow y feature 09 del agente) sin la IaC.

## 8. Después del hito 0: mejoras en orden

| # | Mejora | Qué resuelve | Dueño |
|---|---|---|---|
| 1 | Vault dedicado al framework, con un scope propio sobre él, si el paso 4 usó el vault compartido | Que el framework comparta vault con otros proyectos. Es requisito para leer los secretos por el scope (§6.1) | TI de SUMMA (vault) y un admin del workspace con permisos sobre el vault (scope) |
| 2 | Identidad del Container App con `AcrPull` y `Key Vault Secrets User`; después, desactivar el usuario admin del ACR | Credenciales de larga vida en el despliegue | TI y el equipo |
| 3 | Feed y LIB-04: el workflow y el agente instalan la librería desde el feed | La wheel que hoy se construye al desplegar | Plataforma y el equipo |
| 4 | Pipelines de CI/CD (feature 15 del workflow y 09 del agente) sobre las service connections que ya existen | Que cada despliegue dependa de la persona | El equipo y DevOps |
| 5 | Identidad de los jobs: un service principal con `run_as` | Jobs que corren con la identidad de quien despliega | Plataforma |
| 6 | Red privada: VNet del entorno de Container Apps, private endpoints y subredes de Databricks autorizadas | Lo que piden los `tech-stack.md` del workflow y del agente (§9 de cada uno) | IaC de SUMMA |
| 7 | Ambiente de prod: recursos, nombres e identidades | Los `PENDIENTE` de prod de las Constituciones | Plataforma |

## 9. Decisiones pendientes

| # | Pregunta | Dueño |
|---|---|---|
| 1 | ¿Workspace del framework: `dbr-analitica-summa-aba-qa` (con Unity Catalog y scope, pero sin VNet propia) o `dbr-celula-ia` (sin Unity Catalog)? Cambia el `tech-stack.md` del workflow (§1, §7 y §9) | SUMMA y plataforma |
| 2 | ¿Key Vault dedicado (`kv-summa-agentsfw`, como pide el PDF) o el compartido? Si los jobs leen por el scope (§6.1), hace falta el dedicado. Con el compartido solo sirven los roles por secreto, y para eso hay que saber qué modelo de permisos usa `kv-comparido-devtest`: RBAC o directivas de acceso | TI de SUMMA |
| 3 | ¿ACR `pocopenaicontainerregistry`, al que apunta DevOps, o `summacontainerregistryqa`? | TI de SUMMA |
| 4 | ¿En qué proyecto de DevOps están las service connections del PDF? Allí hay que crear los tres repos decididos el 2026-11-12 (librería, workflow y agente), no los dos que propone el PDF (`agents-framework-backend` y `agents-framework-frontend`) | SUMMA y DevOps |
| 5 | Identidades: la del Container App (`PENDIENTE` del `tech-stack.md` del agente, §6) y la de los jobs (`PENDIENTE` del `tech-stack.md` del workflow, §6). Leer los secretos por el scope (§6.1) cambiaría el `tech-stack.md` de la librería (§6) | Plataforma |
| 6 | ¿Qué deployments de Foundry se ofrecen en dev? El framework no fija modelos: cada caso de uso elige los suyos. Hay `text-embedding-3-large`, y el PDF pedía `text-embedding-3-small`; el de embeddings fija la dimensión del índice | SUMMA y la persona |
| 7 | ¿Catálogo de Unity Catalog del framework? | SUMMA (data engineer) |
| 8 | ¿Content Understanding está disponible en la región de `aifcelulaiaqa0282309147` (East US)? | El equipo, al empezar LIB-09 |
| 9 | AI Search está en West US y Foundry en East US, mientras que Databricks y Container Apps están en East US 2: ¿se aceptan la latencia y el tráfico entre regiones? | Plataforma |
| 10 | ¿En qué repo y con qué herramienta vive la IaC? (`PENDIENTE` del `alcance-inicial.md` del workflow y del agente) | SUMMA |
| 11 | Nombres de los recursos: los de cada ambiente (`PENDIENTE` del `tech-stack.md` del agente, §7) y los de prod (`PENDIENTE` del `tech-stack.md` del workflow, §7). Los de dev del §3 son lo que existe hoy, no una decisión | Plataforma |
| 12 | Acceso del equipo a `RecursosCompartidosQA`: sin él no puede verificar ni operar el Key Vault ni el ACR que el PDF da por existentes | TI de SUMMA |
| 13 | ¿Cómputo clásico o serverless para el workflow? En SUMMA los dos llegan a los servicios (§6.4). Serverless arranca en segundos y no le afecta la política de discos, pero cambia el `tech-stack.md` del workflow (§1): es el replanning que ese proyecto ya tiene abierto | La persona y plataforma |
