"""Golden files for every renderer and README block, from fixed fixture data."""

from __future__ import annotations

import base64
import re
import xml.etree.ElementTree as ET

import pytest
from conftest import assert_golden
from dfwb import art, data, profile, validate
from dfwb.theme import Theme
from svgkit.color import Ledger

TOKENS = profile.TOKENS
RELEASED = data.Live(public=True, version="0.1.0", licence="MIT", ci="passing")
CITATION = data.Citation(
    title="Deepfake Workbench",
    authors=("Luke Collins",),
    year="2026",
    version="0.1.0",
    url="https://github.com/dfwb-research/deepfake-workbench",
)
FRIEND = data.Contributor(login="example-contributor", id=1)
MAINTAINER = data.Contributor(login=data.MAINTAINER_LOGIN, id=data.MAINTAINER_ID)
# The goldens use this 1x1 PNG for every avatar, so they never depend on the avatars the weekly
# refresh caches (a new profile picture would otherwise fail CI on the refresh's own PR).
FIXED_AVATAR = (
    "image/png",
    base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    ),
)


def committed(name: str) -> str:
    return (profile.ASSETS / name).read_text(encoding="utf-8")


def committed_repo(repo: str, name: str) -> str:
    return (profile.REPOS / repo / f"hero-{name}.svg").read_text(encoding="utf-8")


def test_hero_and_cards_match_the_committed_images() -> None:
    for name, theme in TOKENS.themes.items():
        assert art.hero(TOKENS, theme, art.HERO_WIDE, Ledger(), "h") == committed(
            f"hero-{name}.svg"
        )
        packages = data.packages()
        for package, gap in zip(packages, profile.card_gaps(len(packages)), strict=True):
            card = art.package_card(TOKENS, theme, package, data.Live(), Ledger(), "c", gap=gap)
            assert card == committed(f"{package.repo}-{name}.svg")
        assert art.maintainer_card(TOKENS, theme, Ledger(), "m") == committed(
            f"maintainer-{name}.svg"
        )


def test_repo_heroes_match_the_committed_images() -> None:
    for name, theme in TOKENS.themes.items():
        for package in data.packages():
            hero = art.repo_hero(TOKENS, theme, art.HERO_WIDE, Ledger(), "h", package.repo)
            assert hero == committed_repo(package.repo, name)


def test_released_card_and_contributor_wall(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(data, "avatar", lambda user_id: FIXED_AVATAR)
    package = data.packages()[0]
    for name, theme in sorted(TOKENS.themes.items()):
        ledger = Ledger()
        card = art.package_card(TOKENS, theme, package, RELEASED, ledger, "c")
        assert_golden(f"card-released-{name}.svg", card)
        wall = art.contributor_wall(TOKENS, theme, (FRIEND, MAINTAINER), ledger, "w")
        assert_golden(f"contributors-{name}.svg", wall)
        assert ledger.failures(TOKENS.min_text_px) == []


def test_readme_blocks() -> None:
    before = data.State(status_verified="2026-09-25", contributors=(MAINTAINER,))
    after = data.State(
        status_verified="2026-10-23",
        live={"deepfake-workbench": RELEASED},
        citations={"deepfake-workbench": CITATION},
        contributors=(FRIEND, MAINTAINER),
    )
    assert_golden("packages-before.md", profile.packages_block(before) + "\n")
    assert_golden("packages-after.md", profile.packages_block(after) + "\n")
    assert_golden("cite-after.md", profile.cite_block(after) + "\n")
    assert_golden("people-before.md", profile.people_block(before) + "\n")
    assert_golden("people-after.md", profile.people_block(after) + "\n")
    assert profile.status_block(after).endswith("<samp>status verified 2026-10-23</samp></p>")
    assert "github.com/dfwb-research/dfwb-torch" not in profile.packages_block(after)


def test_tables(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(data, "datasets", lambda: [])
    monkeypatch.setattr(data, "detectors", lambda: [])
    assert profile.tables_block() == "The dataset and detector tables are populating with v0.1."
    example = data.Dataset(
        name="Example-DF",
        modality="audio-visual",
        protocol_version="1.0",
        terms="https://example.org/terms",
        status="released",
        real=1200,
        fake=34_567,
        methods=("face_swap", "Lip-sync"),
        default_protocol="official",
        rights_cleared=True,
        repository="https://example.org/df",
        year=2021,
        subjects=42,
        variants=("raw", "c23"),
        variants_of="fakes",
    )
    wide = data.Dataset(
        name="Wide-DF",
        modality="video",
        protocol_version="1.0",
        terms="https://example.org/wide-terms",
        status="in preparation",
        real=1,
        fake=6,
        methods=tuple(f"m{n}" for n in range(6)),
        default_protocol="all-test",
        rights_cleared=False,
    )
    monkeypatch.setattr(data, "datasets", lambda: [example, wide])
    monkeypatch.setattr(
        data,
        "detectors",
        lambda: [data.Detector("ExampleNet", "https://doi.org/10.0000/x", "planned", "MIT")],
    )
    block = profile.tables_block()
    assert_golden("tables.md", block + "\n")
    assert "Of the 2 datasets, 1 is released and 1 is in preparation." in block
    assert (
        "| [Example-DF](https://example.org/df) | 2021 | audio-visual | 1,200 | 34,567 | 35,767 "
        "| 42 | 2: face\\_swap, Lip-sync | raw, c23 (fakes only) | `official` | Yes |"
    ) in block
    assert (
        "| Wide-DF | — | video | 1 | 6 | 7 | — | 6, listed below | — | `all-test` | No |" in block
    )
    assert "- **Wide-DF** (6): m0, m1, m2, m3, m4, m5" in block
    assert "lists in dfwb-protocols 1.0;" in block


def test_tables_match_the_protocol_pack_notes() -> None:
    """The profile's notes are word for word those dfwb-protocols writes under its own table."""
    notes = profile.dataset_notes(["0.1.0"])
    assert notes[0].startswith("- Real, Fake and Total count the videos each protocol lists in ")
    assert "dfwb-protocols 0.1.0; a video at several compressions counts once." in notes[0]
    assert notes[-1] == (
        "- Rights cleared: No means DFWB does not yet publish these lists. Each dataset comes "
        "from its owner, under the owner's terms."
    )


def test_ieee_reference_and_bibtex() -> None:
    assert profile.ieee(CITATION) == (
        'L. Collins, "Deepfake Workbench," version 0.1.0, 2026. [Online]. '
        "Available: https://github.com/dfwb-research/deepfake-workbench"
    )
    two = data.Citation(
        title="T",
        authors=("Ada Lovelace", "Alan Mathison Turing"),
        year="2026",
        doi="10.5281/zenodo.1",
    )
    assert profile.ieee(two) == 'A. Lovelace and A. M. Turing, "T," 2026. doi: 10.5281/zenodo.1.'
    assert profile.bibtex("x", two).startswith("@software{x,\n  author = {Ada Lovelace and Alan")


def _assert_green_only_marks_verified_overlays(svg: str, theme: Theme) -> None:
    root = ET.fromstring(svg)
    parents = {child: parent for parent in root.iter() for child in parent}
    for element in root.iter():
        if theme.verified in (element.get("stroke"), element.get("fill")):
            node: ET.Element | None = element
            while node is not None and not re.fullmatch(r"[kl]\d", node.get("class", "")):
                node = parents.get(node)
            assert node is not None, "green outside a verified-state overlay"


def test_green_marks_only_verified_states() -> None:
    """The verified colour may appear only on the stage checks, the chain, and release checks."""
    for theme in TOKENS.themes.values():
        hero = art.hero(TOKENS, theme, art.HERO_WIDE, Ledger(), "h")
        _assert_green_only_marks_verified_overlays(hero, theme)
        for package in data.packages():
            repo_hero = art.repo_hero(TOKENS, theme, art.HERO_WIDE, Ledger(), "h", package.repo)
            _assert_green_only_marks_verified_overlays(repo_hero, theme)
        pending = art.package_card(TOKENS, theme, data.packages()[0], data.Live(), Ledger(), "c")
        assert theme.verified not in pending
        released = art.package_card(TOKENS, theme, data.packages()[0], RELEASED, Ledger(), "c")
        assert theme.verified in released


def test_the_resting_frame_is_fully_verified() -> None:
    css = art._timeline_css(12)
    outside_keyframes = re.sub(r"@keyframes\s+\w+\{(?:[^{}]*\{[^{}]*\})*\}", "", css)
    assert "opacity:0" not in outside_keyframes
    assert "prefers-reduced-motion:reduce" in css


def test_avatar_is_an_outlined_monochrome_square() -> None:
    svg = art.avatar(TOKENS)
    assert svg == profile.AVATAR.read_text(encoding="utf-8")
    assert validate.check_svg("avatar.svg", svg) == []
    assert 'viewBox="0 0 500 500"' in svg
    assert "<text" not in svg and "@font-face" not in svg  # outlines draw the same everywhere
    dark = TOKENS.themes["dark"]
    assert set(re.findall(r'fill="(#[0-9A-Fa-f]{6})"', svg)) == {dark.bg, dark.text}


def test_the_hero_is_exactly_as_wide_as_the_card_row() -> None:
    gaps = profile.card_gaps(len(data.packages()))
    row = sum(art.CARD_W + gap for gap in gaps)
    assert art.HERO_WIDE.width == row
    assert gaps[-1] == 0 and profile.card_gaps(0) == []
    block = profile.packages_block(data.State(status_verified="2026-09-25"))
    assert "</picture><picture>" in block  # no font-dependent space between the cards
