from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest
from pytest import MonkeyPatch

from entities.connection import Connection
from entities.driver import Driver
from modules.connections import model as connections_model
from modules.connections.crypto import encrypt
from modules.database import model as database_model
from modules.queries_history import model as queries_history_model
from modules.settings import model as settings_model
from tests.e2e.data.connections import (
    MYSQL_CONNECTION,
    ORACLE_CONNECTION,
    POSTGRESQL_CONNECTION,
    SQLITE_CONNECTION,
)
from tests.e2e.data.settings import (
    LANGUAGE_KEY,
    LANGUAGE_VALUE,
    THEME_KEY,
    THEME_VALUE,
)


@pytest.fixture
def temporary_database(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> Path:
    """
    Crea una base de datos SQLite temporal y redirige hacia ella
    todos los accesos realizados por los módulos de persistencia.

    Args:
        tmp_path (Path):
            Directorio temporal exclusivo del test.

        monkeypatch (MonkeyPatch):
            Utilidad de pytest para sustituir atributos durante
            la ejecución del test.

    Returns:
        Path:
            Ruta de la base de datos temporal.
    """

    db_path = tmp_path / "test.db"

    original_get_connection = database_model.get_connection
    original_init_database = database_model.init_database

    def get_connection(
        *args: Any,
        **kwargs: Any,
    ) -> Any:

        kwargs.setdefault(
            "db_path",
            str(db_path),
        )

        kwargs["db_path"] = str(db_path)

        return original_get_connection(
            *args,
            **kwargs,
        )

    def init_database(
        *args: Any,
        **kwargs: Any,
    ) -> Any:

        kwargs.setdefault(
            "db_path",
            str(db_path),
        )

        kwargs["db_path"] = str(db_path)
        kwargs["data_dir"] = str(tmp_path)

        return original_init_database(
            *args,
            **kwargs,
        )

    # Redirigir las funciones del módulo de base de datos.
    monkeypatch.setattr(
        database_model,
        "get_connection",
        get_connection,
    )

    monkeypatch.setattr(
        database_model,
        "init_database",
        init_database,
    )

    # Redirigir los alias importados por los modelos.
    monkeypatch.setattr(
        connections_model,
        "get_db_connection",
        get_connection,
    )

    monkeypatch.setattr(
        queries_history_model,
        "get_db_connection",
        get_connection,
    )

    monkeypatch.setattr(
        settings_model,
        "get_db_connection",
        get_connection,
    )

    # Inicializar el esquema sobre la base temporal.
    database_model.init_database()

    # Preparar datos iniciales.
    connections = [
        encrypt(MYSQL_CONNECTION),
        encrypt(ORACLE_CONNECTION),
        encrypt(POSTGRESQL_CONNECTION),
        encrypt(
            replace(
                SQLITE_CONNECTION,
                path=str(db_path),
            )
        ),
    ]

    # Insertar datos iniciales.
    with database_model.get_connection(
        db_path=str(db_path),
    ) as connection:

        connection.executemany(
            """
            INSERT INTO connections (
                id,
                name,
                driver,
                host,
                port,
                database,
                username,
                password,
                path
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    item.id,
                    item.name,
                    item.driver.value,
                    item.host,
                    item.port,
                    item.database,
                    item.username,
                    item.password,
                    item.path,
                )
                for item in connections
            ],
        )

        connection.executemany(
            """
            INSERT INTO settings (
                key,
                value
            )
            VALUES (?, ?)
            """,
            [
                (THEME_KEY, THEME_VALUE),
                (LANGUAGE_KEY, LANGUAGE_VALUE),
            ],
        )

    return db_path
