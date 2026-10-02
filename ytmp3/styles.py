STYLESHEET = """
* {
    font-family: "Segoe UI", "Ubuntu", "Helvetica Neue", sans-serif;
    font-size: 13px;
}

QMainWindow, QWidget {
    background-color: #1b1c22;
    color: #e9e9f1;
}

QLabel#appTitle {
    font-size: 22px;
    font-weight: 600;
    color: #ffffff;
}

QLabel#appSubtitle {
    color: #9a9ab0;
    font-size: 12px;
    margin-bottom: 4px;
}

QPlainTextEdit {
    background-color: #24252e;
    border: 1px solid #34354a;
    border-radius: 10px;
    padding: 10px;
    color: #e9e9f1;
    selection-background-color: #7c5cff;
}

QPlainTextEdit:focus {
    border: 1px solid #7c5cff;
}

QPushButton {
    background-color: #2a2b36;
    color: #e9e9f1;
    border: 1px solid #383a4d;
    border-radius: 8px;
    padding: 8px 16px;
}

QPushButton:hover {
    background-color: #33344350;
    border: 1px solid #4a4c66;
}

QPushButton:pressed {
    background-color: #24252e;
}

QPushButton:disabled {
    color: #6c6c7c;
    border: 1px solid #2a2b36;
}

QPushButton#primaryBtn {
    background-color: #7c5cff;
    border: 1px solid #7c5cff;
    color: #ffffff;
    font-weight: 600;
}

QPushButton#primaryBtn:hover {
    background-color: #8d70ff;
}

QPushButton#primaryBtn:pressed {
    background-color: #6a4ce0;
}

QPushButton#primaryBtn:disabled {
    background-color: #3a3550;
    border: 1px solid #3a3550;
    color: #8a8a9c;
}

QTableWidget {
    background-color: #20212a;
    alternate-background-color: #24252e;
    border: 1px solid #2f3040;
    border-radius: 10px;
    gridline-color: #2f3040;
    color: #e9e9f1;
}

QTableWidget::item {
    padding: 6px;
}

QTableWidget::item:selected {
    background-color: #3a3357;
    color: #ffffff;
}

QHeaderView::section {
    background-color: #24252e;
    color: #9a9ab0;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #2f3040;
    font-weight: 600;
}

QProgressBar {
    background-color: #24252e;
    border: 1px solid #2f3040;
    border-radius: 8px;
    text-align: center;
    color: #e9e9f1;
    height: 18px;
}

QProgressBar::chunk {
    background-color: #7c5cff;
    border-radius: 8px;
}

QScrollBar:vertical {
    background: #1b1c22;
    width: 10px;
}

QScrollBar::handle:vertical {
    background: #3a3b4d;
    border-radius: 5px;
    min-height: 20px;
}

QMessageBox {
    background-color: #1b1c22;
}
"""
