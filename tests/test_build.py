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
    assert len(files) == 12
    problems = [p for f in files for p in validate.check_svg(f.name, f.read_text(encoding="utf-8"))]
    assert problems == []


def test_every_picture_has_both_variants() -> None:
    text = profile.README.read_text(encoding="utf-8")
    for rel in re.findall(r'(?:srcset|src)="(assets/[^"]+\.svg)"', text):
        assert (profile.PROFILE / rel).exists(), rel
        twin = rel.replace("-dark", "-light") if "-dark" in rel else rel.replace("-light", "-dark")
        assert (profile.PROFILE / twin).exists(), twin


def test_theme_queries_come_last_in_combined_media() -> None:
    """GitHub rewrites "(prefers-color-scheme: …)" to match its own theme setting. Leading with
    it turns the other theme's compact hero into "not all and (max-width: 600px)", which matches
    every wide screen, so the compact hero replaces the full-width one on desktop."""
    text = profile.README.read_text(encoding="utf-8")
    for media in re.findall(r'media="([^"]+)"', text):
        assert not re.match(r"\(prefers-color-scheme:[^)]*\)\s*and\b", media), media
