from collections import defaultdict
from copy import deepcopy
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from PySide6.QtCore import QAbstractTableModel, Qt, Signal
from PySide6.QtGui import QColor

from entities.query_result import ResultSet


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

        if role in (
            Qt.DisplayRole,
            Qt.EditRole,
        ):

            return self.result_set.rows[row][column]

        if role == Qt.BackgroundRole:

            if (row, column) in self.modified_cells:

                return QColor("red")

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

        print(
            f"Old: {original_value!r} ({type(original_value).__name__}) "
            f"-> New: {new_value!r} ({type(new_value).__name__})"
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

        try:

            column_type = self.result_set.columns_types[column]

            if value == "":
                return None

            if column_type is int:
                return int(value)

            if column_type is float:
                return float(value)

            if column_type is str:
                return value

            if column_type is bool:
                return value.lower() in (
                    "true",
                    "1",
                    "yes",
                )

            if column_type is Decimal:
                return Decimal(value)

            if column_type is date:
                return date.fromisoformat(value)

            if column_type is datetime:
                return datetime.fromisoformat(value)

            return value

        except (
            ValueError,
            TypeError,
        ):

            return value

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

    def generate_update_queries(
        self,
    ) -> list[str]:
        """
        Genera las sentencias SQL necesarias para
        persistir las modificaciones realizadas.

        Returns:
            list[str]:
                Lista de sentencias UPDATE generadas.
        """

        queries = []

        modified_columns_by_row = defaultdict(set)

        for row, column in self.modified_cells:
            modified_columns_by_row[row].add(column)

        for row, modified_columns in modified_columns_by_row.items():

            set_parts = []

            for column in modified_columns:

                column_name = self.result_set.columns[column]

                value = self.result_set.rows[row][column]

                set_parts.append(f"{column_name} = {self._format_sql_value(value)}")

            where_parts = []

            for pk_column in self.result_set.primary_key_columns:

                pk_index = self.result_set.columns.index(pk_column)

                value = self.original_result_set.rows[row][pk_index]

                where_parts.append(f"{pk_column} = {self._format_sql_value(value)}")

            query = (
                f"UPDATE {self.result_set.table_name} "
                f"SET {', '.join(set_parts)} "
                f"WHERE {' AND '.join(where_parts)};"
            )

            queries.append(query)

        return queries

    def _format_sql_value(
        self,
        value: Any,
    ) -> str:
        """
        Convierte un valor Python a su representación
        equivalente en SQL.

        Args:
            value (Any):
                Valor que se desea formatear.

        Returns:
            str:
                Representación del valor en formato
                SQL.
        """

        if value is None:
            return "NULL"

        if isinstance(value, str):
            return "'" + value.replace("'", "''") + "'"

        if isinstance(value, bool):
            return "TRUE" if value else "FALSE"

        if isinstance(value, (date, datetime)):
            return f"'{value.isoformat()}'"

        if isinstance(value, Decimal):
            return str(value)

        return str(value)
