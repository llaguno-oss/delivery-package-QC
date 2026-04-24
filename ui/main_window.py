"""Main application window."""
from __future__ import annotations

import json
from pathlib import Path

from ui.compat import (
    Qt,
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTabWidget, QFileDialog,
    QMessageBox, QScrollArea, QFrame,
)

from config import QCConfig, default_config, load_config, save_config, config_to_dict, validate_config, config_from_dict
from ui.core_config import CoreConfigWidget
from ui.file_types_tab import FileTypesTab
from ui.codecs_tab import CodecsTab
from ui.file_type_pairs_tab import FileTypePairsTab
from ui.naming_pattern_tab import NamingPatternTab
from ui.module_manager import ModuleManagerTab
from ui.scan_tab import ScanTab

# Default path for auto-save
DEFAULT_CONFIG_PATH = Path('qc_config.json')

# Tab indices (before dynamic module tabs)
_TAB_CORE = 0


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._config = default_config()
        self._config_path: Path | None = None
        self._module_tab_indices: dict[str, int] = {}

        # Tab widget references
        self._core_tab: CoreConfigWidget | None = None
        self._ft_tab: FileTypesTab | None = None
        self._co_tab: CodecsTab | None = None
        self._fp_tab: FileTypePairsTab | None = None
        self._np_tab: NamingPatternTab | None = None

        self._setup_ui()
        self._load_default_config()

    def _setup_ui(self):
        self.setWindowTitle('Delivery Package QC')
        self.setMinimumSize(1100, 700)
        self.resize(1200, 780)

        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── Header ──────────────────────────────────────────────────────────
        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet('background: #1a1d27; border-bottom: 1px solid #333650;')
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(20, 0, 20, 0)
        h_layout.setSpacing(12)

        # App icon + title
        icon_label = QLabel('📦')
        icon_label.setStyleSheet('font-size: 22px;')
        title_label = QLabel('Delivery Package QC')
        title_label.setStyleSheet('font-size: 15px; font-weight: 700; color: #e8eaf0;')
        sub_label = QLabel('Package scan configuration')
        sub_label.setStyleSheet('font-size: 11px; color: #8b90a7;')

        title_vl = QVBoxLayout()
        title_vl.setSpacing(1)
        title_vl.addWidget(title_label)
        title_vl.addWidget(sub_label)

        h_layout.addWidget(icon_label)
        h_layout.addLayout(title_vl)
        h_layout.addStretch()

        # Buttons
        for label, slot in [
            ('Import', self._import_config),
            ('Export', self._export_config),
            ('Save', self._save_config),
        ]:
            btn = QPushButton(label)
            btn.clicked.connect(slot)
            h_layout.addWidget(btn)

        div = QFrame()
        div.setFrameShape(QFrame.VLine)
        div.setStyleSheet('color: #333650;')
        h_layout.addWidget(div)

        reset_btn = QPushButton('Reset')
        reset_btn.clicked.connect(self._reset_config)
        h_layout.addWidget(reset_btn)

        root_layout.addWidget(header)

        # ── Tab widget ───────────────────────────────────────────────────────
        self._tabs = QTabWidget()
        self._tabs.setTabPosition(QTabWidget.North)
        self._tabs.setDocumentMode(True)
        root_layout.addWidget(self._tabs, 1)

        # Core Config (always present, always index 0)
        self._core_tab = CoreConfigWidget()
        self._core_tab.changed.connect(self._on_config_changed)
        scroll = self._make_scroll(self._core_tab)
        self._tabs.addTab(scroll, 'Core Config')

        # Module manager tab (always present)
        self._module_mgr = ModuleManagerTab()
        self._module_mgr.modules_changed.connect(self._on_modules_changed)
        self._tabs.addTab(self._module_mgr, '⚙  Modules')

        # Scan tab (always present, always rightmost)
        self._scan_tab = ScanTab(get_config=self._collect_config)
        self._tabs.addTab(self._scan_tab, '▶  Scan')

    def _make_scroll(self, widget: QWidget) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidget(widget)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        return scroll

    # ── Module tab management ─────────────────────────────────────────────────

    def _on_modules_changed(self, enabled_ids: list[str]):
        """Add/remove module tabs based on enabled_ids."""
        # Remove all existing module tabs (between core and modules mgr)
        while self._tabs.count() > 3:  # core + modules + scan
            self._tabs.removeTab(1)
        self._module_tab_indices.clear()

        # Re-init tab widgets if needed
        if self._ft_tab is None:
            self._ft_tab = FileTypesTab()
            self._ft_tab.changed.connect(self._on_config_changed)
        if self._co_tab is None:
            self._co_tab = CodecsTab()
            self._co_tab.changed.connect(self._on_config_changed)
        if self._fp_tab is None:
            self._fp_tab = FileTypePairsTab()
            self._fp_tab.changed.connect(self._on_config_changed)
        if self._np_tab is None:
            self._np_tab = NamingPatternTab()
            self._np_tab.changed.connect(self._on_config_changed)

        MODULE_TABS = {
            'fileTypes':    ('File Types',    self._ft_tab),
            'codecs':       ('Codecs',         self._co_tab),
            'fileTypePairs':('File Pairs',     self._fp_tab),
            'namingPattern':('Naming',         self._np_tab),
        }

        insert_at = 1  # after Core Config, before Modules+Scan
        for mid in ['fileTypes', 'codecs', 'fileTypePairs', 'namingPattern']:
            if mid in enabled_ids:
                label, widget = MODULE_TABS[mid]
                scroll = self._make_scroll(widget)
                self._tabs.insertTab(insert_at, scroll, label)
                self._module_tab_indices[mid] = insert_at
                insert_at += 1

    # ── Config collection / distribution ──────────────────────────────────────

    def _collect_config(self) -> QCConfig:
        """Read current UI state into a QCConfig."""
        cfg = self._config
        cfg.core = self._core_tab.get_core_config()
        cfg.enabledModules = self._module_mgr.get_enabled_modules()

        if self._ft_tab:
            cfg.modules.fileTypes = self._ft_tab.get_config()
        if self._co_tab:
            cfg.modules.codecs = self._co_tab.get_config()
        if self._fp_tab:
            cfg.modules.fileTypePairs = self._fp_tab.get_config()
        if self._np_tab:
            cfg.modules.namingPattern = self._np_tab.get_config()
        return cfg

    def _distribute_config(self, config: QCConfig):
        """Push a QCConfig into all tab widgets."""
        self._config = config
        self._core_tab.set_core_config(config.core)
        self._module_mgr.set_enabled_modules(config.enabledModules)
        self._on_modules_changed(config.enabledModules)

        if self._ft_tab:
            self._ft_tab.set_config(config.modules.fileTypes)
        if self._co_tab:
            self._co_tab.set_config(config.modules.codecs)
        if self._fp_tab:
            self._fp_tab.set_config(config.modules.fileTypePairs)
        if self._np_tab:
            self._np_tab.set_config(config.modules.namingPattern)

    def _on_config_changed(self):
        self._collect_config()  # keep self._config in sync

    # ── File I/O ──────────────────────────────────────────────────────────────

    def _load_default_config(self):
        if DEFAULT_CONFIG_PATH.exists():
            try:
                cfg = load_config(DEFAULT_CONFIG_PATH)
                self._distribute_config(cfg)
                self._config_path = DEFAULT_CONFIG_PATH
            except Exception:
                pass  # ignore bad file, use defaults

    def _save_config(self):
        cfg = self._collect_config()
        path = self._config_path or DEFAULT_CONFIG_PATH
        try:
            save_config(cfg, path)
        except Exception as exc:
            QMessageBox.critical(self, 'Save failed', str(exc))

    def _export_config(self):
        cfg = self._collect_config()
        path, _ = QFileDialog.getSaveFileName(
            self, 'Export QC Config', 'qc_config.json', 'JSON Files (*.json)'
        )
        if path:
            try:
                save_config(cfg, Path(path))
            except Exception as exc:
                QMessageBox.critical(self, 'Export failed', str(exc))

    def _import_config(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Import QC Config', '', 'JSON Files (*.json)'
        )
        if not path:
            return
        try:
            cfg = load_config(Path(path))
            self._distribute_config(cfg)
            self._config_path = Path(path)
        except Exception as exc:
            QMessageBox.critical(self, 'Import failed', f'Could not load config:\n{exc}')

    def _reset_config(self):
        reply = QMessageBox.question(
            self, 'Reset configuration',
            'This will clear all parameters and return to the default empty state.\n'
            'This cannot be undone.',
            QMessageBox.Yes | QMessageBox.Cancel,
        )
        if reply == QMessageBox.Yes:
            self._distribute_config(default_config())
