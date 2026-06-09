"""Tests for sorter.py."""

from pathlib import Path
from unittest.mock import patch

from src.sorter import plan_sort
from src.models import FileInfo, ScanResult
from src.config import Category


def test_plan_sort():
    """Plan file moves by category."""
    files = [FileInfo(Path("/test.txt"), 100, 1.0)]
    scan = ScanResult(files=files, categories={Category.DOCS: 1})
    with patch("src.categorizer.get_category", return_value=Category.DOCS):
        plan = plan_sort(scan, Path("/downloads"))
    assert len(plan) == 1
