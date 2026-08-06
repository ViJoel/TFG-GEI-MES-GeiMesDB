from dataclasses import replace

import keyring
from cryptography.fernet import Fernet

from common.constants import APP_NAME
from entities.connection import Connection

# =================
# === VARIABLES ===
# =================

# Nombre del servicio utilizado por keyring para identificar
# las credenciales pertenecientes a esta aplicación.
#
# En Windows aparecerá como una entrada dentro del
# Administrador de credenciales.
_SERVICE_NAME = APP_NAME

# Nombre con el que se almacena la clave de cifrado
# dentro del almacén seguro del sistema operativo.
#
# La aplicación únicamente necesita una clave maestra,
# reutilizada para cifrar todas las conexiones.
_KEY_NAME = "fernet_key"

# ===================
# === PRIVATE API ===
# ===================


def _get_cipher() -> Fernet:
    """
    Recupera el cifrador de la aplicación.

    Si todavía no existe una clave maestra almacenada
    en el sistema operativo, se genera automáticamente
    y se registra mediante keyring.

    Returns:
        Fernet:
            Instancia preparada para cifrar y descifrar.
    """

    # Intenta recuperar la clave maestra desde el
    # almacén seguro del sistema operativo.
    key = keyring.get_password(
        _SERVICE_NAME,
        _KEY_NAME,
    )

    # Primera ejecución de la aplicación.
    #
    # Si todavía no existe ninguna clave registrada,
    # se genera una nueva y se almacena de forma segura
    # mediante keyring.
    if key is None:

        # Fernet genera una clave binaria.
        # Se convierte a str para que keyring
        # pueda almacenarla sin problemas.
        key = Fernet.generate_key().decode()

        keyring.set_password(
            _SERVICE_NAME,
            _KEY_NAME,
            key,
        )

    # Reconstruye el objeto Fernet a partir
    # de la clave almacenada.
    return Fernet(key.encode())


# El objeto Fernet se inicializa una única vez al importar
# el módulo.
#
# De esta forma evitamos consultar keyring en cada operación
# de cifrado o descifrado.
#
# Instancia compartida utilizada por todas las operaciones
# de cifrado y descifrado.
_CIPHER = _get_cipher()


def _encrypt_str(
    value: str | None,
) -> str | None:
    """
    Cifra un valor `str` de texto.

    Args:
        value (str | None):
            Texto a cifrar.

    Returns:
        str | None:
            Texto cifrado o None si el valor de entrada es None.
    """

    # Mantiene el comportamiento de los campos opcionales.
    if value is None:
        return None

    # Fernet opera sobre bytes.
    # El resultado vuelve a convertirse a str para poder
    # almacenarlo directamente en SQLite.
    return _CIPHER.encrypt(
        value.encode(),
    ).decode()


def _decrypt_str(
    value: str | None,
) -> str | None:
    """
    Descifra un valor `str` previamente cifrado.

    Args:
        value (str | None):
            Texto cifrado.

    Returns:
        str | None:
            Texto descifrado o None si el valor de entrada es None.
    """

    # Mantiene el comportamiento de los campos opcionales.
    if value is None:
        return None

    # Convierte el texto cifrado a bytes, lo descifra
    # y devuelve nuevamente un str listo para ser utilizado
    # por el resto de la aplicación.
    return _CIPHER.decrypt(
        value.encode(),
    ).decode()


def _encrypt_int(
    port: int | None,
) -> str | None:
    """
    Cifra un valor `int` correspondiente al puerto.

    Args:
        port (int | None):
            Puerto a cifrar.

    Returns:
        str | None:
            Puerto cifrado o None si el valor de entrada es None.
    """

    if port is None:
        return None

    return _encrypt_str(str(port))


def _decrypt_int(
    port: str | None,
) -> int | None:
    """
    Descifra un valor `int` correspondiente al puerto.

    Args:
        port (str | None):
            Puerto cifrado.

    Returns:
        int | None:
            Puerto descifrado o None si el valor de entrada es None.
    """

    if port is None:
        return None

    return int(_decrypt_str(port))


# ==================
# === PUBLIC API ===
# ==================


def encrypt(
    connection: Connection,
) -> Connection:
    """
    Devuelve una copia cifrada de una conexión.

    La instancia original no es modificada.

    Args:
        connection (Connection):
            Conexión en texto plano.

    Returns:
        Connection:
            Nueva conexión con los campos sensibles cifrados.
    """

    # Se utiliza dataclasses.replace() para crear una nueva
    # instancia de Connection conservando todos los atributos
    # originales y sustituyendo únicamente aquellos que deben
    # almacenarse cifrados en la base de datos.
    #
    # El nombre permanece en texto plano para permitir
    # búsquedas y ordenaciones desde SQLite.
    return replace(
        connection,
        name=connection.name,
        host=_encrypt_str(connection.host),
        port=_encrypt_int(connection.port),
        database=_encrypt_str(connection.database),
        username=_encrypt_str(connection.username),
        password=_encrypt_str(connection.password),
        path=_encrypt_str(connection.path),
    )


def decrypt(
    connection: Connection,
) -> Connection:
    """
    Devuelve una copia descifrada de una conexión.

    La instancia original no es modificada.

    Args:
        connection (Connection):
            Conexión cifrada.

    Returns:
        Connection:
            Nueva conexión con los campos sensibles descifrados.
    """

    # Se reconstruye una nueva entidad Connection con los
    # campos sensibles restaurados a texto plano.
    #
    # A partir de este momento el resto de la aplicación
    # trabaja exclusivamente con datos descifrados, evitando
    # realizar operaciones de cifrado/descifrado durante el
    # ciclo de vida normal de la aplicación.
    return replace(
        connection,
        name=connection.name,
        host=_decrypt_str(connection.host),
        port=_decrypt_int(connection.port),
        database=_decrypt_str(connection.database),
        username=_decrypt_str(connection.username),
        password=_decrypt_str(connection.password),
        path=_decrypt_str(connection.path),
    )
