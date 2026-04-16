from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QMenu, QPushButton, QVBoxLayout, QWidget

from bookmark_manager.utils.url_formatter import shorten_url

if TYPE_CHECKING:
    from collections.abc import Sequence

    from PySide6.QtGui import QContextMenuEvent, QMouseEvent

    from bookmark_manager.domain.models import Bookmark, Selection


class BookmarkRowWidget(QFrame):
    clicked = Signal(int)
    copy_requested = Signal(int, str)
    edit_requested = Signal(int)

    def __init__(self, bookmark: Bookmark, tag_names: Sequence[str] = ()) -> None:
        super().__init__()
        self._bookmark = bookmark
        self._tag_names = tuple(tag_names)
        self._is_selected = False
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(8, 8, 8, 8)
        root_layout.setSpacing(6)
        self.setLayout(root_layout)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        self._display_name_label = QLabel(bookmark.display_name)
        display_name_font = self._display_name_label.font()
        display_name_font.setBold(True)
        self._display_name_label.setFont(display_name_font)
        self._display_name_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        header_layout.addWidget(self._display_name_label)
        header_layout.addStretch(1)
        self._copy_button = QPushButton("Copy")
        self._copy_button.clicked.connect(self._on_copy_clicked)
        header_layout.addWidget(self._copy_button)
        root_layout.addLayout(header_layout)
        self._url_label = QLabel(shorten_url(bookmark.url))
        self._url_label.setToolTip(bookmark.url)
        self._url_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        root_layout.addWidget(self._url_label)
        self._tags_container = QWidget()
        self._tags_layout = QHBoxLayout()
        self._tags_layout.setContentsMargins(0, 0, 0, 0)
        self._tags_layout.setSpacing(4)
        self._tags_container.setLayout(self._tags_layout)
        root_layout.addWidget(self._tags_container)
        self._populate_tags()
        self._apply_selected_style()

    def bookmark_id(self) -> int:
        return self._bookmark.bookmark_id

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:  # noqa: N802
        menu = QMenu(self)
        copy_action = QAction("Copy URL", self)
        copy_action.triggered.connect(self._on_copy_clicked)
        menu.addAction(copy_action)
        edit_action = QAction("Edit URL", self)
        edit_action.triggered.connect(self._on_edit_clicked)
        menu.addAction(edit_action)
        menu.exec_(event.globalPos())

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._bookmark.bookmark_id)
            event.accept()
            return
        super().mousePressEvent(event)

    def set_selected(self, selected: Selection) -> None:
        self._is_selected = bool(selected)
        self._apply_selected_style()

    def _apply_selected_style(self) -> None:
        if self._is_selected:
            self.setStyleSheet("QFrame { background-color: palette(alternate-base); border: 1px solid palette(highlight); border-radius: 6px; }")
            return
        self.setStyleSheet("QFrame { background-color: palette(base); border: 1px solid palette(mid); border-radius: 6px; }")

    def _on_copy_clicked(self) -> None:
        self.copy_requested.emit(self._bookmark.bookmark_id, self._bookmark.url)

    def _on_edit_clicked(self) -> None:
        self.edit_requested.emit(self._bookmark.bookmark_id)

    def _populate_tags(self) -> None:
        if not self._tag_names:
            self._tags_container.hide()
            return
        for tag_name in self._tag_names:
            label = QLabel(tag_name)
            label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
            label.setStyleSheet("QLabel { border: 1px solid palette(mid); border-radius: 8px; padding: 2px 6px; }")
            self._tags_layout.addWidget(label)
        self._tags_layout.addStretch(1)
