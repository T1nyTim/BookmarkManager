from typing import TYPE_CHECKING

from PySide6.QtWidgets import QLineEdit, QMainWindow, QVBoxLayout, QWidget

if TYPE_CHECKING:
    from bookmark_manager.services.search import SearchService
    from bookmark_manager.services.selection import SelectionService


class MainWindow(QMainWindow):
    def __init__(self, search_service: SearchService, selection_service: SelectionService) -> None:
        super().__init__()
        self._search_service = search_service
        self._selection_service = selection_service
        self.setWindowTitle("Bookmark Manager")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self._layout = QVBoxLayout()
        central_widget.setLayout(self._layout)
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Search...")
        self._layout.addWidget(self._search_input)
        # TODO: actual content view later to be built
        self._results_container = QWidget()
        self._results_layout = QVBoxLayout()
        self._results_container.setLayout(self._results_layout)
        self._layout.addWidget(self._results_container)
        self._search_input.textChanged.connect(self._on_search_changed)

    def _on_search_changed(self, text: str) -> None:
        results = self._search_service.search(text)
        while self._results_layout.count():
            item = self._results_layout.takeAt(0)
            if item is None:
                break
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        # TODO: replace with real bookmark row widgets
        for bookmark in results:
            widget = QWidget()
            self._results_layout.addWidget(widget)
