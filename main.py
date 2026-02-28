import sys

from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton,
                               QVBoxLayout, QWidget, QSizeGrip,
                               QToolBar, QSizePolicy, QComboBox, QSpinBox)
from PySide6.QtCore import Qt, QRectF, QPoint, QRect


# --- Configuration & Styles ---
class UIStyles:
    TRANSPARENCY = 70
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
        background: rgba(255, 255, 255, 70);
        border-bottom: 1px solid rgba(255, 255, 255, 20);
        border-top-left-radius: {RADIUS};
        border-top-right-radius: {RADIUS};
        padding: 4px;
    }}
    
    QToolBar > QWidget {{
        height: 24px;
        max-height: 24px;
        min-height: 24px;
    }}
    
    QToolButton {{ 
        color: white; 
        padding: 5px; 
        font-weight: bold; 
    }}
    
    QToolButton:hover {{ 
        background: rgba(255, 255, 255, 30); 
        border-radius: 4px; 
    }}
    """

    OPACITY_TOOL = """
        QSpinBox {
            background: rgba(0, 0, 0, 100);
            color: white;
            border: 1px solid rgba(255, 255, 255, 30);
            border-radius: 4px;
            padding: 2px;
        }
    """

    MODE_SELECT = """
        QComboBox { 
            background: rgba(0, 0, 0, 100); 
            color: white; 
            border: 1px solid rgba(255, 255, 255, 30);
            border-radius: 4px;
            padding: 2px 10px;
        }
        QComboBox QAbstractItemView { background-color: #2b2b2b; color: white; }
    """


# --- Custom Widgets ---
class CustomTitleBar(QToolBar):
    """A specialized toolbar that handles window movement and controls."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mode_select = None
        self.opacity_spin = None
        self.btn_close = None
        self.btn_full = None
        self.parent_window: ModernWindow = parent
        self.setMovable(False)
        self.setStyleSheet(UIStyles.TOOLBAR)
        self.init_ui()

    def init_ui(self):
        # 1. Left Side Actions
        self.opacity_spin = QSpinBox()
        self.opacity_spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.opacity_spin.setRange(0, 100)
        self.opacity_spin.setSuffix("%")
        self.opacity_spin.setValue(70)
        self.opacity_spin.setStyleSheet(UIStyles.OPACITY_TOOL)
        self.opacity_spin.valueChanged.connect(self.update_background_opacity)
        self.addWidget(self.opacity_spin)

        self.mode_select = QComboBox()
        self.mode_select.addItems(["Circle", "Line"])
        self.mode_select.setStyleSheet(UIStyles.MODE_SELECT)
        self.addSeparator()
        self.addWidget(self.mode_select)

        # 2. Spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.addWidget(spacer)

        # 3. Window Buttons
        self.btn_full = self._create_btn("⛶", self.parent_window.toggle_fullscreen)
        self.btn_close = self._create_btn("✕", self.parent_window.close, is_close=True)

        self.addWidget(self.btn_full)
        self.addWidget(self.btn_close)

    def update_background_opacity(self, value):
        """
        Updates only the alpha channel of the background
        while preserving the rest of the UI design.
        """
        alpha = int(value * 255 / 100)
        new_style = f"""
            QWidget#MainContainer {{
                background-color: rgba(30, 30, 30, {alpha});
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 40);
            }}
        """
        self.parent_window.main_container.setStyleSheet(new_style)

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


class DrawingArea(QWidget):
    def __init__(self):
        super().__init__()
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.is_drawing = False

    def mousePressEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:
            self.start_point = event.position().toPoint()
            self.end_point = self.start_point
            self.is_drawing = True
            self.update()  # Triggers a repaint

    def mouseMoveEvent(self, event):
        if self.is_drawing:
            self.end_point = event.position().toPoint()
            self.update()  # Redraws the "preview" as you drag

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.end_point = event.position().toPoint()
            self.is_drawing = False
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Style the circle
        pen = QPen(QColor(0, 0, 0), 2)
        painter.setPen(pen)
        painter.setBrush(QColor(255, 255, 255, 0))  # Semi-transparent white

        if not self.start_point.isNull() and not self.end_point.isNull():
            # Define the bounding box for the ellipse
            rect = QRect(self.start_point, self.end_point)
            painter.drawEllipse(rect)

# --- Main Window ---
class ModernWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.painter = None
        self.sizegrip = None
        self.content_area = None
        self.title_bar = None
        self.main_layout: QVBoxLayout = None
        self.main_container: QWidget = None
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

        self.sizegrip = QSizeGrip(self)

        self.content_area = DrawingArea()
        self.main_layout.addWidget(self.content_area, stretch=1)

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