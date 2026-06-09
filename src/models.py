"""Data models for TidyTrail."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from src.config import Category


@dataclass
class FileInfo:
    path: Path
    size: int
    mtime: float
    hash: Optional[str] = None

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def extension(self) -> str:
        return self.path.suffix.lower()


@dataclass
class ScanResult:
    files: list[FileInfo]
    categories: dict[Category, list[FileInfo]]

    @property
    def total_files(self) -> int:
        return len(self.files)

    @property
    def total_size(self) -> int:
        return sum(f.size for f in self.files)
