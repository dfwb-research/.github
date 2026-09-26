<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/hero-dark.svg">
  <img alt="DFWB Research. Open, reproducible tooling for deepfake detection research: datasets, protocols, training, evaluation." src="assets/hero-light.svg">
</picture>

### Packages

<!-- PACKAGES:START -->
The first releases are in preparation. Each repository opens with its v0.1 release.

<p>
<picture><source media="(prefers-color-scheme: dark)" srcset="assets/deepfake-workbench-dark.svg"><img alt="deepfake-workbench: The framework: verified dataset inventories, face preprocessing, training, scoring any detector, and evaluation with uncertainty. One dfwb command. v0.1 in preparation." src="assets/deepfake-workbench-light.svg" width="272"></picture><picture><source media="(prefers-color-scheme: dark)" srcset="assets/dfwb-protocols-dark.svg"><img alt="dfwb-protocols: Versioned train, validation and test splits for public deepfake datasets, CC BY 4.0. v0.1 in preparation." src="assets/dfwb-protocols-light.svg" width="272"></picture><picture><source media="(prefers-color-scheme: dark)" srcset="assets/dfwb-torch-dark.svg"><img alt="dfwb-torch: Small, standalone PyTorch utilities for media forensics, starting with dfwb-torch-srm. v0.1 in preparation." src="assets/dfwb-torch-light.svg" width="264"></picture>
</p>
<!-- PACKAGES:END -->

### Principles

**Never media.** We publish identifiers, labels and splits, never the videos, frames or audio. You get each dataset from its owner, under the owner's terms.

**Reproducible by default.** Local inventories are checked against versioned, sha256-pinned splits, runs are seed-locked, and results carry confidence intervals. [RESPONSIBLE_USE.md](https://github.com/dfwb-research/.github/blob/main/RESPONSIBLE_USE.md) covers the rest.

### Datasets and detectors

<!-- TABLES:START -->
All 21 datasets are in preparation.

| Dataset | Year | Modality | Real | Fake | Total | Subjects | Manipulation methods | Compression variants | Default protocol | Rights cleared |
|---|---:|---|---:|---:|---:|---:|---|---|---|---|
| [AV-Deepfake1M++](https://huggingface.co/datasets/ControlNet/AV-Deepfake1M-PlusPlus) | 2025 | audio-visual | 39,158 | 38,168 | 77,326 | — | 2: diff2lip, Talklip | — | `official` | No |
| [Celeb-DF v1](https://github.com/yuezunli/celeb-deepfakeforensics) | 2020 | video | 408 | 795 | 1,203 | — | 1: Celeb-synthesis | — | `official+ident-80-20` | No |
| [Celeb-DF v2](https://github.com/yuezunli/celeb-deepfakeforensics) | 2020 | video | 890 | 5,639 | 6,529 | — | 1: Celeb-synthesis | — | `official+ident-80-20` | No |
| [Celeb-DF v3](https://github.com/OUC-VAS/Celeb-DF-PP) | 2025 | video | 890 | 53,196 | 54,086 | — | 22, listed below | — | `official+ident-80-20` | No |
| [DeeperForensics-1.0](https://github.com/EndlessSora/DeeperForensics-1.0) | 2020 | video | 40,352 | 11,000 | 51,352 | 100 | 11, listed below | — | `official` | No |
| [DeepFakeDetection](https://github.com/ondyari/FaceForensics) | — | video | 363 | 3,068 | 3,431 | 28 | 1: deepfakedetection | raw, c23, c40 | `ident-72-14-14` | No |
| [DeepSpeak v1](https://huggingface.co/datasets/faridlab/deepspeak_v1_1) | 2026 | audio-visual | 6,667 | 6,796 | 13,463 | 220 | 5: facefusion, facefusion\_gan, facefusion\_live, retalking, wav2lip | — | `official+ident-80-20` | No |
| [DeepSpeak v2](https://huggingface.co/datasets/faridlab/deepspeak_v2) | 2026 | audio-visual | 9,376 | 7,209 | 16,585 | 280 | 6, listed below | — | `official+ident-80-20` | No |
| [DFDC](https://ai.meta.com/datasets/dfdc/) | 2020 | video | 2,500 | 2,500 | 5,000 | — | 1: deepfake | — | `official` | No |
| DFDC Preview | 2019 | video | 1,131 | 4,119 | 5,250 | 68 | 2: method\_a, method\_b | — | `official+ident-80-20` | No |
| [DFDM](https://github.com/shanface33/Deepfake_Model_Attribution) | 2022 | video | 590 | 2,150 | 2,740 | 59 | 5: DFaker, DFL-H128, FaceSwap, IAE, LightWeight | c0, c10, c23 (fakes only) | `ident-72-14-14` | No |
| [FaceForensics++](https://github.com/ondyari/FaceForensics) | 2019 | video | 1,000 | 5,000 | 6,000 | — | 5: Deepfakes, Face2Face, FaceShifter, FaceSwap, NeuralTextures | raw, c23, c40 | `official` | No |
| [FakeAVCeleb](https://github.com/DASH-Lab/FakeAVCeleb) | 2021 | audio-visual | 1,000 | 20,544 | 21,544 | 500 | 5: faceswap, faceswap-wav2lip, fsgan, fsgan-wav2lip, wav2lip | — | `ident-72-14-14` | No |
| [FFIW-10K](https://github.com/tfzhou/FFIW) | 2021 | video | 9,988 | 9,988 | 19,976 | — | 1: unknown | — | `official` | No |
| [IDForge](https://github.com/xyyandxyy/IDForge) | 2024 | audio-visual | 120,000 | 130,000 | 250,000 | 54 | 7, listed below | — | `official` | No |
| [KoDF](https://github.com/deepbrainai-research/kodf) | 2021 | video | 62,164 | 175,660 | 237,824 | 403 | 5: audio-driven, dffs, dfl, fo, fsgan | — | `ident-72-14-14` | No |
| [LAV-DF](https://github.com/ControlNet/LAV-DF) | 2022 | audio-visual | 69,601 | 66,703 | 136,304 | — | 2: FakeVideo-FakeAudio, FakeVideo-RealAudio | — | `official` | No |
| [PolyGlotFake](https://github.com/tobuta/PolyGlotFake) | 2024 | audio-visual | 762 | 13,605 | 14,367 | — | 1: lip\_sync | — | `ident-72-14-14` | No |
| [TalkingHeadBench](https://huggingface.co/datasets/luchaoqi/TalkingHeadBench) | 2025 | audio-visual | 2,608 | 2,994 | 5,602 | — | 8, listed below | — | `official` | No |
| [UADFV](https://docs.google.com/forms/d/e/1FAIpQLScKPoOv15TIZ9Mn0nGScIVgKRM9tFWOmjh9eHKx57Yp-XcnxA/viewform) | 2019 | video | 49 | 49 | 98 | — | 1: faceswap | — | `all-test` | No |
| [WildDeepfake](https://huggingface.co/datasets/xingjunm/WildDeepfake) | 2020 | video | 3,805 | 3,509 | 7,314 | — | 1: fake | — | `official+ident-80-20` | No |

- Real, Fake and Total count the videos each protocol lists in dfwb-protocols 0.1.0; a video at several compressions counts once. These are not the publishers' totals, and differ where the local release differs: DFDC's protocol, for one, lists only the public test set.
- Real and Fake follow each dataset's own `binary` label, which judges the video alone: a real video with fake audio counts as real.
- Year is that of the paper the dataset's card cites, which can be later than the release.
- Subjects count distinct people, shown only where every identity a dataset records is a person; — elsewhere.
- Manipulation methods count the distinct `method` labels of the fakes. Where a release does not say how each fake was made, one label covers them all.
- Rights cleared: No means DFWB does not yet publish these lists. Each dataset comes from its owner, under the owner's terms.

The manipulation methods of the datasets with more than five:

- **Celeb-DF v3** (22): AniTalker, BlendFace, Celeb-DF-v2, DaGAN, EchoMimic, EDTalk, FLOAT, FSRT, GHOST, HifiFace, HyperReenact, InSwapper, IP\_LAP, LIA, LivePortrait, MCNET, MobileFaceSwap, Real3DPortrait, SadTalker, SimSwap, TPSMM, UniFace
- **DeeperForensics-1.0** (11): E2E-Level-1, E2E-Level-2, E2E-Level-3, E2E-Level-4, E2E-Level-5, E2E-Mix-2, E2E-Mix-3, E2E-Mix-4, E2E-Random, End-to-End, Reenact-Post
- **DeepSpeak v2** (6): diff2lip, facefusion, hellomeme, latentsync, liveportrait, memo
- **IDForge** (7): face\_audiomismatch\_textmismatch, face\_rvc\_textmismatch, face\_tts, face\_tts\_textgen, lip\_audiomismatch\_textmismatch, lip\_rvc\_textmismatch, lip\_tts\_textgen
- **TalkingHeadBench** (8): AniPortraitAudio, AniPortraitVideo, EmoPortrait, Hallo, Hallo2, Hallo3, LivePortrait, MAGI-1
<!-- TABLES:END -->

### Cite this work

<!-- CITE:START -->
The deepfake-workbench and dfwb-protocols repositories each carry a `CITATION.cff`, so GitHub's "Cite this repository" button gives you the reference once the repository is public. Each dfwb-torch package carries its own `CITATION.cff`, in the package's folder.

If you found this work helpful, or used it in your research, please cite the following paper:

```bibtex
% BibTeX entry to follow on publication.
```
<!-- CITE:END -->

### Maintainer

<!-- PEOPLE:START -->
<a href="https://github.com/lukegcollins"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/maintainer-dark.svg"><img alt="Luke Collins, lead maintainer, Deakin University, ORCID 0009-0002-7771-1081." src="assets/maintainer-light.svg" width="400"></picture></a>

Contributions are welcome! Check out our [contributing guidelines](https://github.com/dfwb-research/.github/blob/main/CONTRIBUTING.md) to get started.
<!-- PEOPLE:END -->

### Acknowledgments

This work was supported by a [DUPR Scholarship](https://www.deakin.edu.au) and partially funded by [Dynamis Group](https://dynamisgroup.com.au). We also gratefully acknowledge the authors and contributors of the associated modules, packages, datasets, and detectors utilised in this research; we make no claims of ownership regarding these external resources.

<!-- STATUS:START -->
<p align="right"><samp>status verified 2026-09-25</samp></p>
<!-- STATUS:END -->
