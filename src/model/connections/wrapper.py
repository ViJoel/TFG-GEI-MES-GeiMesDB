import logging
from functools import wraps
from sqlite3 import IntegrityError, OperationalError
from .exceptions.connection_not_found import ConnectionNotFoundError

# Crear sub-logger
logger = logging.getLogger(__name__)


def handle_db_errors(operation_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Asumimos que el primer argumento o un kwarg es la 'connection'
            connection = kwargs.get("connection") or (args[0] if args else None)
            conn_id = getattr(connection, "id", "N/A")

            try:
                return func(*args, **kwargs)
            except ConnectionNotFoundError:
                logger.warning(
                    f"No se encontró la conexión con ID: {conn_id} para {operation_name}"
                )
                raise
            except IntegrityError as e:
                logger.warning(f"Intento de duplicar ID: {conn_id}. Error: {e}")
                raise
            except OperationalError as e:
                logger.error(
                    f"Error de acceso a la BD al {operation_name} (¿Existe el archivo?): {e}"
                )
                raise
            except Exception as e:
                logger.error(f"Error inesperado al {operation_name} conexión: {e}")
                raise

        return wrapper

    return decorator
