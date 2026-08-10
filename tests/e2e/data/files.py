FILE_SQL = "test.sql"
FILE_SQL_CONTENT = """
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    );

    INSERT INTO users (id, name)
    VALUES (1, 'Alice');
    """

FILE_TXT = "test.txt"
FILE_TXT_CONTENT = "Este es un archivo de texto de prueba.\n"
