import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton,
                               QHBoxLayout, QVBoxLayout, QWidget, QSizeGrip)
from PySide6.QtCore import Qt, QPoint


class ModernTransparentWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(500, 400)

        self._drag_pos = QPoint()
        self._is_fullscreen = False

        # --- UI Setup ---
        self.central_widget = QWidget()
        self.central_widget.setObjectName("MainContainer")
        self.central_widget.setStyleSheet("""
            QWidget#MainContainer {
                background-color: rgba(30, 30, 30, 220);
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 30);
            }
        """)
        self.setCentralWidget(self.central_widget)

        # Main Layout
        self.main_layout = QVBoxLayout(self.central_widget)

        # Header bar for buttons
        self.header_layout = QHBoxLayout()

        # Fullscreen Button
        self.full_btn = QPushButton("⛶")  # Square symbol
        self.full_btn.setFixedSize(30, 30)
        self.full_btn.clicked.connect(self.toggle_fullscreen)

        # Close Button
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.clicked.connect(self.close)

        # Style for both buttons
        button_style = """
            QPushButton {
                background-color: rgba(255, 255, 255, 20);
                color: white;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover { background-color: rgba(255, 255, 255, 40); }
        """
        self.full_btn.setStyleSheet(button_style)
        self.close_btn.setStyleSheet(button_style + "QPushButton:hover { background-color: #e81123; }")

        self.header_layout.addStretch()  # Push buttons to the right
        self.header_layout.addWidget(self.full_btn)
        self.header_layout.addWidget(self.close_btn)

        self.main_layout.addLayout(self.header_layout)
        self.main_layout.addStretch()  # Push content to top

        # Resize Handle
        self.sizegrip = QSizeGrip(self)

    def toggle_fullscreen(self):
        if not self._is_fullscreen:
            self.showFullScreen()
            self.full_btn.setText("❐")  # Change icon to "restore"
            self.central_widget.setStyleSheet(
                "QWidget#MainContainer { border-radius: 0px; background-color: rgba(30, 30, 30, 220); }")
            self.sizegrip.hide()  # Hide resize handle in fullscreen
        else:
            self.showNormal()
            self.full_btn.setText("⛶")
            self.central_widget.setStyleSheet(
                "QWidget#MainContainer { border-radius: 15px; background-color: rgba(30, 30, 30, 220); }")
            self.sizegrip.show()

        self._is_fullscreen = not self._is_fullscreen

    def resizeEvent(self, event):
        super().resizeEvent(event)
        rect = self.rect()
        self.sizegrip.move(rect.right() - 20, rect.bottom() - 20)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self._is_fullscreen:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and not self._is_fullscreen:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernTransparentWindow()
    window.show()
    sys.exit(app.exec())