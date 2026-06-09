"""Tests for undo.py."""

from unittest.mock import patch
from src.undo import undo_last_operation


def test_undo_no_history():
    """Return (0, 0) if no history."""
    with patch("src.undo.load_history", return_value=[]):
        moved, failed = undo_last_operation()
    assert moved == 0
    assert failed == 0
