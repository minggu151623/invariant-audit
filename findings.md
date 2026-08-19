# Findings

No public claim is eligible from M00. Its documentary verification does not
establish public-claim eligibility.

## M00 research direction

The user-approved pivot, with **Provenance: user**, is from a generic
metamorphic robustness benchmark to validating semantic/state invariants and
false-positive/false-negative calibration. M00 is verified only as a
documentary direction/provenance record, not as an experimental result.

### Evidence boundary

Sourced evidence is limited to the [design spec](docs/superpowers/specs/2026-08-19-invariant-audit-research-workspace-design.md),
real commits `995b318` and `5424d4c`, and the real repository files linked from
the M00 record. Reviewer inference is labeled as reviewer inference and is not
evidence. No user decision or reviewer interpretation is a result.

### Limitations

There are no experiments yet, no results/data, no calibrated metrics, and no
public claim eligibility. No robustness, invariant-validity, or calibration
performance claim is supported by this record.

### Protocol-before-results gate

Before any experiment or result/data record, a protocol Markdown record must be
created and committed with its question or hypothesis, inputs, method,
parameters, evaluation metrics, expected outputs, stopping criteria, data
recording, and limitations. A result must reference that protocol commit, and
the protocol commit must be an ancestor of the result commit. Public-facing
content remains gated on a verified milestone and human review.

## M00 documentary verification

The verification scope is limited to documentary direction and provenance
consistency. Validation paths are `milestones/M00-research-direction.md`,
`research-state.yaml`, `state/workspace.yaml`, `research-log.md`, and
`findings.md`.

Planned verification commit subject: `research(reflect): verify M00 research direction`.
The verification hash is intentionally omitted until after the verification
commit is pushed and is recorded only in the later ARA provenance update.
Captured verification commit after the successful push: `c79f20276657f67bb9840a469b7813473fe0ef60`.

There are still no experiments, no results/data, no calibrated metrics, and no
public claim eligibility. No robustness, invariant-validity, or calibration
performance claim is supported by this documentary verification.

## M01/E001 protocol design

M01 is active and documentary/protocol-only. It is not verified experimental
evidence and is not eligible to source public claims. The proposed protocol is
[E001-v1](experiments/E001-synthetic-invariant-calibration/protocol.md), with
the documentary milestone at [milestones/M01-protocol-design.md](milestones/M01-protocol-design.md)
and the source boundary at [literature/survey.md](literature/survey.md).

### Provenance correction

The exact user instruction on 2026-08-19 was `tiếp tục` (“continue”). It
authorized continuation at a high level, but did not enumerate the E001 design
or explicitly grant or withhold commit, push, run, or public-action authority.
The initial eight-path allowlist and withheld commit/push/run/external-action
authority came from the orchestrator-bounded worker brief. The detailed E001
recipes, parameterization, metrics, and gates are reviewer/worker design
choices, not a user-selected design. The local draft was completed on
2026-08-20; the current remediation is limited to the five paths named in its
worker brief.

### Current understanding

The current record defines a bounded measurement design rather than a finding:
an exact synthetic oracle labels valid and single-fault invalid semantic/state
cases; B0 is a schema-only baseline; M1 checks four invariant families; a
calibration split is disjoint from a confirmatory split; and the confirmatory
analysis is pre-specified around FP, FN, balanced accuracy, Brier score, ECE,
and paired cluster-bootstrap intervals. These are proposed protocol choices,
not observed performance.

### Evidence boundary

The literature foundation records sourced technical facts and links, while the
E001 generator, transformations, counts, confidence mapping, metrics, and
gates are reviewer/design choices. No source or local file presently establishes
that M1 outperforms B0, that the confidence is calibrated, or that the synthetic
design generalizes.

### Protocol-before-results gate

The E001-v1 protocol was locked locally in commit
`d8b26d21e9692ace19436d78461460940043f5c7` with subject
`research(protocol): lock E001 synthetic invariant calibration`. This lock is
temporal protocol evidence, not result evidence: it establishes the
protocol-before-results boundary but does not establish performance,
calibration, generalization, novelty, safety, or public-claim eligibility. The
commit has not been pushed. No run, result, metric, figure, data, or code may
be created without a separately authorized run, and any future result must
reference this exact hash and pass the ancestor check.

## Post-lock protocol evidence

The local protocol lock is the only new evidence recorded here. M01 remains
active and documentary/protocol-only; it is not verified experimental evidence
and is not eligible to source public claims. The metadata update records the
commit identity and validation boundary only, not an observation or measured
outcome.

### Open questions and limitations

Future authorized work must verify generator determinism, oracle isolation,
single-fault construction, output schema, and the declared uncertainty method.
E001 remains finite, synthetic, ontology-coupled, and conditional on its
generator; even valid results would not establish production validity,
generalization, novelty, safety, or public-claim eligibility. Any new seeds,
faults, metrics, thresholds, or post-hoc analyses must be labeled exploratory
or placed in a new protocol version.
