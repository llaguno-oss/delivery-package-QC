#!/usr/bin/env python3
"""
Delivery Package QC — standalone desktop application.

Launch:
    python main.py

Requirements:
    pip install -r requirements.txt
"""
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from ui.main_window import MainWindow
from ui.theme import DARK_QSS


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('Delivery Package QC')
    app.setOrganizationName('DeliveryQC')
    app.setStyleSheet(DARK_QSS)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
