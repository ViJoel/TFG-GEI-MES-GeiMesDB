from enum import (
    StrEnum,
    auto,
)


class MessageType(StrEnum):
    DEFAULT = auto()
    DISABLED = auto()
    ERROR = auto()
    INFO = auto()
    SUCCESS = auto()
    WARNING = auto()
