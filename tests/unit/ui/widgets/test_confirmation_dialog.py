import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QWidget,
)

from ui.widgets.dialogs.confirmation_dialog import ConfirmationDialog

# =============================================================================
# FIXTURES
# =============================================================================


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


# =============================================================================
# INIT
# =============================================================================


def test_dialog_is_initialized(dialog):
    assert dialog.windowTitle() == "Delete item"
    assert dialog.objectName() == "confirmation_dialog"

    assert dialog.isModal()

    assert dialog.message_view.toPlainText() == "Are you sure?"

    assert dialog.accept_button.text() == "Accept"
    assert dialog.cancel_button.text() == "Cancel"


def test_message_is_set_from_constructor(parent_widget, qtbot):
    dialog = ConfirmationDialog(
        title="Title",
        message="Custom message",
        parent=parent_widget,
    )

    qtbot.addWidget(dialog)

    assert dialog.message_view.toPlainText() == "Custom message"


def test_origin_widget_is_saved(dialog, parent_widget):
    assert dialog.origin_widget is parent_widget


def test_dialog_parent_is_parent_window(dialog, parent_widget):
    assert dialog.parent() is parent_widget.window()


# =============================================================================
# UI SETUP
# =============================================================================


def test_message_view_is_read_only(dialog):
    assert dialog.message_view.isReadOnly()


def test_message_view_has_no_frame(dialog):
    from PySide6.QtWidgets import QFrame

    assert dialog.message_view.frameStyle() == QFrame.NoFrame


def test_message_view_does_not_accept_rich_text(dialog):
    assert not dialog.message_view.acceptRichText()


def test_message_view_has_no_text_interaction(dialog):
    assert (
        dialog.message_view.textInteractionFlags()
        == Qt.TextInteractionFlag.NoTextInteraction
    )


def test_message_view_has_no_focus(dialog):
    assert dialog.message_view.focusPolicy() == Qt.FocusPolicy.NoFocus


def test_button_types(dialog):
    assert dialog.cancel_button.property("type") == "primary"
    assert dialog.accept_button.property("type") == "danger"


# =============================================================================
# UI HELPERS
# =============================================================================


def test_dialog_visual_properties(dialog):
    assert dialog.windowFlags() & Qt.FramelessWindowHint

    assert dialog.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)


def test_dialog_matches_parent_geometry(dialog):
    assert dialog.geometry() == dialog.parent().rect()


def test_message_height_is_adjusted(dialog):
    assert dialog.message_view.height() > 0


def test_long_message_increases_height(parent_widget, qtbot):
    dialog = ConfirmationDialog(
        title="Title",
        message="Lorem ipsum " * 300,
        parent=parent_widget,
    )

    qtbot.addWidget(dialog)

    assert dialog.message_view.height() > 100


# =============================================================================
# EVENT HANDLERS
# =============================================================================


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
