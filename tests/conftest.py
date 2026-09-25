"""Shared helpers. Regenerate goldens after a deliberate change with UPDATE_GOLDEN=1."""

from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "tests" / "golden"


def assert_golden(name: str, actual: str) -> None:
    path = GOLDEN / name
    if os.environ.get("UPDATE_GOLDEN") == "1":
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(actual, encoding="utf-8", newline="\n")
    assert path.exists(), f"missing golden {name}; run with UPDATE_GOLDEN=1"
    assert actual == path.read_text(encoding="utf-8"), f"{name} differs from its golden file"


class FakeWeb:
    """A tiny stand-in for the public APIs: URL -> body, anything unknown is a 404."""

    def __init__(self, pages: dict[str, object]) -> None:
        self.pages = pages
        self.seen: list[str] = []

    def __call__(self, url: str) -> bytes | None:
        self.seen.append(url)
        page = self.pages.get(url)
        if page is None:
            return None
        if isinstance(page, bytes):
            return page
        if isinstance(page, str):
            return page.encode("utf-8")
        return json.dumps(page).encode("utf-8")
