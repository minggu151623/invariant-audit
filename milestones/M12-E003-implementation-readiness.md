# M12 — E003 implementation-readiness

Status: `implementation_ready_pending_independent_review`. This milestone
records implementation and development/calibration preflight evidence only. It
does not authorize, reserve, or execute an E003 confirmatory run and is not an
E003 result.

## Scope and provenance

The bounded continuation began from the green uncommitted E003 code slice at
the accepted acquisition HEAD `ca62f6e3cd9f10d7ed79b128b31d37caf974c573`.
The locked protocol remains
[E003-v1](../experiments/E003-external-transfer-validation/protocol.md),
locked at commit `163e44dcabc698f101dee70dd7f3aa1bb7c8d5fb`, with protocol blob
SHA-256
`8ec0ebc9b3420a2d71eebfe579ae2d1c87aa74c419dd3f38d1f0dc06c5c1e2a6`.
The implementation choices follow that locked protocol and are worker
implementation/verification work, not user-selected scientific design.

## Implementation paths

The standard-library/local-CPU implementation is contained in the scoped
[E003 code directory](../experiments/E003-external-transfer-validation/code/):

- [e003.py](../experiments/E003-external-transfer-validation/code/e003.py):
  deterministic source adapter, projection, selection, mutations, methods,
  calibration, exact metrics/bootstrap, schemas, hashes, and in-memory
  artifacts;
- [oracle_e003.py](../experiments/E003-external-transfer-validation/code/oracle_e003.py):
  separate fail-closed reference oracle;
- [run_e003.py](../experiments/E003-external-transfer-validation/code/run_e003.py):
  explicit future-run CLI with preflight, two-build, staging, and invalid-run
  guards; and
- [test_e003.py](../experiments/E003-external-transfer-validation/code/test_e003.py):
  synthetic boundary/runner tests and guarded development/calibration
  integration.

Imports are side-effect free. The runner was not invoked, no run ID was
reserved, and no production E003 path was created.

## Development/calibration-only integration evidence

Two independent guarded preflight builds used only the frozen 2019
development and 2020 calibration payloads. The byte-read guard observed exactly
`2019-01-15-12.json.gz` and `2020-01-15-12.json.gz`; requesting
`2021-01-15-12.json.gz` would have raised, and
`opened_confirmatory=false`.

| Check | Development | Calibration |
| --- | ---: | ---: |
| selected bases | 64 IssuesEvent + 64 PullRequestEvent | 64 IssuesEvent + 64 PullRequestEvent |
| cases | 512 | 512 |
| selected repositories | 103 | 92 |
| eligible events after split isolation | 5,408 | 9,435 |

There were 2,178 repository IDs shared by the two scanned source groups; they
were removed before selection. The selected repository intersection was zero.
The combined development/calibration scoring pass produced 5,120 raw method
rows. Calibration fitting used only the 2020 calibration rows.

The source manifest SHA-256 was
`683eef39cd26d2a7f6622689adc2cd9e357e78a770f77bf91e98513b859e4633`.
The calibration lookup serialized-byte hashes were:

| Method | SHA-256 |
| --- | --- |
| B0 | `2d5d789ed71d73772e62c29eebdce252eee0e6dfe46965ceec676de424463058` |
| M1 | `02b1d8bddcb941bde65c59499e1799ee559abc9f62ef42755850ab11b5c0c6a2` |
| M1-no-identity | `370cd8fa7f24bffe5c72a41e8a1e2f5f93e68f2bba88cb88518a475e89c573d5` |
| M1-no-state | `0e786b395a7af8913bdb8fcb2b02957448f94ed9587a471759a73c3f0623e98b` |

The projection signature SHA-256 was
`8adb4a38cbe92aed57d37c3e8e0812299e6dc57072434061427624ad6fda0f53`.
The two preflight builds were equal, including lookup bytes and hashes.
These are development/calibration implementation checks, not confirmatory
metrics or evidence.

## Verification and remediation

- `py_compile` passed for all four Python modules.
- `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s experiments/E003-external-transfer-validation/code -p 'test_*.py' -v` passed **25/25** in **18.574 seconds** (`OK`; 18.72 seconds wall time).
- The suite covers oracle separation, source projection/selection/isolation,
  exact mutation and method arithmetic, calibration isolation, metric `NA`
  behavior, bootstrap determinism, schemas/hashes, import side effects,
  output absence, atomic staging, and invalid-run cleanup.
- The initial diagnostic run had six failures (four failures and two errors).
  Two were real implementation defects: mixed-type cross-split exclusion
  bookkeeping and calibration callers passing development rows to the lookup
  fitter. Four were fixture/assertion mismatches: ablation expectations,
  missing synthetic pull-request bootstrap subgroup, a smoothed-calibration
  expected value, and temporary-directory cleanup. All were remediated in the
  scoped implementation/tests and the final suite passed. This remediation is
  not experiment evidence.

## Boundary and next gate

`implementation_ready_pending_independent_review` is the current state.
Confirmatory run, predictions, metrics, bootstrap, result report, and
production output paths are absent; `run_authorized: false`, `run: absent`,
`results: absent`, and `public_claim_eligibility: false` remain explicit.
The 2021 payload was not opened, selected, scored, or used in any metric or
bootstrap computation. Independent implementation review and separate explicit
authority are required before exactly one future confirmatory run.
