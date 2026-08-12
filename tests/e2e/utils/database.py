from pathlib import Path

import sqlparse
from sqlalchemy import text

from entities.connection import Connection
from entities.session import Session


def reset_database(
    connection: Connection,
    script_path: Path,
) -> None:
    """
    Restablece la base de datos ejecutando el script SQL indicado.

    Args:
        connection (Connection):
            Configuración de la conexión.

        script_path (Path):
            Ruta del script SQL utilizado para restablecer
            la base de datos.
    """

    script = script_path.read_text(
        encoding="utf-8",
    )

    statements = sqlparse.split(script)

    session = Session.create(
        connection=connection,
    )

    try:

        with session.engine.begin() as engine_connection:

            for statement in statements:

                statement = statement.strip()

                if not statement:
                    continue

                engine_connection.execute(
                    text(statement),
                )

    finally:
        session.close()
