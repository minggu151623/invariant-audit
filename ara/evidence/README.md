# Evidence Index

This index separates repository artifact facts, worker test claims, and
independent-review checks. E001 artifacts are scientific evidence only within
the locked finite synthetic design. E002 artifacts below are process or
diagnostic evidence and never scientific evidence.

## C01 — E001 finite synthetic evidence

The proof for [C01](../logic/claims.md) is the M02 result record and the
published E001-v1 artifact set:
[M02](../../milestones/M02-E001-results.md), protocol commit
`d8b26d21e9692ace19436d78461460940043f5c7`, and result commit
`31071ddf65ad9a1f0e5b28eb0d501899253cd17b`.

| Artifact | Repository fact | SHA-256 |
| --- | --- | --- |
| [Predictions](../../data/E001-v1-predictions.jsonl) | 5,120 rows; 2,966,528 B | `be5e5e2a6c3f33778a34af69d79ec4f14e3b2c0cba2f371ecc004310b7c9559a` |
| [Metrics](../../data/E001-v1-metrics.csv) | 75 rows plus header; 162,200 B | `ae7c32be651b5dfe175ca0537aa3cb8283acbd7063b14e15b8ec386f0d6a20cb` |
| [Bootstrap](../../data/E001-v1-bootstrap.csv) | 450,270 rows plus header; 32,920,126 B | `63b86d44f3425f0c2a43c53191d13ce614b0d0726ff1e941da98d11ee545ede5` |
| [Published result](../../experiments/E001-synthetic-invariant-calibration/results/run-e001-20260825-001.md) | valid run `e001-20260825-001`; 2,870 B; 60 lines | `cc00b21deabb88fd51c55090fc642a80424f960ad6b51c50f75818e8ffa485d6` |

The result reports primary M1-minus-B0 deltas of balanced accuracy `+0.5`,
FPR `-1`, FNR `0`, Brier `-0.2499408284`, and ECE `+0.007692307692`.
H1 is supported only within this finite, hand-designed, balanced, synthetic,
single-fault design. The oracle is recipe-coupled and
`public_claim_eligibility` is `false`.

## E002 — process and diagnostic evidence only

- Locked E002-v1 protocol:
  [protocol](../../experiments/E002-heterogeneous-specification-stress/protocol.md),
  commit `9e39c5defc89f2c2a896b53dda529f326e9dfcf8`, blob
  `f7d27a069ee3fd1600f89d9271e107c197033238`.
- [M05 invalid-run record](../../milestones/M05-E002-run-001-invalid.md) and
  [M06 remediation gate](../../milestones/M06-E002-validator-remediation.md)
  are documentary process/review records.
- The only E002 output is the preserved [invalid report](../../experiments/E002-heterogeneous-specification-stress/results/run-e002-20260825-001.md),
  SHA-256
  `f441d55795b81d280e35b09980dcb6f79e58e7cfacbe9886ed094a207580aa34`.
  It records exit code `2`, `D9_OR_NA`, and no metrics, data, evidence, or
  H2 outcome.

The E002 report and remediation checks must not be used as scientific proof.
The corrected run remains unauthorized and would require a new run ID and
separate explicit authorization.
