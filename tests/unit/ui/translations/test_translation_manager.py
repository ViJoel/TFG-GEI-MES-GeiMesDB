from unittest.mock import (
    MagicMock,
    patch,
)

import pytest

from entities.setting import Setting
from entities.setting_key import SettingKey
from ui.translations.translation_manager import TranslationManager

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture(autouse=True)
def reset_translation_manager():
    """
    Restablece el estado global del TranslationManager
    antes y después de cada test.
    """

    TranslationManager._current_language = "en"
    TranslationManager._translator = None

    yield

    TranslationManager._current_language = "en"
    TranslationManager._translator = None


@pytest.fixture
def app_mock():
    """
    Crea un mock de la aplicación Qt.
    """

    return MagicMock()


# =============================================================================
# CURRENT LANGUAGE
# =============================================================================


def test_current_language():
    """
    Verifica que devuelve el idioma actualmente activo.
    """

    TranslationManager._current_language = "es"

    assert TranslationManager.current_language() == "es"


# =============================================================================
# GET LANGUAGES
# =============================================================================


def test_get_languages():
    """
    Verifica que devuelve los idiomas disponibles y
    el idioma actualmente seleccionado.
    """

    TranslationManager._current_language = "en"

    result = TranslationManager.get_languages()

    assert result["current_language"] == "en"

    assert result["languages"] == {
        "en": "English",
        "es": "Español",
    }


def test_get_languages_returns_copy():
    """
    Verifica que la lista de idiomas devuelta es una copia
    y no modifica el estado interno del gestor.
    """

    result = TranslationManager.get_languages()

    result["languages"]["fr"] = "French"

    assert "fr" not in TranslationManager._languages


# =============================================================================
# LANGUAGE NAME
# =============================================================================


def test_language_name():
    """
    Verifica que obtiene correctamente el nombre visible
    asociado a un código de idioma.
    """

    assert TranslationManager.language_name("en") == "English"
    assert TranslationManager.language_name("es") == "Español"


def test_language_name_invalid():
    """
    Verifica que solicitar el nombre de un idioma inexistente
    genera una excepción.
    """

    with pytest.raises(KeyError):

        TranslationManager.language_name("fr")


# =============================================================================
# EVENTS
# =============================================================================


def test_events_returns_events_object():
    """
    Verifica que devuelve correctamente el objeto encargado
    de emitir eventos de traducción.
    """

    events = TranslationManager.events()

    assert events is TranslationManager._events


def test_language_changed_event():
    """
    Verifica que la señal language_changed emite el código
    del idioma configurado.
    """

    received = []

    TranslationManager.events().language_changed.connect(
        lambda lang: received.append(lang)
    )

    TranslationManager.events().language_changed.emit(
        "es",
    )

    assert received == ["es"]


# =============================================================================
# INITIALIZE
# =============================================================================


def test_initialize_without_saved_language():
    """
    Verifica que inicializa el gestor aplicando el idioma
    por defecto cuando no existe configuración guardada.
    """

    with (
        patch(
            "ui.translations.translation_manager.get_setting",
            return_value=None,
        ),
        patch.object(
            TranslationManager,
            "apply",
        ) as apply,
    ):

        TranslationManager.initialize()

    apply.assert_called_once()


def test_initialize_with_saved_language():
    """
    Verifica que utiliza el idioma almacenado en configuración
    durante la inicialización.
    """

    setting = Setting(
        key=SettingKey.LANGUAGE,
        value="es",
    )

    with (
        patch(
            "ui.translations.translation_manager.get_setting",
            return_value=setting,
        ),
        patch.object(
            TranslationManager,
            "apply",
        ) as apply,
    ):

        TranslationManager.initialize()

    assert TranslationManager.current_language() == "es"

    apply.assert_called_once()


def test_initialize_ignores_invalid_language():
    """
    Verifica que ignora configuraciones con códigos de idioma
    no registrados.
    """

    setting = Setting(
        key=SettingKey.LANGUAGE,
        value="fr",
    )

    TranslationManager._current_language = "en"

    with (
        patch(
            "ui.translations.translation_manager.get_setting",
            return_value=setting,
        ),
        patch.object(
            TranslationManager,
            "apply",
        ),
    ):

        TranslationManager.initialize()

    assert TranslationManager.current_language() == "en"


# =============================================================================
# APPLY
# =============================================================================


def test_apply_base_language(app_mock):
    """
    Verifica que aplicar el idioma base no carga traducciones
    externas y emite el evento correspondiente.
    """

    TranslationManager._current_language = "en"
    TranslationManager._translator = None

    received = []

    TranslationManager.events().language_changed.connect(
        lambda lang: received.append(lang)
    )

    with patch(
        "ui.translations.translation_manager.AppContext.get_app",
        return_value=app_mock,
    ):

        TranslationManager.apply()

    app_mock.removeTranslator.assert_not_called()

    assert received == ["en"]


def test_apply_removes_existing_translator(app_mock):
    """
    Verifica que elimina el traductor previamente instalado
    antes de aplicar un nuevo idioma.
    """

    translator = MagicMock()

    TranslationManager._translator = translator
    TranslationManager._current_language = "en"

    with patch(
        "ui.translations.translation_manager.AppContext.get_app",
        return_value=app_mock,
    ):

        TranslationManager.apply()

    app_mock.removeTranslator.assert_called_once_with(
        translator,
    )

    assert TranslationManager._translator is None


def test_apply_translation_language(app_mock):
    """
    Verifica que carga e instala correctamente un archivo
    de traducción para un idioma distinto al base.
    """

    TranslationManager._current_language = "es"

    translator_mock = MagicMock()

    translator_mock.load.return_value = True

    received = []

    TranslationManager.events().language_changed.connect(
        lambda lang: received.append(lang)
    )

    with (
        patch(
            "ui.translations.translation_manager.AppContext.get_app",
            return_value=app_mock,
        ),
        patch(
            "ui.translations.translation_manager.QTranslator",
            return_value=translator_mock,
        ),
    ):

        TranslationManager.apply()

    translator_mock.load.assert_called_once()

    app_mock.installTranslator.assert_called_once_with(
        translator_mock,
    )

    assert received == ["es"]


def test_apply_missing_translation_file(app_mock):
    """
    Verifica que genera FileNotFoundError cuando no puede
    cargar el archivo de traducción solicitado.
    """

    TranslationManager._current_language = "es"

    translator_mock = MagicMock()

    translator_mock.load.return_value = False

    with (
        patch(
            "ui.translations.translation_manager.AppContext.get_app",
            return_value=app_mock,
        ),
        patch(
            "ui.translations.translation_manager.QTranslator",
            return_value=translator_mock,
        ),
    ):

        with pytest.raises(FileNotFoundError):

            TranslationManager.apply()


# =============================================================================
# SET LANGUAGE
# =============================================================================


def test_set_language_changes_language():
    """
    Verifica que cambiar el idioma actualiza el estado,
    guarda la configuración y aplica el nuevo idioma.
    """

    TranslationManager._current_language = "en"

    with (
        patch(
            "ui.translations.translation_manager.save_setting",
        ) as save,
        patch.object(
            TranslationManager,
            "apply",
        ) as apply,
    ):

        TranslationManager.set_language("es")

    assert TranslationManager.current_language() == "es"

    save.assert_called_once_with(
        Setting(
            key=SettingKey.LANGUAGE,
            value="es",
        )
    )

    apply.assert_called_once()


def test_set_language_same_language_does_nothing():
    """
    Verifica que cambiar al mismo idioma activo no realiza
    ninguna operación.
    """

    TranslationManager._current_language = "en"

    with (
        patch(
            "ui.translations.translation_manager.save_setting",
        ) as save,
        patch.object(
            TranslationManager,
            "apply",
        ) as apply,
    ):

        TranslationManager.set_language("en")

    save.assert_not_called()

    apply.assert_not_called()


def test_set_language_invalid():
    """
    Verifica que cambiar a un idioma no registrado genera
    una excepción ValueError.
    """

    with pytest.raises(ValueError):

        TranslationManager.set_language("fr")


def test_set_language_emits_event():
    """
    Verifica que cambiar de idioma notifica a los
    suscriptores mediante la señal correspondiente.
    """

    received = []

    TranslationManager._current_language = "en"

    TranslationManager.events().language_changed.connect(
        lambda lang: received.append(lang)
    )

    with (
        patch(
            "ui.translations.translation_manager.save_setting",
        ),
        patch.object(
            TranslationManager,
            "apply",
        ),
    ):

        TranslationManager.set_language("es")

    assert received == ["es"]
