"""Fronteras de import entre módulos comunes, de workflow y de agente (DEC-002)."""

import importlib.util
from pathlib import Path

import pytest

LIBRERIA = Path(__file__).resolve().parents[1]
especificacion = importlib.util.spec_from_file_location(
    "fronteras", LIBRERIA / "scripts" / "fronteras.py"
)
assert especificacion and especificacion.loader
fronteras = importlib.util.module_from_spec(especificacion)
especificacion.loader.exec_module(fronteras)


def paquete(tmp_path: Path, archivos: dict[str, str]) -> Path:
    """Paquete summa_ai_framework sintético con los archivos dados (ruta → código)."""
    raiz = tmp_path / "summa_ai_framework"
    for ruta, codigo in {"__init__.py": "", **archivos}.items():
        (raiz / ruta).parent.mkdir(parents=True, exist_ok=True)
        (raiz / ruta).write_text(codigo, encoding="utf-8")
    return raiz


def test_el_paquete_real_respeta_las_fronteras() -> None:
    src = LIBRERIA / "src" / "summa_ai_framework"
    assert (src / "__init__.py").is_file()  # rglob sobre una ruta inexistente no revisaría nada
    assert fronteras.violaciones(src) == []


def test_ningun_modulo_esta_en_dos_grupos() -> None:
    assert sum(map(len, fronteras.GRUPOS.values())) == len(fronteras.GRUPO_DE)


@pytest.mark.parametrize(
    "archivos",
    [
        {"workflow/__init__.py": "from summa_ai_framework.config import x\n"},
        {"agents/memoria.py": "from ..config import x\nfrom . import otro\n"},
        {"config/__init__.py": "import os\nfrom summa_ai_framework.llms import y\n"},
        {"auth/jwt.py": "import summa_ai_framework\n"},
        {"__init__.py": "from ...x import y\n"},  # Python ya falla al ejecutarlo
    ],
    ids=[
        "workflow-a-comun",
        "agente-relativo",
        "comun-a-comun",
        "raiz-vacia",
        "relativo-fuera-del-paquete",
    ],
)
def test_imports_permitidos(tmp_path: Path, archivos: dict[str, str]) -> None:
    assert fronteras.violaciones(paquete(tmp_path, archivos)) == []


@pytest.mark.parametrize(
    ("archivos", "esperado"),
    [
        (
            {"workflow/paso.py": "\n\nfrom summa_ai_framework.agents import grafo\n"},
            "paso.py:3: workflow no puede importar summa_ai_framework.agents.grafo",
        ),
        (
            {"agents/x.py": "import summa_ai_framework.storage.unity\n"},
            "x.py:1: agents no puede importar summa_ai_framework.storage.unity",
        ),
        (
            {"processing/x.py": "from ..auth import jwt\n"},
            "x.py:1: processing no puede importar summa_ai_framework.auth.jwt",
        ),
        (
            {"config/x.py": "from summa_ai_framework import workflow\n"},
            "x.py:1: config no puede importar summa_ai_framework.workflow",
        ),
        (
            {
                "llms/x.py": "from typing import TYPE_CHECKING\n"
                "if TYPE_CHECKING:\n    from summa_ai_framework.auth import y\n"
            },
            "x.py:3: llms no puede importar summa_ai_framework.auth.y",
        ),
        (
            {"__init__.py": "from . import config\n"},
            "__init__.py:1: el __init__.py raíz no puede importar summa_ai_framework.config",
        ),
        ({"pdf/__init__.py": ""}, "el módulo pdf no está en ningún grupo"),
        ({"utils.py": ""}, "el módulo utils no está en ningún grupo"),
    ],
    ids=[
        "workflow-a-agente",
        "agente-a-workflow",
        "relativo-workflow-a-agente",
        "comun-a-workflow",
        "type-checking",
        "raiz-reexporta",
        "subpaquete-sin-grupo",
        "modulo-sin-grupo",
    ],
)
def test_imports_prohibidos(tmp_path: Path, archivos: dict[str, str], esperado: str) -> None:
    errores = fronteras.violaciones(paquete(tmp_path, archivos))
    assert len(errores) == 1
    assert esperado in errores[0]
