from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QFrame, QLineEdit, QMainWindow, QMenuBar, QMessageBox, QPushButton, QVBoxLayout, QWidget

from bookmark_manager.app.intents import (
    Intent,
    RequestAddBookmark,
    RequestCopyBookmark,
    RequestCopySelectedBookmark,
    RequestEditBookmark,
    RequestEditSelectedBookmark,
    RequestSearchChanged,
    RequestToggleSelection,
    RequestToggleTagExpansion,
)
from bookmark_manager.ui.dialogs.bookmark_editor_presenter import BookmarkEditorPresenter
from bookmark_manager.ui.widgets.bookmark_row import BookmarkRowWidget

if TYPE_CHECKING:
    from bookmark_manager.app.dispatcher import AppDispatcher
    from bookmark_manager.app.projections import MainWindowProjection
    from bookmark_manager.ui.viewmodels.bookmark_row_state import BookmarkRowState
    from bookmark_manager.ui.viewmodels.content_state import TagViewState
    from bookmark_manager.ui.viewmodels.search_results_state import SearchResultsState


class MainWindow(QMainWindow):
    def __init__(self, dispatcher: AppDispatcher) -> None:
        super().__init__()
        self._dispatcher = dispatcher
        self._result_widgets = {}
        self.setWindowTitle("Bookmark Manager")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self._layout = QVBoxLayout()
        central_widget.setLayout(self._layout)
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Search...")
        self._search_input.textChanged.connect(self._on_search_text_changed)
        self._layout.addWidget(self._search_input)
        self._results_container = QFrame()
        self._results_container.setFrameShape(QFrame.Shape.StyledPanel)
        self._results_layout = QVBoxLayout()
        self._results_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._results_container.setLayout(self._results_layout)
        self._layout.addWidget(self._results_container, 1)
        self._bookmark_editor_presenter = BookmarkEditorPresenter(self)
        self._bookmark_editor_presenter.intent_emitted.connect(self._dispatch_and_render)
        self._build_actions()
        self._build_menus()
        self._render(self._dispatcher.dispatch(RequestSearchChanged(query_text="")))

    def _add_bookmark_row(self, row_state: BookmarkRowState) -> None:
        widget = BookmarkRowWidget(row_state)
        widget.clicked.connect(self._on_bookmark_clicked)
        widget.copy_requested.connect(self._on_copy_bookmark_requested)
        widget.edit_requested.connect(self._on_edit_bookmark_requested)
        self._results_layout.addWidget(widget)
        self._result_widgets[row_state.bookmark_id] = widget

    def _build_actions(self) -> None:
        self._add_bookmark_action = QAction("Add URL", self)
        self._add_bookmark_action.setShortcut(QKeySequence("Ctrl+N"))
        self._add_bookmark_action.triggered.connect(self._on_add_bookmark_requested)
        self._copy_bookmark_action = QAction("Copy URL", self)
        self._copy_bookmark_action.setShortcut(QKeySequence("Ctrl+C"))
        self._copy_bookmark_action.triggered.connect(self._on_copy_selected_requested)
        self._edit_bookmark_action = QAction("Edit URL", self)
        self._edit_bookmark_action.triggered.connect(self._on_edit_selected_requested)
        self._exit_action = QAction("Exit", self)
        self._exit_action.triggered.connect(self.close)

    def _build_menus(self) -> None:
        menu_bar = QMenuBar(self)
        menu_bar.setNativeMenuBar(False)
        self.setMenuBar(menu_bar)
        file_menu = menu_bar.addMenu("File")
        file_menu.addAction(self._add_bookmark_action)
        file_menu.addSeparator()
        file_menu.addAction(self._exit_action)
        edit_menu = menu_bar.addMenu("Edit")
        edit_menu.addAction(self._copy_bookmark_action)
        edit_menu.addAction(self._edit_bookmark_action)

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

    def _on_copy_bookmark_requested(self, bookmark_id: int) -> None:
        self._dispatch_and_render(RequestCopyBookmark(bookmark_id))

    def _on_copy_selected_requested(self) -> None:
        self._dispatch_and_render(RequestCopySelectedBookmark())

    def _on_edit_bookmark_requested(self, bookmark_id: int) -> None:
        self._dispatch_and_render(RequestEditBookmark(bookmark_id))

    def _on_edit_selected_requested(self) -> None:
        self._dispatch_and_render(RequestEditSelectedBookmark())

    def _on_search_text_changed(self, text: str) -> None:
        self._dispatch_and_render(RequestSearchChanged(text))

    def _render(self, projection: MainWindowProjection) -> None:
        self._copy_bookmark_action.setEnabled(projection.menu_state.can_copy)
        self._edit_bookmark_action.setEnabled(projection.menu_state.can_edit)
        self._clear_results()
        content_state = projection.content_state
        if content_state.search_results is not None:
            self._render_search_results(content_state.search_results)
        elif content_state.tag_view is not None:
            self._render_tag_view(content_state.tag_view)
        self._bookmark_editor_presenter.render(projection.bookmark_editor)

    def _render_search_results(self, state: SearchResultsState) -> None:
        for row_state in state.row_states:
            self._add_bookmark_row(row_state)

    def _render_tag_view(self, state: TagViewState) -> None:
        for section in state.sections:
            header = QPushButton(section.tag_name)
            header.clicked.connect(lambda _checked=False, tag_id=section.tag_id: self._dispatch_and_render(RequestToggleTagExpansion(tag_id)))
            self._results_layout.addWidget(header)
            if section.is_expanded:
                for row_state in section.row_states:
                    self._add_bookmark_row(row_state)
