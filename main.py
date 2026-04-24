#!/usr/bin/env python3
"""
Delivery Package QC — standalone desktop application.

Launch:
    python main.py

Requirements:
    pip install -r requirements.txt
"""
import sys
from ui.compat import QApplication
from ui.main_window import MainWindow
from ui.theme import DARK_QSS


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('Delivery Package QC')
    app.setOrganizationName('DeliveryQC')
    app.setStyleSheet(DARK_QSS)

    window = MainWindow()
    window.show()

    # PySide2 uses exec_(); PySide6 uses exec()
    _exec = getattr(app, 'exec_', None) or app.exec
    sys.exit(_exec())


if __name__ == '__main__':
    main()
