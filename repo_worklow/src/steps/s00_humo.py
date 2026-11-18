"""Step de humo: comprueba en el clúster el ambiente, el runtime y la librería instalada.

No ejecuta nada al importarse (tech-stack §2): `main()` lee los argumentos y llama a `ejecutar()`.
"""

import argparse
import os
import platform
from importlib.metadata import version


def ejecutar(ambiente: str) -> dict[str, str]:
    """Versiones del entorno donde corre el step; falla si la librería no se puede importar."""
    import summa_ai_framework.config  # noqa: F401
    import summa_ai_framework.security  # noqa: F401

    return {
        "ambiente": ambiente,
        "python": platform.python_version(),
        "runtime": os.environ.get("DATABRICKS_RUNTIME_VERSION", "local"),
        "summa_ai_framework": version("summa-ai-framework"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ambiente", required=True, help="Target del bundle: dev o prod")
    args = parser.parse_args(argv)
    for clave, valor in ejecutar(args.ambiente).items():
        print(f"[HUMO] {clave}: {valor}", flush=True)
    return 0


if __name__ == "__main__":
    # Sin sys.exit: Databricks ejecuta el script en IPython y hasta sys.exit(0) marca la tarea
    # como fallida. Un error se señala con una excepción, que sí hace fallar la tarea.
    main()
