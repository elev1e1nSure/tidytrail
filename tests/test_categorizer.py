"""Tests for categorizer.py."""

import pytest
from pathlib import Path
from unittest.mock import patch

from src.categorizer import get_category, _init_mimetypes
from src.config import Category


def test_custom_category():
    """Custom category takes precedence."""
    with patch("src.rules.get_custom_category", return_value=Category.VIDEO):
        assert get_category(Path("/test/file.xyz")) == Category.VIDEO


def test_lottie_special_case():
    """.lottie files return IMAGES."""
    with patch("src.rules.get_custom_category", return_value=None):
        assert get_category(Path("/test/anim.lottie")) == Category.IMAGES


def test_unknown_mime():
    """Unknown MIME returns OTHER."""
    with patch("src.rules.get_custom_category", return_value=None):
        with patch("src.categorizer.mimetypes.guess_type", return_value=(None, None)):
            assert get_category(Path("/test/unknown")) == Category.OTHER


def test_mime_categories():
    """Test main MIME type categories."""
    with patch("src.rules.get_custom_category", return_value=None):
        with patch("src.categorizer.mimetypes.guess_type") as mock_guess:
            # Images
            mock_guess.return_value = ("image/jpeg", None)
            assert get_category(Path("/test.jpg")) == Category.IMAGES
            # Video
            mock_guess.return_value = ("video/mp4", None)
            assert get_category(Path("/test.mp4")) == Category.VIDEO
            # Audio
            mock_guess.return_value = ("audio/mp3", None)
            assert get_category(Path("/test.mp3")) == Category.AUDIO
            # Docs
            mock_guess.return_value = ("application/pdf", None)
            assert get_category(Path("/test.pdf")) == Category.DOCS
            # Archives
            mock_guess.return_value = ("application/zip", None)
            assert get_category(Path("/test.zip")) == Category.ARCHIVES
            # Executables
            mock_guess.return_value = ("application/x-executable", None)
            assert get_category(Path("/test.exe")) == Category.EXECUTABLES
            # Text
            mock_guess.return_value = ("text/plain", None)
            assert get_category(Path("/test.txt")) == Category.DOCS
            # Code
            mock_guess.return_value = ("application/javascript", None)
            assert get_category(Path("/test.js")) == Category.CODE
            # Other application
            mock_guess.return_value = ("application/octet-stream", None)
            assert get_category(Path("/test.bin")) == Category.OTHER


def test_init_mimetypes():
    """Mimetypes initialized once."""
    import src.categorizer
    src.categorizer._mimetypes_initialized = False
    _init_mimetypes()
    assert src.categorizer._mimetypes_initialized
