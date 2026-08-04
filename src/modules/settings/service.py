from entities.setting import Setting
from entities.setting_key import SettingKey
from modules.settings.model import get_all_settings as gas
from modules.settings.model import get_setting as gs
from modules.settings.model import save_setting as ss


def save_setting(
    setting: Setting,
) -> None:
    """
    Orquesta el guardado de un ajuste
    delegando la operación en la capa
    de datos.

    Args:
        setting (Setting):
            Ajuste a guardar.
    """

    return ss(
        setting=setting,
    )


def get_setting(
    key: SettingKey,
) -> Setting | None:
    """
    Solicita un ajuste a partir
    de su clave.

    Args:
        key (SettingKey):
            Clave del ajuste.

    Returns:
        Setting | None:
            Ajuste encontrado o ``None``
            si no existe.
    """

    return gs(
        key=key,
    )


def get_all_settings() -> list[Setting]:
    """
    Solicita todos los ajustes
    almacenados.

    Returns:
        list[Setting]:
            Lista de ajustes.
    """

    return gas()
