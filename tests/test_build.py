"""The committed profile must equal a fresh build, stay deterministic and pass hygiene."""

from __future__ import annotations

import re

from dfwb import profile, validate


def test_committed_profile_matches_a_fresh_build() -> None:
    built, _ = profile.build_all()
    assert profile.stale(built) == []


def test_build_is_deterministic() -> None:
    assert profile.build_all()[0] == profile.build_all()[0]


def test_every_string_is_legible() -> None:
    _, ledger = profile.build_all()
    assert ledger.entries
    assert ledger.failures(profile.TOKENS.min_text_px) == []


def test_every_svg_passes_hygiene_checks() -> None:
    files = sorted(profile.ASSETS.glob("*.svg"))
    assert len(files) == 10
    problems = [p for f in files for p in validate.check_svg(f.name, f.read_text(encoding="utf-8"))]
    assert problems == []


def test_every_repo_hero_passes_hygiene_checks() -> None:
    files = sorted(profile.REPOS.glob("*/*.svg"))
    assert len(files) == 6  # one light and one dark hero for each of the three packages
    problems = [
        p
        for f in files
        for p in validate.check_svg(
            str(f.relative_to(profile.REPOS)), f.read_text(encoding="utf-8")
        )
    ]
    assert problems == []


def test_every_picture_has_both_variants() -> None:
    text = profile.README.read_text(encoding="utf-8")
    for rel in re.findall(r'(?:srcset|src)="(assets/[^"]+\.svg)"', text):
        assert (profile.PROFILE / rel).exists(), rel
        twin = rel.replace("-dark", "-light") if "-dark" in rel else rel.replace("-light", "-dark")
        assert (profile.PROFILE / twin).exists(), twin


def test_pictures_switch_on_the_theme_alone() -> None:
    """GitHub replaces the whole media query of a source that mentions prefers-color-scheme with
    its own theme's answer, so a query that also tests width is ignored: a phone-width hero showed
    on desktop too. Every source must test the dark theme and nothing else."""
    text = profile.README.read_text(encoding="utf-8")
    medias = re.findall(r'<source media="([^"]+)"', text)
    assert medias
    assert set(medias) == {"(prefers-color-scheme: dark)"}
