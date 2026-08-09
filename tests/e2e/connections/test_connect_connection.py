from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot

from entities.message_type import MessageType
from ui.app.app_context import AppContext
from ui.app.main_window import MainWindow

# =============================================================================
# VARIABLES
# =============================================================================


# =============================================================================
# FUNCTIONS
# =============================================================================


def _get_connection_item(
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


def _connect_to_db(
    qtbot: QtBot,
    window: MainWindow,
    connection_name: str,
):
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
    item, connection = _get_connection_item(
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


# =============================================================================
# TESTS
# =============================================================================


def test_connect_postgresql_success(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica el resultadode una conexión exitosa.
    """

    connection_name = "1 - E2E PostgreSQL"

    _connect_to_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=connection_name,
    )

    # Obtener objeto Connection de la lista de conexiones.
    _, connection = _get_connection_item(
        main_window,
        connection_name,
    )

    # Esperar a que el ID de la conexión aparezca en el diccionario de workspaces.
    qtbot.waitUntil(
        lambda: connection.id in main_window.workspaces,
        timeout=5000,
    )

    # Validar que además la vista actual sea la de ese workspace.
    workspace = main_window.workspaces[connection.id]
    assert main_window.stack.currentWidget() is workspace


def test_connect_mysql_success(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica el resultadode una conexión exitosa.
    """

    connection_name = "1 - E2E MySQL"

    _connect_to_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=connection_name,
    )

    # Obtener objeto Connection de la lista de conexiones.
    _, connection = _get_connection_item(
        main_window,
        connection_name,
    )

    # Esperar a que el ID de la conexión aparezca en el diccionario de workspaces.
    qtbot.waitUntil(
        lambda: connection.id in main_window.workspaces,
        timeout=5000,
    )

    # Validar que además la vista actual sea la de ese workspace.
    workspace = main_window.workspaces[connection.id]
    assert main_window.stack.currentWidget() is workspace


def test_connect_error(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica que una conexión fallida no crea un
    workspace y muestra una notificación de error.
    """

    # Nombre de la conexión que provocará el error.
    connection_name = "1 - E2E Oracle"

    # Obtener la colección de notificaciones gestionadas
    # por la ventana actual.
    notifications = AppContext.notification_manager.notifications

    # Guardar cuántas notificaciones existían antes
    # de iniciar la operación.
    previous_count = len(notifications)

    # Seleccionar la conexión y solicitar su apertura.
    _connect_to_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=connection_name,
    )

    # Esperar a que finalice la operación asíncrona
    # y aparezca una notificación de error.
    qtbot.waitUntil(
        lambda: any(
            notification.message_type is MessageType.ERROR
            for notification in notifications[previous_count:]
        ),
        timeout=5000,
    )

    # Obtener la notificación de error generada por esta operación.
    error_notification = next(
        notification
        for notification in notifications[previous_count:]
        if notification.message_type is MessageType.ERROR
    )

    # Comprobar que el mensaje corresponde al error
    # de conexión esperado, respetando la traducción actual.
    assert error_notification.message == main_window.tr(
        "Connection failed.",
    )

    # Esperar a que la notificación desaparezca automáticamente.
    # Esto permite que finalice su temporizador antes de destruir
    # la ventana del test.
    qtbot.waitUntil(
        lambda: not notifications,
        timeout=5000,
    )
