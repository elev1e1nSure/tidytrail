"""File categorization by MIME type using mimetypes module."""

import mimetypes
from pathlib import Path

from src.config import Category

_mime_categories: dict[str, Category] = {
    "image": Category.IMAGES,
    "video": Category.VIDEO,
    "audio": Category.AUDIO,
    "application/pdf": Category.DOCS,
    "application/msword": Category.DOCS,
    "application/vnd.openxmlformats-officedocument": Category.DOCS,
    "application/vnd.ms-excel": Category.DOCS,
    "application/vnd.ms-powerpoint": Category.DOCS,
    "text/plain": Category.DOCS,
    "text/csv": Category.DOCS,
    "application/zip": Category.ARCHIVES,
    "application/x-rar": Category.ARCHIVES,
    "application/x-7z": Category.ARCHIVES,
    "application/x-tar": Category.ARCHIVES,
    "application/gzip": Category.ARCHIVES,
    "application/x-bzip2": Category.ARCHIVES,
    "application/x-xz": Category.ARCHIVES,
    "application/x-iso": Category.ARCHIVES,
    "application/x-executable": Category.EXECUTABLES,
    "application/x-msdownload": Category.EXECUTABLES,
    "application/x-deb": Category.EXECUTABLES,
    "application/x-rpm": Category.EXECUTABLES,
    "application/x-apple": Category.EXECUTABLES,
}

_mimetypes_initialized = False


def _init_mimetypes():
    """Initialize mimetypes with additional common types (one-time)."""
    global _mimetypes_initialized
    if _mimetypes_initialized:
        return
    
    mimetypes.init()
    mimetypes.add_type("image/webp", ".webp")
    mimetypes.add_type("image/heic", ".heic")
    mimetypes.add_type("image/jfif", ".jfif")
    mimetypes.add_type("application/x-7z-compressed", ".7z")
    mimetypes.add_type("application/vnd.apple.keynote", ".key")
    mimetypes.add_type("application/vnd.apple.numbers", ".numbers")
    mimetypes.add_type("application/vnd.apple.pages", ".pages")
    mimetypes.add_type("application/json", ".lottie")
    _mimetypes_initialized = True


def get_category(file: Path) -> Category:
    """Determine category based on MIME type."""
    _init_mimetypes()
    
    # Special case for .lottie files (animations)
    if file.suffix.lower() == ".lottie":
        return Category.IMAGES
    
    mime_type, _ = mimetypes.guess_type(str(file))
    
    if not mime_type:
        return Category.OTHER
    
    for prefix, category in _mime_categories.items():
        if mime_type == prefix or mime_type.startswith(prefix + "/"):
            return category
    
    if mime_type.startswith("text/"):
        return Category.DOCS
    
    if mime_type.startswith("application/"):
        if "script" in mime_type or "javascript" in mime_type:
            return Category.CODE
        if "python" in mime_type:
            return Category.CODE
    
    return Category.OTHER
