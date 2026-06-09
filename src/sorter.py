"""File sorting functionality."""

import shutil
from pathlib import Path
from typing import Optional

from rich.progress import Progress, SpinnerColumn, TextColumn

from src.config import Category
from src.logger import get_logger
from src.models import FileInfo, ScanResult
from src.undo import log_sort_operation
from src.categorizer import get_category


def _generate_unique_name(target_dir: Path, filename: str) -> Path:
    """Generate unique filename if collision exists."""
    stem = target_dir / filename
    if not stem.exists():
        return stem
    
    name = Path(filename)
    base = name.stem
    ext = name.suffix
    counter = 1
    
    while True:
        new_name = f"{base}_{counter}{ext}"
        candidate = target_dir / new_name
        if not candidate.exists():
            return candidate
        counter += 1


def plan_sort(scan: ScanResult, target: Path) -> dict[Path, Path]:
    """Create sorting plan: source -> destination."""
    plan: dict[Path, Path] = {}
    
    for file_info in scan.files:
        if file_info.path.is_dir():
            continue
            
        category = _get_category_for_file(file_info)
        if category == Category.OTHER:
            continue
        
        dest_dir = target / category.value
        dest_path = _generate_unique_name(dest_dir, file_info.name)
        plan[file_info.path] = dest_path
    
    return plan


def _get_category_for_file(file_info: FileInfo) -> Category:
    """Get category for file based on extension."""
    return get_category(file_info.path)


def execute_sort(plan: dict[Path, Path], dry_run: bool = False) -> tuple[int, int]:
    """Execute sorting plan. Returns (moved, skipped)."""
    logger = get_logger()
    moved = 0
    skipped = 0
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
    ) as progress:
        task = progress.add_task("Sorting files...", total=len(plan))
        
        for src, dest in plan.items():
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                
                if not dry_run:
                    shutil.move(str(src), str(dest))
                    log_sort_operation(src, dest)
                
                logger.info(f"Moved: {src} -> {dest}")
                moved += 1
            except (PermissionError, OSError) as e:
                logger.warning(f"Failed to move {src}: {e}")
                skipped += 1
            
            progress.advance(task)
    
    return moved, skipped
