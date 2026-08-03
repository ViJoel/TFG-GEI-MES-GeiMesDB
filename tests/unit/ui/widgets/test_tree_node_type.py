from ui.widgets.workspace.navigation_tree.tree_node_type import TreeNodeType

# =============================================================================
# TESTS
# =============================================================================


def test_values_are_generated_as_expected():
    """
    Verifica que los valores generados por StrEnum
    coinciden con los nombres de los nodos en
    minúsculas.
    """

    assert TreeNodeType.COLUMN == "column"
    assert TreeNodeType.COLUMNS_FOLDER == "columns_folder"

    assert TreeNodeType.CONSTRAINT == "constraint"
    assert TreeNodeType.CONSTRAINTS_FOLDER == "constraints_folder"

    assert TreeNodeType.INDEX == "index"
    assert TreeNodeType.INDEXES_FOLDER == "indexes_folder"

    assert TreeNodeType.TABLE == "table"
    assert TreeNodeType.TABLES_FOLDER == "tables_folder"

    assert TreeNodeType.VIEW == "view"
    assert TreeNodeType.VIEWS_FOLDER == "views_folder"

    assert TreeNodeType.FOLDER == "folder"


def test_members_exist():
    """
    Verifica que el enum expone todos los tipos de
    nodos soportados por el árbol de navegación.
    """

    assert list(TreeNodeType) == [
        TreeNodeType.COLUMN,
        TreeNodeType.COLUMNS_FOLDER,
        TreeNodeType.CONSTRAINT,
        TreeNodeType.CONSTRAINTS_FOLDER,
        TreeNodeType.INDEX,
        TreeNodeType.INDEXES_FOLDER,
        TreeNodeType.TABLE,
        TreeNodeType.TABLES_FOLDER,
        TreeNodeType.VIEW,
        TreeNodeType.VIEWS_FOLDER,
        TreeNodeType.FOLDER,
    ]
