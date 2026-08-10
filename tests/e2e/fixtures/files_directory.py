from pathlib import Path

import pytest

from tests.e2e.data.files import (
    FILE_SQL,
    FILE_SQL_CONTENT,
    FILE_TXT,
    FILE_TXT_CONTENT,
)


@pytest.fixture
def temporary_sql_directory(tmp_path: Path) -> Path:
    """
    Crea un directorio temporal con un archivo SQL de PostgreSQL
    para utilizarlo en las pruebas de gestión de archivos.
    """

    sql_path = tmp_path / FILE_SQL

    sql_path.write_text(
        FILE_SQL_CONTENT.strip() + "\n",
        encoding="utf-8",
    )

    txt_path = tmp_path / FILE_TXT

    txt_path.write_text(
        FILE_TXT_CONTENT,
        encoding="utf-8",
    )

    return tmp_path
