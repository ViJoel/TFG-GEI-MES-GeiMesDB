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
# QT OVERRIDES
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


def test_accept_restores_previous_focus(
    parent_widget,
    qtbot,
    mocker,
):
    """
    Verifica que al aceptar el diálogo se restaura
    el foco al widget que lo tenía previamente.
    """

    previous = mocker.Mock()

    mocker.patch(
        "ui.widgets.dialogs.confirmation_dialog.QApplication.focusWidget",
        return_value=previous,
    )

    dialog = ConfirmationDialog(
        "Title",
        "Message",
        parent_widget,
    )

    qtbot.addWidget(dialog)

    dialog.accept()

    previous.setFocus.assert_called_once()


def test_reject_restores_previous_focus(
    parent_widget,
    qtbot,
    mocker,
):
    """
    Verifica que al cancelar el diálogo se restaura
    el foco al widget que lo tenía previamente.
    """

    previous = mocker.Mock()

    mocker.patch(
        "ui.widgets.dialogs.confirmation_dialog.QApplication.focusWidget",
        return_value=previous,
    )

    dialog = ConfirmationDialog(
        "Title",
        "Message",
        parent_widget,
    )

    qtbot.addWidget(dialog)

    dialog.reject()

    previous.setFocus.assert_called_once()


def test_accept_without_previous_focus(
    parent_widget,
    qtbot,
    mocker,
):
    """
    Verifica que aceptar el diálogo funciona
    correctamente cuando no existe un widget con
    el foco previamente.
    """

    mocker.patch(
        "ui.widgets.dialogs.confirmation_dialog.QApplication.focusWidget",
        return_value=None,
    )

    dialog = ConfirmationDialog(
        "Title",
        "Message",
        parent_widget,
    )

    qtbot.addWidget(dialog)

    dialog.accept()

    assert dialog.result() == QDialog.Accepted


def test_show_event_focuses_accept_button(
    dialog,
    qtbot,
    mocker,
):
    """
    Verifica que el diálogo solicita el foco para
    el botón de aceptación al mostrarse.
    """

    set_focus = mocker.patch.object(
        dialog.accept_button,
        "setFocus",
    )

    dialog.show()

    qtbot.waitExposed(dialog)

    set_focus.assert_called_once()


def test_focus_next_prev_child_switches_to_cancel(
    dialog,
    mocker,
):
    """
    Verifica que la navegación con Tab solicita el
    foco para el botón de cancelación.
    """

    mocker.patch.object(
        dialog.accept_button,
        "hasFocus",
        return_value=True,
    )

    set_focus = mocker.patch.object(
        dialog.cancel_button,
        "setFocus",
    )

    assert dialog.focusNextPrevChild(True)

    set_focus.assert_called_once()


def test_focus_next_prev_child_switches_to_accept(
    dialog,
    mocker,
):
    """
    Verifica que la navegación con Tab solicita el
    foco para el botón de aceptación.
    """

    mocker.patch.object(
        dialog.accept_button,
        "hasFocus",
        return_value=False,
    )

    set_focus = mocker.patch.object(
        dialog.accept_button,
        "setFocus",
    )

    assert dialog.focusNextPrevChild(True)

    set_focus.assert_called_once()


def test_message_view_uses_arrow_cursor(
    dialog,
):
    """
    Verifica que el visor de texto utiliza el
    cursor de flecha tanto en el widget como en
    su viewport.
    """

    assert dialog.message_view.cursor().shape() == Qt.ArrowCursor

    assert dialog.message_view.viewport().cursor().shape() == Qt.ArrowCursor


def test_message_view_hides_horizontal_scrollbar(
    dialog,
):
    """
    Verifica que la barra de desplazamiento
    horizontal permanece oculta.
    """

    assert dialog.message_view.horizontalScrollBarPolicy() == Qt.ScrollBarAlwaysOff
