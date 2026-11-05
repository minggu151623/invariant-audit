# Findings

## Submission preparation — 2026-11-05, M34

R3 remains the current scientific manuscript; no science or PDF changes this
turn. The new `paper/submission-r3/` fields/guide match its 10 pages, 3 tables,
exact 1311-character abstract and current official arXiv instructions. Source
ZIP contents/CRC and R3 hashes checked; cs.DB remains a recommendation,
XeLaTeX/TeX Live 2025 and explicit font filenames match current guidance.
`paper/current-submission.json` identifies the right packet among old versions.

The owner has been asked once to approve R3 content/submission and select a
license, with the Vietnamese explanation and license comparison linked. Both
answers remain pending. No account/login, endorsement, upload, server compile,
submission receipt or public identifier is evidenced. After approval, prepare
release wording and recheck; do not remove the pending-review statement now.
See [M34 completion audit](milestones/M34-R3-submission-preparation.md).
Goal active and incomplete; this turn made concrete preparation progress.
Remaining external actions depend on owner decisions. Do not repeat unchanged
experiments or ask the same pending questions on every automatic continuation.

## Current revision — 2026-11-05, M33

The Set Cover lead is now a proved-internally complexity result: making a
rejected target accept within a cell budget is NP-complete for varying binary
singleton schemas, with every target group initially tied, in both fixed-key
and editable-key models. The reduction preserves the optimum; its converse
explicitly handles arbitrary key and support-row edits. Combined with the
polynomial rejection formula, this clarifies the directional algorithmic story.
It does not establish fixed-schema hardness or make key edits the source of
hardness. A standard fixed-q,d margin DP is noted analytically, not benchmarked.

E012's locked finite check passes all 111 instances / 222 radii and 147523
destinations across overlapping edit models. All 25490 accepting destinations
yield a budget-respecting cover; 24288 full-edit successes include key edits.
These checks are not the universal proof or independent validation. Known Set
Cover/lobbying techniques are credited, with no historical-priority guarantee.

The new R3 working preprint has 10 checked pages and preserves 197 prior
scientific artifacts, previous structural proofs and all E008--E011 empirical
text. Source ZIP compiles identically; the 12-member supplement's extracted
stdlib replay exactly reproduces the frozen grid. No new source reconstruction,
speed benchmark or accuracy result. The 30 equal rejected pairs and two full
timeouts remain. See [M33](milestones/M33-acceptance-complexity.md) and the
[Vietnamese explanation](to_human/M33-theory-progress-vi.md).

Internal assessment: now a coherent, narrow theory/algorithm preprint for
substantive author review, not a demonstrated major discovery or cleaning
system. Next resolve the owner's understanding/content questions and obtain
content approval and license choice for submission. Those are not yet given;
no account or external submission is evidenced. Independent peer review is not
being imposed as a submission-preparation gate. Goal remains active; this turn
made substantive progress, not a repeated blocked turn.

## Current revision — 2026-11-05, M32

The owner resumed the arXiv goal and instructed continuation after the candid
internal review. R2 now directly compares the specialized results to cell-based
FD repairs (Debosschere/Geerts 2015), attribute-level/null-based causality
(Bertossi v7), generic intervention partitions (Meliou et al.) and vote-operation
optimization (Xia). Generic objectives/encodings remain prior art; no worldwide
priority or independent assessment is established.

Two elementary analytical families separate whole-table FD repair distance
from protected-target decision radius by unbounded factors in either direction.
Small raw enumerations check the examples (8 cases, 285032 destinations), not
the universal proof or practical impact. The scoped use is a declared-budget
sensitivity query, not error identification or improved cleaning accuracy.

The nine-page R2 manuscript preserves the original structural statements and
E008--E011 outcome text, including the negative accepting-direction source
result. All pages visually checked; one-file extracted source compiles with
identical text; 186 previous scientific artifacts unchanged. The original CSV
cache is absent today; no fresh source reproduction is claimed. See
[M32](milestones/M32-positioning-and-revision.md) and
[R2](paper/context-edit-stability-r2/README.md).

Scientific significance remains open. Next investigate whether the accepting
direction has a sharp tractability/hardness boundary. A Set Cover construction
using binary RHS and singleton determinant rules is an unverified lead, not
included as a theorem yet. Do not obtain a favorable dataset/timing result
merely to soften E011's negative outcome. No owner approval or external peer
review gate blocks this local work. The actual arXiv publication is still absent.

## Current candidate — 2026-10-23 mutable-key action reduction (M26)

E008 extends decision-edit certification to mutable keys and RHS while protecting
the target row. Under six fixed FD families all 30642 radius comparisons match
unrestricted raw-cell edit search on 5107 tables, and all 61854 row-action
dominance checks pass. Both complete builds agree; 30618 finite witnesses verify.
210 finite protected-key radii decrease, and 7290 protected-key INF cases become
finite. These are constructed-domain counts, not accuracy or prevalence claims.

The theorem draft gives a cost-preserving target-relative key quotient and
canonical accepting actions, at most 2^q+1 per context row, plus exact programs
for both decision directions. Its proof assumes same RHS, unit cell costs and
unrestricted independent context-cell edits. Large numbers of rules/RHS values
can make the DP impractical. Originality and practical benefit remain open.
Generic counterfactual/SAT explanations already have direct prior work, so the
candidate must be judged on the specialized reduction rather than minimum edits.

Next: compare with a generic exact optimization baseline and investigate scaling
under a new protocol, while deepening the prior-work collision check. No external
peer review or owner approval blocks this local research. See
[M26](milestones/M26-E008-mutable-key-pilot.md),
[theorem draft](experiments/E008-mutable-key-certificates/theory.md), and
[Vietnamese progress explanation](to_human/M26-mutable-key-progress-vi.md).

## Current research priority — 2026-10-23 novelty reset, M24/M25

The owner requires an original contribution and correctly notes that arXiv
posting does not require peer review. Further local research is authorized;
waiting for approval of the weak audit draft is no longer the next action.
The existing draft remains preserved, without a new novelty claim.

A targeted primary-source search found direct overlap with October 2026 work
on AFD strength versus detection value, including whole-group/non-majority
semantics. Conformal cleaning, FD-repair certification and overlapping-vote
optimization are also established. See the
[collision matrix](literature/novelty-reset-20261023.md).

E007's separately locked finite pilot checks a joint RHS-edit decision-radius
formulation: all 118002 comparisons on 39334 tables match exhaustive enumeration;
114651 finite witnesses verify; 1264 two-rule cases exhibit a strict joint/local
gap. Nine unit tests and byte-identical double builds pass. This establishes
finite mathematical feasibility, not newness or detector performance. The easy
binary form is a familiar covering problem and is insufficient novelty alone.

The next candidate addresses shared determinant edits that alter multiple
rule groups, beyond protected-key certification. It still needs an exact threat
model, unrestricted-edit falsification and deep prior-work comparison. See
[M25](milestones/M25-E007-finite-certificate-pilot.md) and
[E007 analysis](experiments/E007-fd-decision-stability/analysis.md).
Earlier owner-review/submission-status sections below are historical preparation;
no peer-review gate is imposed on this research. No public upload or claim.

## Current submission preparation — 2026-10-23 (M23)

A Vietnamese reading walkthrough and concrete submission fields now accompany
M21's named paper. All 12 walkthrough percentages match E006. The exact abstract
is 1419 ASCII characters; official guidance supports XeLaTeX and the four font
filenames in the current source. No arXiv server build has been performed.
See [M23](milestones/M23-owner-reading-and-submission-preparation.md) and the
[readiness audit](paper/submission-readiness.json).

The owner-review question is pending. Name/affiliation are supplied; approval
of the contents, category/license, account/endorsement and actual posting are
not. The goal remains active and unachieved. Previous turn and this milestone
are progress; no-progress streak is zero. Further action must address a concrete
issue or human feedback, rather than manufacture experiments/status documents.

## Current delivery state — 2026-10-23 (M22)

The portable 35-file evidence bundle passes from a fresh extracted directory
without Git or the original cache: all four E005 outputs reproduce byte for
byte and E006's 720 metric comparisons and 84 interval endpoints verify.
Optional --source-root also checks all nine original source pins. The default
offline result explicitly does not verify those source bytes. Corrupted member
and optimized-Python controls are rejected. This audits frozen evidence, not a
new performance run or independent review. See [M22](milestones/M22-portable-evidence-bundle.md).

M21 remains the current named PDF; M20 the latest scientific result. Responsible
owner review and substantive scientific/archival-interest assessment remain
open. No account/submission/public-push action occurred; goal remains active.

## Current manuscript state — 2026-10-23 (M21)

The expanded 12-page manuscript now integrates E005 and E006, including all four
external policies, the false-rejection/acceptance tradeoff and the mixed Brier
prediction. User-supplied author Trần Vũ Bảo Minh, Independent Researcher,
appears correctly with Vietnamese diacritics. All final pages were inspected;
the four-file source ZIP compiles in isolation with matching text and no layout
warnings. See [M21](milestones/M21-external-reference-manuscript.md).

Owner and independent scientific review and the submission process remain
open; M22 now supplies portable evidence packaging. The goal is active; no submission or public
push occurred. M20 remains the latest scientific result. The following stages
are historical; M19's eight-page preview has been superseded.

## Current research state — 2026-10-22 external reference validation (M20)

E006-v1 adds one valid fixed-source study on Beers, Flights and Rayyan, using
outside reference corrections and fixed simple FD-attribution policies, not the
original M1. All 720 serialized point checks and 84 bootstrap quantiles pass.
Rall makes cell-reference errors in all three; Rmode reduces false rejection
relative to Rall but raises false acceptance on Flights/Rayyan. The Rmode
lookup Brier-improvement prediction is mixed: Flights CI crosses zero. This
contrasts imperfect reference agreement with the original perfect constructed
scores without establishing causal M1 transfer. The source A1 header failure
and A2 explicit metadata correction are preserved. See [M20](milestones/M20-external-reference-results.md).

At M20, the 8-page M19 manuscript needed updating; M21 now supplies that update.
E003-v2 remains unexecuted and scientific acceptance/submission remain unresolved.

## Current manuscript state — 2026-10-22 (M19)

An 8-page English working manuscript and a minimal LaTeX source ZIP now exist.
All pages were visually inspected; the 3-file ZIP compiles in isolation with
identical page text and no overflow or missing-character warnings. These are
artifact checks, not independent scientific acceptance. The user tentatively
expects sole authorship and has no arXiv account; exact name/affiliation are
unknown. The goal remains active. See [M19](milestones/M19-arxiv-working-manuscript.md)
and `paper/review-status.md`. The central next question is whether the narrow
case study has enough archival interest; deepen the evidence if needed rather
than equating formatting completion with a finished research goal.

## Current reading guide — 2026-10-22 arXiv evidence audit (M18)

The user selected an arXiv paper as the research destination. E005, separately
locked before implementation, audited the already inspected E001/E002 artifacts
with a fresh metric implementation: all 195 metric comparisons pass; exact
score-group Brier decomposition holds in all 39 split/method rows. M1 lowers
Brier by increasing resolution while finite score-group reliability worsens in
both designs. Its binary ablation has zero Brier/ECE. E001 has one distinct
statistic signature among 64 evaluation clusters; E002 has six among 48. These
are descriptive counts, not effective sample sizes. Calibration-only lookup
reconstruction is compatible with all predictions; it does not prove historical
absence of leakage. See [M18](milestones/M18-arxiv-evidence-audit.md).

Candidate paper: a bounded methods case study of perfect constructed scores and
measurement interpretation. Neither a new validation algorithm nor broad
external validity is claimed. Independent review and novelty assessment remain
open; public-claim eligibility is false. E003-v2 is unchanged at the M17 gate.
The following M17 and earlier sections are historical.

## Current reading guide — 2026-09-21 E003-v2 adapter integration (M17)

At the historical M17 stage: E001 and
E002 run 002 remain the only valid performance results, restricted to finite
synthetic designs. E003-v1 is invalid with no H3 outcome. Its old cache/manifest
was missing at resumption and is now recovered with original hashes/counts.
E004 run e004-20260917-001 found 537 byte-identical extra occurrences, 537
repeated groups of size two, zero conflicting groups and zero cross-shard
repeated IDs. No canonical-only equivalents occurred. The 2021 shard has
117,780 records and 117,243 unique IDs. This is an exploratory source diagnostic,
not H3/performance evidence. Two aggregation methods agree, with a shared parser
and one agent, not an independent reviewer. See [M15](milestones/M15-E004-source-diagnosis.md).
E003-v2 is separately locked (b9cae97); its pure source-normalization component
(87ccd69) and source adapter (28f74d5) pass all 39 synthetic tests (22 normalizer
+ 17 adapter). The adapter implements normalization -> v1 pinned pure projection/oracle
helpers -> first-reason exclusions -> all-type/all-requested-split repo isolation ->
deterministic quotas/caps/diversity, retaining original coordinates.
This is partial engineering progress, not a new scientific result. Next: complete
evaluation/calibration/bootstrap version identities, transactionality guards,
guarded 2019/2020 integration, and obtain independent acceptance before execution.
Reusing inspected sources cannot be represented as pristine holdout confirmation.
See [M17](milestones/M17-E003-v2-adapter.md).

The paper is corrected against result artifacts: E002 Brier/ECE values and CIs,
positive=valid terminology, Laplace-smoothed lookup, percentage points, and
two-split preflight scope. FPR means false acceptance, not false alarm on a valid
record. ECE increases in both comparisons; lower Brier does not prove generally
improved calibration. The historical attribution of duplicates to at-least-once
delivery/retries is withdrawn: their cause is unknown. No observed documentary
error is attributed to a worker model without evidence.

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

## M08 — E002 corrected run 002 valid result

M08 records one separately authorized, locked local E002-v1 confirmatory run.
It is an observed finite synthetic result, not a claim about production data,
external validity, novelty, safety, generalization, or public eligibility.

### Authority and execution boundary

The current bounded user brief authorized exactly one local corrected run with
ID `e002-20260825-002`, result recording, and no retry, push, publication, or
other external action. The user did not select the technical design. The
protocol, implementation, validator, gates, and artifact encodings remain
worker/reviewer design and verification work under the locked E002 protocol.

The run began at HEAD
`86ede8ac1fcd674b9cc559ee7ad2c381efa4f3d0` with a clean worktree. The locked
protocol commit `9e39c5defc89f2c2a896b53dda529f326e9dfcf8` was an ancestor and
the E002 protocol blob was
`f7d27a069ee3fd1600f89d9271e107c197033238`. Candidate final, staging,
temporary, and lock paths were absent. The cwd and output-root were the repo
root, Python was `3.13.5`, and approximately `18.8 GiB` was free. These
runtime facts satisfy the protocol's standard-library-only local CPU/no
network/API/GPU constraint; the protocol does not pin a Python minor version.

The exact command was executed exactly once, at
`2026-08-25T22:40:19+07:00`, with exit code `0`:

```text
PYTHONDONTWRITEBYTECODE=1 python experiments/E002-heterogeneous-specification-stress/code/run_e002.py --run-id e002-20260825-002 --output-root .
```

Runner stdout reported `status: valid`, result SHA-256
`d1f11d17be3b91d246126dc36b88880a76f039f31fa7eeef63d5aff4cfe713fa`, and
multi-fault relation SHA-256
`a02432ead45db3633e7cbe2f07e5314fa19dd800d9c2441da34bbfbe08510dd5` with
`equals=272`, `contains=160`, and `differs=0`. The report's gates all pass,
the two-build byte comparison passes, and deviations are literal `none`.

### Artifact and result evidence

| Artifact | SHA-256 | Size | Count |
| --- | --- | ---: | ---: |
| `data/E002-v1-predictions.jsonl` | `bcb34aad4338fdfbffe07be1843769b360bf4e8c422d855a9ce605350fad13b7` | 6,556,304 B | 7,296 rows |
| `data/E002-v1-metrics.csv` | `f000348d385550745480066fce2d691686728ebe2bfcf7bd96e7231e4b1e5ca3` | 116,260 B | 243 rows + header |
| `data/E002-v1-bootstrap.csv` | `8c5919f709c9ad8ca673308053ecefbe94ca23b0c190b923f14957cbfeac7d5d` | 30,814,607 B | 530,053 rows + header |
| `experiments/E002-heterogeneous-specification-stress/results/run-e002-20260825-002.md` | `d1f11d17be3b91d246126dc36b88880a76f039f31fa7eeef63d5aff4cfe713fa` | 6,486 B | 100 lines |

On the primary confirmatory anchor M1 minus B0, the observed serialized
deltas are:

| Delta BA | Delta FPR | Delta FNR | Delta Brier | Delta ECE |
| ---: | ---: | ---: | ---: | ---: |
| `0.401960784` | `-0.803921569` | `0.000000000` | `-0.091689527` | `0.005222762` |

The co-primary stress intervals passed, H2 was `supported`, and the FNR
guardrail passed at delta `0.000000000`. The run is confirmatory under the
locked finite synthetic design; no exploratory run was performed and no
additional analysis or retry occurred.

### Interpretation and limits

This result supports the locked E002 H2 rule only for its finite synthetic
population, hand-specified oracle, bounded mutation inventory, and defined
cluster bootstrap. It does not establish production performance, external
validity, novelty, safety, generalization, or a public claim. The prior M05
run `e002-20260825-001` remains an invalid diagnostic-only execution with its
preserved report SHA-256
`f441d55795b81d280e35b09980dcb6f79e58e7cfacbe9886ed094a207580aa34`; it was
not overwritten or converted into evidence by M08. The one-run authorization
is consumed, and any future action requires separate explicit authority and a
new bounded gate. `public_claim_eligibility` remains `false`.

## M09 — outer-loop reflection after E002

M09 is a verified documentary synthesis of the valid E001 and E002 result
records. It introduces no new run or metric. The observed evidence remains
bounded to the finite synthetic designs and `public_claim_eligibility` remains
`false`.

### What is supported

E001's valid confirmatory run supported H1 within its finite synthetic design:
M1 minus B0 had ΔBA `+0.5`, ΔFPR `-1`, ΔFNR `0`, ΔBrier `-0.2499408284`, and
ΔECE `+0.007692307692`, on 512 confirmatory cases and 64 clusters. E002's
corrected valid run supported H2 within its finite heterogeneous synthetic
design: ΔBA `+0.401960784`, ΔFPR `-0.803921569`, ΔFNR `0.000000000`, ΔBrier
`-0.091689527`, and ΔECE `+0.005222762`, on 456 confirmatory cases and 48
confirmatory clusters. E002 also passed the co-primary omit-conservation,
overconstraint, and stale-transition stress intervals.

### Mechanism/pattern

Across both experiments, B0's schema-only acceptance remained vulnerable to
schema-valid semantic/state faults, while M1's cross-field semantic/state
families rejected those faults in the locked synthetic cases. Removing
semantic or state checks reduced E001 BA to `0.75` and FPR to `0.5`; the E002
no-semantic and no-state ablations each had BA `0.823529412` and FPR
`0.352941176`. This is a within-design mechanism inference, not evidence of
real-world performance.

### Lessons and remaining gaps

E002's heterogeneous clusters and bounded specification/multi-fault stress
addressed the principal E001 design weaknesses, but the oracle and cases are
still synthetic and hand-specified. E001's intervals were degenerate; E002's
nondegenerate intervals still describe its finite designed resampling. The
first E002 attempt also demonstrated that exact arithmetic and independent
validation are part of the evidence boundary, not implementation polish.

The largest unresolved gap is external/real-world transfer: externally
authored structured records, source/schema drift, natural irregularity,
natural invalid prevalence, sequence-level behavior, and an oracle boundary
less coupled to generated recipes. More synthetic cases would not directly
answer that gap.

### Direction decision

**BROADEN.** This is the reviewer/design decision for the next stage. DEEPEN
would continue synthetic stress without addressing external validity; CONCLUDE
would be premature because the critical transfer question is open; PIVOT is
not supported because the two results show a coherent repeated pattern. The
next bounded action is a protocol-only E003 external-transfer design with a
frozen public fixture, explicit acquisition hash, split isolation, an
independent oracle boundary, and no run authorization.

The current stopping gate is therefore: lock E003-v1 protocol only; do not
acquire the fixture, implement code, run E003, create E003 data/results, or
make a public claim in this stage. See [M09](milestones/M09-outer-loop-after-E002.md)
and the [M09 progress presentation](to_human/progress-M09.html).

## M10 — E003 protocol-only external-transfer design

M10 records the BROADEN decision as a protocol-only design step. It introduces
no E003 acquisition, implementation, execution, prediction, metric,
bootstrap, result, or public claim. `public_claim_eligibility` remains
`false`, and the source snapshot is explicitly `staged_unacquired`.

The capped E003 source set is the GH Archive official site
(<https://www.gharchive.org/>), GitHub's official event-types documentation
(<https://docs.github.com/en/rest/using-the-rest-api/github-event-types>), and
Kalliamvakou et al.'s primary GitHub-mining study
(<https://doi.org/10.1007/s10664-015-9393-5>). These sources ground only the
archive/event-contract boundary and a validity caution; they do not establish
an E003 outcome. The exact fixture URLs, staged acquisition and hash plan, and
the no-substitution rule are recorded in
[the E003-v1 protocol](experiments/E003-external-transfer-validation/protocol.md).

The protocol defines H3 on three preselected, time-separated GH Archive hourly
shard URLs with 64 IssuesEvent and 64 PullRequestEvent bases per split, four
paired clean or mutated cases per base, B0/M1 plus predeclared ablations,
calibration-only lookup fitting, an independently maintained oracle,
repository-cluster bootstrap uncertainty, and explicit
source/schema/isolation/determinism gates. The sole planned stopping point is
one valid confirmatory run; a valid `mixed/not supported` outcome is terminal,
while any preflight or integrity failure is invalid with no metrics or
evidence. The next action requires separate authority for source acquisition,
implementation/review, and exactly one run; this milestone authorizes none of
those actions.

## M11 — E003 source acquisition freeze and cache remediation

M11 records the completed local audit and reversible remediation of the exact
E003-v1 source cache. This is source provenance and format-validation evidence
only. It is not an E003 result, implementation, metric, or public claim.

The starting Git HEAD was
`b68424e756fb86f05c866647b2471d36e24da716`. The locked protocol commit
`163e44dcabc698f101dee70dd7f3aa1bb7c8d5fb` remains an ancestor and its
protocol blob SHA-256 remains
`8ec0ebc9b3420a2d71eebfe579ae2d1c87aa74c419dd3f38d1f0dc06c5c1e2a6`.

The canonical UTF-8/LF manifest remains outside Git at
`/private/tmp/invariant-audit-e003-v1/source-manifest.json`, with SHA-256
`683eef39cd26d2a7f6622689adc2cd9e357e78a770f77bf91e98513b859e4633`. The
updated metadata sidecar is
`/private/tmp/invariant-audit-e003-v1/acquisition-metadata.json`, with SHA-256
`5937fbf7d8583ed3954b7d107146af331d29f2a14e224d883e892c74ce52388a`. Its
canonical local-only freeze-event object hashes to
`17ac5e9eb4386ef2d6f4f34996f240e600b16d7521fdcc6b91dfd10630c27ed7`.

| Split | SHA-256 | Bytes | JSONL lines | HTTP |
| --- | --- | ---: | ---: | ---: |
| development | `ae451576f78417d75f135b29ee67ea8e666dc5f6cb16e78cef04e20342b42b50` | 29278679 | 67145 | 200 |
| calibration | `624a0d2a2fc575afb1e63bece53521e2b078ddfd1caf60026e313ad36d83cddd` | 46372480 | 90940 | 200 |
| confirmatory | `a4a80c97153c691866d52b7e06ea0051f2449f0c6f8060dad9f441a69cd13788` | 61805367 | 117780 | 200 |

All three payloads and the manifest were re-verified locally. Gzip
decompression, strict UTF-8 decoding, and one-JSON-object-per-nonempty-line
validation passed; the manifest and all payload bytes are unchanged. The
audited cache inventory is exactly the three `.json.gz` files above, with no
`.headers` sidecars. The former sidecars were moved, not deleted, to
`/private/tmp/invariant-audit-e003-v1-remediation-archive-20260901/`; their
SHA-256 values are
`0e9f751b9c213201b49900c94d58776488ddc6c1b7994b06d7530574b100dfd8`,
`d33afd6da92f991d7fabef3d27a2e7df05ba21984aa04b27da01764c19636322`, and
`761ffd6482919336cb57682c9c211843770ad187ed280bec7faf49d59d4d8815`,
respectively. The pre-remediation metadata copy is also
preserved there with SHA-256
`6d47ea164f42a02b69fad37c466cd7253bb7f07b3f6a1985534fc2b657b9554f`.

The authoritative local-only freeze event occurred at
`2026-08-31T19:59:22Z` UTC after manifest/payload verification, records the
exact three-file inventory and starting HEAD, and states that remediation used
no network. The prior metadata value `network_frozen_at_utc:
2026-08-31T19:06:24Z` predates the observed manifest mtime
`2026-08-31T19:07:45Z`; that original chronology is not independently
supported, was not rewritten or backdated, and is retained only as historical
context.

Confirmatory isolation is preserved: the confirmatory file was touched only
for hash, byte, line-count, and format validation, not for event selection,
projection, calibration, scoring, metrics, bootstrap, or result generation.
No E003 output path exists. E003 remains `implementation: absent`,
`run: absent`, `results: absent`, and `public_claim_eligibility: false`; the
next gate requires separate authority and independent review for
implementation and exactly one confirmatory run.

## M12 — E003 implementation-readiness

M12 records implementation and development/calibration-only verification. It
is not an E003 result and does not authorize a confirmatory run. The current
state is `implementation_remediated_pending_independent_re_review`.

### Implementation and integration evidence

The scoped standard-library implementation is in
[the E003 code directory](experiments/E003-external-transfer-validation/code/),
with a separate fail-closed oracle, explicit future-run runner, and synthetic
plus guarded integration tests. Two independent preflight builds opened only
`2019-01-15-12.json.gz` and `2020-01-15-12.json.gz`; the guard would raise on
`2021-01-15-12.json.gz`.

| Measure | Development | Calibration |
| --- | ---: | ---: |
| selected bases | 64 IssuesEvent + 64 PullRequestEvent | 64 IssuesEvent + 64 PullRequestEvent |
| cases | 512 | 512 |
| selected repositories | 103 | 92 |
| eligible events after isolation | 5,408 | 9,435 |

There were 2,178 shared repository IDs between the two scanned groups; all
were excluded before selection. Selected repository overlap was zero. The
combined raw scoring count was 5,120 rows, and calibration fitting used only
calibration rows. The manifest hash was
`683eef39cd26d2a7f6622689adc2cd9e357e78a770f77bf91e98513b859e4633`.

Calibration lookup serialized-byte SHA-256 values were:

- B0: `2d5d789ed71d73772e62c29eebdce252eee0e6dfe46965ceec676de424463058`;
- M1: `02b1d8bddcb941bde65c59499e1799ee559abc9f62ef42755850ab11b5c0c6a2`;
- M1-no-identity: `370cd8fa7f24bffe5c72a41e8a1e2f5f93e68f2bba88cb88518a475e89c573d5`;
- M1-no-state: `0e786b395a7af8913bdb8fcb2b02957448f94ed9587a471759a73c3f0623e98b`.

The deterministic projection signature was
`8adb4a38cbe92aed57d37c3e8e0812299e6dc57072434061427624ad6fda0f53`.
The two independent preflight builds were equal, including lookup bytes and
hashes. No confirmatory metrics, predictions, bootstrap, or result report was
constructed.

### Development remediation record

The first 25-test diagnostic run had six failures: four failures and two
errors. Two were real implementation defects: cross-split exclusion counts
were initialized in a way that mixed tuple and string keys during sorting, and
the calibration callers passed development rows into the lookup fitter. Four
were fixture/assertion mismatches: the ablation expected sets, the synthetic
bootstrap fixture omitted the pull-request subgroup, the smoothed lookup
expected `1/3` instead of `1/8`, and a temporary-directory assertion retained
fixture-created directories. The scoped fixes were applied and the pre-remediation
25/25 suite passed. This is implementation remediation evidence, not E003
experimental evidence.

### State boundary

The final standard-library-only suite passed 29/29 in 16.897 seconds (17.04
seconds wall time), and `py_compile` passed. Confirmatory run, predictions,
metrics, bootstrap, result, and production output paths remain absent;
`run_authorized: false`, `run: absent`, `results: absent`, and
`public_claim_eligibility: false` remain explicit. Independent implementation
review and separate run authority are the next gate.

### Independent-review HOLD and remediation

The initial independent review was **HOLD** for four findings: P1 audited
manifest pinning before payload reads; P1 complete per-source exclusion counts;
P2 measured production oracle-independence perturbation gates; and P2
provenance placeholder state. The bounded remediation from initial HEAD
`2671e8eba6e873206cb8ffbb88439aef275e5b8f` pins the audited manifest
`683eef39cd26d2a7f6622689adc2cd9e357e78a770f77bf91e98513b859e4633`, validates
all exclusion entries, flows measured gate evidence through artifacts, and
records the real implementation commit. The focused four-test regression set
passed; the full suite passed 29/29 in 16.897 seconds (17.04 seconds wall).
The current state is `implementation_remediated_pending_independent_re_review`;
confirmatory execution and E003 output remain absent and unauthorized.

## M13 — E003 run 001 invalid execution and source-integrity failure

M13 records the local confirmatory execution authorized under user directive
`user-2026-09-03-e003-goal`. It is documentary invalid-run evidence and an
empirical source-integrity finding; no valid E003 result exists.

### Observed invalid run

- Run ID: `e003-20260903-001`
- Command: `python3 experiments/E003-external-transfer-validation/code/run_e003.py --run-id e003-20260903-001 --output-root . --source-manifest /private/tmp/invariant-audit-e003-v1/source-manifest.json`
- Started at: `2026-09-03T20:35:54+07:00`
- Exit code: `2`
- Runner failure: `pre-staging pipeline failure: duplicate event ID across source: confirmatory:16450 and confirmatory:16491`
- Invalid report: [run report](experiments/E003-external-transfer-validation/results/run-e003-20260903-001.md)
  with SHA-256 `5bf6c545f43333a6a3cc0d8ea8a8b2d3f7adfb4be0c0358d1cd75c17a8254305`
- The report is 258 bytes and 8 lines, has status `invalid` and failure class `invalid-run`,
  and requires a new ID for a corrected run.
- No metrics, evidence, or data outputs exist. No H3 outcome is established.

### Independent empirical diagnosis

The independent empirical investigation of the external fixtures revealed:

| Shard | File | Records | Duplicate event IDs |
| --- | --- | ---: | ---: |
| development | `2019-01-15-12.json.gz` | 67,145 | 0 |
| calibration | `2020-01-15-12.json.gz` | 90,940 | 0 |
| confirmatory | `2021-01-15-12.json.gz` | 117,780 | 537 |

1. Cross-shard duplicate event ID count across 2019, 2020, and 2021 is exactly `0`.
2. The confirmatory shard (`2021-01-15-12.json.gz`) contains exactly 537 duplicate event IDs (representing duplicate lines in the hourly stream).
3. The first collision occurs between line 16450 and line 16491: `id=14832202395`, type `PushEvent` on repository `La-Z-fandy/Personalsite.github.io`.
4. Distribution across event types: PushEvent (289), CreateEvent (68), WatchEvent (38), PullRequestEvent (34), IssueCommentEvent (26), IssuesEvent (19), and other events (63).
5. Root cause: In upstream production telemetry, GH Archive and GitHub API event feeds are subject to at-least-once delivery semantics, where network retries or polling window overlap cause repeated event delivery.
6. Protocol conflict: Locked protocol E003-v1 lines 150-153 and 201-202 explicitly mandated:
   > *"The source record's raw `id` is the canonical `event_id` and must be unique across all three shards. Any duplicate event ID, including a duplicate with different bytes, is a source-integrity failure; no deduplication choice is permitted."*
   > *"1. Parse one JSON object per nonempty line; reject the entire run if a line is malformed, duplicated by event ID, or not an object."*
7. Scientific classification: This is an **authentic external transfer mismatch**: the synthetic protocol assumed clean, duplicate-free event streams, while real-world production software telemetry contains at-least-once duplicate delivery. The runner correctly executed fail-closed enforcement and rejected the run.

### State and next gate

M13 is the current milestone.

- `run_authorized: false`
- `authorization_consumed: true`
- `run: invalid` for `e003-20260903-001`, exit code `2`
- `results: invalid_report_only`
- `metrics: absent`
- `evidence: absent`
- `data: absent`
- `public_claim_eligibility: false`

The next gate requires an outer-loop decision:
1. Formulate and lock `E003-v2` with realistic streaming deduplication (e.g., deduplicate upon first occurrence in line order or record duplicate delivery as an explicit natural exclusion class).
2. Or acquire an alternative public hourly snapshot that happens to possess zero duplicates.
Any future run requires a protocol lock, new run ID, and clean preflight.

## M27 — singleton bottleneck for initially accepted targets

Under protected targets, same-RHS unique plurality and independent unit-cost
context edits, a nonsingleton target group's exact rejection cost is
ceil((target_count-largest_rival_count)/2), even with editable keys. A singleton
group's exact cost is the cheapest context-row import: differing determinant
cells plus a needed RHS edit. Global rejection is a disjunction, so take the
minimum rule cost. Equivalently rho_fixed=A and rho_full=min(A,S): keys help
exactly when S<A. A singleton is necessary but not sufficient for a reduction.
See the full E009 proof; this does not apply to the joint accepting direction.

All 18779 initially accepted formula/oracle cases and 2118 generic raw-cell MILP
comparisons pass. These are finite mathematical checks, not empirical accuracy,
prevalence, runtime improvement or independent assessment. Generic vote
operations and repair work substantially overlap the framing; originality of
the specialized characterization/action reduction remains open. A separately
locked direction-separated scaling comparison is the next falsification gate.

## M28 — the structural candidate has bounded computational value

E010 validates generalized implementations on 162 raw-oracle fixtures and
compares a direct accepted formula / canonical accepting MILP against the
verified generic raw-cell MILP on 72 constructed cases. All specialized calls
are exact; the generic model times out 14 times across seven dense accepted
cases. Among all 24 rejected cases, both methods finish exactly twice; median
case-level total-time ratio generic/specialized is 2.9967, with one slower
specialized case. Neither that case nor censored observations is omitted.

The distinction between the easy rejection disjunction and the joint accepting
problem yields a plausible contribution-centered story. This evidence is
bounded by small n, q<=6, a shared machine and generator regimes that exclude
mixed target-valued RHSs from rejected contexts. Practical prevalence, factual
correctness and originality remain open. A meaningful reused-source study and
closest-prior-theorem check are required next; neither old owner review nor
external peer review blocks that local research.

## M29 — external-table impact is concentrated in singleton groups

The complete reused-source census has 13762 accepted targets; 1134 have a
strict key-related reduction, comprising 1133 fixed-INF transitions and only
one finite 2-to-1 decrease. The exceptional finite case is Rayyan journal_title
row 644, whose groups have sizes 4 and 1. The source result supports the exact
singleton mechanism but does not suggest broad finite-radius improvements.

All 30 exact pairs in the bounded rejected subset have equal costs. Two full
Rayyan title models time out at five seconds; fixed-key optima are 104 and full
optima remain unestablished. This narrows practical claims for accepting MILPs.
The 1493 reference-disagreeing accepted targets with full radius>=2 reinforce
that stability does not imply correctness. These are reused-source finite
counts, not representative prevalence or accuracy improvements.

Generic predicate partitions, minimum interventions and score-margin ILPs are
prior ingredients. Remove the key quotient from novelty claims. A focused
structural preprint can center on the specialized row-action dominance proof
and singleton radius characterization, with complete assumptions and negative
results. Further experiments solely seeking a positive H11b are unwarranted.

## M30 — manuscript now follows the structural result

The current draft is Exact Context-Edit Stability for Plurality-Based
Functional-Dependency Checks, a seven-page dedicated LaTeX project. It leads
with the same-RHS protected-target unit-cost model, proves both specialized
results and keeps reused-source negative/censored outcomes in the abstract
and main results. It no longer presents benchmark auditing as sufficient
method novelty. Generic predicate quotients and intervention optimization
are expressly credited as prior ingredients.

PDF/source compilation, all-page inspection, font embedding, exact author
name and nine E011 table bindings pass. This is an editable working draft,
not approved content or an arXiv record. Portable evidence packaging and
claim-to-artifact coverage are the next local steps.

## M31 — evidence is portable; publication remains unproven

The new structural companion makes the finite evidence and source-dependent
checks explicit. Default offline verification re-evaluates tiny raw optima,
serialized witnesses, inputs, medians and censoring while marking source raw
checks absent. The optional layers reconstruct E008/E009 finite evidence and
E011 source radii/labels/witnesses without Git, solvers or hidden cache fallback.
All extracted/optimized/relocated and negative-control checks pass. This is
reproduction/self-review, not an all-input proof or novelty certificate.

The completed review packet and exact new metadata now justify asking the
owner about the new content, license and account status. Old audit approval
was never given; supplying a name or a goal continuation does not approve
publication. Independent peer review is not required for this preparation.
No actual submission, server PDF or public arXiv record is present, so the
original goal is not achieved.
