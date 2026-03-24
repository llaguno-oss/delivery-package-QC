#!/usr/bin/env python3
"""
Delivery Package QC — standalone desktop application.

Launch:
    python main.py

Requirements:
    pip install -r requirements.txt
"""
import sys
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import Qt
from ui.main_window import MainWindow
from ui.theme import DARK_QSS


def main():
    # Enable high-DPI scaling before creating QApplication
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName('Delivery Package QC')
    app.setOrganizationName('DeliveryQC')
    app.setStyleSheet(DARK_QSS)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
