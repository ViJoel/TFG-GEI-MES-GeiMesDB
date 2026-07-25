from dataclasses import dataclass

from entities.query_result import QueryResult


@dataclass(
    kw_only=True,
    slots=True,
)
class QueryExecution:
    """
    Contiene la información asociada a la
    ejecución de una consulta SQL.

    Agrupa la consulta ejecutada junto con
    el resultado obtenido para facilitar su
    transferencia entre el worker de
    ejecución y la interfaz de usuario.
    """

    query: str
    result: QueryResult
