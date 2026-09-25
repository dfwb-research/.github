# Maintaining the organisation profile

The profile in [`profile/README.md`](../profile/README.md) is partly generated. The prose
outside the `<!-- NAME:START -->` / `<!-- NAME:END -->` markers is hand-written; everything
between the markers, and every image in `profile/assets/`, comes from the build.

| Path | What it is |
|---|---|
| `design/tokens.json` | The "Verified mono" identity: colours for both themes, type, layout limits, motion. |
| `design/fonts/` | IBM Plex Sans and Mono, unmodified from `google/fonts`, with the OFL. The images embed subsets renamed as the OFL requires for the Reserved Font Name "Plex". |
| `profile/data/packages.yml` | The package cards. Set `pypi` once a package is on PyPI under that name. |
| `profile/data/datasets.yml`, `zoo.yml` | The dataset and detector tables. Add rows only from the packages' own registries. |
| `profile/data/state.json` | Written by the refresh: live package facts, citations, contributors, the status date. |
| `profile/data/avatars/` | Avatars the images embed, cached by GitHub user id. |
| `scripts/build_profile.py` | Rebuilds the images and README blocks from the files above. |
| `scripts/refresh_profile.py` | Fetches the live facts, rebuilds, validates, writes. |

## Rebuild

```bash
uv sync
uv run scripts/build_profile.py           # rewrite profile/assets/ and the README blocks
uv run scripts/build_profile.py --check   # what CI runs: fail if anything is stale
uv run pytest                             # UPDATE_GOLDEN=1 regenerates goldens after a deliberate change
uv run ruff check && uv run ruff format --check && uv run mypy
```

The build refuses text that fails WCAG AA or renders below 12 px on a phone. The green is the
only colour and marks verified states only; a test fails if it shows up anywhere else.

## The weekly refresh

`.github/workflows/refresh.yml` runs every Monday at 06:41 UTC and on demand. With nothing but
the workflow's own `GITHUB_TOKEN` and public APIs it:

1. checks the three package repositories. A card goes live once its repository is public and
   has a release: version and licence from the release and the repository (or PyPI, when
   `pypi` is set), CI state from the latest completed run on the default branch;
2. reads each public package's `CITATION.cff` into an IEEE-style reference and a BibTeX entry;
3. lists the people who have contributed to the organisation's public repositories, bots
   excluded, and caches their avatars. The contributor wall appears once someone besides the
   maintainer is on it;
4. moves the "status verified" date, at most once every 28 days, when every check passes.

It commits only when something changed, as `chore(profile): refresh <what>`. The monthly
status date also keeps this public repository inside GitHub's 60-day activity window.
