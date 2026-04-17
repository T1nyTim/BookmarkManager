from dataclasses import dataclass
from typing import TYPE_CHECKING

from bookmark_manager.ui.viewmodels.search_results_state import SearchResultsState
from bookmark_manager.utils.models import Mode
from bookmark_manager.utils.url_formatter import shorten_url

if TYPE_CHECKING:
    from bookmark_manager.app.state_store import AppState
    from bookmark_manager.services.search import EditableBookmark, SearchResult


@dataclass(slots=True, frozen=True)
class BookmarkEditorProjection:
    mode: Mode
    bookmark_id: int | None
    url: str
    display_name: str
    tag_names: tuple[str, ...]
    initial_weight: int


@dataclass(slots=True, frozen=True)
class MainWindowProjection:
    search_results: SearchResultsState
    menu_state: MenuStateProjection
    selected_bookmark_id: int | None
    bookmark_editor: BookmarkEditorProjection | None


@dataclass(slots=True, frozen=True)
class MenuStateProjection:
    can_copy: bool
    can_edit: bool


class ProjectionBuilder:
    def build_main_window(self, state: AppState, search_result: SearchResult, editable_bookmark: EditableBookmark | None) -> MainWindowProjection:
        selected_bookmark_id = state.selected_bookmark_id
        search_results = SearchResultsState.from_domain(
            state.search_text,
            search_result.bookmarks,
            shorten_url,
            search_result.bookmark_id_to_tag_names,
            selected_bookmark_id,
        )
        has_selection = selected_bookmark_id is not None
        menu_state = MenuStateProjection(has_selection, has_selection)
        bookmark_editor = None
        if state.is_showing_bookmark_editor:
            if editable_bookmark is None:
                bookmark_editor = BookmarkEditorProjection(Mode.ADD, None, "", "", (), 0)
            else:
                bookmark_editor = BookmarkEditorProjection(
                    Mode.EDIT,
                    editable_bookmark.bookmark_id,
                    editable_bookmark.url,
                    editable_bookmark.display_name,
                    editable_bookmark.tag_names,
                    editable_bookmark.initial_weight,
                )
        return MainWindowProjection(search_results, menu_state, selected_bookmark_id, bookmark_editor)
