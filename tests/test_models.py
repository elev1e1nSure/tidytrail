"""Tests for models.py."""

from pathlib import Path
from src.models import FileInfo, ScanResult
from src.config import Category


def test_file_info():
    """FileInfo creation."""
    info = FileInfo(Path("/test.txt"), 100, 1.0)
    assert info.path == Path("/test.txt")
    assert info.size == 100
    assert info.mtime == 1.0


def test_scan_result():
    """ScanResult creation."""
    files = [FileInfo(Path("/a.txt"), 100, 1.0)]
    categories = {Category.DOCS: 1}
    result = ScanResult(files=files, categories=categories)
    assert len(result.files) == 1
    assert result.categories[Category.DOCS] == 1
