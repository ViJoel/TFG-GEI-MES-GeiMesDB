import sqlite3

from entities.setting import Setting
from entities.setting_key import SettingKey
from log.app_logger import get_logger
from modules.database.model import get_connection as get_db_connection
from modules.database.wrapper import handle_db_errors

logger = get_logger(__name__)


def _map_row_to_setting(
    row: sqlite3.Row,
) -> Setting:
    """
    Reconstruye una entidad Setting
    a partir de una fila SQLite.

    Args:
        row (sqlite3.Row):
            Registro recuperado desde la base de datos.

    Returns:
        Setting:
            Ajuste reconstruido.
    """

    return Setting(
        key=SettingKey(row["key"]),
        value=row["value"],
    )


@handle_db_errors("guardar ajuste")
def save_setting(
    setting: Setting,
) -> None:
    """
    Inserta o actualiza un ajuste.

    Args:
        setting (Setting):
            Ajuste a guardar.
    """

    logger.info(
        "Saving setting '%s'...",
        setting.key.value,
    )

    query = """
    INSERT INTO settings (
        key,
        value
    )
    VALUES (?, ?)
    ON CONFLICT(key)
    DO UPDATE SET
        value = excluded.value
    """

    with get_db_connection() as conn:

        cur = conn.cursor()

        cur.execute(
            query,
            (
                setting.key.value,
                setting.value,
            ),
        )

    logger.success(
        "Setting '%s' saved.",
        setting.key.value,
    )


@handle_db_errors("obtener ajuste")
def get_setting(
    key: SettingKey,
) -> Setting | None:
    """
    Recupera un ajuste.

    Args:
        key (SettingKey):
            Clave del ajuste.

    Returns:
        Setting | None:
            Ajuste recuperado o ``None`` si no existe.
    """

    logger.info(
        "Getting setting '%s'...",
        key.value,
    )

    query = """
    SELECT
        key,
        value
    FROM settings
    WHERE key = ?
    """

    with get_db_connection() as conn:

        cur = conn.cursor()

        cur.execute(
            query,
            (key.value,),
        )

        row = cur.fetchone()

    if row is None:

        logger.info(
            "Setting '%s' not found.",
            key.value,
        )

        return None

    logger.success(
        "Setting '%s' loaded.",
        key.value,
    )

    return _map_row_to_setting(row)


@handle_db_errors("obtener todos los ajustes")
def get_all_settings(
) -> list[Setting]:
    """
    Recupera todos los ajustes.

    Returns:
        list[Setting]:
            Lista de ajustes almacenados.
    """

    logger.info(
        "Getting application settings..."
    )

    query = """
    SELECT
        key,
        value
    FROM settings
    ORDER BY key
    """

    settings: list[Setting] = []

    with get_db_connection() as conn:

        cur = conn.cursor()

        cur.execute(query)

        rows = cur.fetchall()

        for row in rows:
            settings.append(_map_row_to_setting(row))

    logger.success(
        "Loaded %d settings.",
        len(settings),
    )

    return settings
