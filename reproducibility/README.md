# Portable evidence verification

This review bundle verifies the existing paper's frozen numerical evidence.
It uses Python's standard library, with no Git checkout, NumPy, TeX, network
access or machine-specific cache required. Extract the ZIP and run from any
working directory:

```sh
python3 /path/to/extracted/reproducibility/verify_evidence.py
```

The verifier checks the manifest's file hashes, rebuilds all four E005 audit
artifacts byte for byte from the original synthetic predictions/metrics, and
recomputes E006's 720 metric comparisons and 84 interval endpoints from delivered
rows. It checks calibration lookup serialization, prediction coverage and
reference-coordinate inventories. It does not overwrite experiment artifacts.
The scripts, not the original performance harnesses, are included for this
verification scope. A failed assertion or nonzero exit means verification failed.
Do not run with `python -O`, which disables assertions used by the historical audits.

Outside raw reference tables are excluded. The default output explicitly says
their bytes were **not checked**. To verify those too, obtain the nine files
listed in `data/E006-v1-source-manifest.json` from its exact revision-pinned URLs,
preserve their relative paths under a local directory, and run:

```sh
python3 /path/to/extracted/reproducibility/verify_evidence.py --source-root /path/to/raha-source
```

No acquisition occurs automatically. The historical manifest's absolute cache
path is provenance; this command uses the supplied directory instead. The nine
SHA-256 pins must all match. The files include the upstream LICENSE.md and reader.

The bundle is an evidence audit, not a full rerun of E001/E002/E006 or a new
performance experiment. Its hash manifest detects accidental drift; it is not
an independent signature or external validation. It cannot establish that
reference corrections are infallible, that the contribution is novel, or that
the manuscript has independent scientific acceptance. Study protocols and
historical outcome reports retain their original scope and dates.

`paper/arxiv-source-draft.zip` is the separate four-file TeX submission draft.
This larger evidence ZIP is for review/reproduction and is not an arXiv TeX
source upload. Both remain unpublished owner-review artifacts.
