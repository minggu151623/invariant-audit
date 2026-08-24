# Research log

Bootstrap was pre-experiment. The current outer-loop state is recorded in the
2026-08-25 reflection below.

## 2026-08-19 — M00 direction record

- User decision: **Provenance: user.** Pivot from a generic metamorphic
  robustness benchmark to validating semantic/state invariants and
  false-positive/false-negative calibration.
- Sourced evidence: the design spec and real design/scaffold commits and files
  linked by [M00](milestones/M00-research-direction.md). Reviewer inference is
  explicitly not evidence.
- Limitations at that time: no experiments yet, no results/data, no calibrated
  metrics, and `public_claim_eligibility: false`.
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
- At draft completion, no experiment, run, result, metric, figure, data, code,
  commit, push, or external/public action had been created or performed under
  the bounded worker brief.
- Planned commit subject: `research(protocol): lock E001 synthetic invariant calibration`.
  At that draft stage, the protocol commit hash was intentionally absent
  because the worker brief withheld commit authority; a later, separately
  authorized local lock is recorded below.
- Validation for the initial draft used Ruby YAML parse of
  `state/workspace.yaml`, `git diff --check`, `git status --short`, and
  `git diff --name-only` with the eight-path allowlist. This remediation uses
  the same read-only checks with the five-path allowlist above.

## 2026-08-20 — E001 protocol lock provenance

- The E001-v1 protocol was locked locally in commit
  `d8b26d21e9692ace19436d78461460940043f5c7` with subject
  `research(protocol): lock E001 synthetic invariant calibration`.
- This is temporal protocol evidence: it establishes the protocol commit
  before any future run/result record. It is not result evidence and does not
  establish performance, calibration, generalization, novelty, or safety.
- Local-only status at the time of this 2026-08-20 entry: the protocol lock and
  this metadata update were local; no push or publication had occurred, and no
  run was authorized or performed.
- Lock validation recorded for this update: `git cat-file` type/subject check,
  `git merge-base --is-ancestor` protocol-commit check, Ruby YAML parse,
  `git diff --check`, exact five-path worktree/index allowlist checks, and
  verification that the protocol file is unchanged from the locked commit.
- The metadata/provenance update is committed locally with subject
  `research(reflect): record E001 protocol provenance`.

## 2026-08-25 — E001 outer-loop reflection after publication

- **Authority (Provenance: user):** The exact user authorization was `cả hai,
  nghiên cứu lâu đi, bao lâu cũng được`. It supplied high-level authority for
  both the previously discussed public push and the E001 implementation/run;
  it did not select the technical design. The protocol, implementation, and
  reviewer/design choices retain their separate provenance.
- **Protocol and implementation chain:** E001-v1 is recorded at protocol
  commit `d8b26d21e9692ace19436d78461460940043f5c7`. The implementation is
  commit `54f530d375372589e191e0231152a177d29c2a64`. The protocol commit is an
  ancestor of the implementation and result chain.
- **Run:** `e001-20260825-001` completed with status `valid` under the locked
  protocol. Split counts were development 256, calibration 256, and
  confirmatory 512, with 64 confirmatory clusters and 10,000 paired bootstrap
  replicates. The development validation suite contained 21 tests and the
  independent review approved the implementation. Deviations: none.
- **Published result:** Result commit
  `31071ddf65ad9a1f0e5b28eb0d501899253cd17b` is on `origin/main`; the remote
  hash and protocol ancestry were verified read-only before this reflection.

| Path | SHA-256 | Size | Count |
| --- | --- | ---: | ---: |
| `data/E001-v1-predictions.jsonl` | `be5e5e2a6c3f33778a34af69d79ec4f14e3b2c0cba2f371ecc004310b7c9559a` | 2,966,528 B | 5,120 rows |
| `data/E001-v1-metrics.csv` | `ae7c32be651b5dfe175ca0537aa3cb8283acbd7063b14e15b8ec386f0d6a20cb` | 162,200 B | 75 rows + header |
| `data/E001-v1-bootstrap.csv` | `63b86d44f3425f0c2a43c53191d13ce614b0d0726ff1e941da98d11ee545ede5` | 32,920,126 B | 450,270 rows + header |
| `experiments/E001-synthetic-invariant-calibration/results/run-e001-20260825-001.md` | `cc00b21deabb88fd51c55090fc642a80424f960ad6b51c50f75818e8ffa485d6` | 2,870 B | 60 lines |

### Observed E001 result

- The primary confirmatory comparison is strictly M1 minus B0. B0 had BA
  `0.5`, FPR `1`, FNR `0`, Brier `0.25`, and ECE `0`; M1 had BA `1`, FPR
  `0`, FNR `0`, Brier `5.917159763e-05`, and ECE `0.007692307692`.
- Primary deltas were BA `+0.5`, FPR `-1`, FNR `0`, Brier `-0.2499408284`, and
  ECE `+0.007692307692`. H1 was **supported** under the locked rule: the
  paired 95% BA interval was entirely above zero, the paired FPR interval was
  entirely below zero, and the FNR point guardrail was non-positive.
- Ablations were reported separately: M1-no-semantic and M1-no-state each had
  BA `0.75`, FPR `0.5`, FNR `0`, Brier `0.166726273`, and ECE
  `0.005076538582`; M1-no-calibration had BA `1`, FPR `0`, FNR `0`, Brier `0`,
  and ECE `0`. These do not alter the primary paired delta.
- The paired intervals are degenerate because the locked 64-cluster signatures
  were identical across all 10,000 replicates. This is a property of this
  finite synthetic design, not evidence of broad real-world uncertainty.

### Evidence boundary and outer-loop decision

- M01's documentary protocol-lock step is complete and published as an
  ancestor; M02 is verified only within the finite synthetic E001 design.
- The oracle is coupled to the hand-designed recipes. The result establishes
  no production validity, external validity, generalization, novelty, or
  safety, and `public_claim_eligibility` remains `false`.
- **Reviewer/design inference, not an E002 result:** deepen and broaden with a
  future separately locked E002 protocol covering heterogeneous clusters,
  specification misspecification, multi-faults, and stronger oracle-method
  separation. No E002 protocol, run, result, or claim exists.
- This reflection is committed locally with subject
  `research(reflect): verify E001 synthetic result`; no push is authorized in
  this turn.
