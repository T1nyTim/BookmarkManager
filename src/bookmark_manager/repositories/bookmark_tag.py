import json
from typing import TYPE_CHECKING

from bookmark_manager.domain.models import Bookmark, Tag

if TYPE_CHECKING:
    import sqlite3


class BookmarkTagRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def get_bookmarks_for_tag(self, tag_id: int) -> list[Bookmark]:
        cursor = self._connection.execute(
            """
            SELECT
                bookmarks.bookmark_id,
                bookmarks.url,
                bookmarks.display_name,
                bookmarks.display_name_normalized,
                bookmarks.initial_weight,
                bookmarks.times_copied
            FROM bookmarks
            INNER JOIN bookmark_tags ON bookmarks.bookmark_id = bookmark_tags.bookmark_id
            WHERE bookmark_tags.tag_id = ?
            """,
            (tag_id,),
        )
        return [self._row_to_bookmark(row) for row in cursor.fetchall()]

    def get_tags_for_bookmark(self, bookmark_id: int) -> list[Tag]:
        cursor = self._connection.execute(
            """
            SELECT tags.tag_id, tags.name_display, tags.name_normalized
            FROM tags
            INNER JOIN bookmark_tags ON tags.tag_id = bookmark_tags.tag_id
            WHERE bookmark_tags.bookmark_id = ?
            """,
            (bookmark_id,),
        )
        return [self._row_to_tag(row) for row in cursor.fetchall()]

    def get_tags_for_bookmarks(self, bookmark_ids: tuple[int, ...]) -> dict[int, tuple[Tag, ...]]:
        if not bookmark_ids:
            return {}
        cursor = self._connection.execute(
            """
            SELECT bookmark_tags.bookmark_id, tags.tag_id, tags.name_display, tags.name_normalized
            FROM bookmark_tags
            INNER JOIN tags ON tags.tag_id = bookmark_tags.tag_id
            WHERE bookmark_tags.bookmark_id IN (
                SELECT value FROM json_each(?)
            )
            """,
            (json.dumps(bookmark_ids),),
        )
        tags_by_bookmark_id = {}
        for row in cursor.fetchall():
            bookmark_id = row["bookmark_id"]
            tags_by_bookmark_id.setdefault(bookmark_id, []).append(self._row_to_tag(row))
        return {bookmark_id: tuple(tags) for bookmark_id, tags in tags_by_bookmark_id.items()}

    def has_bookmarks_for_tag(self, tag_id: int) -> bool:
        cursor = self._connection.execute("SELECT 1 FROM bookmark_tags WHERE tag_id = ? LIMIT 1", (tag_id,))
        return cursor.fetchone() is not None

    def link(self, bookmark_id: int, tag_id: int) -> None:
        self._connection.execute("INSERT OR IGNORE INTO bookmark_tags (bookmark_id, tag_id) VALUES (?, ?)", (bookmark_id, tag_id))
        self._connection.commit()

    def unlink_all(self, bookmark_id: int) -> None:
        self._connection.execute("DELETE FROM bookmark_tags WHERE bookmark_id = ?", (bookmark_id,))
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

    def _row_to_tag(self, row: sqlite3.Row) -> Tag:
        return Tag(row["tag_id"], row["name_display"], row["name_normalized"])
