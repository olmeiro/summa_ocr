# Decisiones técnicas

> Decisiones que aplican a **todo el proyecto**, no a una feature. Las features las citan con `[[decisions]]` y su `DEC-NNN` en lugar de repetir el razonamiento.
> Una decisión no se borra: se reemplaza con otra que indique `Reemplaza: DEC-NNN`.

Se añade una entrada cuando una decisión debe respetarse en varias features, copiando la estructura de DEC-001 con el siguiente número.

---

## DEC-001 — El clúster clásico usa tamaños de VM sin almacenamiento Premium

- **Fecha**: 2026-11-19
- **Introducida en**: primera ejecución del job de humo en SUMMA (`dbr-analitica-summa-aba-qa`), el 2026-11-19
- **Aplica a**: el tipo de nodo de todo clúster clásico del bundle (`node_type_id` y los job clusters de las features siguientes)
- **Estado**: vigente

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

- `tests/test_bundle.py` fija el valor por defecto.
- Que un tipo nuevo no admite Premium se comprueba con `az vm list-skus -l eastus2 --size <tipo>`, en la capacidad `PremiumIO`. No hay test automático porque necesita Azure.
