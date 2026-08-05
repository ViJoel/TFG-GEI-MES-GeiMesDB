from unittest.mock import (
    MagicMock,
    patch,
)

from entities.setting import Setting
from entities.setting_key import SettingKey
from modules.settings import service  # ajusta el import al nombre real del fichero

# =============================================================================
# SAVE SETTING
# =============================================================================


def test_save_setting_delegates_to_model():

    setting = MagicMock(spec=Setting)

    with patch("modules.settings.service.ss") as save_setting_mock:

        result = service.save_setting(setting)

    save_setting_mock.assert_called_once_with(
        setting=setting,
    )

    assert result is save_setting_mock.return_value


# =============================================================================
# GET SETTING
# =============================================================================


def test_get_setting_delegates_to_model():

    key = MagicMock(spec=SettingKey)

    expected = MagicMock(spec=Setting)

    with patch(
        "modules.settings.service.gs",
        return_value=expected,
    ) as get_setting_mock:

        result = service.get_setting(key)

    get_setting_mock.assert_called_once_with(
        key=key,
    )

    assert result is expected


def test_get_setting_returns_none():

    key = MagicMock(spec=SettingKey)

    with patch(
        "modules.settings.service.gs",
        return_value=None,
    ) as get_setting_mock:

        result = service.get_setting(key)

    get_setting_mock.assert_called_once_with(
        key=key,
    )

    assert result is None


# =============================================================================
# GET ALL SETTINGS
# =============================================================================


def test_get_all_settings_delegates_to_model():

    expected = [
        MagicMock(spec=Setting),
        MagicMock(spec=Setting),
    ]

    with patch(
        "modules.settings.service.gas",
        return_value=expected,
    ) as get_all_settings_mock:

        result = service.get_all_settings()

    get_all_settings_mock.assert_called_once_with()

    assert result is expected
