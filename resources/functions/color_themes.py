"""
Color theme management for the Barbell Calculator application.
Provides different color schemes and theme cycling functionality.
"""

from typing import Dict, Any


# Define the color themes
THEMES = {
    "Retro": {
        "background": "#22211f09",
        "text": "#ffe066",
        "highlight": "#ff8800",
        "accent": "#ff5e13",
        "success": "#aaff00",
        "warning": "#ffcc00",
        "error": "#ff003c",
        "info": "#00bfff",
        "border": "#ffe066",
        "button_bg": "#3d3a2f",
        "button_fg": "#ffe066",
        "button_hover": "#ff8800",
        "input_bg": "#2d2a23",
        "input_fg": "#ffe066",
        "selection_bg": "#ff8800",
        "selection_fg": "#22211f"
    },
    "HiViz": {
        "background": "#1a1a1a12",
        "text": "#eaff00",
        "highlight": "#ffea00",
        "accent": "#00ffea",
        "success": "#00ff00",
        "warning": "#ffea00",
        "error": "#ff1744",
        "info": "#00eaff",
        "border": "#eaff00",
        "button_bg": "#222",
        "button_fg": "#eaff00",
        "button_hover": "#ffea00",
        "input_bg": "#333",
        "input_fg": "#eaff00",
        "selection_bg": "#ffea00",
        "selection_fg": "#1a1a1a"
    },
    "Rainbow": {
        "background": "#22223b26",
        "text": "#f72585",
        "highlight": "#b5179e",
        "accent": "#7209b7",
        "success": "#3a86ff",
        "warning": "#ffbe0b",
        "error": "#ff006e",
        "info": "#43aa8b",
        "border": "#f72585",
        "button_bg": "#3a86ff",
        "button_fg": "#fff",
        "button_hover": "#ffbe0b",
        "input_bg": "#7209b7",
        "input_fg": "#fff",
        "selection_bg": "#ffbe0b",
        "selection_fg": "#22223b"
    },
    "HoneyBee": {
        "background": "#fff8e118",
        "text": "#ff4d00",
        "highlight": "#ffd600",
        "accent": "#ffb300",
        "success": "#cddc39",
        "warning": "#ffd600",
        "error": "#ff7043",
        "info": "#ffb300",
        "border": "#ffb300",
        "button_bg": "#fffde7",
        "button_fg": "#ffb300",
        "button_hover": "#ffd600",
        "input_bg": "#fffde7",
        "input_fg": "#ffb300",
        "selection_bg": "#91ff00",
        "selection_fg": "#fff8e1"
    },
    "Dark Modern": {
        "background": "#0d1b2a1f",
        "text": "#e0e0e0", 
        "highlight": "#4f8cff",
        "accent": "#ff9800",
        "success": "#4caf50",
        "warning": "#ffc107",
        "error": "#f44336",
        "info": "#2196f3",
        "border": "#444a52",
        "button_bg": "#2d323b",
        "button_fg": "#e0e0e0",
        "button_hover": "#3a4050",
        "input_bg": "#23272e",
        "input_fg": "#e0e0e0",
        "selection_bg": "#4f8cff",
        "selection_fg": "#23272e"
    },
    "Something": {
        "background": "#a3a3a318",  # Softer, less bright off-white
        "text": "#fe0000",      # Deep red for font color
        "highlight": "#1976d2",
        "accent": "#ff6f00",
        "success": "#388e3c",
        "warning": "#f57c00",
        "error": "#d32f2f",
        "info": "#0288d1",
        "border": "#b3ea00",
        "button_bg": "#e0e0e0",
        "button_fg": "#b71c1c",
        "button_hover": "#bdbdbd",
        "input_bg": "#f7f3ef",
        "input_fg": "#b71c1c",
        "selection_bg": "#1976d2",
        "selection_fg": "#ffffff"
    },
    "Ocean Blue": {
        "background": "#0d1b2a1a",
        "text": "#a8dadc",
        "highlight": "#457b9d",
        "accent": "#e63946",
        "success": "#2a9d8f",
        "warning": "#e9c46a",
        "error": "#e63946",
        "info": "#457b9d",
        "border": "#1d3557",
        "button_bg": "#1d3557",
        "button_fg": "#a8dadc",
        "button_hover": "#457b9d",
        "input_bg": "#0d1b2a",
        "input_fg": "#a8dadc",
        "selection_bg": "#457b9d",
        "selection_fg": "#f1faee"
    },
    "Forest Green": {
        "background": "#1a2e1a",
        "text": "#c8e6c8",
        "highlight": "#4caf50",
        "accent": "#ff9800",
        "success": "#66bb6a",
        "warning": "#ffb74d",
        "error": "#ef5350",
        "info": "#42a5f5",
        "border": "#2e4e2e",
        "button_bg": "#2e4e2e",
        "button_fg": "#c8e6c8",
        "button_hover": "#4caf50",
        "input_bg": "#1a2e1a",
        "input_fg": "#c8e6c8",
        "selection_bg": "#4caf50",
        "selection_fg": "#1a2e1a"
    }
}

THEME_NAMES = list(THEMES.keys())


class ThemeManager:
    """Manages color themes for the application."""
    
    def __init__(self):
        self.current_theme_index = 0
        self.current_theme_name = THEME_NAMES[0]
        
    def get_current_theme(self) -> Dict[str, str]:
        """Get the current theme colors."""
        return THEMES[self.current_theme_name]
        
    def get_current_theme_name(self) -> str:
        """Get the current theme name."""
        return self.current_theme_name
        
    def cycle_theme(self) -> Dict[str, str]:
        """Cycle to the next theme and return its colors."""
        self.current_theme_index = (self.current_theme_index + 1) % len(THEME_NAMES)
        self.current_theme_name = THEME_NAMES[self.current_theme_index]
        return self.get_current_theme()
        
    def set_theme_by_name(self, theme_name: str) -> bool:
        """Set theme by name. Returns True if successful."""
        if theme_name in THEMES:
            self.current_theme_name = theme_name
            self.current_theme_index = THEME_NAMES.index(theme_name)
            return True
        return False
        
    def set_theme_by_index(self, index: int) -> bool:
        """Set theme by index. Returns True if successful."""
        if 0 <= index < len(THEME_NAMES):
            self.current_theme_index = index
            self.current_theme_name = THEME_NAMES[index]
            return True
        return False
        
    def get_all_theme_names(self) -> list:
        """Get list of all available theme names."""
        return THEME_NAMES.copy()
        
    def get_theme_by_name(self, theme_name: str) -> Dict[str, str]:
        """Get specific theme colors by name."""
        return THEMES.get(theme_name, THEMES[THEME_NAMES[0]])
    
    def get_next_theme(self) -> Dict[str, str]:
        """Get the next theme in the cycle without actually switching to it yet."""
        next_index = (self.current_theme_index + 1) % len(THEME_NAMES)
        next_theme_name = THEME_NAMES[next_index]
        # Actually cycle to the next theme
        return self.cycle_theme()


def apply_theme_to_widget_stylesheet(theme_colors: Dict[str, str], widget_type: str = "general") -> str:
    """Generate stylesheet for widgets based on theme colors and widget type."""
    
    if widget_type == "button":
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {theme_colors['button_bg']}, stop:1 {theme_colors['button_hover']});
                color: {theme_colors['button_fg']};
                border: 2px solid {theme_colors['border']};
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {theme_colors['button_hover']}, stop:1 {theme_colors['highlight']});
                border: 2px solid {theme_colors['highlight']};
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {theme_colors['highlight']}, stop:1 {theme_colors['border']});
            }}
        """
    
    elif widget_type == "success_button":
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {theme_colors['success']}, stop:1 #2e7d32);
                color: white;
                border: 2px solid #388e3c;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #66bb6a, stop:1 {theme_colors['success']});
                border: 2px solid #4caf50;
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2e7d32, stop:1 #1b5e20);
            }}
        """
    
    elif widget_type == "error_button":
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {theme_colors['error']}, stop:1 #a32f2f);
                color: white;
                border: 2px solid #8B0000;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #ff6b6b, stop:1 {theme_colors['error']});
                border: 2px solid #ff4444;
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #a32f2f, stop:1 #8B0000);
            }}
        """
    
    elif widget_type == "info_button":
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {theme_colors['info']}, stop:1 #1565c0);
                color: white;
                border: 2px solid #0277bd;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #42a5f5, stop:1 {theme_colors['info']});
                border: 2px solid #29b6f6;
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #1565c0, stop:1 #0d47a1);
            }}
        """
    
    elif widget_type == "input":
        return f"""
            QLineEdit {{
                background-color: {theme_colors['input_bg']};
                color: {theme_colors['input_fg']};
                border: 2px solid {theme_colors['border']};
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
            }}
            QLineEdit:focus {{
                border: 2px solid {theme_colors['highlight']};
            }}
        """
    
    elif widget_type == "label":
        return f"""
            QLabel {{
                color: {theme_colors['text']};
                background-color: {theme_colors['background']};
            }}
        """
    
    elif widget_type == "main":
        return f"""
            QMainWindow {{
                background-color: {theme_colors['background']};
                color: {theme_colors['text']};
            }}
        """
    
    else:  # general
        return f"""
            QWidget {{
                background-color: {theme_colors['background']};
                color: {theme_colors['text']};
            }}
        """
