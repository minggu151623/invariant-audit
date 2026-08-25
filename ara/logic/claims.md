# Claims

Supported claims: C01, strictly within the locked finite synthetic E001-v1
design.

The E002 H2 claim C02 is supported only within the locked finite synthetic
E002-v1 design; neither claim establishes production, external-validity,
generalization, novelty, safety, or public evidence.

## C01: H1 — invariant-aware validation improves synthetic calibration

- **Statement**: On the locked E001-v1 confirmatory split, the invariant-aware
  method M1 outperforms the schema-only baseline B0 under the protocol's
  pre-specified balanced-accuracy, false-positive-rate, and false-negative-rate
  rule.
- **Status**: supported, strictly within the finite synthetic E001-v1 design
- **Provenance**: ai-suggested
- **Falsification criteria**: H1 is not supported, and the outcome is labeled
  mixed/not supported, if the confirmatory M1-B0 balanced-accuracy 95% CI is
  not entirely greater than 0, or the M1-B0 FPR 95% CI is not entirely less
  than 0, or the M1-B0 FNR point estimate is greater than 0.
- **Support rule**: Support H1 only when the balanced-accuracy M1-B0 95% CI
  is entirely > 0, the FPR M1-B0 95% CI is entirely < 0, and the confirmatory
  FNR point difference M1-B0 is <= 0; otherwise label the outcome
  mixed/not supported. Secondary metrics remain reportable but do not change
  this support rule.
- **Observed primary deltas (M1 minus B0)**: balanced accuracy `+0.5`, FPR
  `-1`, FNR `0`; Brier `-0.2499408284`; ECE `+0.007692307692`.
- **Proof**: [M02 result record](../../milestones/M02-E001-results.md) and the
  [published E001 result](../../experiments/E001-synthetic-invariant-calibration/results/run-e001-20260825-001.md)
  with the published predictions, metrics, and bootstrap artifacts bound in
  the [evidence index](../evidence/README.md).
- **Dependencies**: []
- **Limitations**: finite, hand-designed, balanced, synthetic, single-fault,
  recipe-coupled oracle; no production validity, external validity,
  generalization, novelty, safety, or public claim. `public_claim_eligibility`
  is `false`.
- **Tags**: E001-v1, H1, semantic/state-invariant-validation, FP/FN-calibration,
  finite-synthetic-only

## C02: H2 — heterogeneous specification stress improves without guardrail failure

- **Statement**: On the locked E002-v1 confirmatory split, M1 will improve
  balanced accuracy and reduce false-positive rate relative to B0 without
  worsening the false-negative rate, while the predeclared specification
  stress diagnostics pass the locked H2 rule.
- **Status**: supported, strictly within the finite synthetic E002-v1 design
- **Observed result boundary**: One valid locked local confirmatory run,
  `e002-20260825-002`, returned H2 `supported` with the FNR guardrail passing.
  The primary M1-minus-B0 deltas were BA `0.401960784`, FPR `-0.803921569`,
  FNR `0.000000000`, Brier `-0.091689527`, and ECE `0.005222762`; the
  co-primary stress diagnostics passed. This is an AI-executed observation
  under the finite synthetic protocol, not a user-selected technical result.
- **Provenance**: ai-suggested
- **Falsification criteria**: Any failed required anchor interval/point,
  undefined required denominator, failed stress diagnostic, or mixed/not
  supported result under the locked E002 protocol falsifies H2 for this finite
  design.
- **Proof**: [M08 corrected-run record](../../milestones/M08-E002-run-002-valid.md),
  [committed result](../../experiments/E002-heterogeneous-specification-stress/results/run-e002-20260825-002.md),
  and the committed predictions, metrics, and bootstrap hashes in the
  [evidence index](../evidence/README.md), all under the locked
  [E002-v1 protocol](../../experiments/E002-heterogeneous-specification-stress/protocol.md)
  (commit `9e39c5defc89f2c2a896b53dda529f326e9dfcf8`, blob
  `f7d27a069ee3fd1600f89d9271e107c197033238`). Run 001 remains an invalid
  diagnostic-only record and is not part of this proof.
- **Dependencies**: [C01]
- **Limitations**: finite, synthetic, hand-specified oracle, bounded recipe
  inventory and cluster bootstrap; no production validity, external validity,
  generalization, novelty, safety, or public claim. `public_claim_eligibility`
  is `false`.
- **Tags**: E002-v1, H2, heterogeneous-clusters, specification-stress,
  finite-synthetic-only, supported
