"""Naming Pattern module tab."""
from __future__ import annotations

import re
import uuid

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QHeaderView,
)

from config import NamingPatternEntry, NamingPatternsConfig


def _is_valid_regex(pattern: str) -> bool:
    try:
        re.compile(pattern)
        return True
    except re.error:
        return False


class NamingPatternTab(QWidget):
    changed = Signal()

    COLS = ['Name', 'Pattern (regex)', 'Description', '']
    COL_NAME = 0
    COL_PATTERN = 1
    COL_DESC = 2
    COL_DEL = 3

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        heading = QLabel('Naming Patterns')
        heading.setProperty('heading', True)
        layout.addWidget(heading)

        desc = QLabel('Define regular expressions that delivery package filenames must match.')
        desc.setProperty('muted', True)
        layout.addWidget(desc)

        self._table = QTableWidget(0, len(self.COLS))
        self._table.setHorizontalHeaderLabels(self.COLS)
        self._table.horizontalHeader().setSectionResizeMode(self.COL_NAME, QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(self.COL_PATTERN, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(self.COL_DESC, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(self.COL_DEL, QHeaderView.Fixed)
        self._table.setColumnWidth(self.COL_DEL, 40)
        self._table.verticalHeader().setVisible(False)
        self._table.setShowGrid(False)
        self._table.setAlternatingRowColors(True)
        self._table.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self._table)

        # Add form
        add_frame = QWidget()
        add_frame.setStyleSheet(
            'background: #1a1d27; border: 1px dashed #333650; border-radius: 8px; padding: 4px;'
        )
        add_layout = QHBoxLayout(add_frame)
        add_layout.setSpacing(8)

        self._add_name = QLineEdit()
        self._add_name.setPlaceholderText('Pattern name')
        self._add_name.setFixedWidth(160)
        self._add_pattern = QLineEdit()
        self._add_pattern.setPlaceholderText(r'^[A-Z]{3,6}_\d{4}.*$')
        self._add_pattern.setStyleSheet('font-family: monospace; font-size: 12px;')
        self._add_pattern.textChanged.connect(self._validate_add_pattern)
        self._add_desc = QLineEdit()
        self._add_desc.setPlaceholderText('Description (optional)')
        self._add_error = QLabel()
        self._add_error.setStyleSheet('color: #ff6666; font-size: 11px;')
        add_btn = QPushButton('+ Add')
        add_btn.setProperty('primary', True)
        add_btn.clicked.connect(self._add_row)

        for w in (self._add_name, self._add_pattern, self._add_desc):
            w.returnPressed.connect(self._add_row)

        add_layout.addWidget(self._add_name)
        add_layout.addWidget(self._add_pattern, 2)
        add_layout.addWidget(self._add_error)
        add_layout.addWidget(self._add_desc, 1)
        add_layout.addWidget(add_btn)
        layout.addWidget(add_frame)

    def _validate_add_pattern(self):
        pattern = self._add_pattern.text()
        if pattern and not _is_valid_regex(pattern):
            self._add_error.setText('Invalid regex')
            self._add_pattern.setProperty('invalid', True)
        else:
            self._add_error.setText('')
            self._add_pattern.setProperty('invalid', False)
        self._add_pattern.style().unpolish(self._add_pattern)
        self._add_pattern.style().polish(self._add_pattern)

    def _add_row(self):
        name = self._add_name.text().strip()
        pattern = self._add_pattern.text().strip()
        if not name or not pattern or not _is_valid_regex(pattern):
            return
        desc = self._add_desc.text().strip()
        entry = NamingPatternEntry(
            id=str(uuid.uuid4()), name=name, pattern=pattern, description=desc
        )
        self._insert_entry(entry)
        self._add_name.clear()
        self._add_pattern.clear()
        self._add_desc.clear()
        self._add_name.setFocus()
        self.changed.emit()

    def _insert_entry(self, entry: NamingPatternEntry):
        row = self._table.rowCount()
        self._table.insertRow(row)

        name_item = QTableWidgetItem(entry.name)
        name_item.setData(Qt.UserRole, entry.id)

        pattern_item = QTableWidgetItem(entry.pattern)
        pattern_item.setFont(self._table.font())
        if not _is_valid_regex(entry.pattern):
            pattern_item.setForeground(QColor('#ff6666'))
            pattern_item.setToolTip('Invalid regular expression')

        desc_item = QTableWidgetItem(entry.description)

        self._table.setItem(row, self.COL_NAME, name_item)
        self._table.setItem(row, self.COL_PATTERN, pattern_item)
        self._table.setItem(row, self.COL_DESC, desc_item)

        del_btn = QPushButton('✕')
        del_btn.setProperty('danger', True)
        del_btn.clicked.connect(lambda _, b=del_btn: self._remove_row_containing(b))
        self._table.setCellWidget(row, self.COL_DEL, del_btn)
        self._table.setRowHeight(row, 36)

    def _on_item_changed(self, item: QTableWidgetItem):
        if item.column() == self.COL_PATTERN:
            if _is_valid_regex(item.text()):
                item.setForeground(QColor('#e8eaf0'))
                item.setToolTip('')
            else:
                item.setForeground(QColor('#ff6666'))
                item.setToolTip('Invalid regular expression')
        self.changed.emit()

    def _remove_row_containing(self, btn: QPushButton):
        for row in range(self._table.rowCount()):
            if self._table.cellWidget(row, self.COL_DEL) is btn:
                self._table.removeRow(row)
                self.changed.emit()
                return

    def get_config(self) -> NamingPatternsConfig:
        entries = []
        for row in range(self._table.rowCount()):
            name_item = self._table.item(row, self.COL_NAME)
            pattern_item = self._table.item(row, self.COL_PATTERN)
            desc_item = self._table.item(row, self.COL_DESC)
            entry_id = name_item.data(Qt.UserRole) if name_item else str(uuid.uuid4())
            entries.append(NamingPatternEntry(
                id=entry_id,
                name=name_item.text() if name_item else '',
                pattern=pattern_item.text() if pattern_item else '',
                description=desc_item.text() if desc_item else '',
            ))
        return NamingPatternsConfig(entries=entries)

    def set_config(self, cfg: NamingPatternsConfig):
        self._table.blockSignals(True)
        self._table.setRowCount(0)
        for entry in cfg.entries:
            self._insert_entry(entry)
        self._table.blockSignals(False)
