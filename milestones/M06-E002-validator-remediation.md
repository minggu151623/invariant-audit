# M06 — E002 validator remediation and independent-review gate

Status: implementation remediation is complete and independently reviewed; the
M05 run remains invalid; no corrected run is authorized.

## Scope and provenance

M06 closes the implementation-remediation gate raised by the invalid
M04-authorized run. M04 remains the historical implementation-review and
one-run authorization record. M05 remains the historical invalid-run evidence
record. This milestone records remediation and review evidence only; it is not
an E002 scientific result.

The M05 invalid-run record is in commit
`9d8019023082e8125ecb88808408ebb3d40d41d7`. The remediation is in commit
`e090fa76be67a3cb1d52517bd93327ef821b8e75`, whose parent is the M05 commit,
with subject `research(impl): fix E002 exact delta validation`.

Technical implementation choices and the diagnosis below are worker/reviewer
verification work, not user-selected technical design. No new user authority
for a corrected run is inferred by this documentary gate.

## Locked protocol and preserved invalid evidence

- Protocol lock commit:
  `9e39c5defc89f2c2a896b53dda529f326e9dfcf8`.
- Locked protocol blob:
  `f7d27a069ee3fd1600f89d9271e107c197033238`.
- Protocol status: unchanged and byte-identical to the locked blob.
- Invalid run: `e002-20260825-001`, exit code `2`, failure
  `result semantic field drift: D9_OR_NA`.
- Preserved invalid report:
  [run-e002-20260825-001.md](../experiments/E002-heterogeneous-specification-stress/results/run-e002-20260825-001.md)
- Invalid report SHA-256:
  `f441d55795b81d280e35b09980dcb6f79e58e7cfacbe9886ed094a207580aa34`.
- No data, metrics, or evidence outputs exist. The invalid run is not a
  scientific outcome and does not establish an H2 result, external validity,
  novelty, safety, generalization, or public claim.

## Independent diagnosis and remediation

The first mismatch was `D9_OR_NA` at zero-based index `13`, on result line
`38`, `Delta M1-B0 Brier`. The producer value was `-0.091689527`, computed
from exact fractions. The validator value was `-0.091689526`, obtained by
subtracting rounded metric-cell strings. The locked protocol requires exact
arithmetic until serialization. The classification is an implementation
defect, not a scientific outcome.

The remediation commit recomputes validator overall and cluster deltas from
independently reconstructed exact `Fraction` statistics rather than from
rounded D9 metric-row strings. Those exact deltas propagate through D9, H2,
and the guardrail checks. The regression renders a producer-style result and
then validates it through the independent validator path; it is deterministic,
development-sized, in-memory, and does not execute `execute_run` or the CLI.

## Verification evidence

### Implementer evidence

- The targeted producer-style regression failed before the patch with
  `result semantic field drift: D9_OR_NA` and passed after the patch.
- The standard-library-only development command
  `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s experiments/E002-heterogeneous-specification-stress/code -p 'test_e002.py'`
  passed with **54 tests**, `OK`.
- These are worker implementation/test claims. They establish validator
  remediation behavior only, not confirmatory evidence.

### Independent reviewer evidence

- The independent reviewer’s targeted checks passed **3/3**.
- Static, diff, and hash review passed; the protocol blob and preserved invalid
  report hashes were unchanged.
- The review initially returned **HOLD** solely for stale README test-count
  text. After the README was corrected to 54 tests, re-review returned
  **ACCEPT** with no remaining findings.

These are reviewer checks, kept distinct from the implementer’s test claims
and from repository artifacts.

## Current state and next gate

M06 is the current milestone. The M04 one-run authorization was consumed by
the M05 invalid execution. The current E002 state is:

- `implementation_remediation: complete`
- `implementation_reviewed: true`
- `run_authorized: false`
- `corrected_run_authorized: false`
- `authorization_consumed: true` for the prior M04 authorization
- `run: invalid` for `e002-20260825-001`
- `results: invalid_report_only`
- `data: absent`
- `metrics: absent`
- `evidence: absent`
- `public_claim_eligibility: false`

Any corrected run requires a new run ID and separate explicit authorization.
This gate does not authorize or execute a corrected run. Until such a run is
separately authorized and validly recorded, no E002 metric, H2 outcome,
external-validity, novelty, safety, generalization, or public claim exists.
