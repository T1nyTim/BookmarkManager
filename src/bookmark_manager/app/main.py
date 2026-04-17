import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from bookmark_manager.infra.database import get_connection, initialize_schema
from bookmark_manager.repositories.bookmark import BookmarkRepository
from bookmark_manager.repositories.bookmark_tag import BookmarkTagRepository
from bookmark_manager.repositories.tag import TagRepository
from bookmark_manager.services.bookmark import BookmarkService
from bookmark_manager.services.search import SearchService
from bookmark_manager.services.selection import SelectionService
from bookmark_manager.ui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    db_path = Path.cwd() / "bookmarks.sqlite3"
    connection = get_connection(db_path)
    initialize_schema(connection)
    bookmark_repo = BookmarkRepository(connection)
    tag_repo = TagRepository(connection)
    bookmark_tag_repo = BookmarkTagRepository(connection)
    bookmark_service = BookmarkService(bookmark_repo, tag_repo, bookmark_tag_repo)
    search_service = SearchService(bookmark_repo, bookmark_tag_repo)
    selection_service = SelectionService()
    window = MainWindow(search_service, selection_service, bookmark_service)
    window.showMaximized()
    app.exec()


if __name__ == "__main__":
    main()
