from dataclasses import dataclass
from functools import singledispatchmethod
from typing import TYPE_CHECKING

from bookmark_manager.app.intents import (
    RequestAddBookmark,
    RequestCancelBookmarkEditor,
    RequestConfirmBookmarkEditor,
    RequestCopyBookmark,
    RequestCopySelectedBookmark,
    RequestEditBookmark,
    RequestEditSelectedBookmark,
    RequestSearchChanged,
    RequestToggleSelection,
    RequestToggleTagExpansion,
)

if TYPE_CHECKING:
    from bookmark_manager.app.intents import (
        Intent,
    )
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
        self._dispatch_intent(intent)
        return self._build_projection()

    @singledispatchmethod
    def _dispatch_intent(self, intent: object) -> None:
        msg = f"Unsupported intent: {type(intent).__name__}"
        raise TypeError(msg)

    @_dispatch_intent.register
    def _(self, _: RequestAddBookmark) -> None:
        self._state_store.open_add_dialog()

    @_dispatch_intent.register
    def _r(self, _: RequestCancelBookmarkEditor) -> None:
        self._state_store.close_dialog()

    @_dispatch_intent.register
    def _(self, intent: RequestConfirmBookmarkEditor) -> None:
        editing_bookmark_id = self._state_store.state.editing_bookmark_id
        if editing_bookmark_id is None:
            self._services.bookmark.add_bookmark(intent.url, intent.display_name, intent.tag_names, intent.initial_weight)
        else:
            self._services.bookmark.edit_bookmark(editing_bookmark_id, intent.display_name, intent.tag_names, intent.initial_weight)
        self._state_store.close_dialog()

    @_dispatch_intent.register
    def _(self, intent: RequestCopyBookmark) -> None:
        bookmark = self._services.search.get_bookmark_for_edit(intent.bookmark_id)
        if bookmark is None:
            return
        self._services.clipboard.copy(intent.bookmark_id, bookmark.url)

    @_dispatch_intent.register
    def _(self, _: RequestCopySelectedBookmark) -> None:
        selected_bookmark_id = self._state_store.state.selected_bookmark_id
        if selected_bookmark_id is None:
            return
        bookmark = self._services.search.get_bookmark_for_edit(selected_bookmark_id)
        if bookmark is None:
            self._state_store.clear_selection()
            return
        self._services.clipboard.copy(selected_bookmark_id, bookmark.url)

    @_dispatch_intent.register
    def _(self, intent: RequestEditBookmark) -> None:
        self._state_store.open_edit_dialog(intent.bookmark_id)

    @_dispatch_intent.register
    def _(self, _: RequestEditSelectedBookmark) -> None:
        selected_bookmark_id = self._state_store.state.selected_bookmark_id
        if selected_bookmark_id is None:
            return
        self._state_store.open_edit_dialog(selected_bookmark_id)

    @_dispatch_intent.register
    def _(self, intent: RequestSearchChanged) -> None:
        self._state_store.set_search_text(intent.query_text)

    @_dispatch_intent.register
    def _(self, intent: RequestToggleSelection) -> None:
        self._state_store.toggle_selection(intent.bookmark_id)

    @_dispatch_intent.register
    def _(self, intent: RequestToggleTagExpansion) -> None:
        self._state_store.toggle_tag_expansion(intent.tag_id)

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
