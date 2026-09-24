# DFWB Research

**Open, reproducible tooling for deepfake detection research: datasets → protocols → training → evaluation.**

> The first releases are in preparation. The repositories below open with their v0.1 releases.

| | |
|---|---|
| **Deepfake Workbench** (`deepfake-workbench`) | The framework: verified dataset inventories, face preprocessing, training, scoring any detector, and evaluation with uncertainty and coverage reporting. One `dfwb` command. |
| **dfwb-protocols** | Versioned train/val/test protocols (splits and labels) for public deepfake datasets. CC BY 4.0, with a DOI. |
| **dfwb-torch** | Small, standalone PyTorch utilities for media forensics (starting with `dfwb-torch-srm`), usable with or without the framework. |

**Never media.** We publish identifiers, labels and splits only. You obtain each dataset from its
owner, under its own terms.

Maintained by **Luke Collins**, Deakin University
([@lukegcollins](https://github.com/lukegcollins), ORCID
[0009-0002-7771-1081](https://orcid.org/0009-0002-7771-1081)). Contributions are welcome; see
[CONTRIBUTING](https://github.com/dfwb-research/.github/blob/main/CONTRIBUTING.md). If this work
helps yours, please consider citing it: each repository has a `CITATION.cff`.
