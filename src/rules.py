"""Custom rules for file categorization."""

import json
from pathlib import Path

from src.config import Category

RULES_FILE = Path.home() / ".tidytrail" / "rules.json"


def load_rules() -> dict[str, str]:
    """Load custom rules. Returns {extension: category}."""
    RULES_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not RULES_FILE.exists():
        return {}
    try:
        with open(RULES_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_rules(rules: dict[str, str]):
    """Save custom rules."""
    RULES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RULES_FILE, "w") as f:
        json.dump(rules, f, indent=2)


def add_rule(extension: str, category: str) -> bool:
    """Add a custom rule. Returns True if successful."""
    try:
        cat = Category(category)
    except ValueError:
        return False
    rules = load_rules()
    rules[extension.lower()] = category
    save_rules(rules)
    return True


def remove_rule(extension: str) -> bool:
    """Remove a custom rule. Returns True if existed."""
    rules = load_rules()
    ext = extension.lower()
    if ext in rules:
        del rules[ext]
        save_rules(rules)
        return True
    return False


def get_custom_category(extension: str) -> Category | None:
    """Get category for extension from custom rules."""
    rules = load_rules()
    cat = rules.get(extension.lower())
    if cat:
        try:
            return Category(cat)
        except ValueError:
            pass
    return None


def list_rules() -> dict[str, str]:
    """List all custom rules."""
    return load_rules()
