"""Module manager tab — toggle which optional modules are enabled."""
from __future__ import annotations

from ui.compat import (
    Qt, Signal,
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame,
    Qt_PointingHandCursor, Qt_RichText,
)

from config import QCConfig

# Module metadata
MODULE_INFO = [
    {
        'id': 'fileTypes',
        'label': 'File Types',
        'description': 'Define allowed file extensions (.mxf, .mov, .mp4, …)',
        'icon': '📄',
    },
    {
        'id': 'codecs',
        'label': 'Codecs',
        'description': 'Define allowed audio and video codecs with optional aliases.',
        'icon': '🎞',
    },
    {
        'id': 'fileTypePairs',
        'label': 'File Type Pairs',
        'description': 'Require companion sidecar files alongside primary files.',
        'icon': '🔗',
    },
    {
        'id': 'namingPattern',
        'label': 'Naming Patterns',
        'description': 'Validate filenames against one or more regular expressions.',
        'icon': '🔤',
    },
]


class ModuleToggleCard(QFrame):
    toggled = Signal(str, bool)  # module_id, enabled

    def __init__(self, module_id: str, label: str, description: str,
                 icon: str, enabled: bool, parent=None):
        super().__init__(parent)
        self._module_id = module_id
        self._enabled = enabled
        self._setup_ui(label, description, icon)
        self._update_style()

    def _setup_ui(self, label: str, description: str, icon: str):
        self.setFixedHeight(90)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        icon_label = QLabel(icon)
        icon_label.setStyleSheet('font-size: 22px;')
        icon_label.setFixedWidth(32)
        layout.addWidget(icon_label)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        self._title_label = QLabel(label)
        self._title_label.setStyleSheet('font-weight: 600; font-size: 13px;')
        desc_label = QLabel(description)
        desc_label.setStyleSheet('color: #8b90a7; font-size: 11px;')
        desc_label.setWordWrap(True)
        text_layout.addWidget(self._title_label)
        text_layout.addWidget(desc_label)
        layout.addLayout(text_layout, 1)

        # Toggle button
        self._toggle_btn = QLabel()
        self._toggle_btn.setFixedSize(44, 24)
        self._toggle_btn.setCursor(Qt_PointingHandCursor)
        layout.addWidget(self._toggle_btn)
        self.mousePressEvent = self._on_click

    def _on_click(self, event):
        self._enabled = not self._enabled
        self._update_style()
        self.toggled.emit(self._module_id, self._enabled)

    def _update_style(self):
        if self._enabled:
            self.setStyleSheet(
                'ModuleToggleCard { border: 1px solid #4f6ef7; border-radius: 10px;'
                ' background: rgba(79,110,247,0.1); }'
            )
            self._toggle_btn.setStyleSheet(
                'background: #4f6ef7; border-radius: 12px; border: none;'
            )
            self._toggle_btn.setText(
                '<span style="color:white; font-size:10px; padding-left:22px;">ON</span>'
            )
            self._toggle_btn.setTextFormat(Qt_RichText)
        else:
            self.setStyleSheet(
                'ModuleToggleCard { border: 1px solid #333650; border-radius: 10px;'
                ' background: #1a1d27; }'
            )
            self.setStyleSheet(
                'QFrame { border: 1px solid #333650; border-radius: 10px; background: #1a1d27; }'
            )
            self._toggle_btn.setStyleSheet(
                'background: #333650; border-radius: 12px; border: none;'
            )
            self._toggle_btn.setText(
                '<span style="color:#8b90a7; font-size:10px; padding-left:4px;">OFF</span>'
            )
            self._toggle_btn.setTextFormat(Qt_RichText)

    def set_enabled(self, enabled: bool):
        self._enabled = enabled
        self._update_style()

    def is_enabled(self) -> bool:
        return self._enabled


class ModuleManagerTab(QWidget):
    modules_changed = Signal(list)  # emits list of enabled module ids

    def __init__(self, parent=None):
        super().__init__(parent)
        self._cards: dict[str, ModuleToggleCard] = {}
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        heading = QLabel('Extra Parameter Modules')
        heading.setProperty('heading', True)
        layout.addWidget(heading)

        desc = QLabel(
            'Enable additional configuration tabs for scanning specific package parameters. '
            'Click a card to toggle.'
        )
        desc.setProperty('muted', True)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        grid = QGridLayout()
        grid.setSpacing(12)

        for i, info in enumerate(MODULE_INFO):
            card = ModuleToggleCard(
                module_id=info['id'],
                label=info['label'],
                description=info['description'],
                icon=info['icon'],
                enabled=False,
            )
            card.toggled.connect(self._on_toggle)
            self._cards[info['id']] = card
            grid.addWidget(card, i // 2, i % 2)

        layout.addLayout(grid)
        layout.addStretch()

    def _on_toggle(self, module_id: str, enabled: bool):
        enabled_modules = [mid for mid, card in self._cards.items() if card.is_enabled()]
        self.modules_changed.emit(enabled_modules)

    def get_enabled_modules(self) -> list[str]:
        return [mid for mid, card in self._cards.items() if card.is_enabled()]

    def set_enabled_modules(self, module_ids: list[str]):
        for mid, card in self._cards.items():
            card.set_enabled(mid in module_ids)
