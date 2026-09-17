# InvariantAudit: Semantic and State Validation in Two Finite Synthetic Designs

Status: corrected working draft, 2026-09-17; preliminary, not publication-ready.
This draft supersedes numerical and interpretive errors in commit 265bd55.
Public-claim eligibility remains false. No external performance result exists.

## Abstract

We compare a schema-only validator (B0) with an invariant-aware validator (M1)
in two deterministic synthetic constructions. The positive class is valid:
false positives are invalid cases accepted, and false negatives are valid
cases rejected. On E001, M1 improves balanced accuracy by 0.5 and reduces
false acceptance by 1.0, without increasing false rejection. On E002, these
differences are 0.401960784, -0.803921569, and zero; the locked specification-stress
diagnostics also pass. Brier scores decrease, but fixed-bin expected calibration
error (ECE) increases in both comparisons. E003-v1, an attempted external-fixture
evaluation, stopped at its duplicate-ID source gate and produced no performance
metrics or H3 outcome. These results support the specified finite comparisons,
not production performance, general calibration improvement, or external validity.

## Question and methods

The project asks how semantic and state invariants can be validated while
measuring false acceptance, false rejection, and probability-score behavior.
The user approved this direction in [M00](../milestones/M00-research-direction.md).
Detailed experiment designs are AI-suggested, not user-selected.

E001 uses synthetic entity/ledger/event bundles with identity, conservation,
transition-legality, and revision-consistency relations. E002 adds six
heterogeneous synthetic signatures, bounded multi-fault recipes, a separately
implemented replay/conservation oracle, and omission, overconstraint, and
stale-transition checker regimes. These are constructed cases, not sampled
repositories or measurements of naturally occurring software errors.

B0 checks each protocol's structural constraints. M1 also checks its selected
semantic/state relations. This concerns the specific B0 implementation; it does
not prove that every schema language is incapable of relational checks.
The no-semantic and no-state ablations remove their respective predicates.

Each calibrated method fits a lookup on its calibration split:
`p_valid(s) = (k_s + 1)/(n_s + 2)`, with a calibration-wide fallback for unseen
scores. This is Laplace-smoothed empirical lookup, not isotonic regression.
Classification decisions do not change with this confidence transformation.
The no-calibration ablation uses the binary M1 decision as its probability.
See the [E001 protocol](../experiments/E001-synthetic-invariant-calibration/protocol.md)
and [E002 protocol](../experiments/E002-heterogeneous-specification-stress/protocol.md).

With positive=valid, FPR is the fraction of invalid cases accepted; FNR is the
fraction of valid cases rejected. Balanced accuracy averages valid acceptance
and invalid rejection rates. Brier is mean squared probability error. ECE uses
ten fixed probability bins and compares each bin's mean p_valid with mean truth.
Brier is not a pure calibration measure; see the existing
[literature foundation](../literature/survey.md#probability-confidence-and-calibration).

The primary M1-minus-B0 rule requires the 95% paired cluster-bootstrap BA
interval to be strictly positive, the FPR interval strictly negative, and the
point FNR delta nonpositive. E002 additionally requires its subgroup-direction
and three co-primary stress conditions. Secondary confidence metrics do not
determine whether H1/H2 is supported.

## E001: valid finite synthetic result

Run `e001-20260825-001` has 256 development, 256 calibration, and 512
confirmatory cases. The confirmatory set contains 64 clusters and uses 10,000
paired bootstrap replicates. These numbers come from the
[locked result](../experiments/E001-synthetic-invariant-calibration/results/run-e001-20260825-001.md).

| Metric | B0 | M1 | Delta M1-B0 |
| --- | ---: | ---: | ---: |
| Balanced accuracy | 0.5 | 1 | 0.5 |
| FPR (false acceptance) | 1 | 0 | -1 |
| FNR (false rejection) | 0 | 0 | 0 |
| Brier | 0.25 | 0.00005917159763 | -0.2499408284 |
| ECE | 0 | 0.007692307692 | 0.007692307692 |

H1 is supported under the locked rule. All paired intervals collapse to their
point estimates because the constructed cluster signatures are identical.
This does not establish negligible uncertainty beyond the finite construction.
Both no-semantic and no-state ablations have BA 0.75 and FPR 0.5.
The no-calibration ablation already has Brier=ECE=0 and identical decisions:
this experiment does not demonstrate a benefit from adding the lookup.
The secondary prediction of lower ECE was not supported.

## E002: latest valid performance result

Run `e002-20260825-002` has 912 cases in 96 synthetic clusters in total;
228/228/456 cases form the development/calibration/confirmatory sets, with
48 confirmatory clusters. These values and all intervals below come from the
[valid report](../experiments/E002-heterogeneous-specification-stress/results/run-e002-20260825-002.md).

| Metric | B0 | M1 | Delta M1-B0 | 95% paired bootstrap CI for delta |
| --- | ---: | ---: | ---: | --- |
| Balanced accuracy | 0.598039216 | 1.000000000 | 0.401960784 | [0.383254717, 0.422077922] |
| FPR (false acceptance) | 0.803921569 | 0.000000000 | -0.803921569 | [-0.844327177, -0.767281106] |
| FNR (false rejection) | 0.000000000 | 0.000000000 | 0.000000000 | [0.000000000, 0.000000000] |
| Brier | 0.091937429 | 0.000247903 | -0.091689527 | [-0.096349544, -0.087346241] |
| ECE | 0.007408873 | 0.012631635 | 0.005222762 | [0.003377133, 0.007432312] |

Delta BA is a 40.1960784 percentage-point increase, not a 40.2% relative gain.
Deltas are calculated from exact statistics before rounding, rather than by
subtracting displayed rounded cells. H2 is supported and the FNR guardrail
passes. Co-primary d1 has delta FPR 0.352941176 and CI
[0.340425532, 0.366412214]; d2 and d3 each have delta FNR 1 and CI [1,1].
Omission accepts invalid conservation cases; overconstraint and stale rules
reject valid cases. These bounded failures do not demonstrate robustness to
arbitrary incorrect specifications.

Run 001 remains invalid: exact-versus-rounded Brier arithmetic in its report
validator caused `D9_OR_NA`. Its report is not part of H2 evidence.
The valid run followed an implementation correction and separate authorization;
see [M08](../milestones/M08-E002-run-002-valid.md).

## E003: invalid source gate, no external performance result

E003-v1 preselected three GH Archive hourly shards. M11 records 67,145,
90,940, and 117,780 records, totaling 275,865 source records. This is an input
inventory, not the number of evaluated cases. E003 would select external clean
events and create artificial negatives, so even a valid run would not estimate
naturally occurring error prevalence.

The M12 preflight scanned only development/calibration: 2,178 repository IDs
shared by those two groups were excluded. Its 5,408 and 9,435 eligible-event
counts do not establish isolation across all three shards.
The implementation review was HOLD followed by remediation; M12 still says
independent re-review pending. No independent re-review acceptance is established
by the preserved M13 record.

Run `e003-20260903-001` exited 2 on duplicate event IDs at confirmatory lines
16450 and 16491. The locked protocol rejects any duplicated ID before type
filtering and forbids deduplication. No predictions, metrics, bootstrap, or H3
outcome were produced. [M13](../milestones/M13-E003-run-001-invalid.md) reports a
subsequent diagnostic count of 537 duplicate occurrences in the 2021 shard and
zero in the earlier shards. At resumption the external temporary cache/manifest
were missing, so those historical counts required recovery and re-verification.
Follow-up source diagnosis is tracked separately as E004 below.

Duplicate IDs alone do not identify a delivery mechanism. Retries, overlapping
collection, or other causes remain hypotheses; no source in the repository
establishes the cause of these particular duplicates. The former attribution
to at-least-once delivery is withdrawn. Any revised policy must first distinguish
identical repeats from conflicting payloads and preserve the invalid v1 record.

## E004: exploratory source diagnosis, not performance validation

The separately locked E004 protocol was implemented before one clean-tree run
`e004-20260917-001`. The three original shards were recovered with every pinned
compressed hash, byte size and record count matching; the reconstructed manifest
also matches. The [diagnostic report](../experiments/E004-source-duplicate-diagnosis/results/e004-20260917-001.md)
finds 537 extra occurrences in 537 ID groups in the 2021 shard, all with full
raw-line SHA-256 equal to the first occurrence (excluding line terminators).
Every repeated ID occurs twice: 117,780 records contain 117,243 unique IDs.
No conflicting full canonical object, formatting-only equivalent, earlier-shard
duplicate or cross-shard repeated ID was found. This does not prove repository
independence or identify the delivery mechanism.

Nineteen synthetic tests pass; dictionary and sort/groupby aggregation agree.
These share a parser and one author, so they are not independent review. E004
is exploratory follow-up informed by M13, on only three fixed shards. Its result
supports proposing conservative exact-repeat collapse in E003-v2, not its
general safety. A separate protocol and implementation/review gate remain
necessary; reuse of inspected sources must not be called pristine confirmation.

## Limitations and conclusion

E001's oracle is recipe-coupled; E002's separately implemented oracle still
shares a hand-specified synthetic design. Bootstrap intervals describe the
finite resampling scheme, not a representative population. ECE worsens in both
M1-B0 comparisons despite lower Brier; improved probability calibration is not
established. E003 failed before evaluation. No production, external-validity,
generalization, novelty, safety, or public-claim conclusion follows.

Within two locked finite constructions, M1 rejects more invalid cases than B0
without increasing rejection of valid cases. The unresolved question is transfer
to external records under a defensible, predeclared source policy. Source
duplication has now been diagnosed in E004. E003-v2 design is subsequent work;
neither the diagnostic nor a revised policy retroactively validates E003-v1.
