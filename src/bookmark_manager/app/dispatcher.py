from dataclasses import dataclass
from typing import TYPE_CHECKING

from bookmark_manager.app.intents import (
    RequestAddBookmark,
    RequestCancelBookmarkEditor,
    RequestConfirmBookmarkEditor,
    RequestCopyBookmark,
    RequestCopySelectedBookmark,
    RequestEditBookmark,
    RequestSearchChanged,
    RequestToggleSelection,
    RequestToggleTagExpansion,
)

if TYPE_CHECKING:
    from bookmark_manager.app.intents import Intent
    from bookmark_manager.app.projections import MainWindowProjection, ProjectionBuilder
    from bookmark_manager.app.state_store import StateStore
    from bookmark_manager.services.bookmark import BookmarkService
    from bookmark_manager.services.clipboard import ClipboardService
    from bookmark_manager.services.search import SearchService
    from bookmark_manager.services.tag_view import TagViewService


@dataclass(slots=True, frozen=True)
class DispatcherServices:
    bookmark: BookmarkService
    search: SearchService
    clipboard: ClipboardService
    tag_view: TagViewService


class AppDispatcher:
    def __init__(
        self,
        state_store: StateStore,
        projection_builder: ProjectionBuilder,
        services: DispatcherServices,
    ) -> None:
        self._state_store = state_store
        self._projection_builder = projection_builder
        self._services = services

    def dispatch(self, intent: Intent) -> MainWindowProjection:
        if isinstance(intent, RequestAddBookmark):
            self._state_store.open_add_dialog()
        elif isinstance(intent, RequestCancelBookmarkEditor):
            self._state_store.close_dialog()
        elif isinstance(intent, RequestConfirmBookmarkEditor):
            self._handle_confirm_bookmark_editor(intent)
        elif isinstance(intent, RequestCopyBookmark):
            self._handle_copy_bookmark(intent.bookmark_id, intent.url)
        elif isinstance(intent, RequestCopySelectedBookmark):
            self._handle_copy_selected_bookmark()
        elif isinstance(intent, RequestEditBookmark):
            self._state_store.open_edit_dialog(intent.bookmark_id)
        elif isinstance(intent, RequestSearchChanged):
            self._state_store.set_search_text(intent.query_text)
        elif isinstance(intent, RequestToggleSelection):
            self._state_store.toggle_selection(intent.bookmark_id)
        elif isinstance(intent, RequestToggleTagExpansion):
            self._state_store.toggle_tag_expansion(intent.tag_id)
        else:
            msg = f"Unsupported intent: {type(intent).__name__}"
            raise TypeError(msg)
        return self._build_projection()

    def _build_projection(self) -> MainWindowProjection:
        state = self._state_store.state
        editable_bookmark = None
        if state.editing_bookmark_id is not None:
            editable_bookmark = self._services.search.get_bookmark_for_edit(state.editing_bookmark_id)
            if editable_bookmark is None:
                self._state_store.close_dialog()
        search_result = self._services.search.search(state.search_text)
        tag_sections = self._services.tag_view.get_tag_sections()
        return self._projection_builder.build_main_window(self._state_store.state, search_result, editable_bookmark, tag_sections)

    def _handle_confirm_bookmark_editor(self, intent: RequestConfirmBookmarkEditor) -> None:
        editing_bookmark_id = self._state_store.state.editing_bookmark_id
        if editing_bookmark_id is None:
            self._services.bookmark.add_bookmark(intent.url, intent.display_name, intent.tag_names, intent.initial_weight)
        else:
            self._services.bookmark.edit_bookmark(editing_bookmark_id, intent.display_name, intent.tag_names, intent.initial_weight)
        self._state_store.close_dialog()

    def _handle_copy_bookmark(self, bookmark_id: int, url: str) -> None:
        self._services.clipboard.copy_text(url)
        self._services.bookmark.copy_bookmark(bookmark_id)

    def _handle_copy_selected_bookmark(self) -> None:
        selected_bookmark_id = self._state_store.state.selected_bookmark_id
        if selected_bookmark_id is None:
            return
        bookmark = self._services.search.get_bookmark_for_edit(selected_bookmark_id)
        if bookmark is None:
            self._state_store.clear_selection()
            return
        self._services.clipboard.copy(selected_bookmark_id, bookmark.url)
