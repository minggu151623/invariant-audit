# M05 — E002 run 001 invalid evidence record

Status: the authorized local run is recorded as invalid; implementation
remediation is pending; no valid E002 result exists.

## Scope and provenance

M05 records the already-existing local execution of the M04-authorized E002
run. The run was executed once under the locked local command. This record is
documentary evidence of an invalid execution, not a scientific result.

The M04 authorization was bounded to one locked local execution and result
recording. It did not select technical design, authorize push or publication,
authorize a public claim, or establish an outcome. The implementation and the
diagnosis below remain worker/reviewer verification work, not user-selected
technical design.

## Locked protocol and implementation context

- Protocol: [E002-v1](../experiments/E002-heterogeneous-specification-stress/protocol.md)
- Protocol lock commit: `9e39c5defc89f2c2a896b53dda529f326e9dfcf8`
- Locked protocol blob: `f7d27a069ee3fd1600f89d9271e107c197033238`
- Protocol status: unchanged and byte-identical to the locked blob.
- M04 remains the historical implementation-review and one-run authorization
  record; M05 records the subsequent invalid execution.

The implementation chain remains:

1. `42cb62374c2b94ad6c567232acdac6d7365a9d8f` — initial implementation.
2. `6df4f3bc02f5f12feb243df21ec9eeaafd53d8fc` — result-validator hardening.
3. `0977641f129d172dd4d11136197a82cb17654aeb` — independent-review
   remediation.

## Observed invalid run

- Run ID: `e002-20260825-001`
- Exit code: `2`
- Runner failure: `result semantic field drift: D9_OR_NA`
- Invalid report: [run report](../experiments/E002-heterogeneous-specification-stress/results/run-e002-20260825-001.md)
- Invalid report SHA-256:
  `f441d55795b81d280e35b09980dcb6f79e58e7cfacbe9886ed094a207580aa34`
- Invalid report size: 258 bytes; 8 lines.
- Result status: `invalid`; failure class: `invalid-run`.
- No metrics, evidence, or data outputs exist.
- `corrected_run_requires_new_id: true`.

The invalid report records the protocol commit and run ID, states that no
metrics or evidence exist, and requires a new ID for any corrected run. No H2
outcome or scientific metric is established.

## Independent diagnosis

The independent implementation diagnosis is:

- First mismatch: `D9_OR_NA`, at zero-based index `13`.
- Result line: `38`, `Delta M1-B0 Brier`.
- Producer value: `-0.091689527`, computed from exact fractions.
- Validator value: `-0.091689526`, produced by subtracting rounded metric
  cells.
- The locked protocol requires exact arithmetic until serialization.
- Classification: implementation defect, not a scientific outcome.

This diagnosis explains the invalid-run gate failure. It does not convert the
partial computation into metrics, evidence, an H2 outcome, or any external,
novelty, safety, generalization, or public claim.

## Current state and next gate

M05 is the current milestone. The one-run authorization is consumed:

- `implementation_reviewed: true` (historical M04 evidence)
- `implementation_remediation_pending: true`
- `run_authorized: false`
- `authorization_consumed: true`
- `run: invalid` for `e002-20260825-001`, exit code `2`
- `results: invalid_report_only`
- `metrics: absent`
- `evidence: absent`
- `data: absent`
- `public_claim_eligibility: false`

The next gate is implementation remediation followed by independent review.
Any corrected local run requires a new run ID and separate authorization. No
corrected run is authorized by this record.
