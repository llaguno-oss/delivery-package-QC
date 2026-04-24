"""PySide2 / PySide6 compatibility shim.

Import Qt classes and enum aliases from here instead of importing
directly from PySide2 or PySide6 so that either version works at runtime.
"""
from __future__ import annotations

try:
    from PySide6.QtCore import Qt, Signal, QObject, QThread
    from PySide6.QtWidgets import (
        QApplication,
        QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
        QTableWidget, QTableWidgetItem, QLineEdit, QHeaderView,
        QComboBox, QFrame, QSizePolicy, QScrollArea,
        QListWidget, QListWidgetItem,
        QFileDialog, QMessageBox,
        QTabWidget, QMainWindow,
        QTreeWidget, QTreeWidgetItem,
        QProgressBar, QRadioButton, QButtonGroup,
        QAbstractItemView,
    )
    from PySide6.QtGui import QColor, QFont
    PYSIDE_VERSION = 6
except ImportError:
    from PySide2.QtCore import Qt, Signal, QObject, QThread  # type: ignore[no-redef]
    from PySide2.QtWidgets import (  # type: ignore[no-redef]
        QApplication,
        QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
        QTableWidget, QTableWidgetItem, QLineEdit, QHeaderView,
        QComboBox, QFrame, QSizePolicy, QScrollArea,
        QListWidget, QListWidgetItem,
        QFileDialog, QMessageBox,
        QTabWidget, QMainWindow,
        QTreeWidget, QTreeWidgetItem,
        QProgressBar, QRadioButton, QButtonGroup,
        QAbstractItemView,
    )
    from PySide2.QtGui import QColor, QFont  # type: ignore[no-redef]
    PYSIDE_VERSION = 2


def _qattr(obj, *paths: str):
    """Return the first existing dotted attribute path on *obj*."""
    for path in paths:
        try:
            result = obj
            for part in path.split('.'):
                result = getattr(result, part)
            return result
        except AttributeError:
            continue
    raise AttributeError(f"None of {paths!r} found on {obj!r}")


# Cursor shapes
Qt_PointingHandCursor = _qattr(Qt, 'CursorShape.PointingHandCursor', 'PointingHandCursor')
Qt_SizeVerCursor = _qattr(Qt, 'CursorShape.SizeVerCursor', 'SizeVerCursor')

# Text format
Qt_RichText = _qattr(Qt, 'TextFormat.RichText', 'RichText')

# Drop action
Qt_MoveAction = _qattr(Qt, 'DropAction.MoveAction', 'MoveAction')

# Item data role
Qt_UserRole = _qattr(Qt, 'ItemDataRole.UserRole', 'UserRole')

# Item flag
Qt_ItemIsEditable = _qattr(Qt, 'ItemFlag.ItemIsEditable', 'ItemIsEditable')

# Global color
Qt_gray = _qattr(Qt, 'GlobalColor.gray', 'gray')

# Scroll bar policy
Qt_ScrollBarAlwaysOff = _qattr(Qt, 'ScrollBarPolicy.ScrollBarAlwaysOff', 'ScrollBarAlwaysOff')
