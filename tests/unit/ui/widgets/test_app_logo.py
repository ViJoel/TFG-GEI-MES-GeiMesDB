import pytest
from PySide6.QtCore import Qt

from ui.widgets.logos.app_logo import AppLogo

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def logo(qtbot):
    """
    Crea un logo con el tamaño por defecto.
    """

    logo = AppLogo()

    qtbot.addWidget(logo)
    logo.show()

    return logo


# =============================================================================
# INITIALIZATION
# =============================================================================


def test_logo_is_created(logo):
    """
    Verifica que el logo se crea correctamente.
    """

    assert logo.objectName() == "app_logo"
    assert logo.isVisible()


def test_logo_uses_default_size(logo):
    """
    Verifica que el logo utiliza el tamaño por defecto.
    """

    assert logo.size == 60


def test_logo_accepts_custom_size(qtbot):
    """
    Verifica que el logo acepta un tamaño personalizado.
    """

    logo = AppLogo(size=120)

    qtbot.addWidget(logo)

    assert logo.size == 120


# =============================================================================
# UI
# =============================================================================


def test_logo_loads_a_pixmap(logo):
    """
    Verifica que el logo carga una imagen.
    """

    assert logo.pixmap() is not None


def test_logo_pixmap_respects_maximum_size(logo):
    """
    Verifica que la imagen no supera el tamaño configurado.
    """

    pixmap = logo.pixmap()

    assert pixmap.width() <= logo.size
    assert pixmap.height() <= logo.size


def test_logo_is_center_aligned(logo):
    """
    Verifica que el logo se muestra centrado.
    """

    assert logo.alignment() == Qt.AlignmentFlag.AlignCenter
