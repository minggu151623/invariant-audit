# Paper outline and claim-evidence map

Corrected 2026-09-17. The previous outline's universal guarantees, at-least-once
causal claim, isotonic-method description, and self-approved review are withdrawn.
The paper remains preliminary; public_claim_eligibility=false.

## Outline

1. Question, positive=valid convention, and bounded B0/M1 comparison.
2. Synthetic designs, Laplace-smoothed lookup, primary and secondary metrics.
3. Valid E001/E002 results, source numbers, ablations and uncertainty limits.
4. E003 source-gate invalidation and missing external performance evidence.
5. Remaining source-policy, calibration, and external-transfer questions.

## Evidence map

| Claim | Evidence | Status and scope |
| --- | --- | --- |
| M1 improves the locked BA/FPR/FNR rule in E001 | E001 result, M02 | Supported in that finite synthetic design only |
| M1 improves the E002 anchor and stress diagnostics pass | E002 run 002, M08 | Supported in that finite synthetic design only |
| Probability calibration generally improves | Brier falls but ECE rises in both reports; E001 binary ablation is already perfect | Not established |
| Confidence mapping uses isotonic regression | E001/E002/E003 protocol formulas | Incorrect; Laplace-smoothed empirical lookup |
| E003 established external performance | M13 and invalid report | Incorrect; no H3 outcome or performance metrics |
| The recovered 2021 shard has 537 byte-identical extra occurrences and no conflicting ID groups | E004 run e004-20260917-001, M15 | Exploratory source diagnostic only, not performance validation |
| At-least-once delivery/retries caused duplicates | No supporting causal evidence in repository | Hypothesis only |
| Harness guarantees absence of contamination or general reproducibility | Tests, hashes and recorded gates | No universal guarantee; bounded process checks |

## Review obligations

Check every numeric table against its immutable result artifact, distinguish
percentage points from relative percentage changes, and preserve positive=valid
terminology. Do not interpret lower Brier alone as better calibration. Keep
source diagnostics distinct from valid external performance evaluation.
Independent manuscript review and E003 implementation re-review remain open.
