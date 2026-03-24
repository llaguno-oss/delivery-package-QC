"""Codecs module tab."""
from __future__ import annotations

import uuid

from PySide2.QtCore import Qt, Signal
from PySide2.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QComboBox, QHeaderView,
)

from config import CodecEntry, CodecsConfig
from ui.widgets.tag_input import TagInputWidget


class CodecsTab(QWidget):
    changed = Signal()

    COLS = ['Codec Name', 'Type', 'Aliases', '']
    COL_NAME = 0
    COL_KIND = 1
    COL_ALIASES = 2
    COL_DEL = 3

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        heading = QLabel('Allowed Codecs')
        heading.setProperty('heading', True)
        layout.addWidget(heading)

        desc = QLabel('Define the audio and video codecs permitted in delivery packages.')
        desc.setProperty('muted', True)
        layout.addWidget(desc)

        self._table = QTableWidget(0, len(self.COLS))
        self._table.setHorizontalHeaderLabels(self.COLS)
        self._table.horizontalHeader().setSectionResizeMode(self.COL_NAME, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(self.COL_KIND, QHeaderView.Fixed)
        self._table.horizontalHeader().setSectionResizeMode(self.COL_ALIASES, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(self.COL_DEL, QHeaderView.Fixed)
        self._table.setColumnWidth(self.COL_KIND, 90)
        self._table.setColumnWidth(self.COL_DEL, 40)
        self._table.verticalHeader().setVisible(False)
        self._table.setShowGrid(False)
        self._table.setAlternatingRowColors(True)
        self._table.itemChanged.connect(lambda _: self.changed.emit())
        layout.addWidget(self._table)

        # Add form
        add_frame = QWidget()
        add_frame.setStyleSheet(
            'background: #1a1d27; border: 1px dashed #333650; border-radius: 8px; padding: 4px;'
        )
        add_layout = QHBoxLayout(add_frame)
        add_layout.setSpacing(8)

        self._add_name = QLineEdit()
        self._add_name.setPlaceholderText('Codec name (e.g. Apple ProRes 422)')
        self._add_kind = QComboBox()
        self._add_kind.addItem('Video', 'video')
        self._add_kind.addItem('Audio', 'audio')
        self._add_kind.setFixedWidth(90)
        self._add_aliases = TagInputWidget()
        add_btn = QPushButton('+ Add')
        add_btn.setProperty('primary', True)
        add_btn.clicked.connect(self._add_row)
        self._add_name.returnPressed.connect(self._add_row)

        add_layout.addWidget(self._add_name, 2)
        add_layout.addWidget(self._add_kind)
        add_layout.addWidget(QLabel('Aliases:'))
        add_layout.addWidget(self._add_aliases, 2)
        add_layout.addWidget(add_btn)
        layout.addWidget(add_frame)

    def _add_row(self):
        name = self._add_name.text().strip()
        if not name:
            return
        kind = self._add_kind.currentData()
        aliases = self._add_aliases.get_tags()
        entry = CodecEntry(id=str(uuid.uuid4()), name=name, kind=kind, aliases=aliases)
        self._insert_entry(entry)
        self._add_name.clear()
        self._add_aliases.set_tags([])
        self._add_name.setFocus()
        self.changed.emit()

    def _insert_entry(self, entry: CodecEntry):
        row = self._table.rowCount()
        self._table.insertRow(row)

        name_item = QTableWidgetItem(entry.name)
        name_item.setData(Qt.UserRole, entry.id)
        self._table.setItem(row, self.COL_NAME, name_item)

        kind_combo = QComboBox()
        kind_combo.addItem('Video', 'video')
        kind_combo.addItem('Audio', 'audio')
        idx = kind_combo.findData(entry.kind)
        kind_combo.setCurrentIndex(idx if idx >= 0 else 0)
        kind_combo.currentIndexChanged.connect(lambda _: self.changed.emit())
        self._table.setCellWidget(row, self.COL_KIND, kind_combo)

        aliases_widget = TagInputWidget(entry.aliases)
        aliases_widget.tags_changed.connect(lambda _: self.changed.emit())
        self._table.setCellWidget(row, self.COL_ALIASES, aliases_widget)

        del_btn = QPushButton('✕')
        del_btn.setProperty('danger', True)
        del_btn.clicked.connect(lambda _, b=del_btn: self._remove_row_containing(b))
        self._table.setCellWidget(row, self.COL_DEL, del_btn)
        self._table.setRowHeight(row, 42)

    def _remove_row_containing(self, btn: QPushButton):
        for row in range(self._table.rowCount()):
            if self._table.cellWidget(row, self.COL_DEL) is btn:
                self._table.removeRow(row)
                self.changed.emit()
                return

    def get_config(self) -> CodecsConfig:
        entries = []
        for row in range(self._table.rowCount()):
            name_item = self._table.item(row, self.COL_NAME)
            kind_combo = self._table.cellWidget(row, self.COL_KIND)
            aliases_widget = self._table.cellWidget(row, self.COL_ALIASES)
            entry_id = name_item.data(Qt.UserRole) if name_item else str(uuid.uuid4())
            entries.append(CodecEntry(
                id=entry_id,
                name=name_item.text() if name_item else '',
                kind=kind_combo.currentData() if kind_combo else 'video',
                aliases=aliases_widget.get_tags() if aliases_widget else [],
            ))
        return CodecsConfig(entries=entries)

    def set_config(self, cfg: CodecsConfig):
        self._table.blockSignals(True)
        self._table.setRowCount(0)
        for entry in cfg.entries:
            self._insert_entry(entry)
        self._table.blockSignals(False)
