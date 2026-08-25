# Findings

This document separates user authority, protocol/design provenance, observed
E001 results, and reviewer/design inference. M02 is verified only within the
finite synthetic E001 design; `public_claim_eligibility` is `false`.

## M00 — research direction

M00 remains a verified documentary record of the user-approved pivot from a
generic metamorphic robustness benchmark toward semantic/state invariants and
false-positive/false-negative calibration. It is not experimental evidence and
does not establish performance, calibration, generalization, novelty, safety,
or public-claim eligibility.

The underlying design specification, scaffold commits, literature notes, and
M00 milestone preserve the original source boundary. Reviewer interpretation
of that pivot is not a user-selected result.

## M01 — protocol-lock documentary step

M01's documentary protocol-locking step is complete and published as an
ancestor of the E001 result. E001-v1 is the protocol at
`experiments/E001-synthetic-invariant-calibration/protocol.md`, locked in
commit `d8b26d21e9692ace19436d78461460940043f5c7`. M01 remains documentary
protocol evidence, not experimental evidence, and does not grant public-claim
eligibility.

The exact user authorization on 2026-08-25 was
`cả hai, nghiên cứu lâu đi, bao lâu cũng được`. It supplied high-level
authority for both the previously discussed public push and the E001
implementation/run. It did not select the technical design; the detailed
recipes, oracle, metrics, gates, and ablations remain reviewer/worker design
choices.

## E001 result — finite synthetic confirmatory finding

### Evidence chain

- Protocol: commit `d8b26d21e9692ace19436d78461460940043f5c7`.
- Implementation: commit `54f530d375372589e191e0231152a177d29c2a64`.
- Run: `e001-20260825-001`, status `valid`.
- Result: commit `31071ddf65ad9a1f0e5b28eb0d501899253cd17b`, published on
  `origin/main`; protocol ancestry and remote result hash were verified
  read-only.
- Split counts were development 256, calibration 256, and confirmatory 512;
  the confirmatory split had 64 clusters and the paired bootstrap used exactly
  10,000 replicates.
- The reviewed development suite contained 21 tests, and independent review
  approved the implementation. Deviations: none.

| Artifact | SHA-256 | Size | Count |
| --- | --- | ---: | ---: |
| `data/E001-v1-predictions.jsonl` | `be5e5e2a6c3f33778a34af69d79ec4f14e3b2c0cba2f371ecc004310b7c9559a` | 2,966,528 B | 5,120 rows |
| `data/E001-v1-metrics.csv` | `ae7c32be651b5dfe175ca0537aa3cb8283acbd7063b14e15b8ec386f0d6a20cb` | 162,200 B | 75 rows + header |
| `data/E001-v1-bootstrap.csv` | `63b86d44f3425f0c2a43c53191d13ce614b0d0726ff1e941da98d11ee545ede5` | 32,920,126 B | 450,270 rows + header |
| `experiments/E001-synthetic-invariant-calibration/results/run-e001-20260825-001.md` | `cc00b21deabb88fd51c55090fc642a80424f960ad6b51c50f75818e8ffa485d6` | 2,870 B | 60 lines |

### Primary result: M1 minus B0

The primary comparison is strictly M1 minus B0. On the confirmatory split:

| Method | BA | FPR | FNR | Brier | ECE |
| --- | ---: | ---: | ---: | ---: | ---: |
| B0 | 0.5 | 1 | 0 | 0.25 | 0 |
| M1 | 1 | 0 | 0 | 0.00005917159763 | 0.007692307692 |
| Delta M1 − B0 | +0.5 | −1 | 0 | −0.2499408284 | +0.007692307692 |

H1 was **supported within this synthetic design**: the paired 95% interval for
delta BA was entirely above zero, the paired interval for delta FPR was entirely
below zero, and the point delta FNR was non-positive. The FNR guardrail was
satisfied at delta FNR `0`. This is not a production or external-validity
claim.

### Ablations

Ablations were reported as secondary analysis and do not change the primary
paired deltas:

- M1-no-semantic: BA `0.75`, FPR `0.5`, FNR `0`, Brier `0.166726273`, ECE
  `0.005076538582`.
- M1-no-state: BA `0.75`, FPR `0.5`, FNR `0`, Brier `0.166726273`, ECE
  `0.005076538582`.
- M1-no-calibration: BA `1`, FPR `0`, FNR `0`, Brier `0`, ECE `0`.

### Uncertainty and limitations

All locked paired bootstrap intervals are degenerate because the 64-cluster
signatures were identical across all 10,000 replicates. Those point intervals
are a consequence of this finite construction, not evidence of broad
uncertainty characterization.

The oracle is coupled to the hand-designed recipes. E001 is finite, balanced,
synthetic, and single-fault. It establishes no production validity, external
validity, generalization, novelty, or safety, and it is not evidence that the
method is calibrated outside this design. Accordingly,
`public_claim_eligibility` remains `false`.

## Outer-loop decision

**Decision: deepen and broaden.** A future, separately locked E002 protocol
should test heterogeneous clusters, specification misspecification,
multi-faults, and stronger separation between oracle and method. This is a
reviewer/design inference for the next protocol, not an E002 result. No E002
protocol, implementation, run, result, or claim existed at that pre-M03 point;
the later protocol lock is recorded below.

Future E002 work must preserve the protocol-before-results gate and repeat the
provenance separation between user authority, technical design, observed
results, and reviewer inference.

## M03 — E002 protocol-only design

The outer-loop decision has now been converted into a locally locked,
protocol-only E002 design:
[E002-v1 heterogeneous specification stress](experiments/E002-heterogeneous-specification-stress/protocol.md).
This is not an E002 result. No executable E002 implementation or run, or
experimental data/results/output, figure, or ARA artifact exists, and
public_claim_eligibility remains false.

### Technical source boundary

The new literature section uses only direct primary papers or official
technical documentation for its new technical concepts. Stocks and Carrington
and Hierons and Merayo ground specification-based testing and specification
mutation; McKeeman grounds independent differential comparison; Cameron et al.
and Hagemann ground the motivation for cluster-aware treatment under
heterogeneity; Kuhn et al., Yan et al., and the official NIST record ground
bounded interaction and multi-fault motivation. The direct URLs and the
supported-claim limits are recorded in [literature/survey.md](literature/survey.md).
No source establishes an E002 result or validates the protocol's choices.

### Locked design boundary

Every detailed E002 choice is reviewer/design inference, not user selection or
sourced fact. The protocol predeclares non-identical H0-H5 signatures and 96
clusters; valid, four single-fault, and bounded multi-fault/schema-visible
recipes; an independently maintained replay/conservation reference oracle
with no shared checker predicates or tables; schema-only B0; exact-spec M1;
omission, overconstraint, and stale-transition checker regimes; semantic/state
and no-calibration ablations; disjoint development/calibration/confirmatory
splits; calibration isolation; the exact H2 supported versus mixed/not
supported rule; subgroup metrics; paired cluster bootstrap with 10,000
replicates; determinism, leakage, schema, footprint, size, and overwrite
gates; and invalid-run staging.

The heterogeneous signatures and cluster resampling are intended to make
nondegenerate cluster uncertainty possible, but an eventual degenerate
interval would be reported as a property of the finite construction, not
silently treated as broader uncertainty. The oracle is independent in code
structure but remains a hand-specified synthetic reference. The protocol
therefore makes no production, external-validity, novelty, safety, or
generalization claim.

### Status and next gate

M03 is protocol_locked_local. The required lock parent is the published
reflection commit 4494ed80af0dec9b57b183877cb5ed3a8270c3db, and the dedicated
lock subject is research(protocol): lock E002 heterogeneous specification
stress. The user supplied only high-level continuation authority. There is no
E002 run authorization in this record. Implementation, execution, results,
data, and publication require later bounded authority and independent review.

## M03 remediation — co-primary stress and deterministic handoff

The amended protocol makes specification stress co-primary with the
heterogeneous M1-minus-B0 anchor. It locks three denominator-valid diagnostics:
d1 omit-M1 FPR on schema-valid truth-negative conservation-failure cases, d2
over-M1 FNR on valid active-active cases, and d3 stale-M1 FNR on valid
pending-closed cases. d1 uses all 48 confirmatory clusters; d2 uses the 40
H0-H4 clusters; d3 uses the 40 H1-H5 clusters. Each diagnostic requires a
strictly positive lower paired
cluster-bootstrap interval. The suggested FNR-on-negative and FPR-on-positive
forms were explicitly rejected as zero-denominator alternatives under the
truth=1 convention.

H2 now gates only its required overall anchor BA/FPR intervals and the three
stress intervals, together with defined anchor points. Single-class
case-kind BA/FPR/FNR intervals are descriptive and may be partial or
undefined; they do not make H2 unreachable. Partial required intervals cannot
support H2.

The amended arithmetic is 912 cases and 7,296 prediction rows; 240 standard
metric rows plus 3 diagnostic rows; and 530,000 bootstrap replicates plus 53
interval summaries plus one header, or 530,054 lines. The compact deterministic
bootstrap upper estimate is 47,710,564 bytes, below the 50,000,000-byte
pre-write gate and 52,428,800-byte public limit.

The handoff now fixes exact UTF-8/LF, canonical JSON, CSV, Markdown, decimal,
NA, boolean, list, fault-set, case-ID, hash-input, manifest, and row-order
encodings; two-build byte comparison; external post-finalization result
hashing; and all six known-answer signature SHA-256 vectors. Overconstraint
rejects active-active while stale-transition accepts active-active and omits
pending-closed. The generated H0-C00 valid-base payload hash is
`8ddb5fbd84a64ef811a261ad72359f647d0757e8c83c864bd206bbb03b8dd07b` with
decisions M1=true, over=false, stale=true; H5-C00 is
`97935beb48f281d1d1fe8317d8ee7f300089bd2e6ad523fc06aaaaf47d4c6db3` with
M1=true, over=true, stale=false. The mandatory H0-H5 manifest rejects type
label, recipe, count, or signature drift, while distinctness still excludes
type from the structural hash proof.
Signature distinctness excludes type, and split gates enforce pairwise
disjoint base-hash, cluster-ID, and case-ID sets with within-split uniqueness.

The mutation paper attribution is corrected to Robert M. Hierons and Mercedes
G. Merayo, with its direct DOI and ScienceDirect record in the survey. This
lock creates documentary protocol/milestone/state/log/findings/literature/
README updates. At that M03 protocol-only stage, it created no executable E002
code or implementation, run, experimental data/results/output, figure, or ARA
artifact; no E002 metric or H2 outcome existed.

The third review closes the result-template boundary: `result_draft_bytes` and
all report draft/final self-hash fields are removed. Two complete rendered
result drafts are compared directly, while the finalized report SHA-256 is
computed only externally after finalization; no redacted or preimage form is
serialized. Both templates now use a closed placeholder vocabulary with
strict ASCII grammars, fixed semantic sources, exact interval-key membership,
list/empty-list rules, Markdown cell-safety, and static/render gates. Valid
deviations are literal `none`, and invalid records use literal
`failure_class: invalid-run`.

## M04 — E002 implementation review and authorization gate

M03 remains the historical protocol-only stage. M04 records the executable
implementation review and the current bounded authorization state; it is not
an E002 result.

### Authority and provenance

On 2026-08-25, the current user messages were exactly:

- `tiếp tục lúc hết quota đi`
- `bạn đọc lại tài liêụ đi là biết mà`

The existing recorded long-running context is
`cả hai, nghiên cứu lâu đi, bao lâu cũng được`. Calibrated interpretation:
these current messages explicitly direct resumption from documented state and
reaffirm continued local research. They authorize the next locked local E002
confirmatory execution and result recording, but do not select technical
design, authorize push/publication or a public claim, or establish any result.
The implementation and review choices remain worker/reviewer design and
verification work.

### Protocol, implementation, and review evidence

The locked E002-v1 protocol is commit
`9e39c5defc89f2c2a896b53dda529f326e9dfcf8`, blob
`f7d27a069ee3fd1600f89d9271e107c197033238`, unchanged. The implementation
chain is:

1. `42cb62374c2b94ad6c567232acdac6d7365a9d8f` — initial implementation;
2. `6df4f3bc02f5f12feb243df21ec9eeaafd53d8fc` — result-validator hardening;
3. `0977641f129d172dd4d11136197a82cb17654aeb` — independent-review
   remediation.

The initial independent review was **HOLD** for four findings: High interrupt
cleanup, Medium local-index split allocation, Medium canonical-byte
determinism, and Low stale README test count. All four were remediated, and
re-review returned **no findings** / fit for the independent-review gate.
The standard-library-only development suite ran 53 tests and returned `OK`.
No confirmatory run or E002 output has occurred.

### M04-stage state and next gate

At the M04 gate, the documentary state was `implementation_reviewed: true`,
`run_authorized: true`, `run: absent`, `results: absent`, and
`public_claim_eligibility: false`. The next gate is a clean-tree local run
with run ID `e002-20260825-001` using:

```text
PYTHONDONTWRITEBYTECODE=1 python experiments/E002-heterogeneous-specification-stress/code/run_e002.py --run-id e002-20260825-001 --output-root .
```

That M04 documentation task did not run the command or create data, metrics,
bootstrap, results, figures, ARA artifacts, or any H2, external-validity,
novelty, safety, or generalization evidence. The authorization was bounded to
the next locked local execution and result recording; it did not authorize
push, publication, or a public claim. M05 records the later execution as
invalid.

## M05 — E002 run 001 invalid execution

M05 records the already-existing local execution authorized by M04. It is an
invalid-run evidence record, not an E002 scientific result.

### Observed invalid run

- Run ID: `e002-20260825-001`.
- Exit code: `2`.
- Runner failure: `result semantic field drift: D9_OR_NA`.
- Invalid report:
  [run-e002-20260825-001.md](experiments/E002-heterogeneous-specification-stress/results/run-e002-20260825-001.md)
  with SHA-256
  `f441d55795b81d280e35b09980dcb6f79e58e7cfacbe9886ed094a207580aa34`.
- The report is 258 bytes and 8 lines, has status `invalid` and failure class
  `invalid-run`, and requires a new ID for a corrected run.
- No metrics, evidence, or data outputs exist. No H2 outcome is established.

### Independent implementation diagnosis

The first mismatch was `D9_OR_NA` at zero-based index `13`, on result line
`38`, `Delta M1-B0 Brier`. The producer value was `-0.091689527` from exact
fractions. The validator value was `-0.091689526`, produced by subtracting
rounded metric cells. The locked protocol requires exact arithmetic until
serialization. This is an implementation defect, not a scientific outcome.

This diagnosis is independent worker/reviewer verification, not a user-
selected technical design or experimental conclusion. The invalid execution
does not establish an E002 metric, H2 outcome, external validity, novelty,
safety, generalization, or public claim.

### State and next gate

The M04 one-run authorization is consumed. M05 is current with
`run_authorized: false`, `authorization_consumed: true`, implementation
remediation pending, and `public_claim_eligibility: false`. The invalid report
is the only result record; metrics, evidence, and data remain absent.

The next gate is implementation remediation followed by independent review.
Any corrected local run requires a new run ID and separate authorization. No
corrected run, publication, or public claim is authorized by this record.

## M06 — E002 validator remediation and independent review

M06 closes the validator-remediation gate while preserving M04 and M05 as
historical records. M05's invalid-run record is in commit
`9d8019023082e8125ecb88808408ebb3d40d41d7`. The remediation commit is
`e090fa76be67a3cb1d52517bd93327ef821b8e75`, with parent `9d801902` and subject
`research(impl): fix E002 exact delta validation`. These are repository
artifacts, not user-selected technical design.

### Root cause and fix

The first invalid-run mismatch was `D9_OR_NA` at zero-based index `13`, result
line `38`, `Delta M1-B0 Brier`: producer `-0.091689527` from exact fractions
versus validator `-0.091689526` from subtraction of rounded metric cells.
The locked protocol requires exact arithmetic until serialization. This was an
implementation defect, not a scientific outcome.

The remediation recomputes validator overall and cluster deltas from
independently reconstructed exact `Fraction` statistics and propagates those
values through D9, H2, and the guardrail checks. A deterministic regression
renders a producer-style report and then independently validates it. The
implementer’s targeted regression failed prepatch with
`result semantic field drift: D9_OR_NA` and passed postpatch. The worker’s
full standard-library-only development suite passed with 54 tests and `OK`.

### Review and evidence boundary

The independent reviewer’s targeted checks passed 3/3, with static, diff, and
hash review also passing. The review initially returned **HOLD** only for the
stale README test count; after correction to 54 tests, it returned **ACCEPT**.
Worker test results, reviewer checks, and repository hashes are kept as
distinct evidence classes. None is confirmatory experimental evidence.

The locked protocol remains commit
`9e39c5defc89f2c2a896b53dda529f326e9dfcf8`, blob
`f7d27a069ee3fd1600f89d9271e107c197033238`, unchanged. The preserved invalid
report remains SHA-256
`f441d55795b81d280e35b09980dcb6f79e58e7cfacbe9886ed094a207580aa34`. No data,
metrics, or evidence outputs exist, and the invalid run establishes no metric,
H2 outcome, external validity, novelty, safety, generalization, or public
claim.

### Current state and next gate

M06 is current. The M04 authorization was consumed by the M05 invalid run.
Implementation remediation is complete and implementation review is true, but
`run_authorized` and `corrected_run_authorized` are false; the run remains
invalid and the result record remains invalid-report-only. Any corrected run
requires a new run ID and separate explicit authorization. M06 does not
authorize or execute one.

## M07 — E002 corrected-run technical readiness

M07 is a documentary technical-readiness gate, not an E002 result. The
read-only readiness audit began at ARA epilogue HEAD
`70d47de1af70d380437876effe082adcfb1a70a3`; its worker conclusion was
technical **PASS**. No new user authority for a corrected run is inferred, and
all technical choices remain worker/reviewer design and verification.

### Review correction and final remediation

The independent reviewer initially returned **HOLD** for P1: the new
development regression and canonical structural-report call paths computed
confirmatory statistics despite `protocol.md:1164`, plus P3 stale docs. The
first refactor correctly moved the exact-versus-rounded counterexample to
development/calibration data, but re-review correctly held because the
canonical report still executed the real confirmatory
`_validator_primary_deltas` before and under a wraps spy.

The final remediation is commit
`1fe42a7ebc6a9ce69d8a16654e068c0a9a891d08`, parent
`70d47de1af70d380437876effe082adcfb1a70a3`, subject
`research(impl): enforce E002 development test boundary`, containing exactly
the code README, runner, and development-test paths. The final design makes
the delta helper’s `split` keyword required; production report/H2 calls pass
`confirmatory` explicitly; the structural report test installs an exact-delta
stub before generation through all validation/mutation calls and blocks
`_validator_stats`; and the dev/cal regression alone dynamically computes
exact statistics and metric/bootstrap evidence. Its rounding counterexample
remains exact token `-0.091689527` versus rounded-cell token `-0.091689526`.
The README and module docstring now state this boundary accurately.

Worker verification passed targeted `2/2` and the full standard-library-only
development suite `54/54 OK`. Independent review statically traced the calls
and passed targeted `2/2`, returning **TECHNICAL READINESS ACCEPT** with no
findings. It did not run the full suite because runner tests were outside its
read-only scope. These are implementation/reviewer checks, not experimental
evidence.

### Readiness-only evidence and state

The candidate `e002-20260825-002` has valid run-ID grammar. The three shared
E002 data paths and candidate result path were absent; staging/temp/lock paths
were absent; repository cwd/output-root assumptions were correct; Python
`3.14.5` and approximately `18 GiB` free space were nonblocking; protocol
commit/blob identity was valid; and the preserved invalid report for run 001
remains unchanged. Run 001 is still invalid only: exit code `2`,
`D9_OR_NA`, no metrics/data/evidence, and no H2 or scientific outcome.

M07 sets `technical_ready: true` subject to runtime preflight,
`implementation_reviewed: true`, and `corrected_run_authorized: false`. The
M04 authorization is consumed. Candidate 002 was not executed or reserved;
its output is absent. Metrics, data, evidence, H2 outcome, and public-claim
eligibility remain absent/false. The exact intended CLI is recorded as not
authorized and not executed. M07 therefore authorizes no run, publication,
push, or public claim.
