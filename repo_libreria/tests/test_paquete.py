"""El paquete instalado es el de repo_libreria/src y su raíz no expone nada."""

from pathlib import Path
from types import ModuleType

import summa_ai_framework

SRC = Path(__file__).resolve().parents[1] / "src" / "summa_ai_framework"


def test_se_instala_editable_desde_src() -> None:
    assert Path(summa_ai_framework.__file__).resolve().parent == SRC


def test_la_raiz_no_reexporta_nada() -> None:
    # Los submódulos que otro test ya importó aparecen como atributos de la raíz: no cuentan
    publicos = [
        nombre
        for nombre, valor in vars(summa_ai_framework).items()
        if not nombre.startswith("_") and not isinstance(valor, ModuleType)
    ]
    assert publicos == []
    assert not hasattr(summa_ai_framework, "__all__")
