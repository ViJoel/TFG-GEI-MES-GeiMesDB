from pathlib import Path

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
)
from pytestqt.qtbot import QtBot

from entities.connection import Connection
from ui.app.main_window import MainWindow
from ui.widgets.dialogs.confirmation_dialog import ConfirmationDialog
from ui.widgets.workspace.sql_editor.sql_editor import SqlEditor
from ui.widgets.workspace.sql_editor.sql_editor_area import SqlEditorArea
from ui.widgets.workspace.workspace import Workspace

# =============================================================================
# FUNCTIONS
# =============================================================================


def get_connection_item(
    window: MainWindow,
    connection_name: str,
):
    """
    Obtiene el item y la conexión asociada a partir del nombre.

    Args:
        window (MainWindow):
            Ventana principal que contiene la lista de conexiones.

        connection_name (str):
            Nombre de la conexión que se desea localizar.

    Returns:
        tuple:
            Item de la lista y objeto Connection asociado.

    Raises:
        AssertionError:
            Si no existe ninguna conexión con el nombre indicado.
    """

    list_widget = window.sidebar.connections_list.list_widget

    for index in range(list_widget.count()):

        item = list_widget.item(index)

        connection = item.data(
            Qt.ItemDataRole.UserRole,
        )

        if connection.name == connection_name:
            return item, connection

    raise AssertionError(
        f"Connection '{connection_name}' not found in the connections list."
    )


def connect_to_db(
    qtbot: QtBot,
    window: MainWindow,
    connection_name: str,
):
    """
    Selecciona una conexión y solicita su apertura.

    Args:
        qtbot (QtBot):
            Objeto de pytest-qt utilizado para interactuar con la
            interfaz de usuario y gestionar operaciones asíncronas.

        window (MainWindow):
            Ventana principal que contiene la lista de conexiones
            y los controles para conectarlas.

        connection_name (str):
            Nombre de la conexión que se desea abrir.

    Raises:
        AssertionError:
            Si los botones no se encuentran en el estado esperado,
            si existe una selección previa, si no se encuentra la
            conexión indicada o si la selección de la conexión no
            se realiza correctamente.

    Note:
        Este método únicamente inicia la operación de conexión.
        La finalización de la operación se gestiona de forma
        asíncrona y debe esperarse en el test mediante `qtbot.waitUntil()`.
    """

    # Localizar botón de conectar.
    connect_button = window.sidebar.connections_list.connect_button
    assert not connect_button.isEnabled()

    # Localizar botón de desconectar.
    disconnect_button = window.sidebar.connections_list.disconnect_button
    assert not disconnect_button.isEnabled()

    # Localizar lista de conexiones.
    list_widget = window.sidebar.connections_list.list_widget
    assert list_widget.currentItem() is None

    # Obtener item de la lista y objeto Connection metido dentro del item.
    item, connection = get_connection_item(
        window,
        connection_name,
    )
    assert connection.name == connection_name

    # Seleccionar conexión en la lista.
    list_widget.setCurrentItem(item)
    assert list_widget.currentItem() is item
    assert connect_button.isEnabled()

    # Clikamos el botón de conectar.
    connect_button.click()

    # Obtener objeto Connection de la lista de conexiones.
    _, connection = get_connection_item(
        window,
        connection_name,
    )

    # Esperar a que el ID de la conexión aparezca en el diccionario de workspaces.
    qtbot.waitUntil(
        lambda: connection.id in window.workspaces,
        timeout=5000,
    )


def disconnect_from_db(
    qtbot: QtBot,
    window: MainWindow,
    connection_name: str,
):
    """
    Selecciona una conexión activa y solicita su cierre.

    Args:
        qtbot (QtBot):
            Objeto de pytest-qt utilizado para interactuar con la
            interfaz de usuario y gestionar operaciones asíncronas.

        window (MainWindow):
            Ventana principal que contiene la lista de conexiones
            y los controles para desconectarlas.

        connection_name (str):
            Nombre de la conexión que se desea cerrar.

    Raises:
        AssertionError:
            Si la conexión no se encuentra, si el item de la conexión
            no está seleccionado o si los botones no se encuentran
            en el estado esperado.

    Note:
        Este método únicamente inicia la operación de desconexión.
        La finalización de la operación se gestiona de forma asíncrona
        y debe esperarse en el test mediante `qtbot.waitUntil()`.
    """

    # Localizar lista de conexiones.
    list_widget = window.sidebar.connections_list.list_widget

    # Obtener item de la lista y objeto Connection metido dentro del item.
    item, connection = get_connection_item(
        window,
        connection_name,
    )
    assert connection.name == connection_name

    # Comprobamos el item seleccionado.
    assert list_widget.currentItem() is item

    # Localizar botón de conectar.
    connect_button = window.sidebar.connections_list.connect_button
    assert not connect_button.isEnabled()

    # Localizar botón de desconectar.
    disconnect_button = window.sidebar.connections_list.disconnect_button
    assert disconnect_button.isEnabled()

    # Clikamos el botón de desconectar.
    disconnect_button.click()

    # Esperar a que el ID de la conexión desaparezca del diccionario de workspaces.
    qtbot.waitUntil(
        lambda: connection.id not in window.workspaces,
        timeout=5000,
    )


def auto_accept_confirmation_dialog(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Configura el ConfirmationDialog para que se acepte
    automáticamente durante la prueba.

    Esto evita la interacción manual con diálogos modales
    que aparecen durante las pruebas.

    Args:
        monkeypatch (pytest.MonkeyPatch):
            Utilidad de pytest para sustituir temporalmente
            el comportamiento del diálogo.
    """

    def accept_exec(
        dialog: ConfirmationDialog,
    ) -> int:
        dialog.accept()

        return QDialog.DialogCode.Accepted

    def accept_open(
        dialog: ConfirmationDialog,
    ) -> None:
        dialog.confirmed.emit()

    monkeypatch.setattr(
        ConfirmationDialog,
        "exec",
        accept_exec,
    )

    monkeypatch.setattr(
        ConfirmationDialog,
        "open",
        accept_open,
    )


def get_workspace(
    main_window: MainWindow,
    connection: Connection,
) -> Workspace:
    """
    Obtiene el workspace asociado a una conexión.

    Args:
        main_window (MainWindow):
            Ventana principal que contiene los workspaces
            de las conexiones activas.

        connection (Connection):
            Conexión cuyo workspace se desea obtener.

    Returns:
        Workspace:
            Workspace asociado al identificador de la conexión.
    """

    return main_window.workspaces[connection.id]


def get_sql_editor_area(
    main_window: MainWindow,
    connection: Connection,
) -> SqlEditorArea:
    """
    Obtiene el área del editor SQL de una conexión.

    Antes de devolver el área, elimina el editor inicial
    creado automáticamente. Si el editor inicial contiene
    cambios, el diálogo de confirmación se acepta automáticamente.

    Args:
        main_window (MainWindow):
            Ventana principal que contiene los workspaces
            de las conexiones activas.

        connection (Connection):
            Conexión cuyo área de editor SQL se desea obtener.

    Returns:
        SqlEditorArea:
            Área del editor SQL asociada a la conexión,
            sin editores abiertos inicialmente.

    Raises:
        AssertionError:
            Si el área del editor no contiene exactamente un
            editor al obtenerla o si el editor inicial no se
            elimina correctamente.
    """

    workspace = get_workspace(
        main_window=main_window,
        connection=connection,
    )

    sea = workspace.sql_editor_area

    assert sea.editors.count() == 1

    current_editor = sea._get_current_editor()

    assert current_editor is not None

    monkeypatch = pytest.MonkeyPatch()

    try:
        auto_accept_confirmation_dialog(
            monkeypatch=monkeypatch,
        )

        sea._remove_file_and_editor(
            current_editor.file,
        )

    finally:
        monkeypatch.undo()

    assert sea._get_current_editor() is None
    assert sea.editors.count() == 0

    return sea


def create_new_editor(
    sql_editor_area: SqlEditorArea,
) -> SqlEditor:
    """
    Crea un nuevo editor SQL y lo devuelve.

    Args:
        sql_editor_area (SqlEditorArea):
            Área del editor SQL donde se creará
            el nuevo editor.

    Returns:
        SqlEditor:
            Editor SQL recién creado.

    Raises:
        AssertionError:
            Si no se consigue crear el editor.
    """

    sql_editor_area.toolbar.new_button.click()

    editor = sql_editor_area._get_current_editor()

    assert editor is not None

    return editor


def open_file(
    qtbot: QtBot,
    sql_editor_area: SqlEditorArea,
    file_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> SqlEditor | None:
    """
    Abre un archivo en el área del editor SQL.

    Sustituye temporalmente el diálogo de selección de archivos
    para utilizar la ruta proporcionada y espera hasta que exista
    un editor activo.

    Args:
        qtbot (QtBot):
            Objeto de pytest-qt utilizado para interactuar con la
            interfaz de usuario y esperar operaciones asíncronas.

        sql_editor_area (SqlEditorArea):
            Área del editor SQL donde se abrirá el archivo.

        file_path (Path):
            Ruta del archivo que se desea abrir.

        monkeypatch (pytest.MonkeyPatch):
            Utilidad de pytest para sustituir temporalmente
            el diálogo de selección de archivos.

    Returns:
        SqlEditor | None:
            Editor SQL activo después de intentar abrir el archivo.
            Devuelve None si no existe ningún editor activo.
    """

    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *args, **kwargs: (
            str(file_path),
            "",
        ),
    )

    sql_editor_area.toolbar.open_button.click()

    qtbot.waitUntil(
        lambda: sql_editor_area._get_current_editor() is not None,
        timeout=5000,
    )

    return sql_editor_area._get_current_editor()
