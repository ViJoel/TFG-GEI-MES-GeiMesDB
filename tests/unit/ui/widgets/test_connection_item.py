from unittest.mock import patch

import pytest

from entities.connection import Connection
from entities.driver import Driver
from ui.widgets.sidebar.connection_item import ConnectionItem

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def connection():
    """
    Construye una conexión de prueba.
    """

    return Connection(
        id="1",
        name="Test connection",
        driver=Driver.POSTGRESQL,
    )


@pytest.fixture
def item(qtbot, connection):
    """
    Construye un ConnectionItem.
    """

    widget = ConnectionItem(connection)

    qtbot.addWidget(widget)
    widget.show()

    return widget


# =============================================================================
# INITIALIZATION
# =============================================================================


def test_item_is_created(item, connection):
    """
    Verifica que el widget se crea correctamente.
    """

    assert item.objectName() == "connection_item"
    assert item.connection is connection
    assert item.isVisible()


# =============================================================================
# UI STATE
# =============================================================================


def test_set_selected_sets_selected_property(item):
    """
    Verifica que el estado seleccionado se establece correctamente.
    """

    item.set_selected(True)

    assert item.property("selected") == "true"


def test_set_selected_clears_selected_property(item):
    """
    Verifica que el estado seleccionado puede desactivarse.
    """

    item.set_selected(False)

    assert item.property("selected") == "false"


def test_connected_state_is_set_when_session_exists(connection):
    """
    Verifica que el estado es conectado cuando existe una sesión.
    """

    with patch(
        "ui.widgets.sidebar.connection_item.has_session",
        return_value=True,
    ):
        item = ConnectionItem(connection)

    assert item.property("state") == "connected"


def test_disconnected_state_is_set_when_session_does_not_exist(connection):
    """
    Verifica que el estado es desconectado cuando no existe una sesión.
    """

    with patch(
        "ui.widgets.sidebar.connection_item.has_session",
        return_value=False,
    ):
        item = ConnectionItem(connection)

    assert item.property("state") == "disconnected"


# =============================================================================
# UI HELPERS
# =============================================================================


@pytest.mark.parametrize(
    "driver",
    [
        Driver.POSTGRESQL,
        Driver.MYSQL,
        Driver.SQLITE,
        Driver.ORACLE,
    ],
)
def test_get_driver_icon_returns_icon_for_supported_drivers(
    connection,
    driver,
):
    """
    Verifica que cada driver soportado devuelve un icono.
    """

    connection.driver = driver

    item = ConnectionItem(connection)

    assert not item._get_driver_icon().isNull()


def test_get_driver_icon_returns_empty_icon_for_unknown_driver(
    connection,
):
    """
    Verifica que un driver desconocido devuelve un icono vacío.
    """

    connection.driver = None

    item = ConnectionItem(connection)

    assert item._get_driver_icon().isNull()
