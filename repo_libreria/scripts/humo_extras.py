"""Humo por extra (DEC-001 y DEC-002).

Construye la wheel y, por cada extra, la instala sola en un entorno limpio, importa los
módulos de ese consumidor y comprueba que los del otro grupo no se importan.
Necesita uv y red (backend de build y dependencias): por eso no está en el gate.

Uso: python repo_libreria/scripts/humo_extras.py
"""

import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from fronteras import GRUPOS, PAQUETE

LIBRERIA = Path(__file__).resolve().parents[1]
SRC = LIBRERIA / "src" / PAQUETE
EXTRAS = sorted(GRUPOS.keys() - {"comunes"})  # cada extra se llama como su grupo


def ejecutar(*comando: str, cwd: Path | None = None, silencio: bool = False) -> bool:
    salida = subprocess.DEVNULL if silencio else None
    return (
        subprocess.run(comando, cwd=cwd, stdout=salida, stderr=salida, check=False).returncode == 0
    )


def existentes(grupo: str) -> list[str]:
    """Módulos del grupo que ya existen en src: cada feature crea el suyo."""
    return sorted(m for m in GRUPOS[grupo] if (SRC / m).is_dir() or (SRC / f"{m}.py").is_file())


def revisar_wheel(wheel: Path) -> None:
    """Solo el paquete y su dist-info, con py.typed y un Provides-Extra por extra."""
    with zipfile.ZipFile(wheel) as zf:
        nombres = zf.namelist()
        ruta_metadatos = next(n for n in nombres if n.endswith(".dist-info/METADATA"))
        metadatos = zf.read(ruta_metadatos)
    dist_info = ruta_metadatos.split("/")[0]
    ajenos = [n for n in nombres if not n.startswith((f"{PAQUETE}/", f"{dist_info}/"))]
    if ajenos:
        sys.exit(f"[HUMO] FAIL: la wheel trae archivos ajenos al paquete: {ajenos}")
    if f"{PAQUETE}/py.typed" not in nombres:
        sys.exit("[HUMO] FAIL: la wheel no trae py.typed")
    declarados = metadatos.decode().splitlines()
    for extra in EXTRAS:
        if f"Provides-Extra: {extra}" not in declarados:
            sys.exit(f"[HUMO] FAIL: la wheel no declara el extra {extra}")


def probar_extra(wheel: Path, extra: str, tmp: Path) -> None:
    entorno = tmp / f"venv-{extra}"
    python = entorno / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    if not (
        ejecutar("uv", "venv", "--quiet", "--python", "3.12", str(entorno))
        and ejecutar(
            "uv", "pip", "install", "--quiet", "--python", str(python), f"{wheel}[{extra}]"
        )
    ):
        sys.exit(f"[HUMO] FAIL: {extra}: no se pudo crear el entorno o instalar la wheel")
    # Desde tmp e -I: que solo se pueda importar lo instalado, no el código del repo
    importar = [PAQUETE] + [f"{PAQUETE}.{m}" for m in existentes("comunes") + existentes(extra)]
    for modulo in importar:
        if not ejecutar(str(python), "-I", "-c", f"import {modulo}", cwd=tmp):
            sys.exit(f"[HUMO] FAIL: {extra}: no importa {modulo}")
    for otro in (e for e in EXTRAS if e != extra):
        for modulo in existentes(otro):
            # El fallo esperado no se muestra: su traceback confundiría al leer la salida
            if ejecutar(
                str(python), "-I", "-c", f"import {PAQUETE}.{modulo}", cwd=tmp, silencio=True
            ):
                sys.exit(f"[HUMO] FAIL: {extra}: importa {PAQUETE}.{modulo}, que es de {otro}")
    print(f"[HUMO] PASS: {extra} (importa {', '.join(importar)})", flush=True)


def main() -> int:
    if not shutil.which("uv"):
        sys.exit("[HUMO] FAIL: uv no está en el PATH")
    # setuptools reutiliza build/lib: un módulo borrado o renombrado se colaría en la wheel
    shutil.rmtree(LIBRERIA / "build", ignore_errors=True)
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as directorio:
        tmp = Path(directorio)
        if not ejecutar("uv", "build", "--quiet", "--wheel", "--out-dir", str(tmp), str(LIBRERIA)):
            sys.exit("[HUMO] FAIL: no se pudo construir la wheel")
        wheel = next(tmp.glob("*.whl"))
        print(f"[HUMO] Wheel: {wheel.name}", flush=True)
        revisar_wheel(wheel)
        for extra in EXTRAS:
            probar_extra(wheel, extra, tmp)
    print("[HUMO] Todas las comprobaciones pasaron.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
