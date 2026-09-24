# Contributing to dfwb-research

Thanks for your interest. These defaults apply to every repository in the organisation unless a
repository has its own `CONTRIBUTING.md`.

## Before you start

- **Bugs:** open an issue with the bug form and include `dfwb doctor --json`.
- **Features, datasets, zoo adapters:** open an issue with the matching form first, so we can agree
  on the design before you write code.
- **Questions:** use the Discussions tab of
  [deepfake-workbench](https://github.com/dfwb-research/deepfake-workbench/discussions).
- **Security issues:** never in public; see [SECURITY.md](SECURITY.md).

Never attach dataset media (videos, frames, audio) anywhere. The projects distribute identifiers,
labels and splits only.

## Development setup

Linux is the only supported OS. You need [uv](https://docs.astral.sh/uv/) and Python 3.12 or newer.

```bash
git clone https://github.com/dfwb-research/<repository> && cd <repository>
uv sync                         # exact environment from uv.lock
uv run pytest                   # tests
uv run ruff check && uv run ruff format --check && uv run mypy
uv run pre-commit run --all-files
```

## Pull requests

- One logical change per pull request, with tests (the projects are developed test-first).
- Commit messages and the PR title follow [Conventional Commits](https://www.conventionalcommits.org/)
  (`feat: …`, `fix: …`, `docs: …`).
- Add an entry under **Unreleased** in `CHANGELOG.md` for user-visible changes.
- Say so explicitly if you change a public contract (C1–C5: plugin API, config schema, protocol
  records, detector interface, score files).
- Pull requests are squash-merged once CI is green.
- Commit messages must not contain `Co-Authored-By:` or "Generated with …" trailers; CI rejects
  them.

## Licence

By contributing you agree that your contribution is licensed under the repository's licence (MIT
for code; CC BY 4.0 for protocol data in `dfwb-protocols`).
