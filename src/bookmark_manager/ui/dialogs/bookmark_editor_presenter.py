from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, Signal

from bookmark_manager.app.intents import RequestCancelBookmarkEditor, RequestConfirmBookmarkEditor
from bookmark_manager.ui.dialogs.bookmark_editor import BookmarkEditorDialog, BookmarkEditorState

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

    from bookmark_manager.app.projections import BookmarkEditorProjection


class BookmarkEditorPresenter(QObject):
    intent_emitted = Signal(object)

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self._parent = parent
        self._dialog = None
        self._active_projection = None

    def render(self, projection: BookmarkEditorProjection | None) -> None:
        if projection is None:
            self._close_dialog()
            return
        if self._should_rebuild_dialog(projection):
            self._open_dialog(projection)

    def _close_dialog(self) -> None:
        if self._dialog is None:
            self._active_projection = None
            return
        dialog = self._dialog
        self._dialog = None
        self._active_projection = None
        dialog.accepted.disconnect(self._on_dialog_accepted)
        dialog.rejected.disconnect(self._on_dialog_rejected)
        dialog.close()
        dialog.deleteLater()

    def _open_dialog(self, projection: BookmarkEditorProjection) -> None:
        self._close_dialog()
        dialog = BookmarkEditorDialog(
            self._parent,
            BookmarkEditorState(projection.url, projection.display_name, projection.tag_names, projection.initial_weight, projection.mode),
        )
        dialog.accepted.connect(self._on_dialog_accepted)
        dialog.rejected.connect(self._on_dialog_rejected)
        self._dialog = dialog
        self._active_projection = projection
        dialog.open()

    def _on_dialog_accepted(self) -> None:
        dialog = self._dialog
        if dialog is None:
            return
        self.intent_emitted.emit(RequestConfirmBookmarkEditor(dialog.url(), dialog.display_name(), tuple(dialog.tags()), dialog.initial_weight()))

    def _on_dialog_rejected(self) -> None:
        self.intent_emitted.emit(RequestCancelBookmarkEditor())

    def _should_rebuild_dialog(self, projection: BookmarkEditorProjection) -> bool:
        if self._dialog is None:
            return True
        return self._active_projection != projection
