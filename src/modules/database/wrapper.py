from functools import wraps
from sqlite3 import (
    IntegrityError,
    OperationalError,
)

from log.app_logger import get_logger

logger = get_logger(__name__)


def handle_db_errors(operation_name):
    """
    Decorador para centralizar el manejo y registro
    de errores relacionados con SQLite.

    El decorador captura las excepciones más comunes
    de persistencia y genera logs contextualizados
    según la operación ejecutada.

    Args:
        operation_name (str):
            Descripción legible de la operación
            que se está ejecutando.

    Returns:
        callable:
            Función decorada con manejo de errores.
    """

    def decorator(func):
        """
        Envuelve la función original añadiendo
        control centralizado de excepciones SQLite.

        Args:
            func (callable):
                Función objetivo a decorar.

        Returns:
            callable:
                Wrapper con manejo de errores.
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            """
            Ejecuta la función decorada interceptando
            errores comunes de persistencia.

            Raises:
                IntegrityError:
                    Violaciones de integridad como
                    claves duplicadas o constraints.

                OperationalError:
                    Problemas operativos de SQLite
                    como bloqueos, permisos o acceso
                    al archivo de base de datos.

                Exception:
                    Cualquier error inesperado no controlado.
            """

            try:
                return func(*args, **kwargs)

            # Violaciones de constraints, claves únicas,
            # foreign keys o integridad relacional.
            except IntegrityError as e:
                logger.warning(f"Conflicto de integridad al {operation_name}: {e}")
                raise

            # Problemas relacionados con acceso a la BD,
            # permisos, locking o corrupción.
            except OperationalError as e:
                logger.error(f"Fallo operativo al {operation_name}: {e}")
                raise

            # Fallback para cualquier excepción no prevista.
            except Exception as e:
                logger.error(f"Error no controlado al {operation_name}: {e}")
                raise

        return wrapper

    return decorator
