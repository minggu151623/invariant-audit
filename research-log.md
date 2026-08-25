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

  No run is performed in this documentation task. M03 remains the historical
  protocol-only record; M04 is the current implementation-review and
  authorization gate.
