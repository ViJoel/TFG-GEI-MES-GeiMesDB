from dataclasses import is_dataclass

from entities.setting import Setting
from entities.setting_key import SettingKey

# =============================================================================
# TESTS
# =============================================================================


def test_setting_is_dataclass():
    """
    Verifica que Setting es un dataclass.
    """

    assert is_dataclass(Setting)


def test_setting_stores_values():
    """
    Verifica que almacena correctamente
    la clave y el valor.
    """

    setting = Setting(
        key=SettingKey.THEME,
        value="dark",
    )

    assert setting.key is SettingKey.THEME
    assert setting.value == "dark"


def test_setting_uses_slots():
    """
    Verifica que el dataclass utiliza slots.
    """

    setting = Setting(
        key=SettingKey.THEME,
        value="dark",
    )

    assert hasattr(
        setting,
        "__slots__",
    )

    assert setting.__slots__ == (
        "key",
        "value",
    )


def test_setting_equality():
    """
    Verifica que dos instancias con el mismo
    contenido son iguales.
    """

    left = Setting(
        key=SettingKey.THEME,
        value="dark",
    )

    right = Setting(
        key=SettingKey.THEME,
        value="dark",
    )

    assert left == right
