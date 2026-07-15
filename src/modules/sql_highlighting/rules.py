from modules.sql_highlighting.ansi.functions import SQL_FUNCTIONS
from modules.sql_highlighting.ansi.keywords import SQL_KEYWORDS
from modules.sql_highlighting.ansi.literals import (
    SQL_BOOLEAN_VALUES,
    SQL_NULL_VALUES,
)
from modules.sql_highlighting.ansi.symbols import SQL_SYMBOLS
from modules.sql_highlighting.ansi.types import SQL_TYPES

SQL_RULES = {
    "keywords": SQL_KEYWORDS,
    "types": SQL_TYPES,
    "functions": SQL_FUNCTIONS,
    "boolean": SQL_BOOLEAN_VALUES,
    "null": SQL_NULL_VALUES,
    "symbols": SQL_SYMBOLS,
}
