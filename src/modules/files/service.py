from pathlib import Path

from entities.file import File
from modules.files import model


def save_file(
    file: File,
) -> bool:
    """
    Guarda un archivo en disco.

    Args:
        file:
            Archivo a guardar.

    Returns:
        bool:
            - `True` si se guardó correctamente.
            - `False` si hubo algún error.
    """

    return model.save_file(file)


def open_file(
    path: Path,
) -> File | None:
    """
    Abre un archivo existente en disco.

    Args:
        path:
            Ruta del archivo a abrir.

    Returns:
        File | None:
            Entidad File si se abrió correctamente.
            `None` si hubo algún error.
    """

    return model.open_file(path)
