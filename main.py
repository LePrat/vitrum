import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton,
                               QVBoxLayout, QWidget, QSizeGrip,
                               QToolBar, QSizePolicy)
from PySide6.QtCore import Qt


# --- Configuration & Styles ---
class UIStyles:
    TRANSPARENCY = 70  # Increased for better visibility, adjust as needed
    BG_COLOR = f"rgba(30, 30, 30, {TRANSPARENCY})"
    RADIUS = "12px"

    MAIN_CONTAINER = f"""
        QWidget#MainContainer {{
            background-color: {BG_COLOR};
            border-radius: {RADIUS};
            border: 1px solid rgba(255, 255, 255, 40);
        }}
    """

    TOOLBAR = f"""
        QToolBar {{
            background: rgba(255, 255, 255, 15);
            border-bottom: 1px solid rgba(255, 255, 255, 20);
            border-top-left-radius: {RADIUS};
            border-top-right-radius: {RADIUS};
            padding: 4px;
        }}
        QToolButton {{ color: white; padding: 5px; font-weight: bold; }}
        QToolButton:hover {{ background: rgba(255, 255, 255, 30); border-radius: 4px; }}
    """


# --- Custom Widgets ---
class CustomTitleBar(QToolBar):
    """A specialized toolbar that handles window movement and controls."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.btn_close = None
        self.btn_full = None
        self.parent_window = parent
        self.setMovable(False)
        self.setStyleSheet(UIStyles.TOOLBAR)
        self.init_ui()

    def init_ui(self):
        # 1. Left Side Actions
        self.addAction("Save")
        self.addAction("Load")
        self.addAction("Shapes")

        # 2. Spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.addWidget(spacer)

        # 3. Window Buttons
        self.btn_full = self._create_btn("⛶", self.parent_window.toggle_fullscreen)
        self.btn_close = self._create_btn("✕", self.parent_window.close, is_close=True)

        self.addWidget(self.btn_full)
        self.addWidget(self.btn_close)

    @staticmethod
    def _create_btn(text, callback, is_close=False):
        btn = QPushButton(text)
        btn.setFixedSize(32, 28)
        hover_color = "#e81123" if is_close else "rgba(255, 255, 255, 40)"
        btn.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: white; border-radius: 4px; font-size: 14px; }}
            QPushButton:hover {{ background: {hover_color}; }}
        """)
        btn.clicked.connect(callback)
        return btn


# --- Main Window ---
class ModernWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.sizegrip = None
        self.content_area = None
        self.title_bar = None
        self.main_layout = None
        self.main_container = None
        self._is_fullscreen = False
        self._drag_pos = None

        self.setup_window_properties()
        self.setup_ui()

    def setup_window_properties(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(800, 600)

    def setup_ui(self):
        # Central Widget & Layout
        self.main_container = QWidget()
        self.main_container.setObjectName("MainContainer")
        self.main_container.setStyleSheet(UIStyles.MAIN_CONTAINER)
        self.setCentralWidget(self.main_container)

        self.main_layout = QVBoxLayout(self.main_container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Custom Toolbar
        self.title_bar = CustomTitleBar(self)
        self.main_layout.addWidget(self.title_bar)

        self.content_area = QWidget()
        self.main_layout.addWidget(self.content_area, stretch=1)

        self.sizegrip = QSizeGrip(self)

    def toggle_fullscreen(self):
        if not self._is_fullscreen:
            self.showFullScreen()
            # Remove rounding when fullscreen
            self.main_container.setStyleSheet(UIStyles.MAIN_CONTAINER.replace(UIStyles.RADIUS, "0px"))
        else:
            self.showNormal()
            self.main_container.setStyleSheet(UIStyles.MAIN_CONTAINER)
        self._is_fullscreen = not self._is_fullscreen

    def mousePressEvent(self, event):
        if self.title_bar.rect().contains(event.position().toPoint()):
            if event.button() == Qt.MouseButton.LeftButton:
                self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and not self._is_fullscreen:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.sizegrip.move(self.width() - 20, self.height() - 20)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernWindow()
    window.show()
    sys.exit(app.exec())