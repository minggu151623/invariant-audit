# InvariantAudit

Research question: How can semantic and state invariants be validated while calibrating false positives and false negatives?

Scope: local research; arXiv manuscript in preparation.

Current priority: develop an original contribution, per the owner's 2026-10-23
feedback. The audit draft remains a baseline; see the
[novelty screen](literature/novelty-reset-20261023.md) and
[E007 mathematical feasibility protocol](experiments/E007-fd-decision-stability/protocol.md).
Local research continues without waiting for peer-review acceptance.
Current mathematical work: [M27](milestones/M27-E009-singleton-characterization.md)
records an exact accepted-target radius formula, the singleton bottleneck proof,
and a verified generic raw-cell MILP baseline. Novelty and practical usefulness
remain open; [Vietnamese progress](to_human/M27-singleton-result-vi.md).

Earlier submission preparation: [M23](milestones/M23-owner-reading-and-submission-preparation.md),
[reading guide in Vietnamese](paper/reading-guide-vi.md), and
[submission instructions](paper/submission-guide-vi.md). Owner review is pending.

Infrastructure: no paid API; no external GPU.

Target (user-selected on 2026-10-22): an evidence-audited arXiv manuscript and
source package. The candidate framing is a methods case study of finite
benchmark construction and measurement, not a new validation algorithm. See
[arXiv plan](paper/arxiv-plan.md), [working manuscript](paper/main.md), and
[review status](paper/review-status.md).

Latest scientific milestone: [M20](milestones/M20-external-reference-results.md).
A new, predeclared external-reference study compares fixed rule-attribution
policies on Beers, Flights and Rayyan. It preserves the tradeoff between rejecting
correct cells and accepting incorrect ones, and a mixed lookup-score prediction
whose Flights interval crosses zero. All 720 exported point checks and 84
bootstrap intervals pass delivery verification.

The manuscript now includes E005's audit of two finite synthetic constructions
and E006's three fixed reference datasets. It has 12 pages, nine references and
two source-linked figures; see the [preview](paper/arxiv-preview.pdf),
[minimal source draft](paper/arxiv-source-draft.zip), and
[owner review guide](paper/owner-review-vi.md).

E006's policies are not the original M1. Its cell-correction labels, context
and task differ, so this does not establish causal M1 transfer or deployment
performance. E003-v1 remains invalid, E004 stays a source diagnostic, and
E003-v2 remains at [M17](milestones/M17-E003-v2-adapter.md) with its gate unchanged.
The source A1 failure and A2 metadata-only header correction are preserved.

The new audit/study/manuscript lack independent scientific acceptance. Substantive owner
review, public release and the submission
process remain open. A [portable evidence verifier](reproducibility/README.md)
and [review bundle](paper/evidence-review-bundle.zip) now support frozen-output
verification without Git, NumPy, TeX or a machine-specific cache. `public_claim_eligibility=false`. No arXiv posting is
guaranteed and no submission or public push has occurred.

## Verified experiments

- [E001 synthetic invariant calibration](experiments/E001-synthetic-invariant-calibration/results/run-e001-20260825-001.md): valid
  confirmatory result within the finite synthetic E001-v1 design.
- [E002 heterogeneous specification stress](experiments/E002-heterogeneous-specification-stress/results/run-e002-20260825-002.md): valid
  confirmatory result within the finite synthetic E002-v1 design; the earlier
  invalid run is preserved separately.
- [E006 fixed external-reference study](experiments/E006-external-reference-validation/results/run-e006-20261022-001.md):
  valid within its distinct fixed rule-attribution/reference-correction design.
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
