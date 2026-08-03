from enum import (
    StrEnum,
    auto,
)


class TreeNodeType(StrEnum):

    COLUMN = auto()
    COLUMNS_FOLDER = auto()

    CONSTRAINT = auto()
    CONSTRAINTS_FOLDER = auto()

    INDEX = auto()
    INDEXES_FOLDER = auto()

    TABLE = auto()
    TABLES_FOLDER = auto()

    VIEW = auto()
    VIEWS_FOLDER = auto()

    FOLDER = auto()
