from entities.connection import Connection
from entities.driver import Driver

MYSQL_CONNECTION = Connection(
    id="1-e2e-mysql",
    name="E2E MySQL",
    driver=Driver.MYSQL,
    host="localhost",
    port=3306,
    database="tfg-test",
    username="tfg",
    password="Tfg12345!",
)


ORACLE_CONNECTION = Connection(
    id="1-e2e-oracle",
    name="E2E Oracle",
    driver=Driver.ORACLE,
    host="oracle",
    port=1521,
    database="oracle",
    username="oracle",
    password="oracle",
)


POSTGRESQL_CONNECTION = Connection(
    id="1-e2e-postgresql",
    name="E2E PostgreSQL",
    driver=Driver.POSTGRESQL,
    host="localhost",
    port=5432,
    database="tfg-test",
    username="tfg",
    password="tfg",
)


SQLITE_CONNECTION = Connection(
    id="1-e2e-sqlite",
    name="E2E SQLite",
    driver=Driver.SQLITE,
    path=None,
)
