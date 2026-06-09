"""Trash and empty folder cleaning."""

from pathlib import Path

from rich.console import Console
from rich.prompt import Confirm

from src.config import TRASH_EXTENSIONS
from src.logger import get_logger

console = Console()
logger = get_logger()


def find_trash_files(path: Path, recursive: bool = False) -> list[Path]:
    """Find trash files in directory."""
    trash: list[Path] = []
    
    if recursive:
        iterator = path.rglob("*")
    else:
        iterator = path.iterdir()
    
    for item in iterator:
        if item.is_file():
            if item.suffix.lower() in TRASH_EXTENSIONS:
                trash.append(item)
            elif item.name.startswith(".") and item.suffix == "":
                if item.name in {".DS_Store", ".Thumbs.db", "desktop.ini"}:
                    trash.append(item)
    
    return trash


def find_empty_dirs(path: Path, recursive: bool = False) -> list[Path]:
    """Find empty directories."""
    empty: list[Path] = []
    
    if recursive:
        iterator = path.rglob("*")
    else:
        iterator = path.iterdir()
    
    for item in iterator:
        if item.is_dir() and not item.is_symlink():
            try:
                if not any(item.iterdir()):
                    empty.append(item)
            except (PermissionError, OSError):
                continue
    
    return empty


def clean_trash(path: Path, confirm: bool = True, recursive: bool = False) -> tuple[int, int]:
    """Clean trash files and empty directories. Returns (files_deleted, dirs_deleted)."""
    trash_files = find_trash_files(path, recursive=recursive)
    empty_dirs = find_empty_dirs(path, recursive=recursive)
    
    if not trash_files and not empty_dirs:
        console.print("[green]No trash files or empty folders found.[/green]")
        return 0, 0
    
    console.print(f"\n[bold]Found:[/bold]")
    console.print(f"  Trash files: {len(trash_files)}")
    console.print(f"  Empty folders: {len(empty_dirs)}")
    
    if confirm:
        if not Confirm.ask("Delete these files and folders?"):
            console.print("[yellow]Cancelled.[/yellow]")
            return 0, 0
    
    files_deleted = 0
    dirs_deleted = 0
    
    for f in trash_files:
        try:
            f.unlink()
            logger.info(f"Deleted trash file: {f}")
            files_deleted += 1
            console.print(f"  [red]Deleted:[/red] {f.name}")
        except (PermissionError, OSError) as e:
            logger.warning(f"Failed to delete {f}: {e}")
            console.print(f"  [yellow]Failed:[/yellow] {f.name}")
    
    for d in empty_dirs:
        try:
            d.rmdir()
            logger.info(f"Deleted empty folder: {d}")
            dirs_deleted += 1
            console.print(f"  [red]Deleted:[/red] {d.name}/")
        except (PermissionError, OSError) as e:
            logger.warning(f"Failed to delete {d}: {e}")
    
    return files_deleted, dirs_deleted
