from typing import TYPE_CHECKING

from bookmark_manager.domain.models import Tag

if TYPE_CHECKING:
    import sqlite3


class TagRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def get_or_create(self, name_display: str, name_normalized: str) -> Tag:
        cursor = self._connection.execute("SELECT tag_id, name_display, name_normalized FROM tags WHERE name_normalized = ?", (name_normalized,))
        row = cursor.fetchone()
        if row is not None:
            return self._row_to_tag(row)
        cursor = self._connection.execute("INSERT INTO tags (name_display, name_normalized) VALUES (?, ?)", (name_display, name_normalized))
        self._connection.commit()
        tag_id = cursor.lastrowid
        if tag_id is None:
            msg = "Failed to retrieve lastrowid"
            raise RuntimeError(msg)
        return Tag(tag_id, name_display, name_normalized)

    def list_all(self) -> list[Tag]:
        cursor = self._connection.execute("SELECT tag_id, name_display, name_normalized FROM tags")
        return [self._row_to_tag(row) for row in cursor.fetchall()]

    def _row_to_tag(self, row: sqlite3.Row) -> Tag:
        return Tag(row["tag_id"], row["name_display"], row["name_normalized"])
