from dataclasses import dataclass
from typing import TYPE_CHECKING

from bookmark_manager.ui.viewmodels.bookmark_row_state import BookmarkRowState
from bookmark_manager.utils.models import Selection

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence

    from bookmark_manager.domain.models import Bookmark


@dataclass(slots=True)
class SearchResultsState:
    query_text: str
    row_states: tuple[BookmarkRowState, ...]

    @property
    def is_search_mode(self) -> bool:
        return bool(self.query_text.strip())

    @classmethod
    def from_domain(
        cls,
        query_text: str,
        bookmarks: Sequence[Bookmark],
        shorten_url: Callable[[str], str],
        bookmark_id_to_tag_names: Mapping[int, tuple[str, ...]],
        selected_bookmark_id: int | None,
    ) -> SearchResultsState:
        row_states = tuple(
            BookmarkRowState.from_domain(
                bookmark,
                shorten_url,
                bookmark_id_to_tag_names.get(bookmark.bookmark_id, ()),
                Selection.SELECTED if bookmark.bookmark_id == selected_bookmark_id else Selection.NOT_SELECTED,
            )
            for bookmark in bookmarks
        )
        return cls(query_text, row_states)
