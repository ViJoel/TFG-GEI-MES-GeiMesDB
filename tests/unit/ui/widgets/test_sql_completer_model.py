from unittest.mock import (
    MagicMock,
    patch,
)

from PySide6.QtCore import Qt

from ui.widgets.workspace.sql_editor.sql_completer_model import SqlCompleterModel


def test_refresh_loads_completion_items():
    """
    Verifica que refresh crea items en el modelo
    con los datos disponibles.
    """

    model = SqlCompleterModel()

    model.clear()

    with patch(
        "ui.widgets.workspace.sql_editor.sql_completer_model.SQL_STATIC_COMPLETION_DATA",
        {
            "keywords": {
                "values": {"SELECT", "FROM"},
                "color": "keyword",
            },
        },
    ):
        model.refresh()

    assert model.rowCount() == 2

    values = {model.item(row).text() for row in range(model.rowCount())}

    assert values == {"SELECT", "FROM"}


def test_refresh_sorts_items_case_insensitive():
    """
    Verifica que los elementos aparecen ordenados
    alfabéticamente sin distinguir mayúsculas.
    """

    model = SqlCompleterModel()

    model.clear()

    with patch(
        "ui.widgets.workspace.sql_editor.sql_completer_model.SQL_STATIC_COMPLETION_DATA",
        {
            "keywords": {
                "values": {"select", "FROM", "and"},
                "color": "keyword",
            },
        },
    ):
        model.refresh()

    values = [model.item(row).text() for row in range(model.rowCount())]

    assert values == [
        "and",
        "FROM",
        "select",
    ]


def test_refresh_applies_foreground_color():
    """
    Verifica que cada item recibe el color
    correspondiente.
    """

    model = SqlCompleterModel()

    model.clear()

    with patch(
        "ui.widgets.workspace.sql_editor.sql_completer_model.SQL_STATIC_COMPLETION_DATA",
        {
            "keywords": {
                "values": {"SELECT"},
                "color": "keyword",
            },
        },
    ), patch(
        "ui.widgets.workspace.sql_editor.sql_completer_model.ThemeManager.get_color",
        return_value="#ffffff",
    ):

        model.refresh()

    item = model.item(0)

    color = item.data(
        Qt.ItemDataRole.ForegroundRole,
    )

    assert color.name() == "#ffffff"


def test_update_refreshes_model_when_dynamic_data_changes():
    """
    Verifica que update reconstruye el modelo
    cuando hay cambios dinámicos.
    """

    model = SqlCompleterModel()

    model._document_completion_provider.update = MagicMock(
        return_value=True,
    )

    model.refresh = MagicMock()

    changed = model.update(
        "SELECT :id",
    )

    assert changed is True

    model.refresh.assert_called_once()


def test_update_does_not_refresh_when_no_changes():
    """
    Verifica que update no reconstruye el modelo
    si no hay cambios.
    """

    model = SqlCompleterModel()

    model._document_completion_provider.update = MagicMock(
        return_value=False,
    )

    model.refresh = MagicMock()

    changed = model.update(
        "SELECT 1",
    )

    assert changed is False

    model.refresh.assert_not_called()
