"""Step de humo en Python puro: no ejecuta al importarse e informa el entorno."""

import importlib
import platform
import runpy
import sys
from importlib.metadata import version
from pathlib import Path

import pytest
import steps.s00_humo
from steps.s00_humo import ejecutar, main


def test_importar_no_imprime_nada(capsys: pytest.CaptureFixture[str]) -> None:
    sys.modules.pop("steps.s00_humo", None)
    importlib.import_module("steps.s00_humo")
    assert capsys.readouterr().out == ""


def test_ejecutar_en_local(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABRICKS_RUNTIME_VERSION", raising=False)
    assert ejecutar("dev") == {
        "ambiente": "dev",
        "python": platform.python_version(),
        "runtime": "local",
        "summa_ai_framework": version("summa-ai-framework"),
    }


def test_como_script_termina_sin_system_exit(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # En Databricks el script corre dentro de IPython: un SystemExit, incluso con 0,
    # marca la tarea como fallida (visto en serverless, 2026-11-18)
    script = Path(steps.s00_humo.__file__)
    monkeypatch.setattr(sys, "argv", [str(script), "--ambiente", "dev"])
    runpy.run_path(str(script), run_name="__main__")
    assert "[HUMO] ambiente: dev" in capsys.readouterr().out


def test_main_imprime_y_devuelve_cero(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("DATABRICKS_RUNTIME_VERSION", "18.0")
    assert main(["--ambiente", "prod"]) == 0
    assert capsys.readouterr().out.splitlines() == [
        "[HUMO] ambiente: prod",
        f"[HUMO] python: {platform.python_version()}",
        "[HUMO] runtime: 18.0",
        f"[HUMO] summa_ai_framework: {version('summa-ai-framework')}",
    ]
