"""Prueba de integración de LIB-03 contra un Key Vault real (fuera del gate).

La ejecuta la persona: necesita su identidad de Azure (`az login`) y SUMMA_PRUEBA_KEYVAULT_URL
en el entorno, cargada desde su .env. El Key Vault debe tener el secreto SUMMA-PRUEBA-LIB-03.
Nunca imprime valores secretos, solo su longitud.

Uso: python repo_libreria/scripts/integracion_keyvault.py
"""

import os
import sys
import tempfile
from pathlib import Path

from summa_ai_framework.config import (
    ConfigError,
    ConfigModel,
    SecretRef,
    SummaConfig,
    load_config,
)


class Prueba(ConfigModel):
    api_key: SecretRef


class PruebaConfig(SummaConfig):
    prueba: Prueba


def cargar(vault_url: str, referencia: str, directorio: Path) -> PruebaConfig:
    """Carga un YAML como el de una plantilla, con Key Vault y una sola referencia."""
    ruta = directorio / "config_prueba.yaml"
    ruta.write_text(
        "secrets:\n  provider: azure_key_vault\n"
        f"  vault_url: {vault_url}\n"
        f"prueba:\n  api_key: ${{{referencia}}}\n",
        encoding="utf-8",
    )
    return load_config(ruta, PruebaConfig)


def main() -> int:
    vault_url = os.environ.get("SUMMA_PRUEBA_KEYVAULT_URL")
    if not vault_url:
        sys.exit("[INTEGRACION] FAIL: falta SUMMA_PRUEBA_KEYVAULT_URL (cárgala desde tu .env)")
    with tempfile.TemporaryDirectory() as directorio:
        try:
            config = cargar(vault_url, "SUMMA_PRUEBA_LIB_03", Path(directorio))
        except ConfigError as e:
            sys.exit(f"[INTEGRACION] FAIL: no se leyó SUMMA-PRUEBA-LIB-03\n{e}")
        largo = len(config.prueba.api_key.get_secret_value())
        print(f"[INTEGRACION] PASS: SUMMA-PRUEBA-LIB-03 leído de Key Vault ({largo} caracteres)")
        try:
            cargar(vault_url, "SUMMA_NO_EXISTE_LIB_03", Path(directorio))
        except ConfigError as e:
            print(f"[INTEGRACION] PASS: un secreto inexistente da ConfigError\n{e}")
        else:
            sys.exit("[INTEGRACION] FAIL: un secreto inexistente no dio ConfigError")
    print("[INTEGRACION] Todas las comprobaciones pasaron.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
