from typing import TYPE_CHECKING

from bookmark_manager.domain.models import Bookmark

if TYPE_CHECKING:
    import sqlite3


class BookmarkRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def add(self, bookmark: Bookmark) -> int:
        cursor = self._connection.execute(
            "INSERT INTO bookmarks (url, display_name, display_name_normalized, initial_weight, times_copied) VALUES (?, ?, ?, ?, ?)",
            (bookmark.url, bookmark.display_name, bookmark.display_name_normalized, bookmark.initial_weight, bookmark.times_copied),
        )
        self._connection.commit()
        row_id = cursor.lastrowid
        if row_id is None:
            msg = "Failed to retrieve lastrowid"
            raise RuntimeError(msg)
        return row_id

    def get_by_id(self, bookmark_id: int) -> Bookmark | None:
        cursor = self._connection.execute(
            "SELECT bookmark_id, url, display_name, display_name_normalized, initial_weight, times_copied FROM bookmarks WHERE bookmark_id = ?",
            (bookmark_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_bookmark(row)

    def get_by_url(self, url: str) -> Bookmark | None:
        cursor = self._connection.execute(
            "SELECT bookmark_id, url, display_name, display_name_normalized, initial_weight, times_copied FROM bookmarks WHERE url = ?",
            (url,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_bookmark(row)

    def increment_copy_count(self, bookmark_id: int) -> None:
        self._connection.execute(
            "UPDATE bookmarks SET times_copied = times_copied + 1, updated_at = CURRENT_TIMESTAMP WHERE bookmark_id = ?",
            (bookmark_id,),
        )
        self._connection.commit()

    def list_all(self) -> list[Bookmark]:
        cursor = self._connection.execute(
            "SELECT bookmark_id, url, display_name, display_name_normalized, initial_weight, times_copied FROM bookmarks",
        )
        return [self._row_to_bookmark(row) for row in cursor.fetchall()]

    def update(self, bookmark: Bookmark) -> None:
        self._connection.execute(
            """
            UPDATE bookmarks
            SET display_name = ?, display_name_normalized = ?, initial_weight = ?, updated_at = CURRENT_TIMESTAMP
            WHERE bookmark_id = ?
            """,
            (bookmark.display_name, bookmark.display_name_normalized, bookmark.initial_weight, bookmark.bookmark_id),
        )
        self._connection.commit()

    def _row_to_bookmark(self, row: sqlite3.Row) -> Bookmark:
        return Bookmark(
            row["bookmark_id"],
            row["url"],
            row["display_name"],
            row["display_name_normalized"],
            row["initial_weight"],
            row["times_copied"],
        )
