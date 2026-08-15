import pytest

from entities.connection import Connection
from entities.driver import Driver
from modules.connections.crypto import (
    _decrypt_int,
    _decrypt_str,
    _encrypt_int,
    _encrypt_str,
    decrypt,
    encrypt,
)

# =============================================================================
# _encrypt_str / _decrypt_str
# =============================================================================


def test_encrypt_str_returns_encrypted_value():
    """
    Comprueba que un texto se cifra correctamente.
    """

    encrypted = _encrypt_str("hello")

    assert encrypted != "hello"
    assert isinstance(encrypted, str)


def test_encrypt_str_none():
    """
    Comprueba que None permanece como None.
    """

    assert _encrypt_str(None) is None


def test_decrypt_str_returns_original_value():
    """
    Comprueba que un texto cifrado se recupera correctamente.
    """

    encrypted = _encrypt_str("hello")

    assert _decrypt_str(encrypted) == "hello"


def test_decrypt_str_none():
    """
    Comprueba que None permanece como None.
    """

    assert _decrypt_str(None) is None


# =============================================================================
# _encrypt_int / _decrypt_int
# =============================================================================


def test_encrypt_int_returns_encrypted_value():
    """
    Comprueba que un puerto se cifra correctamente.
    """

    encrypted = _encrypt_int(5432)

    assert encrypted != "5432"
    assert isinstance(encrypted, str)


def test_encrypt_int_none():
    """
    Comprueba que None permanece como None.
    """

    assert _encrypt_int(None) is None


def test_decrypt_int_returns_original_value():
    """
    Comprueba que un puerto cifrado se recupera correctamente.
    """

    encrypted = _encrypt_int(5432)

    assert _decrypt_int(encrypted) == 5432


def test_decrypt_int_none():
    """
    Comprueba que None permanece como None.
    """

    assert _decrypt_int(None) is None


# =============================================================================
# encrypt / decrypt
# =============================================================================


@pytest.mark.parametrize(
    "connection",
    [
        Connection(
            id="sqlite",
            name="SQLite",
            driver=Driver.SQLITE,
            path="/tmp/test.db",
        ),
        Connection(
            id="postgres",
            name="PostgreSQL",
            driver=Driver.POSTGRESQL,
            host="localhost",
            port=5432,
            database="postgres",
            username="postgres",
            password="secret",
        ),
    ],
)
def test_encrypt_returns_new_connection(connection: Connection):
    """
    Comprueba que encrypt devuelve una copia nueva
    manteniendo la identidad pero con los campos sensibles cifrados.
    """

    encrypted = encrypt(connection)

    # Es un objeto diferente en memoria
    assert encrypted is not connection

    # Sigue siendo la misma entidad
    assert encrypted.id == connection.id

    # Los campos públicos permanecen iguales
    assert encrypted.name == connection.name
    assert encrypted.driver == connection.driver

    # Los campos sensibles se cifran
    sensitive_fields = [
        "host",
        "port",
        "database",
        "username",
        "password",
        "path",
    ]

    for field in sensitive_fields:
        original = getattr(connection, field)
        encrypted_value = getattr(encrypted, field)

        if original is not None:
            assert encrypted_value != original

    # La original no se modifica
    assert connection.host == "localhost" if connection.host else True
    assert connection.password == "secret" if connection.password else True
    assert connection.port == 5432 if connection.port else True


@pytest.mark.parametrize(
    "connection,sensitive_fields",
    [
        (
            Connection(
                id="sqlite",
                name="SQLite",
                driver=Driver.SQLITE,
                path="/tmp/test.db",
            ),
            ("path",),
        ),
        (
            Connection(
                id="postgres",
                name="PostgreSQL",
                driver=Driver.POSTGRESQL,
                host="localhost",
                port=5432,
                database="postgres",
                username="postgres",
                password="secret",
            ),
            (
                "host",
                "port",
                "database",
                "username",
                "password",
            ),
        ),
    ],
)
def test_encrypt_encrypts_sensitive_fields(
    connection: Connection,
    sensitive_fields: tuple[str, ...],
):
    """
    Comprueba que los campos sensibles se almacenan cifrados.
    """

    encrypted = encrypt(connection)

    for field in sensitive_fields:
        assert getattr(encrypted, field) != getattr(connection, field)


@pytest.mark.parametrize(
    "connection",
    [
        Connection(
            id="sqlite",
            name="SQLite",
            driver=Driver.SQLITE,
            path="/tmp/test.db",
        ),
        Connection(
            id="postgres",
            name="PostgreSQL",
            driver=Driver.POSTGRESQL,
            host="localhost",
            port=5432,
            database="postgres",
            username="postgres",
            password="secret",
        ),
    ],
)
def test_decrypt_restores_original_connection(connection: Connection):
    """
    Comprueba que una conexión cifrada puede recuperarse
    exactamente igual que la original.
    """

    encrypted = encrypt(connection)

    decrypted = decrypt(encrypted)

    assert decrypted == connection
    assert decrypted.name == connection.name
    assert decrypted.host == connection.host
    assert decrypted.port == connection.port
    assert decrypted.database == connection.database
    assert decrypted.username == connection.username
    assert decrypted.password == connection.password
    assert decrypted.path == connection.path
