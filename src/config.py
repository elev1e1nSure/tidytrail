"""Configuration for file categories and extensions."""

from enum import Enum


class Category(str, Enum):
    IMAGES = "images"
    DOCS = "docs"
    ARCHIVES = "archives"
    VIDEO = "video"
    CODE = "code"
    AUDIO = "audio"
    EXECUTABLES = "executables"
    OTHER = "other"


EXTENSIONS: dict[Category, frozenset[str]] = {
    Category.IMAGES: frozenset({
        ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".ico", ".heic", ".jfif"
    }),
    Category.DOCS: frozenset({
        ".pdf", ".doc", ".docx", ".txt", ".xls", ".xlsx", ".ppt", ".pptx", ".odt", ".rtf", ".csv"
    }),
    Category.ARCHIVES: frozenset({
        ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso"
    }),
    Category.VIDEO: frozenset({
        ".mp4", ".mkv", ".avi", ".mov", ".wmv", ".webm", ".flv", ".m4v"
    }),
    Category.CODE: frozenset({
        ".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".java", ".cpp", ".c", ".h",
        ".go", ".rs", ".rb", ".php", ".swift", ".kt", ".scala", ".sh", ".bat", ".ps1"
    }),
    Category.AUDIO: frozenset({
        ".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac", ".wma", ".opus"
    }),
    Category.EXECUTABLES: frozenset({
        ".exe", ".msi", ".dmg", ".deb", ".rpm", ".app", ".pkg", ".snap", ".flatpak"
    }),
}

TRASH_EXTENSIONS: set[str] = {
    ".tmp", ".temp", ".part", ".crdownload", ".download", ".partial", "~"
}

LOG_FILE = "tidytrail.log"
