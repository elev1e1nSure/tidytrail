"""File categorization by extension."""

from pathlib import Path

from src.config import Category, EXTENSIONS


def get_category(file: Path) -> Category:
    """Determine category based on file extension (case-insensitive)."""
    ext = file.suffix.lower()
    
    for category, extensions in EXTENSIONS.items():
        if ext in extensions:
            return category
    
    return Category.OTHER
