# Claims

Supported claims: none.

Proof references: pending. C01 was created as an untested AI-suggested
hypothesis; no claim was advanced, weakened, or confirmed in this session.

## C01: H1 — invariant-aware validation improves synthetic calibration

- **Statement**: On the locked E001-v1 confirmatory split, the invariant-aware
  method M1 will outperform the schema-only baseline B0 under the protocol's
  pre-specified balanced-accuracy, false-positive-rate, and false-negative-rate
  rule.
- **Status**: untested
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
- **Proof**: [pending experimental evidence; `experiments/E001-synthetic-invariant-calibration/protocol.md` @ `d8b26d21e9692ace19436d78461460940043f5c7`]
- **Dependencies**: []
- **Tags**: E001-v1, H1, semantic/state-invariant-validation, FP/FN-calibration
