import logging
from unittest.mock import patch

from log.logger_config import (
    SUCCESS,
    setup_logging,
)

# =============================================================================
# Nivel SUCCESS
# =============================================================================


def test_success_level_is_registered():
    """
    El nivel SUCCESS debe estar registrado en el
    sistema de logging.
    """

    assert logging.getLevelName(SUCCESS) == "SUCCESS"


# =============================================================================
# Configuración
# =============================================================================


def test_setup_logging_creates_log_directory(tmp_path):
    """
    setup_logging() debe crear el directorio de
    logs cuando no existe.
    """

    setup_logging(base_dir=str(tmp_path))

    assert (tmp_path / "geimesdb_logs").exists()


def test_setup_logging_creates_log_file(tmp_path):
    """
    setup_logging() debe crear el archivo de log.
    """

    setup_logging(base_dir=str(tmp_path))

    assert (tmp_path / "geimesdb_logs" / "app.log").exists()


def test_setup_logging_can_be_called_without_errors(tmp_path):
    """
    setup_logging() debe poder ejecutarse sin
    lanzar excepciones.
    """

    setup_logging(base_dir=str(tmp_path))


def test_setup_logging_default_base_dir(tmp_path):
    with patch("log.logger_config.os.path.dirname") as mock_dirname:
        mock_dirname.return_value = str(tmp_path)

        setup_logging()  # base_dir = None

        assert (tmp_path / "geimesdb_logs").exists()


def test_setup_logging_pyinstaller_mode(tmp_path):
    fake_exe = tmp_path / "fake_app"
    fake_exe.write_text("")

    with patch("log.logger_config.sys.executable", str(fake_exe)), patch(
        "log.logger_config.sys.frozen", True, create=True
    ):

        setup_logging(base_dir=None)

        log_dir = tmp_path / "geimesdb_logs"
        log_file = log_dir / "app.log"

        assert log_dir.exists()
        assert log_file.exists()
