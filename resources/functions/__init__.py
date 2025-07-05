"""
Functions package for the Barbell Calculator application.

This package contains modularized functions organized by functionality:
- utils: Core utility functions
- weight_calculations: Weight conversions and calculations
- theme_manager: Theme loading and management
- image_processing: Image manipulation and caching
- user_management: User data operations
- color_themes: GUI color theme management
- tools: Stopwatch, timer and other utilities

Usage:
    from resources.functions import utils, weight_calculations, theme_manager, image_processing, user_management, color_themes, tools
"""

# Import commonly used functions for easier access
from .utils import resource_path, load_config, round_weight
from .weight_calculations import (
    compute_dots, 
    compute_wilks,
    compute_wilks2,
    compute_ipf,
    compute_ipf_gl,
    convert_lb_to_kg, 
    convert_kg_to_lb, 
    convert_kg_to_stone,
    calculate_total_lifts,
    CONVERSION_FACTOR_LB_TO_KG,
    CONVERSION_FACTOR_KG_TO_STONE
)
from .theme_manager import (
    get_theme_folder, 
    get_image_path, 
    load_available_themes,
    filter_themes_by_text,
    filter_themes_by_category
)
from .image_processing import (
    create_combined_image_pixmap,
    get_cached_static_image,
    pil_to_pixmap,
    cleanup_temp_files,
    load_and_validate_image
)
from .user_management import (
    load_users_from_csv,
    save_users_to_csv,
    import_users_from_csv_file,
    export_users_to_csv_file,
    save_removed_user,
    backup_users_data,
    update_user_dots,
    update_user_scores,
    validate_user_data,
    filter_users_by_text,
    sort_users_by_column,
    load_judge_scores,
    ensure_user_completeness,
    LIFT_COLS
)
from .color_themes import (
    ThemeManager,
    THEMES,
    THEME_NAMES,
    apply_theme_to_widget_stylesheet
)
from .tools import (
    StopwatchDialog,
    TimerDialog,
    get_powerlifting_rules_url,
    open_rules_link
)

__all__ = [
    # Utils
    'resource_path', 'load_config', 'round_weight',
    
    # Weight calculations
    'compute_dots', 'compute_wilks', 'compute_wilks2', 'compute_ipf', 'compute_ipf_gl',
    'convert_lb_to_kg', 'convert_kg_to_lb', 'convert_kg_to_stone',
    'calculate_total_lifts', 'CONVERSION_FACTOR_LB_TO_KG', 'CONVERSION_FACTOR_KG_TO_STONE',
    
    # Theme management
    'get_theme_folder', 'get_image_path', 'load_available_themes',
    'filter_themes_by_text', 'filter_themes_by_category',
    
    # Image processing
    'create_combined_image_pixmap', 'get_cached_static_image', 'pil_to_pixmap',
    'cleanup_temp_files', 'load_and_validate_image',
    
    # User management
    'load_users_from_csv', 'save_users_to_csv', 'import_users_from_csv_file',
    'export_users_to_csv_file', 'save_removed_user', 'backup_users_data',
    'update_user_dots', 'update_user_scores', 'validate_user_data', 'filter_users_by_text',
    'sort_users_by_column', 'load_judge_scores', 'ensure_user_completeness',
    'LIFT_COLS',
    
    # Color themes
    'ThemeManager', 'THEMES', 'THEME_NAMES', 'apply_theme_to_widget_stylesheet',
    
    # Tools
    'StopwatchDialog', 'TimerDialog', 'get_powerlifting_rules_url', 'open_rules_link'
]
