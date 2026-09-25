"""Repository invariants that the review checklist would otherwise have to remember."""

from __future__ import annotations

import json
import re
import tomllib

from conftest import ROOT


def inline_dependencies(script: str) -> list[str]:
    text = (ROOT / "scripts" / script).read_text(encoding="utf-8")
    block = re.search(r"^# /// script\n(.*?)^# ///$", text, flags=re.MULTILINE | re.DOTALL)
    assert block, script
    lines = block.group(1).splitlines()
    body = "\n".join(line.removeprefix("# ").removeprefix("#") for line in lines)
    return sorted(tomllib.loads(body)["dependencies"])


def test_pep723_blocks_match_pyproject() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    pinned = sorted(project["project"]["dependencies"])
    for script in ("build_profile.py", "refresh_profile.py"):
        assert inline_dependencies(script) == pinned, script


def test_tokens_keep_one_colour() -> None:
    tokens = json.loads((ROOT / "design" / "tokens.json").read_text(encoding="utf-8"))
    for theme in tokens["themes"].values():
        colours = {
            k
            for k, v in theme.items()
            if v.startswith("#") and k not in {"bg", "surface", "text", "muted"}
        }
        assert colours == {"verified"}


def test_fonts_ship_with_their_licences() -> None:
    for font in sorted((ROOT / "design" / "fonts").glob("*.ttf")):
        assert (font.parent / f"OFL-{font.stem.split('-')[0]}.txt").exists(), font.name


def test_code_of_conduct_stays_on_contributor_covenant_2_1() -> None:
    text = (ROOT / "CODE_OF_CONDUCT.md").read_text(encoding="utf-8")
    assert "Contributor Covenant][homepage], version 2.1" in text


def test_discussion_forms_use_the_default_category_slugs() -> None:
    forms = {p.stem for p in (ROOT / ".github" / "DISCUSSION_TEMPLATE").glob("*.yml")}
    assert forms == {"q-a", "ideas", "show-and-tell"}


def test_every_workflow_template_has_properties() -> None:
    folder = ROOT / "workflow-templates"
    workflows = {p.name.removesuffix(".yml") for p in folder.glob("*.yml")}
    properties = {p.name.removesuffix(".properties.json") for p in folder.glob("*.properties.json")}
    assert workflows == properties == {"dfwb-python-ci", "dfwb-release"}
    for name in workflows:
        text = (folder / f"{name}.yml").read_text(encoding="utf-8")
        for use in re.findall(r"uses:\s*(\S+)", text):
            if use.startswith("dfwb-research/.github/"):
                assert use.endswith("@v1"), use
            else:
                assert re.search(r"@[0-9a-f]{40}$", use), f"{use} is not pinned to a commit"


def test_the_refresh_proposes_changes_through_a_pull_request() -> None:
    """main takes changes only through pull requests, so the refresh must never push to it."""
    workflows = ROOT / ".github" / "workflows"
    refresh = (workflows / "refresh.yml").read_text(encoding="utf-8")
    code = re.sub(r"(^|\s)#.*$", "", refresh, flags=re.MULTILINE)
    assert not re.search(r"HEAD:(refs/heads/)?main\b|\bpush\s[^\n]*\bmain\b", code)
    assert "gh pr create" in code and "gh workflow run ci.yml" in code
    ci = (workflows / "ci.yml").read_text(encoding="utf-8")
    assert re.search(r"^  workflow_dispatch:", ci, flags=re.MULTILINE), "the refresh starts CI"
