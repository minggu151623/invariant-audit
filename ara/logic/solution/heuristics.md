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
