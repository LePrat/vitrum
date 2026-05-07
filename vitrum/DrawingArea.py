import json
import math
from copy import deepcopy
from typing import Any

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtWidgets import QWidget

from vitrum.CustomSpinBox import CustomSpinBox
from vitrum.utils import create_btn


class DrawingArea(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent_window = parent
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.is_drawing = False
        self.id = 1
        self.circles = {}
        self.scale_value = 1
        self.is_scale_mode = False

    def delete_circles(self):
        if self.circles:
            for circle_id, circle_data in self.circles.items():
                _, spin_box, _ = circle_data
                spin_box.deleteLater()
                spin_box.btn.deleteLater()
            self.circles = {}

    def load_from_file(self, file_path: str):
        self.delete_circles()
        with open(file_path) as user_file:
            file_contents = user_file.read()
        json_data: dict = json.loads(file_contents)

        self.id = int(max(json_data["circles"], key=int)) + 1
        self.scale_value = float(json_data["scale"])
        title_bar = self.parent_window.title_bar

        for json_circle_id, circle_data in json_data["circles"].items():
            json_circle_id = int(json_circle_id)
            radius = circle_data["radius"]
            sb = CustomSpinBox(self)
            sb_value = radius * self.scale_value
            sb.setValue(sb_value)
            sb.valueChanged.connect(lambda value: self.circle_resize(json_circle_id, value))

            point = circle_data["point"]
            qpoint = QPoint(int(point["x"]), int(point["y"]))

            delete_callback = lambda _=None, cid=json_circle_id, spinbox=sb : self.delete_circle_callback(cid, spinbox)
            self.circles[json_circle_id] = [QPoint(qpoint), sb, radius]
            btn = create_btn("✕", delete_callback, is_close=False)
            btn.clicked.connect(btn.deleteLater)
            sb.btn = btn
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
            sb = CustomSpinBox(self)
            sb_value = radius * self.scale_value
            sb.setValue(sb_value)
            sb.valueChanged.connect(lambda value: self.circle_resize(circle_id, value))

            btn = create_btn("✕", lambda: self.delete_circle_callback(circle_id, sb), is_close=False)
            btn.clicked.connect(btn.deleteLater)
            sb.btn = btn
            self.circles[self.id] = [self.start_point, sb, radius]
            x_action = title_bar.insertWidget(title_bar.spacer_action, btn)
            title_bar.insertWidget(x_action, sb)

            self.id += 1
            self.update()

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

