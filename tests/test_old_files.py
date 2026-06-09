"""Tests for old_files.py."""

import pytest
from pathlib import Path
from unittest.mock import patch
from datetime import datetime, timedelta

from src.old_files import find_old_files
from src.models import FileInfo


def test_find_old_files():
    """Find files older than N days."""
    cutoff = datetime.now() - timedelta(days=90)
    old_file = FileInfo(Path("/old.txt"), 100, cutoff.timestamp() - 1000)
    new_file = FileInfo(Path("/new.txt"), 100, datetime.now().timestamp())
    
    result = find_old_files([old_file, new_file], 90)
    assert len(result) == 1
    assert result[0].path == old_file.path
