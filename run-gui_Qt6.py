import sys
import os
import json
import csv
import datetime
from typing import Dict, List, Optional, Any
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QRadioButton, QButtonGroup, QCheckBox, QLineEdit, QListWidget, QGroupBox, QScrollArea,
    QGridLayout, QDialog, QFrame, QSizePolicy, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QDialogButtonBox, QStyle, QFileDialog, QMessageBox
)
from PyQt6.QtGui import QPixmap, QFont, QCursor, QIcon
from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtGui import QDesktopServices

try:
    from PIL import Image
except ImportError:
    Image = None  # Handle missing PIL gracefully

# Constants
LIFT_COLS = [
    "Bench1", "Bench2", "Bench3",
    "Squat1", "Squat2", "Squat3",
    "Deadlift1", "Deadlift2", "Deadlift3"
]

CONVERSION_FACTOR_LB_TO_KG = 2.20462
CONVERSION_FACTOR_KG_TO_STONE = 6.35029

def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller .exe."""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def load_config() -> Dict[str, Any]:
    """Load configuration from JSON file with error handling."""
    config_path = resource_path(os.path.join("resources", "config.json"))
    try:
        with open(config_path, "r", encoding='utf-8') as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        # Return default config if file not found
        return {
            "window": {"width": 750, "height": 750},
            "fonts": {"default": ["Consolas", 12], "bold": ["Consolas", 12, "bold"]},
            "colors": {
                "background": "#23272e", "text": "#e0e0e0", "highlight": "#4f8cff",
                "accent": "#ff9800", "success": "#4caf50", "warning": "#ffc107",
                "error": "#f44336", "info": "#2196f3", "border": "#444a52",
                "button_bg": "#2d323b", "button_fg": "#e0e0e0", "button_hover": "#3a4050",
                "input_bg": "#23272e", "input_fg": "#e0e0e0",
                "selection_bg": "#4f8cff", "selection_fg": "#23272e"
            },
            "barbell_types": {
                "Standard": [45, 20],
                "Bella Bar": [35, 15],
                "Power Bar": [45, 20],
                "Deadlift Bar": [45, 20],
                "Squat Bar": [55, 25],
                "EZ Curl Bar": [20, 10],
                "Trap Bar": [55, 25],
                "Safety Squat Bar": [55, 25],
                "Elephant Bar": [60, 28]
            },
            "image": {"rounding": 5},
            "paths": {"theme": "BarBellWeights"},
            "padding": {"default": 3, "button": 1},
            "app": {
                "title": "Barbell Calculator",
                "author": "JonesCKevin",
                "github_repo": "https://github.com/Jonesckevin/Bar_loader_Colored",
                "icon_path": "resources/icon.ico",
                "description": "A visual aid for barbell calculatoring; For weightlifting enthusiasts."
            }
        }
    except json.JSONDecodeError as e:
        print(f"Error loading config: {e}")
        return {}
    except Exception as e:
        print(f"Unexpected error loading config: {e}")
        return {}

def round_weight(weight: float, rounding: float) -> float:
    """Round weight to specified increment."""
    return round(weight / rounding) * rounding

def get_theme_folder(selected_theme: str) -> str:
    """Get theme folder path."""
    base_path = resource_path("")
    return os.path.join(base_path, THEME_PATH, selected_theme)

def get_image_path(theme: str, image_name: str) -> str:
    """Get full image path for theme."""
    folder = get_theme_folder(theme)
    return os.path.join(folder, image_name)

# Load configuration
config = load_config()

# Extract configuration variables
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

# Extract application metadata
APP_TITLE = config["app"]["title"]
APP_AUTHOR = config["app"]["author"]
APP_GITHUB_REPO = config["app"]["github_repo"]
APP_ICON_PATH = config["app"]["icon_path"]
APP_DESCRIPTION = config["app"]["description"]

def compute_wilks(sex: str, bodyweight_kg: str, total_kg: float) -> str:
    """Compute Wilks score for powerlifting."""
    # Wilks coefficients (2017, IPF)
    if sex.lower() == "male":
        a, b, c, d, e, f = -216.0475144, 16.2606339, -0.002388645, -0.00113732, 7.01863e-06, -1.291e-08
    else:
        a, b, c, d, e, f = 594.31747775582, -27.23842536447, 0.82112226871, -0.00930733913, 4.731582e-05, -9.054e-08
    
    try:
        bw = float(bodyweight_kg) if bodyweight_kg else 0
        if bw <= 0 or total_kg <= 0:
            return ""
        coeff = a + b*bw + c*bw**2 + d*bw**3 + e*bw**4 + f*bw**5
        if coeff == 0:
            return ""
        wilks = 500 * float(total_kg) / coeff
        return f"{wilks:.1f}"
    except (ValueError, TypeError):
        return ""


class AddUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("➕ Add New User")
        self.setModal(True)
        self.resize(650, 800)
        self.setMinimumSize(600, 750)
        
        # Apply modern styling
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
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Create scroll area for better organization
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameStyle(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(20)
        
        # Personal Information Group
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
        
                
        # Connect weight conversion signals
        self.weight_lb_edit.textChanged.connect(self._convert_lb_to_kg)
        self.weight_kg_edit.textChanged.connect(self._convert_kg_to_lb)

        # Add personal info fields to layout
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
        
        # Powerlifting Attempts Group
        lifts_group = QGroupBox("🏋️ Powerlifting Attempts")
        lifts_layout = QGridLayout(lifts_group)
        lifts_layout.setSpacing(12)
        lifts_layout.setContentsMargins(15, 25, 15, 15)
        
        # Create lift fields
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
        
        # Add header labels
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
        
        # Add attempt rows
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
        
        # Styled button box
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
            "Wilks": ""
        }


class EditUserDialog(QDialog):
    def __init__(self, user_data, columns, parent=None):
        super().__init__(parent)
        self.setWindowTitle("✏️ Edit User")
        self.setModal(True)
        self.resize(650, 800)
        self.setMinimumSize(600, 750)
        
        # Apply modern styling
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
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Create scroll area for better organization
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameStyle(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(20)
        
        self.fields = {}
        
        # Personal Information Group
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
        
        scroll_layout.addWidget(personal_group)
        
        # Powerlifting Attempts Group
        lifts_group = QGroupBox("🏋️ Powerlifting Attempts")
        lifts_layout = QGridLayout(lifts_group)
        lifts_layout.setSpacing(12)
        lifts_layout.setContentsMargins(15, 25, 15, 15)
        
        # Create lift sections
        lift_types = ["Squat", "Bench", "Deadlift"]
        row = 0
        
        # Add header labels
        lifts_layout.addWidget(QLabel(""), 0, 0)  # Empty corner
        for col, lift_type in enumerate(lift_types):
            header_label = QLabel(f"{lift_type}")
            header_label.setStyleSheet(f"color: {COLOR3}; font-weight: bold; font-size: 14px;")
            lifts_layout.addWidget(header_label, 0, col + 1)
        
        # Add attempt rows
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
        
        # Add any remaining fields that weren't categorized
        other_fields = [col for col in columns if col not in personal_fields + [f"{lift}{num}" for lift in lift_types for num in range(1, 4)] and col != "Wilks"]
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
        
        # Styled button box
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
    
    def get_user_data(self):
        data = {}
        for col, widget in self.fields.items():
            if isinstance(widget, QComboBox):
                data[col] = widget.currentText()
            else:
                data[col] = widget.text()
        data["Wilks"] = ""  # Will be calculated later
        return data


class UserPaneWindow(QMainWindow):
    def __init__(self, user_pane_widget, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Users")
        # Set a larger default size for the user pane
        self.setMinimumSize(700, 800)  # Increased width and height
        self.setCentralWidget(user_pane_widget)
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)

    def showEvent(self, event):
        # Always stay attached to the right of the parent window
        parent = self.parent()
        if parent is not None and parent.isVisible():
            geo = parent.geometry()
            # Remove setFixedHeight to allow resizing
            self.move(geo.x() + geo.width() - 2, geo.y())
            # self.setFixedHeight(geo.height())
        super().showEvent(event)

class BarbellCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        if os.path.exists(APP_ICON_PATH):
            self.setWindowIcon(QIcon(APP_ICON_PATH))
        self.setMinimumSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.central_widget.setStyleSheet(f"""
            background-color: {COLOR1};
            color: {COLOR2};
        """)

        # Set global stylesheet for better visibility
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

        self.setup_header()
        self.setup_main_frame()
        self.setup_theme_controls()
        self.set_default_theme()

        # Main layout: add a horizontal layout for left (main) pane only
        self.outer_layout = QHBoxLayout()

        # Left/main pane
        self.left_widget = QWidget()
        self.left_layout = QVBoxLayout(self.left_widget)
        self.outer_layout.addWidget(self.left_widget, stretch=3)
        self.layout = self.left_layout  # For compatibility with existing code

        # Right/user pane in its own attached window
        self.setup_user_pane()
        self.user_pane_window = UserPaneWindow(self.user_pane_container, parent=self)
        self.user_pane_window.hide()

        # Add show/hide right pane button (middle right of window)
        self.toggle_right_pane_btn = QPushButton()
        self.toggle_right_pane_btn.setFixedWidth(28)
        self.toggle_right_pane_btn.setFixedHeight(60)
        self.toggle_right_pane_btn.setCheckable(True)
        self.toggle_right_pane_btn.setChecked(False)
        self.toggle_right_pane_btn.setStyleSheet(
            f"background-color: {COLOR_BUTTON_BG}; color: {COLOR_BUTTON_FG}; border-radius: 8px; border: 2px solid {COLOR3};"
        )
        # Set initial icon to a user icon (SP_DirHomeIcon is the closest standard Qt icon)
        self.toggle_right_pane_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirHomeIcon))
        self.toggle_right_pane_btn.setIconSize(self.toggle_right_pane_btn.size() * 0.7)
        self.toggle_right_pane_btn.clicked.connect(self.toggle_right_pane_visibility)

        # Overlay the button on the right edge, vertically centered
        self.toggle_right_pane_btn_container = QWidget(self)
        self.toggle_right_pane_btn_container.setFixedWidth(32)
        self.toggle_right_pane_btn_layout = QVBoxLayout(self.toggle_right_pane_btn_container)
        self.toggle_right_pane_btn_layout.addStretch(1)
        self.toggle_right_pane_btn_layout.addWidget(self.toggle_right_pane_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.toggle_right_pane_btn_layout.addStretch(1)
        self.toggle_right_pane_btn_layout.setContentsMargins(0, 0, 0, 0)
        self.toggle_right_pane_btn_container.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.toggle_right_pane_btn.raise_()

        # Place the button container using absolute positioning after show
        self.toggle_right_pane_btn_container.hide()
        self.installEventFilter(self)

        self.enlarged_image_window = None  # Track enlarged image window

    def setup_header(self):
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_widget.setStyleSheet(f"background-color: {COLOR1};")

        author_label = QLabel(f"Author: {APP_AUTHOR}")
        author_label.setFont(QFont(FONT[0], 10))
        author_label.setStyleSheet(f"color: {COLOR2};")

        # Exit button in header, centered
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
                margin: 0 16px;
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

        github_label = QLabel('<a href="#">GitHub Repository</a>')
        github_label.setFont(QFont(FONT[0], 10, QFont.Weight.Bold))
        github_label.setStyleSheet("color: blue; text-decoration: underline;")
        github_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        github_label.linkActivated.connect(self.open_github)

        # Add widgets to header: Author (left), Exit (center), GitHub (right)
        header_layout.addWidget(author_label, alignment=Qt.AlignmentFlag.AlignLeft)
        header_layout.addStretch(1)
        header_layout.addWidget(self.exit_button, alignment=Qt.AlignmentFlag.AlignCenter)
        header_layout.addStretch(1)
        header_layout.addWidget(github_label, alignment=Qt.AlignmentFlag.AlignRight)

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
        main_widget.setStyleSheet(f"background-color: {COLOR1};")
        self.layout.addWidget(main_widget)

        # Weight label
        self.current_weight_label = QLabel(f"{self.current_weight_lb} lbs / {self.current_weight_kg} kg")
        self.current_weight_label.setFont(QFont(FONT[0], 16, QFont.Weight.Bold))
        self.current_weight_label.setStyleSheet(f"color: {COLOR2};")
        main_layout.addWidget(self.current_weight_label, 0, 1)

        self.conversion_label = QLabel("(Conversions: 3 st)")
        self.conversion_label.setFont(QFont(FONT[0], 10))
        self.conversion_label.setStyleSheet(f"color: {COLOR2};")
        main_layout.addWidget(self.conversion_label, 1, 1)

        # Weight unit controls
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
        main_layout.addWidget(unit_group, 0, 0)
        self.lb_radio.toggled.connect(self.update_weight_buttons)
        self.kg_radio.toggled.connect(self.update_weight_buttons)
        self.st_radio.toggled.connect(self.update_weight_buttons)

        # Rounding controls
        rounding_group = QGroupBox("Rounding Options")
        rounding_layout = QVBoxLayout(rounding_group)
        self.rounding_checkbox = QCheckBox("Enable Rounding to 2.5")
        self.rounding_checkbox.stateChanged.connect(self.update_weight)
        rounding_layout.addWidget(self.rounding_checkbox)
        main_layout.addWidget(rounding_group, 0, 2)

        # Add/subtract buttons
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

        # Theme listbox with scrollbar, limited to 5 visible items
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
        base_path = os.path.dirname(__file__)
        theme_path = os.path.join(base_path, THEME_PATH)
        if os.path.exists(theme_path):
            themes = [folder for folder in os.listdir(theme_path) if os.path.isdir(os.path.join(theme_path, folder))]
        else:
            self.display_message(f"{THEME_PATH} folder not found.")
            themes = []
        self.lb_themes = [theme for theme in themes if theme.startswith("lb_")]
        self.kg_themes = [theme for theme in themes if theme.startswith("kg_")]
        self.other_themes = [theme for theme in themes if not (theme.startswith("lb_") or theme.startswith("kg_"))]
        self.all_themes = self.lb_themes + self.kg_themes + self.other_themes
        self.theme_listbox.clear()
        for theme in self.all_themes:
            self.theme_listbox.addItem(theme)

    def setup_user_pane(self):
        # Collapsible container
        self.user_pane_container = QWidget()
        self.user_pane_layout = QVBoxLayout(self.user_pane_container)
        # Remove fixed/minimum/maximum width to allow expansion
        # self.user_pane_container.setMaximumWidth(220)
        # self.user_pane_container.setMinimumWidth(120)
        self.user_pane_container.setStyleSheet(f"background-color: {COLOR1}; border-left: 2px solid {COLOR_BORDER};")
        self.user_pane_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Remove collapse/expand button
        # self.collapse_btn = QPushButton("⯈ Users")
        # self.collapse_btn.setCheckable(True)
        # self.collapse_btn.setChecked(True)
        # self.collapse_btn.clicked.connect(self.toggle_user_pane)
        # self.user_pane_layout.addWidget(self.collapse_btn)

        # Filter and sort controls
        filter_sort_layout = QHBoxLayout()
        self.user_filter_entry = QLineEdit()
        self.user_filter_entry.setPlaceholderText("Filter users...")
        self.user_filter_entry.textChanged.connect(self.filter_and_sort_users)
        filter_sort_layout.addWidget(self.user_filter_entry)

        # Add refresh, import, and export buttons
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

        # --- Add Import button ---
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
        # -------------------------

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
                    stop:0 #ffb74d, stop:1 {COLOR_WARNING});
                border: 2px solid #ffb74d;
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #f57c00, stop:1 #e65100);
            }}
        """)
        filter_sort_layout.addWidget(self.export_btn)

        # Update: Add new columns for lifts
        self.user_columns = [
            "First", "Last", "Age", "Weight_LB", "Weight_KG", "Sex",
            *LIFT_COLS,
            "Wilks"
        ]

        # Update sort combo to include new columns
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            "First", "Last", "Age", "Weight_LB", "Weight_KG", "Sex",
            *LIFT_COLS,
            "Wilks"
        ])
        self.sort_combo.currentIndexChanged.connect(self.filter_and_sort_users)
        filter_sort_layout.addWidget(self.sort_combo)
        self.user_pane_layout.addLayout(filter_sort_layout)

        # Add/Remove user buttons
        btns_layout = QHBoxLayout()
        self.add_user_btn = QPushButton("➕ Add User")
        self.add_user_btn.clicked.connect(self.open_add_user_dialog)
        self.add_user_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {COLOR_SUCCESS}, stop:1 #2e7d32);
                color: white;
                border: 2px solid #388e3c;
                border-radius: 12px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
                min-width: 90px;
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
        
        self.remove_user_btn = QPushButton("🗑️ Remove User")
        self.remove_user_btn.clicked.connect(self.remove_selected_user)  # Connect remove logic
        self.remove_user_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #ff7043, stop:1 #d84315);
                color: white;
                border: 2px solid #ff5722;
                border-radius: 12px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
                min-width: 110px;
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
        # --- Add Purge button (smaller, dark red border) ---
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
        # --- Remove Load button ---
        # self.load_btn = QPushButton("Load")
        # self.load_btn.setFixedWidth(60)
        # self.load_btn.setStyleSheet(
        #     "QPushButton {"
        #     "  border: 2px solid #228B22;"
        #     "  color: #228B22;"
        #     "  background-color: #eaffea;"
        #     "  border-radius: 6px;"
        #     "  font-weight: bold;"
        #     "  padding: 2px 6px;"
        #     "}"
        #     "QPushButton:hover {"
        #     "  background-color: #d0ffd0;"
        #     "  border: 2.5px solid #228B22;"
        #     "}"
        # )
        # self.load_btn.clicked.connect(self.load_users_from_csv_file)
        # btns_layout.addWidget(self.load_btn)
        # ---------------------------------------------------
        self.user_pane_layout.addLayout(btns_layout)

        # User table
        self.users = self.load_users_from_csv()
        self.filtered_sorted_users = self.users.copy()
        self.current_user_idx = 0

        self.user_table = QTableWidget()
        self.user_table.setColumnCount(len(self.user_columns))
        self.user_table.setHorizontalHeaderLabels(self.user_columns)
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.user_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.user_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        # Remove fixed maximum height and width so it expands with window
        # self.user_table.setMaximumHeight(160)
        # self.user_pane_container.setMaximumWidth(220)
        self.user_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.user_pane_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.user_table.verticalHeader().setVisible(False)
        self.user_table.setShowGrid(True)
        self.user_table.setStyleSheet(f"background-color: {COLOR1}; color: {COLOR2};")
        self.user_table.itemSelectionChanged.connect(self.on_user_table_selected)
        # --- Enable column resizing and moving ---
        self.user_table.horizontalHeader().setSectionsMovable(True)
        self.user_table.horizontalHeader().setSectionsClickable(True)
        self.user_table.horizontalHeader().setStretchLastSection(False)
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        # --- Connect double click to open edit dialog ---
        self.user_table.cellDoubleClicked.connect(self.open_edit_user_dialog)
        # -------------------------------------------------
        self.user_pane_layout.addWidget(self.user_table, stretch=1)  # Make table expand

        # User detail group
        self.user_detail_group = QGroupBox("Current User")
        self.user_detail_group.setStyleSheet("QGroupBox::title { font-weight: bold; }")
        self.user_detail_group.setMaximumWidth(400)
        self.user_detail_layout = QVBoxLayout(self.user_detail_group)
        self.user_name_label = QLabel()
        self.user_stats_label = QLabel()
        self.user_stats_label.setFont(QFont(FONT[0], 11))
        self.user_detail_layout.addWidget(self.user_name_label)
        self.user_detail_layout.addWidget(self.user_stats_label)

        # Add: Table for lifts
        self.lifts_table = QTableWidget(3, 3)
        self.lifts_table.setHorizontalHeaderLabels(["Squat", "Bench", "Deadlift"])
        self.lifts_table.setVerticalHeaderLabels(["1", "2", "3"])
        self.lifts_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.lifts_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.lifts_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.lifts_table.setFixedHeight(100)
        self.user_detail_layout.addWidget(self.lifts_table)

        self.user_pane_layout.addWidget(self.user_detail_group)

        # Next user preview (remove Age)
        self.next_user_group = QGroupBox("Up Next,")
        self.next_user_group.setStyleSheet("QGroupBox::title { font-weight: bold; }")
        self.next_user_group.setMaximumWidth(200)
        self.next_user_layout = QVBoxLayout(self.next_user_group)
        self.next_user_label = QLabel()
        self.next_user_layout.addWidget(self.next_user_label)
        self.user_pane_layout.addWidget(self.next_user_group)

        # Next button with arrow icon/character
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

        # --- Add a stretch to push everything above up, so the bar aligns with the prev/next buttons ---
        self.user_pane_layout.addStretch(1)

        # Initialize display
        self.populate_user_table()
        if self.filtered_sorted_users:
            self.user_table.selectRow(0)
            self.display_user(0)

    def prev_user(self):
        if not self.filtered_sorted_users:
            return
        prev_idx = (self.current_user_idx - 1) % len(self.filtered_sorted_users)
        self.display_user(prev_idx)

    def compute_wilks(self, sex: str, bodyweight_kg: str, total_kg: float) -> str:
        """Compute Wilks score for powerlifting."""
        return compute_wilks(sex, bodyweight_kg, total_kg)

    def update_all_wilks(self):
        for user in self.users:
            try:
                sex = user.get("Sex", "")
                bw = user.get("Weight_KG", "")
                squat = float(user.get("Squat3", 0) or 0)
                bench = float(user.get("Bench3", 0) or 0)
                deadlift = float(user.get("Deadlift3", 0) or 0)
                total = squat + bench + deadlift
                user["Wilks"] = self.compute_wilks(sex, bw, total)
            except Exception:
                user["Wilks"] = ""
        # Also update filtered_sorted_users
        for user in self.filtered_sorted_users:
            try:
                sex = user.get("Sex", "")
                bw = user.get("Weight_KG", "")
                squat = float(user.get("Squat3", 0) or 0)
                bench = float(user.get("Bench3", 0) or 0)
                deadlift = float(user.get("Deadlift3", 0) or 0)
                total = squat + bench + deadlift
                user["Wilks"] = self.compute_wilks(sex, bw, total)
            except Exception:
                user["Wilks"] = ""

    def populate_user_table(self):
        self.update_all_wilks()
        self.user_table.setRowCount(len(self.filtered_sorted_users))
        for row, user in enumerate(self.filtered_sorted_users):
            for col, key in enumerate(self.user_columns):
                self.user_table.setItem(row, col, QTableWidgetItem(user.get(key, "")))

    def filter_and_sort_users(self):
        filter_text = self.user_filter_entry.text().lower()
        sort_key = self.sort_combo.currentText()
        self.update_all_wilks()
        self.filtered_sorted_users = [
            user for user in self.users
            if any(filter_text in str(value).lower() for value in user.values())
        ]
        # Sort
        if sort_key in ["Age", "Weight_LB", "Weight_KG",
                        "Bench1", "Bench2", "Bench3",
                        "Squat1", "Squat2", "Squat3",
                        "Deadlift1", "Deadlift2", "Deadlift3", "Wilks"]:
            try:
                self.filtered_sorted_users.sort(key=lambda u: float(u.get(sort_key, 0) or 0))
            except Exception:
                self.filtered_sorted_users.sort(key=lambda u: u.get(sort_key, ""))
        else:
            self.filtered_sorted_users.sort(key=lambda u: u.get(sort_key, ""))
        self.populate_user_table()
        if self.filtered_sorted_users:
            self.user_table.selectRow(0)
            self.display_user(0)
        else:
            self.user_name_label.setText("No users")
            self.user_stats_label.setText("")
            self.next_user_label.setText("")
            # Clear lifts table
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
            # Clear lifts table
            for i in range(3):
                for j in range(3):
                    item = QTableWidgetItem("")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.lifts_table.setItem(i, j, item)
            return
        user = self.filtered_sorted_users[idx]
        # Use .get() for all fields to avoid KeyError
        first = user.get('First', '')
        last = user.get('Last', '')
        sex = user.get('Sex', '')
        weight_lb = user.get('Weight_LB', '')
        weight_kg = user.get('Weight_KG', '')
        self.user_name_label.setText(f"<b>{first} {last}</b> ({sex})")
        self.user_stats_label.setText(
            f"BodyWeight: {weight_lb} lbs / {weight_kg} kg"
        )
        # Fill lifts table
        for i, lift in enumerate(["Squat", "Bench", "Deadlift"]):
            for j in range(1, 4):
                key = f"{lift}{j}"
                value = user.get(key, "")
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.lifts_table.setItem(j-1, i, item)
        # Next user preview (remove Age)
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
        users = []
        base_path = resource_path("")
        data_dir = os.path.join(base_path, "data")
        csv_path = os.path.join(data_dir, "users.csv")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
        if not os.path.exists(csv_path):
            example_users = [
                {"First": "Alice", "Last": "Example1", "Age": "28", "Weight_LB": "135", "Weight_KG": "61.2", "Sex": "Female",
                 "Bench1": "80", "Bench2": "85", "Bench3": "90",
                 "Squat1": "120", "Squat2": "125", "Squat3": "130",
                 "Deadlift1": "150", "Deadlift2": "155", "Deadlift3": "160"},
                {"First": "Bob", "Last": "Example2", "Age": "34", "Weight_LB": "185", "Weight_KG": "83.9", "Sex": "Male",
                 "Bench1": "110", "Bench2": "115", "Bench3": "120",
                 "Squat1": "180", "Squat2": "185", "Squat3": "190",
                 "Deadlift1": "210", "Deadlift2": "215", "Deadlift3": "220"},
                {"First": "Carol", "Last": "Example3", "Age": "22", "Weight_LB": "120", "Weight_KG": "54.4", "Sex": "Female",
                 "Bench1": "60", "Bench2": "65", "Bench3": "70",
                 "Squat1": "100", "Squat2": "105", "Squat3": "110",
                 "Deadlift1": "130", "Deadlift2": "135", "Deadlift3": "140"},
                {"First": "David", "Last": "Example4", "Age": "40", "Weight_LB": "200", "Weight_KG": "90.7", "Sex": "Male",
                 "Bench1": "120", "Bench2": "125", "Bench3": "130",
                 "Squat1": "200", "Squat2": "205", "Squat3": "210",
                 "Deadlift1": "230", "Deadlift2": "235", "Deadlift3": "240"},
            ]
            for user in example_users:
                try:
                    sex = user.get("Sex", "")
                    bw = user.get("Weight_KG", "")
                    squat = float(user.get("Squat3", 0) or 0)
                    bench = float(user.get("Bench3", 0) or 0)
                    deadlift = float(user.get("Deadlift3", 0) or 0)
                    total = squat + bench + deadlift
                    user["Wilks"] = self.compute_wilks(sex, bw, total)
                except Exception:
                    user["Wilks"] = ""
            with open(csv_path, "w", newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=[
                    "First", "Last", "Age", "Weight_LB", "Weight_KG", "Sex",
                    *LIFT_COLS,
                    "Wilks"
                ])
                writer.writeheader()
                for user in example_users:
                    writer.writerow(user)
        if os.path.exists(csv_path):
            with open(csv_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    for col in [*LIFT_COLS, "Wilks"]:
                        if col not in row:
                            row[col] = ""
                    users.append(row)
        return users

    def load_judge_scores(self):
        base_path = resource_path("")
        judge_csv = os.path.join(base_path, "data", "judge_scores.csv")
        scores = []
        if os.path.exists(judge_csv):
            with open(judge_csv, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    scores.append(row)
        return scores

    def save_judge_scores(self):
        base_path = resource_path("")
        judge_csv = os.path.join(base_path, "data", "judge_scores.csv")
        os.makedirs(os.path.dirname(judge_csv), exist_ok=True)
        fieldnames = ["User", "Judge", "Score"]
        try:
            with open(judge_csv, "w", newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                # Write example scores for testing
                for user in self.filtered_sorted_users:
                    writer.writerow({"User": f"{user.get('First')} {user.get('Last')}", "Judge": "Judge1", "Score": "9"})
                    writer.writerow({"User": f"{user.get('First')} {user.get('Last')}", "Judge": "Judge2", "Score": "8"})
        except Exception as e:
            self.display_message(f"Error saving judge scores: {e}")

    def toggle_user_pane(self):
        if self.collapse_btn.isChecked():
            self.user_pane_container.setMaximumWidth(320)
            self.collapse_btn.setText("⯈ Users")
            for i in range(1, self.user_pane_layout.count()):
                item = self.user_pane_layout.itemAt(i)
                if item and item.widget():
                    item.widget().show()
        else:
            self.user_pane_container.setMaximumWidth(32)
            self.collapse_btn.setText("⯆")
            for i in range(1, self.user_pane_layout.count()):
                item = self.user_pane_layout.itemAt(i)
                if item and item.widget():
                    item.widget().hide()

    def open_image_in_window(self):
        if hasattr(self, "current_image_path") and self.current_image_path and os.path.exists(self.current_image_path):
            # If already open, just raise and update
            if self.enlarged_image_window and self.enlarged_image_window.isVisible():
                self.update_enlarged_image(self.current_image_path)
                self.enlarged_image_window.raise_()
                self.enlarged_image_window.activateWindow()
                return
            # Create a new window
            self.enlarged_image_window = QDialog(self)
            self.enlarged_image_window.setWindowTitle("Enlarged Image")
            self.enlarged_image_window.setMinimumSize(200, 200)
            self.enlarged_image_window.resize(600, 700)
            vbox = QVBoxLayout(self.enlarged_image_window)
            self.enlarged_image_label = QLabel()
            self.enlarged_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.enlarged_image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            vbox.addWidget(self.enlarged_image_label)
            self.update_enlarged_image(self.current_image_path)
            self.enlarged_image_window.setModal(False)
            # Add resize event to update image scaling
            self.enlarged_image_window.resizeEvent = self._enlarged_image_resize_event
            self.enlarged_image_window.show()
        else:
            self.display_message("No image available to enlarge.")

    def _enlarged_image_resize_event(self, event):
        # Called on enlarged image window resize
        if hasattr(self, "enlarged_image_label") and self.current_image_path:
            self.update_enlarged_image(self.current_image_path)
        event.accept()

    def update_enlarged_image(self, image_path):
        if hasattr(self, "enlarged_image_label") and self.enlarged_image_label:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                label_size = self.enlarged_image_label.size()
                self.enlarged_image_label.setPixmap(
                    pixmap.scaled(label_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                )

    def update_example_image(self, image_name: str) -> None:
        """Update the example image with optimization for performance."""
        if not Image:
            self.display_message("PIL/Pillow not available for image processing")
            return
            
        selected_theme = getattr(self, "theme_var", "")
        base_path = os.path.dirname(__file__)
        
        if os.path.exists(image_name):
            image_path = image_name
        else:
            image_path = get_image_path(selected_theme, image_name)
        
        if os.path.exists(image_path):
            try:
                # Optimize image loading with proper resource management
                with Image.open(image_path) as image:
                    image = image.resize((180, 180), Image.Resampling.LANCZOS)
                    inverted_image = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                    
                    static_image_path = get_image_path(selected_theme, "bar.png")
                    if os.path.exists(static_image_path):
                        with Image.open(static_image_path) as static_img:
                            static_image = static_img.resize((250, 180), Image.Resampling.LANCZOS)
                    else:
                        static_image = Image.new("RGBA", (250, 180), (255, 255, 255, 0))
                    
                    combined_width = image.width * 2 + static_image.width
                    combined_image = Image.new("RGBA", (combined_width, image.height))
                    combined_image.paste(image, (0, 0))
                    combined_image.paste(static_image, (image.width, 0))
                    combined_image.paste(inverted_image, (image.width + static_image.width, 0))
                    
                    # Use a more unique temp filename to avoid conflicts
                    temp_path = os.path.join(base_path, "resources", f"temp_combined_{id(self)}.png")
                    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
                    combined_image.save(temp_path)
                    
                    pixmap = QPixmap(temp_path)
                    if not pixmap.isNull():
                        self.example_image_label.setPixmap(
                            pixmap.scaled(self.example_image_label.size(), 
                                        Qt.AspectRatioMode.KeepAspectRatio,
                                        Qt.TransformationMode.SmoothTransformation)
                        )
                        self.current_image_path = temp_path
                        
                        # Update enlarged window if visible
                        if hasattr(self, 'enlarged_image_window') and self.enlarged_image_window and self.enlarged_image_window.isVisible():
                            self.update_enlarged_image(self.current_image_path)
                    
            except Exception as e:
                self.display_message(f"Image error: {e}")
                self._show_fallback_image(selected_theme)
        else:
            self._show_fallback_image(selected_theme)
    
    def _show_fallback_image(self, selected_theme: str) -> None:
        """Show fallback image when main image is not available."""
        fallback_image_path = get_image_path(selected_theme, "none.png")
        if os.path.exists(fallback_image_path):
            pixmap = QPixmap(fallback_image_path)
            if not pixmap.isNull():
                self.example_image_label.setPixmap(
                    pixmap.scaled(self.example_image_label.size(), 
                                Qt.AspectRatioMode.KeepAspectRatio,
                                Qt.TransformationMode.SmoothTransformation)
                )
                self.current_image_path = fallback_image_path
                
                if hasattr(self, 'enlarged_image_window') and self.enlarged_image_window and self.enlarged_image_window.isVisible():
                    self.update_enlarged_image(self.current_image_path)
        else:
            self.example_image_label.clear()
            self.current_image_path = None
            if hasattr(self, 'enlarged_image_window') and self.enlarged_image_window and self.enlarged_image_window.isVisible():
                self.enlarged_image_window.close()

    def open_github(self) -> None:
        """Open GitHub repository in browser."""
        QDesktopServices.openUrl(QUrl(APP_GITHUB_REPO))

    def display_message(self, message: str) -> None:
        """Display message to user."""
        self.message_label.setText(message)
        # Auto-clear message after 5 seconds
        if hasattr(self, '_message_timer'):
            self._message_timer.stop()
        self._message_timer = QTimer()
        self._message_timer.setSingleShot(True)
        self._message_timer.timeout.connect(lambda: self.message_label.setText(""))
        self._message_timer.start(5000)

    def update_weight_buttons(self) -> None:
        """Update weight increment/decrement buttons based on selected unit."""
        # Clear existing buttons efficiently
        self._clear_layout(self.add_buttons_layout)
        self._clear_layout(self.subtract_buttons_layout)

        if self.lb_radio.isChecked():
            increments = [1.75, 2.5, 5, 10, 25, 35, 45, 55]
        elif self.kg_radio.isChecked():
            increments = [1, 2.5, 5, 10, 15, 20, 25]
        else:
            increments = []

        # Create buttons with proper slot connections
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
            
            # Apply weight limits in pounds and convert back
            if self.current_weight_lb < min_weight:
                self.current_weight_lb = min_weight
                self.current_weight_kg = self.current_weight_lb / CONVERSION_FACTOR_LB_TO_KG
            elif self.current_weight_lb > max_weight:
                self.current_weight_lb = max_weight
                self.current_weight_kg = self.current_weight_lb / CONVERSION_FACTOR_LB_TO_KG
        
        self.update_weight()
        self.update_theme_photo(self.current_weight_lb)

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
        filter_text = self.theme_filter_entry.text().lower()
        if self.theme_filter_var == "All":
            filtered = self.all_themes
        elif self.theme_filter_var == "Other":
            filtered = self.other_themes
        else:
            filtered = [theme for theme in self.all_themes if theme.startswith(self.theme_filter_var)]
        self.theme_listbox.clear()
        for theme in filtered:
            if filter_text in theme.lower():
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
        base_path = os.path.dirname(__file__)
        theme_folder = os.path.join(base_path, THEME_PATH, selected_theme)
        # Use the current rounded weight for the preview image
        rounding = 2.5 if self.rounding_checkbox.isChecked() else IMAGE_ROUNDING
        rounded_weight_lb = round_weight(self.current_weight_lb, rounding)
        rounded_weight_str = f"{int(rounded_weight_lb)}" if rounded_weight_lb.is_integer() else f"{rounded_weight_lb:.1f}"
        image_path = os.path.join(theme_folder, f"{rounded_weight_str}.png")
        if not os.path.exists(image_path):
            # Try fallback to none.png
            fallback_image_path = os.path.join(theme_folder, "none.png")
            if os.path.exists(fallback_image_path):
                self.update_example_image(fallback_image_path)
            else:
                self.display_message(f"Theme image not found for {selected_theme}.")
        else:
            self.update_example_image(image_path)

    def set_default_theme(self):
        if self.theme_listbox.count() > 0:
            self.theme_listbox.setCurrentRow(0)
            self.on_theme_change_from_listbox()

    def showEvent(self, event):
        super().showEvent(event)
        # Position the toggle button container at the right edge, vertically centered
        self.position_toggle_right_pane_btn()

    def resizeEvent(self, event):
        """Handle window resize events."""
        super().resizeEvent(event)
        self.position_toggle_right_pane_btn()
        # Keep user pane attached if visible
        if hasattr(self, 'user_pane_window') and self.user_pane_window.isVisible():
            self.attach_user_pane_window()

    def position_toggle_right_pane_btn(self) -> None:
        """Position the toggle button at the right edge of the window."""
        if hasattr(self, "toggle_right_pane_btn_container"):
            w = self.width()
            h = self.height()
            btn_w = self.toggle_right_pane_btn_container.width()
            y = (h - 60) // 2
            self.toggle_right_pane_btn_container.setGeometry(w - btn_w, y, btn_w, 60)
            self.toggle_right_pane_btn_container.show()

    def toggle_right_pane_visibility(self) -> None:
        """Toggle visibility of the user pane window."""
        if self.user_pane_window.isVisible():
            self.user_pane_window.hide()
            self.toggle_right_pane_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirHomeIcon))
            self.toggle_right_pane_btn.setChecked(False)
        else:
            self.attach_user_pane_window()
            self.user_pane_window.show()
            self.toggle_right_pane_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirHomeIcon))
            self.toggle_right_pane_btn.setChecked(True)

    def attach_user_pane_window(self) -> None:
        """Attach the user pane window to the right of the main window."""
        geo = self.geometry()
        self.user_pane_window.move(geo.x() + geo.width() - 2, geo.y())

    def moveEvent(self, event):
        super().moveEvent(event)
        # Keep user pane attached if visible
        if self.user_pane_window.isVisible():
            self.attach_user_pane_window()

    def closeEvent(self, event):
        # Clean up temporary files before closing
        self.cleanup_temp_files()
        
        if hasattr(self, "user_pane_window") and self.user_pane_window is not None:
            try:
                self.user_pane_window.close()
            except Exception:
                pass
        super().closeEvent(event)

    def exit_all(self):
        # Clean up temporary files before exiting
        self.cleanup_temp_files()
        
        if hasattr(self, "user_pane_window") and self.user_pane_window is not None:
            try:
                self.user_pane_window.close()
            except Exception:
                pass
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
            # Basic validation: require First and Last name
            if not user_data["First"] or not user_data["Last"]:
                self.display_message("First and Last name are required.")
                return
            self.users.append(user_data)
            self.save_users_to_csv()  # Save after adding
            self.filter_and_sort_users()
            # Select the newly added user
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
        # Remove from self.users
        try:
            self.users.remove(user_to_remove)
        except ValueError:
            pass  # Already removed
        # Save to removed.csv
        base_path = resource_path("")
        removed_csv_path = os.path.join(base_path, "data", "removed.csv")
        os.makedirs(os.path.dirname(removed_csv_path), exist_ok=True)
        fieldnames = self.user_columns
        file_exists = os.path.exists(removed_csv_path)
        try:
            with open(removed_csv_path, "a", newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                if not file_exists:
                    writer.writeheader()
                writer.writerow({k: user_to_remove.get(k, "") for k in fieldnames})
        except Exception as e:
            self.display_message(f"Error saving to removed.csv: {e}")
        # Save updated users to users.csv and refresh UI
        self.save_users_to_csv()
        self.filter_and_sort_users()
        # Select next available user if any
        if self.filtered_sorted_users:
            idx = min(row, len(self.filtered_sorted_users) - 1)
            self.user_table.selectRow(idx)
            self.display_user(idx)
        else:
            self.user_name_label.setText("No users")
            self.user_stats_label.setText("")
            self.next_user_label.setText("")

    def purge_users(self):
        # Show warning dialog
        reply = QMessageBox.warning(
            self,
            "Confirm Purge",
            "This will move all user data to a dated backup and clear the user list. This cannot be undone.\n\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        import datetime
        base_path = resource_path("")
        csv_path = os.path.join(base_path, "data", "users.csv")
        today = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        purged_csv_path = os.path.join(base_path, "data", f"users_purged_{today}.csv")
        try:
            # Copy current users.csv to users_purged_<YYYY-MM-DD>.csv
            if os.path.exists(csv_path):
                with open(csv_path, "r", encoding="utf-8") as src, open(purged_csv_path, "w", encoding="utf-8") as dst:
                    dst.write(src.read())
            # Overwrite users.csv with only header
            with open(csv_path, "w", newline='', encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.user_columns)
                writer.writeheader()
            self.users = []
            self.filtered_sorted_users = []
            self.populate_user_table()
            self.user_name_label.setText("No users")
            self.user_stats_label.setText("")
            self.next_user_label.setText("")
            for i in range(3):
                for j in range(3):
                    self.lifts_table.setItem(i, j, QTableWidgetItem(""))
            self.display_message(f"All users purged to {os.path.basename(purged_csv_path)}.")
        except Exception as e:
            self.display_message(f"Purge failed: {e}")

    def save_users_to_csv(self):
        base_path = resource_path("")
        csv_path = os.path.join(base_path, "data", "users.csv")
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        fieldnames = self.user_columns
        self.update_all_wilks()
        try:
            with open(csv_path, "w", newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for user in self.users:
                    writer.writerow({k: user.get(k, "") for k in fieldnames})
        except Exception as e:
            self.display_message(f"Error saving users: {e}")

    def refresh_users(self):
        self.users = self.load_users_from_csv()
        self.filter_and_sort_users()
        self.display_message("User data reloaded.")

    def export_users(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Export Users", "users_export.csv", "CSV Files (*.csv)")
        if not filename:
            return
        self.update_all_wilks()
        try:
            with open(filename, "w", newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.user_columns)
                writer.writeheader()
                for user in self.filtered_sorted_users:
                    writer.writerow({k: user.get(k, "") for k in self.user_columns})
            self.display_message(f"Exported {len(self.filtered_sorted_users)} users to {filename}")
        except Exception as e:
            self.display_message(f"Export failed: {e}")

    def import_users_from_csv(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Import Users from CSV", "", "CSV Files (*.csv)")
        if not filename:
            return
        users = []
        try:
            with open(filename, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Ensure all columns exist
                    for col in [
                        "First", "Last", "Age", "Weight_LB", "Weight_KG", "Sex",
                        *LIFT_COLS,
                        "Wilks"
                    ]:
                        if col not in row:
                            row[col] = ""
                    users.append(row)
        except Exception as e:
            self.display_message(f"Failed to import users: {e}")
            return
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
            # Find the user in self.users and update
            for idx, u in enumerate(self.users):
                if all(u.get(k, "") == user.get(k, "") for k in ["First", "Last", "Age", "Sex"]):
                    self.users[idx] = updated_user
                    break
            # Also update in filtered_sorted_users
            self.filtered_sorted_users[row] = updated_user
            self.save_users_to_csv()
            self.filter_and_sort_users()
            self.display_user(row)

    def update_theme_photo(self, weight_number: float) -> None:
        """Update theme photo based on weight with optimized error handling."""
        self.display_message("")
        rounding = 2.5 if self.rounding_checkbox.isChecked() else IMAGE_ROUNDING
        rounded_weight = round_weight(weight_number, rounding)
        rounded_weight_str = f"{int(rounded_weight)}" if rounded_weight.is_integer() else f"{rounded_weight:.1f}"
        
        selected_theme = getattr(self, "theme_var", "")
        if not selected_theme:
            return
            
        theme_folder = get_theme_folder(selected_theme)
        if os.path.exists(theme_folder):
            image_path = os.path.join(theme_folder, f"{rounded_weight_str}.png")
            if os.path.exists(image_path):
                self.update_example_image(image_path)
            else:
                self._show_fallback_image(selected_theme)
        else:
            self.display_message(f"Selected theme folder does not exist: {theme_folder}")

    def cleanup_temp_files(self):
        """Clean up temporary combined image files created by the application."""
        try:
            base_path = resource_path("")
            resources_dir = os.path.join(base_path, "resources")
            
            if os.path.exists(resources_dir):
                # Find all temp_combined files in the resources directory
                for filename in os.listdir(resources_dir):
                    if filename.startswith("temp_combined_") and filename.endswith(".png"):
                        temp_file_path = os.path.join(resources_dir, filename)
                        try:
                            os.remove(temp_file_path)
                            print(f"Deleted temporary file: {filename}")
                        except Exception as e:
                            print(f"Failed to delete {filename}: {e}")
        except Exception as e:
            print(f"Error during temp file cleanup: {e}")

    def closeEvent(self, event):
        self.cleanup_temp_files()  # Clean up temp files on exit
        if hasattr(self, "user_pane_window") and self.user_pane_window is not None:
            try:
                self.user_pane_window.close()
            except Exception:
                pass
        super().closeEvent(event)

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
            window.cleanup_temp_files()
