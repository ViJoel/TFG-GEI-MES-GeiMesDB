from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QColor,
    QStandardItem,
    QStandardItemModel,
)

from modules.sql.autocompletion.dynamic_data import SqlDynamicCompletionData
from modules.sql.autocompletion.schema_data import (
    SQL_SCHEMA_COMPLETION_DATA,
)
from modules.sql.autocompletion.sql_document_completion_provider import (
    SqlDocumentCompletionProvider,
)
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
        autocompletado combinando todas las
        fuentes de datos disponibles:

        - Datos estáticos del lenguaje SQL.
        - Datos del esquema de la base de datos.
        - Datos dinámicos obtenidos del documento SQL.
        """

        self.clear()

        items = []

        for completion_data in (
            SQL_STATIC_COMPLETION_DATA,
            SQL_SCHEMA_COMPLETION_DATA.get_data(),
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
        sql: str | None = None,
        force_update: bool = False,
    ) -> bool:
        """
        Actualiza el modelo del autocompletador.

        Cuando `force_update` es `False`, analiza el
        contenido del documento SQL para detectar
        cambios en los datos dinámicos. Si se detectan,
        reconstruye automáticamente el modelo.

        Cuando `force_update` es `True`, reconstruye el
        modelo directamente sin analizar el documento,
        permitiendo reflejar cambios externos como una
        actualización del esquema de la base de datos.

        Args:
            sql (str | None):
                Contenido completo del documento SQL.

                Debe proporcionarse cuando `force_update`
                es `False`. Se ignora cuando `force_update`
                es `True`.

            force_update (bool):
                Indica si se debe reconstruir el modelo
                sin comprobar los datos dinámicos del
                documento.

        Returns:
            bool:
                - `True` si el modelo ha sido
                reconstruido.
                - `False` si no se ha detectado ningún
                cambio y no ha sido necesario
                actualizarlo.
        """

        if force_update:
            self.refresh()
            return True

        if sql is None:
            return False

        changed = self._document_completion_provider.update(
            sql=sql,
            dynamic_data=self._dynamic_data,
        )

        if changed:
            self.refresh()

        return changed
