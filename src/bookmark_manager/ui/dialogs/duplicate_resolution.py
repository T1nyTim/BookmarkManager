from collections import OrderedDict
from typing import TYPE_CHECKING

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from bookmark_manager.app.intents import RequestCancelDuplicateResolution, RequestResolveDuplicateBookmark
from bookmark_manager.domain.normalization import normalize_tag

if TYPE_CHECKING:
    from bookmark_manager.app.projections import DuplicateFieldProjection, DuplicateResolutionProjection


class DuplicateResolutionDialog(QDialog):
    intent_emitted = Signal(object)

    def __init__(self, parent: QWidget, projection: DuplicateResolutionProjection) -> None:
        super().__init__(parent)
        self._projection = projection
        self.setModal(True)
        self.setWindowTitle("Resolve Duplicate Bookmark")
        self.resize(800, self.sizeHint().height())
        root_layout = QVBoxLayout(self)
        description = QLabel("That URL already exists. Choose which values to keep for each differing field.")
        description.setWordWrap(True)
        root_layout.addWidget(description)
        self._url_input = QLineEdit(projection.url)
        self._url_input.setReadOnly(True)
        root_layout.addWidget(self._build_row("URL", self._url_input))
        self._display_name_group, self._display_name_inputs = self._build_two_way_field(projection.display_name)
        root_layout.addWidget(self._display_name_group)
        self._tags_group, self._tags_input = self._build_tag_field(projection.tags)
        root_layout.addWidget(self._tags_group)
        self._initial_weight_group, self._initial_weight_inputs = self._build_two_way_field(projection.initial_weight)
        root_layout.addWidget(self._initial_weight_group)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self._on_reject)
        root_layout.addWidget(buttons)

    def _build_row(self, label: str, widget: QWidget) -> QWidget:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        label_widget = QLabel(label)
        label_widget.setMinimumWidth(120)
        layout.addWidget(label_widget)
        layout.addWidget(widget, 1)
        return container

    def _build_tag_field(self, field: DuplicateFieldProjection) -> tuple[QGroupBox, dict[str, QLineEdit]]:
        group = QGroupBox(field.label)
        layout = QGridLayout(group)
        button_group = QButtonGroup(group)
        existing_radio = QRadioButton("Keep existing")
        button_group.addButton(existing_radio)
        incoming_radio = QRadioButton("Use incoming")
        button_group.addButton(incoming_radio)
        merged_radio = QRadioButton("Merge")
        button_group.addButton(merged_radio)
        existing_input = QLineEdit(field.existing_value)
        existing_input.setReadOnly(True)
        incoming_input = QLineEdit(field.incoming_value)
        incoming_input.setReadOnly(True)
        merged_input = QLineEdit(self._merge_tags(field.existing_value, field.incoming_value))
        merged_input.setReadOnly(True)
        if field.values_match:
            existing_radio.setChecked(True)
            incoming_radio.setVisible(False)
            merged_radio.setVisible(False)
            layout.addWidget(QLabel("Values already match."), 0, 0, 1, 3)
            layout.addWidget(existing_input, 1, 0, 1, 3)
        else:
            merged_radio.setChecked(True)
            layout.addWidget(existing_radio, 0, 0)
            layout.addWidget(incoming_radio, 0, 1)
            layout.addWidget(merged_radio, 0, 2)
            layout.addWidget(existing_input, 1, 0)
            layout.addWidget(incoming_input, 1, 1)
            layout.addWidget(merged_input, 1, 2)
        group.setProperty("button_group", button_group)
        return group, {"existing": existing_input, "incoming": incoming_input, "merged": merged_input}

    def _build_two_way_field(self, field: DuplicateFieldProjection) -> tuple[QGroupBox, dict[str, QLineEdit]]:
        group = QGroupBox(field.label)
        layout = QGridLayout(group)
        button_group = QButtonGroup(group)
        existing_radio = QRadioButton("Keep existing")
        button_group.addButton(existing_radio)
        incoming_radio = QRadioButton("Use incoming")
        button_group.addButton(incoming_radio)
        existing_input = QLineEdit(field.existing_value)
        existing_input.setReadOnly(True)
        incoming_input = QLineEdit(field.incoming_value)
        incoming_input.setReadOnly(True)
        if field.values_match:
            existing_radio.setChecked(True)
            incoming_radio.setVisible(False)
            layout.addWidget(QLabel("Values already match."), 0, 0, 1, 2)
            layout.addWidget(existing_input, 1, 0, 1, 2)
        else:
            existing_radio.setChecked(True)
            layout.addWidget(existing_radio, 0, 0)
            layout.addWidget(incoming_radio, 0, 1)
            layout.addWidget(existing_input, 1, 0)
            layout.addWidget(incoming_input, 1, 1)
        group.setProperty("button_group", button_group)
        return group, {"existing": existing_input, "incoming": incoming_input}

    def _merge_tags(self, existing_value: str, incoming_value: str) -> str:
        merged = OrderedDict()
        for tag in existing_value.split():
            merged[normalize_tag(tag)] = tag
        for tag in incoming_value.split():
            merged.setdefault(normalize_tag(tag), tag)
        return " ".join(merged.values())

    def _on_accept(self) -> None:
        display_name = self._selected_text(self._display_name_group, self._display_name_inputs).strip()
        tags_text = self._selected_text(self._tags_group, self._tags_input).strip()
        initial_weight_text = self._selected_text(self._initial_weight_group, self._initial_weight_inputs).strip()
        if not tags_text:
            QMessageBox.warning(self, self.windowTitle(), "At least one tag is required.")
            return
        self.intent_emitted.emit(
            RequestResolveDuplicateBookmark(self._projection.bookmark_id, display_name, tuple(tags_text.strip()), int(initial_weight_text)),
        )
        self.accept()

    def _on_reject(self) -> None:
        self.intent_emitted.emit(RequestCancelDuplicateResolution())
        self.reject()

    def _selected_text(self, group: QGroupBox, inputs: dict[str, QLineEdit]) -> str:
        button_group = group.property("button_group")
        checked_button = button_group.checkedButton()
        text = checked_button.text()
        if text == "Keep existing":
            return inputs["existing"].text()
        if text == "Use incoming":
            return inputs["incoming"].text()
        return inputs["merged"].text()
