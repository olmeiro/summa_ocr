# Decisiones técnicas

> Decisiones que aplican a **todo el proyecto**, no a una feature. Las features las citan con `[[decisions]]` y su `DEC-NNN` en lugar de repetir el razonamiento.
> Una decisión no se borra: se reemplaza con otra que indique `Reemplaza: DEC-NNN`.

Se añade una entrada cuando una decisión debe respetarse en varias features, copiando la estructura de DEC-001 con el siguiente número.

---

## DEC-001 — El clúster clásico usa tamaños de VM sin almacenamiento Premium

- **Fecha**: 2026-11-19
- **Introducida en**: primera ejecución del job de humo en SUMMA (`dbr-analitica-summa-aba-qa`), el 2026-11-19
- **Aplica a**: el tipo de nodo de todo clúster clásico del bundle (`node_type_id` y los job clusters de las features siguientes)
- **Estado**: reemplazada por DEC-002 el 2026-11-20. Vuelve a aplicar si algún job usa un clúster clásico

### Contexto

La Azure Policy «Restringir Discos Premium (SSD)» de SUMMA rechaza los discos (`Microsoft.Compute/disks`) cuya SKU no está en una lista permitida. Azure Databricks pone un disco de sistema operativo Premium SSD a las VM que admiten almacenamiento Premium. El 2026-11-19, en `dbr-analitica-summa-aba-qa`, el job de humo con `Standard_D4ds_v5` falló al crear el clúster con `RequestDisallowedByPolicy`.

### Decisión

- `node_type_id` vale por defecto `Standard_D4d_v4`: 4 núcleos y 16 GB, como el anterior, pero sin almacenamiento Premium.
- Cualquier otro tipo de nodo debe cumplir dos condiciones: tener `PremiumIO = False` en `az vm list-skus` y estar en la lista de tipos del workspace.
- Con `Standard_D4d_v4`, el job de humo corrió en `SUCCESS` el mismo día, con DBR 18.3, Python 3.12.3 y la librería 0.1.0.

### Alternativas descartadas

- **Exención de la política** para el grupo administrado del workspace: depende de TI y deja pasar discos Premium, que SUMMA quiere evitar. Queda como salida si algún día hace falta un tamaño que solo exista con Premium.
- **Serverless**: no crea VMs en la suscripción y la política no le afecta, pero cambiar de cómputo es el replanning abierto «¿clásico o serverless?».
- **`Standard_D3_v2` o `Standard_F4`**: también pasan la política, pero `D3_v2` es de una generación más antigua y `F4` solo tiene 8 GB.

### Cómo se verifica

- Hasta el 2026-11-20, `tests/test_bundle.py` fijaba el valor por defecto. Desde DEC-002 no hay clúster clásico que comprobar.
- Que un tipo nuevo no admite Premium se comprueba con `az vm list-skus -l eastus2 --size <tipo>`, en la capacidad `PremiumIO`. No hay test automático porque necesita Azure.

---

## DEC-002 — El job corre en cómputo serverless

- **Fecha**: 2026-11-20
- **Introducida en**: `replanning/2026-11-20-serverless-y-repo.md`
- **Aplica a**: el cómputo de todas las tareas del job (`resources/workflow.yml`) y las variables del bundle que lo describen
- **Estado**: vigente. Implementada en el bundle y verificada en dev el 2026-11-20 (run `386609408515617` del 2026-11-20, `SUCCESS` en unos 40 s, con Python 3.12.3, runtime `client.6.5` y la librería 0.1.0)
- **Reemplaza**: DEC-001

### Contexto

[[tech-stack]] §1 pedía un clúster clásico efímero con DBR 18. El 2026-11-19, en `dbr-analitica-summa-aba-qa`, el clásico necesitó cambiar de tipo de nodo por la política de discos de SUMMA (DEC-001) y tardaba unos 8 minutos en arrancar. Serverless arrancó en unos 5 segundos y llegó a los mismos servicios, PyPI incluido (`specs/prerrequisitos-azure.md` §6.4, en la raíz). El workspace de pruebas de la persona solo admite serverless (feature 01, `review.md`).

### Decisión

Decisión de la persona, 2026-11-20:

- Las tareas del job usan un environment serverless, no un clúster. El bundle fija `environment_version` en un solo lugar, como antes fijaba `spark_version`.
- Se empieza con `environment_version: "6"`: con él corrió el humo el 2026-11-18, con Python 3.12.3, y trae azure-identity, pydantic y PyYAML en los rangos de la librería.
- La wheel de la librería y sus dependencias se declaran como dependencias del environment.
- Dejan de aplicar el tipo de nodo, la cuota de núcleos y la política de discos.

### Alternativas descartadas

- **Clúster clásico con `Standard_D4d_v4`** (DEC-001): funciona en SUMMA, pero arranca en unos 8 minutos, depende de la cuota de núcleos y de la política de discos, y no corre en workspaces solo serverless.

### Cómo se verifica

- `tests/test_bundle.py` comprueba que ninguna tarea declara clúster y que todas usan el environment con la versión fijada.
- La persona despliega y ejecuta el job en dev, con resultado `SUCCESS`, tras el cambio del bundle y cada vez que suba `environment_version`.
