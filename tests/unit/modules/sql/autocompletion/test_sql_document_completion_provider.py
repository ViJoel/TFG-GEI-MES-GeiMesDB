from modules.sql.autocompletion.dynamic_data import (
    SqlDynamicCompletionData,
)
from modules.sql.autocompletion.sql_document_completion_provider import (
    SqlDocumentCompletionProvider,
)


def test_update_extracts_parameters_and_variables():
    """
    Verifica que se extraen parámetros y variables
    del documento SQL.
    """

    provider = SqlDocumentCompletionProvider()
    dynamic_data = SqlDynamicCompletionData()

    changed = provider.update(
        """
        SELECT *
        FROM users
        WHERE id = :user_id
        AND name = $name
        AND value = @variable
        AND other = @@global;
        """,
        dynamic_data,
    )

    assert changed is True

    assert dynamic_data.get_data()["parameters"]["values"] == {
        ":user_id",
        "$name",
    }

    assert dynamic_data.get_data()["variables"]["values"] == {
        "@variable",
        "@@global",
    }


def test_update_returns_false_when_data_is_already_updated():
    """
    Verifica que no actualiza cuando los datos
    ya coinciden.
    """

    provider = SqlDocumentCompletionProvider()
    dynamic_data = SqlDynamicCompletionData()

    provider.update(
        "SELECT * FROM users WHERE id = :id",
        dynamic_data,
    )

    changed = provider.update(
        "SELECT * FROM users WHERE id = :id",
        dynamic_data,
    )

    assert changed is False


def test_update_returns_true_when_values_change():
    """
    Verifica que devuelve True cuando aparecen
    nuevos valores dinámicos.
    """

    provider = SqlDocumentCompletionProvider()
    dynamic_data = SqlDynamicCompletionData()

    provider.update(
        "SELECT * FROM users WHERE id = :old_id",
        dynamic_data,
    )

    changed = provider.update(
        "SELECT * FROM users WHERE id = :new_id",
        dynamic_data,
    )

    assert changed is True

    assert dynamic_data.get_data()["parameters"]["values"] == {
        ":new_id",
    }


def test_update_returns_false_for_document_without_dynamic_values():
    """
    Verifica que un documento sin parámetros ni
    variables no provoca cambios.
    """

    provider = SqlDocumentCompletionProvider()
    dynamic_data = SqlDynamicCompletionData()

    changed = provider.update(
        "SELECT * FROM users;",
        dynamic_data,
    )

    assert changed is False
