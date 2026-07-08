from datetime import (
    datetime,
    timezone,
)

from entities.queries_history_entry import QueriesHistoryEntry

# =============================================================================
# INIT
# =============================================================================


def test_create_entry_with_values():
    """
    Verifica que la entidad almacena correctamente
    los valores proporcionados.
    """

    executed_at = datetime(
        2025,
        1,
        1,
        tzinfo=timezone.utc,
    )

    entry = QueriesHistoryEntry(
        connection_id="connection-1",
        query="SELECT * FROM users",
        executed_at=executed_at,
    )

    assert entry.connection_id == "connection-1"
    assert entry.query == "SELECT * FROM users"
    assert entry.executed_at == executed_at


def test_executed_at_is_generated_by_default():
    """
    Verifica que executed_at se genera automáticamente
    cuando no se proporciona.
    """

    before = datetime.now(timezone.utc)

    entry = QueriesHistoryEntry()

    after = datetime.now(timezone.utc)

    assert before <= entry.executed_at <= after


def test_default_values():
    """
    Verifica los valores por defecto de la entidad.
    """

    entry = QueriesHistoryEntry()

    assert entry.connection_id == ""
    assert entry.query == ""
    assert entry.executed_at is not None
