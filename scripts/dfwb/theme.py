"""Load design/tokens.json into typed objects shared by every DFWB renderer."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from svgkit import fonts

ROOT = Path(__file__).resolve().parents[2]
TOKENS = ROOT / "design" / "tokens.json"
FONT_DIR = ROOT / "design" / "fonts"


@dataclass(frozen=True)
class Theme:
    name: str
    bg: str
    surface: str
    hairline: str
    hairline_strong: str
    text: str
    muted: str
    verified: str


@dataclass(frozen=True)
class Fonts:
    sans: fonts.FontFace
    sans_medium: fonts.FontFace
    sans_bold: fonts.FontFace
    mono: fonts.FontFace
    mono_medium: fonts.FontFace


@dataclass(frozen=True)
class Tokens:
    themes: dict[str, Theme]
    fonts: Fonts
    desktop_px: float
    mobile_px: float
    min_text_px: float
    loop_s: float

    def min_scale(self, width: float) -> float:
        return min(1.0, self.mobile_px / width)


_ALIASES = {"sans": "s", "sans_medium": "t", "sans_bold": "b", "mono": "m", "mono_medium": "n"}


def _face(role: str, spec: dict[str, Any]) -> fonts.FontFace:
    return fonts.FontFace(
        alias=_ALIASES[role],
        path=FONT_DIR / str(spec["file"]),
        weight=int(spec["weight"]),
        axes=tuple(sorted((str(k), float(v)) for k, v in spec.get("axes", {}).items())),
    )


def load(path: Path = TOKENS) -> Tokens:
    data = json.loads(path.read_text(encoding="utf-8"))
    return Tokens(
        themes={name: Theme(name=name, **values) for name, values in data["themes"].items()},
        fonts=Fonts(**{role: _face(role, spec) for role, spec in data["type"].items()}),
        desktop_px=float(data["layout"]["desktop_content_px"]),
        mobile_px=float(data["layout"]["mobile_content_px"]),
        min_text_px=float(data["layout"]["min_text_px"]),
        loop_s=float(data["motion"]["loop_s"]),
    )
