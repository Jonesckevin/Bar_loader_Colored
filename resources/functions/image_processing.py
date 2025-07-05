"""
Image processing functions.
Handles image loading, combining, caching, and conversion operations.
"""

import os
import io
from typing import Optional

try:
    from PIL import Image
except ImportError:
    Image = None

from PyQt6.QtGui import QPixmap
from .theme_manager import get_image_path


def create_combined_image_pixmap(image_path: str, selected_theme: str, static_image_cache: dict) -> QPixmap:
    """Create combined image pixmap in memory without file I/O."""
    if not Image:
        return QPixmap()
        
    try:
        # Load and resize main image
        with Image.open(image_path) as image:
            # Use faster nearest neighbor for initial resize, then smooth for final
            image = image.resize((180, 180), Image.Resampling.NEAREST)
            inverted_image = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            
            # Get or create cached static image
            static_image = get_cached_static_image(selected_theme, static_image_cache)
            
            # Create combined image
            combined_width = image.width * 2 + static_image.width
            combined_image = Image.new("RGBA", (combined_width, image.height))
            combined_image.paste(image, (0, 0))
            combined_image.paste(static_image, (image.width, 0))
            combined_image.paste(inverted_image, (image.width + static_image.width, 0))
            
            # Convert PIL image directly to QPixmap without saving to disk
            return pil_to_pixmap(combined_image)
            
    except Exception as e:
        print(f"Error creating combined image: {e}")
        return QPixmap()


def get_cached_static_image(selected_theme: str, static_image_cache: dict):
    """Get cached static bar image or create and cache it."""
    if selected_theme in static_image_cache:
        return static_image_cache[selected_theme]
    
    static_image_path = get_image_path(selected_theme, "bar.png")
    if os.path.exists(static_image_path):
        with Image.open(static_image_path) as static_img:
            # Cache resized static image
            resized_static = static_img.resize((250, 180), Image.Resampling.NEAREST)
            static_image_cache[selected_theme] = resized_static.copy()
    else:
        # Create and cache default static image
        default_static = Image.new("RGBA", (250, 180), (255, 255, 255, 0))
        static_image_cache[selected_theme] = default_static
    
    return static_image_cache[selected_theme]


def pil_to_pixmap(pil_image) -> QPixmap:
    """Convert PIL image to QPixmap without file I/O."""
    # Convert PIL image to bytes
    byte_array = io.BytesIO()
    pil_image.save(byte_array, format='PNG')
    byte_array = byte_array.getvalue()
    
    # Create QPixmap from bytes
    pixmap = QPixmap()
    pixmap.loadFromData(byte_array)
    return pixmap


def cleanup_temp_files(resources_dir: str) -> None:
    """Clean up temporary combined image files."""
    import os
    import fnmatch
    try:
        if os.path.exists(resources_dir):
            for root, dirs, files in os.walk(resources_dir):
                for filename in files:
                    if fnmatch.fnmatch(filename, "temp_combined_*.png"):
                        temp_file_path = os.path.join(root, filename)
                        try:
                            os.remove(temp_file_path)
                            print(f"Deleted temporary file: {temp_file_path}")
                        except Exception as e:
                            print(f"Failed to delete {temp_file_path}: {e}")
    except Exception as e:
        print(f"Error during cleanup: {e}")


def load_and_validate_image(image_path: str) -> bool:
    """Check if an image file exists and can be loaded."""
    if not os.path.exists(image_path):
        return False
    
    if not Image:
        return True  # Assume valid if PIL not available
    
    try:
        with Image.open(image_path) as img:
            img.verify()  # Verify that it's a valid image
        return True
    except Exception:
        return False
