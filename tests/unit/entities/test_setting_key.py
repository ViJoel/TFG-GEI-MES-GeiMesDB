from enum import StrEnum

from entities.setting_key import SettingKey

# =============================================================================
# TESTS
# =============================================================================


def test_setting_key_is_str_enum():
    """
    Verifica que SettingKey hereda de StrEnum.
    """

    assert issubclass(
        SettingKey,
        StrEnum,
    )


def test_setting_key_contains_expected_members():
    """
    Verifica que expone todas las claves esperadas.
    """

    assert SettingKey.THEME.name == "THEME"
    assert SettingKey.LANGUAGE.name == "LANGUAGE"


def test_setting_key_values():
    """
    Verifica que auto() genera los valores esperados.
    """

    assert SettingKey.THEME.value == "theme"
    assert SettingKey.LANGUAGE.value == "language"


def test_setting_key_values_are_unique():
    """
    Verifica que todas las claves son únicas.
    """

    assert len({member.value for member in SettingKey}) == len(SettingKey)
