import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton,
                               QVBoxLayout, QWidget, QSizeGrip,
                               QToolBar, QSizePolicy)
from PySide6.QtCore import Qt, QPoint

TRANSPARENCY = 70

class ToolbarWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(700, 500)
        self._drag_pos = QPoint()
        self._is_fullscreen = False
        self._transparency = TRANSPARENCY

        # --- Main Container ---
        self.container = QWidget()
        self.container.setObjectName("MainContainer")
        self.container.setStyleSheet(f"""
            QWidget#MainContainer {{
                background-color: rgba(30, 30, 30, {self._transparency});
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 40);
            }}
        """)
        self.setCentralWidget(self.container)
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(0, 0, 0, 0)  # Toolbar should touch the edges

        # --- 1. The Unified ToolBar ---
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)  # Keep it locked at the top
        self.toolbar.setStyleSheet("""
            QToolBar {
                background: rgba(255, 255, 255, 15);
                border-bottom: 1px solid rgba(255, 255, 255, 20);
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                padding: 4px;
            }
            QToolButton { color: white; padding: 5px; font-weight: bold; }
            QToolButton:hover { background: rgba(255, 255, 255, 30); border-radius: 4px; }
        """)

        # Standard App Actions (Left side)
        self.toolbar.addAction("Save")
        self.toolbar.addAction("Load")
        self.toolbar.addAction("Shapes")

        # The Spacer: This pushes everything after it to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.toolbar.addWidget(spacer)

        # Window Controls (Right side)
        self.full_btn = QPushButton("⛶")
        self.close_btn = QPushButton("✕")
        for btn in [self.full_btn, self.close_btn]:
            btn.setFixedSize(32, 28)
            btn.setStyleSheet("""
                QPushButton { 
                    background: transparent; color: white; border-radius: 4px; font-size: 14px;
                }
                QPushButton:hover { background: rgba(255, 255, 255, 40); }
            """)
        # Specific hover for close button
        self.close_btn.setStyleSheet(self.close_btn.styleSheet() + "QPushButton:hover { background: #e81123; }")
        self.full_btn.clicked.connect(self.toggle_fullscreen)
        self.close_btn.clicked.connect(self.close)

        self.toolbar.addWidget(self.full_btn)
        self.toolbar.addWidget(self.close_btn)

        # Add toolbar to the top of our layout
        self.layout.addWidget(self.toolbar)
        self.layout.addStretch()  # Content area

        self.sizegrip = QSizeGrip(self)

    def toggle_fullscreen(self):
        if not self._is_fullscreen:
            self.showFullScreen()
            self.container.setStyleSheet(
                f"QWidget#MainContainer {{ border-radius: 0px; background-color: rgb(30, 30, 30, {self._transparency}); }}")
            self.toolbar.setStyleSheet(
                self.toolbar.styleSheet().replace("border-top-left-radius: 12px; border-top-right-radius: 12px;", ""))
        else:
            self.showNormal()
            self.container.setStyleSheet(
                f"QWidget#MainContainer {{ border-radius: 12px; background-color: rgba(30, 30, 30, {self._transparency}); }}")
            self.toolbar.setStyleSheet(
                self.toolbar.styleSheet() + "QToolBar { border-top-left-radius: 12px; border-top-right-radius: 12px; }")

        self._is_fullscreen = not self._is_fullscreen

    # Dragging Logic (still needed on the whole window or toolbar)
    def mousePressEvent(self, event):
        # Only start the drag if we click inside the toolbar
        if self.toolbar.rect().contains(event.position().toPoint()):
            if event.button() == Qt.MouseButton.LeftButton and not self._is_fullscreen:
                self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
        else:
            # If we click the body, we don't set _drag_pos, so mouseMoveEvent won't move it
            self._drag_pos = None

    def mouseMoveEvent(self, event):
        # Only move if _drag_pos was successfully set in mousePressEvent
        if self._drag_pos and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.sizegrip.move(self.width() - 20, self.height() - 20)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ToolbarWindow()
    window.show()
    sys.exit(app.exec())