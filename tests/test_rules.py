"""Tests for rules.py."""

from unittest.mock import patch
from src.rules import add_rule, remove_rule, list_rules


def test_add_valid_rule():
    """Add valid rule."""
    with patch("src.rules.load_rules", return_value={}):
        with patch("src.rules.save_rules"):
            assert add_rule(".xyz", "images")


def test_add_invalid_rule():
    """Reject invalid category."""
    with patch("src.rules.load_rules", return_value={}):
        assert not add_rule(".xyz", "invalid")


def test_list_rules():
    """List all rules."""
    with patch("src.rules.load_rules", return_value={".xyz": "images"}):
        assert list_rules() == {".xyz": "images"}
