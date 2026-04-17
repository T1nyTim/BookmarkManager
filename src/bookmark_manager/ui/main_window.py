from typing import TYPE_CHECKING

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QLineEdit, QMainWindow, QMessageBox, QVBoxLayout, QWidget

from bookmark_manager.ui.dialogs.bookmark_editor import BookmarkEditorDialog, BookmarkEditorState
from bookmark_manager.ui.viewmodels.search_results_state import SearchResultsState
from bookmark_manager.ui.widgets.bookmark_row import BookmarkRowWidget
from bookmark_manager.utils.models import Mode
from bookmark_manager.utils.url_formatter import shorten_url

if TYPE_CHECKING:
    from bookmark_manager.services.bookmark import BookmarkService
    from bookmark_manager.services.search import SearchService
    from bookmark_manager.services.selection import SelectionService


class MainWindow(QMainWindow):
    def __init__(self, search_service: SearchService, selection_service: SelectionService, bookmark_service: BookmarkService) -> None:
        super().__init__()
        self._search_service = search_service
        self._selection_service = selection_service
        self._bookmark_service = bookmark_service
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
        self._build_actions()
        self._build_menus()
        self._on_search_changed("")

    def _build_actions(self) -> None:
        self._add_bookmark_action = QAction("Add URL", self)
        self._add_bookmark_action.triggered.connect(self._on_add_bookmark_requested)

    def _build_menus(self) -> None:
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        file_menu.addAction(self._add_bookmark_action)

    def _clear_results(self) -> None:
        self._result_widgets.clear()
        while self._results_layout.count() > 0:
            item = self._results_layout.takeAt(0)
            if item is None:
                continue
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _on_add_bookmark_requested(self) -> None:
        dialog = BookmarkEditorDialog(self)
        if dialog.exec() != BookmarkEditorDialog.DialogCode.Accepted:
            return
        try:
            self._bookmark_service.add_bookmark(dialog.url(), dialog.display_name(), dialog.tags(), dialog.initial_weight())
        except ValueError as err:
            QMessageBox.warning(self, "Add URL", str(err))
            return
        self._on_search_changed(self._search_input.text())

    def _on_bookmark_clicked(self, bookmark_id: int) -> None:
        self._selection_service.select(bookmark_id)
        self._on_search_changed(self._search_input.text())

    def _on_edit_bookmark_requested(self, bookmark_id: int) -> None:
        bookmark = self._search_service.get_bookmark_for_edit(bookmark_id)
        if bookmark is None:
            QMessageBox.warning(self, "Edit URL", "Bookmark not found.")
            return
        dialog = BookmarkEditorDialog(
            self,
            BookmarkEditorState(bookmark.url, bookmark.display_name, bookmark.tag_names, bookmark.initial_weight, Mode.EDIT),
        )
        if dialog.exec() != BookmarkEditorDialog.DialogCode.Accepted:
            return
        try:
            self._bookmark_service.edit_bookmark(bookmark_id, dialog.display_name(), dialog.tags(), dialog.initial_weight())
        except ValueError as err:
            QMessageBox.warning(self, "Edit URL", str(err))
            return
        self._on_search_changed(self._search_input.text())

    def _on_search_changed(self, text: str) -> None:
        search_result = self._search_service.search(text)
        self._clear_results()
        state = SearchResultsState.from_domain(
            text,
            search_result.bookmarks,
            shorten_url,
            search_result.bookmark_id_to_tag_names,
            self._selection_service.get_selected(),
        )
        for row_state in state.row_states:
            widget = BookmarkRowWidget(row_state)
            widget.clicked.connect(self._on_bookmark_clicked)
            widget.edit_requested.connect(self._on_edit_bookmark_requested)
            self._results_layout.addWidget(widget)
            self._result_widgets[row_state.bookmark_id] = widget
