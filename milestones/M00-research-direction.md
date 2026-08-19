# M00 — Research direction

## ID

M00

## Status

active

## User decision

**Provenance: user.** On 2026-08-19, the user approved the pivot from a generic
metamorphic robustness benchmark to validating semantic/state invariants and
false-positive/false-negative calibration.

## Sourced evidence

The sourced evidence for this record is limited to the following real repository
files and commits:

- [InvariantAudit research workspace design spec](../docs/superpowers/specs/2026-08-19-invariant-audit-research-workspace-design.md), dated 2026-08-19 and recorded by [design commit `995b318`](https://github.com/minggu151623/invariant-audit/commit/995b318).
- [Scaffold commit `5424d4c`](https://github.com/minggu151623/invariant-audit/commit/5424d4c), which established the documented workspace and its pointer, log, and findings files.
- The real scaffold files [research-state.yaml](../research-state.yaml), [research-log.md](../research-log.md), and [findings.md](../findings.md).

These sources establish the workspace conventions and provenance boundary. They
do not provide experiment results, data, calibrated metrics, or evidence of
research performance.

## Reviewer inference

**Reviewer inference — not evidence.** The pivot narrows the first research
direction to an auditable validation protocol in which semantic/state invariants
and false-positive/false-negative calibration are explicit prerequisites for
interpretable claims. This interpretation does not establish performance and
must not be presented as a result.

## Goal

Define the initial research direction for validating semantic and state
invariants while calibrating false positives and false negatives, with a clear
chain from protocol to run, result, data, reflection, and milestone evidence.

## Completion criteria

- M00 remains `active` until its evidence has been produced and reviewed.
- A protocol Markdown record is written and committed before any experiment,
  run, result, or data record is created.
- The protocol specifies the research question or hypothesis, inputs, method,
  parameters, evaluation metrics, expected outputs, stopping criteria, data
  recording, and known limitations.
- Any future result records its protocol path and protocol commit, and the
  protocol commit is an ancestor of the result commit.
- The canonical YAML state and this Markdown record retain separated user,
  sourced-evidence, and reviewer-inference provenance.

## Limitations

There are no experiments yet, no results/data, no calibrated metrics, and no
public claim eligibility. This record documents a direction decision only; it
does not support a robustness, invariant-validity, or calibration claim. The
reviewer inference above is not evidence.

## Next gate

Before any run, create and commit the protocol Markdown record. Before any
result or data commit, verify the protocol-before-results gate with
`git merge-base --is-ancestor <protocol_commit> <results_commit>`. A future
milestone must be reviewed with complete provenance and evidence before it can
be used for public-facing content; M00 is currently active and has no public
claim eligibility.
