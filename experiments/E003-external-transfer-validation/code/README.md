# E003-v1 implementation

This directory contains the standard-library-only E003-v1 source adapter,
independent reference oracle, validators, calibration, exact metrics,
repository-cluster bootstrap, canonical serializers, and staged future-run
CLI. Imports are side-effect free.

Run the development suite from the repository root:

```text
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover \
  -s experiments/E003-external-transfer-validation/code -p 'test_e003.py' -v
```

The suite uses synthetic fixtures for boundary and runner tests. Its only real
source integration is the 2019 development and 2020 calibration preflight,
which proves the exact 64 IssuesEvent + 64 PullRequestEvent bases and 512 cases
per split, fits the four calibration lookups, and checks deterministic
canonical projection. A byte-read guard fails if the 2021 confirmatory gzip is
requested; no confirmatory metrics, predictions, bootstrap, or result are
constructed by development tests.

The future CLI is explicit and is not run by this suite:

```text
python experiments/E003-external-transfer-validation/code/run_e003.py \
  --run-id e003-YYYYMMDD-NNN \
  --output-root . \
  --source-manifest /private/tmp/invariant-audit-e003-v1/source-manifest.json
```

It requires the external manifest, verifies all frozen gzip-byte hashes before
the core pipeline parses source records, checks the locked protocol and clean
tree, refuses any existing E003 output, builds the complete in-memory pipeline
twice, enforces the size and artifact gates, and publishes through exclusive
atomic staging with the result document last. A post-staging failure removes
runner-owned files and leaves only the exact concise invalid-run record; there
is no retry or output overwrite path.

The implementation does not reserve a run ID, create a production E003 output,
or establish an E003 result. Raw sources and the acquisition manifest remain
outside Git.

## M12 implementation evidence

The guarded development/calibration preflight selected exactly 64
`IssuesEvent` and 64 `PullRequestEvent` bases in each split, producing 512
cases per split. Selected repository counts were development `103` and
calibration `92`; `2,178` cross-split repository IDs were excluded before
selection, `5,408`/`9,435` eligible events remained, and the selected
repository intersection was empty. The combined scoring pass had `5,120` raw
method rows and fitted calibration only from calibration rows.

The manifest hash was
`683eef39cd26d2a7f6622689adc2cd9e357e78a770f77bf91e98513b859e4633`. The
lookup byte hashes were `B0=2d5d789ed71d73772e62c29eebdce252eee0e6dfe46965ceec676de424463058`,
`M1=02b1d8bddcb941bde65c59499e1799ee559abc9f62ef42755850ab11b5c0c6a2`,
`M1-no-identity=370cd8fa7f24bffe5c72a41e8a1e2f5f93e68f2bba88cb88518a475e89c573d5`,
and `M1-no-state=0e786b395a7af8913bdb8fcb2b02957448f94ed9587a471759a73c3f0623e98b`.
Two independent preflight builds matched in all recorded fields, lookup bytes,
and lookup hashes. The byte-read guard observed only the 2019 and 2020 gzip
basenames; any 2021 request raises. These are implementation checks, not
confirmatory evidence.
