"""Folder statistics module."""

from pathlib import Path
from collections import Counter

from src.categorizer import get_category
from src.config import Category


def get_folder_stats(path: Path, recursive: bool = False) -> dict:
    """Get folder statistics."""
    files = list(path.rglob("*") if recursive else path.iterdir())
    files = [f for f in files if f.is_file()]
    
    total_size = sum(f.stat().st_size for f in files)
    
    categories = Counter(get_category(f) for f in files)
    
    largest = sorted(files, key=lambda f: f.stat().st_size, reverse=True)[:10]
    largest_files = [
        {"name": f.name, "size": f.stat().st_size, "path": f.parent}
        for f in largest
    ]
    
    return {
        "total_files": len(files),
        "total_size": total_size,
        "by_category": dict(categories),
        "largest_files": largest_files,
    }


def format_size(size: int) -> str:
    """Format size in human readable form."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"
