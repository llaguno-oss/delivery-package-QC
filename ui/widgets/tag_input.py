"""Tag chip input widget."""
from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QLineEdit, QSizePolicy, QScrollArea,
)
from PySide6.QtCore import Qt


class TagInputWidget(QWidget):
    """Displays tags as chips with × buttons; Enter/comma in the input adds a new tag."""

    tags_changed = Signal(list)

    def __init__(self, tags: list[str] | None = None, parent=None):
        super().__init__(parent)
        self._tags: list[str] = list(tags or [])
        self._setup_ui()

    def _setup_ui(self):
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Scrollable chip area
        self._scroll = QScrollArea()
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setWidgetResizable(True)
        self._scroll.setFixedHeight(34)
        self._scroll.setStyleSheet(
            'QScrollArea { border: 1px solid #333650; border-radius: 6px; background: #252836; }'
        )

        self._chip_widget = QWidget()
        self._chip_widget.setStyleSheet('background: transparent;')
        self._chip_layout = QHBoxLayout(self._chip_widget)
        self._chip_layout.setContentsMargins(4, 2, 4, 2)
        self._chip_layout.setSpacing(4)
        self._chip_layout.addStretch()

        self._scroll.setWidget(self._chip_widget)

        # Input
        self._input = QLineEdit()
        self._input.setPlaceholderText('Add…')
        self._input.setFixedHeight(34)
        self._input.setMinimumWidth(80)
        self._input.setMaximumWidth(140)
        self._input.returnPressed.connect(self._commit_input)
        self._input.textChanged.connect(self._on_text_changed)

        outer.addWidget(self._scroll, 1)
        outer.addSpacing(4)
        outer.addWidget(self._input)

        self._rebuild_chips()

    def _on_text_changed(self, text: str):
        if text.endswith(','):
            self._commit_input()

    def _commit_input(self):
        text = self._input.text().strip().rstrip(',').strip()
        if text and text not in self._tags:
            self._tags.append(text)
            self._input.clear()
            self._rebuild_chips()
            self.tags_changed.emit(list(self._tags))

    def _rebuild_chips(self):
        # Remove all chip buttons (leave the stretch)
        while self._chip_layout.count() > 1:
            item = self._chip_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for tag in self._tags:
            chip = QPushButton(f'{tag}  ×')
            chip.setFixedHeight(22)
            chip.setStyleSheet(
                'QPushButton { background: #2e3245; border: 1px solid #444966; border-radius: 4px;'
                '  color: #e8eaf0; font-size: 11px; padding: 1px 8px; }'
                'QPushButton:hover { background: rgba(255,102,102,0.15); border-color: #ff6666;'
                '  color: #ff9999; }'
            )
            tag_copy = tag
            chip.clicked.connect(lambda _, t=tag_copy: self._remove_tag(t))
            self._chip_layout.insertWidget(self._chip_layout.count() - 1, chip)

    def _remove_tag(self, tag: str):
        if tag in self._tags:
            self._tags.remove(tag)
            self._rebuild_chips()
            self.tags_changed.emit(list(self._tags))

    # ── Public API ────────────────────────────────────────────────────────────

    def get_tags(self) -> list[str]:
        return list(self._tags)

    def set_tags(self, tags: list[str]):
        self._tags = list(tags)
        self._rebuild_chips()
