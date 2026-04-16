from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import sqlite3


def get_connection() -> sqlite3.Connection: ...
def initialize_schema(connection: sqlite3.Connection) -> None: ...
