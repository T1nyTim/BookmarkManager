from typing import TYPE_CHECKING

from PySide6.QtWidgets import QLineEdit, QMainWindow, QVBoxLayout, QWidget

from bookmark_manager.ui.widgets.bookmark_row import BookmarkRowWidget

if TYPE_CHECKING:
    from bookmark_manager.services.search import SearchService
    from bookmark_manager.services.selection import SelectionService


class MainWindow(QMainWindow):
    def __init__(self, search_service: SearchService, selection_service: SelectionService) -> None:
        super().__init__()
        self._search_service = search_service
        self._selection_service = selection_service
        self._result_widgets = {}
        self.setWindowTitle("Bookmark Manager")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self._layout = QVBoxLayout()
        central_widget.setLayout(self._layout)
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Search...")
        self._search_input.textChanged.connect(self._on_search_changed)
        self._layout.addWidget(self._search_input)
        self._results_container = QWidget()
        self._results_layout = QVBoxLayout()
        self._results_container.setLayout(self._results_layout)
        self._layout.addWidget(self._results_container)
        self._on_search_changed("")

    def _clear_results(self) -> None:
        self._result_widgets.clear()
        while self._results_layout.count() > 0:
            item = self._results_layout.takeAt(0)
            if item is None:
                continue
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _on_bookmark_clicked(self, bookmark_id: int) -> None:
        self._selection_service.select(bookmark_id)
        self._refresh_selection_state()

    def _on_search_changed(self, text: str) -> None:
        results = self._search_service.search(text)
        self._clear_results()
        for bookmark in results:
            widget = BookmarkRowWidget(bookmark)
            widget.set_selected(bookmark.bookmark_id == self._selection_service.get_selected())
            widget.clicked.connect(self._on_bookmark_clicked)
            self._results_layout.addWidget(widget)
            self._result_widgets[bookmark.bookmark_id] = widget

    def _refresh_selection_state(self) -> None:
        selected_bookmark_id = self._selection_service.get_selected()
        for bookmark_id, widget in self._result_widgets.items():
            widget.set_selected(bookmark_id == selected_bookmark_id)
