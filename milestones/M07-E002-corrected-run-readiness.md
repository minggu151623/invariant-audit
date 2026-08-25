# M07 — E002 corrected-run technical-readiness gate

Status: technical readiness is accepted subject to the locked runtime
preflight; the corrected run is not authorized, reserved, or executed.

## Scope and provenance

This milestone records a documentary, read-only technical-readiness audit for
candidate run `e002-20260825-002`. The audit began from the ARA epilogue HEAD
`70d47de1af70d380437876effe082adcfb1a70a3`. The worker’s initial read-only
readiness conclusion was **technical PASS**. This record does not infer user
authority for a corrected run, select technical design, authorize publication
or a public claim, or establish an E002 result.

The independent review then found a **P1 HOLD**: the new development
regression and canonical-report call paths still computed confirmatory
statistics, contrary to `protocol.md:1164`, which limits development tests to
development/calibration splits and prohibits confirmatory metrics. It also
recorded a **P3 HOLD** for stale documentation. The first refactor moved the
exact-versus-rounded counterexample to development/calibration data, but
independent re-review correctly held because the canonical structural report
still executed the real confirmatory `_validator_primary_deltas` before and
under a wraps spy.

The final remediation is repository commit
`1fe42a7ebc6a9ce69d8a16654e068c0a9a891d08`, parent
`70d47de1af70d380437876effe082adcfb1a70a3`, subject
`research(impl): enforce E002 development test boundary`. It contains exactly
the three reviewed code paths: [code README](../experiments/E002-heterogeneous-specification-stress/code/README.md),
[runner](../experiments/E002-heterogeneous-specification-stress/code/run_e002.py),
and [development tests](../experiments/E002-heterogeneous-specification-stress/code/test_e002.py).

## Preserved protocol, implementation, and invalid-run evidence

- Locked protocol: [E002-v1](../experiments/E002-heterogeneous-specification-stress/protocol.md).
- Protocol lock commit: `9e39c5defc89f2c2a896b53dda529f326e9dfcf8`.
- Locked protocol blob: `f7d27a069ee3fd1600f89d9271e107c197033238`; unchanged.
- Implementation chain:
  `42cb62374c2b94ad6c567232acdac6d7365a9d8f` (initial implementation),
  `6df4f3bc02f5f12feb243df21ec9eeaafd53d8fc` (result-validator hardening),
  `0977641f129d172dd4d11136197a82cb17654aeb` (independent-review
  remediation), and the final boundary remediation commit above.
- Preserved invalid report:
  [run-e002-20260825-001.md](../experiments/E002-heterogeneous-specification-stress/results/run-e002-20260825-001.md),
  SHA-256 `f441d55795b81d280e35b09980dcb6f79e58e7cfacbe9886ed094a207580aa34`.
- Run `e002-20260825-001` remains invalid only: exit code `2`,
  `D9_OR_NA`, no metrics/data/evidence, and no H2 or scientific outcome.

M04 remains the historical implementation-review and one-run authorization
record; M05 remains the invalid-run record; M06 remains the validator-
remediation and independent-review record. The prior M04 authorization is
consumed, and any corrected run requires a new ID and separate explicit
authorization.

## Boundary remediation and verification

The final design separates structural report validation from dynamic
development evidence:

- `_validator_primary_deltas` now requires a `split` keyword. Production H2
  and report paths pass `split="confirmatory"` explicitly.
- The canonical structural report test installs a deterministic side-effect
  stub before report generation and keeps it active through every validation
  and mutation call. The stub asserts `split="confirmatory"` and returns exact
  deltas matching the fabricated primary/cluster rows. A blocking
  `_validator_stats` patch proves that real confirmatory statistics cannot run
  on that path.
- The development/calibration regression is the only dynamic exact-statistics
  and metric/bootstrap counterexample. It retains the exact serialized tokens
  `-0.091689527` versus rounded-cell subtraction `-0.091689526`.
- README and test-module documentation now describe the development-test
  boundary truthfully. Structural labels, counts, templates, and fabricated
  rows remain structural fixtures; no confirmatory scoring or bootstrap is
  executed by the development evidence path.

Worker verification recorded targeted checks `2/2` passed and the full
standard-library-only development suite `54/54 OK`. The independent reviewer
statically traced the call paths and ran the two targeted checks, returning
**TECHNICAL READINESS ACCEPT** with no findings. The reviewer did not run the
full suite because its runner tests were outside the reviewer’s read-only
scope. These worker and reviewer claims are kept distinct from repository
artifacts and from experimental evidence.

## Corrected-run readiness audit

The read-only audit recorded the following non-authorizing technical gates:

| Gate | Evidence | Status |
| --- | --- | --- |
| Candidate run ID | `e002-20260825-002` conforms to the locked E002 run-ID grammar. | PASS |
| Candidate final/shared outputs | The three shared data paths and candidate result path were absent: `data/E002-v1-predictions.jsonl`, `data/E002-v1-metrics.csv`, `data/E002-v1-bootstrap.csv`, and `experiments/E002-heterogeneous-specification-stress/results/run-e002-20260825-002.md`. | PASS |
| Staging/temp/lock collision | No E002 staging, temporary, or lock paths were present. | PASS |
| Repository assumptions | Working directory and output-root assumption were the repository root. | PASS |
| Runtime and disk | CPython/Python `3.14.5`; approximately `18 GiB` local free space. Both were nonblocking at audit time. | PASS |
| Protocol identity | Protocol commit `9e39c5defc89f2c2a896b53dda529f326e9dfcf8` was valid ancestry and its working blob matched `f7d27a069ee3fd1600f89d9271e107c197033238`. | PASS |
| Prior invalid evidence | Run 001’s invalid report was preserved with the hash above. | PASS |

The exact intended command is recorded for a future separately authorized
execution only; it was not authorized or executed by M07:

```text
PYTHONDONTWRITEBYTECODE=1 python experiments/E002-heterogeneous-specification-stress/code/run_e002.py --run-id e002-20260825-002 --output-root .
```

## M07 state and boundary

M07 sets the documentary state to:

- `technical_ready: true`, subject to the locked runtime preflight;
- `implementation_reviewed: true`;
- `corrected_run_authorized: false`;
- prior M04 authorization: consumed;
- `run: invalid` only for `e002-20260825-001`;
- candidate `e002-20260825-002`: not executed, not reserved, output absent;
- metrics, data, evidence, and H2 outcome: absent;
- `public_claim_eligibility: false`.

No corrected run, result recording, publication, push, or public claim is
authorized by this gate. The protocol, code, existing invalid report, data,
ARA artifacts, and experimental outputs are not changed by this documentary
record.
