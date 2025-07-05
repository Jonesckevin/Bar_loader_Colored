import sys
import os
import io
import json
import csv
import datetime
from typing import Dict, List, Optional, Any
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QRadioButton, QButtonGroup, QCheckBox, QLineEdit, QListWidget, QGroupBox, QScrollArea,
    QGridLayout, QDialog, QFrame, QSizePolicy, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QDialogButtonBox, QStyle, QFileDialog, QMessageBox, QSplitter, QMenu
)
from PyQt6.QtGui import QPixmap, QFont, QCursor, QIcon
from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtGui import QDesktopServices

try:
    from PIL import Image
except ImportError:
    Image = None  # Handle missing PIL gracefully

from resources.functions import (

    resource_path, load_config, round_weight,

    compute_dots, convert_lb_to_kg, convert_kg_to_lb, convert_kg_to_stone,
    calculate_total_lifts, CONVERSION_FACTOR_LB_TO_KG, CONVERSION_FACTOR_KG_TO_STONE,

    get_theme_folder, get_image_path, load_available_themes,
    filter_themes_by_text, filter_themes_by_category,

    create_combined_image_pixmap, get_cached_static_image, pil_to_pixmap,
    cleanup_temp_files, load_and_validate_image,

    load_users_from_csv, save_users_to_csv, import_users_from_csv_file,
    export_users_to_csv_file, save_removed_user, backup_users_data,
    update_user_dots, update_user_scores, validate_user_data, filter_users_by_text as filter_users_text,
    sort_users_by_column, load_judge_scores, ensure_user_completeness, LIFT_COLS,
    
    StopwatchDialog, TimerDialog, open_rules_link,
    ThemeManager
)

# Load config and set up global variables
def initialize_config():
    """Initialize configuration and global variables."""
    config = load_config()
    return config

# Initialize config
config = initialize_config()

WINDOW_WIDTH = config["window"]["width"]
WINDOW_HEIGHT = config["window"]["height"]
FONT = tuple(config["fonts"]["default"])
FONT_BOLD = tuple(config["fonts"]["bold"])
COLOR1 = config["colors"]["background"]
COLOR2 = config["colors"]["text"]
COLOR3 = config["colors"]["highlight"]
COLOR_ACCENT = config["colors"].get("accent", "#ff9800")
COLOR_SUCCESS = config["colors"].get("success", "#4caf50")
COLOR_WARNING = config["colors"].get("warning", "#ffc107")
COLOR_ERROR = config["colors"].get("error", "#f44336")
COLOR_INFO = config["colors"].get("info", "#2196f3")
COLOR_BORDER = config["colors"].get("border", "#cccccc")
COLOR_BUTTON_BG = config["colors"].get("button_bg", "#e0e0e0")
COLOR_BUTTON_FG = config["colors"].get("button_fg", "#212121")
COLOR_BUTTON_HOVER = config["colors"].get("button_hover", "#bdbdbd")
COLOR_INPUT_BG = config["colors"].get("input_bg", "#ffffff")
COLOR_INPUT_FG = config["colors"].get("input_fg", "#212121")
COLOR_SELECTION_BG = config["colors"].get("selection_bg", "#cce5ff")
COLOR_SELECTION_FG = config["colors"].get("selection_fg", "#212121")
BARBELL_TYPES = config.get("barbell_types", {"Standard": [45, 20.4]})
IMAGE_ROUNDING = config["image"]["rounding"]
THEME_PATH = config["paths"]["theme"]
DEFAULT_PADDING = config["padding"]["default"]
DEFAULT_BUTTON_PADDING = config["padding"]["button"]

APP_TITLE = config["app"]["title"]
APP_AUTHOR = config["app"]["author"]
APP_GITHUB_REPO = config["app"]["github_repo"]
APP_ICON_PATH = config["app"]["icon_path"]
APP_DESCRIPTION = config["app"]["description"]

class EditableLabel(QLabel):
    """A QLabel that becomes editable when double-clicked."""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.original_text = text
        self.edit_mode = False
        self.line_edit = None
        
    def mouseDoubleClickEvent(self, event):
        """Start editing when double-clicked."""
        if not self.edit_mode:
            self.start_editing()
        super().mouseDoubleClickEvent(event)
        
    def start_editing(self):
        """Switch to edit mode with stable positioning."""
        self.edit_mode = True
        self.original_text = self.text()
        

        self.line_edit = QLineEdit(self.text(), self.parent())
        

        self.line_edit.setGeometry(self.geometry())
        self.line_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.line_edit.setFont(self.font())
        self.line_edit.setStyleSheet(self.styleSheet())
        

        self.line_edit.setSizePolicy(self.sizePolicy())
        self.line_edit.setMinimumSize(self.minimumSize())
        self.line_edit.setMaximumSize(self.maximumSize())
        
        self.line_edit.selectAll()
        self.line_edit.show()
        self.line_edit.setFocus()
        

        self.line_edit.returnPressed.connect(self.finish_editing)
        self.line_edit.editingFinished.connect(self.finish_editing)
        

        self.setStyleSheet(self.styleSheet() + "color: transparent;")
        
    def finish_editing(self):
        """Finish editing and update the label."""
        if self.edit_mode and self.line_edit:
            new_text = self.line_edit.text().strip()
            if new_text:
                self.setText(new_text)
            else:
                self.setText(self.original_text)
            

            original_style = self.styleSheet().replace("color: transparent;", "")
            self.setStyleSheet(original_style)
            
            self.line_edit.deleteLater()
            self.line_edit = None
            self.edit_mode = False

class AddUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("➕ Add New User")
        self.setModal(True)
        self.resize(650, 800)
        self.setMinimumSize(600, 750)
        

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLOR1};
                color: {COLOR2};
            }}
            QGroupBox {{
                background-color: {COLOR1};
                color: {COLOR2};
                border: 2px solid {COLOR_BORDER};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 8px;
                font-weight: bold;
                font-size: 14px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: {COLOR3};
            }}
            QLabel {{
                color: {COLOR2};
                font-weight: bold;
                font-size: 12px;
                padding: 2px;
            }}
            QLineEdit {{
                background-color: {COLOR_INPUT_BG};
                color: {COLOR_INPUT_FG};
                border: 2px solid {COLOR_BORDER};
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
                min-height: 20px;
            }}
            QLineEdit:focus {{
                border: 2px solid {COLOR3};
                background-color: {COLOR1};
            }}
            QComboBox {{
                background-color: {COLOR_INPUT_BG};
                color: {COLOR_INPUT_FG};
                border: 2px solid {COLOR_BORDER};
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
                min-height: 20px;
            }}
            QComboBox:focus {{
                border: 2px solid {COLOR3};
            }}
            QComboBox::drop-down {{
                border: none;
                background: {COLOR_BUTTON_BG};
                border-radius: 4px;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid {COLOR2};
                margin: 0px 4px 0px 4px;
            }}
        """)
        

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameStyle(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(20)
        

        personal_group = QGroupBox("👤 Personal Information")
        personal_layout = QGridLayout(personal_group)
        personal_layout.setSpacing(12)
        personal_layout.setContentsMargins(15, 25, 15, 15)
        
        self.first_name_edit = QLineEdit()
        self.first_name_edit.setPlaceholderText("Enter first name...")
        self.last_name_edit = QLineEdit()
        self.last_name_edit.setPlaceholderText("Enter last name...")
        self.age_edit = QLineEdit()
        self.age_edit.setPlaceholderText("Enter age...")
        self.weight_lb_edit = QLineEdit()
        self.weight_lb_edit.setPlaceholderText("Weight in pounds...")
        self.weight_kg_edit = QLineEdit()
        self.weight_kg_edit.setPlaceholderText("Weight in kilograms...")
        self.sex_combo = QComboBox()
        self.sex_combo.addItems(["Male", "Female"])
        
                

        self.weight_lb_edit.textChanged.connect(self._convert_lb_to_kg)
        self.weight_kg_edit.textChanged.connect(self._convert_kg_to_lb)

        personal_layout.addWidget(QLabel("First Name:"), 0, 0)
        personal_layout.addWidget(self.first_name_edit, 0, 1)
        personal_layout.addWidget(QLabel("Last Name:"), 1, 0)
        personal_layout.addWidget(self.last_name_edit, 1, 1)
        personal_layout.addWidget(QLabel("Age:"), 2, 0)
        personal_layout.addWidget(self.age_edit, 2, 1)
        personal_layout.addWidget(QLabel("Weight LB:"), 3, 0)
        personal_layout.addWidget(self.weight_lb_edit, 3, 1)
        personal_layout.addWidget(QLabel("Weight KG:"), 4, 0)
        personal_layout.addWidget(self.weight_kg_edit, 4, 1)
        personal_layout.addWidget(QLabel("Sex:"), 5, 0)
        personal_layout.addWidget(self.sex_combo, 5, 1)
        
        scroll_layout.addWidget(personal_group)
        

        lifts_group = QGroupBox("🏋️ Powerlifting Attempts")
        lifts_layout = QGridLayout(lifts_group)
        lifts_layout.setSpacing(12)
        lifts_layout.setContentsMargins(15, 25, 15, 15)
        

        self.bench1_edit = QLineEdit()
        self.bench1_edit.setPlaceholderText("Weight...")
        self.bench2_edit = QLineEdit()
        self.bench2_edit.setPlaceholderText("Weight...")
        self.bench3_edit = QLineEdit()
        self.bench3_edit.setPlaceholderText("Weight...")
        self.squat1_edit = QLineEdit()
        self.squat1_edit.setPlaceholderText("Weight...")
        self.squat2_edit = QLineEdit()
        self.squat2_edit.setPlaceholderText("Weight...")
        self.squat3_edit = QLineEdit()
        self.squat3_edit.setPlaceholderText("Weight...")
        self.deadlift1_edit = QLineEdit()
        self.deadlift1_edit.setPlaceholderText("Weight...")
        self.deadlift2_edit = QLineEdit()
        self.deadlift2_edit.setPlaceholderText("Weight...")
        self.deadlift3_edit = QLineEdit()
        self.deadlift3_edit.setPlaceholderText("Weight...")
        

        lifts_layout.addWidget(QLabel(""), 0, 0)  # Empty corner
        
        squat_header = QLabel("Squat")
        squat_header.setStyleSheet(f"color: {COLOR3}; font-weight: bold; font-size: 14px;")
        lifts_layout.addWidget(squat_header, 0, 1)
        
        bench_header = QLabel("Bench")
        bench_header.setStyleSheet(f"color: {COLOR3}; font-weight: bold; font-size: 14px;")
        lifts_layout.addWidget(bench_header, 0, 2)
        
        deadlift_header = QLabel("Deadlift")
        deadlift_header.setStyleSheet(f"color: {COLOR3}; font-weight: bold; font-size: 14px;")
        lifts_layout.addWidget(deadlift_header, 0, 3)
        

        lifts_layout.addWidget(QLabel("Attempt 1:"), 1, 0)
        lifts_layout.addWidget(self.squat1_edit, 1, 1)
        lifts_layout.addWidget(self.bench1_edit, 1, 2)
        lifts_layout.addWidget(self.deadlift1_edit, 1, 3)
        
        lifts_layout.addWidget(QLabel("Attempt 2:"), 2, 0)
        lifts_layout.addWidget(self.squat2_edit, 2, 1)
        lifts_layout.addWidget(self.bench2_edit, 2, 2)
        lifts_layout.addWidget(self.deadlift2_edit, 2, 3)
        
        lifts_layout.addWidget(QLabel("Attempt 3:"), 3, 0)
        lifts_layout.addWidget(self.squat3_edit, 3, 1)
        lifts_layout.addWidget(self.bench3_edit, 3, 2)
        lifts_layout.addWidget(self.deadlift3_edit, 3, 3)
        
        scroll_layout.addWidget(lifts_group)
        
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.setStyleSheet(f"""
            QDialogButtonBox {{
                background-color: {COLOR1};
            }}
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {COLOR_BUTTON_BG}, stop:1 {COLOR_BUTTON_HOVER});
                color: {COLOR_BUTTON_FG};
                border: 2px solid {COLOR_BORDER};
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {COLOR3}, stop:1 {COLOR_BUTTON_BG});
                border: 2px solid {COLOR3};
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {COLOR_BUTTON_HOVER}, stop:1 {COLOR_BORDER});
            }}
        """)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
    
    def _convert_lb_to_kg(self):
        """Convert pounds to kilograms when LB field changes."""
        try:
            lb_text = self.weight_lb_edit.text().strip()
            if lb_text and lb_text != "":
                lb_value = float(lb_text)
                kg_value = convert_lb_to_kg(lb_value)

                self.weight_kg_edit.textChanged.disconnect()
                self.weight_kg_edit.setText(f"{kg_value:.1f}")

                self.weight_kg_edit.textChanged.connect(self._convert_kg_to_lb)
        except (ValueError, TypeError):
            pass
    
    def _convert_kg_to_lb(self):
        """Convert kilograms to pounds when KG field changes."""
        try:
            kg_text = self.weight_kg_edit.text().strip()
            if kg_text and kg_text != "":
                kg_value = float(kg_text)
                lb_value = convert_kg_to_lb(kg_value)

                self.weight_lb_edit.textChanged.disconnect()
                self.weight_lb_edit.setText(f"{lb_value:.1f}")

                self.weight_lb_edit.textChanged.connect(self._convert_lb_to_kg)
        except (ValueError, TypeError):
            pass

    def get_user_data(self):
        return {
            "First": self.first_name_edit.text(),
            "Last": self.last_name_edit.text(),
            "Age": self.age_edit.text(),
            "Weight_LB": self.weight_lb_edit.text(),
            "Weight_KG": self.weight_kg_edit.text(),
            "Sex": self.sex_combo.currentText(),
            "Bench1": self.bench1_edit.text(),
            "Bench2": self.bench2_edit.text(),
            "Bench3": self.bench3_edit.text(),
            "Squat1": self.squat1_edit.text(),
            "Squat2": self.squat2_edit.text(),
            "Squat3": self.squat3_edit.text(),
            "Deadlift1": self.deadlift1_edit.text(),
            "Deadlift2": self.deadlift2_edit.text(),
            "Deadlift3": self.deadlift3_edit.text(),
            "Total": "",
            "DOTS": "",
            "Wilks": "",
            "Wilks2": "",
            "IPF": "",
            "IPF_GL": ""
        }

class EditUserDialog(QDialog):
    def __init__(self, user_data, columns, parent=None):
        super().__init__(parent)
        self.setWindowTitle("✏️ Edit User")
        self.setModal(True)
        self.resize(650, 800)
        self.setMinimumSize(600, 750)
        

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLOR1};
                color: {COLOR2};
            }}
            QGroupBox {{
                background-color: {COLOR1};
                color: {COLOR2};
                border: 2px solid {COLOR_BORDER};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 8px;
                font-weight: bold;
                font-size: 14px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: {COLOR3};
            }}
            QLabel {{
                color: {COLOR2};
                font-weight: bold;
                font-size: 12px;
                padding: 2px;
            }}
            QLineEdit {{
                background-color: {COLOR_INPUT_BG};
                color: {COLOR_INPUT_FG};
                border: 2px solid {COLOR_BORDER};
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
                min-height: 20px;
            }}
            QLineEdit:focus {{
                border: 2px solid {COLOR3};
                background-color: {COLOR1};
            }}
            QComboBox {{
                background-color: {COLOR_INPUT_BG};
                color: {COLOR_INPUT_FG};
                border: 2px solid {COLOR_BORDER};
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
                min-height: 20px;
            }}
            QComboBox:focus {{
                border: 2px solid {COLOR3};
            }}
            QComboBox::drop-down {{
                border: none;
                background: {COLOR_BUTTON_BG};
                border-radius: 4px;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid {COLOR2};
                margin: 0px 4px 0px 4px;
            }}
        """)
        

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameStyle(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(20)
        
        self.fields = {}
        

        personal_group = QGroupBox("👤 Personal Information")
        personal_layout = QGridLayout(personal_group)
        personal_layout.setSpacing(12)
        personal_layout.setContentsMargins(15, 25, 15, 15)
        
        personal_fields = ["First", "Last", "Age", "Weight_LB", "Weight_KG", "Sex"]
        row = 0
        for field in personal_fields:
            if field in columns:
                label = QLabel(f"{field.replace('_', ' ')}:")
                if field == "Sex":
                    widget = QComboBox()
                    widget.addItems(["Male", "Female"])
                    widget.setCurrentText(user_data.get(field, ""))
                else:
                    widget = QLineEdit()
                    widget.setText(user_data.get(field, ""))
                    if field in ["Age", "Weight_LB", "Weight_KG"]:
                        widget.setPlaceholderText("Enter number...")
                
                self.fields[field] = widget
                personal_layout.addWidget(label, row, 0)
                personal_layout.addWidget(widget, row, 1)
                row += 1
        

        if "Weight_LB" in self.fields and "Weight_KG" in self.fields:
            self.fields["Weight_LB"].textChanged.connect(self._convert_lb_to_kg)
            self.fields["Weight_KG"].textChanged.connect(self._convert_kg_to_lb)
        
        scroll_layout.addWidget(personal_group)
        

        lifts_group = QGroupBox("🏋️ Powerlifting Attempts")
        lifts_layout = QGridLayout(lifts_group)
        lifts_layout.setSpacing(12)
        lifts_layout.setContentsMargins(15, 25, 15, 15)
        

        lift_types = ["Squat", "Bench", "Deadlift"]
        row = 0
        

        lifts_layout.addWidget(QLabel(""), 0, 0)  # Empty corner
        for col, lift_type in enumerate(lift_types):
            header_label = QLabel(f"{lift_type}")
            header_label.setStyleSheet(f"color: {COLOR3}; font-weight: bold; font-size: 14px;")
            lifts_layout.addWidget(header_label, 0, col + 1)
        

        for attempt in range(1, 4):
            attempt_label = QLabel(f"Attempt {attempt}:")
            lifts_layout.addWidget(attempt_label, attempt, 0)
            
            for col, lift_type in enumerate(lift_types):
                field = f"{lift_type}{attempt}"
                if field in columns:
                    widget = QLineEdit()
                    widget.setText(user_data.get(field, ""))
                    widget.setPlaceholderText("Weight...")
                    self.fields[field] = widget
                    lifts_layout.addWidget(widget, attempt, col + 1)
        
        scroll_layout.addWidget(lifts_group)
        

        other_fields = [col for col in columns if col not in personal_fields + [f"{lift}{num}" for lift in lift_types for num in range(1, 4)] and col != "DOTS"]
        if other_fields:
            other_group = QGroupBox("📊 Additional Information")
            other_layout = QGridLayout(other_group)
            other_layout.setSpacing(12)
            other_layout.setContentsMargins(15, 25, 15, 15)
            
            for i, field in enumerate(other_fields):
                label = QLabel(f"{field.replace('_', ' ')}:")
                widget = QLineEdit()
                widget.setText(user_data.get(field, ""))
                self.fields[field] = widget
                other_layout.addWidget(label, i, 0)
                other_layout.addWidget(widget, i, 1)
            
            scroll_layout.addWidget(other_group)
        
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.setStyleSheet(f"""
            QDialogButtonBox {{
                background-color: {COLOR1};
            }}
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {COLOR_BUTTON_BG}, stop:1 {COLOR_BUTTON_HOVER});
                color: {COLOR_BUTTON_FG};
                border: 2px solid {COLOR_BORDER};
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {COLOR3}, stop:1 {COLOR_BUTTON_BG});
                border: 2px solid {COLOR3};
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {COLOR_BUTTON_HOVER}, stop:1 {COLOR_BORDER});
            }}
        """)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
    
    def _convert_lb_to_kg(self):
        """Convert pounds to kilograms when LB field changes."""
        try:
            if "Weight_LB" in self.fields and "Weight_KG" in self.fields:
                lb_text = self.fields["Weight_LB"].text().strip()
                if lb_text and lb_text != "":
                    lb_value = float(lb_text)
                    kg_value = convert_lb_to_kg(lb_value)

                    self.fields["Weight_KG"].textChanged.disconnect()
                    self.fields["Weight_KG"].setText(f"{kg_value:.1f}")

                    self.fields["Weight_KG"].textChanged.connect(self._convert_kg_to_lb)
        except (ValueError, TypeError):
            pass
    
    def _convert_kg_to_lb(self):
        """Convert kilograms to pounds when KG field changes."""
        try:
            if "Weight_KG" in self.fields and "Weight_LB" in self.fields:
                kg_text = self.fields["Weight_KG"].text().strip()
                if kg_text and kg_text != "":
                    kg_value = float(kg_text)
                    lb_value = convert_kg_to_lb(kg_value)

                    self.fields["Weight_LB"].textChanged.disconnect()
                    self.fields["Weight_LB"].setText(f"{lb_value:.1f}")

                    self.fields["Weight_LB"].textChanged.connect(self._convert_lb_to_kg)
        except (ValueError, TypeError):
            pass
    
    def get_user_data(self):
        data = {}
        for col, widget in self.fields.items():
            if isinstance(widget, QComboBox):
                data[col] = widget.currentText()
            else:
                data[col] = widget.text()
        data["DOTS"] = ""  # Will be calculated later
        data["Wilks"] = ""  # Will be calculated later
        data["Wilks2"] = ""  # Will be calculated later
        data["IPF"] = ""  # Will be calculated later
        data["IPF_GL"] = ""  # Will be calculated later
        return data

class BarbellCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        if os.path.exists(APP_ICON_PATH):
            self.setWindowIcon(QIcon(APP_ICON_PATH))
        self.setMinimumSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)

        self._image_cache = {}
        self._static_image_cache = {}
        self._current_combined_pixmap = None
        
        # Initialize theme manager
        self.theme_manager = ThemeManager()

        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)
        self.central_widget.setStyleSheet(f"""
            background-color: {COLOR1};
            color: {COLOR2};
        """)

        self.setStyleSheet(f"""
            QGroupBox {{
                background-color: {COLOR1};
                color: {COLOR2};
                border: 1px solid {COLOR_BORDER};
                border-radius: 6px;
                margin-top: 6px;
            }}
            QGroupBox:title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }}
            QPushButton {{
                background-color: {COLOR_BUTTON_BG};
                color: {COLOR_BUTTON_FG};
                border-radius: 8px;
                border: 2px solid {COLOR3};
                padding: 6px 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLOR_BUTTON_HOVER};
                color: {COLOR_BUTTON_FG};
                border: 2px solid {COLOR_ACCENT};
            }}
            QRadioButton, QCheckBox {{
                background-color: {COLOR1};
                color: {COLOR3};
                font-weight: bold;
                border: 1.5px solid {COLOR3};
                border-radius: 6px;
                padding: 3px 8px;
                margin: 2px;
            }}
            QRadioButton::indicator, QCheckBox::indicator {{
                border: 1.5px solid {COLOR3};
                border-radius: 6px;
                background: {COLOR1};
                width: 16px;
                height: 16px;
                margin-right: 6px;
            }}
            QRadioButton::indicator:checked {{
                background-color: {COLOR3};
                border: 2px solid {COLOR_ACCENT};
            }}
            QRadioButton::indicator:unchecked {{
                background-color: {COLOR1};
                border: 1.5px solid {COLOR3};
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLOR3};
                border: 2px solid {COLOR_ACCENT};
            }}
            QCheckBox::indicator:unchecked {{
                background-color: {COLOR1};
                border: 1.5px solid {COLOR3};
            }}
            QListWidget {{
                background-color: {COLOR1};
                color: {COLOR2};
                border: 1px solid {COLOR_BORDER};
                selection-background-color: {COLOR_SELECTION_BG};
                selection-color: {COLOR_SELECTION_FG};
            }}
            QLineEdit {{
                background-color: {COLOR_INPUT_BG};
                color: {COLOR_INPUT_FG};
                border: 1px solid {COLOR_BORDER};
            }}
        """)

        self.current_weight_lb, self.current_weight_kg = list(BARBELL_TYPES.values())[0]
        self.rounding_enabled = False

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(self.splitter)

        self.left_widget = QWidget()
        self.left_layout = QVBoxLayout(self.left_widget)
        self.layout = self.left_layout  # For compatibility with existing code
        self.splitter.addWidget(self.left_widget)

        self.setup_header()
        self.setup_main_frame()
        
        # Initialize default theme and set up theme controls
        self.theme_var = ""  # Initialize theme variable
        self.theme_filter_var = "All"  # Initialize filter variable
        self.setup_theme_controls()
        self.set_default_theme()
        
        # Apply initial theme
        self.apply_theme()

        self.setup_user_pane()
        self.splitter.addWidget(self.user_pane_container)
        

        self.user_pane_container.setVisible(False)
        

        self.splitter.setSizes([700, 300])
        

        self.splitter.setChildrenCollapsible(False)  # Prevent completely collapsing panes
        

        self.left_widget.setMinimumWidth(400)
        self.user_pane_container.setMinimumWidth(300)
        

        self.splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {COLOR_BORDER};
                width: 3px;
                margin: 0px;
                padding: 0px;
            }}
            QSplitter::handle:hover {{
                background-color: {COLOR_ACCENT};
            }}
            QSplitter::handle:pressed {{
                background-color: {COLOR3};
            }}
        """)

        self.enlarged_image_window = None  # Track enlarged image window

    def setup_header(self):
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_widget.setStyleSheet(f"""
            background-color: {COLOR1};
            border-radius: 12px;
            margin: 5px;
            padding: 0;
            padding: 0;
        """)
        author_label = QLabel(f"Author: {APP_AUTHOR}")
        author_label.setFont(QFont(FONT[0], 10))
        author_label.setStyleSheet(f"color: {COLOR2};")

        self.toggle_title_btn = QPushButton("👁️ Hide Title")
        self.toggle_title_btn.setCheckable(True)
        self.toggle_title_btn.setChecked(False)  # Start with title visible
        self.toggle_title_btn.clicked.connect(self.toggle_title_visibility)
        self.toggle_title_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.toggle_title_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {COLOR_INFO}, stop:1 #1565c0);
                color: white;
                border: 2px solid #0277bd;
                border-radius: 12px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
                margin: 0 8px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #42a5f5, stop:1 {COLOR_INFO});
                border: 2px solid #29b6f6;
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #1565c0, stop:1 #0d47a1);
            }}
            QPushButton:checked {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #66bb6a, stop:1 {COLOR_SUCCESS});
                border: 2px solid #4caf50;
            }}
        """)

        self.toggle_user_pane_btn = QPushButton("👥 Show")
        self.toggle_user_pane_btn.setCheckable(True)
        self.toggle_user_pane_btn.setChecked(False)  # Start with users pane hidden
        self.toggle_user_pane_btn.clicked.connect(self.toggle_user_pane)
        self.toggle_user_pane_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.toggle_user_pane_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {COLOR_INFO}, stop:1 #1565c0);
                color: white;
                border: 2px solid #0277bd;
                border-radius: 12px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
                margin: 0 8px;
                min-width: 70px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #42a5f5, stop:1 {COLOR_INFO});
                border: 2px solid #29b6f6;
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #1565c0, stop:1 #0d47a1);
            }}
            QPushButton:checked {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #66bb6a, stop:1 {COLOR_SUCCESS});
                border: 2px solid #4caf50;
            }}
        """)

        self.exit_button = QPushButton("🚪 Exit")
        self.exit_button.clicked.connect(self.exit_all)
        self.exit_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.exit_button.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {COLOR_ERROR}, stop:1 #a32f2f);
                color: white;
                border: 2px solid #8B0000;
                border-radius: 12px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
                margin: 0 8px;
                min-width: 60px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #ff6b6b, stop:1 {COLOR_ERROR});
                border: 2px solid #ff4444;
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #a32f2f, stop:1 #8B0000);
            }}
        """)

        # Create tools dropdown menu
        self.tools_btn = QPushButton("🛠️ Tools")
        self.tools_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.tools_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {COLOR_WARNING}, stop:1 #e65100);
                color: white;
                border: 2px solid #f57c00;
                border-radius: 12px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
                margin: 0 8px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #ffb74d, stop:1 #f57c00);
                border: 2px solid #ffb74d;
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #e65100, stop:1 #bf360c);
            }}
        """)
        
        # Create tools menu
        tools_menu = QMenu(self)
        tools_menu.setStyleSheet(f"""
            QMenu {{
                background-color: {COLOR1};
                border: 2px solid {COLOR3};
                border-radius: 8px;
                padding: 4px;
                min-width: 150px;
            }}
            QMenu::item {{
                background-color: transparent;
                color: {COLOR2};
                padding: 8px 12px;
                margin: 2px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: {COLOR3};
                color: {COLOR1};
            }}
        """)

        # Add menu actions
        stopwatch_action = tools_menu.addAction("⏱️ Stopwatch")
        stopwatch_action.triggered.connect(self.open_stopwatch)

        timer_action = tools_menu.addAction("⏲️ Timer")
        timer_action.triggered.connect(self.open_timer)

        tools_menu.addSeparator()

        # Rules submenu
        from PyQt6.QtGui import QDesktopServices
        from PyQt6.QtCore import QUrl
        rules_menu = QMenu("📋 Rules", self)
        rules_menu.setStyleSheet(f"""
            QMenu {{
                background-color: {COLOR1};
                border: 2px solid {COLOR3};
                border-radius: 8px;
                padding: 4px;
                min-width: 200px;
            }}
            QMenu::item {{
                background-color: transparent;
                color: {COLOR2};
                padding: 8px 12px;
                margin: 2px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: {COLOR3};
                color: {COLOR1};
            }}
        """)
        federation_urls = {
            "IPF (International)": "https://www.powerlifting.sport/rules/codes/info/technical-rules",
            "USAPL": "https://powerlifting-ipl.com/wp-content/uploads/2025/05/2025-IPL-RULEBOOK.pdf",
            "RPS": "https://www.revolutionpowerlifting.com/rulebook/",
            "SPF": "https://www.southernpowerlifting.com/spf-rule-book/",
            "IPA": "https://ipapower.com/ipa-rules/",
            "NASA": "https://nasa-sports.com/rulebook/"
        }
        for fed, url in federation_urls.items():
            action = rules_menu.addAction(fed)
            action.triggered.connect(lambda checked, u=url: QDesktopServices.openUrl(QUrl(u)))
        tools_menu.addMenu(rules_menu)

        self.tools_btn.setMenu(tools_menu)

        # Create theme cycling button
        self.theme_btn = QPushButton("🎨 Theme")
        self.theme_btn.clicked.connect(self.cycle_theme)
        self.theme_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.theme_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #9c27b0, stop:1 #6a1b9a);
                color: white;
                border: 2px solid #7b1fa2;
                border-radius: 12px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
                margin: 0 8px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #ba68c8, stop:1 #9c27b0);
                border: 2px solid #ba68c8;
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #6a1b9a, stop:1 #4a148c);
            }}
        """)

        github_label = QLabel('<a href="#">GitHub Repository</a>')
        github_label.setFont(QFont(FONT[0], 10, QFont.Weight.Bold))
        github_label.setStyleSheet("color: blue; text-decoration: underline;")
        github_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        github_label.linkActivated.connect(self.open_github)

        right_info_widget = QWidget()
        right_info_layout = QVBoxLayout(right_info_widget)
        right_info_layout.setContentsMargins(0, 0, 0, 0)
        right_info_layout.setSpacing(2)
        right_info_layout.addWidget(github_label, alignment=Qt.AlignmentFlag.AlignRight)
        right_info_layout.addWidget(author_label, alignment=Qt.AlignmentFlag.AlignRight)

        # Layout: [Exit] [Theme] [Stretch] [Tools] [Title] [Users] [Stretch] [Info]
        header_layout.addWidget(self.exit_button, alignment=Qt.AlignmentFlag.AlignLeft)
        header_layout.addWidget(self.theme_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        header_layout.addStretch(1)
        header_layout.addWidget(self.tools_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.toggle_title_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.toggle_user_pane_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        header_layout.addStretch(1)
        header_layout.addWidget(right_info_widget, alignment=Qt.AlignmentFlag.AlignRight)

        self.layout.addWidget(header_widget)

        self.message_label = QLabel("")
        self.message_label.setFont(QFont(FONT[0], 12, QFont.Weight.Bold))
        self.message_label.setStyleSheet("color: red;")
        self.layout.addWidget(self.message_label)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        self.layout.addWidget(line)

    def setup_main_frame(self):
        main_widget = QWidget()
        main_layout = QGridLayout(main_widget)
        main_widget.setStyleSheet(f"""
            background-color: {COLOR1};
            border-radius: 12px;
        """)
        self.layout.addWidget(main_widget)

        self.title_container = QWidget()
        self.title_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        title_container_layout = QHBoxLayout(self.title_container)
        title_container_layout.setContentsMargins(5, 5, 5, 5)
        title_container_layout.setSpacing(10)
        

        

        self.title_label = EditableLabel("Bar Tracker")
        self.title_label.setFont(QFont(FONT[0], 24, QFont.Weight.Bold))
        self.title_label.setStyleSheet(f"""
            color: {COLOR3};
            background-color: {COLOR1};
            border: 2px solid {COLOR_BORDER};
            border-radius: 8px;
            padding: 10px;
            margin: 5px;
        """)
        self.title_label.setMinimumHeight(70)
        self.title_label.setMaximumHeight(70)  # Prevent expansion
        self.title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        title_container_layout.addWidget(self.title_label, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        
        main_layout.addWidget(self.title_container, 0, 0, 1, 3)

        weight_container = QWidget()
        weight_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        weight_layout = QVBoxLayout(weight_container)
        weight_layout.setContentsMargins(10, 10, 10, 10)
        weight_layout.setSpacing(5)
        weight_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.current_weight_label = QLabel(f"{self.current_weight_lb} lbs / {self.current_weight_kg} kg")
        self.current_weight_label.setFont(QFont(FONT[0], 16, QFont.Weight.Bold))
        self.current_weight_label.setStyleSheet(f"color: {COLOR2};")
        self.current_weight_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        weight_layout.addWidget(self.current_weight_label)

        self.conversion_label = QLabel("(Conversions: 3 st)")
        self.conversion_label.setFont(QFont(FONT[0], 10))
        self.conversion_label.setStyleSheet(f"color: {COLOR2};")
        self.conversion_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        weight_layout.addWidget(self.conversion_label)
        
        main_layout.addWidget(weight_container, 1, 1)

        unit_group = QGroupBox("Weight Units")
        unit_layout = QHBoxLayout(unit_group)
        self.weight_unit_group = QButtonGroup(self)
        self.lb_radio = QRadioButton("Lbs")
        self.lb_radio.setChecked(True)
        self.kg_radio = QRadioButton("Kgs")
        self.st_radio = QRadioButton("St")
        self.weight_unit_group.addButton(self.lb_radio)
        self.weight_unit_group.addButton(self.kg_radio)
        self.weight_unit_group.addButton(self.st_radio)
        unit_layout.addWidget(self.lb_radio)
        unit_layout.addWidget(self.kg_radio)
        unit_layout.addWidget(self.st_radio)
        main_layout.addWidget(unit_group, 1, 0)
        self.lb_radio.toggled.connect(self.update_weight_buttons)
        self.kg_radio.toggled.connect(self.update_weight_buttons)
        self.st_radio.toggled.connect(self.update_weight_buttons)

        rounding_group = QGroupBox("Rounding Options")
        rounding_layout = QVBoxLayout(rounding_group)
        self.rounding_checkbox = QCheckBox("Enable Rounding to 2.5")
        self.rounding_checkbox.stateChanged.connect(self.update_weight)
        rounding_layout.addWidget(self.rounding_checkbox)
        main_layout.addWidget(rounding_group, 1, 2)

        self.add_buttons_widget = QWidget()
        self.add_buttons_layout = QHBoxLayout(self.add_buttons_widget)
        self.add_buttons_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        main_layout.addWidget(self.add_buttons_widget, 2, 0, 1, 3)

        self.subtract_buttons_widget = QWidget()
        self.subtract_buttons_layout = QHBoxLayout(self.subtract_buttons_widget)
        self.subtract_buttons_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        main_layout.addWidget(self.subtract_buttons_widget, 3, 0, 1, 3)

        self.update_weight_buttons()

    def setup_theme_controls(self):
        theme_group = QGroupBox("Themes")
        theme_layout = QVBoxLayout(theme_group)
        self.layout.addWidget(theme_group)

        filter_layout = QHBoxLayout()
        theme_layout.addLayout(filter_layout)

        self.theme_filter_entry = QLineEdit()
        self.theme_filter_entry.setPlaceholderText("Filter themes...")
        self.theme_filter_entry.textChanged.connect(self.filter_themes)
        filter_layout.addWidget(self.theme_filter_entry)

        self.theme_filter_var = "All"
        self.all_radio = QRadioButton("All")
        self.kg_radio_theme = QRadioButton("Kgs")
        self.lb_radio_theme = QRadioButton("Lbs")
        self.other_radio = QRadioButton("Other")
        self.all_radio.setChecked(True)
        filter_layout.addWidget(self.all_radio)
        filter_layout.addWidget(self.kg_radio_theme)
        filter_layout.addWidget(self.lb_radio_theme)
        filter_layout.addWidget(self.other_radio)
        self.all_radio.toggled.connect(lambda: self.set_theme_filter("All"))
        self.kg_radio_theme.toggled.connect(lambda: self.set_theme_filter("kg_"))
        self.lb_radio_theme.toggled.connect(lambda: self.set_theme_filter("lb_"))
        self.other_radio.toggled.connect(lambda: self.set_theme_filter("Other"))

        from PyQt6.QtWidgets import QScrollArea

        theme_listbox_container = QScrollArea()
        theme_listbox_container.setWidgetResizable(True)
        theme_listbox_container.setFrameShape(QFrame.Shape.NoFrame)
        theme_listbox_container.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        theme_listbox_container.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        theme_listbox_container.setMinimumHeight(5 * 18)  # Approximate 5 items, adjust as needed
        theme_listbox_container.setMaximumHeight(5 * 18)

        self.theme_listbox = QListWidget()
        self.theme_listbox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.theme_listbox.setStyleSheet(f"""
            background-color: {COLOR1};
            color: {COLOR2};
            border: 1px solid {COLOR_BORDER};
            selection-background-color: {COLOR_SELECTION_BG};
            selection-color: {COLOR_SELECTION_FG};
        """)
        theme_listbox_container.setWidget(self.theme_listbox)
        theme_layout.addWidget(theme_listbox_container)
        self.theme_listbox.currentItemChanged.connect(self.on_theme_change_from_listbox)

        self.enlarge_button = QPushButton("🔍 Enlarge Image")
        self.enlarge_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.enlarge_button.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #9c27b0, stop:1 #673ab7);
                color: white;
                border: 2px solid #7b1fa2;
                border-radius: 10px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #ba68c8, stop:1 #9c27b0);
                border: 2px solid #ab47bc;
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #673ab7, stop:1 #512da8);
            }}
        """)
        theme_layout.addWidget(self.enlarge_button)
        self.enlarge_button.clicked.connect(self.open_image_in_window)

        self.example_image_label = QLabel()
        self.example_image_label.setFixedSize(500, 180)
        self.example_image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        theme_layout.addWidget(self.example_image_label, alignment=Qt.AlignmentFlag.AlignCenter)

        theme_layout.addStretch(1)
        self.load_themes()

    def load_themes(self):
        theme_data = load_available_themes(THEME_PATH)
        self.lb_themes = theme_data["lb"]
        self.kg_themes = theme_data["kg"]  
        self.other_themes = theme_data["other"]
        self.all_themes = theme_data["all"]
        self.theme_listbox.clear()
        for theme in self.all_themes:
            self.theme_listbox.addItem(theme)

    def setup_user_pane(self):

        self.user_pane_container = QWidget()
        self.user_pane_layout = QVBoxLayout(self.user_pane_container)

        self.user_pane_container.setStyleSheet(f"background-color: {COLOR1}; border-left: 2px solid {COLOR_BORDER};")
        self.user_pane_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        filter_sort_layout = QHBoxLayout()
        self.user_filter_entry = QLineEdit()
        self.user_filter_entry.setPlaceholderText("Filter users...")
        self.user_filter_entry.textChanged.connect(self.filter_and_sort_users)
        filter_sort_layout.addWidget(self.user_filter_entry)

        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_users)
        self.refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {COLOR_INFO}, stop:1 #1565c0);
                color: white;
                border: 2px solid #0277bd;
                border-radius: 10px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 11px;
                min-width: 70px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #42a5f5, stop:1 {COLOR_INFO});
                border: 2px solid #29b6f6;
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #1565c0, stop:1 #0d47a1);
            }}
        """)
        filter_sort_layout.addWidget(self.refresh_btn)

        self.import_btn = QPushButton("📥 Import")
        self.import_btn.setToolTip("Import users from a CSV file (replaces current users)")
        self.import_btn.clicked.connect(self.import_users_from_csv)
        self.import_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {COLOR_SUCCESS}, stop:1 #2e7d32);
                color: white;
                border: 2px solid #388e3c;
                border-radius: 10px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 11px;
                min-width: 70px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #66bb6a, stop:1 {COLOR_SUCCESS});
                border: 2px solid #4caf50;
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2e7d32, stop:1 #1b5e20);
            }}
        """)
        filter_sort_layout.addWidget(self.import_btn)

        self.export_btn = QPushButton("📤 Export")
        self.export_btn.clicked.connect(self.export_users)
        self.export_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {COLOR_WARNING}, stop:1 #f57c00);
                color: white;
                border: 2px solid #ff9800;
                border-radius: 10px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 11px;
                min-width: 70px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #ffb74d, stop:1 #f57c00);
                border: 2px solid #ffb74d;
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #f57c00, stop:1 #e65100);
            }}
        """)
        filter_sort_layout.addWidget(self.export_btn)

        self.user_columns = [
            "First", "Last", "Age", "Weight_LB", "Weight_KG", "Sex",
            *LIFT_COLS,
            "Total", "DOTS", "Wilks", "Wilks2", "IPF", "IPF_GL"
        ]

        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            "First", "Last", "Age", "Weight_LB", "Weight_KG", "Sex",
            *LIFT_COLS,
            "Total", "DOTS", "Wilks", "Wilks2", "IPF", "IPF_GL"
        ])
        self.sort_combo.currentIndexChanged.connect(self.filter_and_sort_users)
        filter_sort_layout.addWidget(self.sort_combo)
        self.user_pane_layout.addLayout(filter_sort_layout)

        btns_layout = QHBoxLayout()
        self.add_user_btn = QPushButton("➕ Add")
        self.add_user_btn.clicked.connect(self.open_add_user_dialog)
        self.add_user_btn.setFixedWidth(70)
        self.add_user_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {COLOR_SUCCESS}, stop:1 #2e7d32);
                color: white;
                border: 2px solid #388e3c;
                border-radius: 8px;
                padding: 4px 8px;
                font-weight: bold;
                font-size: 10px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #66bb6a, stop:1 {COLOR_SUCCESS});
                border: 2px solid #4caf50;
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2e7d32, stop:1 #1b5e20);
            }}
        """)
        btns_layout.addWidget(self.add_user_btn)
        
        self.remove_user_btn = QPushButton("🗑️")
        self.remove_user_btn.clicked.connect(self.remove_selected_user)  # Connect remove logic
        self.remove_user_btn.setFixedWidth(50)
        self.remove_user_btn.setToolTip("Remove selected user")
        self.remove_user_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #ff7043, stop:1 #d84315);
                color: white;
                border: 2px solid #ff5722;
                border-radius: 8px;
                padding: 4px 8px;
                font-weight: bold;
                font-size: 10px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #ff8a65, stop:1 #ff7043);
                border: 2px solid #ff8a65;
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #d84315, stop:1 #bf360c);
            }}
        """)
        btns_layout.addWidget(self.remove_user_btn)
        

        self.confirm_remove_checkbox = QCheckBox("Confirm before removing")
        self.confirm_remove_checkbox.setChecked(True)  # Default to confirming
        self.confirm_remove_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {COLOR2};
                font-size: 9px;
                padding: 2px;
            }}
        """)
        btns_layout.addWidget(self.confirm_remove_checkbox)
        

        btns_layout.addStretch(1)
        

        self.purge_btn = QPushButton("Purge")
        self.purge_btn.setFixedWidth(60)
        self.purge_btn.setStyleSheet(
            "QPushButton {"
            "  border: 2px solid #8B0000;"
            "  color: #8B0000;"
            "  background-color: #fff0f0;"
            "  border-radius: 6px;"
            "  font-weight: bold;"
            "  padding: 2px 6px;"
            "}"
            "QPushButton:hover {"
            "  background-color: #ffe0e0;"
            "  border: 2.5px solid #8B0000;"
            "}"
        )
        self.purge_btn.clicked.connect(self.purge_users)
        btns_layout.addWidget(self.purge_btn)



        self.user_pane_layout.addLayout(btns_layout)

        self.users = self.load_users_from_csv()
        self.filtered_sorted_users = self.users.copy()
        self.current_user_idx = 0

        self.user_table = QTableWidget()
        self.user_table.setColumnCount(len(self.user_columns))
        self.user_table.setHorizontalHeaderLabels(self.user_columns)
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.user_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.user_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.user_table.setMinimumHeight(300)  # Set larger default minimum height
        self.user_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.user_pane_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.user_table.verticalHeader().setVisible(False)
        self.user_table.setShowGrid(True)
        self.user_table.setStyleSheet(f"background-color: {COLOR1}; color: {COLOR2};")
        self.user_table.itemSelectionChanged.connect(self.on_user_table_selected)

        self.user_table.horizontalHeader().setSectionsMovable(True)
        self.user_table.horizontalHeader().setSectionsClickable(True)
        self.user_table.horizontalHeader().setStretchLastSection(False)
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        self.user_table.cellDoubleClicked.connect(self.open_edit_user_dialog)

        self.user_pane_layout.addWidget(self.user_table, stretch=1)  # Make table expand

        self.user_detail_group = QGroupBox("Current User")
        self.user_detail_group.setStyleSheet("QGroupBox::title { font-weight: bold; }")
        self.user_detail_group.setMaximumWidth(400)
        self.user_detail_layout = QVBoxLayout(self.user_detail_group)
        self.user_name_label = QLabel()
        self.user_stats_label = QLabel()
        self.user_stats_label.setFont(QFont(FONT[0], 11))
        self.user_detail_layout.addWidget(self.user_name_label)
        self.user_detail_layout.addWidget(self.user_stats_label)

        self.lifts_table = QTableWidget(3, 3)
        self.lifts_table.setHorizontalHeaderLabels(["Squat", "Bench", "Deadlift"])
        self.lifts_table.setVerticalHeaderLabels(["1", "2", "3"])
        self.lifts_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.lifts_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.lifts_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.lifts_table.setFixedHeight(100)
        self.user_detail_layout.addWidget(self.lifts_table)

        self.user_pane_layout.addWidget(self.user_detail_group)

        self.next_user_group = QGroupBox("Up Next,")
        self.next_user_group.setStyleSheet("QGroupBox::title { font-weight: bold; }")
        self.next_user_group.setMaximumWidth(200)
        self.next_user_layout = QVBoxLayout(self.next_user_group)
        self.next_user_label = QLabel()
        self.next_user_layout.addWidget(self.next_user_label)
        self.user_pane_layout.addWidget(self.next_user_group)

        btn_layout = QHBoxLayout()
        self.prev_btn = QPushButton("⬅️ Prev")
        self.prev_btn.clicked.connect(self.prev_user)
        self.prev_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #607d8b, stop:1 #455a64);
                color: white;
                border: 2px solid #546e7a;
                border-radius: 12px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #78909c, stop:1 #607d8b);
                border: 2px solid #78909c;
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #455a64, stop:1 #37474f);
            }}
        """)
        btn_layout.addWidget(self.prev_btn)
        
        self.next_btn = QPushButton("Next ➡️")
        self.next_btn.clicked.connect(self.next_user)
        self.next_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #607d8b, stop:1 #455a64);
                color: white;
                border: 2px solid #546e7a;
                border-radius: 12px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #78909c, stop:1 #607d8b);
                border: 2px solid #78909c;
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #455a64, stop:1 #37474f);
            }}
        """)
        btn_layout.addWidget(self.next_btn)
        self.user_pane_layout.addLayout(btn_layout)

        self.user_pane_layout.addStretch(1)

        self.populate_user_table()
        if self.filtered_sorted_users:
            self.user_table.selectRow(0)
            self.display_user(0)

    def prev_user(self):
        if not self.filtered_sorted_users:
            return
        prev_idx = (self.current_user_idx - 1) % len(self.filtered_sorted_users)
        self.display_user(prev_idx)


    def compute_dots(self, sex: str, bodyweight_kg: str, total_kg: float) -> str:
        """Compute DOTS score for powerlifting."""
        return compute_dots(sex, bodyweight_kg, total_kg)

    def update_all_scores(self):
        update_user_scores(self.users)
        update_user_scores(self.filtered_sorted_users)

    def populate_user_table(self):
        self.update_all_scores()
        self.user_table.setRowCount(len(self.filtered_sorted_users))
        for row, user in enumerate(self.filtered_sorted_users):
            for col, key in enumerate(self.user_columns):
                self.user_table.setItem(row, col, QTableWidgetItem(user.get(key, "")))

    def filter_and_sort_users(self):
        filter_text = self.user_filter_entry.text().lower()
        sort_key = self.sort_combo.currentText()
        self.update_all_scores()
        self.filtered_sorted_users = filter_users_text(self.users, filter_text)
        self.filtered_sorted_users = sort_users_by_column(self.filtered_sorted_users, sort_key)
        self.populate_user_table()
        if self.filtered_sorted_users:
            self.user_table.selectRow(0)
            self.display_user(0)
        else:
            self.user_name_label.setText("No users")
            self.user_stats_label.setText("")
            self.next_user_label.setText("")

            for i in range(3):
                for j in range(3):
                    item = QTableWidgetItem("")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.lifts_table.setItem(i, j, item)

    def display_user(self, idx):
        if not self.filtered_sorted_users:
            self.user_name_label.setText("No users")
            self.user_stats_label.setText("")
            self.next_user_label.setText("")

            for i in range(3):
                for j in range(3):
                    item = QTableWidgetItem("")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.lifts_table.setItem(i, j, item)
            return
        user = self.filtered_sorted_users[idx]

        first = user.get('First', '')
        last = user.get('Last', '')
        sex = user.get('Sex', '')
        weight_lb = user.get('Weight_LB', '')
        weight_kg = user.get('Weight_KG', '')
        self.user_name_label.setText(f"<b>{first} {last}</b> ({sex})")
        self.user_stats_label.setText(
            f"BodyWeight: {weight_lb} lbs / {weight_kg} kg"
        )

        for i, lift in enumerate(["Squat", "Bench", "Deadlift"]):
            for j in range(1, 4):
                key = f"{lift}{j}"
                value = user.get(key, "")
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.lifts_table.setItem(j-1, i, item)

        next_idx = (idx + 1) % len(self.filtered_sorted_users)
        next_user = self.filtered_sorted_users[next_idx]
        next_first = next_user.get('First', '')
        next_last = next_user.get('Last', '')
        self.next_user_label.setText(
            f"{next_first} {next_last}"
        )
        self.current_user_idx = idx
        self.user_table.selectRow(idx)

    def next_user(self):
        if not self.filtered_sorted_users:
            return
        next_idx = (self.current_user_idx + 1) % len(self.filtered_sorted_users)
        self.display_user(next_idx)

    def load_users_from_csv(self):
        return load_users_from_csv()

    def load_judge_scores(self):
        return load_judge_scores()

    def save_judge_scores(self):
        base_path = resource_path("")
        judge_csv = os.path.join(base_path, "data", "judge_scores.csv")
        os.makedirs(os.path.dirname(judge_csv), exist_ok=True)
        fieldnames = ["User", "Judge", "Score"]
        try:
            with open(judge_csv, "w", newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for user in self.filtered_sorted_users:
                    writer.writerow({"User": f"{user.get('First')} {user.get('Last')}", "Judge": "Judge1", "Score": "9"})
                    writer.writerow({"User": f"{user.get('First')} {user.get('Last')}", "Judge": "Judge2", "Score": "8"})
        except Exception as e:
            self.display_message(f"Error saving judge scores: {e}")

    def toggle_user_pane(self):
        """Toggle visibility of the user management pane."""
        if self.toggle_user_pane_btn.isChecked():

            self.user_pane_container.setVisible(True)
            self.toggle_user_pane_btn.setText("👥 Users")
            self.toggle_user_pane_btn.setToolTip("Hide user management pane")
        else:

            self.user_pane_container.setVisible(False)
            self.toggle_user_pane_btn.setText("👥 Show")
            self.toggle_user_pane_btn.setToolTip("Show user management pane")

    def toggle_title_visibility(self):
        """Toggle visibility of the title container to allow layout collapsing."""
        if self.toggle_title_btn.isChecked():

            self.title_container.setVisible(False)
            self.toggle_title_btn.setText("👁️ Show Title")
            self.toggle_title_btn.setToolTip("Show title")
        else:

            self.title_container.setVisible(True)
            self.toggle_title_btn.setText("👁️ Hide Title")
            self.toggle_title_btn.setToolTip("Hide title")

    def open_image_in_window(self):

        if hasattr(self, "_current_combined_pixmap") and self._current_combined_pixmap and not self._current_combined_pixmap.isNull():

            if self.enlarged_image_window and self.enlarged_image_window.isVisible():
                self._update_enlarged_image_from_pixmap(self._current_combined_pixmap)
                self.enlarged_image_window.raise_()
                self.enlarged_image_window.activateWindow()
                return
            

            self.enlarged_image_window = QDialog(self)
            self.enlarged_image_window.setWindowTitle("🔍 Enlarged Barbell Preview")
            self.enlarged_image_window.setMinimumSize(300, 300)
            self.enlarged_image_window.resize(800, 600)
            

            self.enlarged_image_window.setStyleSheet(f"""
                QDialog {{
                    background-color: {COLOR1};
                    color: {COLOR2};
                }}
                QLabel {{
                    background-color: {COLOR1};
                    color: {COLOR2};
                    border: 2px solid {COLOR_BORDER};
                    border-radius: 8px;
                    padding: 10px;
                }}
            """)
            

            vbox = QVBoxLayout(self.enlarged_image_window)
            vbox.setContentsMargins(20, 20, 20, 20)
            vbox.setSpacing(10)
            

            title_label = QLabel("Barbell Configuration Preview")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 16px;
                    font-weight: bold;
                    color: {COLOR3};
                    background-color: transparent;
                    border: none;
                    padding: 5px;
                }}
            """)
            vbox.addWidget(title_label)
            

            self.enlarged_image_label = QLabel()
            self.enlarged_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.enlarged_image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.enlarged_image_label.setMinimumSize(280, 280)
            vbox.addWidget(self.enlarged_image_label)
            

            self.enlarged_weight_label = QLabel(f"Weight: {self.current_weight_lb} lbs / {self.current_weight_kg} kg")
            self.enlarged_weight_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.enlarged_weight_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 14px;
                    font-weight: bold;
                    color: {COLOR2};
                    background-color: transparent;
                    border: none;
                    padding: 5px;
                }}
            """)
            vbox.addWidget(self.enlarged_weight_label)
            

            self._update_enlarged_image_from_pixmap(self._current_combined_pixmap)
            self.enlarged_image_window.setModal(False)
            

            self.enlarged_image_window.resizeEvent = self._enlarged_image_resize_event
            self.enlarged_image_window.show()
        else:
            self.display_message("No image available to enlarge. Please select a theme and weight first.")

    def _enlarged_image_resize_event(self, event):

        if (hasattr(self, "enlarged_image_label") and self.enlarged_image_label and 
            hasattr(self, "_current_combined_pixmap") and self._current_combined_pixmap and 
            not self._current_combined_pixmap.isNull()):
            self._update_enlarged_image_from_pixmap(self._current_combined_pixmap)
            

            if hasattr(self, "enlarged_weight_label") and self.enlarged_weight_label:
                self.enlarged_weight_label.setText(f"Weight: {self.current_weight_lb} lbs / {self.current_weight_kg} kg")
        event.accept()

    def _update_enlarged_image_from_pixmap(self, pixmap: QPixmap) -> None:
        """Update enlarged image window from cached pixmap with improved scaling."""
        if hasattr(self, "enlarged_image_label") and self.enlarged_image_label and pixmap and not pixmap.isNull():

            label_size = self.enlarged_image_label.size()
            

            target_width = max(label_size.width() - 20, 250)  # 10px margin on each side
            target_height = max(label_size.height() - 20, 250)  # 10px margin on top/bottom
            

            if target_width < 100 or target_height < 100:
                if hasattr(self, "enlarged_image_window") and self.enlarged_image_window:
                    window_size = self.enlarged_image_window.size()
                    target_width = max(window_size.width() - 100, 400)
                    target_height = max(window_size.height() - 150, 400)
                else:
                    target_width, target_height = 500, 400
            

            scaled_pixmap = pixmap.scaled(
                target_width, target_height,
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            self.enlarged_image_label.setPixmap(scaled_pixmap)

    def update_example_image(self, image_name: str) -> None:
        """Update the example image with aggressive caching and in-memory processing."""
        if not Image:
            self.display_message("PIL/Pillow not available for image processing")
            return
            
        selected_theme = getattr(self, "theme_var", "")
        cache_key = f"{selected_theme}_{image_name}"
        

        if cache_key in self._image_cache:
            pixmap = self._image_cache[cache_key]
            self._set_image_pixmap(pixmap)
            return
        
        base_path = os.path.dirname(__file__)
        
        if os.path.exists(image_name):
            image_path = image_name
        else:
            image_path = get_image_path(selected_theme, image_name)
        
        if os.path.exists(image_path):
            try:
                combined_pixmap = self._create_combined_image_pixmap(image_path, selected_theme)
                if combined_pixmap and not combined_pixmap.isNull():
                    self._image_cache[cache_key] = combined_pixmap
                    self._set_image_pixmap(combined_pixmap)
                else:
                    self._show_fallback_image(selected_theme)
                    
            except Exception as e:
                self.display_message(f"Image error: {e}")
                self._show_fallback_image(selected_theme)
        else:
            self._show_fallback_image(selected_theme)

    def _create_combined_image_pixmap(self, image_path: str, selected_theme: str) -> QPixmap:
        """Create combined image pixmap in memory without file I/O."""
        return create_combined_image_pixmap(image_path, selected_theme, self._static_image_cache)

    def _get_cached_static_image(self, selected_theme: str):
        """Get cached static bar image or create and cache it."""
        return get_cached_static_image(selected_theme, self._static_image_cache)

    def _pil_to_pixmap(self, pil_image) -> QPixmap:
        """Convert PIL image to QPixmap without file I/O."""
        return pil_to_pixmap(pil_image)

    def _set_image_pixmap(self, pixmap: QPixmap) -> None:
        """Set pixmap to image label with optimized scaling."""
        if pixmap and not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                self.example_image_label.size(), 
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.FastTransformation  # Use fast transformation
            )
            self.example_image_label.setPixmap(scaled_pixmap)
            self._current_combined_pixmap = pixmap
            

            if hasattr(self, 'enlarged_image_window') and self.enlarged_image_window and self.enlarged_image_window.isVisible():
                self._update_enlarged_image_from_pixmap(pixmap)
    
    def _show_fallback_image(self, selected_theme: str) -> None:
        """Show fallback image when main image is not available."""
        fallback_cache_key = f"{selected_theme}_fallback"
        

        if fallback_cache_key in self._image_cache:
            pixmap = self._image_cache[fallback_cache_key]
            self._set_image_pixmap(pixmap)
            return
        
        fallback_image_path = get_image_path(selected_theme, "none.png")
        if os.path.exists(fallback_image_path):
            try:
                combined_pixmap = self._create_combined_image_pixmap(fallback_image_path, selected_theme)
                if combined_pixmap and not combined_pixmap.isNull():
                    self._image_cache[fallback_cache_key] = combined_pixmap
                    self._set_image_pixmap(combined_pixmap)
                else:
                    self.example_image_label.clear()
                    self._current_combined_pixmap = None
            except Exception as e:
                print(f"Error loading fallback image: {e}")
                self.example_image_label.clear()
                self._current_combined_pixmap = None
        else:
            self.example_image_label.clear()
            self._current_combined_pixmap = None

    def open_github(self) -> None:
        """Open GitHub repository in browser."""
        QDesktopServices.openUrl(QUrl(APP_GITHUB_REPO))

    def display_message(self, message: str) -> None:
        """Display message to user."""
        self.message_label.setText(message)

        if hasattr(self, '_message_timer'):
            self._message_timer.stop()
        self._message_timer = QTimer()
        self._message_timer.setSingleShot(True)
        self._message_timer.timeout.connect(lambda: self.message_label.setText(""))
        self._message_timer.start(5000)

    def update_weight_buttons(self) -> None:
        """Update weight increment/decrement buttons based on selected unit."""

        self._clear_layout(self.add_buttons_layout)
        self._clear_layout(self.subtract_buttons_layout)

        if self.lb_radio.isChecked():
            increments = [1.75, 2.5, 5, 10, 25, 35, 45, 55]
        elif self.kg_radio.isChecked():
            increments = [1, 2.5, 5, 10, 15, 20, 25]
        else:
            increments = []

        for inc in increments:
            btn = QPushButton(f"+{inc}")
            btn.clicked.connect(lambda checked, amount=inc: self.adjust_weight(amount))
            self.add_buttons_layout.addWidget(btn)
            
        for inc in increments:
            btn = QPushButton(f"-{inc}")
            btn.clicked.connect(lambda checked, amount=-inc: self.adjust_weight(amount))
            self.subtract_buttons_layout.addWidget(btn)

    def _clear_layout(self, layout: QHBoxLayout) -> None:
        """Efficiently clear all widgets from a layout."""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def adjust_weight(self, amount: float) -> None:
        """Adjust weight by the specified amount with optimization."""
        self.display_message("")
        unit = "Pounds" if self.lb_radio.isChecked() else ("Kilograms" if self.kg_radio.isChecked() else "Stone")
        selected_theme = getattr(self, "theme_var", "").lower()
        is_dumbell_theme = "dumbell" in selected_theme or "dumbbell" in selected_theme

        if is_dumbell_theme:
            self.rounding_checkbox.setChecked(True)

        effective_amount = amount if is_dumbell_theme else amount * 2
        min_weight = 5 if is_dumbell_theme else 45
        max_weight = 120 if is_dumbell_theme else (900 if unit == "Pounds" else 855)

        if unit == "Pounds":
            self.current_weight_lb = max(min_weight, min(max_weight, 
                                       round(self.current_weight_lb + effective_amount)))
            self.current_weight_kg = self.current_weight_lb / CONVERSION_FACTOR_LB_TO_KG
        elif unit == "Kilograms":
            self.current_weight_kg = round(self.current_weight_kg + effective_amount)
            self.current_weight_lb = self.current_weight_kg * CONVERSION_FACTOR_LB_TO_KG
            

            if self.current_weight_lb < min_weight:
                self.current_weight_lb = min_weight
                self.current_weight_kg = self.current_weight_lb / CONVERSION_FACTOR_LB_TO_KG
            elif self.current_weight_lb > max_weight:
                self.current_weight_lb = max_weight
                self.current_weight_kg = self.current_weight_lb / CONVERSION_FACTOR_LB_TO_KG
        
        self.update_weight()

    def update_weight(self) -> None:
        """Update weight display with proper rounding."""
        self.display_message("")
        rounding = 2.5 if self.rounding_checkbox.isChecked() else IMAGE_ROUNDING
        rounded_weight_lb = round_weight(self.current_weight_lb, rounding)
        rounded_weight_kg = round_weight(self.current_weight_kg, rounding)
        
        self.current_weight_label.setText(f"{rounded_weight_lb:.1f} lbs / {rounded_weight_kg:.1f} kg")
        self.calculate_weight()
        
        rounded_weight_str = f"{int(rounded_weight_lb)}" if rounded_weight_lb.is_integer() else f"{rounded_weight_lb:.1f}"
        self.update_example_image(f"{rounded_weight_str}.png")
        

        if (hasattr(self, 'enlarged_image_window') and self.enlarged_image_window and 
            self.enlarged_image_window.isVisible() and hasattr(self, 'enlarged_weight_label')):
            self.enlarged_weight_label.setText(f"Weight: {rounded_weight_lb:.1f} lbs / {rounded_weight_kg:.1f} kg")

    def calculate_weight(self) -> None:
        """Calculate and update weight conversions."""
        try:
            self.update_conversions(self.current_weight_kg)
        except Exception as e:
            self.display_message(f"Calculation error: {str(e)}")

    def update_conversions(self, weight_in_kg: float) -> None:
        """Update weight conversions display."""
        stone = round(weight_in_kg / CONVERSION_FACTOR_KG_TO_STONE)
        self.conversion_label.setText(f"(Conversions: {stone} st)")

    def set_theme_filter(self, prefix):
        self.theme_filter_var = prefix
        self.filter_themes()

    def filter_themes(self):
        filter_text = self.theme_filter_entry.text()
        theme_data = {
            "all": self.all_themes,
            "lb": self.lb_themes,
            "kg": self.kg_themes,
            "other": self.other_themes
        }
        filtered = filter_themes_by_category(theme_data, self.theme_filter_var)
        filtered = filter_themes_by_text(filtered, filter_text)
        self.theme_listbox.clear()
        for theme in filtered:
            self.theme_listbox.addItem(theme)

    def on_theme_change_from_listbox(self):
        item = self.theme_listbox.currentItem()
        if item:
            self.theme_var = item.text()
            self.on_theme_change()

    def on_theme_change(self):
        selected_theme = getattr(self, "theme_var", None)
        if not selected_theme:
            return
        

        self._clear_theme_cache()
        

        rounding = 2.5 if self.rounding_checkbox.isChecked() else IMAGE_ROUNDING
        rounded_weight_lb = round_weight(self.current_weight_lb, rounding)
        rounded_weight_str = f"{int(rounded_weight_lb)}" if rounded_weight_lb.is_integer() else f"{rounded_weight_lb:.1f}"
        
        base_path = os.path.dirname(__file__)
        theme_folder = os.path.join(base_path, THEME_PATH, selected_theme)
        image_path = os.path.join(theme_folder, f"{rounded_weight_str}.png")
        
        if not os.path.exists(image_path):

            fallback_image_path = os.path.join(theme_folder, "none.png")
            if os.path.exists(fallback_image_path):
                self.update_example_image("none.png")
            else:
                self.display_message(f"Theme image not found for {selected_theme}.")
        else:
            self.update_example_image(f"{rounded_weight_str}.png")

    def _clear_theme_cache(self):
        """Clear image cache when theme changes."""
        self._image_cache.clear()
        self._static_image_cache.clear()

    def set_default_theme(self):
        if self.theme_listbox.count() > 0:
            self.theme_listbox.setCurrentRow(0)
            self.on_theme_change_from_listbox()

    def showEvent(self, event):
        super().showEvent(event)

    def resizeEvent(self, event):
        """Handle window resize events."""
        super().resizeEvent(event)

    def moveEvent(self, event):
        super().moveEvent(event)

    def closeEvent(self, event):

        self.cleanup_temp_files()
        super().closeEvent(event)

    def exit_all(self):

        self.cleanup_temp_files()
        self.close()

    def on_user_table_selected(self):
        selected = self.user_table.selectedItems()
        if selected:
            row = self.user_table.currentRow()
            self.display_user(row)

    def open_add_user_dialog(self):
        dialog = AddUserDialog(self)
        if dialog.exec():
            user_data = dialog.get_user_data()

            is_valid, error_message = validate_user_data(user_data)
            if not is_valid:
                self.display_message(error_message)
                return
            self.users.append(user_data)
            self.save_users_to_csv()  # Save after adding
            self.filter_and_sort_users()

            idx = self.filtered_sorted_users.index(user_data)
            self.user_table.selectRow(idx)
            self.display_user(idx)

    def remove_selected_user(self):
        selected = self.user_table.selectedItems()
        if not selected:
            self.display_message("No user selected to remove.")
            return
        row = self.user_table.currentRow()
        if row < 0 or row >= len(self.filtered_sorted_users):
            self.display_message("Invalid user selection.")
            return
        
        user_to_remove = self.filtered_sorted_users[row]
        user_name = f"{user_to_remove.get('First', '')} {user_to_remove.get('Last', '')}"
        

        if self.confirm_remove_checkbox.isChecked():

            reply = QMessageBox.question(
                self,
                "Confirm User Removal",
                f"Are you sure you want to remove user:\n\n{user_name}\n\nThis action will move the user to removed.csv and cannot be undone.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
        

        try:
            self.users.remove(user_to_remove)
        except ValueError:
            pass  # Already removed
        

        save_removed_user(user_to_remove)
        

        self.save_users_to_csv()
        self.filter_and_sort_users()

        if self.filtered_sorted_users:
            idx = min(row, len(self.filtered_sorted_users) - 1)
            self.user_table.selectRow(idx)
            self.display_user(idx)
        else:
            self.user_name_label.setText("No users")
            self.user_stats_label.setText("")
            self.next_user_label.setText("")

    def purge_users(self):

        reply = QMessageBox.warning(
            self,
            "Confirm Purge",
            "This will move all user data to a dated backup and clear the user list. This cannot be undone.\n\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        

        backup_path = backup_users_data()
        if backup_path:

            self.users = []
            self.filtered_sorted_users = []
            self.save_users_to_csv()  # Save empty list
            self.populate_user_table()
            self.user_name_label.setText("No users")
            self.user_stats_label.setText("")
            self.next_user_label.setText("")
            for i in range(3):
                for j in range(3):
                    self.lifts_table.setItem(i, j, QTableWidgetItem(""))
            self.display_message(f"All users purged to {os.path.basename(backup_path)}.")
        else:
            self.display_message("Purge failed")

    def save_users_to_csv(self):
        self.update_all_scores()
        if save_users_to_csv(self.users):
            pass  # Success - no message needed
        else:
            self.display_message("Error saving users")

    def refresh_users(self):
        self.users = self.load_users_from_csv()
        self.filter_and_sort_users()
        self.display_message("User data reloaded.")

    def export_users(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Export Users", "users_export.csv", "CSV Files (*.csv)")
        if not filename:
            return
        self.update_all_scores()
        if export_users_to_csv_file(self.filtered_sorted_users, filename):
            self.display_message(f"Exported {len(self.filtered_sorted_users)} users to {filename}")
        else:
            self.display_message("Export failed")

    def import_users_from_csv(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Import Users from CSV", "", "CSV Files (*.csv)")
        if not filename:
            return
        users = import_users_from_csv_file(filename)
        if users:
            self.users = users
            self.save_users_to_csv()
            self.filter_and_sort_users()
            self.display_message(f"Imported {len(users)} users from {filename}")
        else:
            self.display_message("No users imported from file.")

    def open_edit_user_dialog(self, row, column):
        if row < 0 or row >= len(self.filtered_sorted_users):
            return
        user = self.filtered_sorted_users[row]
        dialog = EditUserDialog(user, self.user_columns, self)
        if dialog.exec():
            updated_user = dialog.get_user_data()

            for idx, u in enumerate(self.users):
                if all(u.get(k, "") == user.get(k, "") for k in ["First", "Last", "Age", "Sex"]):
                    self.users[idx] = updated_user
                    break

            self.filtered_sorted_users[row] = updated_user
            self.save_users_to_csv()
            self.filter_and_sort_users()
            self.display_user(row)

    def cleanup_temp_files(self):
        """Clean up temporary combined image files and caches."""
        try:

            if hasattr(self, '_image_cache'):
                self._image_cache.clear()
            if hasattr(self, '_static_image_cache'):
                self._static_image_cache.clear()
            

            base_path = resource_path("")
            resources_dir = os.path.join(base_path, "resources")
            cleanup_temp_files(resources_dir)
        except Exception as e:
            print(f"Error during cleanup: {e}")

    def closeEvent(self, event):
        self.cleanup_temp_files()  # Clean up temp files on exit
        if hasattr(self, "user_pane_window") and self.user_pane_window is not None:
            try:
                self.user_pane_window.close()
            except Exception:
                pass
        super().closeEvent(event)

    def open_stopwatch(self):
        """Open the stopwatch tool in a popup dialog."""
        try:
            stopwatch = StopwatchDialog(self)
            stopwatch.show()
        except Exception as e:
            print(f"Error opening stopwatch: {e}")
    
    def open_timer(self):
        """Open the timer tool in a popup dialog."""
        try:
            timer = TimerDialog(self)
            timer.show()
        except Exception as e:
            print(f"Error opening timer: {e}")
    
    def open_rules(self):
        """Open the powerlifting rules URL in the default browser."""
        try:
            open_rules_link()
        except Exception as e:
            print(f"Error opening rules link: {e}")
    
    def cycle_theme(self):
        """Cycle to the next color theme and apply it to the application."""
        try:
            # Get the next theme
            theme_colors = self.theme_manager.get_next_theme()
            
            # Update global color variables
            global COLOR1, COLOR2, COLOR3, COLOR_ACCENT, COLOR_SUCCESS, COLOR_WARNING
            global COLOR_ERROR, COLOR_INFO, COLOR_BORDER, COLOR_BUTTON_BG, COLOR_BUTTON_FG
            global COLOR_BUTTON_HOVER, COLOR_INPUT_BG, COLOR_INPUT_FG, COLOR_SELECTION_BG, COLOR_SELECTION_FG
            
            COLOR1 = theme_colors["background"]
            COLOR2 = theme_colors["text"]
            COLOR3 = theme_colors["highlight"]
            COLOR_ACCENT = theme_colors["accent"]
            COLOR_SUCCESS = theme_colors["success"]
            COLOR_WARNING = theme_colors["warning"]
            COLOR_ERROR = theme_colors["error"]
            COLOR_INFO = theme_colors["info"]
            COLOR_BORDER = theme_colors["border"]
            COLOR_BUTTON_BG = theme_colors["button_bg"]
            COLOR_BUTTON_FG = theme_colors["button_fg"]
            COLOR_BUTTON_HOVER = theme_colors["button_hover"]
            COLOR_INPUT_BG = theme_colors["input_bg"]
            COLOR_INPUT_FG = theme_colors["input_fg"]
            COLOR_SELECTION_BG = theme_colors["selection_bg"]
            COLOR_SELECTION_FG = theme_colors["selection_fg"]
            
            # Apply the theme to the application
            self.apply_theme()
            
            # Update the theme button text to show current theme
            current_theme_name = self.theme_manager.get_current_theme_name()
            self.theme_btn.setText(f"🎨 {current_theme_name}")
            
        except Exception as e:
            print(f"Error cycling theme: {e}")
    
    def apply_theme(self):
        """Apply the current theme colors to all UI elements."""
        try:
            # Update main window stylesheet
            self.central_widget.setStyleSheet(f"""
                background-color: {COLOR1};
                color: {COLOR2};
            """)
            
            # Update main application stylesheet
            self.setStyleSheet(f"""
                QGroupBox {{
                    background-color: {COLOR1};
                    color: {COLOR2};
                    border: 1px solid {COLOR_BORDER};
                    border-radius: 6px;
                    margin-top: 6px;
                }}
                QGroupBox:title {{
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 3px 0 3px;
                }}
                QPushButton {{
                    background-color: {COLOR_BUTTON_BG};
                    color: {COLOR_BUTTON_FG};
                    border-radius: 8px;
                    border: 2px solid {COLOR3};
                    padding: 6px 12px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {COLOR_BUTTON_HOVER};
                    color: {COLOR_BUTTON_FG};
                    border: 2px solid {COLOR_ACCENT};
                }}
                QRadioButton, QCheckBox {{
                    background-color: {COLOR1};
                    color: {COLOR3};
                    font-weight: bold;
                    border: 1.5px solid {COLOR3};
                    border-radius: 6px;
                    padding: 3px 8px;
                    margin: 2px;
                }}
                QRadioButton::indicator, QCheckBox::indicator {{
                    border: 1.5px solid {COLOR3};
                    border-radius: 6px;
                    background: {COLOR1};
                    width: 16px;
                    height: 16px;
                    margin-right: 6px;
                }}
                QRadioButton::indicator:checked {{
                    background-color: {COLOR3};
                    border: 2px solid {COLOR_ACCENT};
                }}
                QRadioButton::indicator:unchecked {{
                    background-color: {COLOR1};
                    border: 1.5px solid {COLOR3};
                }}
                QCheckBox::indicator:checked {{
                    background-color: {COLOR3};
                    border: 2px solid {COLOR_ACCENT};
                }}
                QCheckBox::indicator:unchecked {{
                    background-color: {COLOR1};
                    border: 1.5px solid {COLOR3};
                }}
                QListWidget {{
                    background-color: {COLOR1};
                    color: {COLOR2};
                    border: 1px solid {COLOR_BORDER};
                    selection-background-color: {COLOR_SELECTION_BG};
                    selection-color: {COLOR_SELECTION_FG};
                }}
                QLineEdit {{
                    background-color: {COLOR_INPUT_BG};
                    color: {COLOR_INPUT_FG};
                    border: 1px solid {COLOR_BORDER};
                }}
            """)
            
            # Update header button styles individually to maintain their unique colors
            self.update_header_button_styles()
            
        except Exception as e:
            print(f"Error applying theme: {e}")
    
    def update_header_button_styles(self):
        """Update the header button styles with theme-aware colors."""
        try:
            # Update exit button
            self.exit_button.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 {COLOR_ERROR}, stop:1 #a32f2f);
                    color: white;
                    border: 2px solid #8B0000;
                    border-radius: 12px;
                    padding: 8px 16px;
                    font-weight: bold;
                    font-size: 12px;
                    margin: 0 8px;
                    min-width: 60px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #ff6b6b, stop:1 {COLOR_ERROR});
                    border: 2px solid #ff4444;
                }}
                QPushButton:pressed {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #a32f2f, stop:1 #8B0000);
                }}
            """)
            
            # Update theme button
            self.theme_btn.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #9c27b0, stop:1 #6a1b9a);
                    color: white;
                    border: 2px solid #7b1fa2;
                    border-radius: 12px;
                    padding: 8px 16px;
                    font-weight: bold;
                    font-size: 12px;
                    margin: 0 8px;
                    min-width: 80px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #ba68c8, stop:1 #9c27b0);
                    border: 2px solid #ba68c8;
                }}
                QPushButton:pressed {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #6a1b9a, stop:1 #4a148c);
                }}
            """)
            
            # Update tools button
            self.tools_btn.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 {COLOR_WARNING}, stop:1 #e65100);
                    color: white;
                    border: 2px solid #f57c00;
                    border-radius: 12px;
                    padding: 8px 16px;
                    font-weight: bold;
                    font-size: 12px;
                    margin: 0 8px;
                    min-width: 80px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #ffb74d, stop:1 #f57c00);
                    border: 2px solid #ffb74d;
                }}
                QPushButton:pressed {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #e65100, stop:1 #bf360c);
                }}
            """)
            
            # Update toggle buttons
            self.toggle_title_btn.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 {COLOR_INFO}, stop:1 #1565c0);
                    color: white;
                    border: 2px solid #0277bd;
                    border-radius: 12px;
                    padding: 8px 16px;
                    font-weight: bold;
                    font-size: 12px;
                    margin: 0 8px;
                    min-width: 80px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #42a5f5, stop:1 {COLOR_INFO});
                    border: 2px solid #29b6f6;
                }}
                QPushButton:pressed {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #1565c0, stop:1 #0d47a1);
                }}
                QPushButton:checked {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #66bb6a, stop:1 {COLOR_SUCCESS});
                    border: 2px solid #4caf50;
                }}
            """)
            
            self.toggle_user_pane_btn.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 {COLOR_INFO}, stop:1 #1565c0);
                    color: white;
                    border: 2px solid #0277bd;
                    border-radius: 12px;
                    padding: 8px 16px;
                    font-weight: bold;
                    font-size: 12px;
                    margin: 0 8px;
                    min-width: 70px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #42a5f5, stop:1 {COLOR_INFO});
                    border: 2px solid #29b6f6;
                }}
                QPushButton:pressed {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #1565c0, stop:1 #0d47a1);
                }}
                QPushButton:checked {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #66bb6a, stop:1 {COLOR_SUCCESS});
                    border: 2px solid #4caf50;
                }}
            """)
            
        except Exception as e:
            print(f"Error updating header button styles: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BarbellCalculator()
    window.show()
    # Ensure cleanup happens when the application exits
    try:
        sys.exit(app.exec())
    finally:
        # Final cleanup in case closeEvent wasn't called
        if 'window' in locals():
            # Clean up temp files using the same logic as BarbellCalculator
            base_path = resource_path("")
            resources_dir = os.path.join(base_path, "resources")
            cleanup_temp_files(resources_dir)
