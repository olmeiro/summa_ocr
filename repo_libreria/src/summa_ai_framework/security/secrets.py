"""Proveedores de secretos: resuelven por nombre las referencias `${NOMBRE}` de la configuración."""

import os
from typing import Protocol


class SecretNotFoundError(LookupError):
    """El secreto pedido no existe o está vacío. Solo lleva el nombre, nunca un valor."""

    def __init__(self, name: str) -> None:
        super().__init__(f"No se encontró el secreto '{name}' o está vacío")
        self.name = name


class SecretProvider(Protocol):
    """Interfaz de un proveedor de secretos (entorno; Key Vault en LIB-03)."""

    def get_secret(self, name: str) -> str:
        """Devuelve el valor del secreto o lanza SecretNotFoundError."""
        ...


class EnvSecretProvider:
    """Lee los secretos de las variables de entorno: desarrollo local y tests."""

    def get_secret(self, name: str) -> str:
        value = os.environ.get(name)
        if not value:  # vacía cuenta como ausente: un secreto vacío nunca es válido
            raise SecretNotFoundError(name)
        return value
