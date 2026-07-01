import logging
from unittest.mock import MagicMock

import pytest

import modules.sessions.manager as manager

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture(autouse=True)
def patch_logger_success(monkeypatch):
    """
    Evita fallos por logger.success.
    """

    logger = logging.getLogger("modules.sessions.manager")
    monkeypatch.setattr(logger, "success", logger.info, raising=False)


# =============================================================================
# _get_primary_key_columns
# =============================================================================


def test_get_primary_key_columns(monkeypatch):
    """
    Debe recuperar correctamente las columnas que
    forman la clave primaria de una tabla.
    """

    inspector = MagicMock()
    inspector.get_pk_constraint.return_value = {"constrained_columns": ["id"]}

    monkeypatch.setattr(
        manager,
        "inspect",
        MagicMock(return_value=inspector),
    )

    engine = MagicMock()

    result = manager._get_primary_key_columns(
        engine,
        "users",
    )

    assert result == ["id"]


def test_get_primary_key_columns_without_pk(monkeypatch):
    """
    Debe devolver una lista vacía cuando la tabla
    no tenga clave primaria.
    """

    inspector = MagicMock()
    inspector.get_pk_constraint.return_value = {}

    monkeypatch.setattr(
        manager,
        "inspect",
        MagicMock(return_value=inspector),
    )

    engine = MagicMock()

    result = manager._get_primary_key_columns(
        engine,
        "users",
    )

    assert result == []


# =============================================================================
# _get_editable_metadata
# =============================================================================


def test_get_editable_metadata(monkeypatch):
    """
    Debe devolver el nombre de la tabla y su clave
    primaria para consultas editables.
    """

    monkeypatch.setattr(
        manager,
        "_get_primary_key_columns",
        MagicMock(return_value=["id"]),
    )

    engine = MagicMock()

    table, pk = manager._get_editable_metadata(
        "SELECT * FROM users",
        engine,
    )

    assert table == "users"
    assert pk == ["id"]


def test_get_editable_metadata_non_editable():
    """
    Debe devolver valores vacíos cuando la consulta
    no sea editable.
    """

    engine = MagicMock()

    table, pk = manager._get_editable_metadata(
        "SELECT id FROM users",
        engine,
    )

    assert table is None
    assert pk == []


def test_get_editable_metadata_without_table(monkeypatch):
    """
    Debe devolver valores vacíos cuando no pueda
    determinarse la tabla objetivo.
    """

    monkeypatch.setattr(
        manager,
        "is_editable_query",
        MagicMock(return_value=True),
    )

    monkeypatch.setattr(
        manager,
        "_extract_table_name",
        MagicMock(return_value=None),
    )

    engine = MagicMock()

    table, pk = manager._get_editable_metadata(
        "SELECT * FROM",
        engine,
    )

    assert table is None
    assert pk == []
