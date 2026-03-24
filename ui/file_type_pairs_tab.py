"""File Type Pairs module tab."""
from __future__ import annotations

import uuid

from PySide2.QtCore import Qt, Signal
from PySide2.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QHeaderView,
)

from config import FileTypePairEntry, FileTypePairsConfig


class FileTypePairsTab(QWidget):
    changed = Signal()

    COLS = ['Label', 'Primary Ext.', '→ requires', 'Companion Ext.', '']
    COL_LABEL = 0
    COL_PRIMARY = 1
    COL_ARROW = 2
    COL_COMPANION = 3
    COL_DEL = 4

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        heading = QLabel('File Type Pairs')
        heading.setProperty('heading', True)
        layout.addWidget(heading)

        desc = QLabel(
            'Define required file pairings. If the primary file exists, '
            'the companion file must also be present in the same folder.'
        )
        desc.setProperty('muted', True)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        self._table = QTableWidget(0, len(self.COLS))
        self._table.setHorizontalHeaderLabels(self.COLS)
        self._table.horizontalHeader().setSectionResizeMode(self.COL_LABEL, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(self.COL_PRIMARY, QHeaderView.Fixed)
        self._table.horizontalHeader().setSectionResizeMode(self.COL_ARROW, QHeaderView.Fixed)
        self._table.horizontalHeader().setSectionResizeMode(self.COL_COMPANION, QHeaderView.Fixed)
        self._table.horizontalHeader().setSectionResizeMode(self.COL_DEL, QHeaderView.Fixed)
        self._table.setColumnWidth(self.COL_PRIMARY, 110)
        self._table.setColumnWidth(self.COL_ARROW, 80)
        self._table.setColumnWidth(self.COL_COMPANION, 110)
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

        self._add_label = QLineEdit()
        self._add_label.setPlaceholderText('Label (optional, e.g. MXF + XML sidecar)')
        self._add_primary = QLineEdit()
        self._add_primary.setPlaceholderText('.mxf')
        self._add_primary.setFixedWidth(90)
        self._add_primary.setStyleSheet('font-family: monospace;')
        arrow_lbl = QLabel('requires')
        arrow_lbl.setProperty('muted', True)
        self._add_companion = QLineEdit()
        self._add_companion.setPlaceholderText('.xml')
        self._add_companion.setFixedWidth(90)
        self._add_companion.setStyleSheet('font-family: monospace;')
        add_btn = QPushButton('+ Add')
        add_btn.setProperty('primary', True)
        add_btn.clicked.connect(self._add_row)

        for w in (self._add_label, self._add_primary, self._add_companion):
            w.returnPressed.connect(self._add_row)

        add_layout.addWidget(self._add_label, 2)
        add_layout.addWidget(self._add_primary)
        add_layout.addWidget(arrow_lbl)
        add_layout.addWidget(self._add_companion)
        add_layout.addWidget(add_btn)
        layout.addWidget(add_frame)

    def _add_row(self):
        primary = self._add_primary.text().strip()
        companion = self._add_companion.text().strip()
        if not primary or not companion:
            return
        label = self._add_label.text().strip()
        entry = FileTypePairEntry(
            id=str(uuid.uuid4()),
            primaryExtension=primary,
            companionExtension=companion,
            label=label,
        )
        self._insert_entry(entry)
        self._add_label.clear()
        self._add_primary.clear()
        self._add_companion.clear()
        self._add_primary.setFocus()
        self.changed.emit()

    def _insert_entry(self, entry: FileTypePairEntry):
        row = self._table.rowCount()
        self._table.insertRow(row)

        label_item = QTableWidgetItem(entry.label)
        label_item.setData(Qt.UserRole, entry.id)
        primary_item = QTableWidgetItem(entry.primaryExtension)
        primary_item.setFont(self._table.font())
        arrow_item = QTableWidgetItem('→ requires')
        arrow_item.setForeground(Qt.gray)
        arrow_item.setFlags(arrow_item.flags() & ~Qt.ItemIsEditable)
        companion_item = QTableWidgetItem(entry.companionExtension)
        companion_item.setFont(self._table.font())

        self._table.setItem(row, self.COL_LABEL, label_item)
        self._table.setItem(row, self.COL_PRIMARY, primary_item)
        self._table.setItem(row, self.COL_ARROW, arrow_item)
        self._table.setItem(row, self.COL_COMPANION, companion_item)

        del_btn = QPushButton('✕')
        del_btn.setProperty('danger', True)
        del_btn.clicked.connect(lambda _, b=del_btn: self._remove_row_containing(b))
        self._table.setCellWidget(row, self.COL_DEL, del_btn)
        self._table.setRowHeight(row, 36)

    def _remove_row_containing(self, btn: QPushButton):
        for row in range(self._table.rowCount()):
            if self._table.cellWidget(row, self.COL_DEL) is btn:
                self._table.removeRow(row)
                self.changed.emit()
                return

    def get_config(self) -> FileTypePairsConfig:
        entries = []
        for row in range(self._table.rowCount()):
            label_item = self._table.item(row, self.COL_LABEL)
            primary_item = self._table.item(row, self.COL_PRIMARY)
            companion_item = self._table.item(row, self.COL_COMPANION)
            entry_id = label_item.data(Qt.UserRole) if label_item else str(uuid.uuid4())
            entries.append(FileTypePairEntry(
                id=entry_id,
                label=label_item.text() if label_item else '',
                primaryExtension=primary_item.text() if primary_item else '',
                companionExtension=companion_item.text() if companion_item else '',
            ))
        return FileTypePairsConfig(entries=entries)

    def set_config(self, cfg: FileTypePairsConfig):
        self._table.blockSignals(True)
        self._table.setRowCount(0)
        for entry in cfg.entries:
            self._insert_entry(entry)
        self._table.blockSignals(False)
