import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QColor,
    QStandardItem,
    QStandardItemModel,
)

from modules.sql.autocompletion.data import SQL_STATIC_COMPLETION_DATA
from ui.themes.theme_manager import ThemeManager


class SqlCompleterModel(QStandardItemModel):
    """
    Modelo de datos utilizado por el autocompletador SQL.

    Almacena los elementos que se muestran en el popup del
    autocompletador, aplicando el color correspondiente a
    cada categoría de palabras mediante los datos definidos
    en ``SQL_STATIC_COMPLETION_DATA``.
    """

    # =================
    # === VARIABLES ===
    # =================

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
    ) -> None:
        """
        Inicializa el modelo con los elementos estáticos
        del autocompletador SQL.

        Carga todas las categorías definidas en
        ``SQL_STATIC_COMPLETION_DATA`` y crea un
        ``QStandardItem`` por cada palabra, asignándole
        el color correspondiente para su representación
        en el popup de autocompletado.
        """

        super().__init__()

        for value in SQL_STATIC_COMPLETION_DATA.values():

            color = QColor(
                ThemeManager.get_color(
                    value.get(
                        "color",
                        "text",
                    )
                )
            )

            for word in value.get(
                "values",
                [],
            ):
                item = QStandardItem(word)
                item.setData(color, Qt.ItemDataRole.ForegroundRole)
                self.appendRow(item)

    # ================
    # === UI SETUP ===
    # ================

    # ================
    # === UI STATE ===
    # ================

    # ==================
    # === UI HELPERS ===
    # ==================

    # ===============
    # === SIGNALS ===
    # ===============

    # ======================
    # === EVENT HANDLERS ===
    # ======================

    # =====================
    # === EVENT HELPERS ===
    # =====================

    # ====================
    # === QT OVERRIDES ===
    # ====================

    # ===================
    # === PRIVATE API ===
    # ===================

    # ==================
    # === PUBLIC API ===
    # ==================
