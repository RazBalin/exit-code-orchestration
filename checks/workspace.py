"""workspace.py: shared helpers for the checks (standard library only)."""
from __future__ import annotations

import json
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[1]


def config(repo: pathlib.Path = REPO) -> dict:
    return json.loads((repo / "config" / "workspace.json").read_text(encoding="utf-8"))


def models(repo: pathlib.Path = REPO) -> dict:
    return json.loads((repo / "config" / "models.json").read_text(encoding="utf-8"))


def front_matter(text: str) -> tuple[dict, str]:
    """Parse a flat front matter block: 'key: value' lines between two '---' lines.

    A value in square brackets is a comma-separated list. Returns (fields, body).
    Raises ValueError when the block is missing or a line is not 'key: value'.
    """
    if not text.startswith("---\n"):
        raise ValueError("no front matter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("front matter not closed")
    fields: dict = {}
    for n, line in enumerate(text[4:end].split("\n"), 2):
        if not line.strip():
            continue
        if ":" not in line:
            raise ValueError("line %d is not 'key: value'" % n)
        key, value = line.split(":", 1)
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            value = [v.strip() for v in value[1:-1].split(",") if v.strip()]
        elif len(value) >= 2 and value[0] == value[-1] == '"':
            value = value[1:-1]
        fields[key.strip()] = value
    return fields, text[end + 5:]
