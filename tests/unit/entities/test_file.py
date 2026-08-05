from pathlib import Path
from uuid import UUID

from entities.file import File

# =============================================================================
# TESTS
# =============================================================================


def test_create_empty_file_generates_name():
    """
    Comprueba que crea un archivo vacío con un nombre generado automáticamente.
    """

    file = File()

    assert file.path is None
    assert file.content == ""
    assert file.name.startswith("Script_")
    assert file.name.endswith(".sql")
    assert isinstance(file._id, UUID)


def test_create_file_with_path_uses_filename():
    """
    Comprueba que usa el nombre del archivo asociado a la ruta indicada.
    """

    path = Path("queries/test.sql")

    file = File(path=path)

    assert file.path == path
    assert file.name == "test.sql"
    assert file._saved_path == path
    assert file.has_changes is False


def test_new_file_has_no_changes():
    """
    Comprueba que un archivo recién creado no tiene cambios pendientes.
    """

    file = File(content="SELECT 1;")

    assert file.has_changes is False


def test_content_change_marks_file_as_modified():
    """
    Comprueba que modificar el contenido marca el archivo como cambiado.
    """

    file = File(content="SELECT 1;")

    file.content = "SELECT 2;"

    assert file.has_changes is True


def test_save_changes_resets_change_state():
    """
    Comprueba que guardar los cambios restablece el estado del archivo.
    """

    file = File(content="SELECT 1;")

    file.content = "SELECT 2;"

    assert file.has_changes is True

    file.save_changes()

    assert file.has_changes is False
    assert file._saved_content == "SELECT 2;"


def test_rename_changes_name():
    """
    Comprueba que renombrar un archivo actualiza su nombre y ruta.
    """

    file = File(path=Path("test.sql"))

    file.rename("new_name")

    assert file.name == "new_name.sql"
    assert file.path == Path("new_name.sql")


def test_rename_preserves_sql_extension():
    """
    Comprueba que mantiene la extensión SQL al renombrar un archivo.
    """

    file = File()

    file.rename("query.sql")

    assert file.name == "query.sql"


def test_rename_preserves_txt_extension():
    """
    Comprueba que mantiene la extensión TXT al renombrar un archivo.
    """

    file = File()

    file.rename("notes.txt")

    assert file.name == "notes.txt"


def test_rename_adds_sql_extension_when_missing():
    """
    Comprueba que añade la extensión SQL cuando el nombre no tiene extensión.
    """

    file = File()

    file.rename("script")

    assert file.name == "script.sql"


def test_rename_removes_trailing_dot():
    """
    Comprueba que elimina el punto final antes de asignar la extensión.
    """

    file = File()

    file.rename("script.")

    assert file.name == "script.sql"


def test_rename_strips_spaces():
    """
    Comprueba que elimina espacios al principio y al final del nombre.
    """

    file = File()

    file.rename("  query  ")

    assert file.name == "query.sql"


def test_rename_same_name_does_nothing():
    """
    Comprueba que no modifica el archivo al asignar el mismo nombre.
    """

    path = Path("query.sql")

    file = File(path=path)

    file.rename("query.sql")

    assert file.path == path
    assert file.name == "query.sql"


def test_change_path_updates_path_and_name():
    """
    Comprueba que cambiar la ruta actualiza también el nombre del archivo.
    """

    file = File()

    new_path = Path("folder/new.sql")

    file.change_path(new_path)

    assert file.path == new_path
    assert file.name == "new.sql"


def test_exists_on_disk_without_path():
    """
    Comprueba que indica que el archivo no existe sin una ruta asociada.
    """

    file = File()

    assert file.existsOnDisk is False


def test_exists_on_disk_with_path():
    """
    Comprueba que indica que el archivo existe cuando tiene una ruta asociada.
    """

    file = File(path=Path("does_not_matter.sql"))

    assert file.existsOnDisk is True
