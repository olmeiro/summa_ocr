"""Fronteras de import entre módulos comunes, de workflow y de agente (DEC-002).

Lo usan el test de fronteras (en el gate) y el humo por extra (fuera del gate).
"""

import ast
from pathlib import Path

PAQUETE = "summa_ai_framework"

# Cada grupo de workflow o de agente se instala con el extra del mismo nombre.
GRUPOS: dict[str, set[str]] = {
    "comunes": {"config", "security", "observability", "llms", "embeddings", "vectordb"},
    "workflow": {"storage", "workflow", "extraction", "processing", "sources"},
    "agent": {"auth", "agents"},
}
GRUPO_DE = {modulo: grupo for grupo, modulos in GRUPOS.items() for modulo in modulos}


def _importados(archivo: Path, partes: list[str]) -> list[tuple[int, str]]:
    """(línea, módulo) de cada import del archivo, con los relativos resueltos a absolutos."""
    importados: list[tuple[int, str]] = []
    for nodo in ast.walk(ast.parse(archivo.read_text(encoding="utf-8"))):
        if isinstance(nodo, ast.Import):
            importados += [(nodo.lineno, alias.name) for alias in nodo.names]
        elif isinstance(nodo, ast.ImportFrom):
            # partes termina en el módulo (o en __init__), así que level=1 es su paquete
            # max: un relativo que sale del paquete no debe recortar desde el final
            base = partes[: max(len(partes) - nodo.level, 0)] if nodo.level else []
            origen = ".".join([*base, *([nodo.module] if nodo.module else [])])
            importados += [(nodo.lineno, f"{origen}.{alias.name}") for alias in nodo.names]
    return importados


def violaciones(paquete: Path) -> list[str]:
    """`archivo:línea: motivo` por cada import que cruza una frontera; vacía si no hay ninguno.

    shortcut: no ve imports dinámicos (importlib); el humo por extra los cubre en parte.
    """
    errores = []
    for archivo in sorted(paquete.rglob("*.py")):
        partes = [PAQUETE, *archivo.relative_to(paquete).with_suffix("").parts]
        raiz = partes[1] == "__init__"
        grupo = GRUPO_DE.get(partes[1])
        if not raiz and grupo is None:
            errores.append(f"{archivo}: el módulo {partes[1]} no está en ningún grupo de DEC-002")
            continue
        permitidos = set() if raiz else {grupo, "comunes"}
        quien = "el __init__.py raíz" if raiz else partes[1]
        for linea, destino in _importados(archivo, partes):
            nombres = destino.split(".")
            if (
                nombres[0] == PAQUETE
                and len(nombres) > 1
                and GRUPO_DE.get(nombres[1]) not in permitidos
            ):
                errores.append(f"{archivo}:{linea}: {quien} no puede importar {destino}")
    return errores
