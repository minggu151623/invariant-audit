# Research log

## 2026-09-21 — M17 E003-v2 source filtering and selection adapter

- User instruction: `được rồi tiếp tục công việc nghiên cứu đi`. Authority is
  continuation for local milestone commits without push; technical design and
  implementation architecture are AI-suggested (author: Gemini 3.8 Flash high via AGY in Herdr ipse).
- Implementation commit: `28f74d56eb9d4813139279da445c32fd10ec973e` (`adapter_v2.py`,
  `test_adapter_v2.py`, `code/README.md`).
- Pure in-memory source adapter implements:
  `normalization -> v1 pinned pure projection/oracle helpers -> first reason exclusions -> all-type/all-requested-split repo isolation -> deterministic quotas/caps/diversity`,
  retaining original source coordinates throughout.
- Protocol and helper pins verified: both locked protocol SHA-256 digests unchanged
  (E003-v2 `2c7b762...`, E003-v1 `8ec0ebc...`); unversioned pure helpers loaded with
  SHA-256 digest validation (`e003.py` `cd21b21...`, `oracle_e003.py` `0bfc2be...`).
- Test execution: orchestrator independently ran all 39 synthetic tests (22 source normalizer + 17 adapter):
  `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s experiments/E003-v2-exact-repeat-transfer/code -p 'test_*.py' -v`.
  All 39 pass in 0.312 s. Initial 35 tests had 1 failure 9 errors; after first remediation
  2 fixture failures remained; now all 39 pass.
- Bounded review scope: bounded synthetic unit tests verify in-memory adapter behavior.
  No real sources were read; no independent full-pipeline acceptance. Old and new raw
  data/metrics/run remain absent.
- Classification: `exploratory_reused_sources`; `public_claim_eligibility: false`.
- Next gates (remaining M16 priorities 2–5): evaluation/calibration/bootstrap version identities,
  guards/transactionality, guarded 2019/2020 integration, and full independent acceptance
  before performance execution. See [M17](milestones/M17-E003-v2-adapter.md).
- No network, source-cache/real shards, run/scoring/calibration, protocol edits,
  E001-E004 evidence edits, external actions, push, or publication.

## 2026-09-21 — M16 E003-v2 protocol lock and source component

- Resumed from clean M15 commit 6c9b4d0 on user instruction `được rồi tiếp tục đi`.
- Locked E003-v2 amendment in b9cae97 before implementation. V1 is incorporated
  by immutable hash; changes are explicit. All source reuse is exploratory.
- Implemented pure exact-repeat normalization in 87ccd69 with full-byte
  comparison, strict parsing, atomic return, original coordinates, all-type
  repository index and explicit production pins. No v1 imports or mutations.
- Synthetic suite: 22 tests PASS (0.003 s). No real shard content was opened,
  no v2 manifest written and no performance scoring performed. Manifest expected
  hash calculation read original manifest metadata only.
- Full evaluation integration, transactional runner, guarded two-split tests
  and independent acceptance remain open. This is partial implementation, not
  a valid external result. See [M16](milestones/M16-E003-v2-protocol-and-normalizer.md).
- No network, delegation, push, publication, automation or epilogue writes.

## 2026-09-17 — M15 E004 completion and outer-loop synthesis

- Locked E004 in 1bf1a4a, implemented/tested in 648a607, then ran exactly once
  on a clean worktree: e004-20260917-001, exit 0, valid_source_diagnostic_only.
- Recovered the exact three public source shards outside Git. All original
  compressed hashes, byte sizes, JSONL counts and reconstructed manifest match.
  New acquisition metadata is dated today, not backdated to M11.
- Confirmatory: 117,780 records, 117,243 unique IDs, 537 extra occurrences;
  all full raw-line hashes match the first occurrence. No canonical-only
  equivalents, conflicting groups or cross-shard repeated IDs. Max multiplicity
  two. Development/calibration have no duplicate IDs.
- Nineteen synthetic tests pass; dictionary/sort outputs and separate aggregate
  arithmetic/hash checks agree. One-agent verification, not independent review.
  No causal delivery-mechanism conclusion follows.
- Outer loop retains BROADEN. Propose conservative exact-repeat collapse in
  E003-v2 with conflict rejection; separately lock, test and independently
  review before any exploratory reused-source performance run. E003-v1 stays
  invalid; no H3/external-performance result exists.
- Evidence/hashes and next gates: [M15](milestones/M15-E004-source-diagnosis.md).
  No push, publication, delegation or ARA epilogue writes were performed.

## 2026-09-17 — M14 correction and E004 design

- User authorized continued research; technical choices are AI-suggested.
- Corrected paper/outline against immutable E001/E002 results/protocols:
  table errors, class orientation, calibration method, scope and overclaims.
  Withdrew the historical LinkedIn draft. No public action was taken.
- E003-v1 invalidation is preserved. No model-specific cause for errors is
  established. Duplicate-delivery causal attribution is unestablished.
- Proposed E004 with fixed original source hashes, a separate protocol lock,
  raw/canonical/conflicting categories and dictionary-versus-sort verification.
  It is exploratory follow-up to M13, not external performance evidence.
  Original temporary cache/manifest were absent at resumption.

Bootstrap was pre-experiment. Earlier entries below retain their historical
outer-loop state; the current state is M17 above.

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
  separation. At that pre-M03 reflection point, no E002 protocol, run, result,
  or claim existed; the later M03 protocol lock is recorded below.
- This reflection is committed locally with subject
  `research(reflect): verify E001 synthetic result`; no push is authorized in
  this turn.

## 2026-08-25 — M03/E002 protocol lock design

- **Authority (Provenance: user):** The current user message authorizes
  high-level continuation to design and locally lock the next outer-loop
  protocol. It does not select any E002 technical design. No technical choice
  below is attributed to the user.
- **Source boundary:** New technical concepts were researched only through
  direct primary research papers or official technical documentation. The
  source-to-claim map is in [the E002 section of the literature
  survey](literature/survey.md): specification-based testing and
  specification mutation (Stocks and Carrington; Hierons and Merayo),
  independent differential testing (McKeeman), heterogeneous clustered
  inference and bootstrap (Cameron et al.; Hagemann), and interaction/
  multi-fault motivation (Kuhn et al.; Yan et al.; NIST). Those sources do
  not supply E002 parameters, outcomes, or evidence.
- **Reviewer/design inference:** The locked E002-v1 choices are six
  non-identical heterogeneous cluster templates H0-H5, 96 clusters, 912
  cases, exact split counts 228/228/456, valid/single/multi recipes,
  schema-visible mutations, an independently maintained replay/conservation
  reference oracle, schema-only B0, exact-spec M1, omission/overconstraint/
  stale-transition regimes, semantic/state/no-calibration ablations,
  calibration isolation, the H2 primary rule, subgroup metrics, paired
  10,000-replicate cluster bootstrap, the under-50,000,000-byte bootstrap
  budget, determinism/leakage/footprint/size gates, and invalid-run staging
  rules. These are predeclared design choices, not sourced facts or results.
- **Protocol state:** E002-v1 is recorded at
  [the protocol](experiments/E002-heterogeneous-specification-stress/protocol.md)
  and M03. The dedicated local lock subject is
  research(protocol): lock E002 heterogeneous specification stress, with
  required parent 4494ed80af0dec9b57b183877cb5ed3a8270c3db. The file does not
  self-embed its future commit hash; the full hash is supplied by git evidence
  after the one commit.
- **Negative evidence and documentary update:** This lock creates the
  documentary protocol, M03 milestone, state and research-state pointer,
  research-log and findings entries, literature notes, and README index
  updates. At that M03 protocol-only stage, it created no executable E002 code
  or implementation, run, experimental data/results/output, figure, or ARA
  artifact. run_authorized remained false and public_claim_eligibility
  remained false.
- **Next gate:** A separately authorized and independently reviewed
  implementation may begin only from the protocol lock commit. A future run
  must use the locked preflight, independent oracle, full determinism gate,
  safe staging, overwrite refusal, and finite stopping rule. No E002
  experimental result or metric exists at this point; run_authorized remains
  false.

## 2026-08-25 — M03/E002 protocol remediation

- **Co-primary design inference:** The amended E002-v1 protocol retains the
  heterogeneous M1-B0 anchor and makes specification stress co-primary through
  d1 omit-M1 FPR on schema-valid truth-negative conservation-failure cases,
  d2 over-M1 FNR on valid active-active cases, and d3 stale-M1 FNR on valid
  pending-closed cases. The originally suggested FNR-on-negative and
  FPR-on-positive forms were denominator-invalid under truth=1 for valid
  cases, so the class-appropriate complementary rates are the locked bounded
  alternative. Each requires a strictly positive lower 95 percent interval.
- **Eligibility and arithmetic:** d1 has all 48 confirmatory clusters; d2 has
  the 40 H0-H4 confirmatory clusters; d3 has the 40 H1-H5 confirmatory
  clusters. Standard bootstrap blocks are
  10 subgroups times 5 metrics = 50, and d1-d3 add 3 blocks. The exact output
  is 530,000 replicate rows plus 53 interval rows plus one header, or 530,054
  lines. Metrics are 240 method rows plus 3 diagnostic rows, or 243 data rows.
- **NA policy:** H2 gates only the overall anchor BA/FPR intervals and d1-d3
  stress intervals, plus the defined anchor point conditions. The
  single-class case-kind BA/FPR/FNR intervals are explicitly descriptive and
  may be partial or undefined without making H2 unreachable. Partial required
  intervals cannot support H2.
- **Behavioral separation and leakage:** Overconstraint rejects active-active;
  stale-transition accepts active-active but omits pending-closed. The exact
  generated H0-C00 valid-base payload hash is
  `8ddb5fbd84a64ef811a261ad72359f647d0757e8c83c864bd206bbb03b8dd07b` and
  must produce M1=true, over=false, stale=true; H5-C00 is
  `97935beb48f281d1d1fe8317d8ee7f300089bd2e6ad523fc06aaaaf47d4c6db3` and
  must produce M1=true, over=true, stale=false. Runtime probes must
  distinguish them. Split gates require within-split uniqueness and pairwise
  disjoint base-hash, cluster-ID, and case-ID sets across all three splits.
  Signature distinctness uses non-type structural tuples, while the complete
  H0-H5 type/tuple/case/signature/recipe manifest is mandatory and rejects
  label, recipe, count, or signature drift.
- **Deterministic handoff:** The amended protocol fixes UTF-8/LF bytes,
  canonical JSON, CSV dialect, Markdown, nine-place rational decimal output,
  NA/bool/list/fault-set encodings, case suffixes, row orders, manifests,
  data-artifact hashes, and external post-finalization result hashing. Known
  vectors include amount 920, primary bootstrap index 28, the H0 signature
  all six signature digests
  (`2e80ccf18dad2a97d8d3e975b0f726f6cf15687fa6e4f50ddf55a940e6d29e9b`,
  `0195af9dd2a1ef0f4348c6fc6f082b626d7c9ab1c310c9487d5760bf74afa574`,
  `0863b001f0a85dc2582be68a41d33afc2c7d8b28bb52e224e66c4124b8a42d45`,
  `278251e55ee1daf215d42e1f534bf811529ab9da39069e488c448f88014d3272`,
  `d96362a72a4bd443d8e750ced1cebca4521ff28a9e5116bfe6e65c57d2cfbaf3`,
  `9a0568400739c46729f811419f84a144a0dfd5de1031f30bd9a47834f101bdcd`),
  and the valid/R1 case-ID digests recorded in the protocol.
- **Source correction:** The cited mutation paper is Robert M. Hierons and
  Mercedes G. Merayo, *Mutation testing from probabilistic and stochastic
  finite state machines*, DOI 10.1016/j.jss.2009.06.030, with the direct
  ScienceDirect record in the survey. This is a source-attribution correction,
  not E002 evidence.
- **Status:** This is still documentary protocol remediation only. No
  executable E002 code or implementation, run, experimental data/results/
  output, figure, or ARA artifact exists; the documentary ten-path update is
  the only change. No E002 experimental metric or result exists.

## 2026-08-25 — E002 serialization-template remediation

- **Draft-byte boundary:** The result template and internal hash list contain
  no `result_draft_bytes` field and no report draft/final hash. Two independent
  builds compare the complete rendered valid-result bytes directly before
  finalization; the finalized report SHA-256 is computed only externally after
  writing. No redacted or preimage form is serialized or hashed.
- **Placeholder gate:** The valid and invalid templates have a closed
  vocabulary with strict ASCII grammars, field sources, exact delimiters and
  empty-list rules, fixed interval-key membership, Markdown cell-safety, and
  static/render gates. Valid deviations are literal `none`; invalid records
  use literal `failure_class: invalid-run`.
- **Scope:** This remains documentary serialization remediation only. Counts,
  signatures, H0/H5 probes, 48/40/40 eligibility, and synthetic-only limits
  are unchanged; no E002 code, run, result, data, output, figure, or ARA
  artifact exists.

## 2026-08-25 — M04/E002 implementation review and authorization gate

- **Authority (Provenance: user):** The current messages were `tiếp tục lúc
  hết quota đi` and `bạn đọc lại tài liêụ đi là biết mà`. The existing
  long-running context also records `cả hai, nghiên cứu lâu đi, bao lâu cũng
  được`. Calibrated interpretation: these current messages explicitly direct
  resumption from documented state and reaffirm continued local research. They
  authorize the next locked local E002 confirmatory execution and result
  recording, but do not select technical design, authorize push/publication or
  a public claim, or establish any result.
- **Protocol lock:** E002-v1 remains locked at commit
  `9e39c5defc89f2c2a896b53dda529f326e9dfcf8`, with protocol blob
  `f7d27a069ee3fd1600f89d9271e107c197033238`; the protocol is unchanged.
- **Implementation chain:** The initial implementation is
  `42cb62374c2b94ad6c567232acdac6d7365a9d8f`; result-validator hardening is
  `6df4f3bc02f5f12feb243df21ec9eeaafd53d8fc`; independent-review remediation
  is `0977641f129d172dd4d11136197a82cb17654aeb`.
- **Independent review:** Initial status was **HOLD** with High interrupt
  cleanup, Medium local-index split allocation, Medium canonical-byte
  determinism, and Low stale README test-count findings. All four findings
  were remediated. Re-review returned **no findings** and fit the
  independent-review gate.
- **Observed verification:** The standard-library-only development command
  `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s
  experiments/E002-heterogeneous-specification-stress/code -p 'test_e002.py'`
  ran 53 tests and returned `OK`. This is implementation/test evidence only;
  no confirmatory run or E002 output has yet occurred.
- **Current E002 state:** `implementation_reviewed: true`,
  `run_authorized: true`, `run: absent`, `results: absent`, and
  `public_claim_eligibility: false`. No E002 metrics, H2 outcome, external
  validity, novelty, safety, or generalization claim is established.
- **Next gate:** After the required clean-tree preflight, the authorized local
  command is:

  ```text
  PYTHONDONTWRITEBYTECODE=1 python experiments/E002-heterogeneous-specification-stress/code/run_e002.py --run-id e002-20260825-001 --output-root .
  ```

  No run was performed in that M04 documentation task. M03 remains the
  historical protocol-only record; M04 was the current implementation-review
  and authorization gate at that stage. M05 now records the subsequent
  invalid execution.

## 2026-08-25 — M05/E002 run 001 invalid evidence record

- **Observed run (runner evidence):** The M04-authorized local command was run
  once with run ID `e002-20260825-001`. It exited with code `2` and emitted
  `status: invalid`, the run ID, and
  `error: result semantic field drift: D9_OR_NA`.
- **Invalid report:** The existing report is
  [run-e002-20260825-001.md](experiments/E002-heterogeneous-specification-stress/results/run-e002-20260825-001.md),
  SHA-256
  `f441d55795b81d280e35b09980dcb6f79e58e7cfacbe9886ed094a207580aa34`, 258
  bytes and 8 lines. It records `failure_class: invalid-run`, states that no
  metrics or evidence exist, and sets `corrected_run_requires_new_id: true`.
  The three E002 data outputs were absent.
- **Independent diagnosis (worker/reviewer verification, not user-selected
  design):** The first mismatch was `D9_OR_NA` at zero-based index `13`, on
  result line `38`, `Delta M1-B0 Brier`. The producer value was
  `-0.091689527` from exact fractions, while the validator produced
  `-0.091689526` by subtracting rounded metric cells. The locked protocol
  requires exact arithmetic until serialization. This is an implementation
  defect, not a scientific outcome.
- **State transition:** M05 records the invalid run. The one-run M04
  authorization is consumed: `run_authorized: false`,
  `authorization_consumed: true`, implementation remediation is pending, and
  `public_claim_eligibility: false`. No metrics, evidence, data, H2 outcome,
  external-validity, novelty, safety, generalization, or public claim is
  established.
- **Next gate:** Remediate the implementation and obtain independent review
  before any separately authorized corrected local run. A corrected run must
  use a new run ID. No corrected run or publication is authorized here.

## 2026-08-25 — M06/E002 validator remediation and independent-review gate

- **Provenance (repository artifacts):** M05's invalid-run record is in commit
  `9d8019023082e8125ecb88808408ebb3d40d41d7`. The validator remediation is in
  commit `e090fa76be67a3cb1d52517bd93327ef821b8e75`, whose parent is the M05
  commit and whose subject is `research(impl): fix E002 exact delta validation`.
  The locked protocol remains commit
  `9e39c5defc89f2c2a896b53dda529f326e9dfcf8`, blob
  `f7d27a069ee3fd1600f89d9271e107c197033238`; its bytes are unchanged. The
  preserved invalid report remains SHA-256
  `f441d55795b81d280e35b09980dcb6f79e58e7cfacbe9886ed094a207580aa34`.
- **Independent diagnosis (Provenance: worker/reviewer verification):** The
  first mismatch in run `e002-20260825-001` was `D9_OR_NA` at zero-based index
  `13`, result line `38`, `Delta M1-B0 Brier`. The producer value was
  `-0.091689527` from exact fractions; the validator value was
  `-0.091689526` from subtracting rounded metric cells. The protocol requires
  exact arithmetic until serialization. This was an implementation defect,
  not a scientific outcome.
- **Remediation (Provenance: worker implementation):** The validator now
  recomputes overall and cluster deltas from independently reconstructed exact
  `Fraction` statistics, rather than rounded D9 metric-row strings, and
  propagates those exact values through D9, H2, and the guardrail. The
  deterministic regression renders through the producer and then validates
  through the independent validator. The implementer’s targeted regression
  failed before the patch with `result semantic field drift: D9_OR_NA` and
  passed after it. The full standard-library-only development suite passed
  with 54 tests and `OK`.
- **Independent review (Provenance: reviewer check):** Targeted checks passed
  `3/3`; static, diff, and hash review passed. The review initially returned
  **HOLD** solely for stale README test-count text, then returned **ACCEPT**
  after the count was corrected to 54.
- **Current state:** M06 is current. The M04 one-run authorization was
  consumed by M05: `implementation_remediation: complete`,
  `implementation_reviewed: true`, `run_authorized: false`,
  `corrected_run_authorized: false`, `authorization_consumed: true`,
  `run: invalid`, `results: invalid_report_only`, and data, metrics, and
  evidence are absent. `public_claim_eligibility` remains `false`.
- **Next gate:** Any corrected run requires a new run ID and separate explicit
  authorization. M06 neither authorizes nor executes a corrected run. No E002
  metric, H2 outcome, external-validity, novelty, safety, generalization, or
  public claim is established by this remediation record.

## 2026-08-25 — M07/E002 corrected-run technical-readiness gate

- **Provenance boundary:** The read-only readiness audit began at the ARA
  epilogue HEAD `70d47de1af70d380437876effe082adcfb1a70a3`. The worker’s
  initial readiness conclusion was technical **PASS**. This documentary gate
  does not infer corrected-run authority or attribute technical design to the
  user.
- **Independent review correction:** The reviewer found a P1 **HOLD** because
  the new development regression and canonical structural-report paths still
  computed confirmatory statistics, contrary to `protocol.md:1164`, plus a P3
  stale-documentation finding. Moving the exact-versus-rounded counterexample
  to development/calibration splits was insufficient: re-review correctly
  held because the canonical report still executed the real confirmatory
  `_validator_primary_deltas` before and under a wraps spy.
- **Final remediation (Provenance: worker implementation):** Commit
  `1fe42a7ebc6a9ce69d8a16654e068c0a9a891d08`, parent
  `70d47de1af70d380437876effe082adcfb1a70a3`, subject
  `research(impl): enforce E002 development test boundary`, contains exactly
  the code README, runner, and development-test files. The final design makes
  `split` required; production report/H2 calls pass `confirmatory` explicitly;
  the structural test stubs exact deltas before report generation through all
  validations and blocks `_validator_stats`; and only the development/
  calibration regression dynamically computes exact statistics and
  metric/bootstrap evidence. It retains `-0.091689527` versus
  `-0.091689526`, and the README/module docstring are truthful.
- **Verification boundary:** Worker evidence was targeted `2/2` and full
  standard-library-only suite `54/54 OK`. Independent review statically traced
  the call paths and ran targeted `2/2`, returning **TECHNICAL READINESS
  ACCEPT** with no findings. It did not run the full suite because runner
  tests were outside its read-only scope. These are worker/reviewer claims,
  not experimental evidence.
- **Readiness gates (read-only):** Candidate `e002-20260825-002` has valid
  grammar. Its three shared E002 data paths and candidate result path were
  absent; no staging, temporary, or lock paths existed; repository cwd and
  output-root assumptions were valid; Python `3.14.5` and approximately
  `18 GiB` free space were nonblocking; protocol commit/blob identity was
  valid; and invalid run 001’s report was preserved.
- **State:** M07 sets `technical_ready: true` subject to runtime preflight,
  `implementation_reviewed: true`, and `corrected_run_authorized: false`.
  The M04 authorization is consumed; run 001 remains invalid only; candidate
  002 was not executed or reserved and its output is absent. Metrics, data,
  evidence, H2 outcome, and public-claim eligibility remain absent/false. The
  exact intended CLI is recorded in M07 as not authorized and not executed.
  A corrected run requires separate explicit authority; no run or claim is
  established here.

## 2026-08-25 — M08/E002 corrected run 002 valid result

- **Authority and provenance boundary:** The current bounded user brief
  explicitly authorized exactly one corrected local E002 run with run ID
  `e002-20260825-002`, its locked result recording, and no retry or external
  action. It did not select the E002 technical design. The protocol, runner,
  validator, and test design remain locked worker/reviewer implementation
  work; this record separates that provenance from the observed run.
- **Runtime preflight (worker evidence):** The run began from HEAD
  `86ede8ac1fcd674b9cc559ee7ad2c381efa4f3d0` with a clean worktree. The E002
  protocol commit `9e39c5defc89f2c2a896b53dda529f326e9dfcf8` was an ancestor,
  and `experiments/E002-heterogeneous-specification-stress/protocol.md` had
  locked blob `f7d27a069ee3fd1600f89d9271e107c197033238`. The candidate final,
  staging, temporary, and lock paths were absent; cwd/output-root matched the
  repository; Python was `3.13.5`; and `19,730,772` 1-KiB blocks were free
  (approximately `18.8 GiB`). The protocol requires standard-library-only
  local CPU execution with no network/API/GPU and does not pin a Python minor
  version.
- **Execution (runner evidence):** The exact command was run once at
  `2026-08-25T22:40:19+07:00` and exited `0`:

  ```text
  PYTHONDONTWRITEBYTECODE=1 python experiments/E002-heterogeneous-specification-stress/code/run_e002.py --run-id e002-20260825-002 --output-root .
  ```

  Runner stdout reported `status: valid`, the expected run ID, result SHA-256
  `d1f11d17be3b91d246126dc36b88880a76f039f31fa7eeef63d5aff4cfe713fa`, and
  multi-fault relation SHA-256
  `a02432ead45db3633e7cbe2f07e5314fa19dd800d9c2441da34bbfbe08510dd5` with
  `equals=272`, `contains=160`, and `differs=0`. The emitted relation JSON
  contained no `differs` rows.
- **Artifact evidence:**

  | Artifact | SHA-256 | Size | Count |
  | --- | --- | ---: | ---: |
  | `data/E002-v1-predictions.jsonl` | `bcb34aad4338fdfbffe07be1843769b360bf4e8c422d855a9ce605350fad13b7` | 6,556,304 B | 7,296 rows |
  | `data/E002-v1-metrics.csv` | `f000348d385550745480066fce2d691686728ebe2bfcf7bd96e7231e4b1e5ca3` | 116,260 B | 243 rows + header |
  | `data/E002-v1-bootstrap.csv` | `8c5919f709c9ad8ca673308053ecefbe94ca23b0c190b923f14957cbfeac7d5d` | 30,814,607 B | 530,053 rows + header |
  | `experiments/E002-heterogeneous-specification-stress/results/run-e002-20260825-002.md` | `d1f11d17be3b91d246126dc36b88880a76f039f31fa7eeef63d5aff4cfe713fa` | 6,486 B | 100 lines |

  The result report records all protocol gates as pass, two-build byte
  comparison as pass, literal `Deviations: none`, and
  `confirmatory_execution: completed exactly once`.
- **Observed locked result:** On the primary confirmatory anchor M1 minus B0,
  the report records delta BA `0.401960784`, FPR `-0.803921569`, FNR
  `0.000000000`, Brier `-0.091689527`, and ECE `0.005222762`. The co-primary
  stress intervals passed, H2 is `supported`, and the FNR guardrail passed at
  delta `0.000000000`. This is a confirmatory result within the finite,
  synthetic E002-v1 construction only. It is not production, external-
  validity, novelty, safety, generalization, or public-claim evidence;
  `public_claim_eligibility` remains `false`.
- **Preservation and state transition:** The M05 invalid report for
  `e002-20260825-001` remains unchanged with SHA-256
  `f441d55795b81d280e35b09980dcb6f79e58e7cfacbe9886ed094a207580aa34`.
  M08 is now current; the one-run corrected authorization is consumed,
  `run_001` remains invalid only, `run_002` is valid, and data, metrics,
  evidence, and the bounded H2 outcome are present. No further run, retry,
  publication, push, or public claim is authorized by this record.

## 2026-08-31 — M09 outer-loop reflection after E002

- **Scope/provenance:** This reflection synthesizes only the verified E001
  record M02 and the verified E002 record M08. The numbers are observed
  result/artifact evidence; mechanism interpretation, gap analysis, and the
  direction choice are reviewer/design inference. No new run or data was
  created.
- **Quantitative comparison:** E001 used 512 confirmatory cases and 64
  clusters; M1-B0 deltas were BA `+0.5`, FPR `-1`, FNR `0`, Brier
  `-0.2499408284`, and ECE `+0.007692307692`, with H1 supported within the
  finite synthetic design. E002 used 456 confirmatory cases and 48
  confirmatory clusters; M1-B0 deltas were BA `+0.401960784`, FPR
  `-0.803921569`, FNR `0.000000000`, Brier `-0.091689527`, and ECE
  `+0.005222762`, with H2 supported within the finite synthetic design and
  all three co-primary specification-stress intervals passing.
- **Pattern/mechanism inference:** In both constructions, schema-only B0
  accepted schema-valid semantic/state faults that M1's cross-field checks
  rejected. E001 no-semantic/no-state each had BA `0.75`, FPR `0.5`; E002
  no-semantic/no-state each had BA `0.823529412`, FPR `0.352941176`.
- **Lessons:** E002's heterogeneous signatures and stress diagnostics reduced
  synthetic design weaknesses but did not establish external validity. E001's
  intervals were degenerate; E002's intervals are still finite-design
  resampling. The first E002 run's rounded-cell arithmetic defect reinforces
  exact arithmetic, independent validation, and preserved invalid-run records
  as mandatory evidence gates.
- **Remaining gap:** externally authored structured records, source/schema
  drift, natural invalid prevalence, sequence-level behavior, and a less
  recipe-coupled oracle boundary remain untested.
- **Decision:** **BROADEN**, not DEEPEN, PIVOT, or CONCLUDE. The repeated
  synthetic pattern does not require a question pivot, while further synthetic
  stress would not directly answer the largest transfer gap and conclusion
  would overreach.
- **Next gate:** design and locally lock an E003-v1 protocol only. The next
  protocol must specify a frozen public fixture, acquisition/hash plan,
  inclusion/exclusion, source split isolation, independent oracle, metrics,
  invalid-run rules, and a stopping gate. The fixture is not acquired, E003 is
  not implemented or run, and no E003 data/result/public claim is authorized.
- **Artifacts:** [M09 milestone](milestones/M09-outer-loop-after-E002.md) and
  the self-contained [M09 progress presentation](to_human/progress-M09.html).

## 2026-08-31 — M10 E003 protocol-only external-transfer design

- **Provenance and source cap:** M10 follows the M09 **BROADEN** decision. New
  E003 literature discovery was capped at three directly relevant
  primary/official sources: [GH Archive](https://www.gharchive.org/),
  [GitHub event types](https://docs.github.com/en/rest/using-the-rest-api/github-event-types),
  and [Kalliamvakou et al.](https://doi.org/10.1007/s10664-015-9393-5). Their
  narrow sourced facts are separated from the worker/reviewer protocol
  choices; no further search was performed.
- **Protocol design:** [E003-v1](experiments/E003-external-transfer-validation/protocol.md)
  fixes three timestamped GH Archive shard URLs, a staged external acquisition
  and SHA-256 manifest plan, an explicit GitHub event subset, strict exclusion
  and repository isolation rules, 64+64 bases per split, four paired cases per
  base, B0/M1 and ablations, calibration/confirmatory isolation, an
  independently maintained oracle, deterministic repository bootstrap, exact
  artifact schemas, invalid-run behavior, and one-valid-run stopping.
- **Acquisition/execution boundary:** The three source files are not acquired;
  no hash, byte count, line count, HTTP metadata, source manifest, E003 code,
  run, prediction, metric, bootstrap, result, or public claim exists. No
  download or experiment was attempted in this stage.
- **State transition:** M10 is the current documentary milestone and the
  research pointer/state/index updates identify the E003 stopping gate. The
  technical design is not user-selected, and `run_authorized: false`,
  `acquisition_authorized: false`, and `public_claim_eligibility: false` remain
  explicit.
- **Git handoff:** The two required local commits are now recorded in order,
  with the M09/report slice first and the E003 protocol/state/literature/index
  slice second. The full protocol commit hash is available from Git history and
  is intentionally not self-embedded in the state record.
- **Next gate:** Separate authority is required for source acquisition,
  implementation/review, or the single confirmatory run; the protocol-only lock
  authorizes none of those actions.

## 2026-09-01 — M11 E003 source acquisition freeze and cache remediation

- **Authority (Provenance: user):** The bounded M11 acquisition-remediation
  brief authorized local verification, reversible cache moves, metadata and
  scoped documentation/state updates, and one local commit from clean HEAD
  `b68424e756fb86f05c866647b2471d36e24da716`. It prohibited network access,
  delegation, protocol edits, E003 implementation/tests, event selection,
  scoring, confirmatory execution, publication, and push.
- **Pre-remediation verification:** The canonical manifest
  `/private/tmp/invariant-audit-e003-v1/source-manifest.json` was verified
  unchanged at SHA-256
  `683eef39cd26d2a7f6622689adc2cd9e357e78a770f77bf91e98513b859e4633`.
  Each manifest-listed gzip was locally rehashed and decompressed with the
  standard library; strict UTF-8 and one-object-per-nonempty-line validation
  passed with unchanged byte and JSONL counts.
- **Cache remediation:** The three extra `.headers` files were moved, not
  deleted, to `/private/tmp/invariant-audit-e003-v1-remediation-archive-20260901/`.
  Their hashes are
  `0e9f751b9c213201b49900c94d58776488ddc6c1b7994b06d7530574b100dfd8`,
  `d33afd6da92f991d7fabef3d27a2e7df05ba21984aa04b27da01764c19636322`, and
  `761ffd6482919336cb57682c9c211843770ad187ed280bec7faf49d59d4d8815`; the
  source directory now contains exactly the three manifest-listed `.json.gz`
  files. A copy of the old metadata is preserved at
  `.../acquisition-metadata.pre-remediation.json` with SHA-256
  `6d47ea164f42a02b69fad37c466cd7253bb7f07b3f6a1985534fc2b657b9554f`.
- **Authoritative freeze:** After the post-move verification, the local-only
  freeze event was recorded at `2026-08-31T19:59:22Z` UTC with the exact cache
  inventory, manifest SHA-256, starting HEAD, and explicit
  `network_used_during_remediation: false`. Its canonical object hash is
  `17ac5e9eb4386ef2d6f4f34996f240e600b16d7521fdcc6b91dfd10630c27ed7`.
  The updated metadata v2 hash is
  `5937fbf7d8583ed3954b7d107146af331d29f2a14e224d883e892c74ce52388a`.
- **Chronology reconciliation:** The old `network_frozen_at_utc`
  `2026-08-31T19:06:24Z` predates the observed manifest mtime
  `2026-08-31T19:07:45Z`. That original ordering is not independently
  supported and is retained only as historical context; it was not rewritten
  or backdated. The new post-verification local event is the authoritative
  audited-freeze boundary.
- **Isolation and state:** The confirmatory shard was touched only for hash,
  byte, line-count, and format validation; no event selection, projection,
  calibration, scoring, metrics, bootstrap, or result generation occurred.
  M11 is now `acquisition_complete_audited_implementation_absent`;
  implementation, run, predictions, metrics, bootstrap, result, and code are
  absent; `run_authorized: false` and `public_claim_eligibility: false` remain
  explicit. The locked protocol and protected E001/E002/ARA paths remain
  unchanged. Separate authority and independent review are required for the
  next gate.

## 2026-09-01 — M12 E003 implementation-readiness

- **Scope and authority:** The bounded continuation from the green uncommitted
  E003 code slice authorized scoped implementation verification and M12
  documentation/state updates, followed by exactly one local implementation
  commit. It did not authorize a confirmatory run, result production, push, or
  a public claim. The locked protocol and acquisition cache were not edited.
- **Implementation:** The standard-library/local-CPU implementation is indexed
  in [the E003 code README](experiments/E003-external-transfer-validation/code/README.md)
  and consists of the source adapter/methods, separate oracle, future-run
  runner, and tests. Imports are side-effect free; the runner was not invoked.
- **Guarded integration:** Two independent development/calibration preflight
  builds used only `2019-01-15-12.json.gz` and `2020-01-15-12.json.gz`; a
  byte-read guard rejected any request for `2021-01-15-12.json.gz`. Each split
  selected 64 IssuesEvent and 64 PullRequestEvent bases, 512 cases, and had
  selected repository counts 103 (development) and 92 (calibration). There
  were 2,178 shared repository IDs removed before selection, 5,408/9,435
  eligible events after isolation, and zero selected-repository overlap.
- **Calibration and determinism:** The combined raw scoring count was 5,120;
  only calibration rows fit the four calibrated methods. The manifest hash was
  `683eef39cd26d2a7f6622689adc2cd9e357e78a770f77bf91e98513b859e4633`.
  Lookup hashes were B0
  `2d5d789ed71d73772e62c29eebdce252eee0e6dfe46965ceec676de424463058`, M1
  `02b1d8bddcb941bde65c59499e1799ee559abc9f62ef42755850ab11b5c0c6a2`,
  M1-no-identity
  `370cd8fa7f24bffe5c72a41e8a1e2f5f93e68f2bba88cb88518a475e89c573d5`, and
  M1-no-state
  `0e786b395a7af8913bdb8fcb2b02957448f94ed9587a471759a73c3f0623e98b`.
  The projection signature was
  `8adb4a38cbe92aed57d37c3e8e0812299e6dc57072434061427624ad6fda0f53`; two
  independent preflight builds matched in all recorded fields, lookup bytes,
  and lookup hashes.
- **Testing:** `py_compile` passed. The four focused regressions passed **4/4**
  in 0.014 seconds. The full
  `PYTHONDONTWRITEBYTECODE=1` unittest discovery passed **29/29** in 16.897
  seconds (17.04 seconds wall time). The initial diagnostic had six failures
  (4 failures, 2 errors): two real implementation defects (mixed exclusion
  key bookkeeping and calibration-row isolation) and four fixture/assertion
  mismatches (ablation sets, missing bootstrap subgroup, expected smoothed
  value, and temporary-directory cleanup). All were remediated in scoped
  code/tests; this is development remediation, not experiment evidence.
- **Boundary:** M12 state is
  `implementation_remediated_pending_independent_re_review`. The confirmatory gzip
  was not opened, selected, scored, or used for metrics/bootstrap. Run,
  predictions, metrics, bootstrap, result, and production output paths are
  absent; `run_authorized: false`, `run: absent`, `results: absent`, and
  `public_claim_eligibility: false` remain explicit. Independent review and
  separate run authority are required next.

## 2026-09-03 — M13 E003 confirmatory run and source-integrity failure

- **Context:** Autonomous continuation under user directive
  `user-2026-09-03-e003-goal`. Remediated M12 implementation was committed as
  `915448450702d849fafe39b23b5c777e48b30dcf` with 29/29 tests passing.
- **Execution:** Executed authorized single confirmatory run:
  `python3 experiments/E003-external-transfer-validation/code/run_e003.py --run-id e003-20260903-001 --output-root . --source-manifest /private/tmp/invariant-audit-e003-v1/source-manifest.json`
- **Observed outcome:** Run terminated with exit code `2`, `status: invalid`.
  Runner failure: `pre-staging pipeline failure: duplicate event ID across source: confirmatory:16450 and confirmatory:16491`.
- **Diagnosis:** Detailed inspection of external source fixtures in
  `/private/tmp/invariant-audit-e003-v1/source/` revealed that the 2021
  confirmatory shard contains 537 duplicate event IDs across multiple types
  (289 PushEvent, 34 PullRequestEvent, 19 IssuesEvent, etc.), while development
  (2019) and calibration (2020) shards contain 0 duplicates. This reflects
  real-world upstream telemetry at-least-once delivery. Locked protocol E003-v1
  Filter 1 explicitly forbids deduplication and treats any duplicate ID as a
  source-integrity failure that rejects the run.
- **Artifacts:** Concise invalid report written to
  `experiments/E003-external-transfer-validation/results/run-e003-20260903-001.md`
  (SHA-256 `5bf6c545f43333a6a3cc0d8ea8a8b2d3f7adfb4be0c0358d1cd75c17a8254305`,
  258 bytes, 8 lines). Milestone M13 recorded in
  `milestones/M13-E003-run-001-invalid.md`.
- **Boundary:** M13 status is `invalid_run_recorded`. Authorization is consumed.
  No metrics, evidence, data, predictions, bootstrap, or H3 claims exist.
  Public claim eligibility remains `false`. Outer-loop reflection is required
  to decide between protocol revision E003-v2 (with realistic stream deduplication)
  or alternative collision-free fixture acquisition.

## 2026-10-22 — arXiv destination and E005 protocol

User explicitly changed the research destination to an arXiv paper. Read M17,
canonical state, locked protocols and corrected manuscript. The destination
does not establish a scientific result or guarantee posting. AI-proposed
framing is a methods case study of benchmark construction and score behavior.
Locked a separate exploratory reanalysis protocol for the already inspected
E001/E002 row artifacts; no new performance run or E003 gate bypass. See
[arXiv plan](paper/arxiv-plan.md) and [E005 protocol](experiments/E005-benchmark-evidence-audit/protocol.md).

## 2026-10-22 — E005 valid exploratory audit and M18

After protocol 2e6f7c2, implemented E005 at 167f721 and passed 21 synthetic
tests. One run e005-20261022-001 completed with byte-identical double builds.
Four original hashes matched, 39 summary rows and 12 score groups were produced,
and all 195 metric comparisons passed. The Brier decomposition exposes increased
resolution alongside worse score-group reliability; the binary ablation remains
perfect on these constructions. Same-agent verification is bounded and is not
independent acceptance. No original input, protocol, performance run or unrelated
user artifact was changed. See M18 and the E005 result/checks.

## 2026-10-22 — M19 arXiv-directed working manuscript

Reframed the existing Markdown in place as a finite methods case study using
E005/M18 evidence, seven source-verified references and explicit AI-use disclosure.
Generated the Brier figure, LaTeX project, 8-page preview and three-file source
ZIP. The initial native compile timed out on resource downloads; isolated
hash-verified Tectonic 0.17.0 compiled the source. Corrected command wrapping and
kept tables intact, rendered/inspected every final page, and successfully
compiled the extracted ZIP with matching text and zero layout warnings.
User replied that they have no arXiv account/materials yet and tentatively expect
sole authorship; name and affiliation remain unknown. Recorded metadata without
inventing identity. Scientific scope/novelty and independent review remain open.
Goal stays active; no push, upload or account creation.
