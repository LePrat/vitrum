#!/usr/bin/env -S uv run --script
import json
import math
import sys
from copy import deepcopy
from typing import Any

from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton,
                               QVBoxLayout, QWidget, QSizeGrip,
                               QToolBar, QSizePolicy, QSpinBox, QDoubleSpinBox, QToolButton, QMenu)
from PySide6.QtCore import Qt, QPoint, QLocale, Slot, Signal
from pynput import keyboard


# --- Configuration & Styles ---
class UIStyles:
    TRANSPARENCY = int(50 * 255 / 100)
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
    FILE_MENU = """
        QToolButton {
            background: rgba(0, 0, 0, 100);
            color: white;
            border: 1px solid rgba(255, 255, 255, 30);
            padding: 4px 10px;
        }
        QToolButton:hover {
            background: rgba(255, 255, 255, 30);
        }
        QToolButton::menu-indicator {
            image: none;
        }
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
        self.setDecimals(5)
        self.is_focused = False
        self.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.setRange(0, 10000)
        self.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.setStyleSheet(UIStyles.OPACITY_TOOL)
        self.drawing_area = drawing_area

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.is_focused = True
        self.drawing_area.update()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.is_focused = False
        self.drawing_area.update()

    def __repr__(self):
        return str(self.value())


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
        self.file_button = None
        self.action_save = None
        self.action_load = None
        self.init_ui()

    def init_ui(self):
        self.file_button = QToolButton()
        self.file_button.setText("File")
        self.file_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.file_button.setStyleSheet(UIStyles.FILE_MENU)

        file_menu = QMenu(self.file_button)
        file_menu.setStyleSheet("""
            QMenu {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid rgba(255, 255, 255, 30);
            }
            QMenu::item:selected {
                background-color: rgba(255, 255, 255, 30);
            }
        """)

        self.action_save = file_menu.addAction("Save")
        self.action_load = file_menu.addAction("Load")

        self.file_button.setMenu(file_menu)
        self.addWidget(self.file_button)
        self.addSeparator()

        # 1. Left Side Actions (existing code continues...)
        self.opacity_spin = QSpinBox()
        # 1. Left Side Actions
        self.opacity_spin = QSpinBox()
        self.opacity_spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.opacity_spin.setRange(0, 100)
        self.opacity_spin.setSuffix("%")
        self.opacity_spin.setValue(50)
        self.opacity_spin.setStyleSheet(UIStyles.OPACITY_TOOL)
        self.opacity_spin.valueChanged.connect(self.update_background_opacity)
        self.addWidget(self.opacity_spin)
        self.addSeparator()
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
        drawing_area: DrawingArea = self.parent_window.content_area
        drawing_area.is_scale_mode = True


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
        self.is_scale_mode = False
        self.load_from_file("save.json")

    def load_from_file(self, file_path: str):
        with open(file_path) as user_file:
            file_contents = user_file.read()
        json_data: dict = json.loads(file_contents)

        self.id = int(max(json_data["circles"], key=int)) + 1
        self.scale_value = float(json_data["scale"])
        title_bar = self.parent_window.title_bar

        for json_circle_id, circle_data in json_data["circles"].items():
            json_circle_id = int(json_circle_id)
            radius = circle_data["radius"]
            sb = MySpinBox(self)
            sb_value = radius * self.scale_value
            sb.setValue(sb_value)
            sb.valueChanged.connect(lambda value: self.circle_resize(json_circle_id, value))

            point = circle_data["point"]
            qpoint = QPoint(int(point["x"]), int(point["y"]))
            self.circles[json_circle_id] = [QPoint(qpoint), sb, radius]

            delete_callback = lambda _=None, cid=json_circle_id, spinbox=sb : self.delete_circle_callback(cid, spinbox)
            btn = create_btn("✕", delete_callback, is_close=False)
            btn.clicked.connect(btn.deleteLater)
            x_action = title_bar.insertWidget(title_bar.spacer_action, btn)
            title_bar.insertWidget(x_action, sb)
        self.update()

    def save_to_file(self, file_path: str):
        json_data: dict[str, Any] = {"scale": self.scale_value}
        my_circles: dict[Any, Any] = {}
        for circle_id, circle_data in self.circles.items():
            point = {"x": circle_data[0].x(), "y": circle_data[0].y()}
            radius = circle_data[2]
            my_circles[str(circle_id)] = {"point": point, "radius": radius}
        json_data["circles"] = my_circles
        with open(file_path, 'w') as f:
            json.dump(json_data, f, indent=4)

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
        if event.button() == Qt.MouseButton.LeftButton and self.is_scale_mode is False:
            circle_id = deepcopy(self.id)
            radius = math.dist((self.start_point.x(), self.start_point.y()),
                                   (self.end_point.x(), self.end_point.y()))
            sb = MySpinBox(self)
            sb_value = radius * self.scale_value
            sb.setValue(sb_value)
            sb.valueChanged.connect(lambda value: self.circle_resize(circle_id, value))

            self.circles[self.id] = [self.start_point, sb, radius]
            btn = create_btn("✕", lambda: self.delete_circle_callback(circle_id, sb), is_close=False)
            btn.clicked.connect(btn.deleteLater)
            x_action = title_bar.insertWidget(title_bar.spacer_action, btn)
            title_bar.insertWidget(x_action, sb)

            self.id += 1
            self.update()
            self.save_to_file("save.json")

        elif event.button() == Qt.MouseButton.LeftButton and self.is_scale_mode:
            user_value = 0.5
            length_measured = math.dist((self.start_point.x(), self.start_point.y()),
                                        (self.end_point.x(), self.end_point.y()))
            self.scale_value = user_value / length_measured
            for center, sb, original_r in self.circles.values():
                sb.setValue(original_r * self.scale_value)
            self.is_scale_mode = False
            self.update()
        self.is_drawing = False

    def circle_resize(self, circle_id, sb_value):
        self.circles[circle_id][2] =  sb_value / self.scale_value
        self.update()

    def delete_circle_callback(self, circle_id, sb):
        del self.circles[circle_id]
        sb.deleteLater()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor(0, 0, 0), 2))

        for center, sb, original_r  in self.circles.values():
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

        if self.is_drawing and self.is_scale_mode:
            painter.drawLine(self.start_point, self.end_point)

        elif self.is_drawing:
            r = math.dist((self.start_point.x(), self.start_point.y()),
                      (self.end_point.x(), self.end_point.y()))
            painter.drawEllipse(self.start_point, r, r)


class ModernWindow(QMainWindow):
    _toggle_lock_signal = Signal()

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
        self._locked = False
        self._normal_flags = None
        self._toggle_lock_signal.connect(self.toggle_lock)  # signal → slot, always on main thread
        self._start_hotkey_listener()

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

    def _start_hotkey_listener(self):
        def on_activate():
            self._toggle_lock_signal.emit()  # safe to emit from any thread

        self._hotkey_listener = keyboard.GlobalHotKeys({
            '<ctrl>+<alt>+m': on_activate
        })
        self._hotkey_listener.daemon = True
        self._hotkey_listener.start()

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

    def lock_window(self):
        self._normal_flags = self.windowFlags()
        flags = (
                Qt.WindowType.FramelessWindowHint  # no title bar / borders
                | Qt.WindowType.WindowStaysOnTopHint  # always in foreground
                | Qt.WindowType.WindowTransparentForInput  # <-- the magic: all input ignored
                | Qt.WindowType.Tool  # keeps it out of taskbar
        )
        self.setWindowFlags(flags)
        self.show()
        self._locked = True

    def unlock_window(self):
        if not self._locked:
            return
        self.setWindowFlags(self._normal_flags)
        self.show()
        self._locked = False

    @Slot()
    def toggle_lock(self):
        if self._locked:
            self.unlock_window()
        else:
            self.lock_window()

if __name__ == "__main__":
    # TODO save feature
    QLocale.setDefault(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
    app = QApplication(sys.argv)
    window = ModernWindow()
    window.show()
    sys.exit(app.exec())