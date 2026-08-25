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

The M04-authorized locked local confirmatory command was:

```text
PYTHONDONTWRITEBYTECODE=1 python experiments/E002-heterogeneous-specification-stress/code/run_e002.py --run-id e002-20260825-001 --output-root .
```

The development suite currently contains 54 tests. Its ordinary fixtures
score, calibrate, and reduced-bootstrap only development and calibration
cases; confirmatory counts are checked as locked arithmetic. The added
deterministic in-memory validator regression reconstructs only the development
and calibration population/prediction evidence and performs a reduced
bootstrap on those splits to compare exact producer and validator values.
Confirmatory report/H2 coverage is structural arithmetic only, with exact-delta
calls stubbed to the fabricated locked rows; it does not evaluate confirmatory
scores, compute confirmatory metric rows from cases, or bootstrap confirmatory
cases. The regression does not invoke `execute_run` or the CLI and produces no
confirmatory repository artifacts; separate runner tests use fake artifacts in
temporary directories for staging and fail-closed behavior.

One authorized locked attempt, `e002-20260825-001`, was executed after the
M04 gate. It failed closed with exit code 2 because of
`result semantic field drift: D9_OR_NA`. The only preserved output is the
[invalid run report](../results/run-e002-20260825-001.md), with SHA-256
`f441d55795b81d280e35b09980dcb6f79e58e7cfacbe9886ed094a207580aa34`; no
data, metrics, or evidence outputs were produced. See the [M05 invalid-run
record](../../../milestones/M05-E002-run-001-invalid.md). No corrected run
has been executed or authorized, and this invalid attempt establishes no
scientific result, metric, H2 outcome, or public claim.

The runner validates every staged byte before publication, reports the
finalized result SHA-256 externally, and emits multi-fault relation evidence
only after a valid run.
