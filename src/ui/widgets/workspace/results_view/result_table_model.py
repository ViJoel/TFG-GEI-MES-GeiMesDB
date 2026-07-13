import json
from collections import defaultdict
from copy import deepcopy
from datetime import (
    date,
    datetime,
    time,
)
from decimal import Decimal
from typing import Any

from PySide6.QtCore import (
    QAbstractTableModel,
    Qt,
    Signal,
)
from PySide6.QtGui import QColor

from entities.query_result import ResultSet
from entities.update_operation import UpdateOperation
from ui.themes.theme_manager import ThemeManager


class ResultTableModel(QAbstractTableModel):
    """
    Modelo de datos utilizado para representar y
    editar los resultados de una consulta en una
    tabla Qt.

    Permite detectar modificaciones realizadas sobre
    las celdas y generar sentencias SQL necesarias
    para persistir los cambios efectuados.
    Mantiene una copia del estado original
    """

    # =================
    # === VARIABLES ===
    # =================

    state_changed = Signal(bool)

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
        result_set: ResultSet,
    ) -> None:
        """
        Inicializa el modelo con un conjunto de
        resultados.

        Args:
            result_set (ResultSet):
                Conjunto de resultados que será
                gestionado por el modelo.
        """

        super().__init__()

        self.result_set = result_set
        self.original_result_set = deepcopy(result_set)
        self.modified_cells: set[tuple[int, int]] = set()

    # ==================
    # === UI HELPERS ===
    # ==================

    def _get_table_cell_color(
        self,
        row: int,
        column: int,
        role: Qt.ItemDataRole,
    ) -> QColor | None:
        """
        Devuelve el color asociado a una celda en
        función de su estado y del tipo de dato que
        contiene.

        Args:
            row (int):
                Índice de la fila.

            column (int):
                Índice de la columna.

            role (Qt.ItemDataRole):
                Rol solicitado por Qt.

        Returns:
            QColor | None:
                Color correspondiente al rol
                solicitado, o `None` si no aplica.
        """

        if role not in (
            Qt.ForegroundRole,
            Qt.BackgroundRole,
        ):
            return None

        if (row, column) in self.modified_cells:

            if role == Qt.BackgroundRole:
                return QColor(
                    ThemeManager.get_color(
                        "table_cell_modified_background_color",
                    )
                )

            return QColor(
                ThemeManager.get_color(
                    "table_cell_modified_color",
                )
            )

        if role == Qt.BackgroundRole:
            return None

        value = self.result_set.rows[row][column]

        if value is None:
            color = "null"

        elif isinstance(value, bool):
            color = "boolean"

        elif isinstance(value, (int, float, Decimal)):
            color = "number"

        elif isinstance(value, str):
            color = "string"

        elif isinstance(value, (date, datetime, time)):
            color = "datetime"

        elif isinstance(value, dict):
            color = "json"

        else:
            color = "default"

        theme_key = f"table_{color}_color"

        return QColor(ThemeManager.get_color(theme_key))

    # ====================
    # === QT OVERRIDES ===
    # ====================

    def rowCount(
        self,
        parent=None,
    ) -> int:
        """
        Devuelve el número de filas del modelo.

        Returns:
            int:
                Número de filas disponibles.
        """

        return len(self.result_set.rows)

    def columnCount(
        self,
        parent=None,
    ) -> int:
        """
        Devuelve el número de columnas del modelo.

        Returns:
            int:
                Número de columnas disponibles.
        """

        return len(self.result_set.columns)

    def data(
        self,
        index,
        role,
    ):
        """
        Devuelve los datos asociados a una celda.

        Args:
            index:
                Índice de la celda consultada.

            role:
                Rol solicitado por Qt.

        Returns:
            Any:
                Valor asociado a la celda para el rol
                indicado.
        """

        row = index.row()
        column = index.column()

        # Separamos los roles para formatear la visualización
        # Reutilizamos la función centralizada para la vista y la edición
        if role in (Qt.DisplayRole, Qt.EditRole):
            value = self.result_set.rows[row][column]
            return self._value_to_str(value)

        if role in (
            Qt.ForegroundRole,
            Qt.BackgroundRole,
        ):
            return self._get_table_cell_color(
                row=row,
                column=column,
                role=role,
            )

    def headerData(
        self,
        section,
        orientation,
        role,
    ):
        """
        Devuelve los datos de una cabecera.

        Args:
            section:
                Índice de la sección solicitada.

            orientation:
                Orientación de la cabecera.

            role:
                Rol solicitado por Qt.

        Returns:
            Any:
                Valor asociado a la cabecera.
        """

        if orientation == Qt.Horizontal and role == Qt.DisplayRole:

            return self.result_set.columns[section]

    def flags(
        self,
        index,
    ):
        """
        Devuelve las capacidades disponibles para una
        celda.

        Args:
            index:
                Índice de la celda.

        Returns:
            Qt.ItemFlags:
                Banderas asociadas a la celda.
        """

        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def setData(
        self,
        index,
        value,
        role,
    ):
        """
        Actualiza el valor de una celda.

        Args:
            index:
                Índice de la celda a modificar.

            value:
                Nuevo valor introducido.

            role:
                Rol asociado a la modificación.

        Returns:
            bool:
                True si el valor fue procesado
                correctamente; False en caso
                contrario.
        """

        if role != Qt.EditRole:
            return False

        row = index.row()
        column = index.column()

        original_value = self.original_result_set.rows[row][column]

        new_value = self._convert_value(
            column=column,
            value=value,
        )

        self._modify_cell_value(
            row=row,
            column=column,
            original_value=original_value,
            new_value=new_value,
        )

        self.dataChanged.emit(
            index,
            index,
        )

        return True

    # ===================
    # === PRIVATE API ===
    # ===================

    def _modify_cell_value(
        self,
        row: int,
        column: int,
        original_value: Any,
        new_value: Any,
    ):
        """
        Actualiza el valor de una celda y registra si
        ha sido modificada.

        Args:
            row (int):
                Índice de la fila modificada.

            column (int):
                Índice de la columna modificada.

            original_value (Any):
                Valor original de la celda.

            new_value (Any):
                Nuevo valor asignado a la celda.
        """

        self.result_set.rows[row][column] = new_value

        if new_value == original_value:
            self.modified_cells.discard((row, column))
        else:
            self.modified_cells.add((row, column))

        self.state_changed.emit(self._has_changes())

    def _convert_value(
        self,
        column: int,
        value: str,
    ) -> Any:
        """
        Convierte un valor textual al tipo asociado a
        una columna.

        Args:
            column (int):
                Índice de la columna.

            value (str):
                Valor introducido por el usuario.

        Returns:
            Any:
                Valor convertido al tipo de datos
                correspondiente.
        """

        column_name = self.result_set.columns[column]

        return self.result_set.table_metadata.convert_value(
            column_name=column_name,
            value=value,
        )

    def _value_to_str(self, value: Any) -> str:
        """
        Convierte cualquier tipo de objeto devuelto
        por SQLAlchemy a su representación textual
        idónea para la interfaz gráfica.

        Args:
            value (Any):
                Valor a convertir.

        Returns:
            str:
                Valor convertida a string.
        """

        if value is None:
            return "[NULL]"

        if isinstance(
            value,
            (
                date,
                datetime,
                time,
            ),
        ):
            return value.isoformat()

        if isinstance(value, Decimal):
            return str(value)

        if isinstance(value, dict):
            return json.dumps(
                value,
                ensure_ascii=False,
            )

        return str(value)

    def _has_changes(
        self,
    ) -> bool:
        """
        Comprueba si existen cambios pendientes.

        Returns:
            bool:
                True si alguna celda ha sido
                modificada; False en caso contrario.
        """

        return bool(self.modified_cells)

    # ==================
    # === PUBLIC API ===
    # ==================

    def discard_changes(
        self,
    ) -> None:
        """
        Descarta todos los cambios realizados y
        restaura el estado original del conjunto de
        resultados.
        """

        self.result_set.columns = deepcopy(
            self.original_result_set.columns,
        )

        self.result_set.rows = deepcopy(
            self.original_result_set.rows,
        )

        self.modified_cells.clear()

        self.layoutChanged.emit()

        self.state_changed.emit(False)

    def generate_update_operations(
        self,
    ) -> list[UpdateOperation]:
        """
        Genera las operaciones necesarias para
        persistir las modificaciones realizadas.

        Returns:
            list[UpdateOperation]:
                Operaciones de actualización
                correspondientes a las filas
                modificadas.
        """

        operations: list[UpdateOperation] = []

        modified_columns_by_row = defaultdict(set)

        for row, column in self.modified_cells:
            modified_columns_by_row[row].add(column)

        column_indexes = {
            column: index for index, column in enumerate(self.result_set.columns)
        }

        for row, modified_columns in modified_columns_by_row.items():

            values: dict[str, Any] = {}

            primary_key: dict[str, Any] = {}

            for column in modified_columns:

                column_name = self.result_set.columns[column]

                values[column_name] = self.result_set.rows[row][column]

            for pk_column in self.result_set.table_metadata.primary_key_columns:

                pk_index = column_indexes[pk_column]

                primary_key[pk_column] = self.original_result_set.rows[row][pk_index]

            operations.append(
                UpdateOperation(
                    table_metadata=self.result_set.table_metadata,
                    primary_key=primary_key,
                    values=values,
                )
            )

        return operations
