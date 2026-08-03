from unittest.mock import MagicMock

import pytest

import modules.sessions.service as service

# =============================================================================
# FIXTURE: MOCK DEL MANAGER
# =============================================================================


@pytest.fixture(autouse=True)
def mock_manager(monkeypatch):
    """
    Sustituye la capa manager por mocks para aislar
    completamente la capa de servicio.
    """

    monkeypatch.setattr(service, "os", MagicMock())
    monkeypatch.setattr(service, "cs", MagicMock())
    monkeypatch.setattr(service, "gs", MagicMock())
    monkeypatch.setattr(service, "hs", MagicMock())
    monkeypatch.setattr(service, "cas", MagicMock())
    monkeypatch.setattr(service, "tc", MagicMock())
    monkeypatch.setattr(service, "eq", MagicMock())
    monkeypatch.setattr(service, "ieq", MagicMock())
    monkeypatch.setattr(service, "es", MagicMock())
    monkeypatch.setattr(service, "eu", MagicMock())


def test_open_session():
    """
    Verifica que open_session delega correctamente
    la apertura de una sesión al manager.
    """
    connection = MagicMock()

    service.os.return_value = "session"

    result = service.open_session(connection)

    service.os.assert_called_once_with(connection)
    assert result == "session"


def test_close_session():
    """
    Verifica que close_session delega correctamente
    el cierre de una sesión al manager.
    """
    service.close_session("1")

    service.cs.assert_called_once_with("1")


def test_get_session():
    """
    Verifica que get_session delega correctamente
    la recuperación de una sesión al manager.
    """
    service.gs.return_value = "session"

    result = service.get_session("1")

    service.gs.assert_called_once_with("1")
    assert result == "session"


def test_has_session():
    """
    Verifica que has_session delega correctamente
    la comprobación de existencia de una sesión.
    """
    service.hs.return_value = True

    result = service.has_session("1")

    service.hs.assert_called_once_with("1")
    assert result is True


def test_close_all_sessions():
    """
    Verifica que close_all_sessions delega correctamente
    el cierre de todas las sesiones al manager.
    """
    service.close_all_sessions()

    service.cas.assert_called_once()


def test_test_connection():
    """
    Verifica que test_connection delega correctamente
    la comprobación de conectividad al manager.
    """
    connection = MagicMock()

    service.tc.return_value = True

    result = service.test_connection(connection)

    service.tc.assert_called_once_with(connection)
    assert result is True


def test_execute_query():
    """
    Verifica que execute_query delega correctamente
    la ejecución de una consulta SQL al manager.
    """
    service.eq.return_value = "result"

    result = service.execute_query("1", "SELECT * FROM table")

    service.eq.assert_called_once_with("1", "SELECT * FROM table")
    assert result == "result"


def test_is_editable_query():
    """
    Verifica que is_editable_query delega correctamente
    la comprobación de editabilidad de una consulta.
    """
    query = "SELECT * FROM table"

    service.ieq.return_value = True

    result = service.is_editable_query(query)

    service.ieq.assert_called_once_with(query)
    assert result is True


def test_execute_script():
    """
    Verifica que execute_script delega correctamente
    la ejecución de un script SQL al manager.
    """
    queries = [
        "SELECT 1",
        "SELECT 2",
    ]

    service.es.return_value = "result"

    result = service.execute_script("1", queries)

    service.es.assert_called_once_with("1", queries)
    assert result == "result"


def test_execute_updates():
    """
    Verifica que execute_updates delega correctamente
    la ejecución de operaciones UPDATE al manager.
    """

    operations = [
        MagicMock(),
        MagicMock(),
    ]

    service.eu.return_value = "result"

    result = service.execute_updates(
        connection_id="1",
        operations=operations,
    )

    service.eu.assert_called_once_with(
        connection_id="1",
        operations=operations,
    )

    assert result == "result"
