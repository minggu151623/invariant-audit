# M01 — Protocol design

## ID

M01

## Status

active

This milestone is active for documentary protocol design only. Its documentary
protocol-locking step is complete locally, but it is not verified experimental
evidence, does not contain a run or result, and does not grant public-claim
eligibility.

## Relationship to M00

M00 is the verified documentary record of the user-approved pivot toward
semantic/state invariant validation and false-positive/false-negative
calibration. M01 turns that direction into the proposed [E001 synthetic
calibration protocol](../experiments/E001-synthetic-invariant-calibration/protocol.md).

## Provenance

**User instruction (Provenance: user):** On 2026-08-19, the exact user message
was `tiếp tục` (“continue”). This is interpreted as a high-level instruction to
continue the existing work. It did not enumerate the E001 design and did not
explicitly grant or withhold commit, push, run, or public-action authority.

**Orchestrator-bounded worker scope:** The exact initial eight-path file
allowlist and the withheld commit/push/run/external-action authority came from
the orchestrator's bounded worker brief, not from the user's one-word
instruction. That initial allowlist was `literature/survey.md`,
`literature/README.md`, `experiments/E001-synthetic-invariant-calibration/protocol.md`,
`experiments/README.md`, `milestones/M01-protocol-design.md`,
`state/workspace.yaml`, `research-log.md`, and `findings.md`. The current
remediation brief separately limits edits to this milestone, protocol, state,
log, and findings set.

**Draft date:** The initial draft was completed locally on 2026-08-20. The
protocol was subsequently locked locally in commit
`d8b26d21e9692ace19436d78461460940043f5c7`. No push, run, or public action was
performed.

**Sourced foundation:** [literature/survey.md](../literature/survey.md) links
the primary papers and official documentation used to ground terminology and
measurement choices. Those sources do not verify E001 or supply E001 results.

**Reviewer/design inference — not evidence:** The detailed E001 design was
chosen as a bounded reviewer/worker proposal, not selected by the user. A
deterministic synthetic oracle,
four semantic/state invariant families, a schema-only baseline, an
invariant-aware method, disjoint calibration/confirmatory splits, and clustered
uncertainty are a bounded design for testing measurement behavior. They are not
claims that the method will work or that the design is novel.

## Protocol record

- Protocol path: `experiments/E001-synthetic-invariant-calibration/protocol.md`
- Protocol version: `E001-v1`
- Planned protocol commit subject: `research(protocol): lock E001 synthetic invariant calibration`
- Protocol commit hash: `d8b26d21e9692ace19436d78461460940043f5c7`
- Protocol-lock status: complete locally; the commit has not been pushed or
  published.
- Run/result/data status: none created; no run is authorized by this record.

The protocol-before-results gate remains active: the dedicated protocol commit
must precede every future run/result/data record, and future results must record
the exact commit and pass the ancestor check.

## Documentary completion criteria

The documentary protocol-locking step is complete locally: the protocol is
committed separately, the state/log/index pointers record the exact commit, and
the read-only review confirms that no result or data was created before it.
M01 remains active and documentary; experimental verification would be a
separate milestone decision with separate evidence.

## Limitations and eligibility

The current evidence is M00 direction/provenance plus literature notes and a
local protocol draft. There are no observations, calibrated metrics, results,
data, or public claims. M01 is not a verified milestone and cannot source
external-facing content.

## Next gate

With the protocol commit in place, a worker may separately evaluate whether a
run is authorized. Any run must follow E001 exactly, record deviations and
invalid outcomes, and keep confirmatory and exploratory evidence separate.
