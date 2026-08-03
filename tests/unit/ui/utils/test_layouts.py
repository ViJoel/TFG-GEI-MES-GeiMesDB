from PySide6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
)

from ui.utils.layouts import (
    hbox,
    vbox,
)

# =============================================================================
# VBOX
# =============================================================================


def test_vbox_returns_qvboxlayout():
    """
    Verifica que vbox crea un QVBoxLayout.
    """

    layout = vbox()

    assert isinstance(
        layout,
        QVBoxLayout,
    )


def test_vbox_sets_contents_margins():
    """
    Verifica configuración de márgenes.
    """

    layout = vbox(
        ml=10,
        mt=20,
        mr=30,
        mb=40,
    )

    margins = layout.contentsMargins()

    assert margins.left() == 10
    assert margins.top() == 20
    assert margins.right() == 30
    assert margins.bottom() == 40


def test_vbox_sets_spacing():
    """
    Verifica configuración del espaciado.
    """

    layout = vbox(
        sp=16,
    )

    assert layout.spacing() == 16


def test_vbox_default_values():
    """
    Verifica valores por defecto.
    """

    layout = vbox()

    margins = layout.contentsMargins()

    assert margins.left() == 0
    assert margins.top() == 0
    assert margins.right() == 0
    assert margins.bottom() == 0

    assert layout.spacing() == 0


# =============================================================================
# HBOX
# =============================================================================


def test_hbox_returns_qhboxlayout():
    """
    Verifica que hbox crea un QHBoxLayout.
    """

    layout = hbox()

    assert isinstance(
        layout,
        QHBoxLayout,
    )


def test_hbox_sets_contents_margins():
    """
    Verifica configuración de márgenes.
    """

    layout = hbox(
        ml=5,
        mt=15,
        mr=25,
        mb=35,
    )

    margins = layout.contentsMargins()

    assert margins.left() == 5
    assert margins.top() == 15
    assert margins.right() == 25
    assert margins.bottom() == 35


def test_hbox_sets_spacing():
    """
    Verifica configuración del espaciado.
    """

    layout = hbox(
        sp=8,
    )

    assert layout.spacing() == 8


def test_hbox_default_values():
    """
    Verifica valores por defecto.
    """

    layout = hbox()

    margins = layout.contentsMargins()

    assert margins.left() == 0
    assert margins.top() == 0
    assert margins.right() == 0
    assert margins.bottom() == 0

    assert layout.spacing() == 0
