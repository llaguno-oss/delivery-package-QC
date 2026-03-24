"""Core config widget: filename blocks + allowed resolutions."""
from __future__ import annotations

import uuid
from typing import List

from PySide2.QtCore import Qt, Signal
from PySide2.QtGui import QColor
from PySide2.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QLineEdit, QComboBox, QFrame,
    QSizePolicy, QScrollArea,
)

from config import FilenameBlock, CoreConfig
from ui.theme import BLOCK_CHIP_COLORS
from ui.widgets.tag_input import TagInputWidget


# ─── Filename block row widget ────────────────────────────────────────────────

class FilenameBlockRow(QWidget):
    changed = Signal()
    remove_requested = Signal(str)  # emits block id

    TYPES = ['token', 'fixed', 'list', 'wildcard']
    SEPARATORS = [('_', '_'), ('.', '.'), ('-', '-'), ('', 'none')]

    def __init__(self, block: FilenameBlock, parent=None):
        super().__init__(parent)
        self._block = block
        self._setup_ui()
        self._load(block)

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        # Drag handle label (visual only – QListWidget handles drag)
        handle = QLabel('⠿')
        handle.setFixedWidth(16)
        handle.setStyleSheet('color: #555c7a; font-size: 14px;')
        handle.setCursor(Qt.SizeVerCursor)
        layout.addWidget(handle)

        # Label
        self._label_edit = QLineEdit()
        self._label_edit.setPlaceholderText('label')
        self._label_edit.setFixedWidth(110)
        self._label_edit.textChanged.connect(self._on_change)
        layout.addWidget(self._label_edit)

        # Type
        self._type_combo = QComboBox()
        for t in self.TYPES:
            self._type_combo.addItem(t.capitalize(), t)
        self._type_combo.setFixedWidth(100)
        self._type_combo.currentIndexChanged.connect(self._on_type_change)
        layout.addWidget(self._type_combo)

        # Dynamic value area
        self._value_stack = QWidget()
        self._value_stack.setMinimumWidth(180)
        self._value_stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        vs_layout = QHBoxLayout(self._value_stack)
        vs_layout.setContentsMargins(0, 0, 0, 0)
        vs_layout.setSpacing(0)

        self._fixed_input = QLineEdit()
        self._fixed_input.setPlaceholderText('fixed value')
        self._fixed_input.textChanged.connect(self._on_change)
        vs_layout.addWidget(self._fixed_input)

        self._list_input = TagInputWidget()
        self._list_input.tags_changed.connect(lambda _: self._on_change())
        vs_layout.addWidget(self._list_input)

        self._badge_label = QLabel()
        self._badge_label.setStyleSheet('font-size: 11px; padding: 2px 8px; border-radius: 4px;')
        vs_layout.addWidget(self._badge_label)

        layout.addWidget(self._value_stack, 1)

        # Separator
        self._sep_combo = QComboBox()
        for val, label in self.SEPARATORS:
            self._sep_combo.addItem(label, val)
        self._sep_combo.setFixedWidth(70)
        self._sep_combo.currentIndexChanged.connect(self._on_change)
        layout.addWidget(self._sep_combo)

        # Delete button
        self._del_btn = QPushButton('✕')
        self._del_btn.setProperty('danger', True)
        self._del_btn.setFixedSize(28, 28)
        self._del_btn.clicked.connect(lambda: self.remove_requested.emit(self._block.id))
        layout.addWidget(self._del_btn)

    def _load(self, block: FilenameBlock):
        self._label_edit.setText(block.label)

        idx = self._type_combo.findData(block.type)
        self._type_combo.setCurrentIndex(idx if idx >= 0 else 0)

        self._fixed_input.setText(block.value or '')
        self._list_input.set_tags(block.values or [])

        sep_idx = self._sep_combo.findData(block.separator)
        self._sep_combo.setCurrentIndex(sep_idx if sep_idx >= 0 else 0)

        self._update_dynamic_field(block.type)

    def _update_dynamic_field(self, block_type: str):
        self._fixed_input.setVisible(block_type == 'fixed')
        self._list_input.setVisible(block_type == 'list')
        self._badge_label.setVisible(block_type in ('token', 'wildcard'))

        if block_type == 'wildcard':
            fg, bg, border = BLOCK_CHIP_COLORS['wildcard']
            label_text = '* (any)'
        elif block_type == 'token':
            fg, bg, border = BLOCK_CHIP_COLORS['token']
            label_text = f'{{{self._label_edit.text() or "token"}}}'
        else:
            fg, bg, border = '#e8eaf0', '#252836', '#333650'
            label_text = ''

        self._badge_label.setText(label_text)
        self._badge_label.setStyleSheet(
            f'font-size: 11px; font-family: monospace; padding: 2px 10px; border-radius: 4px;'
            f' color: {fg}; background: {bg}; border: 1px solid {border};'
        )

    def _on_type_change(self):
        t = self._type_combo.currentData()
        self._update_dynamic_field(t)
        self._on_change()

    def _on_change(self):
        t = self._type_combo.currentData()
        if t == 'token':
            self._update_dynamic_field(t)  # refresh badge text
        self.changed.emit()

    def get_block(self) -> FilenameBlock:
        b = self._block
        b.label = self._label_edit.text()
        b.type = self._type_combo.currentData()
        b.value = self._fixed_input.text()
        b.values = self._list_input.get_tags()
        b.separator = self._sep_combo.currentData()
        return b


# ─── Filename blocks section ──────────────────────────────────────────────────

class FilenameBlocksWidget(QWidget):
    changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rows: dict[str, FilenameBlockRow] = {}  # block_id → row widget
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Heading
        heading = QLabel('Filename Blocks')
        heading.setProperty('heading', True)
        layout.addWidget(heading)

        desc = QLabel('Define the ordered segments of a valid filename. Drag rows to reorder.')
        desc.setProperty('muted', True)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Live preview
        self._preview_label = QLabel('Add blocks below to see a preview')
        self._preview_label.setWordWrap(True)
        self._preview_label.setTextFormat(Qt.RichText)
        self._preview_label.setStyleSheet(
            'background: #1a1d27; border: 1px solid #333650; border-radius: 6px;'
            ' padding: 8px 12px; min-height: 36px;'
        )
        layout.addWidget(self._preview_label)

        # Legend
        legend_row = QHBoxLayout()
        legend_row.setSpacing(8)
        legend_label = QLabel('Types:')
        legend_label.setProperty('muted', True)
        legend_row.addWidget(legend_label)
        for btype, (fg, bg, border) in BLOCK_CHIP_COLORS.items():
            chip = QLabel(btype)
            chip.setStyleSheet(
                f'font-size: 11px; font-family: monospace; padding: 1px 8px; border-radius: 4px;'
                f' color: {fg}; background: {bg}; border: 1px solid {border};'
            )
            legend_row.addWidget(chip)
        legend_row.addStretch()
        layout.addLayout(legend_row)

        # Column headers
        col_header = QWidget()
        col_header.setStyleSheet('background: #1a1d27; border-radius: 4px;')
        ch_layout = QHBoxLayout(col_header)
        ch_layout.setContentsMargins(32, 4, 8, 4)
        ch_layout.setSpacing(8)
        for text, width in [('Label', 110), ('Type', 100), ('Value / Options', 0), ('Sep.', 70), ('', 28)]:
            lbl = QLabel(text)
            lbl.setStyleSheet('color: #555c7a; font-size: 11px; font-weight: 600; text-transform: uppercase;')
            if width:
                lbl.setFixedWidth(width)
            else:
                lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            ch_layout.addWidget(lbl)
        layout.addWidget(col_header)

        # Block list (drag to reorder)
        self._list = QListWidget()
        self._list.setDragDropMode(QListWidget.InternalMove)
        self._list.setDefaultDropAction(Qt.MoveAction)
        self._list.setSelectionMode(QListWidget.SingleSelection)
        self._list.setSpacing(2)
        self._list.setMinimumHeight(80)
        self._list.model().rowsMoved.connect(self._on_reorder)
        layout.addWidget(self._list)

        # Add block button
        add_btn = QPushButton('+ Add Block')
        add_btn.clicked.connect(self._add_block)
        layout.addWidget(add_btn)

    def _add_block(self):
        block = FilenameBlock(
            id=str(uuid.uuid4()),
            type='token',
            label='segment',
            separator='_',
        )
        self._add_row(block)
        self._update_preview()
        self.changed.emit()

    def _add_row(self, block: FilenameBlock):
        row_widget = FilenameBlockRow(block)
        row_widget.changed.connect(self._update_preview)
        row_widget.changed.connect(self.changed)
        row_widget.remove_requested.connect(self._remove_block)

        item = QListWidgetItem(self._list)
        item.setSizeHint(row_widget.sizeHint())
        item.setData(Qt.UserRole, block.id)
        self._list.addItem(item)
        self._list.setItemWidget(item, row_widget)
        self._rows[block.id] = row_widget

    def _remove_block(self, block_id: str):
        for i in range(self._list.count()):
            item = self._list.item(i)
            if item.data(Qt.UserRole) == block_id:
                self._list.takeItem(i)
                self._rows.pop(block_id, None)
                break
        self._update_preview()
        self.changed.emit()

    def _on_reorder(self):
        self._update_preview()
        self.changed.emit()

    def _update_preview(self):
        blocks = self.get_blocks()
        if not blocks:
            self._preview_label.setText(
                '<span style="color:#555c7a; font-style:italic;">Add blocks below to see a preview</span>'
            )
            return

        parts = []
        for i, block in enumerate(blocks):
            fg, bg, border = BLOCK_CHIP_COLORS.get(block.type, ('#e8eaf0', '#252836', '#333650'))
            if block.type == 'fixed':
                text = block.value or block.label
            elif block.type == 'list':
                text = '|'.join(block.values) if block.values else block.label
            elif block.type == 'wildcard':
                text = '*'
            else:
                text = f'{{{block.label}}}'
            chip_html = (
                f'<span style="color:{fg}; background:{bg}; border:1px solid {border};'
                f' border-radius:4px; padding:1px 6px; font-family:monospace; font-size:12px;">'
                f'{text}</span>'
            )
            parts.append(chip_html)
            if i < len(blocks) - 1 and block.separator:
                parts.append(
                    f'<span style="color:#555c7a; font-family:monospace;">{block.separator}</span>'
                )
        self._preview_label.setText(' '.join(parts))

    # ── Public API ─────────────────────────────────────────────────────────────

    def get_blocks(self) -> List[FilenameBlock]:
        result = []
        for i in range(self._list.count()):
            item = self._list.item(i)
            block_id = item.data(Qt.UserRole)
            row = self._rows.get(block_id)
            if row:
                result.append(row.get_block())
        return result

    def set_blocks(self, blocks: List[FilenameBlock]):
        self._list.clear()
        self._rows.clear()
        for block in blocks:
            self._add_row(block)
        self._update_preview()


# ─── Resolutions section ──────────────────────────────────────────────────────

RESOLUTION_PRESETS = ['1920x1080', '1280x720', '3840x2160', '4096x2160', '720x576', '720x486']


class ResolutionListWidget(QWidget):
    changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._resolutions: list[str] = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        heading = QLabel('Allowed Resolutions')
        heading.setProperty('heading', True)
        layout.addWidget(heading)

        desc = QLabel('Define the resolutions permitted in delivery packages (e.g. 1920x1080).')
        desc.setProperty('muted', True)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Current resolution chips
        self._chips_area = QWidget()
        self._chips_layout = QHBoxLayout(self._chips_area)
        self._chips_layout.setContentsMargins(0, 0, 0, 0)
        self._chips_layout.setSpacing(6)
        self._chips_layout.addStretch()
        self._empty_label = QLabel('No resolutions defined.')
        self._empty_label.setProperty('muted', True)
        self._chips_layout.insertWidget(0, self._empty_label)
        layout.addWidget(self._chips_area)

        # Quick presets
        preset_row = QHBoxLayout()
        preset_row.setSpacing(6)
        ql = QLabel('Quick add:')
        ql.setProperty('muted', True)
        preset_row.addWidget(ql)
        self._preset_buttons: dict[str, QPushButton] = {}
        for p in RESOLUTION_PRESETS:
            btn = QPushButton(f'+ {p}')
            btn.setProperty('flat', True)
            btn.setStyleSheet(
                'QPushButton { font-family: monospace; font-size: 11px;'
                ' border: 1px dashed #333650; border-radius: 4px; padding: 2px 8px;'
                ' color: #8b90a7; background: transparent; }'
                'QPushButton:hover { border-color: #4f6ef7; color: #4f6ef7; }'
            )
            btn.clicked.connect(lambda _, res=p: self._add_resolution(res))
            preset_row.addWidget(btn)
            self._preset_buttons[p] = btn
        preset_row.addStretch()
        layout.addLayout(preset_row)

        # Custom input
        input_row = QHBoxLayout()
        input_row.setSpacing(8)
        self._input = QLineEdit()
        self._input.setPlaceholderText('Custom resolution (e.g. 2048x1556)')
        self._input.setFixedWidth(260)
        self._input.returnPressed.connect(self._add_from_input)
        input_row.addWidget(self._input)
        add_btn = QPushButton('Add')
        add_btn.setProperty('primary', True)
        add_btn.clicked.connect(self._add_from_input)
        input_row.addWidget(add_btn)
        input_row.addStretch()
        layout.addLayout(input_row)

    def _add_from_input(self):
        text = self._input.text().strip()
        if text:
            self._add_resolution(text)
            self._input.clear()

    def _add_resolution(self, res: str):
        if res and res not in self._resolutions:
            self._resolutions.append(res)
            self._rebuild_chips()
            self.changed.emit()

    def _remove_resolution(self, res: str):
        if res in self._resolutions:
            self._resolutions.remove(res)
            self._rebuild_chips()
            self.changed.emit()

    def _rebuild_chips(self):
        while self._chips_layout.count() > 0:
            item = self._chips_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self._resolutions:
            empty = QLabel('No resolutions defined.')
            empty.setProperty('muted', True)
            self._chips_layout.addWidget(empty)
        else:
            for res in self._resolutions:
                chip = QPushButton(f'{res}  ✕')
                chip.setStyleSheet(
                    'QPushButton { background: #252836; border: 1px solid #333650; border-radius: 6px;'
                    '  color: #e8eaf0; font-family: monospace; padding: 4px 10px; }'
                    'QPushButton:hover { border-color: #ff6666; color: #ff9999;'
                    '  background: rgba(255,102,102,0.1); }'
                )
                chip.clicked.connect(lambda _, r=res: self._remove_resolution(r))
                self._chips_layout.addWidget(chip)

        self._chips_layout.addStretch()

        # Update preset button visibility
        for res, btn in self._preset_buttons.items():
            btn.setVisible(res not in self._resolutions)

    # ── Public API ─────────────────────────────────────────────────────────────

    def get_resolutions(self) -> list[str]:
        return list(self._resolutions)

    def set_resolutions(self, resolutions: list[str]):
        self._resolutions = list(resolutions)
        self._rebuild_chips()


# ─── Composite core config widget ─────────────────────────────────────────────

class CoreConfigWidget(QWidget):
    changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(0)

        self._blocks_widget = FilenameBlocksWidget()
        self._blocks_widget.changed.connect(self.changed)
        layout.addWidget(self._blocks_widget)

        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet('color: #333650; margin: 24px 0;')
        layout.addWidget(divider)

        self._resolution_widget = ResolutionListWidget()
        self._resolution_widget.changed.connect(self.changed)
        layout.addWidget(self._resolution_widget)

        layout.addStretch()

    def get_core_config(self) -> CoreConfig:
        return CoreConfig(
            filenameBlocks=self._blocks_widget.get_blocks(),
            allowedResolutions=self._resolution_widget.get_resolutions(),
        )

    def set_core_config(self, core: CoreConfig):
        self._blocks_widget.set_blocks(core.filenameBlocks)
        self._resolution_widget.set_resolutions(core.allowedResolutions)
