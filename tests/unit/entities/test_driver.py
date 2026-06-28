import pytest

from src.entities.driver import Driver

# ========================
# === VALORES DEL ENUM ===
# ========================


def test_postgresql_value():
    assert Driver.POSTGRESQL.value == "postgresql"


def test_mysql_value():
    assert Driver.MYSQL.value == "mysql"


def test_sqlite_value():
    assert Driver.SQLITE.value == "sqlite"


def test_oracle_value():
    assert Driver.ORACLE.value == "oracle"


# ===================
# === CONSTRUCTOR ===
# ===================


def test_create_postgresql_driver_from_string():
    assert Driver("postgresql") is Driver.POSTGRESQL


def test_create_mysql_driver_from_string():
    assert Driver("mysql") is Driver.MYSQL


def test_create_sqlite_driver_from_string():
    assert Driver("sqlite") is Driver.SQLITE


def test_create_oracle_driver_from_string():
    assert Driver("oracle") is Driver.ORACLE


def test_driver_without_value_raises_type_error():
    with pytest.raises(TypeError):
        Driver()


def test_empty_driver_raises_value_error():
    with pytest.raises(ValueError):
        Driver("")


def test_invalid_driver_raises_value_error():
    with pytest.raises(ValueError):
        Driver("a")


def test_blank_driver_raises_value_error():
    with pytest.raises(ValueError):
        Driver(" ")
