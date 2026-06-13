from dataclasses import dataclass
from typing import Any


@dataclass
class ResultSet:
    rows: list[list[Any]]
    columns: list[str]
    columns_types: list[type]

    table_name: str | None
    primary_key_columns: list[str]

    @property
    def is_editable(self) -> bool:

        return self.table_name is not None and len(self.primary_key_columns) > 0


@dataclass
class QueryResult:
    success: bool
    console_output: str
    result_set: ResultSet | None
