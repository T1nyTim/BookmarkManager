from typing import TYPE_CHECKING

from bookmark_manager.app.dispatcher import AppDispatcher
from bookmark_manager.app.projections import ProjectionBuilder
from bookmark_manager.app.state_store import StateStore
from bookmark_manager.services.clipboard import ClipboardService

if TYPE_CHECKING:
    from bookmark_manager.services.bookmark import BookmarkService
    from bookmark_manager.services.search import SearchService


def build_dispatcher(bookmark_service: BookmarkService, search_service: SearchService) -> AppDispatcher:
    state_store = StateStore()
    projection_builder = ProjectionBuilder()
    clipboard_service = ClipboardService(bookmark_service)
    return AppDispatcher(state_store, projection_builder, bookmark_service, search_service, clipboard_service)
