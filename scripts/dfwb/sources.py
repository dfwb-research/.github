"""Live facts for the profile, from public APIs only: GitHub REST, PyPI and raw CITATION.cff.

Everything here is public information about public repositories. A repository that is private
or missing reads as "not public yet", which keeps its card on "v0.1 in preparation".
"""

from __future__ import annotations

import datetime as dt
import json
import urllib.error
import urllib.request
from collections.abc import Callable
from typing import Any

import yaml

from . import data

API = "https://api.github.com"
ORG = "dfwb-research"
USER_AGENT = "dfwb-research-profile/1.0 (+https://github.com/dfwb-research/.github)"
STATUS_EVERY = dt.timedelta(days=28)

Get = Callable[[str], bytes | None]  # URL -> body, or None on 404


def http_get(token: str | None) -> Get:
    def get(url: str) -> bytes | None:
        headers = {"User-Agent": USER_AGENT}
        if token and url.startswith(API):
            headers["Authorization"] = f"Bearer {token}"
            headers["Accept"] = "application/vnd.github+json"
        request = urllib.request.Request(url, headers=headers)  # noqa: S310 (fixed https URLs)
        try:
            with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310
                body: bytes = response.read()
                return body
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return None
            raise

    return get


def _json(get: Get, url: str) -> Any:
    body = get(url)
    return None if body is None else json.loads(body)


def _ci(get: Get, repo: str, branch: str) -> str | None:
    runs = _json(
        get, f"{API}/repos/{ORG}/{repo}/actions/runs?branch={branch}&status=completed&per_page=1"
    )
    items = (runs or {}).get("workflow_runs") or []
    if not items:
        return None
    return "passing" if items[0].get("conclusion") == "success" else "failing"


def _citation(get: Get, repo: str, branch: str) -> data.Citation | None:
    body = get(f"https://raw.githubusercontent.com/{ORG}/{repo}/{branch}/CITATION.cff")
    if body is None:
        return None
    cff = yaml.safe_load(body.decode("utf-8")) or {}
    authors = []
    for person in cff.get("authors") or []:
        name = " ".join(p for p in (person.get("given-names"), person.get("family-names")) if p)
        authors.append(name or str(person.get("name", "")).strip())
    released = str(cff.get("date-released") or "")
    if not cff.get("title") or not authors or not released:
        return None
    return data.Citation(
        title=str(cff["title"]),
        authors=tuple(a for a in authors if a),
        year=released[:4],
        version=str(cff["version"]) if cff.get("version") else None,
        doi=str(cff["doi"]) if cff.get("doi") else None,
        url=str(cff.get("repository-code") or f"https://github.com/{ORG}/{repo}"),
    )


def package_state(get: Get, package: data.Package) -> tuple[data.Live, data.Citation | None]:
    repo = _json(get, f"{API}/repos/{ORG}/{package.repo}")
    if not repo or repo.get("private"):
        return data.Live(), None
    branch = str(repo.get("default_branch") or "main")
    release = _json(get, f"{API}/repos/{ORG}/{package.repo}/releases/latest")
    version = str(release["tag_name"]).removeprefix("v") if release else None
    licence = ((repo.get("license") or {}).get("spdx_id")) or None
    if package.pypi:
        info = (_json(get, f"https://pypi.org/pypi/{package.pypi}/json") or {}).get("info") or {}
        version = str(info.get("version") or "") or version
        licence = info.get("license_expression") or licence
    if licence == "NOASSERTION":
        licence = None
    return (
        data.Live(public=True, version=version, licence=licence, ci=_ci(get, package.repo, branch)),
        _citation(get, package.repo, branch),
    )


def contributors(get: Get) -> tuple[data.Contributor, ...]:
    """People (never bots) who contributed to any public repository in the organisation."""
    people: dict[int, data.Contributor] = {}
    repos = _json(get, f"{API}/orgs/{ORG}/repos?type=public&per_page=100") or []
    for repo in sorted(repos, key=lambda r: str(r.get("name"))):
        if repo.get("private") or repo.get("fork"):
            continue
        listed = _json(get, f"{API}/repos/{ORG}/{repo['name']}/contributors?per_page=100") or []
        for person in listed:
            login = str(person.get("login") or "")
            if not login or person.get("type") == "Bot" or login.endswith("[bot]"):
                continue
            people[int(person["id"])] = data.Contributor(login=login, id=int(person["id"]))
    return tuple(sorted(people.values(), key=lambda c: c.login.lower()))


def fetch_avatar(get: Get, user_id: int) -> tuple[str, bytes] | None:
    body = get(f"https://avatars.githubusercontent.com/u/{user_id}?s=96&v=4")
    if not body:
        return None
    if body.startswith(b"\x89PNG"):
        return ".png", body
    if body.startswith(b"\xff\xd8"):
        return ".jpg", body
    return None


def next_stamp(previous: str, today: dt.date) -> str:
    """The status date moves at most every 28 days: often enough for the 60-day keepalive."""
    last = dt.date.fromisoformat(previous)
    return today.isoformat() if today - last >= STATUS_EVERY else previous
