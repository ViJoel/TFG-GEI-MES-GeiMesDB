from enum import StrEnum, auto


class MessageType(StrEnum):
    DEFAULT = auto()
    DISABLED = auto()
    INFO = auto()
    SUCCESS = auto()
    WARNING = auto()
    ERROR = auto()
