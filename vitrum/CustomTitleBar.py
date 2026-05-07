from PySide6.QtCore import QStandardPaths
from PySide6.QtWidgets import QToolBar, QToolButton, QMenu, QSpinBox, QWidget, QSizePolicy, QFileDialog

from vitrum.ui import UIStyles
from vitrum.utils import create_btn


class CustomTitleBar(QToolBar):
    """A specialized toolbar that handles window movement and controls."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mode_select = None
        self.opacity_spin = None
        self.btn_close = None
        self.btn_full = None
        self.parent_window = parent
        self.setMovable(False)
        self.setStyleSheet(UIStyles.TOOLBAR)
        self.spacer_action = None
        self.circles = None
        self.btn_set_scale = None
        self.file_button = None
        self.action_save_as = None
        self.action_save = None
        self.action_load = None
        self.current_file_name = ""
        self.init_ui()

    def init_ui(self):
        self.file_button = QToolButton()
        self.file_button.setText("File")
        self.file_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.file_button.setStyleSheet(UIStyles.FILE_MENU)

        file_menu = QMenu(self.file_button)
        file_menu.setStyleSheet(UIStyles.MENU)

        self.action_load = file_menu.addAction("Open...")
        self.action_save_as = file_menu.addAction("Save As...")
        self.action_save = file_menu.addAction("Save")
        self.action_save_as.triggered.connect(self.on_save_as_clicked)
        self.action_save.triggered.connect(self.on_save_clicked)
        self.action_load.triggered.connect(self.on_load_clicked)

        self.file_button.setMenu(file_menu)
        self.addWidget(self.file_button)
        self.addSeparator()

        self.opacity_spin = QSpinBox()
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

    def on_save_as_clicked(self):
        documents_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
        drawing_area = self.parent_window.content_area

        dialog = QFileDialog(self)
        dialog.setWindowTitle("Save Vitrum project")
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)

        dialog.setDirectory(documents_dir)
        dialog.setNameFilter("JSON Files (*.json)")
        dialog.setDefaultSuffix("json")
        dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        dialog.setViewMode(QFileDialog.ViewMode.Detail)
        if dialog.exec():
            selected_files = dialog.selectedFiles()
            file_path = selected_files[0]
            drawing_area.save_to_file(file_path)
            self.current_file_name = file_path

    def on_save_clicked(self):
        drawing_area = self.parent_window.content_area
        if self.current_file_name:
            drawing_area.save_to_file(self.current_file_name)
        else:
            self.on_save_as_clicked()

    def on_load_clicked(self):
        documents_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
        drawing_area = self.parent_window.content_area

        dialog = QFileDialog(self)
        dialog.setWindowTitle("Load Vitrum project")

        dialog.setDirectory(documents_dir)
        dialog.setNameFilter("JSON Files (*.json)")
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setViewMode(QFileDialog.ViewMode.Detail)
        if dialog.exec():
            selected_files = dialog.selectedFiles()
            file_path = selected_files[0]
            drawing_area.load_from_file(file_path)
            self.current_file_name = file_path



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
        drawing_area = self.parent_window.content_area
        drawing_area.is_scale_mode = True

