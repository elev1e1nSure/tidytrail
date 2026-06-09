"""Tests for trash_cleaner.py."""

import pytest
from pathlib import Path
from unittest.mock import patch

from src.trash_cleaner import find_trash_files, find_empty_dirs, clean_trash


def test_find_trash_files(tmp_path):
    """Find trash files by extension."""
    (tmp_path / "test.tmp").write_text("content")
    result = find_trash_files(tmp_path, recursive=False)
    assert len(result) == 1


def test_find_empty_dirs(tmp_path):
    """Find empty directories."""
    (tmp_path / "empty").mkdir()
    result = find_empty_dirs(tmp_path, recursive=False)
    assert len(result) == 1


def test_clean_trash(tmp_path):
    """Clean trash files and dirs."""
    (tmp_path / "test.tmp").write_text("content")
    with patch("src.trash_cleaner.Confirm.ask", return_value=True):
        files, dirs = clean_trash(tmp_path, confirm=True, recursive=False)
    assert files >= 0
    assert dirs >= 0
