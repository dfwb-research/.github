"""The hand-kept data files: shape checks, and a lossless state round trip."""

from __future__ import annotations

from pathlib import Path

import pytest
from dfwb import data


def test_committed_data_files_parse() -> None:
    assert [p.repo for p in data.packages()] == [
        "deepfake-workbench",
        "dfwb-protocols",
        "dfwb-torch",
    ]
    assert data.datasets() == []
    assert data.detectors() == []
    assert data.load_state().status_verified


def test_bad_rows_are_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(data, "DATA", tmp_path)
    (tmp_path / "datasets.yml").write_text(
        "datasets:\n  - name: X\n    modality: hologram\n    protocol_version: '1'\n"
        "    terms: https://example.org\n    status: released\n",
        encoding="utf-8",
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
