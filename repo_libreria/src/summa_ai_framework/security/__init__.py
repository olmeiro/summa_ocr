"""Identidad y secretos: proveedores que resuelven las referencias de la configuración."""

from .secrets import (
    EnvSecretProvider,
    KeyVaultSecretProvider,
    SecretError,
    SecretNotFoundError,
    SecretProvider,
)

__all__ = [
    "EnvSecretProvider",
    "KeyVaultSecretProvider",
    "SecretError",
    "SecretNotFoundError",
    "SecretProvider",
]
