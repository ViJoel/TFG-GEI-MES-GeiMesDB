from dataclasses import dataclass
from model.connections.drivers import Driver
from typing import Optional


@dataclass
class Connection:
    id: Optional[int]
    name: str
    driver: Driver
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    path: Optional[str] = None
