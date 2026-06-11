from dataclasses import dataclass
from typing import Any


@dataclass
class ResultSet:
    columns: list[str]
    rows: list[list[Any]]


@dataclass
class QueryResult:
    success: bool
    console_output: str
    result_set: ResultSet | None
