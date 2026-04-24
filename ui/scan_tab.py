"""Scan tab — path picker, scan runner, and results tree."""
from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional

from ui.compat import (
    Qt, QThread, Signal, QObject, QColor, QFont,
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFileDialog, QTreeWidget, QTreeWidgetItem,
    QProgressBar, QRadioButton, QButtonGroup, QFrame, QSizePolicy,
)

from scanner import ScanReport, FileResult, scan_path
from config import QCConfig


# ─── Background worker ────────────────────────────────────────────────────────

class ScanWorker(QObject):
    progress = Signal(int, int)         # current, total
    file_done = Signal(object)          # FileResult
    finished = Signal(object)           # ScanReport
    error = Signal(str)

    def __init__(self, root: Path, config: QCConfig):
        super().__init__()
        self._root = root
        self._config = config
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        try:
            report = scan_path(
                root=self._root,
                config=self._config,
                progress_callback=lambda cur, tot: self.progress.emit(cur, tot),
                cancel_check=lambda: self._cancelled,
            )
            self.finished.emit(report)
        except Exception as exc:
            self.error.emit(str(exc))


class ScanThread(QThread):
    def __init__(self, worker: ScanWorker):
        super().__init__()
        self._worker = worker
        self._worker.moveToThread(self)
        self.started.connect(self._worker.run)

    def cancel(self):
        self._worker.cancel()


# ─── Scan tab widget ──────────────────────────────────────────────────────────

PASS_COLOR = QColor('#3ecf8e')
FAIL_COLOR = QColor('#ff6666')
MUTED_COLOR = QColor('#8b90a7')


class ScanTab(QWidget):
    # Provide a callback to get the current config from the main window
    def __init__(self, get_config: Callable[[], QCConfig], parent=None):
        super().__init__(parent)
        self._get_config = get_config
        self._thread: Optional[ScanThread] = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 16)
        layout.setSpacing(12)

        # ── Header ──────────────────────────────────────────────────────────
        heading = QLabel('Scan Delivery Package')
        heading.setProperty('heading', True)
        layout.addWidget(heading)

        desc = QLabel(
            'Select a folder to scan for compliance against the active configuration. '
            'All nested subfolders are included.'
        )
        desc.setProperty('muted', True)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # ── Path picker ──────────────────────────────────────────────────────
        path_row = QHBoxLayout()
        path_row.setSpacing(8)

        self._path_input = QLineEdit()
        self._path_input.setPlaceholderText('Select a folder to scan…')
        self._path_input.setReadOnly(True)
        path_row.addWidget(self._path_input, 1)

        browse_btn = QPushButton('Browse…')
        browse_btn.clicked.connect(self._browse)
        path_row.addWidget(browse_btn)

        self._scan_btn = QPushButton('▶  Scan')
        self._scan_btn.setProperty('primary', True)
        self._scan_btn.setEnabled(False)
        self._scan_btn.clicked.connect(self._start_scan)
        path_row.addWidget(self._scan_btn)

        self._cancel_btn = QPushButton('Cancel')
        self._cancel_btn.setVisible(False)
        self._cancel_btn.clicked.connect(self._cancel_scan)
        path_row.addWidget(self._cancel_btn)

        layout.addLayout(path_row)

        # ── Progress bar (hidden until scanning) ─────────────────────────────
        self._progress = QProgressBar()
        self._progress.setVisible(False)
        self._progress.setFixedHeight(6)
        layout.addWidget(self._progress)

        # ── Summary bar ──────────────────────────────────────────────────────
        self._summary_frame = QFrame()
        self._summary_frame.setStyleSheet(
            'QFrame { background: #1a1d27; border: 1px solid #333650;'
            ' border-radius: 8px; padding: 2px; }'
        )
        self._summary_frame.setVisible(False)
        summary_layout = QHBoxLayout(self._summary_frame)
        summary_layout.setContentsMargins(16, 8, 16, 8)
        summary_layout.setSpacing(24)

        self._lbl_total = self._make_stat_label('0', 'Total files')
        self._lbl_passed = self._make_stat_label('0', 'Passed', PASS_COLOR.name())
        self._lbl_failed = self._make_stat_label('0', 'Failed', FAIL_COLOR.name())
        self._lbl_warn = QLabel()
        self._lbl_warn.setStyleSheet('color: #f0a429; font-size: 11px;')
        self._lbl_warn.setWordWrap(True)

        for w in (self._lbl_total, self._lbl_passed, self._lbl_failed):
            summary_layout.addWidget(w)
        summary_layout.addWidget(self._lbl_warn, 1)
        summary_layout.addStretch()
        layout.addWidget(self._summary_frame)

        # ── Filter bar ───────────────────────────────────────────────────────
        filter_row = QHBoxLayout()
        filter_row.setSpacing(12)

        self._radio_all = QRadioButton('All files')
        self._radio_fail = QRadioButton('Failures only')
        self._radio_all.setChecked(True)
        radio_group = QButtonGroup(self)
        radio_group.addButton(self._radio_all)
        radio_group.addButton(self._radio_fail)
        self._radio_all.toggled.connect(self._apply_filter)

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText('Filter by filename…')
        self._search_input.setFixedWidth(240)
        self._search_input.textChanged.connect(self._apply_filter)

        filter_row.addWidget(self._radio_all)
        filter_row.addWidget(self._radio_fail)
        filter_row.addSpacing(8)
        filter_row.addWidget(QLabel('Search:'))
        filter_row.addWidget(self._search_input)
        filter_row.addStretch()
        layout.addLayout(filter_row)

        # ── Results tree ─────────────────────────────────────────────────────
        self._tree = QTreeWidget()
        self._tree.setColumnCount(3)
        self._tree.setHeaderLabels(['File', 'Status', 'Issues'])
        self._tree.header().setStretchLastSection(True)
        self._tree.setColumnWidth(0, 400)
        self._tree.setColumnWidth(1, 70)
        self._tree.setAlternatingRowColors(True)
        self._tree.setSortingEnabled(False)
        layout.addWidget(self._tree, 1)

        # Store all results for filter re-apply
        self._all_results: list[FileResult] = []

    def _make_stat_label(self, value: str, label: str, color: str = '#e8eaf0') -> QWidget:
        w = QWidget()
        vl = QVBoxLayout(w)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(0)
        num = QLabel(value)
        num.setStyleSheet(f'font-size: 22px; font-weight: 700; color: {color};')
        num.setObjectName(f'stat_{label}')
        txt = QLabel(label)
        txt.setStyleSheet('font-size: 11px; color: #8b90a7;')
        vl.addWidget(num)
        vl.addWidget(txt)
        return w

    def _browse(self):
        path = QFileDialog.getExistingDirectory(self, 'Select delivery package folder')
        if path:
            self._path_input.setText(path)
            self._scan_btn.setEnabled(True)

    def _start_scan(self):
        path = self._path_input.text().strip()
        if not path:
            return
        root = Path(path)
        if not root.is_dir():
            return

        config = self._get_config()
        self._tree.clear()
        self._all_results.clear()
        self._summary_frame.setVisible(False)
        self._progress.setVisible(True)
        self._progress.setRange(0, 0)  # indeterminate until we know total
        self._scan_btn.setEnabled(False)
        self._cancel_btn.setVisible(True)

        worker = ScanWorker(root, config)
        self._thread = ScanThread(worker)

        worker.progress.connect(self._on_progress)
        worker.finished.connect(self._on_finished)
        worker.error.connect(self._on_error)

        self._thread.start()

    def _cancel_scan(self):
        if self._thread and self._thread.isRunning():
            self._thread.cancel()
            self._cancel_btn.setEnabled(False)

    def _on_progress(self, current: int, total: int):
        self._progress.setRange(0, total)
        self._progress.setValue(current)

    def _on_finished(self, report: ScanReport):
        self._progress.setVisible(False)
        self._scan_btn.setEnabled(True)
        self._cancel_btn.setVisible(False)

        self._all_results = report.results
        self._populate_tree(report.results)

        # Summary
        total_lbl = self._lbl_total.findChild(QLabel, 'stat_Total files')
        pass_lbl = self._lbl_passed.findChild(QLabel, 'stat_Passed')
        fail_lbl = self._lbl_failed.findChild(QLabel, 'stat_Failed')
        if total_lbl:
            total_lbl.setText(str(report.total))
        if pass_lbl:
            pass_lbl.setText(str(report.passed))
        if fail_lbl:
            fail_lbl.setText(str(report.failed))

        self._lbl_warn.setText(' | '.join(report.warnings))
        self._summary_frame.setVisible(True)

    def _on_error(self, message: str):
        self._progress.setVisible(False)
        self._scan_btn.setEnabled(True)
        self._cancel_btn.setVisible(False)
        self._lbl_warn.setText(f'Scan error: {message}')
        self._summary_frame.setVisible(True)

    def _populate_tree(self, results: list[FileResult]):
        self._tree.clear()
        show_failures_only = self._radio_fail.isChecked()
        search = self._search_input.text().lower()

        mono_font = QFont('Courier New', 11)

        for result in results:
            path_str = str(result.path)

            # Apply filters
            if search and search not in path_str.lower():
                continue
            if show_failures_only and result.passed:
                continue

            status_text = 'PASS' if result.passed else 'FAIL'
            failed = result.failed_checks
            issues_text = '; '.join(c.detail for c in failed) if failed else ''

            item = QTreeWidgetItem([path_str, status_text, issues_text])
            item.setFont(0, mono_font)

            color = PASS_COLOR if result.passed else FAIL_COLOR
            item.setForeground(1, color)

            if not result.passed:
                item.setForeground(0, FAIL_COLOR)
                # Add child rows for each failed check
                for check in result.checks:
                    child_status = '✓' if check.passed else '✗'
                    child = QTreeWidgetItem(['', child_status, f'{check.rule}: {check.detail}'])
                    child_color = PASS_COLOR if check.passed else FAIL_COLOR
                    child.setForeground(1, child_color)
                    child.setForeground(2, child_color if not check.passed else MUTED_COLOR)
                    item.addChild(child)

            self._tree.addTopLevelItem(item)

        # Expand failures
        self._tree.expandAll() if not results else None

    def _apply_filter(self):
        self._populate_tree(self._all_results)
