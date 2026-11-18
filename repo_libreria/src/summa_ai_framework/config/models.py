"""Esquemas base de la configuración: cada feature añade su sección y cada plantilla los extiende."""

from typing import Annotated, Literal

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, SecretStr


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
    """Cómo se resuelven las referencias. Key Vault llega en LIB-03."""

    provider: Literal["env"] = "env"


class SummaConfig(ConfigModel):
    """Esquema raíz. Las plantillas lo extienden con una subclase para sus secciones propias."""

    secrets: SecretsConfig = Field(default_factory=SecretsConfig)
