"""Tests for stats.py."""

import pytest
from pathlib import Path

from src.stats import get_folder_stats, format_size


def test_format_size():
    """Format file sizes."""
    assert "B" in format_size(100)
    assert "KB" in format_size(2048)
    assert "MB" in format_size(2 * 1024 * 1024)


def test_get_folder_stats(tmp_path):
    """Get folder statistics."""
    (tmp_path / "test.txt").write_text("content")
    stats = get_folder_stats(tmp_path, recursive=False)
    assert stats["total_files"] == 1
    assert stats["total_size"] > 0
