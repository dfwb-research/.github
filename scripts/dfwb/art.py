"""DFWB images, "Verified mono": monochrome, with one green used only for verified states.

The hero is a four-stage pipeline (datasets, protocols, training, evaluation). Each stage ticks
green in turn and the chain between them lights up behind it; then everything rests verified.
The resting frame is the fully verified one, so reduced motion shows it directly.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass

from svgkit import fonts
from svgkit.canvas import Canvas
from svgkit.color import Ledger
from svgkit.svg import document, el, fmt

from . import data
from .theme import Theme, Tokens

TITLE = "DFWB Research"
TAGLINE = "Open, reproducible tooling for deepfake detection research."
STAGES = (
    ("datasets", ("sha256-verified", "inventories")),
    ("protocols", ("versioned", "splits")),
    ("training", ("seed-locked", "runs")),
    ("evaluation", ("AUC ± CI", "with coverage")),
)
HERO_DESC = (
    "DFWB Research: open, reproducible tooling for deepfake detection research. A four-stage "
    "pipeline, each stage ticking green in turn: datasets (sha256-verified inventories), "
    "protocols (versioned splits), training (seed-locked runs) and evaluation (AUC with "
    "confidence intervals and coverage)."
)


def _panel(width: float, height: float, theme: Theme, fill: str | None = None) -> str:
    return el("rect", {"width": width, "height": height, "rx": 12, "fill": fill or theme.bg}) + el(
        "rect",
        {
            "x": 0.5,
            "y": 0.5,
            "width": width - 1,
            "height": height - 1,
            "rx": 11.5,
            "fill": "none",
            "stroke": theme.hairline_strong,
        },
    )


def check(cx: float, cy: float, size: float, colour: str, width: float = 1.8) -> str:
    s = size / 2
    return el(
        "path",
        {
            "d": f"M{fmt(cx - s * 0.62)} {fmt(cy + s * 0.02)}"
            f"L{fmt(cx - s * 0.16)} {fmt(cy + s * 0.46)}"
            f"L{fmt(cx + s * 0.66)} {fmt(cy - s * 0.44)}",
            "fill": "none",
            "stroke": colour,
            "stroke-width": fmt(width),
            "stroke-linecap": "round",
            "stroke-linejoin": "round",
        },
    )


def _timeline_css(loop: float) -> str:
    """Stage k ticks at 0.8 + k s; the link to the next stage lights 0.45 s later."""
    rules: list[str] = []
    end_hold, end_fade = 92, 96
    for k in range(len(STAGES)):
        tick = (0.8 + k) / loop * 100
        link = (1.25 + k) / loop * 100
        for name, at in ((f"k{k}", tick), (f"l{k}", link)):
            rules.append(
                f"@keyframes {name}{{0%,{fmt(at - 0.01, 2)}%{{opacity:0}}{fmt(at + 2.5, 2)}%,"
                f"{end_hold}%{{opacity:1}}{end_fade}%,100%{{opacity:0}}}}"
                f".{name}{{animation:{name} {fmt(loop)}s ease-out infinite}}"
            )
    rules.append("@media (prefers-reduced-motion:reduce){*{animation:none!important}}")
    return "".join(rules)


@dataclass(frozen=True)
class HeroLayout:
    width: float
    height: float
    pad: float
    title_size: float
    title_y: float
    tagline_size: float
    tagline_y: float


# One wide hero for every screen. GitHub replaces the whole media query of any <picture> source
# that mentions prefers-color-scheme, so a phone-width variant would also show on desktop.
HERO_WIDE = HeroLayout(880, 320, 40, 44, 108, 19, 144)


def hero(tokens: Tokens, theme: Theme, layout: HeroLayout, ledger: Ledger, asset: str) -> str:
    f = tokens.fonts
    scale = min(1.0, tokens.desktop_px / layout.width)
    c = Canvas(asset, layout.width, layout.height, ledger=ledger, bg=theme.bg, min_scale=scale)
    c.style("e", f.mono, 13, theme.muted)
    c.style("h", f.sans_bold, layout.title_size, theme.text)
    c.style("g", f.sans, layout.tagline_size, theme.muted)
    c.style("s", f.sans_medium, 17, theme.text)
    c.style("u", f.mono, 13, theme.muted)
    w, pad = layout.width, layout.pad
    parts = [_panel(w, layout.height, theme)]
    parts.append(c.text("github.com/dfwb-research", pad, pad + 4, "e"))
    parts.append(c.text(TITLE, pad, layout.title_y, "h"))
    parts.append(c.text(TAGLINE, pad, layout.tagline_y, "g"))

    spacing = (w - 2 * pad - 160) / (len(STAGES) - 1)
    nodes = [(pad + 80 + i * spacing, 212) for i in range(len(STAGES))]
    r = 10
    # The chain: neutral links, and green overlays that light as each stage verifies.
    for k in range(len(STAGES) - 1):
        (x0, y0), (x1, _) = nodes[k], nodes[k + 1]
        seg = f"M{fmt(x0 + r + 6)} {fmt(y0)}H{fmt(x1 - r - 6)}"
        parts.append(el("path", {"d": seg, "stroke": theme.hairline_strong, "stroke-width": "1"}))
        parts.append(
            el(
                "path",
                {"d": seg, "stroke": theme.verified, "stroke-width": "1.5", "class": f"l{k}"},
            )
        )
    for k, ((name, sub), (x, y)) in enumerate(zip(STAGES, nodes, strict=True)):
        parts.append(
            el(
                "circle",
                {
                    "cx": x,
                    "cy": y,
                    "r": r,
                    "fill": theme.bg,
                    "stroke": theme.hairline_strong,
                    "stroke-width": "1.5",
                },
            )
        )
        parts.append(
            el(
                "g",
                {"class": f"k{k}"},
                el(
                    "circle",
                    {
                        "cx": x,
                        "cy": y,
                        "r": r,
                        "fill": theme.bg,
                        "stroke": theme.verified,
                        "stroke-width": "1.5",
                    },
                )
                + check(x, y, 11, theme.verified),
            )
        )
        parts.append(c.text(name, x, y + 44, "s", anchor="middle"))
        parts.append(c.text(sub[0], x, y + 68, "u", anchor="middle"))
        parts.append(c.text(sub[1], x, y + 86, "u", anchor="middle"))
    return c.render(
        title=f"{TITLE}. {TAGLINE}",
        desc=HERO_DESC,
        body="".join(parts),
        extra_css=_timeline_css(tokens.loop_s),
    )


CARD_W, CARD_H = 264, 272


def package_card(
    tokens: Tokens, theme: Theme, package: data.Package, live: data.Live, ledger: Ledger, asset: str
) -> str:
    f = tokens.fonts
    c = Canvas(
        asset, CARD_W, CARD_H, ledger=ledger, bg=theme.bg, min_scale=tokens.min_scale(CARD_W)
    )
    c.style("n", f.mono_medium, 17, theme.text)
    c.style("d", f.sans, 15, theme.muted)
    c.style("k", f.mono, 13, theme.muted)
    c.style("v", f.mono, 13, theme.text)
    parts = [_panel(CARD_W, CARD_H, theme), c.text(package.repo, 24, 48, "n")]
    for i, line in enumerate(c.wrap(package.summary, "d", CARD_W - 48)):
        parts.append(c.text(line, 24, 84 + i * 22, "d"))
    parts.append(el("path", {"d": f"M24 {CARD_H - 56.5}H{CARD_W - 24}", "stroke": theme.hairline}))
    if live.released and live.version:
        facts = [f"v{live.version.removeprefix('v')}"]
        if live.licence:
            facts.append(live.licence)
        parts.append(check(31, CARD_H - 28, 12, theme.verified))
        parts.append(c.text(" · ".join(facts), 46, CARD_H - 23, "v"))
        if live.ci:
            ci_x = 46 + c.measure(" · ".join(facts), "v") + 12
            parts.append(c.text(f"CI {live.ci}", ci_x, CARD_H - 23, "k"))
        status = f"Released: {' · '.join(facts)}" + (f", CI {live.ci}" if live.ci else "")
    else:
        parts.append(
            el(
                "circle",
                {
                    "cx": 30,
                    "cy": CARD_H - 28,
                    "r": 5,
                    "fill": "none",
                    "stroke": theme.muted,
                    "stroke-width": "1.2",
                },
            )
        )
        parts.append(c.text("v0.1 in preparation", 44, CARD_H - 23, "k"))
        status = "v0.1 in preparation"
    desc = f"{package.repo}: {package.summary} {status}."
    return c.render(title=package.repo, desc=desc, body="".join(parts))


def _avatar_image(user_id: int, x: float, y: float, size: float, clip: str) -> str:
    found = data.avatar(user_id)
    if not found:
        return el(
            "circle", {"cx": x + size / 2, "cy": y + size / 2, "r": size / 2, "fill": "#808080"}
        )
    mime, raw = found
    href = f"data:{mime};base64,{base64.b64encode(raw).decode('ascii')}"
    return el(
        "defs",
        None,
        el(
            "clipPath",
            {"id": clip},
            el("circle", {"cx": x + size / 2, "cy": y + size / 2, "r": size / 2}),
        ),
    ) + el(
        "image",
        {
            "href": href,
            "x": x,
            "y": y,
            "width": size,
            "height": size,
            "clip-path": f"url(#{clip})",
            "preserveAspectRatio": "xMidYMid slice",
        },
    )


MAINTAINER_W, MAINTAINER_H = 400, 112


def maintainer_card(tokens: Tokens, theme: Theme, ledger: Ledger, asset: str) -> str:
    f = tokens.fonts
    c = Canvas(
        asset,
        MAINTAINER_W,
        MAINTAINER_H,
        ledger=ledger,
        bg=theme.bg,
        min_scale=tokens.min_scale(MAINTAINER_W),
    )
    c.style("n", f.sans_bold, 18, theme.text)
    c.style("r", f.sans, 16, theme.muted)
    c.style("o", f.mono, 15, theme.muted)
    parts = [
        _panel(MAINTAINER_W, MAINTAINER_H, theme),
        _avatar_image(data.MAINTAINER_ID, 24, 24, 64, "av"),
        el(
            "circle", {"cx": 56, "cy": 56, "r": 32, "fill": "none", "stroke": theme.hairline_strong}
        ),
        c.text("Luke Collins", 108, 46, "n"),
        c.text("Lead maintainer · Deakin University", 108, 70, "r"),
        c.text("ORCID 0009-0002-7771-1081", 108, 93, "o"),
    ]
    return c.render(
        title="Luke Collins, lead maintainer",
        desc=(
            "Luke Collins, lead maintainer of DFWB Research, Deakin University. "
            "ORCID 0009-0002-7771-1081."
        ),
        body="".join(parts),
    )


def contributor_wall(
    tokens: Tokens, theme: Theme, people: tuple[data.Contributor, ...], ledger: Ledger, asset: str
) -> str:
    size, gap, per_row = 40, 8, 8
    rows = max(1, -(-len(people) // per_row))
    w = 24 * 2 + per_row * size + (per_row - 1) * gap
    h = 24 * 2 + rows * size + (rows - 1) * gap
    c = Canvas(asset, w, h, ledger=ledger, bg=theme.bg, min_scale=tokens.min_scale(w))
    parts = [_panel(w, h, theme)]
    for i, person in enumerate(people):
        x = 24 + (i % per_row) * (size + gap)
        y = 24 + (i // per_row) * (size + gap)
        parts.append(_avatar_image(person.id, x, y, size, f"a{i}"))
    names = ", ".join(p.login for p in people)
    return c.render(title="Contributors", desc=f"Contributors: {names}.", body="".join(parts))


AVATAR_PX = 500
AVATAR_DESC = (
    "The DFWB Research mark: the letters df above wb in IBM Plex Mono, light on near-black."
)


def avatar(tokens: Tokens) -> str:
    """The organisation avatar: "df" over "wb" in Plex Mono Medium, on the dark background.

    Two letters a line stay legible at GitHub's 20 px list size. The letters are outlines, not
    text, so any SVG-to-PNG converter draws them the same (GitHub takes avatars as PNG).
    """
    theme = tokens.themes["dark"]
    face = tokens.fonts.mono_medium
    size, tracking, leading = 210.0, -0.04, 172.0
    x = (AVATAR_PX - fonts.measure(face, "df", size, tracking)) / 2
    _, (_, ink_top, _, _) = fonts.outline(face, "df", size, x, 0.0, tracking)
    _, (_, _, _, ink_bottom) = fonts.outline(face, "wb", size, x, leading, tracking)
    baseline = (AVATAR_PX - (ink_bottom - ink_top)) / 2 - ink_top
    top, _ = fonts.outline(face, "df", size, x, baseline, tracking)
    bottom, _ = fonts.outline(face, "wb", size, x, baseline + leading, tracking)
    body = el("rect", {"width": AVATAR_PX, "height": AVATAR_PX, "fill": theme.bg}) + el(
        "path", {"d": f"{top} {bottom}", "fill": theme.text}
    )
    return document(
        width=AVATAR_PX, height=AVATAR_PX, title=TITLE, desc=AVATAR_DESC, css="", body=body
    )
