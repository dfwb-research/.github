"""The profile's data files: hand-kept YAML inputs and the refresh's JSON state.

profile/data/packages.yml, datasets.yml and zoo.yml are edited by hand (rows only from the
packages' own registries). profile/data/state.json is written by the refresh: live package
facts, citations, contributors and the date the profile was last verified.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .theme import ROOT

DATA = ROOT / "profile" / "data"
STATE = DATA / "state.json"
AVATARS = DATA / "avatars"
MAINTAINER_ID = 82789246
MAINTAINER_LOGIN = "lukegcollins"

DATASET_STATUS = ("released", "in preparation")
MODALITIES = ("video", "image", "audio", "audio-visual")
ADAPTER_STATUS = ("released", "in progress", "planned")


class DataError(ValueError):
    pass


@dataclass(frozen=True)
class Package:
    repo: str
    title: str
    summary: str
    pypi: str | None = None


@dataclass(frozen=True)
class Dataset:
    name: str
    modality: str
    protocol_version: str
    terms: str
    status: str


@dataclass(frozen=True)
class Detector:
    name: str
    paper: str
    adapter: str
    weights_licence: str


@dataclass(frozen=True)
class Live:
    """What the refresh found for one package. ``public`` is False until the repo opens."""

    public: bool = False
    version: str | None = None
    licence: str | None = None
    ci: str | None = None  # "passing" | "failing" | None

    @property
    def released(self) -> bool:
        return self.public and self.version is not None


@dataclass(frozen=True)
class Citation:
    title: str
    authors: tuple[str, ...]
    year: str
    version: str | None = None
    doi: str | None = None
    url: str | None = None


@dataclass(frozen=True)
class Contributor:
    login: str
    id: int


@dataclass(frozen=True)
class State:
    status_verified: str
    live: dict[str, Live] = field(default_factory=dict)
    citations: dict[str, Citation] = field(default_factory=dict)
    contributors: tuple[Contributor, ...] = ()

    def others(self) -> tuple[Contributor, ...]:
        return tuple(c for c in self.contributors if c.id != MAINTAINER_ID)


def _load_yaml(name: str) -> dict[str, Any]:
    loaded = yaml.safe_load((DATA / name).read_text(encoding="utf-8")) or {}
    if not isinstance(loaded, dict):
        raise DataError(f"{name}: expected a mapping at the top level")
    return loaded


def _rows(name: str, key: str, fields: tuple[str, ...]) -> list[dict[str, str]]:
    rows = _load_yaml(name).get(key) or []
    if not isinstance(rows, list):
        raise DataError(f"{name}: `{key}` must be a list")
    out = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or set(row) != set(fields):
            raise DataError(f"{name}: row {index + 1} needs exactly {', '.join(fields)}")
        out.append({k: str(row[k]).strip() for k in fields})
    return out


def packages() -> list[Package]:
    rows = _load_yaml("packages.yml").get("packages") or []
    return [
        Package(
            repo=str(r["repo"]),
            title=str(r["title"]),
            summary=" ".join(str(r["summary"]).split()),
            pypi=r.get("pypi") or None,
        )
        for r in rows
    ]


def datasets() -> list[Dataset]:
    fields = ("name", "modality", "protocol_version", "terms", "status")
    out = [Dataset(**row) for row in _rows("datasets.yml", "datasets", fields)]
    for d in out:
        if d.modality not in MODALITIES or d.status not in DATASET_STATUS:
            raise DataError(f"datasets.yml: {d.name} has an unknown modality or status")
        if not d.terms.startswith("https://"):
            raise DataError(f"datasets.yml: {d.name} needs an https:// link to the owner's terms")
    return out


def detectors() -> list[Detector]:
    fields = ("name", "paper", "adapter", "weights_licence")
    out = [Detector(**row) for row in _rows("zoo.yml", "detectors", fields)]
    for d in out:
        if d.adapter not in ADAPTER_STATUS:
            raise DataError(f"zoo.yml: {d.name} has an unknown adapter status")
        if not d.paper.startswith("https://"):
            raise DataError(f"zoo.yml: {d.name} needs an https:// link to its paper")
    return out


def load_state(path: Path = STATE) -> State:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return State(
        status_verified=str(raw["status_verified"]),
        live={k: Live(**v) for k, v in sorted(raw.get("live", {}).items())},
        citations={
            k: Citation(**{**v, "authors": tuple(v["authors"])})
            for k, v in sorted(raw.get("citations", {}).items())
        },
        contributors=tuple(Contributor(**c) for c in raw.get("contributors", [])),
    )


def dump_state(state: State) -> str:
    payload = {
        "status_verified": state.status_verified,
        "live": {k: asdict(v) for k, v in sorted(state.live.items())},
        "citations": {
            k: {**asdict(v), "authors": list(v.authors)} for k, v in sorted(state.citations.items())
        },
        "contributors": [
            asdict(c) for c in sorted(state.contributors, key=lambda c: c.login.lower())
        ],
    }
    return json.dumps(payload, indent=1, ensure_ascii=False) + "\n"


def avatar(user_id: int) -> tuple[str, bytes] | None:
    """The cached avatar for a GitHub user id as (mime type, bytes), if the refresh stored one."""
    for suffix, mime in ((".jpg", "image/jpeg"), (".png", "image/png")):
        path = AVATARS / f"{user_id}{suffix}"
        if path.exists():
            return mime, path.read_bytes()
    return None
