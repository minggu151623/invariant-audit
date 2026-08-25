# Claims

Supported claims: C01, strictly within the locked finite synthetic E001-v1
design.

Untested claims: C02, the AI-suggested E002 H2 question; no E002 scientific
evidence exists.

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
- **Status**: untested
- **Provenance**: ai-suggested
- **Falsification criteria**: Any failed required anchor interval/point,
  undefined required denominator, failed stress diagnostic, or mixed/not
  supported result under the locked E002 protocol falsifies H2 for this finite
  design.
- **Proof**: pending; [locked E002-v1 protocol](../../experiments/E002-heterogeneous-specification-stress/protocol.md)
  is design evidence only. The sole E002 attempt is an invalid diagnostic
  record and supplies no scientific proof.
- **Dependencies**: [C01]
- **Tags**: E002-v1, H2, heterogeneous-clusters, specification-stress,
  untested
