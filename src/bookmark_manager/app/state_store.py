from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bookmark_manager.services.bookmark import DuplicateCandidate


@dataclass(slots=True)
class AppState:
    search_text: str = ""
    selected_bookmark_id: int | None = None
    is_add_dialog_open: bool = False
    editing_bookmark_id: int | None = None
    expanded_tag_ids: set[int] = field(default_factory=set)
    duplicate_candidate: DuplicateCandidate | None = None


class StateStore:
    def __init__(self) -> None:
        self._state = AppState()

    @property
    def state(self) -> AppState:
        return self._state

    def clear_duplicate_candidate(self) -> None:
        self._state.duplicate_candidate = None

    def clear_selection(self) -> None:
        self._state.selected_bookmark_id = None

    def close_dialog(self) -> None:
        self._state.is_add_dialog_open = False
        self._state.editing_bookmark_id = None

    def open_add_dialog(self) -> None:
        self._state.is_add_dialog_open = True
        self._state.editing_bookmark_id = None
        self._state.duplicate_candidate = None

    def open_duplicate_resolution(self, candidate: DuplicateCandidate) -> None:
        self.close_dialog()
        self._state.duplicate_candidate = candidate

    def open_edit_dialog(self, bookmark_id: int) -> None:
        self._state.is_add_dialog_open = False
        self._state.editing_bookmark_id = bookmark_id
        self._state.duplicate_candidate = None

    def selected_bookmark_id(self) -> int | None:
        return self._state.selected_bookmark_id

    def set_search_text(self, text: str) -> None:
        self._state.search_text = text

    def toggle_selection(self, bookmark_id: int) -> None:
        if self._state.selected_bookmark_id == bookmark_id:
            self._state.selected_bookmark_id = None
            return
        self._state.selected_bookmark_id = bookmark_id

    def toggle_tag_expansion(self, tag_id: int) -> None:
        if tag_id in self._state.expanded_tag_ids:
            self._state.expanded_tag_ids.remove(tag_id)
        else:
            self._state.expanded_tag_ids.add(tag_id)
