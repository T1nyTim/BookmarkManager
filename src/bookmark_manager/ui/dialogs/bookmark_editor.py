from dataclasses import dataclass

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QSpinBox, QVBoxLayout, QWidget

from bookmark_manager.utils.models import Mode


@dataclass(slots=True)
class BookmarkEditorState:
    url: str = ""
    display_name: str = ""
    tag_names: tuple[str, ...] = ()
    initial_weight: int = 0
    mode: Mode = Mode.ADD


class BookmarkEditorDialog(QDialog):
    def __init__(self, parent: QWidget | None = None, state: BookmarkEditorState | None = None) -> None:
        super().__init__(parent)
        if state is None:
            state = BookmarkEditorState()
        self._state = state
        self.setWindowTitle("Edit URL" if state.mode == Mode.EDIT else "Add URL")
        self.setModal(True)
        root_layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        root_layout.addLayout(form_layout)
        self._url_input = QLineEdit(state.url)
        form_layout.addRow("URL", self._url_input)
        self._display_name_input = QLineEdit(state.display_name)
        form_layout.addRow("Display Name", self._display_name_input)
        self._tags_input = QLineEdit(" ".join(state.tag_names))
        form_layout.addRow("Tags", self._tags_input)
        self._initial_weight_input = QSpinBox()
        self._initial_weight_input.setMinimum(0)
        self._initial_weight_input.setValue(state.initial_weight)
        form_layout.addRow("Initial Weight", self._initial_weight_input)
        help_row = QHBoxLayout()
        help_row.addWidget(QLabel("Tags are space-separated."))
        help_row.addStretch(1)
        root_layout.addLayout(help_row)
        self._button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self._button_box.accepted.connect(self._on_accept_clicked)
        self._button_box.rejected.connect(self.reject)
        root_layout.addWidget(self._button_box)
        if state.mode == Mode.EDIT:
            self._url_input.setReadOnly(True)
        self._url_input.selectAll()
        self._url_input.setFocus()

    def display_name(self) -> str:
        return self._display_name_input.text().strip()

    def initial_weight(self) -> int:
        return self._initial_weight_input.value()

    def tags(self) -> list[str]:
        return self._tags_input.text().split()

    def url(self) -> str:
        return self._url_input.text().strip()

    def _on_accept_clicked(self) -> None:
        if not self.url():
            self._show_validation_error("URL is required.")
            return
        if not self.display_name():
            self._show_validation_error("Display Name is required.")
            return
        if not self.tags():
            self._show_validation_error("At least one tag is required.")
            return
        self.accept()

    def _show_validation_error(self, message: str) -> None:
        QMessageBox.warning(self, self.windowTitle(), message)
