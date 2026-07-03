from unittest.mock import MagicMock

import pytest

import ui.app.app_state as app_state
from entities.connection import Connection

# =============================================================================
# FIXTURE
# =============================================================================


@pytest.fixture(autouse=True)
def reset_state(monkeypatch):
    """
    Restablece el estado global antes de cada test.
    """

    app_state.set_selected_connection(None)

    monkeypatch.setattr(app_state, "logger", MagicMock())


# =============================================================================
# SELECTED CONNECTION
# =============================================================================


def test_set_selected_connection_stores_connection():
    """
    Verifica que la conexión queda registrada.
    """

    connection = Connection(
        id="1",
        name="Test",
    )

    app_state.set_selected_connection(connection)

    assert app_state.get_selected_connection() is connection


def test_set_selected_connection_none_clears_connection():
    """
    Verifica que puede eliminar la conexión seleccionada.
    """

    connection = Connection(
        id="1",
        name="Test",
    )

    app_state.set_selected_connection(connection)
    app_state.set_selected_connection(None)

    assert app_state.get_selected_connection() is None


def test_get_selected_connection_returns_none_by_default():
    """
    Verifica que inicialmente no existe conexión seleccionada.
    """

    assert app_state.get_selected_connection() is None
