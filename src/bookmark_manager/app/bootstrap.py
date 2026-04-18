from typing import TYPE_CHECKING

from bookmark_manager.app.dispatcher import AppDispatcher, DispatcherServices
from bookmark_manager.app.projections import ProjectionBuilder
from bookmark_manager.app.state_store import StateStore
from bookmark_manager.services.clipboard import ClipboardService
from bookmark_manager.services.tag_view import TagViewService
from bookmark_manager.utils.url_formatter import shorten_url

if TYPE_CHECKING:
    from bookmark_manager.repositories.bookmark import BookmarkRepository
    from bookmark_manager.repositories.bookmark_tag import BookmarkTagRepository
    from bookmark_manager.repositories.tag import TagRepository
    from bookmark_manager.services.bookmark import BookmarkService
    from bookmark_manager.services.search import SearchService


def build_dispatcher(
    bookmark_service: BookmarkService,
    search_service: SearchService,
    tag_repository: TagRepository,
    bookmark_tag_repository: BookmarkTagRepository,
    bookmark_repository: BookmarkRepository,
) -> AppDispatcher:
    state_store = StateStore()
    projection_builder = ProjectionBuilder(shorten_url)
    clipboard_service = ClipboardService(bookmark_service)
    tag_view_service = TagViewService(tag_repository, bookmark_tag_repository, bookmark_repository)
    services = DispatcherServices(bookmark_service, search_service, clipboard_service, tag_view_service)
    return AppDispatcher(state_store, projection_builder, services)
