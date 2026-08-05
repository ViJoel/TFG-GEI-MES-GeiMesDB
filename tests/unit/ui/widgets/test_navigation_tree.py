from unittest.mock import (
    MagicMock,
    patch,
)

import pytest
from PySide6.QtCore import (
    QModelIndex,
    QPoint,
    Qt,
)
from PySide6.QtGui import (
    QIcon,
    QStandardItem,
)
from PySide6.QtTest import QSignalSpy
from PySide6.QtWidgets import QWidget

from entities.message_type import MessageType
from entities.navigation_tree_action import NavigationTreeAction
from ui.widgets.workspace.navigation_tree.navigation_tree import (
    NavigationTree,
)
from ui.widgets.workspace.navigation_tree.tree_node_type import (
    TreeNodeType,
)

# =============================================================================
# FIXTURES
# =============================================================================

REAL_REFRESH = NavigationTree.refresh


@pytest.fixture(autouse=True)
def patch_theme(monkeypatch):
    monkeypatch.setattr(
        "ui.widgets.workspace.navigation_tree.navigation_tree.ThemeManager.get_color",
        lambda *_: "#ffffff",
    )


@pytest.fixture(autouse=True)
def patch_qta(monkeypatch):
    monkeypatch.setattr(
        "ui.widgets.workspace.navigation_tree.navigation_tree.qta.icon",
        lambda *_, **__: QIcon(),
    )


@pytest.fixture(autouse=True)
def patch_context_menu(mocker):

    menu = mocker.Mock()
    menu.action_requested = mocker.Mock()
    menu.action_requested.connect = mocker.Mock()
    menu.exec = mocker.Mock()

    mocker.patch(
        "ui.widgets.workspace.navigation_tree.navigation_tree.NavigationTreeContextMenu",
        return_value=menu,
    )

    return menu


@pytest.fixture
def tree(qtbot, monkeypatch):

    monkeypatch.setattr(
        NavigationTree,
        "refresh",
        lambda self: None,
    )

    widget = NavigationTree("connection-id")
    qtbot.addWidget(widget)
    return widget


@pytest.fixture
def tree_refresh(qtbot):
    """
    Instancia para probar refresh().
    """

    with patch.object(
        NavigationTree,
        "_connect_signals",
    ):
        widget = NavigationTree("connection-id")

    qtbot.addWidget(widget)

    return widget


@pytest.fixture
def sample_column():
    return {
        "name": "id",
        "type": "INTEGER",
        "pk": True,
        "fk": False,
        "nullable": False,
    }


@pytest.fixture
def sample_constraint():
    return {
        "name": "pk_users",
        "type": "PRIMARY_KEY",
        "columns": ["id"],
    }


@pytest.fixture
def sample_index():
    return {
        "name": "idx_users_name",
        "columns": ["name"],
    }


@pytest.fixture
def sample_table(sample_column, sample_constraint, sample_index):
    return {
        "columns": [sample_column],
        "constraints": [sample_constraint],
        "indexes": [sample_index],
    }


@pytest.fixture
def sample_view(sample_column, sample_index):
    return {
        "columns": [sample_column],
        "indexes": [sample_index],
        "is_materialized": False,
    }


# =============================================================================
# INIT
# =============================================================================


def test_minimo(qtbot):
    """
    Verifica que el widget se puede construir.
    """

    with patch.object(NavigationTree, "refresh", lambda self: None):
        widget = NavigationTree("x")

    qtbot.addWidget(widget)

    assert widget is not None


def test_initial_state(tree):
    """
    Verifica el estado inicial del widget.
    """

    assert tree.connection_id == "connection-id"

    assert tree.objectName() == "navigation_tree"

    assert tree.model is not None

    assert tree.proxy_model is not None


def test_search_bar_is_created(tree):
    """
    Verifica la creación de la barra de búsqueda.
    """

    assert tree.search_bar.objectName() == "navigation_tree_search_bar"

    assert tree.search_bar.isClearButtonEnabled()

    assert tree.search_bar.placeholderText() == tree.tr("🔍 Filter schema...")


def test_refresh_button_is_created(tree):
    """
    Verifica la creación del botón de refresco.
    """

    assert tree.refresh_button.objectName() == ("navigation_tree_refresh_button")

    assert tree.refresh_button.toolTip() == tree.tr("Refresh tree.")


def test_tree_view_is_created(tree):
    """
    Verifica la creación del árbol visual.
    """

    assert tree.tree_view.model() is tree.proxy_model

    assert tree.tree_view.isAnimated()

    assert tree.tree_view.header().isHidden()

    assert tree.tree_view.contextMenuPolicy() == Qt.CustomContextMenu


def test_tree_view_is_not_editable(tree):
    """
    Verifica que el árbol no permite edición.
    """

    assert tree.tree_view.editTriggers() == tree.tree_view.EditTrigger.NoEditTriggers


# =============================================================================
# MODELS
# =============================================================================


def test_setup_models_connects_source_model(tree):
    """
    Verifica que el proxy utiliza el modelo principal.
    """

    assert tree.proxy_model.sourceModel() is tree.model


def test_proxy_model_configuration(tree):
    """
    Verifica la configuración del proxy de filtrado.
    """

    assert tree.proxy_model.isRecursiveFilteringEnabled()

    assert tree.proxy_model.filterCaseSensitivity() == Qt.CaseInsensitive


# =============================================================================
# NODE CREATION
# =============================================================================


def test_create_node(tree):
    """
    Verifica la creación de un nodo genérico.
    """

    item = tree._create_node(
        text="Users",
        node_type=TreeNodeType.TABLE,
    )

    assert isinstance(item, QStandardItem)

    assert item.text() == "Users"

    data = item.data(Qt.UserRole)

    assert data["type"] == TreeNodeType.TABLE

    assert data["data"] is None


def test_create_tables_root_node(tree):
    """
    Verifica la creación del nodo raíz de tablas.
    """

    item = tree._create_tables_root_node()

    assert item.text() == tree.tr("Tables")

    assert item.data(Qt.UserRole)["type"] == TreeNodeType.TABLES_FOLDER


def test_create_views_root_node(tree):
    """
    Verifica la creación del nodo raíz de vistas.
    """

    item = tree._create_views_root_node()

    assert item.text() == tree.tr("Views")

    assert item.data(Qt.UserRole)["type"] == TreeNodeType.VIEWS_FOLDER


def test_create_column_node(tree, sample_column):
    """
    Verifica la creación de un nodo de columna.
    """

    item = tree._create_column_node(
        sample_column,
        "users",
    )

    assert item.text() == "id : INTEGER"

    assert sample_column["table"] == "users"


def test_create_index_node(tree, sample_index):
    """
    Verifica la creación de un nodo de índice.
    """

    item = tree._create_index_node(sample_index)

    assert item.text() == "idx_users_name (name)"


def test_create_constraint_node_primary_key(
    tree,
):
    """
    Verifica la creación de un nodo de clave primaria.
    """

    constraint = {
        "name": "pk_users",
        "type": "PRIMARY_KEY",
        "columns": ["id"],
    }

    item = tree._create_constraint_node(
        constraint,
        "users",
    )

    assert item.text() == "pk_users (id)"

    assert constraint["table"] == "users"


def test_create_constraint_node_foreign_key(
    tree,
):
    """
    Verifica la creación de un nodo de clave foránea.
    """

    constraint = {
        "name": "fk_role",
        "type": "FOREIGN_KEY",
        "columns": ["role_id"],
        "referred_table": "roles",
        "referred_columns": ["id"],
    }

    item = tree._create_constraint_node(
        constraint,
        "users",
    )

    assert item.text() == "fk_role (role_id) → roles(id)"


def test_create_constraint_node_unique(
    tree,
):
    """
    Verifica la creación de un nodo de restricción UNIQUE.
    """

    constraint = {
        "name": "uq_email",
        "type": "UNIQUE",
        "columns": ["email"],
    }

    item = tree._create_constraint_node(
        constraint,
        "users",
    )

    assert item.text() == "uq_email (email)"


def test_create_constraint_node_check(
    tree,
):
    """
    Verifica la creación de un nodo de restricción CHECK.
    """

    constraint = {
        "name": "ck_age",
        "type": "CHECK",
        "sqltext": "age > 0",
    }

    item = tree._create_constraint_node(
        constraint,
        "users",
    )

    assert item.text() == "ck_age (age > 0)"


def test_create_constraint_node_without_name(
    tree,
):
    """
    Verifica que se utiliza el tipo cuando la
    restricción no tiene nombre.
    """

    constraint = {
        "name": "",
        "type": "CHECK",
        "sqltext": "x > 0",
    }

    item = tree._create_constraint_node(
        constraint,
        "users",
    )

    assert item.text() == "CHECK (x > 0)"


def test_create_columns_folder(
    tree,
):
    """
    Verifica la creación de la carpeta de columnas.
    """

    folder = tree._create_columns_folder(
        columns=[
            {
                "name": "id",
                "type": "INTEGER",
                "pk": True,
                "fk": False,
                "nullable": False,
            },
            {
                "name": "name",
                "type": "TEXT",
                "pk": False,
                "fk": False,
                "nullable": True,
            },
        ],
        table_name="users",
    )

    assert folder.text() == tree.tr("Columns")

    assert folder.rowCount() == 2


def test_create_constraints_folder(
    tree,
):
    """
    Verifica la creación de la carpeta de restricciones.
    """

    folder = tree._create_constraints_folder(
        constraints=[
            {
                "name": "pk_users",
                "type": "PRIMARY_KEY",
                "columns": ["id"],
            }
        ],
        table_name="users",
    )

    assert folder.text() == tree.tr("Constraints")

    assert folder.rowCount() == 1


def test_create_indexes_folder(
    tree,
):
    """
    Verifica la creación de la carpeta de índices.
    """

    folder = tree._create_indexes_folder(
        [
            {
                "name": "idx_name",
                "columns": ["name"],
            }
        ]
    )

    assert folder.text() == tree.tr("Indexes")

    assert folder.rowCount() == 1


def test_create_table_node(
    tree,
    sample_table,
):
    """
    Verifica la creación de un nodo de tabla.
    """

    item = tree._create_table_node(
        "users",
        sample_table,
    )

    assert item.text() == "users"

    assert item.rowCount() == 3


def test_create_table_node_without_children(
    tree,
):
    """
    Verifica la creación de una tabla sin hijos.
    """

    item = tree._create_table_node(
        "users",
        {
            "columns": [],
            "constraints": [],
            "indexes": [],
        },
    )

    assert item.rowCount() == 0


def test_create_view_node(
    tree,
    sample_view,
):
    """
    Verifica la creación de un nodo de vista.
    """

    item = tree._create_view_node(
        "active_users",
        sample_view,
    )

    assert item.text() == "active_users"

    assert item.rowCount() == 2


def test_create_view_node_without_children(
    tree,
):
    """
    Verifica la creación de una vista sin hijos.
    """

    item = tree._create_view_node(
        "v",
        {
            "columns": [],
            "indexes": [],
            "is_materialized": False,
        },
    )

    assert item.rowCount() == 0


# =============================================================================
# ICONS
# =============================================================================


def test_get_icon_returns_icon(
    tree,
):
    """
    Verifica que siempre se devuelve un QIcon.
    """

    icon = tree._get_icon(
        TreeNodeType.TABLES_FOLDER,
    )

    assert isinstance(icon, QIcon)


@pytest.mark.parametrize(
    "node_type,data",
    [
        (TreeNodeType.TABLES_FOLDER, None),
        (TreeNodeType.TABLE, {}),
        (TreeNodeType.COLUMNS_FOLDER, None),
        (
            TreeNodeType.COLUMN,
            {
                "pk": True,
                "fk": False,
                "nullable": False,
            },
        ),
        (
            TreeNodeType.COLUMN,
            {
                "pk": False,
                "fk": True,
                "nullable": False,
            },
        ),
        (
            TreeNodeType.COLUMN,
            {
                "pk": False,
                "fk": False,
                "unique": True,
                "nullable": False,
            },
        ),
        (
            TreeNodeType.COLUMN,
            {
                "pk": False,
                "fk": False,
                "nullable": False,
            },
        ),
        (
            TreeNodeType.COLUMN,
            {
                "pk": False,
                "fk": False,
                "nullable": True,
            },
        ),
        (
            TreeNodeType.CONSTRAINT,
            {
                "type": "PRIMARY_KEY",
            },
        ),
        (
            TreeNodeType.CONSTRAINT,
            {
                "type": "FOREIGN_KEY",
            },
        ),
        (
            TreeNodeType.CONSTRAINT,
            {
                "type": "UNIQUE",
            },
        ),
        (
            TreeNodeType.CONSTRAINT,
            {
                "type": "CHECK",
            },
        ),
        (
            TreeNodeType.CONSTRAINT,
            {
                "type": "OTHER",
            },
        ),
        (TreeNodeType.INDEXES_FOLDER, None),
        (TreeNodeType.INDEX, {}),
        (TreeNodeType.VIEWS_FOLDER, None),
        (
            TreeNodeType.VIEW,
            {
                "is_materialized": True,
            },
        ),
        (
            TreeNodeType.VIEW,
            {
                "is_materialized": False,
            },
        ),
        (TreeNodeType.FOLDER, None),
    ],
)
def test_get_icon_all_branches(
    tree,
    node_type,
    data,
):
    """
    Verifica que todas las ramas de selección
    de iconos devuelven un QIcon válido.
    """

    icon = tree._get_icon(
        node_type=node_type,
        data=data,
    )

    assert isinstance(icon, QIcon)


# =============================================================================
# UI HELPERS
# =============================================================================


def test_get_icon_color_default(tree):
    """
    Verifica que se obtiene el color por defecto.
    """

    with patch(
        "ui.widgets.workspace.navigation_tree.navigation_tree.ThemeManager.get_color",
        return_value="#ffffff",
    ) as get_color:
        color = tree._get_icon_color()

    assert color == "#ffffff"

    get_color.assert_called_once_with(
        "navigation_tree_icon_color",
    )


def test_get_icon_color_specific(tree):
    """
    Verifica que se obtiene un color específico.
    """

    with patch(
        "ui.widgets.workspace.navigation_tree.navigation_tree.ThemeManager.get_color",
        return_value="#ff0000",
    ) as get_color:
        color = tree._get_icon_color("table")

    assert color == "#ff0000"

    get_color.assert_called_once_with(
        "navigation_tree_table_icon_color",
    )


# =============================================================================
# SIGNALS
# =============================================================================


def test_connect_signals(tree):
    """
    Verifica que el widget inicializa correctamente
    las conexiones de señales.
    """

    assert tree.search_bar is not None
    assert tree.refresh_button is not None
    assert tree.tree_view is not None


# =============================================================================
# EVENT HANDLERS
# =============================================================================


def test_on_filter_changed_expands_tree(tree):
    """
    Verifica que el árbol se expande cuando existe
    un filtro.
    """

    tree.tree_view.expandAll = MagicMock()

    tree._on_filter_changed("users")

    assert tree.proxy_model.filterRegularExpression().pattern() == "users"

    tree.tree_view.expandAll.assert_called_once()


def test_on_filter_changed_empty_filter(tree):
    """
    Verifica que no se expande el árbol cuando el
    filtro queda vacío.
    """

    tree.tree_view.expandAll = MagicMock()

    tree._on_filter_changed("")

    tree.tree_view.expandAll.assert_not_called()


def test_on_item_collapsed_without_selection(tree):
    """
    Verifica que no ocurre nada si no existe una
    selección válida.
    """

    tree.tree_view.currentIndex = MagicMock(
        return_value=QModelIndex(),
    )

    tree._collapse_children = MagicMock()

    index = QModelIndex()

    tree._on_item_collapsed(index)

    tree._collapse_children.assert_called_once_with(index)


def test_on_item_collapsed_clears_selection(tree):
    """
    Verifica que la selección se elimina cuando el
    elemento seleccionado pertenece al nodo
    colapsado.
    """

    current = MagicMock()

    current.isValid.return_value = True

    tree.tree_view.currentIndex = MagicMock(
        return_value=current,
    )

    tree._is_descendant = MagicMock(
        return_value=True,
    )

    tree.tree_view.clearSelection = MagicMock()

    tree.tree_view.setCurrentIndex = MagicMock()

    tree._collapse_children = MagicMock()

    index = MagicMock()

    tree._on_item_collapsed(index)

    tree.tree_view.clearSelection.assert_called_once()

    tree.tree_view.setCurrentIndex.assert_called_once()

    tree._collapse_children.assert_called_once_with(index)


def test_show_context_menu_invalid_index(tree):
    """
    Verifica que no se crea el menú cuando el clic
    no corresponde a ningún nodo.
    """

    invalid = MagicMock()

    invalid.isValid.return_value = False

    tree.tree_view.indexAt = MagicMock(
        return_value=invalid,
    )

    with patch(
        "ui.widgets.workspace.navigation_tree.navigation_tree.NavigationTreeContextMenu"
    ) as menu:
        tree._show_context_menu(QPoint())

    menu.assert_not_called()


def test_show_context_menu(tree):
    """
    Verifica la creación del menú contextual.
    """

    proxy_index = MagicMock()

    proxy_index.isValid.return_value = True

    source_index = MagicMock()

    item = MagicMock()

    tree.tree_view.indexAt = MagicMock(
        return_value=proxy_index,
    )

    tree.proxy_model.mapToSource = MagicMock(
        return_value=source_index,
    )

    tree.model.itemFromIndex = MagicMock(
        return_value=item,
    )

    tree.tree_view.viewport().mapToGlobal = MagicMock(
        return_value=QPoint(10, 10),
    )

    with patch(
        "ui.widgets.workspace.navigation_tree.navigation_tree.NavigationTreeContextMenu"
    ) as menu_cls:

        menu = menu_cls.return_value

        tree._show_context_menu(QPoint())

        menu_cls.assert_called_once_with(
            parent=tree,
            item=item,
            connection_id="connection-id",
        )

        menu.action_requested.connect.assert_called_once()

        menu.exec.assert_called_once()


# =============================================================================
# EVENT HELPERS
# =============================================================================


def test_is_descendant_same_index(tree):
    """
    Verifica que un índice es descendiente de sí
    mismo.
    """

    index = MagicMock()

    index.isValid.side_effect = [True]

    assert tree._is_descendant(index, index)


def test_is_descendant_false(tree):
    """
    Verifica que devuelve False cuando los índices
    no pertenecen a la misma rama.
    """

    root1 = QStandardItem("root1")
    child1 = QStandardItem("child1")

    root2 = QStandardItem("root2")

    root1.appendRow(child1)

    tree.model.appendRow(root1)
    tree.model.appendRow(root2)

    assert not tree._is_descendant(
        child1.index(),
        root2.index(),
    )


from unittest.mock import MagicMock

from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QStandardItem


def test_collapse_children(tree):
    """
    Verifica el colapso recursivo de los nodos.
    """

    model = MagicMock()

    root = MagicMock()
    child = MagicMock()

    model.rowCount.side_effect = [1, 0]
    model.index.return_value = child

    tree.tree_view.model = MagicMock(return_value=model)
    tree.tree_view.collapse = MagicMock()

    tree._collapse_children(root)

    tree.tree_view.collapse.assert_called_once_with(child)


# =============================================================================
# PRIVATE API
# =============================================================================


def test_load_data(tree):
    """
    Verifica que la carga de datos se delega al
    gestor de tareas.
    """

    task_manager = MagicMock()

    with patch(
        "ui.widgets.workspace.navigation_tree.navigation_tree.AppContext.get_task_manager",
        return_value=task_manager,
    ):
        tree._load_data()

    task_manager.run.assert_called_once()

    _, connection_id = task_manager.run.call_args.args[:2]

    assert connection_id == "connection-id"

    assert task_manager.run.call_args.kwargs["on_success"] == tree._load_data_success
    assert task_manager.run.call_args.kwargs["on_error"] == tree._load_data_error


def test_load_data_success_with_tables_and_views(tree):
    """
    Verifica la carga correcta del árbol cuando
    existen tablas y vistas.
    """

    data = {
        "tables": {
            "users": {
                "columns": [],
                "constraints": [],
                "indexes": [],
            }
        },
        "views": {
            "active_users": {
                "columns": [],
                "indexes": [],
                "is_materialized": False,
            }
        },
    }

    tree.tree_view.expand = MagicMock()

    with patch(
        "ui.widgets.workspace.navigation_tree.navigation_tree.notify",
    ) as notify:
        tree._load_data_success(data)

    assert tree.model.rowCount() == 2

    assert tree.tree_view.expand.call_count == 2

    notify.assert_called_once()


def test_load_data_success_without_tables_or_views(tree):
    """
    Verifica que no se crean nodos cuando no
    existen tablas ni vistas.
    """

    data = {
        "tables": {},
        "views": {},
    }

    with patch(
        "ui.widgets.workspace.navigation_tree.navigation_tree.notify",
    ) as notify:
        tree._load_data_success(data)

    assert tree.model.rowCount() == 0

    notify.assert_called_once()


def test_load_data_error(tree):
    """
    Verifica el tratamiento de errores durante la
    carga del árbol.
    """

    error = MagicMock()

    error.traceback = "traceback"

    with (
        patch(
            "ui.widgets.workspace.navigation_tree.navigation_tree.notify",
        ) as notify,
        patch(
            "ui.widgets.workspace.navigation_tree.navigation_tree.logger",
        ) as logger,
    ):
        tree._load_data_error(error)

    logger.error.assert_called_once()

    notify.assert_called_once()


def test_load_data_success_emits_tree_reloaded_signal(qtbot):
    with (
        patch("ui.widgets.workspace.navigation_tree.navigation_tree.notify"),
        patch(
            "ui.widgets.workspace.navigation_tree.navigation_tree.AppContext.get_task_manager"
        ),
    ):
        tree = NavigationTree(connection_id="connection")
        qtbot.addWidget(tree)

        spy = QSignalSpy(tree.tree_reloaded)

        tree._load_data_success(
            {
                "tables": {},
                "views": {},
            }
        )

    assert spy.count() == 1


def test_load_data_success_clears_previous_model(tree):
    """
    Verifica que el modelo se limpia antes de cargar datos nuevos.
    """

    tree.model.appendRow(QStandardItem("old"))

    with patch(
        "ui.widgets.workspace.navigation_tree.navigation_tree.notify",
    ):
        tree._load_data_success(
            {
                "tables": {},
                "views": {},
            }
        )

    assert tree.model.rowCount() == 0


# =============================================================================
# PUBLIC API
# =============================================================================


def test_refresh(tree, monkeypatch):
    monkeypatch.setattr(
        NavigationTree,
        "refresh",
        REAL_REFRESH,
    )

    tree._load_data = MagicMock()

    with patch(
        "ui.widgets.workspace.navigation_tree.navigation_tree.notify",
    ) as notify:
        tree.refresh()

    notify.assert_called_once()
    tree._load_data.assert_called_once()


def test_refresh_notifies_loading(tree, monkeypatch):
    """
    Verifica que refresh notifica el inicio de la carga.
    """

    monkeypatch.setattr(
        NavigationTree,
        "refresh",
        REAL_REFRESH,
    )

    tree._load_data = MagicMock()

    with patch(
        "ui.widgets.workspace.navigation_tree.navigation_tree.notify",
    ) as notify:

        tree.refresh()

    notify.assert_called_once_with(
        message_type=MessageType.WARNING,
        message=tree.tr("Loading tree..."),
    )


# =============================================================================
# THEME
# =============================================================================


def test_on_theme_changed_updates_icons(tree):
    """
    Verifica que un cambio de tema actualiza todos
    los iconos dependientes del tema.
    """

    tree._update_refresh_button_icon = MagicMock()
    tree._update_tree_icons = MagicMock()

    tree._on_theme_changed("dark")

    tree._update_refresh_button_icon.assert_called_once()
    tree._update_tree_icons.assert_called_once()


def test_update_refresh_button_icon(tree):
    """
    Verifica que se actualiza el icono del botón
    de refresco.
    """

    tree.refresh_button.setIcon = MagicMock()

    with patch(
        "ui.widgets.workspace.navigation_tree.navigation_tree.qta.icon",
        return_value=QIcon(),
    ) as icon:
        tree._update_refresh_button_icon()

    icon.assert_called_once()

    tree.refresh_button.setIcon.assert_called_once()


def test_update_tree_icons(tree):
    """
    Verifica que se actualizan los iconos de todos
    los nodos raíz.
    """

    item1 = QStandardItem("item1")
    item2 = QStandardItem("item2")

    tree.model.appendRow(item1)
    tree.model.appendRow(item2)

    tree._update_item_icons = MagicMock()

    tree._update_tree_icons()

    tree._update_item_icons.assert_any_call(item1)
    tree._update_item_icons.assert_any_call(item2)
    assert tree._update_item_icons.call_count == 2


def test_update_item_icons(tree):
    """
    Verifica que se actualiza recursivamente el
    icono de un nodo y sus hijos.
    """

    parent = QStandardItem("parent")
    child = QStandardItem("child")

    parent.setData(
        {
            "type": TreeNodeType.TABLE,
            "data": {},
        },
        Qt.UserRole,
    )

    child.setData(
        {
            "type": TreeNodeType.TABLE,
            "data": {},
        },
        Qt.UserRole,
    )

    parent.appendRow(child)

    parent.setIcon = MagicMock()
    child.setIcon = MagicMock()

    tree._get_icon = MagicMock(return_value=QIcon())

    tree._update_item_icons(parent)

    assert tree._get_icon.call_count == 2

    parent.setIcon.assert_called_once()
    child.setIcon.assert_called_once()


# =============================================================================
# TRANSLATIONS
# =============================================================================


def test_retranslate_ui(tree):
    """
    Verifica que se actualizan los textos traducibles.
    """

    tree._retranslate_tree = MagicMock()

    tree._retranslate_ui()

    assert tree.refresh_button.toolTip() == tree.tr("Refresh tree.")
    assert tree.search_bar.placeholderText() == tree.tr("🔍 Filter schema...")

    tree._retranslate_tree.assert_called_once()


def test_retranslate_tree(tree):
    """
    Verifica que se actualizan todos los nodos raíz
    del árbol.
    """

    item1 = QStandardItem("Tables")
    item2 = QStandardItem("Views")

    tree.model.appendRow(item1)
    tree.model.appendRow(item2)

    tree._retranslate_item = MagicMock()

    tree._retranslate_tree()

    tree._retranslate_item.assert_any_call(item1)
    tree._retranslate_item.assert_any_call(item2)

    assert tree._retranslate_item.call_count == 2


def test_retranslate_item(tree):
    """
    Verifica que se actualizan recursivamente los
    textos traducibles de un nodo y sus hijos.
    """

    parent = QStandardItem("Tables")
    child = QStandardItem("Columns")

    parent.setData(
        {
            "type": TreeNodeType.TABLES_FOLDER,
            "data": None,
        },
        Qt.UserRole,
    )

    child.setData(
        {
            "type": TreeNodeType.COLUMNS_FOLDER,
            "data": None,
        },
        Qt.UserRole,
    )

    parent.appendRow(child)

    tree._retranslate_item(parent)

    assert parent.text() == tree.tr("Tables")
    assert child.text() == tree.tr("Columns")


def test_retranslate_tree_updates_folder_nodes(tree):
    """
    Verifica que se actualizan los textos de los nodos
    traducibles del árbol.
    """

    tables = tree._create_tables_root_node()
    columns = tree._create_columns_folder([], "users")
    constraints = tree._create_constraints_folder([], "users")
    indexes = tree._create_indexes_folder([])
    views = tree._create_views_root_node()

    tables.appendRow(columns)
    tables.appendRow(constraints)
    tables.appendRow(indexes)

    tree.model.appendRow(tables)
    tree.model.appendRow(views)

    tree._retranslate_tree()

    assert tables.text() == tree.tr("Tables")
    assert columns.text() == tree.tr("Columns")
    assert constraints.text() == tree.tr("Constraints")
    assert indexes.text() == tree.tr("Indexes")
    assert views.text() == tree.tr("Views")


def test_retranslate_tree_does_not_update_non_folder_nodes(tree):
    """
    Verifica que únicamente se actualizan los textos
    de los nodos carpeta.
    """

    tables = tree._create_tables_root_node()
    columns = tree._create_columns_folder([], "users")
    table = tree._create_table_node(
        "users",
        {
            "columns": [],
            "constraints": [],
            "indexes": [],
        },
    )

    tables.appendRow(columns)
    tables.appendRow(table)

    tree.model.appendRow(tables)

    tables.setText = MagicMock()
    columns.setText = MagicMock()
    table.setText = MagicMock()

    tree._retranslate_tree()

    tables.setText.assert_called_once_with(tree.tr("Tables"))
    columns.setText.assert_called_once_with(tree.tr("Columns"))
    table.setText.assert_not_called()
