from pathlib import Path

from entities.file import File
from modules.files.model import (
    _normalize_extension,
    open_file,
    save_file,
)

# =============================================================================
# TESTS
# =============================================================================


def test_normalize_allowed_sql_extension():
    """
    Comprueba que mantiene la extensión SQL permitida.
    """

    path = Path("script.sql")

    result = _normalize_extension(path)

    assert result == path


def test_normalize_allowed_txt_extension():
    """
    Comprueba que mantiene la extensión TXT permitida.
    """

    path = Path("script.txt")

    result = _normalize_extension(path)

    assert result == path


def test_normalize_unknown_extension_changes_to_sql():
    """
    Comprueba que sustituye una extensión no permitida por SQL.
    """

    path = Path("script.py")

    result = _normalize_extension(path)

    assert result == Path("script.sql")


def test_normalize_without_extension_adds_sql():
    """
    Comprueba que añade la extensión SQL cuando no existe extensión.
    """

    path = Path("script")

    result = _normalize_extension(path)

    assert result == Path("script.sql")


def test_open_existing_sql_file(tmp_path):
    """
    Comprueba que abre correctamente un archivo SQL existente.
    """

    path = tmp_path / "query.sql"
    path.write_text(
        "SELECT 1;",
        encoding="utf-8",
    )

    file = open_file(path)

    assert file is not None
    assert file.path == path
    assert file.content == "SELECT 1;"
    assert file.name == "query.sql"


def test_open_existing_txt_file(tmp_path):
    """
    Comprueba que abre correctamente un archivo TXT existente.
    """

    path = tmp_path / "notes.txt"
    path.write_text(
        "hello",
        encoding="utf-8",
    )

    file = open_file(path)

    assert file is not None
    assert file.content == "hello"


def test_open_non_existing_file_returns_none(tmp_path):
    """
    Comprueba que devuelve None al abrir un archivo inexistente.
    """

    path = tmp_path / "missing.sql"

    file = open_file(path)

    assert file is None


def test_open_file_with_invalid_extension_returns_none(tmp_path):
    """
    Comprueba que devuelve None al abrir un archivo con extensión no permitida.
    """

    path = tmp_path / "script.py"
    path.write_text(
        "print('test')",
        encoding="utf-8",
    )

    file = open_file(path)

    assert file is None


def test_save_existing_file(tmp_path):
    """
    Comprueba que guarda correctamente un archivo existente.
    """

    path = tmp_path / "script.sql"

    file = File(
        path=path,
        content="SELECT 1;",
    )

    result = save_file(file)

    assert result is True
    assert path.exists()
    assert path.read_text(encoding="utf-8") == "SELECT 1;"
    assert file.has_changes is False


def test_save_file_without_path_returns_false():
    """
    Comprueba que devuelve False al guardar un archivo sin ruta asociada.
    """

    file = File(
        content="SELECT 1;",
    )

    result = save_file(file)

    assert result is False


def test_save_file_updates_existing_content(tmp_path):
    """
    Comprueba que actualiza el contenido de un archivo existente.
    """

    path = tmp_path / "script.sql"
    path.write_text(
        "OLD",
        encoding="utf-8",
    )

    file = File(
        path=path,
        content="NEW",
    )

    file.content = "UPDATED"

    result = save_file(file)

    assert result is True
    assert path.read_text(encoding="utf-8") == "UPDATED"


def test_save_file_changes_extension_to_sql(tmp_path):
    """
    Comprueba que cambia la extensión a SQL al guardar un archivo.
    """

    path = tmp_path / "script.py"

    file = File(
        content="SELECT 1;",
    )

    file.change_path(path)

    result = save_file(file)

    assert result is True
    assert file.path == tmp_path / "script.sql"
    assert file.path.exists()


def test_save_file_renames_previous_file(tmp_path):
    """
    Comprueba que renombra el archivo anterior al cambiar la ruta.
    """

    old_path = tmp_path / "old.sql"
    new_path = tmp_path / "new.sql"

    old_path.write_text(
        "OLD",
        encoding="utf-8",
    )

    file = File(
        path=new_path,
        content="NEW",
    )

    file._saved_path = old_path

    result = save_file(file)

    assert result is True
    assert not old_path.exists()
    assert new_path.exists()
    assert new_path.read_text(encoding="utf-8") == "NEW"
