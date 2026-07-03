from unittest.mock import MagicMock

import pytest

from ui.app.app_context import AppContext

# =============================================================================
# FIXTURE
# =============================================================================


@pytest.fixture(autouse=True)
def clean_context():
    """
    Restablece el estado global antes y después de cada test.
    """

    AppContext.app = None
    AppContext.notification_manager = None

    yield

    AppContext.app = None
    AppContext.notification_manager = None


# =============================================================================
# APPLICATION
# =============================================================================


def test_initialize_stores_application():
    """
    Verifica que initialize registra la aplicación.
    """

    app = MagicMock()

    AppContext.initialize(app)

    assert AppContext.app is app


def test_get_app_returns_registered_application():
    """
    Verifica que get_app devuelve la aplicación registrada.
    """

    app = MagicMock()

    AppContext.initialize(app)

    assert AppContext.get_app() is app


def test_get_app_raises_if_not_initialized():
    """
    Verifica que get_app falla si no existe aplicación.
    """

    with pytest.raises(RuntimeError):
        AppContext.get_app()


# =============================================================================
# NOTIFICATION MANAGER
# =============================================================================


def test_set_notification_manager_stores_manager():
    """
    Verifica que el gestor queda registrado.
    """

    manager = MagicMock()

    AppContext.set_notification_manager(manager)

    assert AppContext.notification_manager is manager


def test_get_notification_manager_returns_registered_manager():
    """
    Verifica que devuelve el gestor registrado.
    """

    manager = MagicMock()

    AppContext.set_notification_manager(manager)

    assert AppContext.get_notification_manager() is manager


def test_get_notification_manager_raises_if_not_initialized():
    """
    Verifica que falla si no existe gestor registrado.
    """

    with pytest.raises(RuntimeError):
        AppContext.get_notification_manager()
