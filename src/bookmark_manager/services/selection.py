class SelectionService:
    def __init__(self) -> None:
        self._selected_bookmark_id = None

    def clear(self) -> None:
        self._selected_bookmark_id = None

    def get_selected(self) -> int | None:
        return self._selected_bookmark_id

    def select(self, bookmark_id: int) -> None:
        if self._selected_bookmark_id == bookmark_id:
            self._selected_bookmark_id = None
            return
        self._selected_bookmark_id = bookmark_id
