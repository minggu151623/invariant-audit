# E002-v1 implementation

This directory contains the standard-library-only E002 heterogeneous
specification-stress harness.  `e002.py` is side-effect free on import and
contains the deterministic generator, independent reference oracle, evaluated
checkers, calibration, metrics, bootstrap, canonical serializers, and
in-memory gates.  `run_e002.py` performs the locked protocol/clean-tree gate
before staging and publishing the four future artifacts, with the result
Markdown finalized last.

Run the development suite from the repository root:

```text
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s experiments/E002-heterogeneous-specification-stress/code -p 'test_e002.py'
```

The future confirmatory command, invoked only under the protocol's separate
authorization, is:

```text
PYTHONDONTWRITEBYTECODE=1 python experiments/E002-heterogeneous-specification-stress/code/run_e002.py --run-id e002-YYYYMMDD-NNN --output-root .
```

The confirmatory run was not executed in this implementation commit.  The
tests use in-memory generated cases and temporary directories only; they do
not create E002 repository data, metrics, bootstrap, or result outputs.  The
53-test development suite deliberately scores and bootstraps only development
and calibration cases; confirmatory counts are checked as locked arithmetic.
The runner validates every staged byte before publication, reports the
finalized result SHA-256 externally, and emits multi-fault relation evidence
only after a valid run.
