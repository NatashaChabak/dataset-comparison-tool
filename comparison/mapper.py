"""Field mapping helpers."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


IGNORE_FIELD = "(ignore)"
FIELD_TYPES = ["string", "integer", "float", "date", "boolean"]
MAPPINGS_DIR = Path("mappings")


def clean_mapping_name(name: str) -> str:
    """Return a filesystem-safe mapping name."""
    safe_name = re.sub(r"[^a-zA-Z0-9_-]+", "_", name.strip()).strip("_")
    return safe_name or "mapping"


def list_mapping_files() -> list[Path]:
    """Return saved mapping files."""
    if not MAPPINGS_DIR.exists():
        return []

    return sorted(MAPPINGS_DIR.glob("*.json"))


def load_mapping(path: Path) -> dict[str, Any]:
    """Load a JSON mapping file."""
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def restore_mapping_from_json(path: Path) -> dict[str, Any]:
    """Restore a saved mapping from a JSON file."""
    return load_mapping(path)


def save_mapping(mapping: dict[str, Any], name: str) -> Path:
    """Save a mapping as JSON and return its path."""
    MAPPINGS_DIR.mkdir(exist_ok=True)
    path = MAPPINGS_DIR / f"{clean_mapping_name(name)}.json"

    with path.open("w", encoding="utf-8") as file:
        json.dump(mapping, file, indent=4)

    return path


def get_field_config(mapping: dict[str, Any] | None, source: str) -> dict[str, Any]:
    """Return saved field config for a source field, if present."""
    if not mapping:
        return {}

    fields = mapping.get("fields", [])
    for field in fields:
        if field.get("source") == source:
            return field

    return {}
