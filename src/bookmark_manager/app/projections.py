from dataclasses import dataclass
from typing import TYPE_CHECKING

from bookmark_manager.ui.viewmodels.bookmark_row_state import BookmarkRowState
from bookmark_manager.ui.viewmodels.content_state import ContentState, TagViewState
from bookmark_manager.ui.viewmodels.search_results_state import SearchResultsState
from bookmark_manager.ui.viewmodels.tag_section_state import TagSectionState
from bookmark_manager.utils.models import EditorMode, Mergeability, Selection

if TYPE_CHECKING:
    from collections.abc import Callable

    from bookmark_manager.app.state_store import AppState
    from bookmark_manager.domain.models import Bookmark
    from bookmark_manager.services.bookmark import DuplicateCandidate
    from bookmark_manager.services.search import EditableBookmark, SearchResult
    from bookmark_manager.services.tag_view import TagSectionDomain


@dataclass(slots=True, frozen=True)
class BookmarkEditorProjection:
    mode: EditorMode
    url: str
    display_name: str
    tag_names: tuple[str, ...]
    initial_weight: int


@dataclass(slots=True, frozen=True)
class DuplicateFieldProjection:
    label: str
    existing_value: str
    incoming_value: str
    values_match: bool
    allow_merge: Mergeability = Mergeability.UNMERGEABLE


@dataclass(slots=True, frozen=True)
class DuplicateResolutionProjection:
    bookmark_id: int
    url: str
    display_name: DuplicateFieldProjection
    tags: DuplicateFieldProjection
    initial_weight: DuplicateFieldProjection


@dataclass(slots=True, frozen=True)
class MainWindowProjection:
    menu_state: MenuStateProjection
    content_state: ContentState
    bookmark_editor: BookmarkEditorProjection | None
    duplicate_resolution: DuplicateResolutionProjection | None
    selected_bookmark_id: int | None


@dataclass(slots=True, frozen=True)
class MenuStateProjection:
    can_copy: bool
    can_edit: bool


class ProjectionBuilder:
    def __init__(self, shorten_url: Callable[[str], str]) -> None:
        self._shorten_url = shorten_url

    def build_main_window(
        self,
        state: AppState,
        search_result: SearchResult,
        editable_bookmark: EditableBookmark | None,
        tag_sections: tuple[TagSectionDomain, ...],
    ) -> MainWindowProjection:
        has_selection = state.selected_bookmark_id is not None
        menu_state = MenuStateProjection(has_selection, has_selection)
        content_state = self._build_content_state(state, search_result, tag_sections)
        bookmark_editor = self._build_bookmark_editor(state, editable_bookmark)
        duplicate_resolution = self._build_duplicate_resolution(state.duplicate_candidate)
        return MainWindowProjection(menu_state, content_state, bookmark_editor, duplicate_resolution, state.selected_bookmark_id)

    def _build_bookmark_editor(self, state: AppState, editable_bookmark: EditableBookmark | None) -> BookmarkEditorProjection | None:
        if state.is_add_dialog_open:
            return BookmarkEditorProjection(EditorMode.ADD, "", "", (), 0)
        if state.editing_bookmark_id is not None and editable_bookmark is not None:
            return BookmarkEditorProjection(
                EditorMode.EDIT,
                editable_bookmark.url,
                editable_bookmark.display_name,
                editable_bookmark.tag_names,
                editable_bookmark.initial_weight,
            )
        return None

    def _build_content_state(self, state: AppState, search_result: SearchResult, tag_sections: tuple[TagSectionDomain, ...]) -> ContentState:
        if state.search_text.strip():
            return ContentState(
                SearchResultsState.from_domain(
                    state.search_text,
                    search_result.bookmarks,
                    self._shorten_url,
                    search_result.bookmark_id_to_tag_names,
                    state.selected_bookmark_id,
                ),
                None,
            )
        return ContentState(
            None,
            TagViewState(
                tuple(
                    TagSectionState(
                        section.tag_id,
                        section.tag_name,
                        section.tag_id in state.expanded_tag_ids,
                        tuple(
                            search_result_row_from_bookmark(
                                bookmark,
                                self._shorten_url,
                                search_result.bookmark_id_to_tag_names.get(bookmark.bookmark_id, ()),
                                state.selected_bookmark_id,
                            )
                            for bookmark in section.bookmarks
                        ),
                    )
                    for section in tag_sections
                ),
            ),
        )

    def _build_duplicate_resolution(self, candidate: DuplicateCandidate | None) -> DuplicateResolutionProjection | None:
        if candidate is None:
            return None
        return DuplicateResolutionProjection(
            candidate.bookmark_id,
            candidate.url,
            DuplicateFieldProjection(
                "Display Name",
                candidate.existing_display_name,
                candidate.incoming_display_name,
                candidate.existing_display_name == candidate.incoming_display_name,
            ),
            DuplicateFieldProjection(
                "Tags",
                " ".join(candidate.existing_tag_names),
                " ".join(candidate.incoming_tag_names),
                tuple(candidate.existing_tag_names) == tuple(candidate.incoming_tag_names),
                Mergeability.MERGEABLE,
            ),
            DuplicateFieldProjection(
                "Initial Weight",
                str(candidate.existing_initial_weight),
                str(candidate.incoming_initial_weight),
                candidate.existing_initial_weight == candidate.incoming_initial_weight,
            ),
        )


def search_result_row_from_bookmark(
    bookmark: Bookmark,
    shorten_url: Callable[[str], str],
    tag_names: tuple[str, ...],
    selected_bookmark_id: int | None,
) -> BookmarkRowState:
    return BookmarkRowState.from_domain(
        bookmark,
        shorten_url,
        tag_names,
        Selection.SELECTED if bookmark.bookmark_id == selected_bookmark_id else Selection.NOT_SELECTED,
    )
