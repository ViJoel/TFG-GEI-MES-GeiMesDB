import logging
from dataclasses import dataclass

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.pool import NullPool

from entities.connection import Connection
from entities.driver import Driver

logger = logging.getLogger(__name__)


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
        engine = cls._build_engine(connection, connection_url)

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
                raise ValueError(f"Unsupported driver: {connection.driver}")

    @staticmethod
    def _build_engine(connection: Connection, connection_url: str) -> Engine:
        """
        Construye y configura el engine SQLAlchemy
        asociado a una conexión persistida.

        Args:
            connection (Connection):
                Configuración persistida utilizada
                para determinar el driver y opciones
                específicas del engine.

            connection_url (str):
                URL SQLAlchemy ya construida.

        Returns:
            Engine:
                Engine SQLAlchemy configurado.
        """

        logger.info("Creating engine...")

        # Configuración común reutilizable para
        # todos los engines de conexiones de red.
        base_config = {
            "pool_pre_ping": True,
            "pool_recycle": 3600,
        }

        engine = None

        match connection.driver:

            case Driver.SQLITE:
                engine = create_engine(
                    connection_url,
                    poolclass=NullPool,
                )

            case Driver.POSTGRESQL:
                engine = create_engine(
                    connection_url,
                    **base_config,
                    connect_args={"connect_timeout": 5},
                )

            case Driver.MYSQL:
                engine = create_engine(
                    connection_url,
                    **base_config,
                    connect_args={"connect_timeout": 5},
                )

            case Driver.ORACLE:
                engine = create_engine(
                    connection_url,
                    **base_config,
                    connect_args={"tcp_connect_timeout": 5},
                )

            case _:
                raise ValueError(f"Unsupported driver: {connection.driver}")

        logger.info(
            "Engine created: driver=%s, pool_pre_ping=%s, pool_recycle=%s.",
            connection.driver,
            base_config["pool_pre_ping"],
            base_config["pool_recycle"],
        )

        return engine

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
