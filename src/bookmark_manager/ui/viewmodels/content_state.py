from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bookmark_manager.ui.viewmodels.search_results_state import SearchResultsState
    from bookmark_manager.ui.viewmodels.tag_section_state import TagSectionState


@dataclass(slots=True)
class TagViewState:
    sections: tuple[TagSectionState, ...]


@dataclass(slots=True)
class ContentState:
    search_results: SearchResultsState | None
    tag_view: TagViewState | None

    @property
    def is_search_mode(self) -> bool:
        return self.search_results is not None

    @property
    def is_tag_mode(self) -> bool:
        return self.tag_view is not None
