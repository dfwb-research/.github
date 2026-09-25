# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "brotli==1.2.0",
#   "fonttools[woff]==4.66.0",
#   "pyyaml==6.0.3",
#   "uharfbuzz==0.56.2",
# ]
# ///
"""Build the DFWB profile images and README blocks from design/tokens.json and profile/data/.

    uv run scripts/build_profile.py           # write profile/assets/ and profile/README.md
    uv run scripts/build_profile.py --check   # fail if either is stale

The build refuses text that fails WCAG AA or renders below the minimum size.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dfwb import profile
from dfwb.theme import ROOT


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--check", action="store_true", help="verify instead of writing")
    args = parser.parse_args(argv)
    built, ledger = profile.build_all()
    problems = ledger.failures(profile.TOKENS.min_text_px)
    for problem in problems:
        print(f"illegible: {problem}", file=sys.stderr)
    if problems:
        return 1
    if args.check:
        stale = profile.stale(built)
        for path in stale:
            print(f"out of date: {path.relative_to(ROOT)}", file=sys.stderr)
        return 1 if stale else 0
    changed = profile.write(built)
    for path in changed:
        print(f"wrote {path.relative_to(ROOT)}")
    print(f"{len(built)} files, {len(changed)} changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
