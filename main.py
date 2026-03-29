import math
import sys
from copy import deepcopy

from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton,
                               QVBoxLayout, QWidget, QSizeGrip,
                               QToolBar, QSizePolicy, QComboBox, QSpinBox, QDoubleSpinBox)
from PySide6.QtCore import Qt, QPoint


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

def create_btn(text, callback, is_close=False, width=32):
    btn = QPushButton(text)
    btn.setFixedSize(width, 28)
    hover_color = "#e81123" if is_close else "rgba(255, 255, 255, 40)"
    btn.setStyleSheet(f"""
        QPushButton {{ background: transparent; color: white; border-radius: 4px; font-size: 14px; }}
        QPushButton:hover {{ background: {hover_color}; }}
    """)
    if callback is not None:
        btn.clicked.connect(callback)
    return btn


class MySpinBox(QDoubleSpinBox):
    def __init__(self, drawing_area: DrawingArea, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_focused = False
        self.drawing_area = drawing_area

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.is_focused = True
        self.drawing_area.update()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.is_focused = False
        self.drawing_area.update()


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
        self.spacer_action = None
        self.circles = None
        self.btn_set_scale = None
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

        self.mode_select: QComboBox = QComboBox()
        self.mode_select.addItems(["Circle", "Line"])
        self.mode_select.setStyleSheet(UIStyles.MODE_SELECT)
        self.addSeparator()
        self.addWidget(self.mode_select)
        self.addSeparator()

        # 2. Spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.spacer_action = self.addWidget(spacer)

    # 3. Window Buttons
        self.btn_full = create_btn("⛶", self.parent_window.toggle_fullscreen)
        self.btn_close = create_btn("✕", self.parent_window.close, is_close=True)
        self.btn_set_scale = create_btn("Set scale", self.update_scale, is_close=False, width=70)

        self.addWidget(self.btn_set_scale)
        self.addWidget(self.btn_full)
        self.addWidget(self.btn_close)


    def update_background_opacity(self, value):
        """
        Updates only the alpha channel of the background
        while preserving the rest of the UI design.
        """
        if value < 1:
            value = 1
            self.opacity_spin.setValue(value)
        alpha = int(value * 255 / 100)
        new_style = f"""
            QWidget#MainContainer {{
                background-color: rgba(30, 30, 30, {alpha});
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 40);
            }}
        """
        self.parent_window.main_container.setStyleSheet(new_style)

    def update_scale(self):
        drawing_area = self.parent_window.content_area
        drawing_area.scale_value *= 0.5
        for start_point, sb in drawing_area.circles.values():
            sb.setValue(sb.value() * 0.5)
        drawing_area.update()



class DrawingArea(QWidget):
    def __init__(self, parent: ModernWindow):
        super().__init__()
        self.parent_window: ModernWindow = parent
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.is_drawing = False
        self.id = 1
        self.circles = {}
        self.scale_value = 1

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_point = event.position().toPoint()
            self.end_point = self.start_point
            self.is_drawing = True

    def mouseMoveEvent(self, event):
        if self.is_drawing:
            self.end_point = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event):
        title_bar = self.parent_window.title_bar
        if event.button() == Qt.MouseButton.LeftButton and title_bar.mode_select.currentText() == "Circle":
            radius = int(math.dist((self.start_point.x(), self.start_point.y()),
                                   (self.end_point.x(), self.end_point.y())))

            sb = MySpinBox(self)
            sb.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
            sb.setRange(1, 10000)
            sb.setValue(radius * self.scale_value)
            sb.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
            sb.setStyleSheet(UIStyles.OPACITY_TOOL)
            sb.valueChanged.connect(self.update)

            # Store the center and the widget itself
            self.circles[self.id] = (self.start_point, sb)

            xid = deepcopy(self.id)
            btn = create_btn("✕", lambda: self.delete_circle_callback(xid, sb), is_close=False)
            btn.clicked.connect(btn.deleteLater)
            x_action = title_bar.insertWidget(title_bar.spacer_action, btn)
            title_bar.insertWidget(x_action, sb)

            self.id += 1
            self.is_drawing = False
            self.update()

    def delete_circle_callback(self, circle_id, sb):
        del self.circles[circle_id]
        sb.deleteLater()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor(0, 0, 0), 2))

        title_bar: CustomTitleBar = self.parent_window.title_bar
        # 1. Draw finished circles using the SpinBox value as the radius
        for center, sb in self.circles.values():
            current_r = sb.value() / self.scale_value
            if sb.is_focused:
                painter.setPen(QPen(QColor(204, 204, 0), 2))
                painter.drawEllipse(center, current_r, current_r)
                painter.drawPoint(center)
                painter.setPen(QPen(QColor(0, 0, 0), 2))
            else:
                painter.setPen(QPen(QColor(0, 0, 0), 2))
                painter.drawEllipse(center, current_r, current_r)
                painter.drawPoint(center)

            # 2. Draw the "preview" circle while dragging
        if self.is_drawing and title_bar.mode_select.currentText() == "Circle":
            r = math.dist((self.start_point.x(), self.start_point.y()),
                      (self.end_point.x(), self.end_point.y()))
            painter.drawEllipse(self.start_point, r, r)

        elif self.is_drawing and title_bar.mode_select.currentText() == "Line":
            painter.drawLine(self.start_point, self.end_point)


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
        self.content_area = DrawingArea(self)
        self.main_layout.addWidget(self.content_area, stretch=1)

    def toggle_fullscreen(self):
        if not self._is_fullscreen:
            self.showFullScreen()
        else:
            self.showNormal()
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
    # TODO setscale feature = form unit value
    # TODO save feature
    app = QApplication(sys.argv)
    window = ModernWindow()
    window.show()
    sys.exit(app.exec())