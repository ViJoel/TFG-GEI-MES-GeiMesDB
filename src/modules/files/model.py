from pathlib import Path

from entities.file import File
from log.app_logger import get_logger

logger = get_logger(__name__)

ALLOWED_EXTENSIONS = {
    ".sql",
    ".txt",
}


def _normalize_extension(
    path: Path,
) -> Path:
    """
    Normaliza la extensión de un archivo.

    Mantiene las extensiones permitidas.
    Para cualquier otra extensión asigna la extensión
    por defecto .sql.
    """

    if path.suffix.lower() in ALLOWED_EXTENSIONS:
        return path

    return path.with_suffix(".sql")


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

    try:

        if path.suffix.lower() not in ALLOWED_EXTENSIONS:
            raise ValueError(f"Extension not allowed: {path.suffix}")

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        content = path.read_text(
            encoding="utf-8",
        )

        return File(
            path=path,
            content=content,
        )

    except (
        OSError,
        ValueError,
    ):

        logger.exception("Error opening file.")

        return None


def save_file(
    file: File,
) -> bool:
    """
    Guarda un archivo en disco.

    Si la ruta del archivo ha cambiado desde el último guardado,
    primero renombra el archivo existente y después escribe
    su contenido.

    Args:
        file:
            Archivo a guardar.

    Return:
        bool:
            - `True` si se guardó correctamente.
            - `False` si hubo algún error.
    """

    try:

        if file.path is None:
            raise ValueError("The file does not have a path asociated.")

        normalized_path = _normalize_extension(
            file.path,
        )

        if normalized_path != file.path:
            file.rename(
                normalized_path.name,
            )

        if file._saved_path is not None and file._saved_path != file.path:
            file._saved_path.rename(file.path)

        file.path.write_text(
            file.content,
            encoding="utf-8",
        )

        file.save_changes()

        return True

    except (
        OSError,
        ValueError,
    ):

        logger.exception("Error saving file.")

        return False
