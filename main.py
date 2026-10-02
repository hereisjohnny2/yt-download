import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from ytmp3.main_window import MainWindow
from ytmp3.styles import STYLESHEET
from ytmp3.utils import resource_path


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    app.setWindowIcon(QIcon(resource_path("assets", "icon.png")))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
