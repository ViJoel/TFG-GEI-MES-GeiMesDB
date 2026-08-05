from pathlib import Path

from PySide6.QtCore import (
    QObject,
    QTranslator,
    Signal,
)

from entities.setting import Setting
from entities.setting_key import SettingKey
from log.app_logger import get_logger
from modules.settings.service import (
    get_setting,
    save_setting,
)
from ui.app.app_context import AppContext
from ui.common.paths import TRANSLATIONS_DIR

logger = get_logger(__name__)


class _TranslationEvents(QObject):
    """
    Eventos emitidos por el gestor de traducciones.
    """

    language_changed = Signal(str)


class TranslationManager:
    """
    Gestor central de traducciones de la aplicación.

    Responsable de gestionar los idiomas disponibles,
    cargar el traductor correspondiente y aplicar el
    idioma activo a la aplicación en tiempo de ejecución.

    También persiste el idioma seleccionado y expone un
    mecanismo de eventos para que otros componentes puedan
    reaccionar a los cambios de idioma.
    """

    # =================
    # === VARIABLES ===
    # =================

    _languages: dict[str, str] = {
        "en": "English",
        "es": "Español",
    }

    _current_language: str = "en"

    _translator = QTranslator()

    _events = _TranslationEvents()

    # ======================
    # === INITIALIZATION ===
    # ======================

    @classmethod
    def initialize(
        cls,
    ) -> None:
        """
        Inicializa el gestor de traducciones.

        Recupera el idioma almacenado en la configuración
        de la aplicación y aplica dicho idioma. Si no existe
        ninguna preferencia guardada, se utilizará el idioma
        por defecto.

        Raises:
            RuntimeError:
                Si la aplicación todavía no ha sido
                inicializada en AppContext.
        """

        logger.info("Initializing translation manager...")

        setting = get_setting(SettingKey.LANGUAGE)

        if setting is not None and setting.value in cls._languages:
            cls._current_language = setting.value

        cls.apply()

        logger.success("Translation manager initialized.")

    # ==========================
    # === APPLY TRANSLATIONS ===
    # ==========================

    @classmethod
    def apply(
        cls,
    ) -> None:
        """
        Aplica el idioma activo a la aplicación.

        El idioma base de la aplicación (inglés) no requiere
        ningún archivo de traducción. Para otros idiomas carga
        el archivo .qm correspondiente y lo instala como
        traductor global de Qt.

        Raises:
            RuntimeError:
                Si la aplicación no está inicializada.

            FileNotFoundError:
                Si no existe el archivo de traducción solicitado.
        """

        app = AppContext.get_app()

        logger.info(
            "Applying language '%s'...",
            cls._current_language,
        )

        # Eliminar traducción actualmente aplicada
        if cls._translator is not None:

            app.removeTranslator(
                cls._translator,
            )

            cls._translator = None

        # El idioma base está incluido directamente en el código
        # y no necesita archivo .qm.
        if cls._current_language == "en":

            logger.success(
                "Base language applied.",
            )

            cls._events.language_changed.emit(
                cls._current_language,
            )

            return

        translator = QTranslator()

        translation_file = (
            Path(TRANSLATIONS_DIR) / f"geimesdb_{cls._current_language}.qm"
        )

        logger.info(
            "Loading translation file '%s'...",
            translation_file,
        )

        if not translator.load(
            str(translation_file),
        ):

            logger.error(
                "Could not load translation file '%s'.",
                translation_file,
            )

            raise FileNotFoundError(f"Translation file not found: {translation_file}")

        app.installTranslator(
            translator,
        )

        cls._translator = translator

        logger.success(
            "Language '%s' applied.",
            cls._current_language,
        )

        cls._events.language_changed.emit(
            cls._current_language,
        )

    # ==========================
    # === LANGUAGE SWITCHING ===
    # ==========================

    @classmethod
    def set_language(
        cls,
        language: str,
    ) -> None:
        """
        Cambia el idioma activo de la aplicación.

        Si el idioma indicado es válido y distinto del
        actual, se guarda en la configuración, se aplica
        inmediatamente y se notifica a todos los
        suscriptores.

        Args:
            language (str):
                Código ISO del idioma.

        Raises:
            ValueError:
                Si el idioma indicado no está registrado.
        """

        if language not in cls._languages:

            logger.error(
                "Language '%s' is not registered.",
                language,
            )

            raise ValueError(f"Language '{language}' is not registered.")

        if cls._current_language == language:
            return

        logger.info(
            "Switching language from '%s' to '%s'.",
            cls._current_language,
            language,
        )

        cls._current_language = language

        save_setting(
            Setting(
                key=SettingKey.LANGUAGE,
                value=language,
            )
        )

        cls.apply()

        cls._events.language_changed.emit(language)

    # =====================
    # === LANGUAGE INFO ===
    # =====================

    @classmethod
    def current_language(
        cls,
    ) -> str:
        """
        Obtiene el código del idioma activo.

        Returns:
            str:
                Código ISO del idioma actual.
        """

        return cls._current_language

    @classmethod
    def get_languages(
        cls,
    ) -> dict[str, str | tuple[str, ...]]:
        """
        Obtiene la información básica sobre los idiomas.

        Returns:
            dict[str, str | tuple[str, ...]]:
                Diccionario con el idioma actual y los
                idiomas disponibles.
        """

        return {
            "current_language": cls._current_language,
            "languages": cls._languages.copy(),
        }

    @classmethod
    def language_name(
        cls,
        language: str,
    ) -> str:
        """
        Obtiene el nombre visible asociado a un idioma.

        Args:
            language (str):
                Código ISO del idioma.

        Returns:
            str:
                Nombre mostrado al usuario.

        Raises:
            KeyError:
                Si el idioma no existe.
        """

        return cls._languages[language]

    # ==============
    # === EVENTS ===
    # ==============

    @classmethod
    def events(
        cls,
    ) -> _TranslationEvents:
        """
        Devuelve el objeto que expone los eventos del
        gestor de traducciones.

        Returns:
            _TranslationEvents:
                Objeto que contiene las señales emitidas
                por el gestor.
        """

        return cls._events
