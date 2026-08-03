import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QWidget,
)

from ui.widgets.dialogs.confirmation_dialog import ConfirmationDialog


@pytest.fixture
def parent_widget(qtbot):
    widget = QWidget()
    widget.resize(800, 600)
    widget.show()

    qtbot.addWidget(widget)

    return widget


@pytest.fixture
def dialog(parent_widget, qtbot):
    dialog = ConfirmationDialog(
        title="Delete item",
        message="Are you sure?",
        parent=parent_widget,
    )

    qtbot.addWidget(dialog)

    return dialog


def test_dialog_is_initialized(dialog):
    assert dialog.windowTitle() == "Delete item"
    assert dialog.objectName() == "confirmation_dialog"

    assert dialog.isModal()

    assert dialog.message_label.text() == "Are you sure?"

    assert dialog.accept_button.text() == "Accept"
    assert dialog.cancel_button.text() == "Cancel"


def test_dialog_visual_properties(dialog):
    assert dialog.windowFlags() & Qt.FramelessWindowHint

    assert dialog.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)


def test_accept_button_emits_confirmed(dialog, qtbot):
    with qtbot.waitSignal(dialog.confirmed):
        qtbot.mouseClick(
            dialog.accept_button,
            Qt.LeftButton,
        )


def test_cancel_button_emits_cancelled(dialog, qtbot):
    with qtbot.waitSignal(dialog.cancelled):
        qtbot.mouseClick(
            dialog.cancel_button,
            Qt.LeftButton,
        )


def test_accept_sets_dialog_result(dialog, qtbot):
    qtbot.mouseClick(
        dialog.accept_button,
        Qt.LeftButton,
    )

    assert dialog.result() == QDialog.Accepted


def test_cancel_sets_dialog_result(dialog, qtbot):
    qtbot.mouseClick(
        dialog.cancel_button,
        Qt.LeftButton,
    )

    assert dialog.result() == QDialog.Rejected


def test_message_is_set_from_constructor(parent_widget, qtbot):
    dialog = ConfirmationDialog(
        title="Title",
        message="Custom message",
        parent=parent_widget,
    )

    qtbot.addWidget(dialog)

    assert dialog.message_label.text() == "Custom message"


def test_origin_widget_is_saved(dialog, parent_widget):
    assert dialog.origin_widget is parent_widget
