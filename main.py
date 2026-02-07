import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QSizeGrip
from PySide6.QtCore import Qt, QPoint

class ModernTransparentWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 1. Window Setup
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(400, 300)

        # State for dragging
        self._drag_pos = QPoint()

        # 2. UI Layout
        self.central_widget = QWidget()
        self.central_widget.setStyleSheet("""
            QWidget#MainContainer {
                background-color: rgba(30, 30, 30, 220);
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 30);
            }
        """)
        self.central_widget.setObjectName("MainContainer")
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        # 3. Close Button
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 80, 80, 150);
                color: white;
                border-radius: 15px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: rgb(255, 50, 50); }
        """)
        self.layout.addWidget(self.close_btn, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

        # 4. Resize Handle (SizeGrip)
        # This adds a small invisible handle at the bottom right
        self.sizegrip = QSizeGrip(self)
        self.sizegrip.setStyleSheet("background-color: transparent;")

    def resizeEvent(self, event):
        """Ensure the resize handle stays in the bottom right corner."""
        super().resizeEvent(event)
        grip_size = 20
        self.sizegrip.setGeometry(
            self.width() - grip_size,
            self.height() - grip_size,
            grip_size,
            grip_size
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernTransparentWindow()
    window.show()
    sys.exit(app.exec())