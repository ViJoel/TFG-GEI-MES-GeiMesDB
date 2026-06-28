import uuid

import pytest

from entities.connection import Connection
from entities.driver import Driver

# =============================================================================
# Constructor
# =============================================================================


def test_connection_generates_id_when_not_provided():
    connection = Connection()

    assert connection.id is not None


def test_connection_generates_valid_uuid():
    connection = Connection()

    uuid.UUID(connection.id)


def test_connection_keeps_provided_id():
    connection = Connection(id="123")

    assert connection.id == "123"


def test_connection_requires_keyword_arguments():
    with pytest.raises(TypeError):
        Connection("123")


# =============================================================================
# Valores por defecto
# =============================================================================


def test_default_name_is_empty():
    connection = Connection()

    assert connection.name == ""


def test_default_driver_is_postgresql():
    connection = Connection()

    print(type(connection.driver))
    print(type(Driver.POSTGRESQL))

    print(connection.driver.__class__.__module__)
    print(Driver.POSTGRESQL.__class__.__module__)

    assert connection.driver == Driver.POSTGRESQL


def test_default_host_is_none():
    connection = Connection()

    assert connection.host is None


def test_default_port_is_none():
    connection = Connection()

    assert connection.port is None


def test_default_database_is_none():
    connection = Connection()

    assert connection.database is None


def test_default_username_is_none():
    connection = Connection()

    assert connection.username is None


def test_default_password_is_none():
    connection = Connection()

    assert connection.password is None


def test_default_path_is_none():
    connection = Connection()

    assert connection.path is None


# =============================================================================
# Constructor con valores
# =============================================================================


def test_constructor_assigns_name():
    connection = Connection(name="Local")

    assert connection.name == "Local"


def test_constructor_assigns_driver():
    connection = Connection(driver=Driver.SQLITE)

    assert connection.driver == Driver.SQLITE


def test_constructor_assigns_host():
    connection = Connection(host="localhost")

    assert connection.host == "localhost"


def test_constructor_assigns_port():
    connection = Connection(port=5432)

    assert connection.port == 5432


def test_constructor_assigns_database():
    connection = Connection(database="sakila")

    assert connection.database == "sakila"


def test_constructor_assigns_username():
    connection = Connection(username="admin")

    assert connection.username == "admin"


def test_constructor_assigns_password():
    connection = Connection(password="secret")

    assert connection.password == "secret"


def test_constructor_assigns_path():
    connection = Connection(path="/tmp/test.db")

    assert connection.path == "/tmp/test.db"


# =============================================================================
# Igualdad
# =============================================================================


def test_connections_with_same_id_are_equal():
    c1 = Connection(id="1")
    c2 = Connection(id="1")

    assert c1 == c2


def test_connections_with_different_id_are_not_equal():
    c1 = Connection(id="1")
    c2 = Connection(id="2")

    assert c1 != c2


def test_connection_is_equal_to_itself():
    connection = Connection()

    assert connection == connection


def test_connection_is_not_equal_to_none():
    connection = Connection()

    assert connection != None


def test_connection_is_not_equal_to_string():
    connection = Connection()

    assert connection != "connection"


def test_connection_is_not_equal_to_integer():
    connection = Connection()

    assert connection != 1


def test_equality_depends_only_on_id():
    c1 = Connection(id="1", name="Local", driver=Driver.SQLITE, path="/tmp/local.db")

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
