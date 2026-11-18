"""Esquemas base de la configuración: cada feature añade su sección y cada plantilla los extiende."""

from typing import Annotated, Literal, Self

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    HttpUrl,
    SecretStr,
    model_validator,
)


def _solo_referencias(valor: object) -> SecretStr:
    # load_config entrega cada ${NOMBRE} ya como SecretStr: cualquier otra cosa venía en claro
    if not isinstance(valor, SecretStr):
        raise ValueError("debe ser una referencia a secreto ${NOMBRE}, no un valor en claro")
    return valor


SecretRef = Annotated[SecretStr, BeforeValidator(_solo_referencias)]
"""Tipo de toda credencial en un esquema: un SecretStr que solo puede venir de `${NOMBRE}`."""


class ConfigModel(BaseModel):
    """Base de todos los esquemas: una clave desconocida en el YAML es un error, no se ignora."""

    model_config = ConfigDict(extra="forbid")


class SecretsConfig(ConfigModel):
    """Cómo se resuelven las referencias: variables de entorno o Azure Key Vault."""

    provider: Literal["env", "azure_key_vault"] = "env"
    vault_url: HttpUrl | None = None  # obligatoria con azure_key_vault

    @model_validator(mode="after")
    def _vault_url_con_key_vault(self) -> Self:
        if self.provider == "azure_key_vault" and self.vault_url is None:
            raise ValueError("vault_url es obligatoria con provider: azure_key_vault")
        return self


class SummaConfig(ConfigModel):
    """Esquema raíz. Las plantillas lo extienden con una subclase para sus secciones propias."""

    secrets: SecretsConfig = Field(default_factory=SecretsConfig)
