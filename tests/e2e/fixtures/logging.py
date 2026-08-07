from pathlib import Path

import pytest

from log.app_logger import setup_logging


@pytest.fixture
def temporary_logging(
    tmp_path: Path,
) -> Path:
    """
    Configura el sistema de logging para que
    escriba todos los archivos en un directorio
    temporal aislado.

    Returns:
        Path:
            Directorio temporal utilizado para
            almacenar los logs del test.
    """

    log_directory = tmp_path / "logs"

    setup_logging(
        base_dir=str(log_directory),
    )

    return log_directory
