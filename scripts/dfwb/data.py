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
DATASET_REQUIRED = (
    "name",
    "modality",
    "protocol_version",
    "terms",
    "status",
    "real",
    "fake",
    "methods",
    "default_protocol",
    "rights_cleared",
)
DATASET_OPTIONAL = ("repository", "year", "subjects", "variants", "variants_of")
VARIANTS_OF = ("fakes", "reals")
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
    """One row of the dataset table: the facts dfwb-protocols' own README table shows."""

    name: str
    modality: str
    protocol_version: str
    terms: str
    status: str
    real: int
    fake: int
    methods: tuple[str, ...]
    default_protocol: str
    rights_cleared: bool
    repository: str | None = None
    year: int | None = None
    subjects: int | None = None
    variants: tuple[str, ...] = ()
    variants_of: str | None = None

    @property
    def total(self) -> int:
        return self.real + self.fake


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


def _count(where: str, field: str, value: object, *, optional: bool = False) -> int | None:
    """A whole number of at least zero (a bool is not one); ``None`` only if ``optional``."""
    if value is None and optional:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise DataError(f"{where}: `{field}` must be a whole number, not {value!r}")
    return value


def _names(where: str, field: str, value: object, *, optional: bool = False) -> tuple[str, ...]:
    """A list of distinct, non-empty strings; an absent optional list is empty."""
    if value is None and optional:
        return ()
    if (
        not isinstance(value, list)
        or not value
        or not all(isinstance(v, str) and v.strip() for v in value)
        or len(set(value)) != len(value)
    ):
        raise DataError(f"{where}: `{field}` must be a list of distinct names, not {value!r}")
    return tuple(v.strip() for v in value)


def _dataset(index: int, row: object) -> Dataset:
    where = f"datasets.yml: row {index + 1}"
    if not isinstance(row, dict) or not (
        set(DATASET_REQUIRED) <= set(row) <= {*DATASET_REQUIRED, *DATASET_OPTIONAL}
    ):
        raise DataError(
            f"{where} needs exactly {', '.join(DATASET_REQUIRED)}, and may add "
            f"{', '.join(DATASET_OPTIONAL)}"
        )
    text = {k: str(row[k]).strip() for k in ("name", "modality", "protocol_version", "status")}
    where = f"datasets.yml: {text['name']}"
    if text["modality"] not in MODALITIES or text["status"] not in DATASET_STATUS:
        raise DataError(f"{where} has an unknown modality or status")
    terms = str(row["terms"]).strip()
    if not terms.startswith("https://"):
        raise DataError(f"{where} needs an https:// link to the owner's terms")
    repository = row.get("repository")
    if repository is not None and not str(repository).startswith("https://"):
        raise DataError(f"{where}: `repository` must be an https:// link to the owner's page")
    year = row.get("year")
    if year is not None and (isinstance(year, bool) or not isinstance(year, int)):
        raise DataError(f"{where}: `year` must be a year, not {year!r}")
    default_protocol = row["default_protocol"]
    if not isinstance(default_protocol, str) or not default_protocol.strip():
        raise DataError(f"{where}: `default_protocol` must name the default scheme")
    rights_cleared = row["rights_cleared"]
    if not isinstance(rights_cleared, bool):
        raise DataError(f"{where}: `rights_cleared` must be true or false")
    if text["status"] == "released" and not rights_cleared:
        raise DataError(f"{where} is released, so its rights must be cleared")
    variants = _names(where, "variants", row.get("variants"), optional=True)
    variants_of = row.get("variants_of")
    if variants_of is not None and (variants_of not in VARIANTS_OF or not variants):
        raise DataError(
            f"{where}: `variants_of` is {' or '.join(VARIANTS_OF)}, and needs `variants`"
        )
    return Dataset(
        name=text["name"],
        modality=text["modality"],
        protocol_version=text["protocol_version"],
        terms=terms,
        status=text["status"],
        real=_count(where, "real", row["real"]) or 0,
        fake=_count(where, "fake", row["fake"]) or 0,
        methods=_names(where, "methods", row["methods"]),
        default_protocol=default_protocol.strip(),
        rights_cleared=rights_cleared,
        repository=None if repository is None else str(repository),
        year=year,
        subjects=_count(where, "subjects", row.get("subjects"), optional=True),
        variants=variants,
        variants_of=variants_of,
    )


def datasets() -> list[Dataset]:
    rows = _load_yaml("datasets.yml").get("datasets") or []
    if not isinstance(rows, list):
        raise DataError("datasets.yml: `datasets` must be a list")
    return [_dataset(index, row) for index, row in enumerate(rows)]


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
