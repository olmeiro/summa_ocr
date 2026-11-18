"""Proveedores de secretos: variables de entorno y Key Vault (con un cliente doble)."""

from dataclasses import dataclass, field

import pytest
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceNotFoundError,
)
from azure.keyvault.secrets import SecretClient
from summa_ai_framework.security import (
    EnvSecretProvider,
    KeyVaultSecretProvider,
    SecretError,
    SecretNotFoundError,
)

VAULT = "https://kv-prueba.vault.azure.net/"


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


@dataclass
class Secreto:
    value: str | None


@dataclass
class ClienteDoble:
    """Hace de SecretClient: guarda los nombres pedidos y responde o lanza lo configurado."""

    secretos: dict[str, str | None] = field(default_factory=dict)
    error: Exception | None = None
    pedidos: list[str] = field(default_factory=list)

    def get_secret(self, name: str) -> Secreto:
        self.pedidos.append(name)
        if self.error is not None:
            raise self.error
        if name not in self.secretos:
            raise ResourceNotFoundError("SecretNotFound")
        return Secreto(self.secretos[name])


def test_key_vault_traduce_el_nombre_y_cachea() -> None:
    cliente = ClienteDoble({"AZURE-OPENAI-KEY": "valor"})
    proveedor = KeyVaultSecretProvider(VAULT, client=cliente)
    assert proveedor.get_secret("AZURE_OPENAI_KEY") == "valor"
    assert proveedor.get_secret("AZURE_OPENAI_KEY") == "valor"
    assert cliente.pedidos == ["AZURE-OPENAI-KEY"]


@pytest.mark.parametrize("secretos", [{}, {"CLAVE-X": ""}, {"CLAVE-X": None}])
def test_key_vault_inexistente_o_vacio(secretos: dict[str, str | None]) -> None:
    proveedor = KeyVaultSecretProvider(VAULT, client=ClienteDoble(secretos))
    with pytest.raises(SecretNotFoundError) as error:
        proveedor.get_secret("CLAVE_X")
    assert isinstance(error.value, SecretError) and isinstance(error.value, LookupError)
    assert error.value.name == "CLAVE_X"


@pytest.mark.parametrize(
    ("error_azure", "tipo"),
    [
        (ClientAuthenticationError("DefaultAzureCredential failed\nmás detalle"), "ClientAuth"),
        (HttpResponseError("(Forbidden) Caller is not authorized"), "HttpResponseError"),
        # La política de autenticación de Key Vault lanza ValueError, no AzureError
        (ValueError("The challenge resource does not match the requested domain"), "ValueError"),
    ],
    ids=["sin-credencial", "sin-permiso", "dominio-distinto"],
)
def test_key_vault_otros_errores_son_secret_error(error_azure: Exception, tipo: str) -> None:
    proveedor = KeyVaultSecretProvider(VAULT, client=ClienteDoble(error=error_azure))
    with pytest.raises(SecretError) as error:
        proveedor.get_secret("CLAVE_X")
    assert not isinstance(error.value, SecretNotFoundError)
    assert "'CLAVE_X'" in str(error.value) and tipo in str(error.value)
    assert "\n" not in str(error.value)  # solo la primera línea del motivo
    assert error.value.__cause__ is None and error.value.__suppress_context__


def test_un_cliente_inyectado_que_se_evalua_falso_se_usa_igual() -> None:
    class ClienteFalso(ClienteDoble):
        def __bool__(self) -> bool:
            return False

    cliente = ClienteFalso({"CLAVE-X": "valor"})
    assert KeyVaultSecretProvider(VAULT, client=cliente).get_secret("CLAVE_X") == "valor"
    assert cliente.pedidos == ["CLAVE-X"]


def test_sin_cliente_usa_secret_client_del_vault() -> None:
    # Construirlo no llama a la red: la credencial se resuelve en la primera lectura
    proveedor = KeyVaultSecretProvider(VAULT)
    assert isinstance(proveedor._client, SecretClient)
    assert proveedor._client.vault_url == VAULT.rstrip("/")
