"""CLI interface using Typer."""

from pathlib import Path

import typer
from platformdirs import user_downloads_dir
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


def run_interactive():
    """Interactive menu-driven mode."""
    setup_logger()
    
    while True:
        console.print("\n[bold cyan]╔══════════════════════════════════╗[/bold cyan]")
        console.print("[bold cyan]║          TidyTrail               ║[/bold cyan]")
        console.print("[bold cyan]╚══════════════════════════════════╝[/bold cyan]")
        console.print("")
        console.print("  [1] 📋 Preview - Show sorting plan")
        console.print("  [2] 📁 Sort   - Organize files by category")
        console.print("  [3] 🔍 Dupes  - Find and remove duplicates")
        console.print("  [4] 📅 Old    - Show old files")
        console.print("  [5] 🧹 Clean  - Remove trash files")
        console.print("  [6] ⚙️  Settings - Configure options")
        console.print("")
        console.print("  [Enter] Exit")
        
        choice = console.input("\n[bold]›[/bold] ").strip().lower()
        
        if choice in ("", "q", "quit", "exit"):
            console.print("\n[dim]Goodbye![/dim]")
            break
        
        target_path = get_default_downloads()
        recursive = False
        
        if choice == "6":
            console.print("\n[bold]Settings:[/bold]")
            console.print(f"  Target folder: {target_path}")
            r = console.input("  Recursive (y/n)? ").lower().strip() == "y"
            recursive = r
            console.print(f"  Recursive: {recursive}")
            console.print("[green]Settings updated![/green]")
            continue
        
        if choice not in ("1", "2", "3", "4", "5"):
            if choice != "":
                console.print("[red]Invalid option[/red]")
            continue
        
        if choice in ("3", "4", "5"):
            r = console.input("  Scan subdirectories (y/n)? ").lower().strip() == "y"
            recursive = r
        
        console.print(f"\n[bold]Target:[/bold] {target_path}")
        
        try:
            if choice == "1":
                scan = scan_directory(target_path, recursive=recursive)
                plan = plan_sort(scan, target_path)
                table = Table(title="Sorting Plan")
                table.add_column("File", style="cyan")
                table.add_column("Category", style="magenta")
                table.add_column("Size", justify="right")
                for src, dest in plan.items():
                    file_info = next((f for f in scan.files if f.path == src), None)
                    size_str = _format_size(file_info.size) if file_info else "?"
                    table.add_row(src.name, dest.parent.name, size_str)
                console.print(table)
                console.print(f"\n[bold]Summary:[/bold] {len(plan)} files to sort")
                
            elif choice == "2":
                scan = scan_directory(target_path, recursive=recursive)
                plan = plan_sort(scan, target_path)
                if not plan:
                    console.print("[green]No files to sort.[/green]")
                else:
                    moved, skipped = execute_sort(plan, dry_run=False)
                    console.print(f"\n[bold green]Done![/bold green] Moved: {moved}, Skipped: {skipped}")
                    
            elif choice == "3":
                scan = scan_directory(target_path, recursive=recursive)
                console.print(f"[cyan]Computing hashes for {len(scan.files)} files...[/cyan]")
                groups = find_duplicates(scan.files)
                if not groups:
                    console.print("[green]No duplicates found.[/green]")
                else:
                    total_dupes = sum(len(g) - 1 for g in groups.values())
                    console.print(f"[yellow]Found {len(groups)} groups with {total_dupes} duplicate files[/yellow]")
                    deleted = prompt_deletion(groups)
                    console.print(f"\n[bold green]Deleted {deleted} duplicate files.[/bold green]")
                    
            elif choice == "4":
                days_str = console.input("  Days (default 90): ").strip()
                days = int(days_str) if days_str else 90
                scan = scan_directory(target_path, recursive=recursive)
                old_files = find_old_files(scan.files, days)
                print_old_files(old_files, days)
                
            elif choice == "5":
                files_deleted, dirs_deleted = clean_trash(target_path, confirm=True, recursive=recursive)
                console.print(f"\n[bold green]Done![/bold green] Files: {files_deleted}, Folders: {dirs_deleted}")
                
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")


def get_default_downloads() -> Path:
    """Get user's Downloads folder, fallback to current directory."""
    downloads = user_downloads_dir()
    if downloads and Path(downloads).exists():
        return Path(downloads)
    return Path.cwd()


def _format_size(size: int) -> str:
    """Format file size in human-readable form."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


@app.command()
def preview(
    path: Path = typer.Argument(None, help="Directory to scan (default: Downloads folder)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show all files including uncategorized"),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Scan subdirectories"),
):
    """Show sorting plan (what will go where)."""
    if path is None:
        path = get_default_downloads()
    setup_logger()
    console.print(f"[bold]Scanning:[/bold] {path.absolute()}")
    
    try:
        scan = scan_directory(path, recursive=recursive)
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
    path: Path = typer.Argument(None, help="Directory to sort (default: Downloads folder)"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview without moving"),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Scan subdirectories"),
):
    """Sort files into category folders."""
    if path is None:
        path = get_default_downloads()
    setup_logger()
    console.print(f"[bold]Sorting:[/bold] {path.absolute()}")
    
    try:
        scan = scan_directory(path, recursive=recursive)
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
    path: Path = typer.Argument(None, help="Directory to scan (default: Downloads folder)"),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Scan subdirectories"),
):
    """Find and remove duplicate files."""
    if path is None:
        path = get_default_downloads()
    setup_logger()
    console.print(f"[bold]Scanning for duplicates:[/bold] {path.absolute()}")
    
    try:
        scan = scan_directory(path, recursive=recursive)
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
    path: Path = typer.Argument(None, help="Directory to scan (default: Downloads folder)"),
    days: int = typer.Option(90, "--days", "-d", help="Files older than N days"),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Scan subdirectories"),
):
    """Show files older than N days."""
    if path is None:
        path = get_default_downloads()
    setup_logger()
    console.print(f"[bold]Scanning:[/bold] {path.absolute()}")
    
    try:
        scan = scan_directory(path, recursive=recursive)
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    
    old_files = find_old_files(scan.files, days)
    print_old_files(old_files, days)


@app.command()
def clean(
    path: Path = typer.Argument(None, help="Directory to clean (default: Downloads folder)"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Scan subdirectories"),
):
    """Remove trash files and empty folders."""
    if path is None:
        path = get_default_downloads()
    setup_logger()
    console.print(f"[bold]Cleaning:[/bold] {path.absolute()}")
    
    try:
        files_deleted, dirs_deleted = clean_trash(path, confirm=not yes, recursive=recursive)
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    
    console.print(f"\n[bold green]Done![/bold green] Files: {files_deleted}, Folders: {dirs_deleted}")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Launch TidyTrail in interactive mode (default)."""
    if ctx.invoked_subcommand is None:
        run_interactive()


if __name__ == "__main__":
    app()
