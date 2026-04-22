import uuid
from dataclasses import dataclass, field
from typing import Optional

from model.connections.driver import Driver


@dataclass(kw_only=True)  # Obliga a usar nombres de campo
class Connection:
    """
    Configuración técnica para el acceso a diferentes motores de bases de datos.

    Esta clase permite definir tanto conexiones de red (PostgreSQL, MySQL)
    como conexiones basadas en archivos locales (SQLite), utilizando el
    identificador único para la persistencia en la base de datos de la aplicación.

    Attributes:
        id (str): UUID identificador de la conexión. Generado automáticamente si se omite.
        name (str): Etiqueta descriptiva para identificar la conexión en la interfaz.
        driver (Driver): Miembro del enumerado que define el motor (ej. Driver.SQLITE).
        host (Optional[str]): Dirección del servidor. No requerido para SQLite.
        port (Optional[int]): Puerto de red. No requerido para SQLite.
        database (Optional[str]): Nombre de la base de datos en el servidor.
        username (Optional[str]): Credencial de usuario.
        password (Optional[str]): Credencial de acceso (sensible).
        path (Optional[str]): Ruta absoluta al archivo .db (exclusivo para Driver.SQLITE).
    """

    id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )  # Si no pasas un id, se ejecuta el lambda y genera un UUID string
    name: str
    driver: Driver
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    path: Optional[str] = None

    def __eq__(self, other):
        """
        Compara la igualdad entre dos conexiones basándose únicamente en su ID.

        Args:
            other (object): Instancia a comparar.

        Returns:
            bool: True si representan el mismo registro de conexión.
        """
        if not isinstance(other, Connection):
            return False
        return self.id == other.id
