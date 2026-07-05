from entities.sql_scope import SqlScope

# =============================================================================
# MEMBERS
# =============================================================================


def test_sql_scope_members_exist():
    """
    Verifica que los miembros del enum SqlScope existen correctamente.
    """

    assert SqlScope.SELECTED_TEXT
    assert SqlScope.FULL_SCRIPT


# =============================================================================
# LOOKUP
# =============================================================================


def test_sql_scope_lookup_by_value():
    """
    Verifica que el enum puede resolverse a partir de su valor interno.
    """

    assert SqlScope(SqlScope.SELECTED_TEXT.value) is SqlScope.SELECTED_TEXT
    assert SqlScope(SqlScope.FULL_SCRIPT.value) is SqlScope.FULL_SCRIPT


# =============================================================================
# ITERATION
# =============================================================================


def test_sql_scope_iteration():
    """
    Verifica que el enum SqlScope es iterable y contiene todos sus miembros.
    """

    values = list(SqlScope)

    assert SqlScope.SELECTED_TEXT in values
    assert SqlScope.FULL_SCRIPT in values
    assert len(values) == 2


# =============================================================================
# NAMES
# =============================================================================


def test_sql_scope_names():
    """
    Verifica que los nombres de los miembros del enum SqlScope son correctos.
    """

    assert SqlScope.SELECTED_TEXT.name == "SELECTED_TEXT"
    assert SqlScope.FULL_SCRIPT.name == "FULL_SCRIPT"
