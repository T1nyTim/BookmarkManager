from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bookmark_manager.ui.viewmodels.bookmark_row_state import BookmarkRowState


@dataclass(slots=True)
class TagSectionState:
    tag_id: int
    tag_name: str
    is_expanded: bool
    row_states: tuple[BookmarkRowState, ...]
