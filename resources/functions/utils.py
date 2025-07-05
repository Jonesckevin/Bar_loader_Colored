"""
Utility functions for the Barbell Calculator application.
Contains core utility functions used throughout the application.
"""

import sys
import os
import json
from typing import Dict, Any


def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller .exe."""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
        # Go up two levels from resources/functions/ to get to the main directory
        base_path = os.path.dirname(os.path.dirname(base_path))
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
