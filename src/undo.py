"""Undo functionality for sort operations."""

import json
from pathlib import Path
from datetime import datetime

from src.logger import get_logger

logger = get_logger()
HISTORY_FILE = Path("tidytrail_sort_history.json")


def log_sort_operation(source: Path, destination: Path):
    """Log a file move operation."""
    history = load_history()
    history.append({
        "source": str(source),
        "destination": str(destination),
        "timestamp": datetime.now().isoformat(),
    })
    save_history(history)
    logger.info(f"Logged sort: {source} -> {destination}")


def load_history() -> list[dict]:
    """Load sort history."""
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_history(history: list[dict]):
    """Save sort history."""
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def undo_last_operation() -> tuple[int, int]:
    """Undo all sort operations. Returns (moved, failed)."""
    history = load_history()
    if not history:
        return 0, 0
    
    moved = 0
    failed = 0
    
    for op in reversed(history):
        src = Path(op["source"])
        dst = Path(op["destination"])
        
        if dst.exists() and src.parent != dst.parent:
            try:
                src.parent.mkdir(parents=True, exist_ok=True)
                dst.rename(src)
                logger.info(f"Undone: {dst} -> {src}")
                moved += 1
            except (OSError, PermissionError) as e:
                logger.warning(f"Failed to undo: {e}")
                failed += 1
    
    clear_history()
    return moved, failed


def clear_history():
    """Clear sort history."""
    if HISTORY_FILE.exists():
        HISTORY_FILE.unlink()
    logger.info("Sort history cleared")
