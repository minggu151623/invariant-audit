# Evidence Index

This index separates repository artifact facts, worker execution claims, and
independent-review checks. E001 and the valid M08 E002 artifacts are scientific
evidence only within their locked finite synthetic designs. M05 invalid-run,
M06/M07 remediation/readiness, and snapshot-audit entries remain process or
diagnostic evidence and are not scientific proof.

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

## C02 — E002 finite synthetic evidence

The proof for [C02](../logic/claims.md) is the M08 corrected-run record and
the four artifacts committed by
`a60550753a1ea876a47514e67f866ae1332fd5a0`, under the locked E002-v1 protocol
commit `9e39c5defc89f2c2a896b53dda529f326e9dfcf8` and blob
`f7d27a069ee3fd1600f89d9271e107c197033238`:
[M08](../../milestones/M08-E002-run-002-valid.md) and the
[result report](../../experiments/E002-heterogeneous-specification-stress/results/run-e002-20260825-002.md).

| Artifact | Repository fact | SHA-256 |
| --- | --- | --- |
| [Predictions](../../data/E002-v1-predictions.jsonl) | 7,296 rows; 6,556,304 B | `bcb34aad4338fdfbffe07be1843769b360bf4e8c422d855a9ce605350fad13b7` |
| [Metrics](../../data/E002-v1-metrics.csv) | 243 rows plus header; 116,260 B | `f000348d385550745480066fce2d691686728ebe2bfcf7bd96e7231e4b1e5ca3` |
| [Bootstrap](../../data/E002-v1-bootstrap.csv) | 530,053 rows plus header; 30,814,607 B | `8c5919f709c9ad8ca673308053ecefbe94ca23b0c190b923f14957cbfeac7d5d` |
| [Result](../../experiments/E002-heterogeneous-specification-stress/results/run-e002-20260825-002.md) | valid run `e002-20260825-002`; 6,486 B; 100 lines | `d1f11d17be3b91d246126dc36b88880a76f039f31fa7eeef63d5aff4cfe713fa` |

The primary M1-minus-B0 deltas are BA `0.401960784`, FPR `-0.803921569`,
FNR `0`, Brier `-0.091689527`, and ECE `0.005222762`. H2 is `supported`,
the FNR guardrail passes at delta `0`, and runner multi-fault relation
evidence is `equals=272`, `contains=160`, `differs=0`. This supports C02 only
for the finite synthetic E002-v1 construction and does not establish
production, external validity, generalization, novelty, safety, or public
eligibility; `public_claim_eligibility` is `false`.

## E002 — process and diagnostic evidence

- Locked E002-v1 protocol:
  [protocol](../../experiments/E002-heterogeneous-specification-stress/protocol.md),
  commit `9e39c5defc89f2c2a896b53dda529f326e9dfcf8`, blob
  `f7d27a069ee3fd1600f89d9271e107c197033238`.
- [M05 invalid-run record](../../milestones/M05-E002-run-001-invalid.md) and
  [M06 remediation gate](../../milestones/M06-E002-validator-remediation.md)
  are documentary process/review records.
- [M07 corrected-run technical-readiness gate](../../milestones/M07-E002-corrected-run-readiness.md)
  records the historical technical-ready/auth-hold state before run 002.
- The final development-test-boundary remediation commit
  `1fe42a7ebc6a9ce69d8a16654e068c0a9a891d08` and M07 documentary commit
  `cf410dc5d36af3bb2c6b2dd5c60ecc44c1361e78` are process/readiness evidence
  only. Neither commit is proof of E002 H2, metrics, or a scientific result.
- The preserved invalid-run output is the [invalid report](../../experiments/E002-heterogeneous-specification-stress/results/run-e002-20260825-001.md),
  SHA-256
  `f441d55795b81d280e35b09980dcb6f79e58e7cfacbe9886ed094a207580aa34`.
  It records exit code `2`, `D9_OR_NA`, and no metrics, data, evidence, or
  H2 outcome.
- The M08 snapshot audit independently parsed the committed result/artifact
  hashes, counts, validity fields, and gate fields and recorded ACCEPT with no
  P0-P3 findings; reviewer runner invocations were `0`. Timestamp, runtime,
  exactly-once execution, and two-build byte equivalence are retained as
  documentary provenance from the snapshot, not independently reconstructible
  facts of this audit.

Run 001 remains diagnostic-only and is not converted into C02 proof. M06/M07
remediation and readiness records remain process evidence; M08 is the bounded
finite-synthetic result record. No E002 public claim or push/publication is
authorized.
