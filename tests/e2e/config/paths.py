from pathlib import Path

from common.paths import BASE_DIR

TEST_DATABASE_SQL_DIR = Path(BASE_DIR).parent / "tests" / "e2e" / "data"

SCRIPT_POSTGRESQL = TEST_DATABASE_SQL_DIR / "Script_PostgreSQL.sql"

SCRIPT_MYSQL = TEST_DATABASE_SQL_DIR / "Script_MySQL.sql"
