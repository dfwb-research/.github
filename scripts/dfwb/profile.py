"""Build the DFWB profile: every image, and the README blocks between the markers."""

from __future__ import annotations

import re
from pathlib import Path

from svgkit.color import Ledger
from svgkit.svg import write_if_changed

from . import art, data
from .theme import ROOT, load

TOKENS = load()
PROFILE = ROOT / "profile"
ASSETS = PROFILE / "assets"
README = PROFILE / "README.md"
AVATAR = ROOT / "design" / "avatar.svg"
# Package repositories copy their own hero from here: repos/<repo>/hero-{light,dark}.svg.
REPOS = ROOT / "repos"
ORG = "https://github.com/dfwb-research"
_MD_SPECIAL = re.compile(r"([\\`*_\[\]<>$|#])")
# The paper to cite. Replace the placeholder with the BibTeX entry once the paper is published.
PAPER_BIBTEX = "% BibTeX entry to follow on publication."


def md(text: str) -> str:
    """Escape Markdown syntax, and ``$`` (which GitHub may read as maths), in plain text."""
    return _MD_SPECIAL.sub(r"\\\1", " ".join(text.split()))


def picture(base: str, alt: str, *, width: int | None = None) -> str:
    size = f' width="{width}"' if width else ""
    alt = alt.replace("&", "&amp;").replace('"', "&quot;")
    return (
        f'<picture><source media="(prefers-color-scheme: dark)" srcset="{base}-dark.svg">'
        f'<img alt="{alt}" src="{base}-light.svg"{size}></picture>'
    )


def card_gaps(count: int) -> list[int]:
    """Every card but the last carries the gap, so the row is exactly as wide as the hero."""
    return [art.CARD_GAP] * (count - 1) + [0] * min(count, 1)


def build_images(state: data.State) -> tuple[dict[Path, str], Ledger]:
    ledger = Ledger()
    out: dict[Path, str] = {}
    packages = data.packages()
    for name, theme in sorted(TOKENS.themes.items()):
        out[ASSETS / f"hero-{name}.svg"] = art.hero(
            TOKENS, theme, art.HERO_WIDE, ledger, f"hero-{name}.svg"
        )
        for package in packages:
            rel = f"repos/{package.repo}/hero-{name}.svg"
            out[REPOS / package.repo / f"hero-{name}.svg"] = art.repo_hero(
                TOKENS, theme, art.HERO_WIDE, ledger, rel, package.repo
            )
        for package, gap in zip(packages, card_gaps(len(packages)), strict=True):
            rel = f"{package.repo}-{name}.svg"
            live = state.live.get(package.repo, data.Live())
            out[ASSETS / rel] = art.package_card(TOKENS, theme, package, live, ledger, rel, gap=gap)
        out[ASSETS / f"maintainer-{name}.svg"] = art.maintainer_card(
            TOKENS, theme, ledger, f"maintainer-{name}.svg"
        )
        if state.others():
            out[ASSETS / f"contributors-{name}.svg"] = art.contributor_wall(
                TOKENS, theme, state.contributors, ledger, f"contributors-{name}.svg"
            )
    return out, ledger


def packages_block(state: data.State) -> str:
    cards = []
    packages = data.packages()
    for package, gap in zip(packages, card_gaps(len(packages)), strict=True):
        live = state.live.get(package.repo, data.Live())
        image = picture(
            f"assets/{package.repo}",
            f"{package.repo}: {package.summary}"
            + (f" Version {live.version}." if live.released else " v0.1 in preparation."),
            width=round(art.CARD_W + gap),
        )
        # A card links to its repository only once the repository is public and released.
        cards.append(f'<a href="{ORG}/{package.repo}">{image}</a>' if live.released else image)
    released = sum(1 for p in data.packages() if state.live.get(p.repo, data.Live()).released)
    lead = (
        "The first releases are in preparation. Each repository opens with its v0.1 release."
        if not released
        else "Cards link to each released repository; the rest open with their v0.1 release."
    )
    # No whitespace between the cards: the gap is in the images, not a font-dependent space.
    return lead + "\n\n<p>\n" + "".join(cards) + "\n</p>"


# The dataset table is the one dfwb-protocols generates for its own README
# (scripts/dataset_table.py there): the same columns, cells, notes and method lists, word for
# word, so the two never disagree. Only the line on the datasets' status is the profile's own.
DATASET_HEADER = (
    "| Dataset | Year | Modality | Real | Fake | Total | Subjects | Manipulation methods "
    "| Compression variants | Default protocol | Rights cleared |"
)
DATASET_ALIGN = "|---|---:|---|---:|---:|---:|---:|---|---|---|---|"
# A dataset with more methods than this has them listed under the table, not in its cell.
MAX_METHODS_IN_CELL = 5
DASH = "\N{EM DASH}"


def _count(value: int | None) -> str:
    return DASH if value is None else f"{value:,}"


def dataset_cells(d: data.Dataset) -> list[str]:
    name = md(d.name)
    if len(d.methods) <= MAX_METHODS_IN_CELL:
        methods = f"{len(d.methods)}: " + ", ".join(md(m) for m in d.methods)
    else:
        methods = f"{len(d.methods)}, listed below"
    variants = ", ".join(md(v) for v in d.variants) or DASH
    if d.variants_of:
        variants += f" ({d.variants_of} only)"
    return [
        f"[{name}]({d.repository})" if d.repository else name,
        DASH if d.year is None else str(d.year),
        d.modality,
        _count(d.real),
        _count(d.fake),
        _count(d.total),
        _count(d.subjects),
        methods,
        variants,
        f"`{d.default_protocol}`",
        "Yes" if d.rights_cleared else "No",
    ]


def dataset_notes(versions: list[str]) -> list[str]:
    """The notes under the dataset table, one Markdown list item each."""
    return [
        f"- Real, Fake and Total count the videos each protocol lists in dfwb-protocols "
        f"{' and '.join(versions)}; a video at several compressions counts once. These are not "
        "the publishers' totals, and differ where the local release differs: DFDC's protocol, "
        "for one, lists only the public test set.",
        "- Real and Fake follow each dataset's own `binary` label, which judges the video alone: "
        "a real video with fake audio counts as real.",
        "- Year is that of the paper the dataset's card cites, which can be later than the "
        "release.",
        "- Subjects count distinct people, shown only where every identity a dataset records is "
        f"a person; {DASH} elsewhere.",
        "- Manipulation methods count the distinct `method` labels of the fakes. Where a release "
        "does not say how each fake was made, one label covers them all.",
        "- Rights cleared: No means DFWB does not yet publish these lists. Each dataset comes "
        "from its owner, under the owner's terms.",
    ]


def status_line(datasets: list[data.Dataset]) -> str:
    counts = [(s, sum(1 for d in datasets if d.status == s)) for s in data.DATASET_STATUS]
    present = [(s, n) for s, n in counts if n]
    if len(present) == 1:
        return f"All {len(datasets)} datasets are {present[0][0]}."
    said = " and ".join(f"{n} {'is' if n == 1 else 'are'} {s}" for s, n in present)
    return f"Of the {len(datasets)} datasets, {said}."


def datasets_table(datasets: list[data.Dataset]) -> list[str]:
    lines = [status_line(datasets), "", DATASET_HEADER, DATASET_ALIGN]
    lines += ["| " + " | ".join(dataset_cells(d)) + " |" for d in datasets]
    versions = sorted({d.protocol_version for d in datasets})
    lines += ["", *dataset_notes(versions)]
    # After the notes, and behind a paragraph of its own, so the two lists never merge into one.
    long = [d for d in datasets if len(d.methods) > MAX_METHODS_IN_CELL]
    if long:
        lines += ["", "The manipulation methods of the datasets with more than five:", ""]
        lines += [
            f"- **{md(d.name)}** ({len(d.methods)}): " + ", ".join(md(m) for m in d.methods)
            for d in long
        ]
    return lines


def tables_block() -> str:
    datasets, detectors = data.datasets(), data.detectors()
    if not datasets and not detectors:
        return "The dataset and detector tables are populating with v0.1."
    parts: list[str] = []
    if datasets:
        parts += datasets_table(datasets)
    if detectors:
        if parts:
            parts.append("")
        parts.append("| Detector | Paper | Adapter | Weights licence |")
        parts.append("|---|---|---|---|")
        parts += [
            f"| {md(d.name)} | [paper]({d.paper}) | {d.adapter} | {md(d.weights_licence)} |"
            for d in detectors
        ]
    return "\n".join(parts)


def ieee(citation: data.Citation) -> str:
    """IEEE-style software reference: L. Collins, "Title," version 1.0, 2026. [Online]. ..."""

    def initials(name: str) -> str:
        *given, family = name.split()
        return " ".join(f"{g[0]}." for g in given) + f" {family}" if given else family

    authors = [initials(a) for a in citation.authors]
    if len(authors) == 1:
        who = authors[0]
    elif len(authors) == 2:
        who = f"{authors[0]} and {authors[1]}"
    else:
        who = ", ".join(authors[:-1]) + ", and " + authors[-1]
    ref = f'{who}, "{citation.title},"'
    if citation.version:
        ref += f" version {citation.version},"
    ref += f" {citation.year}."
    if citation.doi:
        ref += f" doi: {citation.doi}."
    elif citation.url:
        ref += f" [Online]. Available: {citation.url}"
    return ref


def bibtex(key: str, citation: data.Citation) -> str:
    fields = [
        ("author", " and ".join(citation.authors)),
        ("title", "{" + citation.title + "}"),
        ("year", citation.year),
    ]
    if citation.version:
        fields.append(("version", citation.version))
    if citation.doi:
        fields.append(("doi", citation.doi))
    if citation.url:
        fields.append(("url", citation.url))
    body = ",\n".join(f"  {name} = {{{value}}}" for name, value in fields)
    return f"@software{{{key},\n{body}\n}}"


def cite_block(state: data.State) -> str:
    # GitHub's "Cite this repository" button reads only a CITATION.cff at a repository's root;
    # dfwb-torch has none there, since each of its packages is cited on its own.
    lines = [
        "The deepfake-workbench and dfwb-protocols repositories each carry a `CITATION.cff`, so "
        'GitHub\'s "Cite this repository" button gives you the reference once the repository is '
        "public. Each dfwb-torch package carries its own `CITATION.cff`, in the package's folder."
    ]
    for repo, citation in sorted(state.citations.items()):
        key = repo.replace("-", "_")
        lines += [
            "",
            f"**{md(repo)}**: {md(ieee(citation))}",
            "",
            "```bibtex",
            bibtex(key, citation),
            "```",
        ]
    lines += [
        "",
        "If you found this work helpful, or used it in your research, please cite the "
        "following paper:",
        "",
        "```bibtex",
        PAPER_BIBTEX,
        "```",
    ]
    return "\n".join(lines)


def people_block(state: data.State) -> str:
    card = picture(
        "assets/maintainer",
        "Luke Collins, lead maintainer, Deakin University, ORCID 0009-0002-7771-1081.",
        width=400,
    )
    text = (
        f'<a href="https://github.com/lukegcollins">{card}</a>\n\n'
        "Contributions are welcome! Check out our [contributing guidelines]"
        "(https://github.com/dfwb-research/.github/blob/main/CONTRIBUTING.md) to get started."
    )
    others = state.others()
    if others:
        names = ", ".join(f"[{c.login}](https://github.com/{c.login})" for c in others)
        wall = picture("assets/contributors", "Contributors to DFWB Research")
        text += f"\n\n{wall}\n\nWith thanks to {names}."
    return text


def status_block(state: data.State) -> str:
    return f'<p align="right"><samp>status verified {state.status_verified}</samp></p>'


def replace_block(text: str, name: str, content: str) -> str:
    pattern = re.compile(rf"(<!-- {name}:START -->\n)(.*?)(<!-- {name}:END -->)", flags=re.DOTALL)
    if not pattern.search(text):
        raise ValueError(f"profile/README.md is missing the {name} markers")
    return pattern.sub(lambda m: f"{m.group(1)}{content}\n{m.group(3)}", text, count=1)


def build_readme(text: str, state: data.State) -> str:
    text = replace_block(text, "PACKAGES", packages_block(state))
    text = replace_block(text, "TABLES", tables_block())
    text = replace_block(text, "CITE", cite_block(state))
    text = replace_block(text, "PEOPLE", people_block(state))
    return replace_block(text, "STATUS", status_block(state))


def build_all(state: data.State | None = None) -> tuple[dict[Path, str], Ledger]:
    state = state or data.load_state()
    out, ledger = build_images(state)
    out[README] = build_readme(README.read_text(encoding="utf-8"), state)
    out[AVATAR] = art.avatar(TOKENS)
    return out, ledger


def write(built: dict[Path, str]) -> list[Path]:
    return [path for path, content in sorted(built.items()) if write_if_changed(path, content)]


def stale(built: dict[Path, str]) -> list[Path]:
    present = set(ASSETS.glob("*.svg")) | set(REPOS.glob("*/*.svg"))
    changed = [
        p
        for p, content in sorted(built.items())
        if not p.exists() or p.read_text(encoding="utf-8") != content
    ]
    return changed + sorted(present - set(built))
