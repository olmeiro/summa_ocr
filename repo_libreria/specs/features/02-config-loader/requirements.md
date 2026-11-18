# 02 — config-loader — Requirements

> Contrato funcional: qué debe hacer la feature. El revisor valida el diff contra sus criterios de aceptación.

## Comportamiento esperado

1. `load_config(path, schema)` recibe la ruta de un YAML (`str` o `Path`) y un esquema que es `SummaConfig` o una subclase. Devuelve una instancia validada de ese esquema.
2. En todo el YAML salvo en la sección `secrets`, un texto que es exactamente `${NOMBRE}` se sustituye por `SecretStr(<valor del secreto NOMBRE>)` antes de validar.
3. `secrets.provider` elige el proveedor. En esta feature solo existe `env` (valor por defecto), que lee la variable de entorno `NOMBRE` con `EnvSecretProvider`.
4. Un campo declarado `SecretRef` contiene un `SecretStr` y solo acepta valores venidos de una referencia.
5. Cualquier fallo de carga se lanza como `ConfigError`, con un mensaje que dice el archivo y la ubicación (`clave.subclave[índice]`). Nunca incluye un valor secreto, ni en el mensaje ni en la cadena de excepciones.
6. `EnvSecretProvider().get_secret(nombre)` devuelve el valor de la variable de entorno. Si no existe o está vacía, lanza `SecretNotFoundError` con el nombre.
7. Harness: `scripts/revisor_ci.py` carga la spec de una feature que vive en `<proyecto>/specs/features/NN-nombre/`. La encuentra por los archivos que toca el cambio o por la rama `feature/NN-nombre`, y sigue funcionando igual con `specs/` en la raíz.

## Reglas de negocio

- **Nombres**: la API pública y las claves del YAML van en inglés; docstrings y mensajes de error, en español (decisión de la persona, 2026-11-18). El motivo que da pydantic para un campo (por ejemplo «Input should be a valid string») se incluye tal cual, en inglés: traducirlo exigiría mantener un catálogo de sus mensajes.
- **Referencias**: el nombre de una referencia cumple `[A-Za-z0-9_-]+`. Una referencia ocupa siempre el valor completo; un texto que contiene `${` y no es una referencia completa es un error (decisión de la persona, 2026-11-18).
- **Credenciales**: los esquemas de la librería y de las plantillas declaran sus credenciales como `SecretRef`. Un valor en claro en un campo `SecretRef` es un error, y una referencia en un campo que no es `SecretRef` (o `SecretStr`) también ([[mission]], principio 5; [[tech-stack]] §8).
- **Claves desconocidas**: cualquier `ConfigModel` las rechaza (`extra="forbid"`).
- **La sección `secrets` no se resuelve**: sus valores son literales.
- **API pública**:
  - `summa_ai_framework.config`: `ConfigError`, `ConfigModel`, `SecretRef`, `SecretsConfig`, `SummaConfig` y `load_config`;
  - `summa_ai_framework.security`: `SecretProvider`, `EnvSecretProvider` y `SecretNotFoundError`.

## Casos borde

- Archivo vacío o solo con comentarios: equivale a `{}` y devuelve los valores por defecto (`secrets.provider = "env"`).
- Raíz del YAML que no es un mapa (una lista, un escalar): `ConfigError`.
- Archivo inexistente o ilegible: `ConfigError` con la ruta.
- Archivo que no está en UTF-8 (por ejemplo cp1252 con tildes): `ConfigError` con la ruta, sin los bytes del archivo.
- Alias de YAML circulares (`a: &a [*a]`): `ConfigError`. Una cadena de alias acíclica se resuelve entera. Es un límite aceptado, porque el YAML lo versiona el propio equipo.
- Campo `Any` u `object` que recibe una referencia: la acepta sin error como `SecretStr`, enmascarado. Solo los campos con tipo concreto (`str`, `int`…) la rechazan.
- YAML mal formado: `ConfigError` con el error del parser. También cuando el parser lanza algo que no es `yaml.YAMLError`: `ValueError` por una fecha imposible (`2024-02-30`) o `RecursionError` por un anidamiento muy profundo. El texto del archivo solo contiene nombres de referencias, no valores, porque la resolución ocurre después.
- Secreto con caracteres de YAML (`: `, `#`, `- `, saltos de línea, comillas): se entrega literal y la estructura no cambia.
- Variable de entorno definida pero vacía: se trata como ausente.
- Referencias dentro de listas y de mapas anidados: se resuelven, y la ubicación del error incluye el índice.
- `secrets.provider` con un valor distinto de `env`: `ConfigError` (Key Vault llega en LIB-03).
- Valores no de texto (números, booleanos, `null`): no se tocan.

## Restricciones

- [[decisions]] DEC-001: `pydantic` y `PyYAML` son obligatorias porque las usan los dos consumidores. `types-PyYAML` solo va en `requirements-dev.txt`.
- [[decisions]] DEC-002: `config` y `security` son comunes y no importan nada de workflow ni de agente. `security` no importa de `config`.
- [[tech-stack]] §8: la librería no lee variables de entorno propias; solo las que nombra una referencia.
- El gate no llama a Azure.

## Criterios de aceptación

- [ ] **CA-1**: Dado un YAML con `api_key: ${CLAVE}` en un campo `SecretRef` de una subclase de `SummaConfig`, y la variable `CLAVE` en el entorno, cuando se llama a `load_config`, entonces:
  - `api_key.get_secret_value()` devuelve el valor;
  - el valor no aparece en `repr()` ni en `str()` del modelo, ni en `model_dump()` ni en `model_dump_json()`.
- [ ] **CA-2**: Dado un secreto cuyo valor contiene `: `, `#`, `- `, comillas y un salto de línea, cuando se carga, entonces llega idéntico y el resto de la configuración no cambia.
- [ ] **CA-3**: Dado un YAML que provoca uno de estos fallos, cuando se carga, entonces se lanza `ConfigError` con la ubicación y sin el valor secreto en `str(error)`, y con `__cause__` nulo y el contexto suprimido. Los fallos son:
  - un secreto ausente o vacío (el error nombra la referencia);
  - una referencia en un campo `str`;
  - un valor en claro en un campo `SecretRef`;
  - un campo de otro tipo que recibe la referencia.
- [ ] **CA-4**: Dado un texto con una referencia parcial (`Bearer ${TOKEN}`), cuando se carga, entonces se lanza `ConfigError` con su ubicación, aunque la variable exista.
- [ ] **CA-5**: Dado cualquiera de estos casos, cuando se carga, entonces se lanza `ConfigError` con la ruta o la ubicación:
  - un archivo inexistente;
  - un archivo que no está en UTF-8;
  - un YAML mal formado, una fecha imposible o un anidamiento muy profundo;
  - alias circulares;
  - una raíz que no es un mapa (lista o escalar);
  - una clave desconocida;
  - `secrets.provider: azure_key_vault`.

  Un archivo vacío (cero bytes o solo comentarios) devuelve `SummaConfig` con `secrets.provider == "env"`.
- [ ] **CA-6**: Dada una subclase de `SummaConfig` con una sección propia que incluye una lista de mapas con referencias, cuando se carga, entonces la sección se valida y cada referencia se resuelve. Si falta un secreto dentro de la lista, la ubicación del error incluye el índice.
- [ ] **CA-7**: Dado `EnvSecretProvider`, cuando se pide un nombre presente, entonces devuelve su valor. Si el nombre falta o la variable está vacía, lanza `SecretNotFoundError`, que es un `LookupError` y lleva el nombre.
- [ ] **CA-8**: Dado el paquete, entonces:
  - `pyproject.toml` declara `pydantic>=2.7,<3` y `PyYAML>=6.0.1,<7` como obligatorias;
  - el gate pasa con cobertura de al menos el 80 %;
  - el test de fronteras pasa con `config` y `security`;
  - el humo importa los dos módulos con cada extra;
  - la suite de la librería pasa con las cotas inferiores (`pydantic==2.7.0` y `PyYAML==6.0.1`).
- [ ] **CA-9**: Dado el cambio de documentación, entonces [[tech-stack]] incluye:
  - en §2, el idioma de los nombres;
  - en §5, las dependencias añadidas por LIB-01 y LIB-02;
  - en §8, las reglas de las referencias y de `SecretRef`.
- [ ] **CA-10**: Dado un cambio que toca `repo_libreria/specs/features/NN-nombre/…`, o una rama `feature/NN-nombre` cuya spec vive ahí aunque el cambio no la toque, cuando `revisor_ci.py` calcula las carpetas de feature, entonces devuelve esa carpeta. Además:
  - ignora `_plantilla` y los archivos sueltos de `specs/features/`;
  - devuelve vacío si la rama no tiene spec en el árbol;
  - los casos con `specs/` en la raíz siguen dando el mismo resultado;
  - sobre el repo real, arma el contexto de la feature 01 con sus `CA-N`.
  - `AGENTS.md` explica cómo ejecutarlo en local.
