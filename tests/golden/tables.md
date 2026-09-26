Of the 2 datasets, 1 is released and 1 is in preparation.

| Dataset | Year | Modality | Real | Fake | Total | Subjects | Manipulation methods | Compression variants | Default protocol | Rights cleared |
|---|---:|---|---:|---:|---:|---:|---|---|---|---|
| [Example-DF](https://example.org/df) | 2021 | audio-visual | 1,200 | 34,567 | 35,767 | 42 | 2: face\_swap, Lip-sync | raw, c23 (fakes only) | `official` | Yes |
| Wide-DF | — | video | 1 | 6 | 7 | — | 6, listed below | — | `all-test` | No |

- Real, Fake and Total count the videos each protocol lists in dfwb-protocols 1.0; a video at several compressions counts once. These are not the publishers' totals, and differ where the local release differs: DFDC's protocol, for one, lists only the public test set.
- Real and Fake follow each dataset's own `binary` label, which judges the video alone: a real video with fake audio counts as real.
- Year is that of the paper the dataset's card cites, which can be later than the release.
- Subjects count distinct people, shown only where every identity a dataset records is a person; — elsewhere.
- Manipulation methods count the distinct `method` labels of the fakes. Where a release does not say how each fake was made, one label covers them all.
- Rights cleared: No means DFWB does not yet publish these lists. Each dataset comes from its owner, under the owner's terms.

The manipulation methods of the datasets with more than five:

- **Wide-DF** (6): m0, m1, m2, m3, m4, m5

| Detector | Paper | Adapter | Weights licence |
|---|---|---|---|
| ExampleNet | [paper](https://doi.org/10.0000/x) | planned | MIT |
