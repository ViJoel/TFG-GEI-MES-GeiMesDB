from unittest.mock import MagicMock

import pytest

import modules.connections.service as service
from entities.connection import Connection

# =============================================================================
# FIXTURES: MOCK DEL MODEL
# =============================================================================


@pytest.fixture(autouse=True)
def mock_model(monkeypatch):
    """
    Sustituye la capa de model por mocks
    (aislamiento total de la lógica de BD).
    """

    monkeypatch.setattr(service, "gac", MagicMock())
    monkeypatch.setattr(service, "cc", MagicMock())
    monkeypatch.setattr(service, "uc", MagicMock())
    monkeypatch.setattr(service, "dc", MagicMock())
    monkeypatch.setattr(service, "ce", MagicMock())


# =============================================================================
# get_connections
# =============================================================================


def test_get_connections():
    """
    Verifica que get_connections delega
    correctamente en la capa de model
    y devuelve el resultado esperado.
    """

    service.gac.return_value = ["conn1", "conn2"]

    result = service.get_connections()

    service.gac.assert_called_once()
    assert result == ["conn1", "conn2"]


# =============================================================================
# create_connection
# =============================================================================


def test_create_connection():
    """
    Verifica que create_connection llama
    correctamente al model pasando la
    conexión como parámetro nombrado.
    """

    conn = Connection(id="1")

    service.create_connection(conn)

    service.cc.assert_called_once_with(connection=conn)


# =============================================================================
# update_connection
# =============================================================================


def test_update_connection():
    """
    Verifica que update_connection delega
    correctamente la actualización al model
    con el objeto Connection recibido.
    """

    conn = Connection(id="1")

    service.update_connection(conn)

    service.uc.assert_called_once_with(connection=conn)


# =============================================================================
# delete_connection
# =============================================================================


def test_delete_connection():
    """
    Verifica que delete_connection delega
    correctamente la eliminación de la
    conexión al model.
    """

    conn = Connection(id="1")

    service.delete_connection(conn)

    service.dc.assert_called_once_with(connection=conn)


# =============================================================================
# connection_exists
# =============================================================================


def test_connection_exists():
    """
    Verifica que connection_exists delega
    correctamente en el model y devuelve
    el valor booleano esperado.
    """

    service.ce.return_value = True

    result = service.connection_exists("123")

    service.ce.assert_called_once_with(connection_id="123")
    assert result is True
