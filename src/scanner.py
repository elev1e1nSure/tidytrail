"""Directory scanning functionality."""

from pathlib import Path

from src.categorizer import get_category
from src.config import Category
from src.models import FileInfo, ScanResult


def scan_directory(path: Path) -> ScanResult:
    """Scan directory for files (top-level only, ignores subdirectories)."""
    if not path.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")
    
    if not path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {path}")
    
    files: list[FileInfo] = []
    categories: dict[Category, list[FileInfo]] = {cat: [] for cat in Category}
    
    for item in path.iterdir():
        if item.is_file() and not item.is_symlink():
            try:
                stat = item.stat()
                file_info = FileInfo(
                    path=item,
                    size=stat.st_size,
                    mtime=stat.st_mtime
                )
                files.append(file_info)
                
                category = get_category(item)
                categories[category].append(file_info)
            except (PermissionError, OSError):
                continue
    
    return ScanResult(files=files, categories=categories)
