from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from ui.common.paths import SETTINGS_ICON
from ui.widgets.sidebar.settings_button import SettingsButton

# =============================================================================
# INITIALIZATION
# =============================================================================


def test_initialization_sets_object_name(
    qtbot,
):
    """
    Comprueba que se establece el nombre del objeto.
    """

    button = SettingsButton()

    qtbot.addWidget(button)

    assert button.objectName() == "settings_button"


def test_initialization_sets_icon(
    qtbot,
):
    """
    Comprueba que se establece el icono del botón.
    """

    button = SettingsButton()

    qtbot.addWidget(button)

    assert not button.icon().isNull()


def test_initialization_sets_tooltip(
    qtbot,
):
    """
    Comprueba que se establece el tooltip.
    """

    button = SettingsButton()

    qtbot.addWidget(button)

    assert button.toolTip() == "Settings"


def test_initialization_sets_pointing_hand_cursor(
    qtbot,
):
    """
    Comprueba que se establece el cursor de tipo mano.
    """

    button = SettingsButton()

    qtbot.addWidget(button)

    assert button.cursor().shape() == Qt.CursorShape.PointingHandCursor
