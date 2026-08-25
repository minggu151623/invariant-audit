# Heuristics

## H01: Reconstruct exact validator deltas from independent raw facts before serialization

- **Rationale**: A validator must recompute overall and cluster statistics and
  primary deltas from independently reconstructed exact raw facts and
  predictions. Subtracting rounded serialized metric cells can create a
  semantic mismatch, as shown by `-0.091689527` versus `-0.091689526`. Keep
  exact `Fraction` arithmetic through D9/H2/guardrail checks and round only at
  serialization.
- **Provenance**: ai-suggested
- **Sensitivity**: high
- **Code ref**: [run_e002.py](../../../experiments/E002-heterogeneous-specification-stress/code/run_e002.py),
  [test_e002.py](../../../experiments/E002-heterogeneous-specification-stress/code/test_e002.py)
- **Forensic basis**: [M05 invalid diagnosis](../../../milestones/M05-E002-run-001-invalid.md)
  and [M06 remediation review](../../../milestones/M06-E002-validator-remediation.md);
  this is an implementation heuristic, not a scientific result.

## H02: Body-block restricted computations in protocol-bound structural tests

- **Rationale**: A structural test must body-block restricted computations for
  its full report-generation and validation path, require explicit split
  parameters, and reserve dynamic exact-statistics counterexamples for
  development/calibration data. A wraps spy only observes calls and still
  executes the forbidden body, so it cannot enforce the development-test
  boundary by itself.
- **Provenance**: ai-suggested
- **Sensitivity**: high
- **Code ref**: [run_e002.py](../../../experiments/E002-heterogeneous-specification-stress/code/run_e002.py),
  [test_e002.py](../../../experiments/E002-heterogeneous-specification-stress/code/test_e002.py)
- **Forensic basis**: [M07 corrected-run readiness](../../../milestones/M07-E002-corrected-run-readiness.md)
  and final boundary-remediation commit `1fe42a7`; this is process/test
  evidence, not E002 scientific evidence.
