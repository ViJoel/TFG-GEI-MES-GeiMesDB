from dataclasses import dataclass

from entities.setting_key import SettingKey


@dataclass(
    kw_only=True,
    slots=True,
)
class Setting:
    """
    Representa un ajuste persistente de la aplicación.
    """

    key: SettingKey
    value: str
