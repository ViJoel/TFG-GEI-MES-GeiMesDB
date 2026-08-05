from enum import (
    StrEnum,
    auto,
)


class Driver(StrEnum):
    """
    Motores de base de datos soportados por la aplicación.

    Attributes:
        POSTGRESQL: Driver para bases de datos PostgreSQL.
        MYSQL: Driver para bases de datos MySQL.
        SQLITE: Driver para bases de datos SQLite (locales).
        ORACLE: Driver para bases de datos Oracle.
    """

    SQLITE = auto()
    POSTGRESQL = auto()
    MYSQL = auto()
    ORACLE = auto()
