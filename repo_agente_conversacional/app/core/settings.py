"""Ajustes de la app desde variables de entorno con prefijo APP_.

Solo lo que el proceso necesita para arrancar; la configuración del agente irá en
config/config_<ambiente>.yaml. La app no lee archivos .env: las variables las pone
quien la ejecuta (terminal en local, -e en Docker, el Container App en Azure).
"""

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Valores de producción por defecto (tech-stack §2): documentación apagada."""

    model_config = SettingsConfigDict(env_prefix="APP_", extra="ignore")

    # Obligatoria: un despliegue sin ambiente falla al arrancar en vez de parecer "local"
    environment: Literal["local", "dev", "prod"]
    docs: bool = False
