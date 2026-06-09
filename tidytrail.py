"""TidyTrail - Download folder cleaner.

Usage:
    tidytrail <command> [OPTIONS] [PATH]

Commands:
    preview    Show sorting plan
    sort       Sort files into categories
    dupes      Find and remove duplicates
    old        Show files older than N days
    clean      Remove trash and empty folders
"""

from src.cli import app

if __name__ == "__main__":
    app()
