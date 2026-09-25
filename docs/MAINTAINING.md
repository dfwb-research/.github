# Maintaining the organisation profile

The profile in [`profile/README.md`](../profile/README.md) is partly generated. The prose
outside the `<!-- NAME:START -->` / `<!-- NAME:END -->` markers is hand-written; everything
between the markers, and every image in `profile/assets/`, comes from the build.

| Path | What it is |
|---|---|
| `design/tokens.json` | The "Verified mono" identity: colours for both themes, type, layout limits, motion. |
| `design/avatar.svg` | The organisation avatar, "df" over "wb" as outlines. Built with the rest. |
| `design/fonts/` | IBM Plex Sans and Mono, unmodified from `google/fonts`, with the OFL. The images embed subsets renamed as the OFL requires for the Reserved Font Name "Plex". |
| `profile/data/packages.yml` | The package cards. Set `pypi` once a package is on PyPI under that name. |
| `profile/data/datasets.yml`, `zoo.yml` | The dataset and detector tables. Add rows only from the packages' own registries. |
| `profile/data/state.json` | Written by the refresh: live package facts, citations, contributors, the status date. |
| `profile/data/avatars/` | Avatars the images embed, cached by GitHub user id. |
| `scripts/build_profile.py` | Rebuilds the images and README blocks from the files above. |
| `scripts/refresh_profile.py` | Fetches the live facts, rebuilds, validates, writes. |

The paper under **Cite this work** is `PAPER_BIBTEX` in `scripts/dfwb/profile.py`. It holds a
placeholder until the paper is published; replace it with the real BibTeX entry then, and not before.

## Rebuild

```bash
uv sync
uv run scripts/build_profile.py           # rewrite profile/assets/ and the README blocks
uv run scripts/build_profile.py --check   # what CI runs: fail if anything is stale
uv run pytest                             # UPDATE_GOLDEN=1 regenerates goldens after a deliberate change
uv run ruff check && uv run ruff format --check && uv run mypy
```

The build refuses text that fails WCAG AA or renders below 12 px on a phone. The hero is the
exception: it is checked at desktop width only, because there is one hero for every screen. GitHub
replaces the whole media query of any `<picture>` source that mentions `prefers-color-scheme`, so
a phone-width variant would show on desktop too.

The green is the only colour and marks verified states only; a test fails if it shows up anywhere
else.

## The avatar

GitHub takes avatars as PNG, so after a change to `design/avatar.svg`, render it and upload it
under the organisation's Settings → Profile:

```bash
npx playwright screenshot --viewport-size="500, 500" "file://$PWD/design/avatar.svg" avatar.png
```

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

`main` takes changes only through pull requests, so when something changed the refresh commits
it to the `profile-refresh` branch as `chore(profile): refresh <what>`, opens a pull request (or
updates the open one) and starts CI on the branch. Merge it once CI passes. The branch is
rebuilt from `main` every run, so an unmerged refresh never goes stale. Because the status date
moves monthly, a pull request turns up about once a month, and merging it keeps this public
repository inside GitHub's 60-day activity window.

The workflow can open pull requests only while Settings → Actions → General → Workflow
permissions → "Allow GitHub Actions to create and approve pull requests" is on.
