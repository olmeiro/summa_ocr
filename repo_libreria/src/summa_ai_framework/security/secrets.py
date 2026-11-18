"""Proveedores de secretos: resuelven por nombre las referencias `${NOMBRE}` de la configuración."""

import os
from typing import Protocol

from azure.core.exceptions import AzureError, ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient


class SecretError(Exception):
    """No se pudo obtener un secreto. Lleva el nombre y el motivo, nunca un valor."""


class SecretNotFoundError(SecretError, LookupError):
    """El secreto pedido no existe o está vacío."""

    def __init__(self, name: str) -> None:
        super().__init__(f"No se encontró el secreto '{name}' o está vacío")
        self.name = name


class SecretProvider(Protocol):
    """Interfaz de un proveedor de secretos: variables de entorno o Key Vault."""

    def get_secret(self, name: str) -> str:
        """Devuelve el valor del secreto o lanza SecretError (SecretNotFoundError si no existe)."""
        ...


class EnvSecretProvider:
    """Lee los secretos de las variables de entorno: desarrollo local y tests."""

    def get_secret(self, name: str) -> str:
        value = os.environ.get(name)
        if not value:  # vacía cuenta como ausente: un secreto vacío nunca es válido
            raise SecretNotFoundError(name)
        return value


class _Secreto(Protocol):
    @property
    def value(self) -> str | None: ...


class _ClienteSecretos(Protocol):
    """Lo que se usa de `SecretClient`; los tests pasan un doble con esta forma."""

    def get_secret(self, name: str) -> _Secreto: ...


class KeyVaultSecretProvider:
    """Lee los secretos de Azure Key Vault con DefaultAzureCredential.

    Cada `_` del nombre se lee como `-` (Key Vault no admite `_`), así el mismo YAML sirve
    con variables de entorno. Cada secreto se pide una vez por instancia.
    """

    def __init__(self, vault_url: str, client: _ClienteSecretos | None = None) -> None:
        # Ninguno de los dos llama a la red aquí: la credencial se resuelve en la primera lectura
        self._client = (
            client if client is not None else SecretClient(vault_url, DefaultAzureCredential())
        )
        self._cache: dict[str, str] = {}

    def get_secret(self, name: str) -> str:
        if name not in self._cache:
            self._cache[name] = self._leer(name)
        return self._cache[name]

    def _leer(self, name: str) -> str:
        try:
            value = self._client.get_secret(name.replace("_", "-")).value
        except ResourceNotFoundError:
            raise SecretNotFoundError(name) from None
        # Credencial, permisos o red; la política de autenticación de Key Vault lanza además
        # ValueError (desafío inválido, dominio del vault que no coincide). El valor no se leyó.
        except (AzureError, ValueError) as e:
            resumen = (getattr(e, "message", None) or str(e)).strip().splitlines()
            motivo = f"{type(e).__name__}: {resumen[0]}" if resumen else type(e).__name__
            raise SecretError(
                f"No se pudo leer el secreto '{name}' de Key Vault ({motivo})"
            ) from None
        if not value:
            raise SecretNotFoundError(name)
        return value
