"""File Types module tab."""
from __future__ import annotations

import uuid

from PySide2.QtCore import Qt, Signal
from PySide2.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QHeaderView,
)

from config import FileTypeEntry, FileTypesConfig


class FileTypesTab(QWidget):
    changed = Signal()

    COLS = ['Name', 'Extension', 'Description', '']
    COL_NAME = 0
    COL_EXT = 1
    COL_DESC = 2
    COL_DEL = 3

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        heading = QLabel('Allowed File Types')
        heading.setProperty('heading', True)
        layout.addWidget(heading)

        desc = QLabel('Define the file extensions that delivery packages may contain.')
        desc.setProperty('muted', True)
        layout.addWidget(desc)

        self._table = QTableWidget(0, len(self.COLS))
        self._table.setHorizontalHeaderLabels(self.COLS)
        self._table.horizontalHeader().setSectionResizeMode(self.COL_NAME, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(self.COL_EXT, QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(self.COL_DESC, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(self.COL_DEL, QHeaderView.Fixed)
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
        self._add_name.setPlaceholderText('Name (e.g. MXF Container)')
        self._add_ext = QLineEdit()
        self._add_ext.setPlaceholderText('.mxf')
        self._add_ext.setFixedWidth(90)
        self._add_ext.setStyleSheet('font-family: monospace;')
        self._add_desc = QLineEdit()
        self._add_desc.setPlaceholderText('Description (optional)')
        add_btn = QPushButton('+ Add')
        add_btn.setProperty('primary', True)
        add_btn.clicked.connect(self._add_row)

        for w in (self._add_name, self._add_ext, self._add_desc):
            w.returnPressed.connect(self._add_row)

        add_layout.addWidget(self._add_name, 2)
        add_layout.addWidget(self._add_ext)
        add_layout.addWidget(self._add_desc, 2)
        add_layout.addWidget(add_btn)
        layout.addWidget(add_frame)

    def _add_row(self):
        name = self._add_name.text().strip()
        ext = self._add_ext.text().strip()
        if not name or not ext:
            return
        desc = self._add_desc.text().strip()
        entry = FileTypeEntry(id=str(uuid.uuid4()), name=name, extension=ext, description=desc)
        self._insert_entry(entry)
        self._add_name.clear()
        self._add_ext.clear()
        self._add_desc.clear()
        self._add_name.setFocus()
        self.changed.emit()

    def _insert_entry(self, entry: FileTypeEntry):
        row = self._table.rowCount()
        self._table.insertRow(row)

        name_item = QTableWidgetItem(entry.name)
        name_item.setData(Qt.UserRole, entry.id)
        ext_item = QTableWidgetItem(entry.extension)
        ext_item.setFont(self._table.font())
        desc_item = QTableWidgetItem(entry.description)

        self._table.setItem(row, self.COL_NAME, name_item)
        self._table.setItem(row, self.COL_EXT, ext_item)
        self._table.setItem(row, self.COL_DESC, desc_item)

        del_btn = QPushButton('✕')
        del_btn.setProperty('danger', True)
        del_btn.clicked.connect(lambda _, r=row: self._remove_row_containing(del_btn))
        self._table.setCellWidget(row, self.COL_DEL, del_btn)
        self._table.setRowHeight(row, 36)

    def _remove_row_containing(self, btn: QPushButton):
        for row in range(self._table.rowCount()):
            if self._table.cellWidget(row, self.COL_DEL) is btn:
                self._table.removeRow(row)
                self.changed.emit()
                return

    def get_config(self) -> FileTypesConfig:
        entries = []
        for row in range(self._table.rowCount()):
            name_item = self._table.item(row, self.COL_NAME)
            ext_item = self._table.item(row, self.COL_EXT)
            desc_item = self._table.item(row, self.COL_DESC)
            entry_id = name_item.data(Qt.UserRole) if name_item else str(uuid.uuid4())
            entries.append(FileTypeEntry(
                id=entry_id,
                name=name_item.text() if name_item else '',
                extension=ext_item.text() if ext_item else '',
                description=desc_item.text() if desc_item else '',
            ))
        return FileTypesConfig(entries=entries)

    def set_config(self, cfg: FileTypesConfig):
        self._table.blockSignals(True)
        self._table.setRowCount(0)
        for entry in cfg.entries:
            self._insert_entry(entry)
        self._table.blockSignals(False)
