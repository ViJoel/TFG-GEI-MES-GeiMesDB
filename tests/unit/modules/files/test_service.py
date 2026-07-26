from pathlib import Path

from entities.file import File
from modules.files import service

# =============================================================================
# TESTS
# =============================================================================


def test_save_file_delegates_to_model(monkeypatch):
    """
    Comprueba que delega el guardado del archivo en el modelo.
    """

    file = File(
        content="SELECT 1;",
    )

    called = {}

    def fake_save_file(argument):
        called["file"] = argument
        return True

    monkeypatch.setattr(
        service.model,
        "save_file",
        fake_save_file,
    )

    result = service.save_file(file)

    assert result is True
    assert called["file"] is file


def test_save_file_returns_model_result(monkeypatch):
    """
    Comprueba que devuelve el resultado obtenido del modelo.
    """

    file = File()

    monkeypatch.setattr(
        service.model,
        "save_file",
        lambda _: False,
    )

    result = service.save_file(file)

    assert result is False


def test_open_file_delegates_to_model(monkeypatch, tmp_path):
    """
    Comprueba que delega la apertura del archivo en el modelo.
    """

    path = tmp_path / "test.sql"

    expected = File(
        path=path,
        content="SELECT 1;",
    )

    called = {}

    def fake_open_file(argument):
        called["path"] = argument
        return expected

    monkeypatch.setattr(
        service.model,
        "open_file",
        fake_open_file,
    )

    result = service.open_file(path)

    assert result is expected
    assert called["path"] == path


def test_open_file_returns_none_when_model_fails(monkeypatch):
    """
    Comprueba que devuelve None cuando el modelo no abre el archivo.
    """

    path = Path("missing.sql")

    monkeypatch.setattr(
        service.model,
        "open_file",
        lambda _: None,
    )

    result = service.open_file(path)

    assert result is None
