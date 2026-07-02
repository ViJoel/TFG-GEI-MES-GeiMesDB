import pytest
from PySide6.QtWidgets import QLabel

from common.constants import APP_NAME
from ui.widgets.home.home import Home
from ui.widgets.logos.app_logo import AppLogo

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def home(qtbot):
    """
    Crea la pantalla Home.
    """

    home = Home()

    qtbot.addWidget(home)
    home.show()

    return home


# =============================================================================
# INITIALIZATION
# =============================================================================


def test_home_is_created(home):
    """
    Verifica que la pantalla Home se crea correctamente.
    """

    assert home.objectName() == "home_page"
    assert home.isVisible()


# =============================================================================
# UI
# =============================================================================


def test_home_contains_application_logo(home):
    """
    Verifica que la pantalla muestra el logo de la aplicación.
    """

    logo = home.findChild(AppLogo)

    assert logo is not None


def test_home_contains_application_title(home):
    """
    Verifica que la pantalla muestra el nombre de la aplicación.
    """

    title = home.findChild(
        QLabel,
        "home_page_title",
    )

    assert title is not None
    assert title.text() == APP_NAME


def test_home_contains_application_slogan(home):
    """
    Verifica que la pantalla muestra el eslogan de la aplicación.
    """

    slogan = home.findChild(
        QLabel,
        "home_page_slogan",
    )

    assert slogan is not None
    assert slogan.text() == "Everything you need. Nothing you don't."
