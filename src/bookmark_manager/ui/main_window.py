from typing import TYPE_CHECKING

from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtWidgets import QLineEdit, QMainWindow, QMessageBox, QVBoxLayout, QWidget

from bookmark_manager.app.intents import (
    Intent,
    RequestAddBookmark,
    RequestCancelBookmarkEditor,
    RequestCopyBookmark,
    RequestCopySelectedBookmark,
    RequestEditBookmark,
    RequestSearchChanged,
    RequestSubmitAddBookmark,
    RequestSubmitEditBookmark,
    RequestToggleSelection,
)
from bookmark_manager.ui.dialogs.bookmark_editor import BookmarkEditorDialog, BookmarkEditorState
from bookmark_manager.ui.widgets.bookmark_row import BookmarkRowWidget

if TYPE_CHECKING:
    from bookmark_manager.app.dispatcher import AppDispatcher
    from bookmark_manager.app.projections import MainWindowProjection


class MainWindow(QMainWindow):
    def __init__(self, dispatcher: AppDispatcher) -> None:
        super().__init__()
        self._dispatcher = dispatcher
        self._result_widgets = {}
        self._selected_bookmark_id = None
        self.setWindowTitle("Bookmark Manager")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self._layout = QVBoxLayout()
        central_widget.setLayout(self._layout)
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Search...")
        self._search_input.textChanged.connect(self._on_search_text_changed)
        self._layout.addWidget(self._search_input)
        self._results_container = QWidget()
        self._results_layout = QVBoxLayout()
        self._results_container.setLayout(self._results_layout)
        self._layout.addWidget(self._results_container)
        self._build_actions()
        self._build_menus()
        self._build_shortcuts()
        self._render(self._dispatcher.dispatch(RequestSearchChanged(query_text="")))

    def _build_actions(self) -> None:
        self._add_bookmark_action = QAction("Add URL", self)
        self._add_bookmark_action.setShortcut(QKeySequence("Ctrl+A"))
        self._add_bookmark_action.triggered.connect(self._on_add_bookmark_requested)
        self._copy_bookmark_action = QAction("Copy URL", self)
        self._copy_bookmark_action.setShortcut(QKeySequence("Ctrl+C"))
        self._copy_bookmark_action.triggered.connect(self._on_copy_selected_requested)
        self._edit_bookmark_action = QAction("Edit URL", self)
        self._edit_bookmark_action.triggered.connect(self._on_edit_selected_requested)
        self._exit_action = QAction("Exit", self)
        self._exit_action.triggered.connect(self.close)

    def _build_menus(self) -> None:
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        file_menu.addAction(self._add_bookmark_action)
        file_menu.addSeparator()
        file_menu.addAction(self._exit_action)
        edit_menu = menu_bar.addMenu("Edit")
        edit_menu.addAction(self._copy_bookmark_action)
        edit_menu.addAction(self._edit_bookmark_action)

    def _build_shortcuts(self) -> None:
        self._copy_shortcut = QShortcut(QKeySequence("Ctrl+C"), self)
        self._copy_shortcut.activated.connect(self._on_copy_selected_requested)

    def _clear_results(self) -> None:
        self._result_widgets.clear()
        while self._results_layout.count() > 0:
            item = self._results_layout.takeAt(0)
            if item is None:
                continue
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _dispatch_and_render(self, intent: Intent) -> None:
        try:
            projection = self._dispatcher.dispatch(intent)
        except ValueError as err:
            QMessageBox.warning(self, self.windowTitle(), str(err))
            return
        self._render(projection)

    def _on_add_bookmark_requested(self) -> None:
        self._dispatch_and_render(RequestAddBookmark())

    def _on_bookmark_clicked(self, bookmark_id: int) -> None:
        self._dispatch_and_render(RequestToggleSelection(bookmark_id))

    def _on_copy_bookmark_requested(self, bookmark_id: int, url: str) -> None:
        self._dispatch_and_render(RequestCopyBookmark(bookmark_id, url))

    def _on_copy_selected_requested(self) -> None:
        self._dispatch_and_render(RequestCopySelectedBookmark())

    def _on_edit_bookmark_requested(self, bookmark_id: int) -> None:
        self._dispatch_and_render(RequestEditBookmark(bookmark_id))

    def _on_edit_selected_requested(self) -> None:
        selected_bookmark_id = self._selected_bookmark_id
        if selected_bookmark_id is None:
            return
        self._dispatch_and_render(RequestEditBookmark(selected_bookmark_id))

    def _on_search_text_changed(self, text: str) -> None:
        self._dispatch_and_render(RequestSearchChanged(text))

    def _show_bookmark_editor(self, projection: MainWindowProjection) -> None:
        editor = projection.bookmark_editor
        if editor is None:
            return
        dialog = BookmarkEditorDialog(
            self,
            BookmarkEditorState(editor.url, editor.display_name, editor.tag_names, editor.initial_weight, editor.mode),
        )
        if dialog.exec() != BookmarkEditorDialog.DialogCode.Accepted:
            self._dispatch_and_render(RequestCancelBookmarkEditor())
            return
        if editor.bookmark_id is None:
            self._dispatch_and_render(RequestSubmitAddBookmark(dialog.url(), dialog.display_name(), tuple(dialog.tags()), dialog.initial_weight()))
            return
        self._dispatch_and_render(RequestSubmitEditBookmark(editor.bookmark_id, dialog.display_name(), tuple(dialog.tags()), dialog.initial_weight()))

    def _render(self, projection: MainWindowProjection) -> None:
        self._selected_bookmark_id = projection.selected_bookmark_id
        self._copy_bookmark_action.setEnabled(projection.menu_state.can_copy)
        self._edit_bookmark_action.setEnabled(projection.menu_state.can_edit)
        self._clear_results()
        for row_state in projection.search_results.row_states:
            widget = BookmarkRowWidget(row_state)
            widget.clicked.connect(self._on_bookmark_clicked)
            widget.copy_requested.connect(self._on_copy_bookmark_requested)
            widget.edit_requested.connect(self._on_edit_bookmark_requested)
            self._results_layout.addWidget(widget)
            self._result_widgets[row_state.bookmark_id] = widget
        if projection.bookmark_editor is not None:
            self._show_bookmark_editor(projection)
