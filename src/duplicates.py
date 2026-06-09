"""Duplicate file detection using MD5 hash."""

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.prompt import Prompt

from src.logger import get_logger
from src.models import FileInfo

console = Console()
logger = get_logger()

CHUNK_SIZE = 8192


def compute_md5(file_path: Path) -> Optional[str]:
    """Compute MD5 hash of file (reads in chunks for large files)."""
    try:
        md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            while chunk := f.read(CHUNK_SIZE):
                md5.update(chunk)
        return md5.hexdigest()
    except (PermissionError, OSError) as e:
        logger.warning(f"Failed to hash {file_path}: {e}")
        return None


def find_duplicates(files: list[FileInfo], compute_hashes: bool = True) -> dict[str, list[FileInfo]]:
    """Find duplicate files by content hash."""
    hash_groups: dict[str, list[FileInfo]] = {}
    
    for file_info in files:
        if file_info.size == 0:
            continue
            
        if compute_hashes:
            file_hash = compute_md5(file_info.path)
            if file_hash:
                file_info.hash = file_hash
                if file_hash not in hash_groups:
                    hash_groups[file_hash] = []
                hash_groups[file_hash].append(file_info)
    
    return {k: v for k, v in hash_groups.items() if len(v) > 1}


def _format_size(size: int) -> str:
    """Format file size in human-readable form."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def _format_date(mtime: float) -> str:
    """Format modification time."""
    return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")


def prompt_deletion(groups: dict[str, list[FileInfo]]) -> int:
    """Interactive prompt for duplicate deletion. Returns count of deleted files."""
    deleted = 0
    
    for hash_val, file_list in groups.items():
        console.print(f"\n[bold cyan]Duplicate group (MD5: {hash_val[:8]}...)[/bold cyan]")
        
        sorted_files = sorted(file_list, key=lambda f: f.mtime, reverse=True)
        
        for i, f in enumerate(sorted_files):
            console.print(f"  [{i+1}] {f.path.name}", escape=False)
            console.print(f"      Size: {_format_size(f.size)} | Modified: {_format_date(f.mtime)}")
            console.print(f"      Path: {f.path.parent}")
        
        console.print("")
        console.print("  [n] - keep newest, delete old ones", escape=False)
        console.print("  [o] - keep oldest, delete new ones", escape=False)
        console.print("  [f] - keep first, delete rest", escape=False)
        console.print("  [s] - keep all, skip", escape=False)
        console.print("  [q] - exit", escape=False)
        
        choice = console.input("\nChoose action [n/o/f/s/q]: ").strip().lower() or "s"
        
        if choice not in ("n", "o", "f", "s", "q"):
            console.print("[yellow]Invalid choice, skipping...[/yellow]")
            continue
        
        if choice == "q":
            break
        elif choice == "s":
            continue
        elif choice == "n":
            to_delete = sorted_files[1:]
        elif choice == "o":
            to_delete = sorted_files[:-1]
        elif choice == "f":
            to_delete = sorted_files[1:]
        
        for f in to_delete:
            try:
                f.path.unlink()
                logger.info(f"Deleted duplicate: {f.path}")
                deleted += 1
                console.print(f"  [red]Deleted:[/red] {f.path.name}")
            except (PermissionError, OSError) as e:
                logger.warning(f"Failed to delete {f.path}: {e}")
                console.print(f"  [yellow]Failed to delete:[/yellow] {f.path.name}")
    
    return deleted
