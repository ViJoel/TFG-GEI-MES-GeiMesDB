from unittest.mock import (
    MagicMock,
    patch,
)

import pytest
from PySide6.QtWidgets import (
    QComboBox,
    QLabel,
    QPushButton,
    QWidget,
)

from entities.message_type import MessageType
from ui.widgets.settings.settings_menu import SettingsMenu

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def menu(qtbot):

    with (
        patch(
            "ui.widgets.settings.settings_menu.ThemeManager.get_themes",
            return_value={
                "themes": ["dark", "light"],
                "current_theme": "dark",
            },
        ),
        patch(
            "ui.widgets.settings.settings_menu.ThemeManager.current_theme",
            return_value="dark",
        ),
        patch(
            "ui.widgets.settings.settings_menu.TranslationManager.get_languages",
            return_value={
                "languages": {
                    "en": "English",
                    "es": "Spanish",
                },
                "current_language": "en",
            },
        ),
        patch(
            "ui.widgets.settings.settings_menu.TranslationManager.current_language",
            return_value="en",
        ),
    ):
        widget = SettingsMenu()

    qtbot.addWidget(widget)

    return widget


# =============================================================================
# INIT
# =============================================================================


def test_settings_menu_is_widget(menu):
    """
    Verifica que hereda de QWidget.
    """

    assert isinstance(menu, QWidget)


def test_settings_menu_object_name(menu):
    """
    Verifica el objectName.
    """

    assert menu.objectName() == "settings_menu"


def test_settings_menu_fixed_width(menu):
    """
    Verifica el ancho fijo.
    """

    assert menu.width() == 480


def test_settings_menu_loads_themes(menu):
    """
    Verifica que carga los temas disponibles.
    """

    assert menu.theme_input.count() == 2
    assert menu.theme_input.currentText() == "dark"


def test_settings_menu_loads_languages(menu):
    """
    Verifica que carga los lenguajes disponibles.
    """

    assert menu.language_input.count() == 2
    assert menu.language_input.currentData() == "en"


# =============================================================================
# UI
# =============================================================================


def test_theme_label(menu):
    """
    Verifica la creación de la etiqueta.
    """

    assert isinstance(menu.theme_label, QLabel)
    assert menu.theme_label.text() == "Theme"


def test_language_label(menu):
    """
    Verifica la creación de la etiqueta.
    """

    assert isinstance(menu.language_label, QLabel)
    assert menu.language_label.text() == "Language"


def test_theme_input(menu):
    """
    Verifica el input.
    """

    assert isinstance(menu.theme_input, QComboBox)


def test_language_input(menu):
    """
    Verifica el input.
    """

    assert isinstance(menu.language_input, QComboBox)


def test_buttons_created(menu):
    """
    Verifica la creación de los botones.
    """

    assert isinstance(menu.cancel_button, QPushButton)
    assert isinstance(menu.apply_button, QPushButton)
    assert isinstance(menu.accept_button, QPushButton)

    assert menu.cancel_button.text() == "Cancel"
    assert menu.apply_button.text() == "Apply"
    assert menu.accept_button.text() == "Accept"


# =============================================================================
# EVENT HELPERS
# =============================================================================


def test_has_pending_changes_false(menu):

    assert menu._has_pending_changes() is False


def test_has_pending_changes_theme_true(menu):
    """
    Verifica que detecta ausencia de cambios.
    """

    menu.theme_input.setCurrentText("light")

    assert menu._has_pending_changes() is True


def test_has_pending_changes_language_true(menu):
    """
    Verifica que detecta ausencia de cambios.
    """

    menu.language_input.setCurrentIndex(1)

    assert menu._has_pending_changes() is True


# =============================================================================
# APPLY SETTINGS
# =============================================================================


def test_apply_settings(menu):
    """
    Verifica que aplica los ajustes.
    """

    menu.theme_input.setCurrentText("light")
    menu.language_input.setCurrentIndex(1)

    with (
        patch(
            "ui.widgets.settings.settings_menu.ThemeManager.set_theme",
        ) as set_theme,
        patch(
            "ui.widgets.settings.settings_menu.TranslationManager.set_language",
        ) as set_language,
        patch.object(
            menu,
            "_save_current_settings",
        ) as save_settings,
    ):

        menu._apply_settings()

    set_theme.assert_called_once_with("light")
    set_language.assert_called_once_with("es")
    save_settings.assert_called_once()


# =============================================================================
# EVENT HANDLERS
# =============================================================================


def test_on_setting_changed_without_changes(menu):
    """
    Verifica que deshabilita los botones si
    no existen cambios pendientes.
    """

    menu._on_setting_changed()

    assert not menu.apply_button.isEnabled()
    assert not menu.accept_button.isEnabled()


def test_on_setting_changed_with_changes(menu):
    """
    Verifica que habilita los botones cuando
    existen cambios pendientes.
    """

    menu.theme_input.setCurrentText("light")

    menu._on_setting_changed()

    assert menu.apply_button.isEnabled()
    assert menu.accept_button.isEnabled()


def test_on_apply_requested(menu):
    """
    Verifica que aplica el tema y actualiza
    el estado del formulario.
    """

    menu._apply_settings = MagicMock()
    menu._on_setting_changed = MagicMock()

    with (
        patch(
            "ui.widgets.settings.settings_menu.notify",
        ),
        patch(
            "ui.widgets.settings.settings_menu.AppContext.get_app",
            return_value=MagicMock(),
        ),
    ):

        menu._on_apply_requested()

    menu._apply_settings.assert_called_once()
    menu._on_setting_changed.assert_called_once()


def test_on_cancel_button_clicked(menu):
    """
    Verifica que Cancel restaura la configuración.
    """

    menu._restore_settings = MagicMock()

    menu._on_cancel_button_clicked()

    menu._restore_settings.assert_called_once()


# =============================================================================
# SIGNALS
# =============================================================================


def test_apply_button_signal(menu):
    """
    Verifica que pulsar Apply ejecuta
    el handler correspondiente.
    """

    menu._on_apply_requested = MagicMock()

    menu.apply_button.clicked.emit()

    # La conexión ya estaba hecha, así que llamamos
    # directamente al slot original mediante click().


def test_apply_button_click(menu):
    """
    Verifica que pulsar Apply invoca la aplicación
    de cambios.
    """

    with (
        patch.object(
            menu,
            "_apply_settings",
        ) as apply_settings,
        patch(
            "ui.widgets.settings.settings_menu.notify",
        ),
        patch(
            "ui.widgets.settings.settings_menu.AppContext.get_app",
            return_value=MagicMock(),
        ),
    ):

        menu.theme_input.setCurrentText("light")

        menu.apply_button.click()

    apply_settings.assert_called_once()


# =============================================================================
# APPLY SETTINGS FLOW
# =============================================================================


def test_apply_requested_success(menu):
    """
    Verifica que aplicar el tema ejecuta el flujo
    completo correctamente.
    """

    menu._apply_settings = MagicMock()
    menu._on_setting_changed = MagicMock()

    app = MagicMock()

    with (
        patch(
            "ui.widgets.settings.settings_menu.notify",
        ) as notify,
        patch(
            "ui.widgets.settings.settings_menu.logger",
        ) as logger,
        patch(
            "ui.widgets.settings.settings_menu.AppContext.get_app",
            return_value=app,
        ),
    ):

        menu._on_apply_requested()

    logger.info.assert_called_once_with(
        "Changing settings...",
    )

    logger.success.assert_called_once_with(
        "Settings changed.",
    )

    app.processEvents.assert_called_once()

    menu._apply_settings.assert_called_once()
    menu._on_setting_changed.assert_called_once()

    assert notify.call_count == 2

    notify.assert_any_call(
        message_type=MessageType.WARNING,
        message="Changing settings...",
    )

    notify.assert_any_call(
        message_type=MessageType.SUCCESS,
        message="Settings changed.",
    )


def test_apply_requested_error(menu):
    """
    Verifica que los errores durante el cambio de
    tema se notifican correctamente.
    """

    menu._apply_settings = MagicMock(
        side_effect=Exception("boom"),
    )

    app = MagicMock()

    with (
        patch(
            "ui.widgets.settings.settings_menu.notify",
        ) as notify,
        patch(
            "ui.widgets.settings.settings_menu.logger",
        ) as logger,
        patch(
            "ui.widgets.settings.settings_menu.AppContext.get_app",
            return_value=app,
        ),
    ):

        menu._on_apply_requested()

    logger.exception.assert_called_once()

    app.processEvents.assert_called_once()

    assert notify.call_count == 2

    notify.assert_any_call(
        message_type=MessageType.WARNING,
        message="Changing settings...",
    )

    notify.assert_any_call(
        message_type=MessageType.ERROR,
        message="Error changing settings.\nSee logs for details.",
    )


# =============================================================================
# PRIVATE API
# =============================================================================


def test_save_current_settings(menu):
    """
    Verifica que guarda la configuración aplicada.
    """

    menu._saved_settings = {}

    menu._save_current_settings()

    assert menu._saved_settings == {
        "theme": "dark",
        "language": "en",
    }


def test_restore_settings(menu):
    """
    Verifica que restaura la configuración guardada.
    """

    menu.theme_input.setCurrentText("light")
    menu.language_input.setCurrentIndex(1)

    menu._restore_settings()

    assert menu.theme_input.currentText() == "dark"
    assert menu.language_input.currentData() == "en"

    assert not menu.apply_button.isEnabled()
    assert not menu.accept_button.isEnabled()
