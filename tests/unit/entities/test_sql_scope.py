from entities.sql_scope import SqlScope

# =============================================================================
# MEMBERS
# =============================================================================


def test_sql_scope_members_exist():
    """
    Verifica que los miembros del enum SqlScope existen correctamente.
    """

    assert SqlScope.ACTUAL_QUERY
    assert SqlScope.FULL_SCRIPT
    assert SqlScope.SELECTED_TEXT


# =============================================================================
# LOOKUP
# =============================================================================


def test_sql_scope_lookup_by_value():
    """
    Verifica que el enum puede resolverse a partir de su valor interno.
    """

    assert SqlScope(SqlScope.ACTUAL_QUERY.value) is SqlScope.ACTUAL_QUERY
    assert SqlScope(SqlScope.FULL_SCRIPT.value) is SqlScope.FULL_SCRIPT
    assert SqlScope(SqlScope.SELECTED_TEXT.value) is SqlScope.SELECTED_TEXT


# =============================================================================
# ITERATION
# =============================================================================


def test_sql_scope_iteration():
    """
    Verifica que el enum SqlScope es iterable y contiene todos sus miembros.
    """

    values = list(SqlScope)

    assert SqlScope.ACTUAL_QUERY in values
    assert SqlScope.FULL_SCRIPT in values
    assert SqlScope.SELECTED_TEXT in values
    assert len(values) == 3


# =============================================================================
# NAMES
# =============================================================================


def test_sql_scope_names():
    """
    Verifica que los nombres de los miembros del enum SqlScope son correctos.
    """

    assert SqlScope.ACTUAL_QUERY.name == "ACTUAL_QUERY"
    assert SqlScope.FULL_SCRIPT.name == "FULL_SCRIPT"
    assert SqlScope.SELECTED_TEXT.name == "SELECTED_TEXT"
