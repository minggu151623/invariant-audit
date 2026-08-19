# Research log

Bootstrap has no experiment or result.

## 2026-08-19 — M00 direction record

- User decision: **Provenance: user.** Pivot from a generic metamorphic
  robustness benchmark to validating semantic/state invariants and
  false-positive/false-negative calibration.
- Sourced evidence: the design spec and real design/scaffold commits and files
  linked by [M00](milestones/M00-research-direction.md). Reviewer inference is
  explicitly not evidence.
- Limitations: no experiments yet, no results/data, no calibrated metrics, and
  no public claim eligibility.
- Validation commands:
  - `ruby -e 'require "yaml"; ARGV.each { |p| YAML.load_file(p) }; puts "valid YAML"' research-state.yaml state/workspace.yaml`
  - `git diff --check`
  - `git add milestones/M00-research-direction.md research-state.yaml state/workspace.yaml research-log.md findings.md`
  - `test -n "$(git diff --cached --name-only)"`
- Commit message: `research(reflect): record M00 research direction`
- Push command: `git push origin main`
- Push target: `origin/main`
- Push result: `pending-until-publication`

- Verification method: after publication, compare
  `git ls-remote origin refs/heads/main | cut -f1` with `git rev-parse HEAD`.

## 2026-08-19 — M00 documentary verification planned

- Verification scope: documentary direction/provenance only. This does not
  establish experiments, results/data, calibrated metrics, or public-claim
  eligibility.
- Validation paths: `milestones/M00-research-direction.md`,
  `research-state.yaml`, `state/workspace.yaml`, `research-log.md`, and
  `findings.md`.
- Planned commit message: `research(reflect): verify M00 research direction`
- Verification commit hash: intentionally pending until after the verification
  commit is pushed; it will be recorded in the later ARA provenance update.
- Captured verification commit after the successful push: `c79f20276657f67bb9840a469b7813473fe0ef60`.
- Push command: `git push origin main`
- Push target: `origin/main`
- Push result: `pending-until-publication`

## 2026-08-20 — M01/E001 protocol design draft

- User instruction provenance: on 2026-08-19 the exact user message was
  `tiếp tục` (“continue”). It authorized continuation at a high level but did
  not enumerate the E001 design or explicitly grant/withhold commit, push, run,
  or public-action authority.
- Orchestrator-bounded worker scope: the initial eight-path file allowlist and
  withheld commit/push/run/external-action authority came from the orchestrator
  worker brief, not from that user instruction. The initial paths were
  `literature/survey.md`, `literature/README.md`,
  `experiments/E001-synthetic-invariant-calibration/protocol.md`,
  `experiments/README.md`, `milestones/M01-protocol-design.md`,
  `state/workspace.yaml`, `research-log.md`, and `findings.md`.
- Draft date: the local draft was completed on 2026-08-20. This remediation is
  limited to the protocol, M01, canonical state, log, and findings paths.
- Protocol: [E001-v1](experiments/E001-synthetic-invariant-calibration/protocol.md),
  linked from [experiments/README.md](experiments/README.md) and
  [M01](milestones/M01-protocol-design.md).
- Literature boundary: [literature/survey.md](literature/survey.md) records
  sourced facts from QuickCheck, metamorphic-testing, stateful-testing,
  calibration, probability-score, bootstrap, and official metric sources,
  separately from proposed E001 choices.
- Design boundary: deterministic oracle-controlled synthetic cases; B0
  schema-only baseline; M1 invariant-aware method; development, calibration,
  and confirmatory splits; fixed FP/FN/classification/calibration metrics;
  paired cluster-bootstrap intervals; sanity, ablation, stopping, and
  invalid-run rules. These detailed choices are reviewer/worker design, not
  user-selected facts or observations.
- No experiment, run, result, metric, figure, data, code, commit, push, or
  external/public action was created or performed under the bounded worker
  brief.
- Planned commit subject: `research(protocol): lock E001 synthetic invariant calibration`.
  Protocol commit hash is intentionally absent because the worker brief
  withheld commit authority.
- Validation for the initial draft used Ruby YAML parse of
  `state/workspace.yaml`, `git diff --check`, `git status --short`, and
  `git diff --name-only` with the eight-path allowlist. This remediation uses
  the same read-only checks with the five-path allowlist above.
