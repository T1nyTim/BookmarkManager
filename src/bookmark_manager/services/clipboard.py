from typing import TYPE_CHECKING

from PySide6.QtGui import QGuiApplication

if TYPE_CHECKING:
    from bookmark_manager.services.bookmark import BookmarkService


class ClipboardService:
    def __init__(self, bookmark_service: BookmarkService) -> None:
        self._bookmark_service = bookmark_service

    def copy(self, bookmark_id: int, url: str) -> None:
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(url)
        self._bookmark_service.copy_bookmark(bookmark_id)
