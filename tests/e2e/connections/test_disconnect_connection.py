from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot

from entities.message_type import MessageType
from ui.app.app_context import AppContext
from ui.app.main_window import MainWindow

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


def _disconnect_from_db(
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
    item, connection = _get_connection_item(
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


# =============================================================================
# TESTS
# =============================================================================


def test_disconnect_postgresql_success(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica el resultado de una desconexión exitosa.
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

    # Validar que se haya creado el workspace.
    assert len(main_window.workspaces) == 1

    _disconnect_from_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=connection_name,
    )

    # Esperar a que el ID de la conexión desaparezca del diccionario de workspaces.
    qtbot.waitUntil(
        lambda: connection.id not in main_window.workspaces,
        timeout=5000,
    )

    # Validar que la vista actual sea la de home.
    main_window.home_page
    assert main_window.stack.currentWidget() is main_window.home_page

    # Validar que se haya eliminado el workspace.
    assert len(main_window.workspaces) == 0


def test_disconnect_mysql_success(
    qtbot: QtBot,
    main_window: MainWindow,
):
    """
    Verifica el resultado de una desconexión exitosa.
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

    # Validar que se haya creado el workspace.
    assert len(main_window.workspaces) == 1

    _disconnect_from_db(
        qtbot=qtbot,
        window=main_window,
        connection_name=connection_name,
    )

    # Esperar a que el ID de la conexión desaparezca del diccionario de workspaces.
    qtbot.waitUntil(
        lambda: connection.id not in main_window.workspaces,
        timeout=5000,
    )

    # Validar que la vista actual sea la de home.
    main_window.home_page
    assert main_window.stack.currentWidget() is main_window.home_page

    # Validar que se haya eliminado el workspace.
    assert len(main_window.workspaces) == 0


def test_disconnect_error(
    qtbot: QtBot,
    main_window: MainWindow,
    monkeypatch,
):
    """
    Verifica que una desconexión fallida no elimina el
    workspace y muestra una notificación de error.
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

    # Guardar el workspace para comprobar que permanece tras el error.
    workspace = main_window.workspaces[connection.id]

    # Obtener la colección de notificaciones gestionadas
    # por la ventana actual.
    notifications = AppContext.notification_manager.notifications

    # Guardar cuántas notificaciones existían antes
    # de iniciar la operación.
    previous_count = len(notifications)

    # Forzar un error durante la desconexión.
    def _raise_disconnect_error(
        *args,
        **kwargs,
    ):
        raise RuntimeError("Disconnect failed.")

    monkeypatch.setattr(
        "ui.app.main_window.close_session",
        _raise_disconnect_error,
    )

    _disconnect_from_db(
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
    # de desconexión esperado, respetando la traducción actual.
    assert error_notification.message == main_window.tr(
        "Disconnection failed.",
    )

    # Validar que el workspace no haya sido eliminado.
    assert connection.id in main_window.workspaces

    # Validar que el mismo workspace siga siendo la vista actual.
    assert main_window.workspaces[connection.id] is workspace
    assert main_window.stack.currentWidget() is workspace

    # Esperar a que la notificación desaparezca automáticamente.
    qtbot.waitUntil(
        lambda: not notifications,
        timeout=5000,
    )
