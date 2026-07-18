from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QColor,
    QStandardItem,
    QStandardItemModel,
)

from modules.sql.autocompletion.dynamic_data import SQL_DYNAMIC_COMPLETION_DATA
from modules.sql.autocompletion.static_data import SQL_STATIC_COMPLETION_DATA
from ui.themes.theme_manager import ThemeManager


class SqlCompleterModel(QStandardItemModel):
    """
    Modelo de datos utilizado por el autocompletador SQL.

    Almacena los elementos que se muestran en el popup del
    autocompletador, combinando los datos estáticos y
    dinámicos y aplicando el color correspondiente a cada
    categoría.
    """

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
    ) -> None:
        """
        Inicializa el modelo del autocompletador SQL.
        """

        super().__init__()

        self.refresh()

    # ==================
    # === PUBLIC API ===
    # ==================

    def refresh(
        self,
    ) -> None:
        """
        Recarga los elementos del modelo de
        autocompletado a partir de los datos
        estáticos y dinámicos disponibles.
        """

        self.clear()

        for completion_data in (
            SQL_STATIC_COMPLETION_DATA,
            SQL_DYNAMIC_COMPLETION_DATA,
        ):

            for value in completion_data.values():

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

                    item.setData(
                        color,
                        Qt.ItemDataRole.ForegroundRole,
                    )

                    self.appendRow(item)
