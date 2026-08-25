# E002-v1 implementation

This directory contains the standard-library-only E002 heterogeneous
specification-stress harness.  `e002.py` is side-effect free on import and
contains the deterministic generator, independent reference oracle, evaluated
checkers, calibration, metrics, bootstrap, canonical serializers, and
in-memory gates.  `run_e002.py` performs the locked protocol/clean-tree gate
before staging and publishing the four future artifacts, with the result
Markdown finalized last.

The implementation chain is `42cb62374c2b94ad6c567232acdac6d7365a9d8f`
(initial implementation), `6df4f3bc02f5f12feb243df21ec9eeaafd53d8fc`
(result-validator hardening), and
`0977641f129d172dd4d11136197a82cb17654aeb` (independent-review remediation).
The implementation review is recorded in
`milestones/M04-E002-implementation-review.md`.

Run the development suite from the repository root:

```text
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s experiments/E002-heterogeneous-specification-stress/code -p 'test_e002.py'
```

The next locked local confirmatory command, invoked only under the M04
authorization and a clean-tree preflight, is:

```text
PYTHONDONTWRITEBYTECODE=1 python experiments/E002-heterogeneous-specification-stress/code/run_e002.py --run-id e002-20260825-001 --output-root .
```

No confirmatory run has been executed. The tests use in-memory generated
cases and temporary directories only; they do not create E002 repository data,
metrics, bootstrap, or result outputs. The 53-test development suite
deliberately scores and bootstraps only development and calibration cases;
confirmatory counts are checked as locked arithmetic. The M04 gate authorizes
the next run but establishes no result, metric, H2 outcome, or public claim.
The runner validates every staged byte before publication, reports the
finalized result SHA-256 externally, and emits multi-fault relation evidence
only after a valid run.
