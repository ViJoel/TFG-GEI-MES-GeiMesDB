from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QColor,
    QStandardItem,
    QStandardItemModel,
)

from modules.sql.autocompletion.dynamic_data import SqlDynamicCompletionData
from modules.sql.autocompletion.static_data import SQL_STATIC_COMPLETION_DATA
from ui.themes.theme_manager import ThemeManager
from ui.widgets.workspace.sql_editor.sql_document_completion_provider import (
    SqlDocumentCompletionProvider,
)


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

        self._dynamic_data = SqlDynamicCompletionData()

        self._document_completion_provider = SqlDocumentCompletionProvider()

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

        items = []

        for completion_data in (
            SQL_STATIC_COMPLETION_DATA,
            self._dynamic_data.get_data(),
        ):
            for value in completion_data.values():

                color = QColor(
                    ThemeManager.get_color(
                        value.get("color", "text"),
                    )
                )

                for word in value.get("values", []):
                    items.append((word, color))

        items.sort(key=lambda item: item[0].casefold())

        for word, color in items:
            item = QStandardItem(word)
            item.setData(
                color,
                Qt.ItemDataRole.ForegroundRole,
            )
            self.appendRow(item)

    def update(
        self,
        sql: str,
    ) -> bool:
        """
        Actualiza los datos dinámicos del
        autocompletador a partir del contenido
        del documento.

        Si se detectan cambios, el modelo se
        reconstruye automáticamente.

        Args:
            sql (str):
                Contenido completo del documento.

        Returns:
            bool:
                - `True` si los datos dinámicos
                han cambiado.
                - `False` si no se ha detectado
                ningún cambio.
        """

        changed = self._document_completion_provider.update(
            sql=sql,
            dynamic_data=self._dynamic_data,
        )

        if changed:
            self.refresh()

        return changed
