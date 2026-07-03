import pytest

from entities.driver import Driver

# =============================================================================
# Driver
# =============================================================================


# =====================================
# Valores del enumerado
# =====================================


def test_postgresql_value():
    """
    Driver.POSTGRESQL debe almacenar el valor
    'postgresql'.
    """
    assert Driver.POSTGRESQL.value == "postgresql"


def test_mysql_value():
    """
    Driver.MYSQL debe almacenar el valor
    'mysql'.
    """
    assert Driver.MYSQL.value == "mysql"


def test_sqlite_value():
    """
    Driver.SQLITE debe almacenar el valor
    'sqlite'.
    """
    assert Driver.SQLITE.value == "sqlite"


def test_oracle_value():
    """
    Driver.ORACLE debe almacenar el valor
    'oracle'.
    """
    assert Driver.ORACLE.value == "oracle"


# =====================================
# Constructor
# =====================================


def test_create_postgresql_driver_from_string():
    """
    Debe ser posible construir Driver.POSTGRESQL
    a partir de su representación en texto.
    """
    assert Driver("postgresql") is Driver.POSTGRESQL


def test_create_mysql_driver_from_string():
    """
    Debe ser posible construir Driver.MYSQL
    a partir de su representación en texto.
    """
    assert Driver("mysql") is Driver.MYSQL


def test_create_sqlite_driver_from_string():
    """
    Debe ser posible construir Driver.SQLITE
    a partir de su representación en texto.
    """
    assert Driver("sqlite") is Driver.SQLITE


def test_create_oracle_driver_from_string():
    """
    Debe ser posible construir Driver.ORACLE
    a partir de su representación en texto.
    """
    assert Driver("oracle") is Driver.ORACLE


def test_driver_without_value_raises_type_error():
    """
    El constructor debe lanzar TypeError cuando
    no se proporciona ningún valor.
    """
    with pytest.raises(TypeError):
        Driver()


def test_empty_driver_raises_value_error():
    """
    El constructor debe lanzar ValueError cuando
    se proporciona una cadena vacía.
    """
    with pytest.raises(ValueError):
        Driver("")


def test_invalid_driver_raises_value_error():
    """
    El constructor debe lanzar ValueError cuando
    se proporciona un valor no soportado.
    """
    with pytest.raises(ValueError):
        Driver("a")


def test_blank_driver_raises_value_error():
    """
    El constructor debe lanzar ValueError cuando
    se proporciona una cadena en blanco.
    """
    with pytest.raises(ValueError):
        Driver(" ")
