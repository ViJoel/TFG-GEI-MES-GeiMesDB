import re

from modules.sql.autocompletion.dynamic_data import SqlDynamicCompletionData

_PARAMETER_PATTERN = re.compile(r"(?<!\w)([:$]\w+)")

_VARIABLE_PATTERN = re.compile(r"(?<!\w)(@?@\w+)")


class SqlDocumentCompletionProvider:

    # ============
    # === INIT ===
    # ============

    def __init__(
        self,
    ) -> None:
        """
        Inicializa el proveedor de datos de
        autocompletado obtenidos a partir del
        documento SQL.
        """

        super().__init__()

    # ==================
    # === PUBLIC API ===
    # ==================

    def update(
        self,
        sql: str,
        dynamic_data: SqlDynamicCompletionData,
    ) -> bool:
        """
        Analiza el contenido del documento SQL y actualiza
        los datos dinámicos del autocompletador cuando
        detecta cambios.

        Args:
            sql (str):
                Contenido completo del documento.

            dynamic_data (SqlDynamicCompletionData):
                Datos que pueden estar o no actualizados.

        Returns:
            bool:
                - `True` si los datos dinámicos han cambiado
                y se han actualizado.
                - `False` si no se ha detectado ningún cambio.
        """

        parameters = set(_PARAMETER_PATTERN.findall(sql))
        variables = set(_VARIABLE_PATTERN.findall(sql))

        parameters_changed = dynamic_data.has_changes(
            key="parameters",
            values=parameters,
        )

        variables_changed = dynamic_data.has_changes(
            key="variables",
            values=variables,
        )

        if not parameters_changed and not variables_changed:
            return False

        dynamic_data.clear_dynamic_completion_data()

        dynamic_data.update_dynamic_completion_data(
            key="parameters",
            values=parameters,
        )

        dynamic_data.update_dynamic_completion_data(
            key="variables",
            values=variables,
        )

        return True
