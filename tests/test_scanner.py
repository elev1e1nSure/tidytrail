"""Tests for scanner.py."""

import pytest
from pathlib import Path
from unittest.mock import patch

from src.scanner import scan_directory
from src.models import ScanResult


def test_scan_directory(tmp_path):
    """Scan directory returns files."""
    (tmp_path / "test.txt").write_text("content")
    result = scan_directory(tmp_path, recursive=False)
    assert len(result.files) == 1


def test_scan_not_found():
    """Handle non-existent directory."""
    with pytest.raises(FileNotFoundError):
        scan_directory(Path("/nonexistent"))


def test_scan_recursive(tmp_path):
    """Recursive scan includes subdirectories."""
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "test.txt").write_text("content")
    result = scan_directory(tmp_path, recursive=True)
    assert len(result.files) == 1
