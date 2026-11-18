"""Proveedor de secretos por variables de entorno."""

import pytest
from summa_ai_framework.security import EnvSecretProvider, SecretNotFoundError


def test_devuelve_la_variable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SUMMA_TEST_CLAVE", "valor")
    assert EnvSecretProvider().get_secret("SUMMA_TEST_CLAVE") == "valor"


@pytest.mark.parametrize("valor", [None, ""], ids=["ausente", "vacia"])
def test_ausente_o_vacia_es_error(monkeypatch: pytest.MonkeyPatch, valor: str | None) -> None:
    monkeypatch.delenv("SUMMA_TEST_CLAVE", raising=False)
    if valor is not None:
        monkeypatch.setenv("SUMMA_TEST_CLAVE", valor)
    with pytest.raises(SecretNotFoundError) as error:
        EnvSecretProvider().get_secret("SUMMA_TEST_CLAVE")
    assert isinstance(error.value, LookupError)
    assert error.value.name == "SUMMA_TEST_CLAVE"
