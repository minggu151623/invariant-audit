# InvariantAudit

Research question: How can semantic and state invariants be validated while calibrating false positives and false negatives?

Scope: local-only.

Infrastructure: no paid API; no external GPU.

Status: M12 E003 implementation readiness is pending independent review; E001
and E002 have verified finite-synthetic results. E003 confirmatory run,
results, and production outputs remain absent and unauthorized.

The repository contains verified local evidence for the finite synthetic E001
and E002 designs. Those results are evidence for their locked constructions
only; they do not establish production performance, external validity,
generalization, novelty, safety, or public-claim eligibility.

The current outer-loop decision is **BROADEN**: the largest unresolved gap is
transfer to externally authored structured records. The current gate is M12:
the exact E003-v1 three-file source snapshot has been verified and frozen
outside Git, and the scoped implementation has passed development/calibration
preflight pending independent review. E003 has no confirmatory run, result,
data, or production output.

## Verified experiments

- [E001 synthetic invariant calibration](experiments/E001-synthetic-invariant-calibration/results/run-e001-20260825-001.md): valid
  confirmatory result within the finite synthetic E001-v1 design.
- [E002 heterogeneous specification stress](experiments/E002-heterogeneous-specification-stress/results/run-e002-20260825-002.md): valid
  confirmatory result within the finite synthetic E002-v1 design; the earlier
  invalid run is preserved separately.
- Row-level artifacts are indexed in [data/README.md](data/README.md).

The latest human-readable synthesis is
[to_human/progress-M09.html](to_human/progress-M09.html).

The protocol-only E003 design is
[experiments/E003-external-transfer-validation/protocol.md](experiments/E003-external-transfer-validation/protocol.md),
with its historical documentary gate in
[M10](milestones/M10-E003-protocol-design.md); the current acquisition gate is
[M11](milestones/M11-E003-source-acquisition.md), followed by the
[M12 implementation-readiness gate](milestones/M12-E003-implementation-readiness.md).

The E003 implementation and development/calibration-only verification are
indexed in [the E003 code README](experiments/E003-external-transfer-validation/code/README.md).

## Documentation

- [Design spec](docs/superpowers/specs/2026-08-19-invariant-audit-research-workspace-design.md)
- [Bootstrap plan](docs/superpowers/plans/2026-08-19-invariant-audit-bootstrap.md)
- [Milestones](milestones/README.md)
- [Findings](findings.md)

No overclaim: public claims require verified milestone evidence and human review.
