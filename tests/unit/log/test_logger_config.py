import logging
from unittest.mock import patch

from log.logger_config import SUCCESS, setup_logging

# =============================================================================
# Nivel SUCCESS
# =============================================================================


def test_success_level_is_registered():
    """
    El nivel SUCCESS debe estar registrado en el
    sistema de logging.
    """

    assert logging.getLevelName(SUCCESS) == "SUCCESS"


def test_logger_has_success_method():
    """
    Los objetos Logger deben disponer del método
    success().
    """

    logger = logging.getLogger("test")

    assert hasattr(logger, "success")


def test_logger_success_does_not_raise_exception():
    """
    El método success() debe poder invocarse sin
    producir excepciones.
    """

    logger = logging.getLogger("test")
    logger.success("Mensaje de prueba")


def test_logger_success_calls_log():
    """
    success() debe invocar al método interno
    _log() cuando el nivel SUCCESS está habilitado.
    """

    logger = logging.getLogger("test")
    logger.setLevel(SUCCESS)

    with patch.object(logger, "_log") as mock_log:
        logger.success("Mensaje")

    mock_log.assert_called_once()


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
