import logging
from functools import wraps
from sqlite3 import IntegrityError, OperationalError

logger = logging.getLogger(__name__)

# TODO: PythonDoc
def handle_db_errors(operation_name):
    """
    Decorador agnóstico para capturar errores técnicos de SQLite.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except IntegrityError as e:
                # Error de claves duplicadas o violaciones de constraints
                logger.warning(f"Conflicto de integridad al {operation_name}: {e}")
                raise
            except OperationalError as e:
                # Error de archivo, permisos o base de datos bloqueada
                logger.error(f"Fallo operativo al {operation_name}: {e}")
                raise
            except Exception as e:
                # Cualquier otro error inesperado
                logger.error(f"Error no controlado al {operation_name}: {e}")
                raise

        return wrapper

    return decorator
