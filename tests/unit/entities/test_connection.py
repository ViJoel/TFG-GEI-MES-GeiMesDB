import uuid

import pytest

from entities.connection import Connection
from entities.driver import Driver

# =============================================================================
# Connection
# =============================================================================


# =====================================
# Constructor
# =====================================


def test_connection_generates_id_when_not_provided():
    """
    La conexión debe generar un identificador
    automáticamente cuando no se proporciona uno.
    """
    connection = Connection()

    assert connection.id is not None


def test_connection_generates_valid_uuid():
    """
    El identificador generado automáticamente
    debe ser un UUID válido.
    """
    connection = Connection()

    uuid.UUID(connection.id)


def test_connection_keeps_provided_id():
    """
    La conexión debe conservar el identificador
    proporcionado durante su construcción.
    """
    connection = Connection(id="123")

    assert connection.id == "123"


def test_connection_requires_keyword_arguments():
    """
    La construcción de una conexión debe exigir
    el uso de argumentos con nombre.
    """
    with pytest.raises(TypeError):
        Connection("123")


# =====================================
# Valores por defecto
# =====================================


def test_default_name_is_empty():
    """
    El nombre de la conexión debe ser una cadena
    vacía por defecto.
    """
    connection = Connection()

    assert connection.name == ""


def test_default_driver_is_postgresql():
    """
    El driver por defecto debe ser PostgreSQL.
    """
    connection = Connection()

    assert connection.driver == Driver.POSTGRESQL


def test_default_host_is_none():
    """
    El host debe ser None por defecto.
    """
    connection = Connection()

    assert connection.host is None


def test_default_port_is_none():
    """
    El puerto debe ser None por defecto.
    """
    connection = Connection()

    assert connection.port is None


def test_default_database_is_none():
    """
    La base de datos debe ser None por defecto.
    """
    connection = Connection()

    assert connection.database is None


def test_default_username_is_none():
    """
    El nombre de usuario debe ser None por
    defecto.
    """
    connection = Connection()

    assert connection.username is None


def test_default_password_is_none():
    """
    La contraseña debe ser None por defecto.
    """
    connection = Connection()

    assert connection.password is None


def test_default_path_is_none():
    """
    La ruta del archivo debe ser None por
    defecto.
    """
    connection = Connection()

    assert connection.path is None


# =====================================
# Constructor con valores
# =====================================


def test_constructor_assigns_name():
    """
    El constructor debe asignar correctamente el
    nombre de la conexión.
    """
    connection = Connection(name="Local")

    assert connection.name == "Local"


def test_constructor_assigns_driver():
    """
    El constructor debe asignar correctamente el
    driver de la conexión.
    """
    connection = Connection(driver=Driver.SQLITE)

    assert connection.driver == Driver.SQLITE


def test_constructor_assigns_host():
    """
    El constructor debe asignar correctamente el
    host de la conexión.
    """
    connection = Connection(host="localhost")

    assert connection.host == "localhost"


def test_constructor_assigns_port():
    """
    El constructor debe asignar correctamente el
    puerto de la conexión.
    """
    connection = Connection(port=5432)

    assert connection.port == 5432


def test_constructor_assigns_database():
    """
    El constructor debe asignar correctamente la
    base de datos.
    """
    connection = Connection(database="sakila")

    assert connection.database == "sakila"


def test_constructor_assigns_username():
    """
    El constructor debe asignar correctamente el
    nombre de usuario.
    """
    connection = Connection(username="admin")

    assert connection.username == "admin"


def test_constructor_assigns_password():
    """
    El constructor debe asignar correctamente la
    contraseña.
    """
    connection = Connection(password="secret")

    assert connection.password == "secret"


def test_constructor_assigns_path():
    """
    El constructor debe asignar correctamente la
    ruta del archivo de base de datos.
    """
    connection = Connection(path="/tmp/test.db")

    assert connection.path == "/tmp/test.db"


# =====================================
# Igualdad
# =====================================


def test_connections_with_same_id_are_equal():
    """
    Dos conexiones con el mismo identificador
    deben considerarse iguales.
    """
    c1 = Connection(id="1")
    c2 = Connection(id="1")

    assert c1 == c2


def test_connections_with_different_id_are_not_equal():
    """
    Dos conexiones con distinto identificador no
    deben considerarse iguales.
    """
    c1 = Connection(id="1")
    c2 = Connection(id="2")

    assert c1 != c2


def test_connection_is_equal_to_itself():
    """
    Una conexión debe ser igual a sí misma.
    """
    connection = Connection()

    assert connection == connection


def test_connection_is_not_equal_to_none():
    """
    Una conexión no debe ser igual a None.
    """
    connection = Connection()

    assert connection != None


def test_connection_is_not_equal_to_string():
    """
    Una conexión no debe ser igual a una cadena.
    """
    connection = Connection()

    assert connection != "connection"


def test_connection_is_not_equal_to_integer():
    """
    Una conexión no debe ser igual a un número
    entero.
    """
    connection = Connection()

    assert connection != 1


def test_equality_depends_only_on_id():
    """
    La igualdad entre conexiones debe depender
    únicamente de su identificador.
    """

    c1 = Connection(
        id="1",
        name="Local",
        driver=Driver.SQLITE,
        path="/tmp/local.db",
    )

    c2 = Connection(
        id="1",
        name="Producción",
        driver=Driver.POSTGRESQL,
        host="192.168.1.100",
        port=5432,
        database="empresa",
        username="admin",
        password="1234",
    )

    assert c1 == c2
