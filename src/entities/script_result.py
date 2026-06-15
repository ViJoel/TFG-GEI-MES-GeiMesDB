from dataclasses import dataclass


@dataclass
class ScriptResultItem:
    query: str
    error: str | None = None

    @property
    def success(self) -> bool:
        return self.error is None


@dataclass
class ScriptResult:
    items: list[ScriptResultItem]
