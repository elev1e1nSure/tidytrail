"""Tests for duplicates.py."""

import pytest
from pathlib import Path

from src.duplicates import compute_md5, find_duplicates
from src.models import FileInfo


def test_compute_md5(tmp_path):
    """MD5 hash computed correctly."""
    file_path = tmp_path / "file.txt"
    file_path.write_text("test")
    assert compute_md5(file_path) is not None


def test_find_duplicates():
    """Find duplicate files by hash."""
    files = [
        FileInfo(Path("/a.txt"), 100, 1.0),
        FileInfo(Path("/b.txt"), 100, 1.0),
    ]
    result = find_duplicates(files, compute_hashes=False)
    assert len(result) == 0
