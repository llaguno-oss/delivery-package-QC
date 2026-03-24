"""Dark broadcast-professional QSS theme."""

DARK_QSS = """
/* ── Base ── */
QMainWindow, QDialog {
    background: #0f1117;
}
QWidget {
    background: #0f1117;
    color: #e8eaf0;
    font-family: -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif;
    font-size: 13px;
}

/* ── Tab bar ── */
QTabWidget::pane {
    border: none;
    background: #0f1117;
}
QTabBar {
    background: #1a1d27;
}
QTabBar::tab {
    background: #1a1d27;
    color: #8b90a7;
    padding: 9px 18px;
    border: none;
    border-bottom: 2px solid transparent;
    min-width: 80px;
}
QTabBar::tab:selected {
    color: #4f6ef7;
    border-bottom: 2px solid #4f6ef7;
    background: #1a1d27;
}
QTabBar::tab:hover:!selected {
    color: #e8eaf0;
}

/* ── Inputs ── */
QLineEdit, QTextEdit, QPlainTextEdit {
    background: #252836;
    border: 1px solid #333650;
    border-radius: 6px;
    color: #e8eaf0;
    padding: 5px 10px;
    selection-background-color: #4f6ef7;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #4f6ef7;
}
QLineEdit:disabled {
    color: #555c7a;
    background: #1e2130;
}
QLineEdit[invalid="true"] {
    border-color: #ff6666;
    background: rgba(255,102,102,0.08);
}

/* ── ComboBox ── */
QComboBox {
    background: #252836;
    border: 1px solid #333650;
    border-radius: 6px;
    color: #e8eaf0;
    padding: 5px 28px 5px 10px;
    min-height: 28px;
}
QComboBox:focus {
    border-color: #4f6ef7;
}
QComboBox::drop-down {
    border: none;
    width: 20px;
}
QComboBox::down-arrow {
    image: none;
    width: 0;
    height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #8b90a7;
}
QComboBox QAbstractItemView {
    background: #252836;
    border: 1px solid #333650;
    selection-background-color: #4f6ef7;
    color: #e8eaf0;
    outline: none;
}

/* ── Buttons ── */
QPushButton {
    background: #252836;
    border: 1px solid #333650;
    border-radius: 6px;
    color: #e8eaf0;
    padding: 5px 14px;
    min-height: 28px;
}
QPushButton:hover {
    border-color: #8b90a7;
    background: #2e3245;
}
QPushButton:pressed {
    background: #1e2130;
}
QPushButton:disabled {
    color: #555c7a;
    border-color: #262940;
    background: #1e2130;
}
QPushButton[primary="true"] {
    background: #4f6ef7;
    border: none;
    color: white;
    font-weight: 500;
}
QPushButton[primary="true"]:hover {
    background: #6b85ff;
}
QPushButton[primary="true"]:disabled {
    background: rgba(79,110,247,0.35);
    color: rgba(255,255,255,0.5);
}
QPushButton[danger="true"] {
    background: transparent;
    border: none;
    color: #8b90a7;
    padding: 3px 6px;
    min-height: 22px;
}
QPushButton[danger="true"]:hover {
    color: #ff6666;
    background: rgba(255,102,102,0.12);
    border-radius: 4px;
}
QPushButton[flat="true"] {
    background: transparent;
    border: none;
    color: #8b90a7;
    padding: 3px 8px;
}
QPushButton[flat="true"]:hover {
    color: #e8eaf0;
    background: #252836;
}

/* ── Tables ── */
QTableWidget {
    background: #1a1d27;
    alternate-background-color: #1e2130;
    gridline-color: #262940;
    border: 1px solid #333650;
    border-radius: 8px;
    selection-background-color: rgba(79,110,247,0.2);
    selection-color: #e8eaf0;
    outline: none;
}
QTableWidget::item {
    padding: 4px 8px;
    border: none;
}
QTableWidget::item:selected {
    background: rgba(79,110,247,0.2);
}
QHeaderView::section {
    background: #1a1d27;
    color: #555c7a;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border: none;
    border-bottom: 1px solid #333650;
    padding: 6px 8px;
}
QTableWidget QLineEdit {
    border: none;
    border-radius: 0;
    background: transparent;
    padding: 2px 6px;
}

/* ── List widgets ── */
QListWidget {
    background: #1a1d27;
    border: 1px solid #333650;
    border-radius: 8px;
    outline: none;
}
QListWidget::item {
    padding: 2px 0;
    border-bottom: 1px solid #262940;
}
QListWidget::item:selected {
    background: rgba(79,110,247,0.15);
    color: #e8eaf0;
}
QListWidget::item:hover {
    background: #252836;
}

/* ── Tree widget ── */
QTreeWidget {
    background: #1a1d27;
    border: 1px solid #333650;
    border-radius: 8px;
    outline: none;
    alternate-background-color: #1e2130;
}
QTreeWidget::item {
    padding: 3px 4px;
    border: none;
}
QTreeWidget::item:hover {
    background: #252836;
}
QTreeWidget::item:selected {
    background: rgba(79,110,247,0.2);
    color: #e8eaf0;
}
QTreeWidget QHeaderView::section {
    background: #1a1d27;
    color: #555c7a;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    border: none;
    border-bottom: 1px solid #333650;
    padding: 6px 8px;
}

/* ── Progress bar ── */
QProgressBar {
    background: #252836;
    border: 1px solid #333650;
    border-radius: 4px;
    color: transparent;
    height: 6px;
    text-align: center;
}
QProgressBar::chunk {
    background: #4f6ef7;
    border-radius: 4px;
}

/* ── Scroll bars ── */
QScrollBar:vertical {
    background: #1a1d27;
    width: 8px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #333650;
    border-radius: 4px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover {
    background: #555c7a;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal {
    background: #1a1d27;
    height: 8px;
    margin: 0;
}
QScrollBar::handle:horizontal {
    background: #333650;
    border-radius: 4px;
    min-width: 20px;
}
QScrollBar::handle:horizontal:hover { background: #555c7a; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* ── Tooltip ── */
QToolTip {
    background: #252836;
    color: #e8eaf0;
    border: 1px solid #333650;
    border-radius: 4px;
    padding: 4px 8px;
}

/* ── Splitter ── */
QSplitter::handle {
    background: #333650;
}

/* ── Check box ── */
QCheckBox {
    color: #e8eaf0;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid #333650;
    background: #252836;
}
QCheckBox::indicator:checked {
    background: #4f6ef7;
    border-color: #4f6ef7;
}
QCheckBox::indicator:hover {
    border-color: #8b90a7;
}

/* ── Radio button ── */
QRadioButton {
    color: #e8eaf0;
    spacing: 8px;
}
QRadioButton::indicator {
    width: 14px;
    height: 14px;
    border-radius: 7px;
    border: 1px solid #333650;
    background: #252836;
}
QRadioButton::indicator:checked {
    background: #4f6ef7;
    border-color: #4f6ef7;
}

/* ── Group box ── */
QGroupBox {
    border: 1px solid #333650;
    border-radius: 8px;
    margin-top: 14px;
    padding-top: 10px;
    font-weight: 600;
    color: #8b90a7;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    top: -7px;
    background: #0f1117;
    padding: 0 4px;
}

/* ── Label ── */
QLabel[muted="true"] {
    color: #8b90a7;
}
QLabel[heading="true"] {
    font-size: 14px;
    font-weight: 600;
    color: #e8eaf0;
}
"""


# Chip colours for filename block types
BLOCK_CHIP_COLORS = {
    'fixed':    ('#e8eaf0', '#2e3245', '#444966'),
    'list':     ('#7da3ff', '#1e2540', '#2d3d7a'),
    'wildcard': ('#f0c429', '#2a2515', '#4a3e10'),
    'token':    ('#3ecf8e', '#152a22', '#1a4d38'),
}
