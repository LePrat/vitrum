#!/usr/bin/env -S uv run --script
import sys
from pynput import keyboard
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSizeGrip
from PySide6.QtCore import Qt, QLocale, Slot, Signal

from vitrum.CustomTitleBar import CustomTitleBar
from vitrum.DrawingArea import DrawingArea
from vitrum.ui import UIStyles


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
        self._toggle_lock_signal.connect(self.toggle_lock)
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

        self.title_bar = CustomTitleBar(self)
        self.main_layout.addWidget(self.title_bar)
        self.content_area = QWidget()
        self.sizegrip = QSizeGrip(self)
        self.content_area = DrawingArea(self)
        self.main_layout.addWidget(self.content_area, stretch=1)

    def _start_hotkey_listener(self):
        def on_activate():
            self._toggle_lock_signal.emit()

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
                Qt.WindowType.FramelessWindowHint
                | Qt.WindowType.WindowStaysOnTopHint
                | Qt.WindowType.WindowTransparentForInput
                | Qt.WindowType.Tool
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
    QLocale.setDefault(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
    app = QApplication(sys.argv)
    window = ModernWindow()
    window.show()
    sys.exit(app.exec())