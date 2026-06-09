"""Logging functionality."""

import logging
from pathlib import Path

from src.config import LOG_FILE


def setup_logger(name: str = "tidytrail", log_file: str = LOG_FILE) -> logging.Logger:
    """Setup logger with file handler."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = logging.FileHandler(log_file, encoding="utf-8")
        handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
    
    return logger


def get_logger(name: str = "tidytrail") -> logging.Logger:
    """Get existing logger or create new one."""
    return logging.getLogger(name)
