from dataclasses import dataclass


@dataclass(slots=True)
class AppState:
    search_text: str = ""
    selected_bookmark_id: int | None = None
    is_showing_bookmark_editor: bool = False
    editing_bookmark_id: int | None = None


class StateStore:
    def __init__(self) -> None:
        self._state = AppState()

    @property
    def state(self) -> AppState:
        return self._state

    def clear_selection(self) -> None:
        self._state.selected_bookmark_id = None

    def close_dialog(self) -> None:
        self._state.is_showing_bookmark_editor = False
        self._state.editing_bookmark_id = None

    def open_add_dialog(self) -> None:
        self._state.is_showing_bookmark_editor = True
        self._state.editing_bookmark_id = None

    def open_edit_dialog(self, bookmark_id: int) -> None:
        self._state.is_showing_bookmark_editor = True
        self._state.editing_bookmark_id = bookmark_id

    def set_search_text(self, query_text: str) -> None:
        self._state.search_text = query_text

    def toggle_selection(self, bookmark_id: int) -> None:
        if self._state.selected_bookmark_id == bookmark_id:
            self._state.selected_bookmark_id = None
            return
        self._state.selected_bookmark_id = bookmark_id
