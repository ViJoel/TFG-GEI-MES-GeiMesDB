from enum import Enum


class Driver(Enum):
    """
    Motores de base de datos soportados por la aplicación.

    Attributes:
        POSTGRESQL: Driver para bases de datos PostgreSQL.
        MYSQL: Driver para bases de datos MySQL.
        SQLITE: Driver para bases de datos SQLite (locales).
        ORACLE: Driver para bases de datos Oracle.
    """

    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    ORACLE = "oracle"
