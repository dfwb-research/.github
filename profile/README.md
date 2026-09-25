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

**Reproducible by default.** Inventories are checked against sha256, splits are versioned, runs are seed-locked, and results carry confidence intervals. [RESPONSIBLE_USE.md](https://github.com/dfwb-research/.github/blob/main/RESPONSIBLE_USE.md) covers the rest.

### Datasets and detectors

<!-- TABLES:START -->
| Dataset | Modality | Protocol | Owner's terms | Status |
|---|---|---|---|---|
| AV-Deepfake1M++ | audio-visual | v0.1.0 | [terms](https://github.com/ControlNet/AV-Deepfake1M/blob/master/eula.pdf) | in preparation |
| Celeb-DF v1 | video | v0.1.0 | [terms](https://github.com/yuezunli/celeb-deepfakeforensics) | in preparation |
| Celeb-DF v2 | video | v0.1.0 | [terms](https://github.com/yuezunli/celeb-deepfakeforensics) | in preparation |
| Celeb-DF v3 | video | v0.1.0 | [terms](https://github.com/OUC-VAS/Celeb-DF-PP) | in preparation |
| DeeperForensics-1.0 | video | v0.1.0 | [terms](https://github.com/EndlessSora/DeeperForensics-1.0/raw/master/dataset/Terms_of_Use.pdf) | in preparation |
| DeepFakeDetection | video | v0.1.0 | [terms](https://github.com/ondyari/FaceForensics) | in preparation |
| DeepSpeak v1 | audio-visual | v0.1.0 | [terms](https://huggingface.co/datasets/faridlab/deepspeak_v1) | in preparation |
| DeepSpeak v2 | audio-visual | v0.1.0 | [terms](https://huggingface.co/datasets/faridlab/deepspeak_v2) | in preparation |
| DFDC | video | v0.1.0 | [terms](https://www.kaggle.com/c/deepfake-detection-challenge/rules) | in preparation |
| DFDC Preview | video | v0.1.0 | [terms](https://deepfakedetectionchallenge.ai) | in preparation |
| DFDM | video | v0.1.0 | [terms](https://github.com/shanface33/Deepfake_Model_Attribution) | in preparation |
| FaceForensics++ | video | v0.1.0 | [terms](https://github.com/ondyari/FaceForensics) | in preparation |
| FakeAVCeleb | audio-visual | v0.1.0 | [terms](https://sites.google.com/view/fakeavcelebdash-lab/license) | in preparation |
| FFIW-10K | video | v0.1.0 | [terms](https://github.com/tfzhou/FFIW) | in preparation |
| IDForge | audio-visual | v0.1.0 | [terms](https://github.com/xyyandxyy/IDForge) | in preparation |
| KoDF | video | v0.1.0 | [terms](https://github.com/deepbrainai-research/kodf) | in preparation |
| LAV-DF | audio-visual | v0.1.0 | [terms](https://github.com/ControlNet/LAV-DF/blob/master/TERMS_AND_CONDITIONS.md) | in preparation |
| PolyGlotFake | audio-visual | v0.1.0 | [terms](https://github.com/tobuta/PolyGlotFake) | in preparation |
| TalkingHeadBench | audio-visual | v0.1.0 | [terms](https://huggingface.co/datasets/luchaoqi/TalkingHeadBench) | in preparation |
| WildDeepfake | video | v0.1.0 | [terms](https://github.com/xingjunm/wild-deepfake) | in preparation |
<!-- TABLES:END -->

### Cite this work

<!-- CITE:START -->
Each package repository carries a `CITATION.cff`, so GitHub's "Cite this repository" button gives you the reference once the repository is public.

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
