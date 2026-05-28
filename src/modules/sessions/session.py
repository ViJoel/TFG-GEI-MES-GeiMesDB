from dataclasses import dataclass

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from entities.connection import Connection
from entities.driver import Driver


@dataclass(slots=True)
class Session:
    """
    Representa una sesión activa de base de datos
    en tiempo de ejecución.

    Una sesión encapsula:
        - La configuración persistida de conexión.
        - El engine SQLAlchemy asociado.
        - El estado runtime necesario para operar
          contra una base de datos activa.

    Responsabilidades:
        - Mantener acceso al engine SQLAlchemy.
        - Asociar una entidad Connection con un Engine.
        - Gestionar el ciclo de vida de recursos
          asociados a la conexión runtime.

    Notes:
        Esta entidad pertenece exclusivamente
        a la capa runtime de sesiones.

        No representa persistencia ni interfaz gráfica.

        El engine SQLAlchemy administra internamente:
            - Pools de conexiones.
            - Reconexión automática.
            - Gestión eficiente de conexiones físicas.
    """

    connection: Connection
    engine: Engine

    # =========================
    # === FACTORY FUNCTIONS ===
    # =========================

    @classmethod
    def create(cls, connection: Connection) -> "Session":
        """
        Construye una nueva sesión activa
        a partir de una conexión persistida.

        Args:
            connection (Connection):
                Configuración de conexión persistida.

        Returns:
            Session:
                Nueva sesión inicializada.
        """

        connection_url = cls._build_connection_url(connection)

        engine = create_engine(
            connection_url,
            pool_pre_ping=True,
        )

        return cls(
            connection=connection,
            engine=engine,
        )

    # ==========================
    # === INTERNAL UTILITIES ===
    # ==========================

    @staticmethod
    def _build_connection_url(
        connection: Connection,
    ) -> str:
        """
        Construye la URL SQLAlchemy necesaria
        para inicializar el engine.

        Args:
            connection (Connection):
                Configuración persistida.

        Returns:
            str:
                URL SQLAlchemy válida.

        Raises:
            ValueError:
                Si el driver no está soportado.
        """

        match connection.driver:

            # POSTGRES_URL = "postgresql+psycopg://username:password@host:port/database"
            case Driver.POSTGRESQL:
                return (
                    f"postgresql+psycopg://"
                    f"{connection.username}:"
                    f"{connection.password}@"
                    f"{connection.host}:"
                    f"{connection.port}/"
                    f"{connection.database}"
                )

            # MYSQL_URL = "mysql+pymysql://username:password@host:port/database"
            case Driver.MYSQL:
                return (
                    f"mysql+pymysql://"
                    f"{connection.username}:"
                    f"{connection.password}@"
                    f"{connection.host}:"
                    f"{connection.port}/"
                    f"{connection.database}"
                )

            # SQLITE_URL = "sqlite:///path"
            case Driver.SQLITE:
                return f"sqlite:///{connection.path}"

            # ORACLE_URL = ('oracle+oracledb://username:password@host:port/?service_name=database')
            case Driver.ORACLE:
                return (
                    f"oracle+oracledb://"
                    f"{connection.username}:"
                    f"{connection.password}@"
                    f"{connection.host}:"
                    f"{connection.port}/"
                    f"?service_name={connection.database}"
                )

            case _:
                raise ValueError(f"Driver no soportado: {connection.driver}")

    # =================
    # === LIFECYCLE ===
    # =================

    def close(self) -> None:
        """
        Libera todos los recursos asociados
        al engine SQLAlchemy.

        Notes:
            dispose() cierra el pool de conexiones
            y libera conexiones activas mantenidas
            por SQLAlchemy.
        """

        self.engine.dispose()
