from dataclasses import dataclass


@dataclass
class ScriptResultDataItem:
    query: str
    error: str | None = None

    @property
    def success(self) -> bool:
        return self.error is None


@dataclass
class ScriptResultData:
    items: list[ScriptResultDataItem]
