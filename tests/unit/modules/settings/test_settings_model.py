from unittest.mock import (
    MagicMock,
    patch,
)

from entities.setting import Setting
from entities.setting_key import SettingKey
from modules.settings import model

# =============================================================================
# MAP ROW TO SETTING
# =============================================================================


def test_map_row_to_setting_returns_setting():
    """
    Comprueba que la fila se convierte en una entidad Setting.
    """

    row = {
        "key": SettingKey.THEME.value,
        "value": "dark",
    }

    result = model._map_row_to_setting(row)

    assert result == Setting(
        key=SettingKey.THEME,
        value="dark",
    )


# =============================================================================
# SAVE SETTING
# =============================================================================


def test_save_setting_executes_upsert_query():
    """
    Comprueba que se ejecuta la consulta para guardar el ajuste.
    """

    setting = Setting(
        key=SettingKey.THEME,
        value="dark",
    )

    cursor = MagicMock()
    connection = MagicMock()

    connection.cursor.return_value = cursor
    connection.__enter__.return_value = connection

    with patch(
        "modules.settings.model.get_db_connection",
        return_value=connection,
    ):

        model.save_setting(setting)

    cursor.execute.assert_called_once()

    query, params = cursor.execute.call_args.args

    assert "INSERT INTO settings" in query
    assert params == (
        setting.key.value,
        setting.value,
    )


# =============================================================================
# GET SETTING
# =============================================================================


def test_get_setting_returns_setting():
    """
    Comprueba que se devuelve el ajuste recuperado.
    """

    key = SettingKey.THEME

    row = {
        "key": key.value,
        "value": "dark",
    }

    cursor = MagicMock()
    cursor.fetchone.return_value = row

    connection = MagicMock()

    connection.cursor.return_value = cursor
    connection.__enter__.return_value = connection

    with patch(
        "modules.settings.model.get_db_connection",
        return_value=connection,
    ):

        result = model.get_setting(key)

    cursor.execute.assert_called_once()

    query, params = cursor.execute.call_args.args

    assert "SELECT" in query
    assert params == (key.value,)

    assert result == Setting(
        key=key,
        value="dark",
    )


def test_get_setting_returns_none():
    """
    Comprueba que se devuelve None cuando el ajuste no existe.
    """

    key = SettingKey.THEME

    cursor = MagicMock()
    cursor.fetchone.return_value = None

    connection = MagicMock()

    connection.cursor.return_value = cursor
    connection.__enter__.return_value = connection

    with patch(
        "modules.settings.model.get_db_connection",
        return_value=connection,
    ):

        result = model.get_setting(key)

    cursor.execute.assert_called_once()

    assert result is None


# =============================================================================
# GET ALL SETTINGS
# =============================================================================


def test_get_all_settings_returns_settings():
    """
    Comprueba que se devuelven todos los ajustes almacenados.
    """

    rows = [
        {
            "key": SettingKey.LANGUAGE.value,
            "value": "es",
        },
        {
            "key": SettingKey.THEME.value,
            "value": "dark",
        },
    ]

    cursor = MagicMock()
    cursor.fetchall.return_value = rows

    connection = MagicMock()

    connection.cursor.return_value = cursor
    connection.__enter__.return_value = connection

    with patch(
        "modules.settings.model.get_db_connection",
        return_value=connection,
    ):

        result = model.get_all_settings()

    cursor.execute.assert_called_once()

    assert result == [
        Setting(
            key=SettingKey.LANGUAGE,
            value="es",
        ),
        Setting(
            key=SettingKey.THEME,
            value="dark",
        ),
    ]


def test_get_all_settings_returns_empty_list():
    """
    Comprueba que se devuelve una lista vacía cuando no existen ajustes.
    """

    cursor = MagicMock()
    cursor.fetchall.return_value = []

    connection = MagicMock()

    connection.cursor.return_value = cursor
    connection.__enter__.return_value = connection

    with patch(
        "modules.settings.model.get_db_connection",
        return_value=connection,
    ):

        result = model.get_all_settings()

    cursor.execute.assert_called_once()

    assert result == []
