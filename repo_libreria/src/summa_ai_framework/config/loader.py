"""Carga de la configuración YAML con las referencias `${NOMBRE}` resueltas después de parsear."""

import re
from pathlib import Path

import yaml
from pydantic import SecretStr, ValidationError

from ..security import EnvSecretProvider, SecretNotFoundError, SecretProvider
from .models import SecretsConfig, SummaConfig

_REFERENCIA = re.compile(r"\$\{([A-Za-z0-9_-]+)\}")

Ubicacion = tuple[str | int, ...]


class ConfigError(Exception):
    """Error al cargar la configuración. Su mensaje nunca contiene valores secretos."""


def _texto(ubicacion: Ubicacion) -> str:
    """`clave.subclave[índice]`, como se lee en el YAML."""
    # type() y no isinstance(): un bool (clave `on:` en YAML 1.1) es clave, no índice
    texto = "".join(f"[{p}]" if type(p) is int else f".{p}" for p in ubicacion)
    return texto.removeprefix(".") or "(raíz)"


def _resolver(
    valor: object, proveedor: SecretProvider, ubicacion: Ubicacion, resueltas: set[Ubicacion]
) -> object:
    """Sustituye cada `${NOMBRE}` por un SecretStr y anota dónde estaba."""
    if isinstance(valor, dict):
        return {k: _resolver(v, proveedor, (*ubicacion, k), resueltas) for k, v in valor.items()}
    if isinstance(valor, list):
        return [_resolver(v, proveedor, (*ubicacion, i), resueltas) for i, v in enumerate(valor)]
    if not isinstance(valor, str) or "${" not in valor:
        return valor
    referencia = _REFERENCIA.fullmatch(valor)
    if referencia is None:
        raise ConfigError(
            f"{_texto(ubicacion)}: una referencia a secreto debe ocupar el valor completo (${{NOMBRE}})"
        )
    try:
        secreto = proveedor.get_secret(referencia[1])
    except SecretNotFoundError:
        raise ConfigError(
            f"{_texto(ubicacion)}: no se encontró el secreto '{referencia[1]}' o está vacío"
        ) from None
    resueltas.add(ubicacion)
    return SecretStr(secreto)


def _describir(error: ValidationError, resueltas: set[Ubicacion], prefijo: Ubicacion = ()) -> str:
    """Ubicación y motivo de cada fallo, sin la entrada: pydantic la incluiría en su mensaje."""
    lineas = []
    for detalle in error.errors(include_url=False, include_input=False):
        ubicacion = (*prefijo, *detalle["loc"])
        motivo = detalle["msg"]
        if ubicacion in resueltas:  # se conserva el motivo: el campo puede fallar por otra razón
            motivo += " (recibe una referencia a secreto: el campo debe declararse SecretRef)"
        lineas.append(f"- {_texto(ubicacion)}: {motivo}")
    return "\n".join(lineas)


def _leer(ruta: Path) -> dict[str, object]:
    """El YAML parseado, sin resolver; vacío equivale a {}."""
    try:
        datos = yaml.safe_load(ruta.read_text(encoding="utf-8"))
    except OSError as e:
        motivo = e.strerror or type(e).__name__
        raise ConfigError(f"No se pudo leer la configuración {ruta}: {motivo}") from None
    except UnicodeDecodeError:  # su .object lleva los bytes del archivo: no se encadena
        raise ConfigError(f"{ruta}: el archivo no está en UTF-8") from None
    # El parser también lanza ValueError (fechas imposibles como 2024-02-30) y RecursionError
    # (anidamiento profundo). El texto solo tiene nombres de referencias, nunca valores.
    except (yaml.YAMLError, ValueError, RecursionError) as e:
        raise ConfigError(f"YAML inválido en {ruta}: {e}") from None
    if datos is None:
        return {}
    if not isinstance(datos, dict):
        raise ConfigError(f"{ruta}: la raíz del YAML debe ser un mapa de claves")
    return datos


def load_config[T: SummaConfig](path: str | Path, schema: type[T]) -> T:
    """Lee el YAML de `path`, resuelve sus referencias a secretos y lo valida con `schema`.

    `schema` es SummaConfig o la subclase de la plantilla. Cualquier fallo es ConfigError.
    """
    ruta = Path(path)
    datos = _leer(ruta)
    try:
        SecretsConfig.model_validate(datos.get("secrets") or {})  # solo "env" hasta LIB-03
    except ValidationError as e:
        detalle = _describir(e, set(), ("secrets",))
        raise ConfigError(f"{ruta}: configuración inválida\n{detalle}") from None

    resueltas: set[Ubicacion] = set()
    try:
        proveedor = EnvSecretProvider()
        # secrets no se resuelve: dice cómo resolver todo lo demás
        resuelto = {
            k: v if k == "secrets" else _resolver(v, proveedor, (k,), resueltas)
            for k, v in datos.items()
        }
        return schema.model_validate(resuelto)
    except ConfigError as e:
        raise ConfigError(f"{ruta}: {e}") from None
    except RecursionError:
        # shortcut: corta los alias circulares (a: &a [*a]); una cadena de alias acíclica
        # se recorre entera. Si el YAML dejara de versionarlo el propio equipo, limitar los alias.
        raise ConfigError(f"{ruta}: el YAML tiene alias circulares") from None
    except ValidationError as e:
        raise ConfigError(f"{ruta}: configuración inválida\n{_describir(e, resueltas)}") from None
