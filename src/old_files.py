"""Old file detection by modification time."""

import time
from datetime import datetime
from typing import Optional

from src.models import FileInfo


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


def find_old_files(files: list[FileInfo], days: int) -> list[FileInfo]:
    """Find files older than specified days (by modification time)."""
    cutoff = time.time() - (days * 24 * 60 * 60)
    return [f for f in files if f.mtime < cutoff]


def print_old_files(files: list[FileInfo], days: int) -> None:
    """Print list of old files in formatted table."""
    from rich.console import Console
    from rich.table import Table
    
    console = Console()
    
    if not files:
        console.print(f"[green]No files older than {days} days found.[/green]")
        return
    
    table = Table(title=f"Files older than {days} days")
    table.add_column("Name", style="cyan")
    table.add_column("Size", justify="right")
    table.add_column("Modified", justify="right")
    table.add_column("Age (days)", justify="right")
    
    now = time.time()
    
    for f in sorted(files, key=lambda x: x.mtime):
        age_days = int((now - f.mtime) / (24 * 60 * 60))
        table.add_row(
            f.name,
            _format_size(f.size),
            _format_date(f.mtime),
            str(age_days)
        )
    
    console.print(table)
    console.print(f"\n[bold]Total:[/bold] {len(files)} files")
