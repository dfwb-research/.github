"""Live facts from the public APIs, exercised against a fake web."""

from __future__ import annotations

import datetime as dt

from conftest import FakeWeb
from dfwb import data, sources

API = sources.API
ORG = sources.ORG
RUNS = f"{API}/repos/{ORG}/deepfake-workbench/actions/runs?branch=main&status=completed&per_page=1"
WORKBENCH = data.Package("deepfake-workbench", "Deepfake Workbench", "x")
CFF = """cff-version: 1.2.0
title: Deepfake Workbench
version: 0.1.0
date-released: 2026-10-20
repository-code: https://github.com/dfwb-research/deepfake-workbench
authors:
  - given-names: Luke
    family-names: Collins
"""


def released_web() -> FakeWeb:
    return FakeWeb(
        {
            f"{API}/repos/{ORG}/deepfake-workbench": {
                "private": False,
                "default_branch": "main",
                "license": {"spdx_id": "MIT"},
            },
            f"{API}/repos/{ORG}/deepfake-workbench/releases/latest": {"tag_name": "v0.1.0"},
            RUNS: {"workflow_runs": [{"conclusion": "success"}]},
            f"https://raw.githubusercontent.com/{ORG}/deepfake-workbench/main/CITATION.cff": CFF,
        }
    )


def test_a_missing_or_private_repository_stays_in_preparation() -> None:
    live, citation = sources.package_state(FakeWeb({}), WORKBENCH)
    assert live == data.Live() and not live.released and citation is None
    private = FakeWeb({f"{API}/repos/{ORG}/deepfake-workbench": {"private": True}})
    assert sources.package_state(private, WORKBENCH)[0] == data.Live()


def test_a_released_repository_goes_live_with_its_citation() -> None:
    live, citation = sources.package_state(released_web(), WORKBENCH)
    assert live == data.Live(public=True, version="0.1.0", licence="MIT", ci="passing")
    assert citation == data.Citation(
        title="Deepfake Workbench",
        authors=("Luke Collins",),
        year="2026",
        version="0.1.0",
        url="https://github.com/dfwb-research/deepfake-workbench",
    )


def test_pypi_wins_for_version_and_licence_once_named() -> None:
    web = released_web()
    web.pages["https://pypi.org/pypi/deepfake-workbench/json"] = {
        "info": {"version": "0.1.1", "license_expression": "MIT"}
    }
    package = data.Package(
        "deepfake-workbench", "Deepfake Workbench", "x", pypi="deepfake-workbench"
    )
    live, _ = sources.package_state(web, package)
    assert live.version == "0.1.1"
    # Without a configured PyPI name, PyPI is never asked: the name could belong to anyone.
    sources.package_state(released_web(), WORKBENCH)
    assert not any("pypi.org" in url for url in released_web().seen)


def test_public_repo_without_a_release_is_not_released() -> None:
    web = released_web()
    del web.pages[f"{API}/repos/{ORG}/deepfake-workbench/releases/latest"]
    live, _ = sources.package_state(web, WORKBENCH)
    assert live.public and not live.released


def test_contributors_are_people_across_public_repos() -> None:
    web = FakeWeb(
        {
            f"{API}/orgs/{ORG}/repos?type=public&per_page=100": [
                {"name": ".github", "private": False, "fork": False},
                {"name": "deepfake-workbench", "private": False, "fork": False},
                {"name": "some-fork", "private": False, "fork": True},
            ],
            f"{API}/repos/{ORG}/.github/contributors?per_page=100": [
                {"login": "lukegcollins", "id": 82789246, "type": "User"},
                {"login": "dependabot[bot]", "id": 49699333, "type": "Bot"},
            ],
            f"{API}/repos/{ORG}/deepfake-workbench/contributors?per_page=100": [
                {"login": "Zed", "id": 7, "type": "User"},
                {"login": "lukegcollins", "id": 82789246, "type": "User"},
                {"login": "github-actions[bot]", "id": 41898282, "type": "User"},
            ],
        }
    )
    people = sources.contributors(web)
    assert [p.login for p in people] == ["lukegcollins", "Zed"]
    assert not any("some-fork" in url for url in web.seen)


def test_avatars_are_sniffed_by_content() -> None:
    web = FakeWeb(
        {
            "https://avatars.githubusercontent.com/u/1?s=96&v=4": b"\x89PNG\r\n\x1a\nrest",
            "https://avatars.githubusercontent.com/u/2?s=96&v=4": b"\xff\xd8\xffrest",
            "https://avatars.githubusercontent.com/u/3?s=96&v=4": b"<html>",
        }
    )
    assert sources.fetch_avatar(web, 1) == (".png", b"\x89PNG\r\n\x1a\nrest")
    assert sources.fetch_avatar(web, 2) == (".jpg", b"\xff\xd8\xffrest")
    assert sources.fetch_avatar(web, 3) is None


def test_the_status_date_moves_at_most_every_28_days() -> None:
    assert sources.next_stamp("2026-09-25", dt.date(2026, 10, 22)) == "2026-09-25"
    assert sources.next_stamp("2026-09-25", dt.date(2026, 10, 23)) == "2026-10-23"
