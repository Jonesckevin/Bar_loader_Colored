import sys
import os
import yaml
import csv
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QRadioButton, QButtonGroup, QCheckBox, QLineEdit, QListWidget, QGroupBox, QScrollArea,
    QGridLayout, QDialog, QFrame, QSizePolicy, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QDialogButtonBox, QStyle, QFileDialog, QMessageBox
)
from PyQt6.QtGui import QPixmap, QFont, QCursor, QIcon
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PIL import Image

# Load configuration from YAML file
with open("resources/config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)

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
BARBELL_TYPES = config["barbell_types"]
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

def round_weight(weight, rounding):
    return round(weight / rounding) * rounding

def get_theme_folder(selected_theme):
    base_path = os.path.dirname(__file__)
    return os.path.join(base_path, THEME_PATH, selected_theme)

def get_image_path(theme, image_name):
    folder = get_theme_folder(theme)
    return os.path.join(folder, image_name)

LIFT_COLS = [
    "Bench1", "Bench2", "Bench3",
    "Squat1", "Squat2", "Squat3",
    "Deadlift1", "Deadlift2", "Deadlift3"
]

class UserPaneWindow(QMainWindow):
    def __init__(self, user_pane_widget, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Users")
        # Set a larger default size for the user pane
        self.setMinimumSize(600, 700)  # Increased width and height
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
        self.exit_button = QPushButton("Exit")
        self.exit_button.clicked.connect(self.exit_all)
        self.exit_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.exit_button.setStyleSheet("margin: 0 16px;")

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

        self.enlarge_button = QPushButton("Enlarge Image")
        self.enlarge_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
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
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_users)
        filter_sort_layout.addWidget(self.refresh_btn)

        # --- Add Import button ---
        self.import_btn = QPushButton("Import")
        self.import_btn.setToolTip("Import users from a CSV file (replaces current users)")
        self.import_btn.clicked.connect(self.import_users_from_csv)
        filter_sort_layout.addWidget(self.import_btn)
        # -------------------------

        self.export_btn = QPushButton("Export")
        self.export_btn.clicked.connect(self.export_users)
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
        self.add_user_btn = QPushButton("Add User")
        self.add_user_btn.clicked.connect(self.open_add_user_dialog)
        btns_layout.addWidget(self.add_user_btn)
        self.remove_user_btn = QPushButton("Remove User")
        self.remove_user_btn.clicked.connect(self.remove_selected_user)  # Connect remove logic
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
        self.user_detail_group.setMaximumWidth(500)
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
        self.prev_btn = QPushButton("◀ Prev")
        self.prev_btn.clicked.connect(self.prev_user)
        btn_layout.addWidget(self.prev_btn)
        self.next_btn = QPushButton("Next ▶")
        self.next_btn.clicked.connect(self.next_user)
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

    def compute_wilks(self, sex, bodyweight_kg, total_kg):
        # Wilks coefficients (2017, IPF)
        if sex.lower() == "male":
            a, b, c, d, e, f = -216.0475144, 16.2606339, -0.002388645, -0.00113732, 7.01863e-06, -1.291e-08
        else:
            a, b, c, d, e, f = 594.31747775582, -27.23842536447, 0.82112226871, -0.00930733913, 4.731582e-05, -9.054e-08
        bw = float(bodyweight_kg) if bodyweight_kg else 0
        if bw <= 0 or total_kg <= 0:
            return ""
        coeff = a + b*bw + c*bw**2 + d*bw**3 + e*bw**4 + f*bw**5
        if coeff == 0:
            return ""
        wilks = 500 * float(total_kg) / coeff
        return f"{wilks:.1f}"

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
                    self.lifts_table.setItem(i, j, QTableWidgetItem(""))

    def display_user(self, idx):
        if not self.filtered_sorted_users:
            self.user_name_label.setText("No users")
            self.user_stats_label.setText("")
            self.next_user_label.setText("")
            # Clear lifts table
            for i in range(3):
                for j in range(3):
                    self.lifts_table.setItem(i, j, QTableWidgetItem(""))
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
                self.lifts_table.setItem(j-1, i, QTableWidgetItem(value))
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
        base_path = os.path.dirname(__file__)
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

    def update_example_image(self, image_name):
        selected_theme = getattr(self, "theme_var", "")
        base_path = os.path.dirname(__file__)
        if os.path.exists(image_name):
            image_path = image_name
        else:
            image_path = get_image_path(selected_theme, image_name)
        if os.path.exists(image_path):
            try:
                image = Image.open(image_path).resize((180, 180))
                inverted_image = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                static_image_path = get_image_path(selected_theme, "bar.png")
                static_image = Image.open(static_image_path).resize((250, 180)) if os.path.exists(static_image_path) else Image.new("RGBA", (0, 0), (255, 255, 255, 0))
                combined_width = image.width * 2 + static_image.width
                combined_image = Image.new("RGBA", (combined_width, image.height))
                combined_image.paste(image, (0, 0))
                combined_image.paste(static_image, (image.width, 0))
                combined_image.paste(inverted_image, (image.width + static_image.width, 0))
                temp_path = os.path.join(base_path, "resources", "temp_combined.png")
                combined_image.save(temp_path)
                pixmap = QPixmap(temp_path)
                self.example_image_label.setPixmap(pixmap.scaled(self.example_image_label.size(), Qt.AspectRatioMode.KeepAspectRatio))
                self.current_image_path = temp_path
                if self.enlarged_image_window and self.enlarged_image_window.isVisible():
                    self.update_enlarged_image(self.current_image_path)
            except Exception as e:
                self.display_message(f"Image error: {e}")
        else:
            fallback_image_path = get_image_path(selected_theme, "none.png")
            if os.path.exists(fallback_image_path):
                pixmap = QPixmap(fallback_image_path)
                self.example_image_label.setPixmap(pixmap.scaled(self.example_image_label.size(), Qt.AspectRatioMode.KeepAspectRatio))
                self.current_image_path = fallback_image_path
                if self.enlarged_image_window and self.enlarged_image_window.isVisible():
                    self.update_enlarged_image(self.current_image_path)
            else:
                self.example_image_label.clear()
                self.current_image_path = None
                if self.enlarged_image_window and self.enlarged_image_window.isVisible():
                    self.enlarged_image_window.close()

    def open_github(self):
        QDesktopServices.openUrl(QUrl(APP_GITHUB_REPO))

    def display_message(self, message):
        self.message_label.setText(message)

    def update_weight_buttons(self):
        # Remove old buttons
        for i in reversed(range(self.add_buttons_layout.count())):
            widget = self.add_buttons_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        for i in reversed(range(self.subtract_buttons_layout.count())):
            widget = self.subtract_buttons_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        if self.lb_radio.isChecked():
            increments = [1.75, 2.5, 5, 10, 25, 35, 45, 55]
        elif self.kg_radio.isChecked():
            increments = [1, 2.5, 5, 10, 15, 20, 25]
        else:
            increments = []

        # Use direct slot connection for better performance
        for inc in increments:
            btn = QPushButton(f"+{inc}")
            btn.clicked.connect(self._make_adjust_weight_slot(inc))
            self.add_buttons_layout.addWidget(btn)
        for inc in increments:
            btn = QPushButton(f"-{inc}")
            btn.clicked.connect(self._make_adjust_weight_slot(-inc))
            self.subtract_buttons_layout.addWidget(btn)

    def _make_adjust_weight_slot(self, amount):
        # Avoid lambda capture issues and improve slot call speed
        def slot():
            self.adjust_weight(amount)
        return slot

    def adjust_weight(self, amount):
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
            self.current_weight_lb = round(self.current_weight_lb + effective_amount)
            if self.current_weight_lb < min_weight:
                self.current_weight_lb = min_weight
            elif self.current_weight_lb > max_weight:
                self.current_weight_lb = max_weight
            self.current_weight_kg = self.current_weight_lb / 2.20462
        elif unit == "Kilograms":
            self.current_weight_kg = round(self.current_weight_kg + effective_amount)
            self.current_weight_lb = self.current_weight_kg * 2.20462
            if self.current_weight_lb < min_weight:
                self.current_weight_lb = min_weight
                self.current_weight_kg = self.current_weight_lb / 2.20462
            elif self.current_weight_lb > max_weight:
                self.current_weight_lb = max_weight
                self.current_weight_kg = self.current_weight_lb / 2.20462
        self.update_weight()
        self.update_theme_photo(self.current_weight_lb)

    def update_theme_photo(self, weight_number):
        self.display_message("")
        rounding = 2.5 if self.rounding_checkbox.isChecked() else IMAGE_ROUNDING
        rounded_weight = round_weight(weight_number, rounding)
        rounded_weight_str = f"{int(rounded_weight)}" if rounded_weight.is_integer() else f"{rounded_weight:.1f}"
        selected_theme = getattr(self, "theme_var", "")
        base_path = os.path.dirname(__file__)
        theme_folder = os.path.join(base_path, THEME_PATH, selected_theme)
        if os.path.exists(theme_folder):
            image_path = os.path.join(theme_folder, f"{rounded_weight_str}.png")
            if os.path.exists(image_path):
                self.update_example_image(image_path)
            else:
                fallback_image_path = os.path.join(theme_folder, "none.png")
                if os.path.exists(fallback_image_path):
                    self.update_example_image(fallback_image_path)
                else:
                    self.display_message(f"Image {rounded_weight_str}.png and fallback none.png not found in the selected theme folder.")
        else:
            self.display_message(f"Selected theme folder does not exist: {theme_folder}")

    def update_weight(self):
        self.display_message("")
        rounding = 2.5 if self.rounding_checkbox.isChecked() else IMAGE_ROUNDING
        rounded_weight_lb = round_weight(self.current_weight_lb, rounding)
        rounded_weight_kg = round_weight(self.current_weight_kg, rounding)
        self.current_weight_label.setText(f"{rounded_weight_lb:.1f} lbs / {rounded_weight_kg:.1f} kg")
        self.calculate_weight()
        rounded_weight_str = f"{int(rounded_weight_lb)}" if rounded_weight_lb.is_integer() else f"{rounded_weight_lb:.1f}"
        self.update_example_image(f"{rounded_weight_str}.png")

    def calculate_weight(self):
        try:
            self.update_conversions(self.current_weight_kg)
        except Exception as e:
            self.display_message(f"An error occurred: {str(e)}")

    def update_conversions(self, weight_in_kg):
        stone = round(weight_in_kg / 6.35029)
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
        super().resizeEvent(event)
        self.position_toggle_right_pane_btn()

    def position_toggle_right_pane_btn(self):
        # Place the button at the right edge, vertically centered
        if hasattr(self, "toggle_right_pane_btn_container"):
            w = self.width()
            h = self.height()
            btn_w = self.toggle_right_pane_btn_container.width()
            btn_h = self.toggle_right_pane_btn_container.height()
            y = (h - 60) // 2
            self.toggle_right_pane_btn_container.setGeometry(w - btn_w, y, btn_w, 60)
            self.toggle_right_pane_btn_container.show()

    def toggle_right_pane_visibility(self):
        # Show/hide the user pane window as a thin attached window
        if self.user_pane_window.isVisible():
            self.user_pane_window.hide()
            # Keep user icon when hidden
            self.toggle_right_pane_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirHomeIcon))
            self.toggle_right_pane_btn.setChecked(False)
        else:
            self.attach_user_pane_window()
            self.user_pane_window.show()
            # Keep user icon when shown
            self.toggle_right_pane_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirHomeIcon))
            self.toggle_right_pane_btn.setChecked(True)

    def attach_user_pane_window(self):
        # Attach the user pane window to the right of the main window
        geo = self.geometry()
        # Remove setFixedHeight to allow resizing
        # self.user_pane_window.setFixedHeight(geo.height())
        self.user_pane_window.move(geo.x() + geo.width() - 2, geo.y())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.position_toggle_right_pane_btn()
        # Keep user pane attached if visible
        if self.user_pane_window.isVisible():
            self.attach_user_pane_window()

    def moveEvent(self, event):
        super().moveEvent(event)
        # Keep user pane attached if visible
        if self.user_pane_window.isVisible():
            self.attach_user_pane_window()

    def closeEvent(self, event):
        if hasattr(self, "user_pane_window") and self.user_pane_window is not None:
            try:
                self.user_pane_window.close()
            except Exception:
                pass
        super().closeEvent(event)

    def exit_all(self):
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
        base_path = os.path.dirname(__file__)
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
        base_path = os.path.dirname(__file__)
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
        base_path = os.path.dirname(__file__)
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

class AddUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add User")
        self.setMinimumWidth(300)
        layout = QVBoxLayout(self)

        self.fields = {}
        for label in ["First", "Last", "Age", "Weight_LB", "Weight_KG"]:
            row = QHBoxLayout()
            lbl = QLabel(label + ":")
            edit = QLineEdit()
            row.addWidget(lbl)
            row.addWidget(edit)
            layout.addLayout(row)
            self.fields[label] = edit

        # --- Auto-completion for Weight_LB and Weight_KG ---
        self._weight_autofill_block = False
        self.fields["Weight_LB"].textChanged.connect(self._on_weight_lb_changed)
        self.fields["Weight_KG"].textChanged.connect(self._on_weight_kg_changed)

        # Add: Inputs for Bench, Squat, Deadlift (1/2/3)
        for lift in ["Bench", "Squat", "Deadlift"]:
            group = QGroupBox(lift)
            group_layout = QHBoxLayout(group)
            for i in range(1, 4):
                lbl = QLabel(f"{i}:")
                edit = QLineEdit()
                group_layout.addWidget(lbl)
                group_layout.addWidget(edit)
                self.fields[f"{lift}{i}"] = edit
            layout.addWidget(group)

        # Sex radio buttons
        sex_row = QHBoxLayout()
        sex_lbl = QLabel("Sex:")
        sex_row.addWidget(sex_lbl)
        self.sex_group = QButtonGroup(self)
        self.sex_male = QRadioButton("Male")
        self.sex_female = QRadioButton("Female")
        self.sex_other = QRadioButton("Other")
        self.sex_group.addButton(self.sex_male)
        self.sex_group.addButton(self.sex_female)
        self.sex_group.addButton(self.sex_other)
        sex_row.addWidget(self.sex_male)
        sex_row.addWidget(self.sex_female)
        sex_row.addWidget(self.sex_other)
        layout.addLayout(sex_row)
        self.sex_male.setChecked(True)  # Default selection

        btns = QDialogButtonBox()
        self.add_btn = btns.addButton("Add User", QDialogButtonBox.ButtonRole.AcceptRole)
        self.cancel_btn = btns.addButton("Cancel", QDialogButtonBox.ButtonRole.RejectRole)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _on_weight_lb_changed(self, text):
        if self._weight_autofill_block:
            return
        try:
            lb = float(text)
            kg = lb / 2.20462
            self._weight_autofill_block = True
            self.fields["Weight_KG"].setText(f"{kg:.1f}")
            self._weight_autofill_block = False
        except Exception:
            if text.strip() == "":
                self._weight_autofill_block = True
                self.fields["Weight_KG"].setText("")
                self._weight_autofill_block = False

    def _on_weight_kg_changed(self, text):
        if self._weight_autofill_block:
            return
        try:
            kg = float(text)
            lb = kg * 2.20462
            self._weight_autofill_block = True
            self.fields["Weight_LB"].setText(f"{lb:.1f}")
            self._weight_autofill_block = False
        except Exception:
            if text.strip() == "":
                self._weight_autofill_block = True
                self.fields["Weight_LB"].setText("")
                self._weight_autofill_block = False

    def get_user_data(self):
        data = {k: v.text().strip() for k, v in self.fields.items()}
        if self.sex_male.isChecked():
            data["Sex"] = "Male"
        elif self.sex_female.isChecked():
            data["Sex"] = "Female"
        elif self.sex_other.isChecked():
            data["Sex"] = "Other"
        else:
            data["Sex"] = ""
        # Ensure all lift fields exist
        for col in LIFT_COLS:
            if col not in data:
                data[col] = ""
        return data

class EditUserDialog(QDialog):
    def __init__(self, user_data, user_columns, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit User")
        self.setMinimumWidth(350)
        layout = QVBoxLayout(self)
        self.fields = {}
        # Editable fields
        for label in ["First", "Last", "Age", "Weight_LB", "Weight_KG"]:
            row = QHBoxLayout()
            lbl = QLabel(label + ":")
            edit = QLineEdit()
            edit.setText(user_data.get(label, ""))
            row.addWidget(lbl)
            row.addWidget(edit)
            layout.addLayout(row)
            self.fields[label] = edit

        # --- Auto-completion for Weight_LB and Weight_KG ---
        self._weight_autofill_block = False
        self.fields["Weight_LB"].textChanged.connect(self._on_weight_lb_changed)
        self.fields["Weight_KG"].textChanged.connect(self._on_weight_kg_changed)

        # Lifts
        for lift in ["Bench", "Squat", "Deadlift"]:
            group = QGroupBox(lift)
            group_layout = QHBoxLayout(group)
            for i in range(1, 4):
                lbl = QLabel(f"{i}:")
                edit = QLineEdit()
                edit.setText(user_data.get(f"{lift}{i}", ""))
                group_layout.addWidget(lbl)
                group_layout.addWidget(edit)
                self.fields[f"{lift}{i}"] = edit
            layout.addWidget(group)

        # Sex radio buttons
        sex_row = QHBoxLayout()
        sex_lbl = QLabel("Sex:")
        sex_row.addWidget(sex_lbl)
        self.sex_group = QButtonGroup(self)
        self.sex_male = QRadioButton("Male")
        self.sex_female = QRadioButton("Female")
        self.sex_other = QRadioButton("Other")
        self.sex_group.addButton(self.sex_male)
        self.sex_group.addButton(self.sex_female)
        self.sex_group.addButton(self.sex_other)
        sex_row.addWidget(self.sex_male)
        sex_row.addWidget(self.sex_female)
        sex_row.addWidget(self.sex_other)
        sex_val = user_data.get("Sex", "")
        if sex_val == "Male":
            self.sex_male.setChecked(True)
        elif sex_val == "Female":
            self.sex_female.setChecked(True)
        elif sex_val == "Other":
            self.sex_other.setChecked(True)
        else:
            self.sex_male.setChecked(True)
        layout.addLayout(sex_row)

        btns = QDialogButtonBox()
        self.save_btn = btns.addButton("Save User", QDialogButtonBox.ButtonRole.AcceptRole)
        self.cancel_btn = btns.addButton("Cancel", QDialogButtonBox.ButtonRole.RejectRole)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _on_weight_lb_changed(self, text):
        if self._weight_autofill_block:
            return
        try:
            lb = float(text)
            kg = lb / 2.20462
            self._weight_autofill_block = True
            self.fields["Weight_KG"].setText(f"{kg:.1f}")
            self._weight_autofill_block = False
        except Exception:
            if text.strip() == "":
                self._weight_autofill_block = True
                self.fields["Weight_KG"].setText("")
                self._weight_autofill_block = False

    def _on_weight_kg_changed(self, text):
        if self._weight_autofill_block:
            return
        try:
            kg = float(text)
            lb = kg * 2.20462
            self._weight_autofill_block = True
            self.fields["Weight_LB"].setText(f"{lb:.1f}")
            self._weight_autofill_block = False
        except Exception:
            if text.strip() == "":
                self._weight_autofill_block = True
                self.fields["Weight_LB"].setText("")
                self._weight_autofill_block = False

    def get_user_data(self):
        data = {k: v.text().strip() for k, v in self.fields.items()}
        if self.sex_male.isChecked():
            data["Sex"] = "Male"
        elif self.sex_female.isChecked():
            data["Sex"] = "Female"
        elif self.sex_other.isChecked():
            data["Sex"] = "Other"
        else:
            data["Sex"] = ""
        # Ensure all lift fields exist
        for col in LIFT_COLS:
            if col not in data:
                data[col] = ""
        return data

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BarbellCalculator()
    window.show()
    sys.exit(app.exec())