"""
Theme management functions.
Handles theme loading, filtering, and path resolution.
"""

import os
from .utils import resource_path


def get_theme_folder(selected_theme: str, theme_path: str = "BarBellWeights") -> str:
    """Get theme folder path."""
    base_path = resource_path("")
    return os.path.join(base_path, theme_path, selected_theme)


def get_image_path(theme: str, image_name: str, theme_path: str = "BarBellWeights") -> str:
    """Get full image path for theme."""
    folder = get_theme_folder(theme, theme_path)
    return os.path.join(folder, image_name)


def load_available_themes(theme_path: str = "BarBellWeights") -> dict:
    """Load available themes and categorize them."""
    base_path = resource_path("")
    full_theme_path = os.path.join(base_path, theme_path)
    
    themes = []
    if os.path.exists(full_theme_path):
        themes = [name for name in os.listdir(full_theme_path) 
                 if os.path.isdir(os.path.join(full_theme_path, name))]
    else:
        themes = ["lb_color", "kg_color", "dumbell_orange"]  # Default themes
    
    # Categorize themes
    lb_themes = [theme for theme in themes if theme.startswith("lb_")]
    kg_themes = [theme for theme in themes if theme.startswith("kg_")]
    other_themes = [theme for theme in themes if not (theme.startswith("lb_") or theme.startswith("kg_"))]
    
    return {
        "all": lb_themes + kg_themes + other_themes,
        "lb": lb_themes,
        "kg": kg_themes,
        "other": other_themes
    }


def filter_themes_by_text(themes: list, filter_text: str) -> list:
    """Filter themes by search text."""
    if not filter_text:
        return themes
    return [theme for theme in themes if filter_text.lower() in theme.lower()]


def filter_themes_by_category(themes: dict, category: str) -> list:
    """Filter themes by category (All, lb_, kg_, Other)."""
    if category == "All":
        return themes["all"]
    elif category == "Other":
        return themes["other"]
    elif category.startswith("lb_"):
        return themes["lb"]
    elif category.startswith("kg_"):
        return themes["kg"]
    else:
        return themes["all"]
