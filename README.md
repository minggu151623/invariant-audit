# InvariantAudit

Research question: How can semantic and state invariants be validated while calibrating false positives and false negatives?

Scope: local research; arXiv manuscript in preparation.

Infrastructure: no paid API; no external GPU.

Target (user-selected on 2026-10-22): an evidence-audited arXiv manuscript and
source package. The candidate framing is a methods case study of finite
benchmark construction and measurement, not a new validation algorithm. See
[arXiv plan](paper/arxiv-plan.md), [working manuscript](paper/main.md), and
[review status](paper/review-status.md).

Current manuscript milestone: [M19](milestones/M19-arxiv-working-manuscript.md),
with an 8-page [preview](paper/arxiv-preview.pdf) and minimal
[source draft](paper/arxiv-source-draft.zip). The latest scientific audit is
[M18](milestones/M18-arxiv-evidence-audit.md).
A separately locked exploratory E005 audit independently reimplemented metric
arithmetic on the frozen E001/E002 outputs: all 195 overall metric comparisons
agree within declared rounding tolerances. Exact Brier decomposition explains
why resolution improves while finite score-group reliability and ECE worsen.
The binary M1 ablation has zero Brier/ECE in these constructions. E001 has
one statistic signature among 64 evaluation clusters, E002 six among 48; those
counts are diagnostics, not effective sample sizes.

E001/E002 remain the only valid performance experiments, restricted to finite
synthetic designs. E003-v1 is invalid with no external hypothesis/performance
result. E004 diagnosed 537 byte-identical extra occurrences in its fixed 2021
source. E003-v2 remains at [M17](milestones/M17-E003-v2-adapter.md): the source
normalizer and adapter are implemented with 39 passing synthetic tests, while
full pipeline integration and independent acceptance remain pending. The new
publication target does not bypass that gate or relabel inspected data as a
pristine holdout.

The new audit and manuscript have no independent scientific acceptance. Owner
metadata, substantive review and the separate submission action remain open.
`public_claim_eligibility=false`. No arXiv posting is guaranteed.

## Verified experiments

- [E001 synthetic invariant calibration](experiments/E001-synthetic-invariant-calibration/results/run-e001-20260825-001.md): valid
  confirmatory result within the finite synthetic E001-v1 design.
- [E002 heterogeneous specification stress](experiments/E002-heterogeneous-specification-stress/results/run-e002-20260825-002.md): valid
  confirmatory result within the finite synthetic E002-v1 design; the earlier
  invalid run is preserved separately.
- Row-level artifacts are indexed in [data/README.md](data/README.md).

The historical M09 human-readable synthesis is
[to_human/progress-M09.html](to_human/progress-M09.html).

The protocol-only E003 design is
[experiments/E003-external-transfer-validation/protocol.md](experiments/E003-external-transfer-validation/protocol.md),
with its historical documentary gate in
[M10](milestones/M10-E003-protocol-design.md); historical acquisition is recorded by
[M11](milestones/M11-E003-source-acquisition.md), followed by the
[M12 implementation-readiness gate](milestones/M12-E003-implementation-readiness.md).

The executed invalid run is recorded in [M13](milestones/M13-E003-run-001-invalid.md).
The [corrected working paper](paper/main.md) limits conclusions to the finite
synthetic results and records the failed external source gate.

The E003 implementation and development/calibration-only verification are
indexed in [the E003 code README](experiments/E003-external-transfer-validation/code/README.md).

## Documentation

- [Design spec](docs/superpowers/specs/2026-08-19-invariant-audit-research-workspace-design.md)
- [Bootstrap plan](docs/superpowers/plans/2026-08-19-invariant-audit-bootstrap.md)
- [Milestones](milestones/README.md)
- [Findings](findings.md)

No overclaim: public claims require verified milestone evidence and human review.
