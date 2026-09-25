# Responsible use

DFWB builds tools for detecting manipulated media and for measuring how well detectors work.
This page says how we expect them to be used. It is plain guidance, not legal advice, and it
doesn't replace the licences or the terms of any dataset.

## Dual use

Detection and generation research feed each other. A tool that shows where a detector fails
can also show someone how to get past it. We build for detection, evaluation and research, and
we ask you to do the same: please don't use DFWB to tune a generator until it slips past
detectors, or to help anyone deceive people with synthetic media.

## Datasets stay with their owners

DFWB never distributes media. Our protocols contain identifiers, labels and splits, nothing
more. Get each dataset from its owner, under the owner's terms, and follow those terms for as
long as you hold the data.

Never redistribute dataset media: not in issues, pull requests, discussions, releases, model
cards or example notebooks. If an example needs a face, use the synthetic `toyfake` data.

## Faces are personal information

Many deepfake datasets are made of real people's faces and voices. In Australia, as in many
other places, biometric information can be sensitive information under privacy law. Store it
securely, keep it only as long as your terms allow, and never try to identify, contact or
profile the people in it.

## A detector score is evidence, not a verdict

Detectors are probabilistic. They make mistakes, their scores drift with compression, resizing
and new generators, and a model that does well on a benchmark can do badly on your data.

- Never use a detector's output as the sole evidence in a decision about a person: at work, in
  court, in the news, or anywhere else it could hurt someone.
- Report uncertainty with every result. DFWB's evaluation gives confidence intervals and
  coverage for a reason.
- Test on data that looks like yours before trusting any number, including ours.

## Reporting misuse

If you see DFWB tools or protocols being misused, tell us privately through the contact in
[SECURITY.md](SECURITY.md). Please don't post the details publicly.
