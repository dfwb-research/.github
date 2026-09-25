# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "brotli==1.2.0",
#   "fonttools[woff]==4.66.0",
#   "pyyaml==6.0.3",
#   "uharfbuzz==0.56.2",
# ]
# ///
"""Weekly refresh of the DFWB profile: package cards, tables, citations, contributors, status.

    GITHUB_TOKEN=... uv run scripts/refresh_profile.py

Reads public data only. Validates everything it rebuilds before writing, because the commit it
leads to is pushed with GITHUB_TOKEN and triggers no other workflow. Exit 1 means nothing was
written.
"""

from __future__ import annotations

import datetime as dt
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dfwb import data, profile, sources, validate


def output(name: str, value: str) -> None:
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        with Path(path).open("a", encoding="utf-8") as handle:
            handle.write(f"{name}={value}\n")


def main() -> int:
    get = sources.http_get(os.environ.get("GITHUB_TOKEN"))
    today = dt.datetime.now(dt.UTC).date()
    previous = data.load_state()
    try:
        # The hand-kept files must parse before anything else happens.
        data.datasets()
        data.detectors()
        live: dict[str, data.Live] = {}
        citations: dict[str, data.Citation] = {}
        for package in data.packages():
            package_live, citation = sources.package_state(get, package)
            live[package.repo] = package_live
            if citation:
                citations[package.repo] = citation
        people = sources.contributors(get)
        avatars: dict[Path, bytes] = {}
        for person in people:
            fetched = sources.fetch_avatar(get, person.id)
            if fetched:
                suffix, body = fetched
                avatars[data.AVATARS / f"{person.id}{suffix}"] = body
    except (OSError, ValueError, KeyError) as exc:
        print(f"::error::refresh failed, nothing written: {exc}")
        output("commit", "false")
        return 1

    for path, body in avatars.items():
        if not path.exists() or path.read_bytes() != body:
            for stale in data.AVATARS.glob(f"{path.stem}.*"):
                stale.unlink()
            path.write_bytes(body)

    state = data.State(
        status_verified=sources.next_stamp(previous.status_verified, today),
        live=live,
        citations=citations,
        contributors=people,
    )
    built, ledger = profile.build_all(state)
    built[data.STATE] = data.dump_state(state)
    problems = list(ledger.failures(profile.TOKENS.min_text_px))
    for path, content in built.items():
        if path.suffix == ".svg":
            problems += validate.check_svg(path.name, content)
    if problems:
        for problem in problems:
            print(f"::error::{problem}")
        output("commit", "false")
        return 1

    changed = profile.write(built)
    what = "status" if changed == [data.STATE] else "profile"
    output("commit", "true")
    output("what", what)
    print(f"{len(changed)} files changed; status verified {state.status_verified}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
