"""CLI interface using Typer."""

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from src.duplicates import find_duplicates, prompt_deletion
from src.logger import setup_logger
from src.models import FileInfo
from src.old_files import find_old_files, print_old_files
from src.scanner import scan_directory
from src.sorter import execute_sort, plan_sort
from src.trash_cleaner import clean_trash

app = typer.Typer(help="TidyTrail - Download folder cleaner")
console = Console()


def _format_size(size: int) -> str:
    """Format file size in human-readable form."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


@app.command()
def preview(
    path: Path = typer.Argument(".", help="Directory to scan"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show all files including uncategorized"),
):
    """Show sorting plan (what will go where)."""
    setup_logger()
    console.print(f"[bold]Scanning:[/bold] {path.absolute()}")
    
    try:
        scan = scan_directory(path)
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    
    table = Table(title="Sorting Plan")
    table.add_column("File", style="cyan")
    table.add_column("Category", style="magenta")
    table.add_column("Size", justify="right")
    
    plan = plan_sort(scan, path)
    
    for src, dest in plan.items():
        file_info = next((f for f in scan.files if f.path == src), None)
        size_str = _format_size(file_info.size) if file_info else "?"
        table.add_row(src.name, dest.parent.name, size_str)
    
    console.print(table)
    console.print(f"\n[bold]Summary:[/bold] {len(plan)} files to sort")


@app.command()
def sort(
    path: Path = typer.Argument(".", help="Directory to sort"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview without moving"),
):
    """Sort files into category folders."""
    setup_logger()
    console.print(f"[bold]Sorting:[/bold] {path.absolute()}")
    
    try:
        scan = scan_directory(path)
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    
    plan = plan_sort(scan, path)
    
    if not plan:
        console.print("[green]No files to sort.[/green]")
        return
    
    if dry_run:
        console.print("[yellow]Dry run mode - no files will be moved[/yellow]")
    
    moved, skipped = execute_sort(plan, dry_run=dry_run)
    
    console.print(f"\n[bold green]Done![/bold green] Moved: {moved}, Skipped: {skipped}")


@app.command()
def dupes(
    path: Path = typer.Argument(".", help="Directory to scan"),
):
    """Find and remove duplicate files."""
    setup_logger()
    console.print(f"[bold]Scanning for duplicates:[/bold] {path.absolute()}")
    
    try:
        scan = scan_directory(path)
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    
    console.print(f"[cyan]Computing hashes for {len(scan.files)} files...[/cyan]")
    
    groups = find_duplicates(scan.files)
    
    if not groups:
        console.print("[green]No duplicates found.[/green]")
        return
    
    total_dupes = sum(len(g) - 1 for g in groups.values())
    console.print(f"[yellow]Found {len(groups)} groups with {total_dupes} duplicate files[/yellow]")
    
    deleted = prompt_deletion(groups)
    console.print(f"\n[bold green]Deleted {deleted} duplicate files.[/bold green]")


@app.command()
def old(
    path: Path = typer.Argument(".", help="Directory to scan"),
    days: int = typer.Argument(90, help="Files older than N days"),
):
    """Show files older than N days."""
    setup_logger()
    console.print(f"[bold]Scanning:[/bold] {path.absolute()}")
    
    try:
        scan = scan_directory(path)
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    
    old_files = find_old_files(scan.files, days)
    print_old_files(old_files, days)


@app.command()
def clean(
    path: Path = typer.Argument(".", help="Directory to clean"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """Remove trash files and empty folders."""
    setup_logger()
    console.print(f"[bold]Cleaning:[/bold] {path.absolute()}")
    
    try:
        files_deleted, dirs_deleted = clean_trash(path, confirm=not yes)
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    
    console.print(f"\n[bold green]Done![/bold green] Files: {files_deleted}, Folders: {dirs_deleted}")


if __name__ == "__main__":
    app()
