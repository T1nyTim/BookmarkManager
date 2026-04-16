import sqlite3
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def get_connection(db_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS bookmarks (
            bookmark_id INTEGER PRIMARY KEY,
            url TEXT NOT NULL UNIQUE,
            display_name TEXT NOT NULL,
            display_name_normalized TEXT NOT NULL,
            initial_weight INTEGER NOT NULL CHECK (initial_weight >= 0),
            times_copied INTEGER NOT NULL DEFAULT 0 CHECK (times_copied >= 0),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS tags (
            tag_id INTEGER PRIMARY KEY,
            name_display TEXT NOT NULL,
            name_normalized TEXT NOT NULL UNIQUE
        );
        CREATE TABLE IF NOT EXISTS bookmark_tags (
            bookmark_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (bookmark_id, tag_id),
            FOREIGN KEY (bookmark_id) REFERENCES bookmarks(bookmark_id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags(tag_id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_bookmarks_display_name_norm ON bookmarks(display_name_normalized);
        CREATE INDEX IF NOT EXISTS idx_tags_name_normalized ON tags(name_normalized);
        CREATE INDEX IF NOT EXISTS idx_bookmark_tags_tag ON bookmark_tags(tag_id, bookmark_id);
        CREATE INDEX IF NOT EXISTS idx_bookmark_tags_bookmark ON bookmark_tags(bookmark_id, tag_id);
        """,
    )
    connection.commit()
