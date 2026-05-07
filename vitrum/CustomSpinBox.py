from PySide6.QtWidgets import QDoubleSpinBox, QSpinBox

from vitrum.ui import UIStyles


class CustomSpinBox(QDoubleSpinBox):
    def __init__(self, drawing_area, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setDecimals(5)
        self.is_focused = False
        self.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.setRange(0, 10000)
        self.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.setStyleSheet(UIStyles.CIRCLE_SPINBOX)
        self.drawing_area = drawing_area
        self.btn = None

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.is_focused = True
        self.drawing_area.update()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.is_focused = False
        self.drawing_area.update()

    def __repr__(self):
        return f"MySpinBox({str(self.value())})"

