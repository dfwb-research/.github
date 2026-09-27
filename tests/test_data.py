"""The hand-kept data files: shape checks, and a lossless state round trip."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from dfwb import data


def test_committed_data_files_parse() -> None:
    assert [p.repo for p in data.packages()] == [
        "deepfake-workbench",
        "dfwb-protocols",
        "dfwb-torch",
    ]
    datasets = data.datasets()
    assert [d.name for d in datasets] == sorted((d.name for d in datasets), key=str.casefold)
    assert len(datasets) == 21
    assert all(d.status == "in preparation" for d in datasets)
    assert not any(d.rights_cleared for d in datasets)
    assert all(d.terms.startswith("https://") for d in datasets)
    uadfv = next(d for d in datasets if d.name == "UADFV")
    form = (
        "https://docs.google.com/forms/d/e/"
        "1FAIpQLScKPoOv15TIZ9Mn0nGScIVgKRM9tFWOmjh9eHKx57Yp-XcnxA/viewform"
    )
    assert uadfv.repository == uadfv.terms == form
    assert (uadfv.real, uadfv.fake, uadfv.total, uadfv.methods) == (49, 49, 98, ("faceswap",))
    assert data.detectors() == []
    assert data.load_state().status_verified


def test_bad_rows_are_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(data, "DATA", tmp_path)
    (tmp_path / "datasets.yml").write_text(
        yaml.safe_dump({"datasets": [{**GOOD_ROW, "modality": "hologram"}]}), encoding="utf-8"
    )
    with pytest.raises(data.DataError, match="modality"):
        data.datasets()
    (tmp_path / "zoo.yml").write_text("detectors:\n  - name: Y\n", encoding="utf-8")
    with pytest.raises(data.DataError, match="exactly"):
        data.detectors()


def test_state_round_trips(tmp_path: Path) -> None:
    state = data.State(
        status_verified="2026-09-25",
        live={"dfwb-torch": data.Live(public=True, version="0.1.0", licence="MIT", ci="failing")},
        citations={"dfwb-torch": data.Citation("dfwb-torch", ("Luke Collins",), "2026")},
        contributors=(data.Contributor("zed", 7), data.Contributor("amy", 3)),
    )
    path = tmp_path / "state.json"
    path.write_text(data.dump_state(state), encoding="utf-8")
    loaded = data.load_state(path)
    assert loaded.live == state.live and loaded.citations == state.citations
    assert [c.login for c in loaded.contributors] == ["amy", "zed"]


GOOD_ROW = {
    "name": "X",
    "repository": "https://example.org/x",
    "year": 2020,
    "modality": "video",
    "real": 2,
    "fake": 3,
    "subjects": None,
    "methods": ["a", "b"],
    "variants": ["raw", "c23"],
    "variants_of": None,
    "default_protocol": "official",
    "rights_cleared": False,
    "protocol_version": "1.0",
    "terms": "https://example.org/terms",
    "status": "in preparation",
}


@pytest.mark.parametrize(
    ("change", "problem"),
    [
        ({"real": "2"}, "real"),
        ({"fake": True}, "fake"),
        ({"subjects": -1}, "subjects"),
        ({"year": "2020"}, "year"),
        ({"methods": []}, "methods"),
        ({"methods": ["a", "a"]}, "methods"),
        ({"variants": ["raw", "raw"]}, "variants"),
        ({"variants": None, "variants_of": "fakes"}, "variants_of"),
        ({"variants_of": "everyone"}, "variants_of"),
        ({"repository": "http://example.org/x"}, "repository"),
        ({"rights_cleared": "no"}, "rights_cleared"),
        ({"status": "released"}, "rights"),
        ({"default_protocol": ""}, "default_protocol"),
        ({"colour": "green"}, "exactly"),
    ],
)
def test_bad_dataset_rows_are_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, change: dict[str, object], problem: str
) -> None:
    monkeypatch.setattr(data, "DATA", tmp_path)
    (tmp_path / "datasets.yml").write_text(
        yaml.safe_dump({"datasets": [{**GOOD_ROW, **change}]}), encoding="utf-8"
    )
    with pytest.raises(data.DataError, match=problem):
        data.datasets()


def test_optional_dataset_fields_may_be_left_out(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(data, "DATA", tmp_path)
    row = {k: v for k, v in GOOD_ROW.items() if k not in data.DATASET_OPTIONAL}
    (tmp_path / "datasets.yml").write_text(yaml.safe_dump({"datasets": [row]}), encoding="utf-8")
    (dataset,) = data.datasets()
    assert (dataset.repository, dataset.year, dataset.subjects) == (None, None, None)
    assert (dataset.variants, dataset.variants_of, dataset.total) == ((), None, 5)
