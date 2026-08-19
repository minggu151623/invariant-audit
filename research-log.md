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
