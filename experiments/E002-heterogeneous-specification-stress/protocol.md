# E002-v1 — Heterogeneous specification stress

Status: locked protocol design only. This file is intended to be locked by the
dedicated commit with subject
research(protocol): lock E002 heterogeneous specification stress. The lock
commit is reported in the M03 record and in the git evidence because a commit
cannot contain its own full hash. The required parent is
4494ed80af0dec9b57b183877cb5ed3a8270c3db.

Protocol ID: E002-v1
Milestone: M03
Protocol path: experiments/E002-heterogeneous-specification-stress/protocol.md
Run authorization in this documentary update: false
Implementation, run, result, and data status: absent

## Provenance and boundary

The direct primary and official sources listed in the source map below support
only the named technical concepts. Every numerical parameter, case recipe,
checker regime, split, metric threshold, output field, gate, stopping rule,
and implementation constraint in this protocol is a reviewer/design
inference. None of those details is a user-selected technical design or an
observed result. The user message supplies high-level continuation authority
to design and locally lock the next outer-loop protocol; it does not select
any E002 choice.

This protocol is synthetic-only. It makes no claim about production systems,
external validity, novelty, safety, or generalization. It is a measurement
design for a future implementation and one future confirmatory run. Locking
this file creates documentary updates to the protocol, milestone, state,
research-state pointer, research log, findings, literature, and README
indices. It creates no executable E002 code or implementation, run,
experimental data/results/output, figure, or ARA artifact.

## Source map: facts versus design choices

The literature survey records the direct URLs and the source-fact wording.
The implementation must preserve this boundary.

| Source | Supported primary/official concept | What it does not establish |
| --- | --- | --- |
| Stocks and Carrington, IEEE DOI https://doi.org/10.1109/32.553698 | A specification-based testing framework can use models to organize test data, test purposes, and test oracles. | It does not establish that the E002 specification is correct. |
| Robert M. Hierons and Mercedes G. Merayo, *Mutation testing from probabilistic and stochastic finite state machines*, publisher DOI https://doi.org/10.1016/j.jss.2009.06.030 and [ScienceDirect article](https://www.sciencedirect.com/science/article/pii/S0164121209001356) | Specification mutation can model incorrect specifications and derive tests that distinguish a mutant from an original. | It does not select E002's mutation operators or show a checker result. |
| McKeeman, official HP Journal PDF https://www.hpl.hp.com/hpjournal/dtj/vol10num1/vol10num1art9.pdf | Differential testing compares independently produced results to reduce the cost of deciding whether a generated test exposes a behavioral difference. | Agreement between two implementations is not an external proof of correctness. |
| Cameron, Gelbach, and Miller, DOI https://doi.org/10.1162/REST.90.3.414 | Clustered dependence and small-cluster inference require cluster-aware treatment; their paper studies cluster bootstrap procedures. | It does not validate the E002 resampling algorithm or thresholds. |
| Hagemann, DOI https://doi.org/10.1080/01621459.2016.1148610 | Cluster-robust bootstrap inference can address small, heterogeneous clusters. | It does not guarantee valid inference for this synthetic design. |
| Kuhn, Wallace, and Gallo, DOI https://doi.org/10.1109/TSE.2004.24 | Software failures can be caused by combinations of conditions, motivating bounded interaction analysis. | It does not imply exhaustive interaction coverage here. |
| Yan, Liu, and Li, DOI https://doi.org/10.1109/QRS-C.2017.11 | Multi-fault interactions can produce behavior that is not a simple sum of isolated fault effects. | It does not determine E002's multi-fault truth labels. |
| NIST, official publication https://www.nist.gov/publications/combinatorial-software-testing | Combinatorial testing can exercise all combinations up to a pre-specified interaction strength. | E002 uses a bounded recipe inventory, not exhaustive coverage. |

The six cluster types, 96-cluster allocation, 912-case inventory, five oracle
families, checker names, H2 rule, bootstrap count, public-size budget, and all
other choices below are reviewer/design inference. They are deliberately
predeclared so that a future implementation cannot select them after seeing
confirmatory metrics.

## Question, estimand, and claims

The locked question is: on deterministic synthetic records whose base clusters
have deliberately non-identical signatures, how do a schema-only checker, an
exact specification checker, and three predeclared misspecified checkers behave
on valid, single-fault, and bounded multi-fault cases?

Specification stress is co-primary with the heterogeneous M1-minus-B0 anchor.
The anchor estimand is the case-weighted confirmatory difference in balanced
accuracy, false positive rate, false negative rate, Brier score, and ten-bin
expected calibration error. The co-primary stress estimands are three
denominator-valid directional degradations, each computed on a predeclared
eligible subset and paired cluster bootstrap:

| Diagnostic | Pair and metric | Eligible cases | Expected degradation |
| --- | --- | --- | --- |
| d1 omit-conservation | M1-omit-conservation minus M1 FPR | truth-negative cases with schema-valid payload and conservation in the independently recomputed oracle failure set | omission raises false positives |
| d2 overconstraint | M1-overconstraint minus M1 FNR | valid cases whose unmutated base has at least one active-to-active edge | rejecting active-active raises false negatives |
| d3 stale-transition | M1-stale-transition minus M1 FNR | valid cases whose unmutated base has at least one pending-to-closed edge | omitting pending-closed raises false negatives |

The originally suggested d1 FNR on an all-truth-negative subset and d2/d3
FPR on all-truth-positive subsets would have a zero denominator under the
positive class truth=1 convention. The locked bounded alternative above uses
the class-appropriate complementary error rate: FPR for a negative-only
subset and FNR for a positive-only subset. This is a denominator-valid design
inference, not a post-hoc metric substitution.

The predeclared hypothesis is H2:

> On the confirmatory split, M1 improves balanced accuracy and reduces false
> positive rate relative to B0 without worsening the false negative rate, while
> the direction is not confined to a single cluster type.

The heterogeneous-anchor component passes only when all of these conditions
hold:

1. The overall paired 95 percent interval for delta balanced accuracy
   (M1 minus B0) has lower endpoint strictly greater than zero.
2. The overall paired 95 percent interval for delta false positive rate has
   upper endpoint strictly less than zero.
3. The overall point delta false negative rate is less than or equal to zero.
4. Every nonempty cluster-type subgroup has point delta balanced accuracy
   greater than or equal to zero, and at least four of the six cluster-type
   subgroups have a strictly positive point delta.

H2 is supported only when all of the following hold:

1. The anchor conditions above hold.
2. The d1, d2, and d3 interval statuses are valid, each has all 10,000
   usable replicates, and each lower endpoint is strictly greater than zero.
3. The required anchor balanced-accuracy and false-positive-rate intervals
   are valid with all 10,000 usable replicates.

The exact required interval keys are
primary|overall|balanced_accuracy|M1-B0,
primary|overall|fpr|M1-B0,
stress|d1|fpr|omit-M1,
stress|d2|fnr|over-M1, and
stress|d3|fnr|stale-M1. The overall FNR point and cluster-type balanced
accuracy points are required for the anchor rule, but their intervals are
descriptive and not additional H2 interval gates. Any partial or undefined
required interval, undefined required point denominator, failed gate, or
failed strictly-positive stress lower bound yields the exact outcome label
mixed/not supported. Descriptive intervals, including expected partial or
undefined intervals for single-class case-kind subgroups, never by themselves
make H2 unreachable. The rule is a reviewer/design inference within this
finite synthetic design, not a general scientific threshold.

## Locked base generator

### Canonical representation and determinism

The future implementation must use only the Python standard library and local
CPU execution. It must set no random seed and use no random module, wall clock,
process ID, filesystem order, locale-dependent formatting, network, API,
dependency, or GPU input. Every derived integer comes from SHA-256 of an
explicit UTF-8 string and a fixed big-endian byte slice.

Canonical JSON is UTF-8 with sorted object keys, compact separators, and
ensure_ascii enabled. Hashes are lowercase hexadecimal SHA-256 hashes of those
canonical bytes. The canonical payload has exactly these top-level keys:

    meta
    entities
    ledger
    events

The validator receives only that payload. Cluster type, cluster ID, split,
signature, case kind, recipe, intended fault set, truth, and oracle reports
are never fields in the validator input.

All repository text bytes use UTF-8 without a BOM, LF line endings, and no CR
bytes. Canonical JSON used as a hash input has no trailing newline. JSONL has
one canonical JSON object per line and exactly one LF after every line. CSV
and Markdown have exactly one final LF and no trailing whitespace. JSON
booleans are lowercase true and false. There is no JSON null in a valid
prediction or manifest row.

All non-integer numeric values use exact rational arithmetic until serialization
and then the fixed nine-place decimal form: round half-even to nine digits
after the decimal point, emit a leading zero, retain exactly nine places, and
normalize negative zero to 0.000000000. JSON number tokens use this decimal
text without quotes; integer values use base-10 digits without a decimal point.
There are no NaN, infinity, exponent, locale, or binary-float encodings.
Literal NA is used only in CSV and Markdown fields whose protocol schema
permits undefined values; it is never a JSON value. Lists are ordered by
their locked semantic order or, for fault_set, oracle_failure_set, and
base_structure_flags, by UTF-8 bytewise lexical order. JSON object keys are
UTF-8 bytewise sorted. In prediction JSONL, fault_set, oracle_failure_set,
and base_structure_flags are JSON arrays of strings using those exact
encodings; truth is integer 0 or 1, decision is JSON boolean false or true,
and p_valid is a JSON number token in the fixed decimal form.

The CSV dialect is UTF-8, comma delimiter, double-quote character, doubled
embedded quotes, minimal quoting, no escape character, LF lineterminator, and
no BOM. All CSV fields are serialized strings under that dialect. The result
Markdown uses a fixed section and table order from this protocol, LF only,
exactly one final LF, and no trailing whitespace. These rules apply to every
future data artifact and to every internal byte comparison.

### Hash inputs and deterministic manifests

The amount hash input is the exact UTF-8 string
E002-v1|amount|cluster_index|entity_index, where both indexes are base-10
integers without leading zeroes. The structural signature hash input is the
single UTF-8 string

    E002-v1|signature|entities=n|ledger=L|events=E|active_active=AA|pending_closed=PC|split=0-or-1|multi=M|cases=C

with the displayed field order, decimal values, and no type label. A base or
mutated input hash is SHA-256 of its
canonical JSON payload bytes. A case-ID hash is SHA-256 of its exact UTF-8
case-ID string. Primary bootstrap selection uses
E002-v1|bootstrap|subgroup|metric|replicate|position. Diagnostic bootstrap
selection uses
E002-v1|bootstrap|diagnostic|diagnostic_id|replicate|position. In both
forms, the first eight digest bytes are an unsigned big-endian integer and
the result is reduced modulo the eligible-cluster count.

The canonical population_manifest object has exactly the keys protocol_id and clusters.
Each cluster record has cluster_id, cluster_type, split,
structural_signature, signature_sha256, base_hash, and cases. Each case
record has case_id, case_kind, recipe_id, fault_set, footprint, input_sha256,
and base_structure_flags. Records are ordered by
`(split_rank, type_index, local_index)` and then recipe rank. The canonical
oracle_manifest is an object with protocol_id and cases; each case record has
case_id, schema_valid, truth, oracle_failure_set, and base_structure_flags,
ordered by `(split_rank, type_index, local_index, recipe_rank)`. The calibration_manifest is an
object with protocol_id and methods; each method record has method,
raw_score, positive_count, count, p_valid, and fallback, ordered by the
method order and numeric raw_score. The raw_prediction_manifest is an object
with protocol_id and rows; each row has split, case_id, method, raw_score,
decision, and input_sha256, ordered by
`(split_rank, type_index, local_index, recipe_rank, method_rank)`. The
metric_manifest and bootstrap_manifest are objects with protocol_id and rows,
using the exact output row fields and the total row orders defined below.

Each manifest hash is SHA-256 of its canonical JSON bytes. Before writing, two
independent in-memory builds must compare all manifest hashes and all intended
serialized bytes for the three data files and result Markdown draft. The
complete rendered result draft is compared directly as bytes; it is not
represented by a draft hash, redacted preimage, or alternate serialization.
result Markdown embeds the three data-artifact hashes and the deterministic
internal manifest hashes, but never embeds its own finalized-file hash. After
the result file is finalized last, its SHA-256 is computed and reported
externally in run evidence. This avoids self-hash recursion.

### Canonical ordering and manifest keys

Every order is total and is part of the byte contract. The fixed semantic
ranks are split development=0, calibration=1, confirmatory=2; type H0=0
through H5=5; local cluster index 00 through 15 by numeric value; recipe
valid-base=0, R1=1, C1=2, T1=3, V1=4, M01=5 through M07=11; method
B0=0, M1=1, M1-omit-conservation=2, M1-overconstraint=3,
M1-stale-transition=4, M1-no-semantic=5, M1-no-state=6, and
M1-no-calibration=7. Standard subgroup ranks are overall=0, cluster:H0
through cluster:H5=1 through 6, case_kind:valid=7, case_kind:single=8,
case_kind:multi=9. Standard metric ranks are balanced_accuracy=0, fpr=1,
fnr=2, brier=3, ece=4. Diagnostic ranks are d1=0, d2=1, d3=2. These
rank orders are numeric/declared orders, not lexical guesses.

The population manifest is sorted by
`(split_rank, type_index, local_index)`, then its case list by recipe rank.
The oracle manifest is sorted by
`(split_rank, type_index, local_index, recipe_rank)`. The calibration manifest
is sorted by method rank and then raw_score numeric ascending. The raw
prediction manifest is sorted by
`(split_rank, type_index, local_index, recipe_rank, method_rank)`. The metric
manifest sorts method rows by `(split_rank, subgroup_rank, method_rank)` and
then appends diagnostic rows by diagnostic rank. The bootstrap manifest sorts
blocks by standard `(subgroup_rank, metric_rank)` in nested order, followed by
diagnostic `(diagnostic_rank)`, and sorts each block by replicate index 0
through 9999 followed by its one interval row. Within diagnostic blocks the
diagnostic rank supplies the block key and the metric is the predeclared
diagnostic metric. No output list uses filesystem order. UTF-8 bytewise lexical
ordering is used only for footprint strings, fault_set,
oracle_failure_set/base_structure_flags, JSON object keys, and the eligible
cluster-ID list before each bootstrap selection; all other lists use the
numeric/declared ranks above. Case IDs are never sorted as an accidental
substitute for type/index ranks.

The manifest objects have no keys beyond the exact fields named in the
manifest section above. Object keys are serialized by UTF-8 bytewise key
order, while array record order follows these rank tuples. Each manifest hash
is taken after this ordering and canonical JSON serialization. The runner must
assert that a label permutation, recipe substitution, or alternate sort key
changes the manifest hash and is rejected by the deterministic gate.

### Known-answer SHA-256 vectors

These known-answer vectors are locked protocol test fixtures and were independently
computed from the exact hash inputs above:

H0-C00 entity-0 amount

    input: E002-v1|amount|0|0
    sha256: 6211e62d437c6210a1c02e41c02c49f5dcce723a6ee0d69a6af036803cf629f4
    first-eight-big-endian: 7066682372401160720
    amount_cents: 920

H0 non-type signature

    input: E002-v1|signature|entities=3|ledger=3|events=8|active_active=2|pending_closed=0|split=0|multi=2|cases=7
    sha256: 2e80ccf18dad2a97d8d3e975b0f726f6cf15687fa6e4f50ddf55a940e6d29e9b

Representative case IDs

    input: H0-C00::valid-base
    sha256: bc4c1aa9ecb37f29ec8f1acebb4040d61cca0bf3c3d2de061af53dd1d4876911
    input: H0-C00::R1
    sha256: 0a23225dd76b7860dcbbd24aa80e96666a8cde41a14700bb339c205a108ca6a5

Primary bootstrap selection

    input: E002-v1|bootstrap|overall|balanced_accuracy|0|0
    sha256: ec4fb50879c8319c8000ee52e5d68a1d4617e570c3874457ce9dbb1b727ee050
    first-eight-big-endian: 17028027764118663580
    index modulo 48: 28

The runtime gate must assert these answers independently; they are not
evidence from a future run.

### Cluster population and splits

There are 96 base clusters. Cluster type H0 through H5 has 16 clusters. For
type index t and local index i, the cluster index is t multiplied by 16 plus
i, and the cluster ID is Ht-Cii with two decimal digits. Local indices are
split by type, not by generated case:

| Split | Local indices per type | Clusters | Cases |
| --- | --- | ---: | ---: |
| development | 00-03 | 24 | 228 |
| calibration | 04-07 | 24 | 228 |
| confirmatory | 08-15 | 48 | 456 |

The case count per cluster type is fixed by the recipe count below. Thus the
total is 912 cases, and the split counts are exact. No cluster or base payload
may occur in more than one split.

### Non-identical signatures

Each type is a different structural template. The table is the complete
template definition. A trace is a state sequence; adjacent states are events.
Every entity starts at pending and must end at closed. The allowed reference
edges are pending to active, pending to closed, active to active, and active to
closed. Closed is terminal: no event may follow it.

| Type | Entity traces, in order | Entities | Ledger entries | Events | Active-to-active edges | Direct pending-to-closed edges | Multi recipes | Cases per cluster |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| H0 | pending-active-active-closed; pending-active-closed; pending-active-active-closed | 3 | 3 | 8 | 2 | 0 | 2 | 7 |
| H1 | pending-active-active-closed; pending-active-closed; pending-closed; pending-active-closed | 4 | 4 | 8 | 1 | 1 | 3 | 8 |
| H2 | pending-active-active-closed; pending-active-closed; pending-closed; pending-active-closed; pending-closed | 5 | 5 | 9 | 1 | 2 | 4 | 9 |
| H3 | pending-active-closed; pending-active-active-closed; pending-closed; pending-active-active-closed | 4 | 5 | 9 | 2 | 1 | 5 | 10 |
| H4 | pending-active-active-closed; pending-active-closed; pending-closed; pending-active-closed; pending-active-closed; pending-active-closed | 6 | 6 | 12 | 1 | 1 | 6 | 11 |
| H5 | pending-active-closed; pending-active-closed; pending-active-closed; pending-active-closed; pending-active-closed; pending-closed; pending-closed | 7 | 7 | 12 | 0 | 2 | 7 | 12 |

H3 is the only split-ledger type: entity 0 has two ledger entries and every
other entity has one. The other types have one ledger entry per entity. This
is a deliberate structural difference, not a source fact.

The mandatory type manifest is the following exact mapping. Its recipe lists
are ordered by the recipe rank below, and its case count is one valid plus
four single-fault cases plus the listed multi count.

| Type | Exact non-type tuple `(entities, ledger, events, active-active, pending-closed, split-ledger, multi, cases)` | Required recipe IDs in order | Signature SHA-256 |
| --- | --- | --- | --- |
| H0 | (3, 3, 8, 2, 0, 0, 2, 7) | valid-base, R1, C1, T1, V1, M01, M02 | 2e80ccf18dad2a97d8d3e975b0f726f6cf15687fa6e4f50ddf55a940e6d29e9b |
| H1 | (4, 4, 8, 1, 1, 0, 3, 8) | valid-base, R1, C1, T1, V1, M01, M02, M03 | 0195af9dd2a1ef0f4348c6fc6f082b626d7c9ab1c310c9487d5760bf74afa574 |
| H2 | (5, 5, 9, 1, 2, 0, 4, 9) | valid-base, R1, C1, T1, V1, M01, M02, M03, M04 | 0863b001f0a85dc2582be68a41d33afc2c7d8b28bb52e224e66c4124b8a42d45 |
| H3 | (4, 5, 9, 2, 1, 1, 5, 10) | valid-base, R1, C1, T1, V1, M01, M02, M03, M04, M05 | 278251e55ee1daf215d42e1f534bf811529ab9da39069e488c448f88014d3272 |
| H4 | (6, 6, 12, 1, 1, 0, 6, 11) | valid-base, R1, C1, T1, V1, M01, M02, M03, M04, M05, M06 | d96362a72a4bd443d8e750ced1cebca4521ff28a9e5116bfe6e65c57d2cfbaf3 |
| H5 | (7, 7, 12, 0, 2, 0, 7, 12) | valid-base, R1, C1, T1, V1, M01, M02, M03, M04, M05, M06, M07 | 9a0568400739c46729f811419f84a144a0dfd5de1031f30bd9a47834f101bdcd |

The structural signature used for distinctness is the non-type tuple

    (entities, ledger_entries, events, active_to_active,
     direct_pending_to_closed, split_ledger, multi_recipe_count,
     cases_per_cluster)

encoded by the exact non-type signature hash input above. All six non-type
tuples and all six corresponding hashes must be distinct; type is not part of
this proof. The runtime sanity gate must compare every generated type against
the complete manifest above, including the tuple, cases-per-cluster, exact
signature input and digest, ordered recipe IDs, and type allocation. It must
reject a type-label permutation, recipe substitution, count drift, or
signature drift. It must also require at least two distinct cases-per-cluster
values, eight confirmatory clusters of every type, and no duplicate
confirmatory base-payload hash. A failure is invalid, not a result to be
interpreted.

The exact known-answer signature inputs and digests for all six types are:

    H0: E002-v1|signature|entities=3|ledger=3|events=8|active_active=2|pending_closed=0|split=0|multi=2|cases=7
        2e80ccf18dad2a97d8d3e975b0f726f6cf15687fa6e4f50ddf55a940e6d29e9b
    H1: E002-v1|signature|entities=4|ledger=4|events=8|active_active=1|pending_closed=1|split=0|multi=3|cases=8
        0195af9dd2a1ef0f4348c6fc6f082b626d7c9ab1c310c9487d5760bf74afa574
    H2: E002-v1|signature|entities=5|ledger=5|events=9|active_active=1|pending_closed=2|split=0|multi=4|cases=9
        0863b001f0a85dc2582be68a41d33afc2c7d8b28bb52e224e66c4124b8a42d45
    H3: E002-v1|signature|entities=4|ledger=5|events=9|active_active=2|pending_closed=1|split=1|multi=5|cases=10
        278251e55ee1daf215d42e1f534bf811529ab9da39069e488c448f88014d3272
    H4: E002-v1|signature|entities=6|ledger=6|events=12|active_active=1|pending_closed=1|split=0|multi=6|cases=11
        d96362a72a4bd443d8e750ced1cebca4521ff28a9e5116bfe6e65c57d2cfbaf3
    H5: E002-v1|signature|entities=7|ledger=7|events=12|active_active=0|pending_closed=2|split=0|multi=7|cases=12
        9a0568400739c46729f811419f84a144a0dfd5de1031f30bd9a47834f101bdcd

These six vectors are implementation fixtures, not observed data.

### Exact payload construction

Entity IDs are entity-0 through entity-(n-1). Event IDs are event-e-r for
entity index e and one-based revision r. Each event has entity_id, event_id,
from_state, to_state, and revision. Each entity stores entity_id,
current_state, and revision, where current_state is closed and revision is
the number of events for that entity. The entities list is ordered by entity
index, the ledger list by ledger index, and the events list by entity index
then revision. Therefore entity 0's second event is `/events/1`, which makes
the T1 and V1 footprint pointers exact rather than an implementation choice.

Ledger entry IDs are ledger-0 through ledger-(L-1). Each entry has entry_id,
entity_id, and amount_cents. For an unsplit entity, its amount is

    200 + (integer formed from bytes 0 through 7 of
    SHA256("E002-v1|amount|cluster_index|entity_index") modulo 800).

For H3 entity 0, the same deterministic entity amount is split into floor
half and the remainder, in that order. The metadata field declared_total_cents
is the exact sum of all base ledger amounts and is an integer that is not a
boolean. No payload contains a timestamp or random value.

The following two in-population valid-base probes are mandatory behavioral
separation fixtures. They name the canonical generated payload by its exact
case ID, cluster index, structural tuple, and SHA-256 of canonical JSON bytes;
the listed decisions are evaluated on the payload only, without labels.

| Case ID | Cluster index | Structural tuple | Canonical payload SHA-256 | M1 | M1-overconstraint | M1-stale-transition |
| --- | ---: | --- | --- | --- | --- | --- |
| H0-C00::valid-base | 0 | (3, 3, 8, 2, 0, 0, 2, 7) | 8ddb5fbd84a64ef811a261ad72359f647d0757e8c83c864bd206bbb03b8dd07b | true | false | true |
| H5-C00::valid-base | 80 | (7, 7, 12, 0, 2, 0, 7, 12) | 97935beb48f281d1d1fe8317d8ee7f300089bd2e6ad523fc06aaaaf47d4c6db3 | true | true | false |

The H0 payload contains active-to-active and no direct pending-to-closed
edge; the H5 payload contains direct pending-to-closed and no active-to-active
edge. The implementation must assert both exact payload hashes and all six
decisions at runtime. These are generated-population fixtures, not hand-built
out-of-population probes.

The generator must create base cases before any mutation. It must deep-copy
the base payload for each case and apply only the mutation pointers below.
Case IDs are exactly cluster_id, two ASCII colons, and one recipe suffix:
valid-base, R1, C1, T1, V1, or M01 through M07. For example,
H0-C00::valid-base and H0-C00::R1. There are no alternate spellings or
zero-padding variants. Within a cluster, case order is valid-base, R1, C1,
T1, V1, then the available multi recipes in numeric order. The valid case has
recipe valid-base and an empty intended fault set.

## Locked case recipes and footprints

The reference oracle, not a recipe label, determines truth and the observed
failure set. The recipe label is generator-side provenance only. A footprint is
the exact set of RFC-6901-style JSON pointers whose values or membership are
changed from the base payload. The runtime gate compares the canonical
before/after diff to the predeclared set and rejects any missing or extra
pointer.

Footprint entries are operation-prefixed pointers, with no spaces:
`replace:/ledger/1/entry_id`, `replace:/ledger/<L-1>/amount_cents`,
`replace:/events/1/to_state`, `replace:/events/1/revision`,
`remove:/events/0/revision`, `add:/ledger/0/debug`, and
`replace:/meta/declared_total_cents`. The symbolic `<L-1>` is substituted
with the final ledger index for that cluster before comparison. The exact
recipe mapping is R1 = [`replace:/ledger/1/entry_id`], C1 =
[`replace:/ledger/<L-1>/amount_cents`], T1 =
[`replace:/events/1/to_state`], V1 = [`replace:/events/1/revision`],
Q0-missing = [`remove:/events/0/revision`], Q0-extra =
[`add:/ledger/0/debug`], and Q0-bool =
[`replace:/meta/declared_total_cents`]. A multi footprint is the set union of
the named recipe footprints after applying mutations left-to-right in the
recipe table (for example, M01 applies R1 then C1); the serialized footprint
list is then sorted by the complete operation-prefixed string in UTF-8
bytewise lexical order. The canonical diff treats a changed value as one
replace entry, an absent-to-present member as one add entry, and a
present-to-absent member as one remove entry. No descendant pointer is added
for an object member represented by an add/remove entry. The valid-base
footprint is the empty list.

### Single-fault cases

Every cluster has exactly one case for each single recipe:

| Recipe | Intended family | Exact mutation |
| --- | --- | --- |
| R1 | identity | Replace ledger entry 1 entry_id with ledger entry 0 entry_id. |
| C1 | conservation | Increase the last ledger amount_cents by 1; leave declared_total_cents unchanged. |
| T1 | transition | In entity 0's second event (`event-0-2`, array index 1), replace `to_state` with `pending`; leave current_state and all other fields unchanged. |
| V1 | revision | In entity 0's second event (`event-0-2`, array index 1), replace revision 2 with revision 1. |

The T1 mutation is intentionally checked by ordered replay, not by checking
whether an isolated edge appears in an allowed-edge set. The reference and
M1 paths must both require first from_state pending, every subsequent
from_state equal to the previous to_state, each edge in the allowed set, no
event after closed, and final current_state closed. Their code and tables are
independent as required below.

### Multi-fault and schema-visible cases

The fixed multi-recipe sequence is cumulative by recipe name, but each case
starts from the unmodified base:

| Recipe | Intended mutations | Intended family set |
| --- | --- | --- |
| M01 | R1 plus C1 | identity, conservation |
| M02 | T1 plus V1 | transition, revision |
| M03 | C1 plus V1 | conservation, revision |
| M04 | Q0-missing plus T1 | schema, transition |
| M05 | Q0-extra plus C1 | schema, conservation |
| M06 | Q0-bool plus R1 | schema, identity |
| M07 | Q0-extra plus V1 | schema, revision |

Q0-missing removes events/0/revision. Q0-extra adds ledger/0/debug with the
string unexpected. Q0-bool replaces meta/declared_total_cents with the boolean
true. The exact footprint is the union of the named single footprints.

Each type uses the first m multi recipes in the table, where m is the
multi-recipe count in the cluster table. Therefore clusters contain one valid,
four single-fault, and two through seven multi-fault cases, for 7 through 12
cases per cluster. Every multi case must be truth-negative under the
independent oracle. Its observed family set is recomputed independently and
stored in the oracle manifest; the implementation must report whether the
observed set equals, contains, or differs from the intended set. An extra
failure caused by a schema mutation is an interaction observation, not a
claim that a multi-fault is additive.

## Independent reference oracle

The future code must maintain a reference-oracle module and evaluated-checker
module as separate implementations. Neither may import the other. They may
not share predicate functions, allowed-edge tables, schema tables, family
maps, generated case tables, or mutable objects. The reference oracle must
construct its own literal schema checks, identity/conservation checks, and
ordered replay logic. The checker module must construct its own equivalents.
Names and source locations must be distinct enough for a static independence
test to reject imports or table aliasing.

The reference oracle performs these checks on the payload only:

1. Exact top-level and nested schema, strict scalar types, required fields,
   bounds, and cardinality.
2. Ledger entry IDs are unique, ledger entity references resolve to distinct
   entity IDs, and no entity is omitted from the ledger.
3. Integer ledger amounts are positive and their sum equals the integer
   declared total.
4. For each entity, events are ordered by integer revision. Replay starts at
   pending; the first event must come from pending; every next event must have
   from_state equal to the prior to_state; every edge must be one of the
   independently defined allowed edges; closed is terminal; and the final
   replay state and entity current_state are closed.
5. Revisions are the consecutive one-based values and agree with the entity
   revision.

Truth is one only when strict schema and all four non-schema families pass.
The oracle also returns a fail-closed family set with schema, identity,
conservation, transition, and revision. If a family lacks required fields it
is marked failed rather than raising or being skipped. It never reads recipe,
fault, target, split, cluster, or truth metadata. It never calls an M1
predicate.

The future tests must perturb an M1 predicate or checker table and prove that
the reference output and reference manifest are unchanged. A separate
perturbation of a reference-oracle rule must prove that the M1 implementation
output is unchanged. Static source inspection must reject an oracle/checker
import, shared table, or shared predicate helper. These are runtime gates, not
optional development conveniences.

## Evaluated checkers and ablations

All checkers receive only a sanitized payload. They may not inspect
target_family, truth, fault_set, recipe_id, cluster type, cluster signature,
split, run ID, oracle output, or any other label/oracle metadata. A malformed,
vacuous, or extra nested field is invalid and must return a false decision
without raising. Boolean values are not integers.

The exact method list and retained family sets are:

| Method | Definition | Raw score and calibration |
| --- | --- | --- |
| B0 | Exact schema-only checker; no cross-record identity, sum, replay, or revision relation. | Failed-schema count, 0 or 1; its own Laplace lookup. |
| M1 | Exact schema plus identity, conservation, ordered transition replay, and revision checks. | Failed retained-family count over schema plus four families; its own lookup. |
| M1-omit-conservation | M1 with the conservation family omitted. | Failed count over schema, identity, transition, revision; own lookup. |
| M1-overconstraint | M1 plus a predeclared rejection of any active-to-active event. | Failed count over schema, identity, conservation, transition, revision, overconstraint; own lookup. |
| M1-stale-transition | M1 with stale transition table pending-active, active-active, active-closed and closed terminal; pending-closed is omitted. | Failed count over schema, identity, conservation, stale-transition, revision; own lookup. |
| M1-no-semantic | M1 retaining schema and the state group transition plus revision, omitting identity and conservation. | Failed count over schema, transition, revision; own lookup. |
| M1-no-state | M1 retaining schema and the semantic group identity plus conservation, omitting transition and revision. | Failed count over schema, identity, conservation; own lookup. |
| M1-no-calibration | The exact M1 decision and raw score, with frozen p_valid equal to the binary decision. | No changed classification; calibration ablation only. |

The semantic group is identity plus conservation. The state group is transition
plus revision. The first two retained-family ablations have independent raw
scores and independent calibration lookups; neither reuses M1's lookup.
Misspecified regime point metrics remain separately reported, while d1, d2,
and d3 are co-primary specification-stress diagnostics. Every decision,
including B0, is exactly decision = (raw_score == 0), except that
M1-no-calibration uses the unchanged exact M1 decision while replacing only
its p_valid. Decisions are pure functions of the sanitized payload and the
method's own predeclared predicates.

The runtime sanity gate must prove the two misspecification behaviors are
distinct: a valid payload with active-active passes stale-transition but fails
overconstraint, and a valid payload with pending-closed passes overconstraint
but fails stale-transition. These probes use no case labels.

## Sanitization and exact schema

Sanitization must parse canonical JSON into a fresh ordinary structure and
reject anything other than the exact payload. It must reject an empty payload,
None, a list in place of an object, missing or extra top-level keys, missing or
extra nested keys, strings or floats in integer fields, booleans in integer
fields, wrong list cardinalities, and out-of-range scalar values. It must
return a fail-closed invalid result rather than an exception or a permissive
empty object. Duplicate identifiers and unresolved cross-record references
are not B0 schema failures; those belong to the independent identity,
conservation, transition, and revision families.

The exact schema is:

    {
      "meta": {
        "schema_version": string E002-v1,
        "declared_total_cents": integer, not boolean, positive
      },
      "entities": [
        {"entity_id": string, "current_state": one of pending/active/closed,
         "revision": integer, not boolean, 1 through 12}
      ],
      "ledger": [
        {"entry_id": string, "entity_id": string,
         "amount_cents": integer, not boolean, 1 through 200000}
      ],
      "events": [
        {"event_id": string, "entity_id": string,
         "from_state": string, "to_state": string,
         "revision": integer, not boolean, 1 through 12}
      ]
    }

Top-level keys and each nested object key set are exact. The full payload-only
B0 schema is:

| Field | Exact local rule |
| --- | --- |
| meta.schema_version | string matching regex ^E002-v1$ |
| meta.declared_total_cents | strict integer, not boolean, 600 through 6994 inclusive |
| entities | list length 3 through 7 |
| entities.entity_id | string matching ^entity-[0-6]$ |
| entities.current_state | exact enum pending, active, closed |
| entities.revision | strict integer, not boolean, 1 through 12 |
| ledger | list length 3 through 7; this global bound covers n and H3 n+1 without hidden type |
| ledger.entry_id | string matching ^ledger-[0-6]$ |
| ledger.entity_id | string matching ^entity-[0-6]$ |
| ledger.amount_cents | strict integer, not boolean, 1 through 200000 |
| events | list length 8 through 12 |
| events.event_id | string matching ^event-[0-6]-([1-9]|1[0-2])$ |
| events.entity_id | string matching ^entity-[0-6]$ |
| events.from_state and events.to_state | exact enum pending, active, closed |
| events.revision | strict integer, not boolean, 1 through 12 |

B0 checks only these local types, regexes, enums, exact key sets, and list
cardinalities. It does not check cross-record resolution, uniqueness,
entity-to-ledger cardinality, sums, event ordering, edge membership, terminal
behavior, or revision agreement. M1 and the reference oracle perform those
cross-record checks independently. A type-specific ledger cardinality rule is
therefore never smuggled into B0 through hidden cluster metadata.

## Calibration isolation

Development is used only for generator, oracle, checker, schema, footprint,
leakage, and deterministic self-checks. On the calibration split, each method
is scored once, and the independently computed calibration truth may be used
only by a separate calibration routine. For every method and raw-score value
s, let n_s be the calibration count and k_s its positive truth count. The
frozen lookup is

    p_valid(s) = (k_s + 1) / (n_s + 2).

An unseen score uses the method-specific calibration-wide fallback
(K + 1)/(N + 2). Lookups are frozen before any confirmatory prediction is
materialized. M1-no-calibration uses the binary M1 decision as p_valid and
does not alter the decision. Confirmatory truth is not read by any checker or
calibration routine; it is used only after all predictions are frozen for
metrics and the independent determinism gate.

The runner must serialize a canonical internal calibration-lookup table for
hashing. Its hash, per-method lookup entries, and frozen status are included
in the result Markdown and in every prediction row through
calibration_lookup_sha256.

## Co-primary specification-stress diagnostics

The three diagnostics are confirmatory and co-primary with the M1-B0
heterogeneous anchor. They are not decorative post-hoc subgroup analyses.
Their exact IDs, subsets, metric, method-pair key, eligible clusters, and
expected sign are:

| ID | Exact subset predicate | Metric and method-pair key | Eligible confirmatory clusters | Required direction |
| --- | --- | --- | ---: | --- |
| d1 | truth=0, schema_valid=true, and conservation is in oracle_failure_set | FPR, omit-M1 = M1-omit-conservation minus M1 | 48: every confirmatory cluster has at least one such case | lower CI strictly greater than 0 |
| d2 | truth=1, case_kind=valid, and active-active is in base_structure_flags | FNR, over-M1 = M1-overconstraint minus M1 | 40: H0, H1, H2, H3, and H4 confirmatory clusters only | lower CI strictly greater than 0 |
| d3 | truth=1, case_kind=valid, and pending-closed is in base_structure_flags | FNR, stale-M1 = M1-stale-transition minus M1 | 40: H1, H2, H3, H4, and H5 confirmatory clusters only | lower CI strictly greater than 0 |

The base_structure_flags are computed from the unmutated base payload and
recorded in the population and oracle manifests; they are not read by a
validator. The oracle_failure_set is independently recomputed by the
reference oracle. The runtime gate must assert that every eligible cluster has
at least one eligible case and that every diagnostic denominator is positive
before resampling. Thus every diagnostic point estimate and every bootstrap
replicate has a defined class denominator. A d1 replicate uses FPR because its
subset is truth-negative; d2 and d3 use FNR because their subsets are
truth-positive.

Diagnostics use the same frozen calibration and paired cluster-resampling
principle as primary rows. For d1, d2, and d3, each replicate samples the
diagnostic's eligible clusters with replacement, ordered by cluster ID bytes,
using the diagnostic hash input defined in the deterministic handoff. All
matching cases in each selected cluster are retained with multiplicity. Both
methods in a pair are scored on exactly the same resample. The method-pair
keys are exact strings in report and metrics metadata and compact keys in the
bootstrap codebook: M1-B0 maps to m1-b0, omit-M1 to omit-m1, over-M1 to
over-m1, and stale-M1 to stale-m1.

## Metrics and undefined-value policy

Metrics are computed for every method, split, and exactly these ten subgroups:

    overall
    cluster:H0, cluster:H1, cluster:H2, cluster:H3, cluster:H4, cluster:H5
    case_kind:valid, case_kind:single, case_kind:multi

The three diagnostic rows use exact subgroup labels diagnostic:d1,
diagnostic:d2, and diagnostic:d3 and are not silently folded into the
case-kind rows.

The metrics CSV has 8 times 3 times 10 equals 240 method rows plus exactly
three confirmatory diagnostic rows, for 243 data rows plus the header. Its
columns are:

    row_kind, run_id, protocol_path, protocol_commit, split, subgroup,
    method, method_pair, diagnostic_id, calibration_lookup_sha256,
    support, positive_count, negative_count,
    tp, tn, fp, fn, fpr_denominator, fnr_denominator,
    precision_denominator, recall_denominator, specificity_denominator,
    f1_denominator, ece_denominator, balanced_accuracy, fpr, fnr,
    precision, recall, specificity, f1, brier, ece,
    paired_interval_ref, delta_ba_ci_lower, delta_ba_ci_upper,
    delta_fpr_ci_lower, delta_fpr_ci_upper, delta_fnr_ci_lower,
    delta_fnr_ci_upper, delta_brier_ci_lower, delta_brier_ci_upper,
    delta_ece_ci_lower, delta_ece_ci_upper, interval_status,
    diagnostic_metric, diagnostic_support, diagnostic_positive_count,
    diagnostic_negative_count, diagnostic_denominator,
    diagnostic_method_a_error_count, diagnostic_method_b_error_count,
    diagnostic_delta, diagnostic_interval_ref, diagnostic_ci_lower,
    diagnostic_ci_upper

Method rows have row_kind method, method_pair and diagnostic fields NA.
Diagnostic rows have row_kind diagnostic, method NA, diagnostic_id d1/d2/d3,
the exact method_pair key, diagnostic_metric fpr or fnr, diagnostic_support
counts, the class-appropriate diagnostic denominator, both method error
counts, the diagnostic delta, and its real diagnostic interval reference/CI
fields.
Their ordinary single-method metric fields are NA. Diagnostic row order is d1,
d2, d3 after all method rows. Method row order is split development,
calibration, confirmatory; subgroup order as listed; then method order as
listed in the method table.

For primary confirmatory B0 and M1 rows, the five interval pairs and
paired_interval_ref point to matching primary bootstrap interval rows. For
d1-d3 rows, diagnostic_interval_ref points to the matching stress interval
row. The primary B0/M1 status is the actual valid, partial, or undefined
status for that subgroup; all other method/split interval fields use the
literal NA and interval_status descriptive-only. Every reference is a real
subgroup/metric or diagnostic/method-pair key, not an invented placeholder.

The positive class is truth one and the predicted positive is decision one.
FPR is fp/(tn+fp); FNR is fn/(tp+fn); precision is tp/(tp+fp); recall is
tp/(tp+fn); specificity is tn/(tn+fp); F1 is 2tp/(2tp+fp+fn);
balanced accuracy is the mean of recall and specificity; Brier is the mean
of (p_valid minus truth) squared. ECE uses ten fixed bins [0,0.1), ...,
[0.9,1.0] and is the support-weighted absolute difference between each
nonempty bin's mean p_valid and mean truth.

If a metric denominator is zero, the metric serializes as the literal NA,
never blank and never zero. Its denominator and all confusion counts remain
serialized. Brier and ECE are NA only when support is zero. The same policy
applies to bootstrap replicates: an undefined delta is serialized as NA and
is not imputed as zero.

Case-kind rows are intentionally descriptive. case_kind:valid is
truth-positive-only, so FPR and balanced accuracy can be undefined; the
single and multi rows are truth-negative-only, so FNR and balanced accuracy
can be undefined. Their bootstrap interval statuses may therefore be partial
or undefined and must be reported as such. These descriptive rows do not
enter the H2 required interval set. Overall and cluster-type rows, plus d1-d3,
must have the denominators required by their role; required H2 intervals are
invalid only when one of their own exact keys is partial or undefined.

## Paired cluster bootstrap and public-size gate

The bootstrap is exact and deterministic: 10,000 replicates, indexed 0 through
9999. It produces paired M1-minus-B0 deltas for the five metrics
balanced_accuracy, fpr, fnr, brier, and ece across the ten locked standard
subgroups, plus one paired delta metric for each of d1, d2, and d3. It does
not duplicate per-method replicate rows.

For overall and case-kind subgroups, eligible confirmatory clusters are all
48 clusters. For cluster:Hj, eligible clusters are the eight confirmatory
clusters of Hj. Within each replicate r and subgroup/metric pair, order
eligible cluster IDs by UTF-8 bytes. For position j, select the cluster at

    integer formed from bytes 0 through 7 of
    SHA256("E002-v1|bootstrap|subgroup|metric|r|j") modulo eligible_count.

Resample eligible clusters with replacement and include all matching cases
from each selected cluster, preserving multiplicity. Compute M1 and B0
metrics on the same resampled cases, then store their delta. Calibration is
the already frozen mapping.

For d1-d3, use the eligible cluster sets in the diagnostic table and the
diagnostic hash input. Resample the same cluster IDs for both methods in the
pair, filter to the exact diagnostic subset, and compute the class-appropriate
FPR or FNR delta. The runtime gate must reject a diagnostic block if any
eligible cluster lacks a target case or if a resample has a zero denominator.

The bootstrap CSV has 530,000 replicate rows, 53 interval-summary rows, and
one header: 530,054 lines. Its exact columns are:

    row_type, replicate, subgroup_code, metric_code, method_pair_key,
    delta, ci_lower, ci_upper, usable_replicates, status

The bootstrap codebook is exact: subgroup_code o, h0, h1, h2, h3, h4, h5, v,
s, and m mean overall, cluster:H0 through cluster:H5, case_kind:valid,
case_kind:single, and case_kind:multi. d1, d2, and d3 mean the three
diagnostics. metric_code ba, fpr, fnr, brier, and ece mean the five standard
metrics. method_pair_key m1-b0, omit-m1, over-m1, and stale-m1 mean the
primary and three diagnostic pairs. These compact codes are the exact keys,
not abbreviations chosen after a run.

Replicate rows have row_type replicate, a decimal replicate index, a code
block, delta or NA, NA interval fields, the total usable count after the
full block, and status usable or undefined. Interval rows have row_type
interval, replicate NA, the same codes, delta NA, percentile endpoints,
usable count, and status valid, partial, or undefined. Block order is the ten
standard subgroups in listed order crossed with the five metrics in listed
order, followed by d1, d2, and d3; within each block, replicate rows 0
through 9999 precede its one interval row. No per-method bootstrap
duplication is permitted.

For a usable count n greater than zero, sort the numeric deltas and use
nearest-rank indices
max(0, min(n-1, ceil(0.025*n)-1)) and
max(0, min(n-1, ceil(0.975*n)-1)).
For n=10,000 these are 249 and 9749. If fewer than 10,000 are usable, use
the usable values and mark partial; any partial required H2 interval makes
H2 mixed/not supported, while descriptive intervals remain reportable. If
n=0, write NA endpoints and status undefined. The replicate count remains
exactly 10,000 in every standard or diagnostic block.

Before any write, the future runner must estimate the canonical CSV byte size
from the exact row serializer and reject an estimate at or above 50,000,000
bytes. The public hard limit is 52,428,800 bytes. With the compact codebook,
fixed nine-place numbers, and a locked 90-byte maximum data-row envelope, the
upper estimate is
530,000 times 90 plus 53 times 180 plus 1,024 = 47,710,564 bytes, below both
limits. A development test must serialize the worst-case envelope and assert
this exact arithmetic. The actual intended bytes are also compared before
write; the upper estimate is a gate, not permission to publish an oversized
artifact.

## Predictions, result, and exact output schemas

The future run may create only these four final paths under the repository
root:

    data/E002-v1-predictions.jsonl
    data/E002-v1-metrics.csv
    data/E002-v1-bootstrap.csv
    experiments/E002-heterogeneous-specification-stress/results/run-<run-id>.md

None of these paths exists in this protocol-lock commit.

Predictions JSONL has one row for each of 912 cases times eight methods, or
7,296 rows. Each row has exactly:

    run_id, protocol_path, protocol_commit, method, split, cluster_id,
    cluster_type, cluster_signature_sha256, case_id, case_kind, recipe_id,
    fault_set, oracle_failure_set, base_structure_flags, truth, decision,
    raw_score, p_valid, input_sha256, oracle_manifest_sha256,
    calibration_lookup_sha256, status

The row uniqueness key is run_id, method, case_id. All p_valid values are
finite numbers in [0,1]. fault_set and truth are evaluation/reporting
metadata; oracle_failure_set and base_structure_flags are independently
recomputed reporting metadata. None of these fields is ever passed to a
validator. Prediction row order is exactly
`(split_rank, type_index, local_index, recipe_rank, method_rank)`, with the
rank definitions in the canonical ordering section; cluster-ID lexical order
is not used as a substitute.

The result Markdown is finalized last and must contain protocol ID/path/commit,
run ID, validity, environment, exact split and cluster counts, gate status,
the calibration hash, raw-prediction/calibration/metric/bootstrap internal
manifest hashes, hashes for the three data artifacts, primary B0/M1 anchor
metrics and paired intervals, all three co-primary stress diagnostics and
paired intervals, the exact H2 rule and either supported or mixed/not
supported, FNR guardrail status, secondary misspecified-regime and ablation
summaries, deviations (none or an exact list), links to all four artifacts,
limitations, the synthetic-only boundary, and the stopping/run-validity
statement. It embeds hashes for the three data artifacts; it does not embed
its own finalized-file SHA-256, which is computed and reported externally
after finalization.

The valid result Markdown is a byte fixture, not free-form prose. The runner
must render exactly this template, in this order, with no additional headings,
rows, wrapping, or blank lines. The complete placeholder vocabulary in the
two templates is exactly
`RUN_ID, PROTOCOL_COMMIT, PASS_OR_FAIL, INT, D9_OR_NA, STATUS, H2_OUTCOME,
HASH, INT_LIST, PASS_OR_FAIL_AND_DELTA, SECONDARY_METRICS,
CALIBRATION_SUMMARY`. No other placeholder token is permitted. `KEY`, `D9`,
and `D9_LIST` are grammar atoms used inside the composite definitions below,
not standalone template tokens.

The exact ASCII grammars and semantic sources are:

- `RUN_ID`: regex `^e002-[0-9]{8}-[0-9]{3}$`; the `--run-id` argument, with a
  valid Gregorian `YYYYMMDD` date and a three-digit decimal serial.
- `PROTOCOL_COMMIT`: regex `^[0-9a-f]{40}$`; the exact lowercase commit ID
  established by the protocol identity gate.
- `PASS_OR_FAIL`: enumeration `pass|fail`; the named gate result.
- `INT`: regex `^(0|[1-9][0-9]*)$`; a nonnegative decimal count with no leading
  zeroes. `INT_LIST` is `none` or one or more `INT` values joined by comma
  plus one ASCII space, in ascending numeric order; `none` is permitted only
  for an empty source list.
- `HASH`: regex `^[0-9a-f]{64}$`; the SHA-256 of the artifact, manifest, or
  lookup named by the field containing it. It is never an arbitrary value.
- `D9`: regex `^-?(0|[1-9][0-9]*)\.[0-9]{9}$`, excluding
  `-0.000000000`; fixed nine-place decimal output, with negative zero
  normalized to `0.000000000`. `D9_OR_NA` is either `D9` or the literal
  `NA`. `D9_LIST` is `none` or one or more `D9` values joined by comma plus
  one ASCII space in source-key order; `none` is permitted only for an empty
  source list.
- `STATUS`: enumeration `valid|partial|undefined|descriptive-only`.
- `H2_OUTCOME`: enumeration `supported|mixed/not supported`, with the latter
  exact fallback label.
- `KEY`: not an unrestricted string. It is exactly one of the 53 generated
  interval keys: the 50 strings
  `primary|<subgroup>|<metric>|M1-B0` for subgroup in declared order
  `overall, cluster:H0, cluster:H1, cluster:H2, cluster:H3, cluster:H4,
  cluster:H5, case_kind:valid, case_kind:single, case_kind:multi` and metric
  in declared order `balanced_accuracy, fpr, fnr, brier, ece`, or exactly
  `stress|d1|fpr|omit-M1`, `stress|d2|fnr|over-M1`, or
  `stress|d3|fnr|stale-M1`. The fixed `interval_refs` line below uses the
  five overall keys in metric order and is not a free-form placeholder.
- `PASS_OR_FAIL_AND_DELTA`: exactly
  `status=<PASS_OR_FAIL>;delta=<D9_OR_NA>` after substitution.
- `SECONDARY_METRICS`: exactly
  `ba=<D9_OR_NA>;fpr=<D9_OR_NA>;fnr=<D9_OR_NA>;brier=<D9_OR_NA>;ece=<D9_OR_NA>`.
- `CALIBRATION_SUMMARY`: exactly
  `lookup=<HASH>;scores=<INT_LIST>;p_valid=<D9_LIST>`, where both lists use
  the same ascending raw-score order.

All placeholder substitutions are ASCII, contain no CR, LF, backtick, or pipe,
and therefore are safe in Markdown table cells without escaping. The fixed
interval-key line is outside a table and contains its literal pipe separators.
No placeholder carries prose, a list uses any delimiter other than the one
specified above, and no dynamic deviations are allowed: a confirmatory
deviation invalidates the run, so the valid template contains the literal
`none`. The environment line is a fixed literal rather than a host-dependent
Python/platform/byteorder field. Every line ends in LF and each template has
exactly one final LF.

```text
# E002-v1 result — <RUN_ID>
status: valid
protocol_id: E002-v1
protocol_path: experiments/E002-heterogeneous-specification-stress/protocol.md
protocol_commit: <PROTOCOL_COMMIT>
run_id: <RUN_ID>
validity: valid
environment: standard-library-only local CPU; no network/API/GPU

## Gate status
| gate | status |
| --- | --- |
| protocol_identity | <PASS_OR_FAIL> |
| clean_tree | <PASS_OR_FAIL> |
| split_disjointness | <PASS_OR_FAIL> |
| oracle | <PASS_OR_FAIL> |
| footprints | <PASS_OR_FAIL> |
| calibration_isolation | <PASS_OR_FAIL> |
| determinism | <PASS_OR_FAIL> |
| size | <PASS_OR_FAIL> |
| status | valid |

## Counts
clusters: <INT>
cases: <INT>
development_cases: <INT>
calibration_cases: <INT>
confirmatory_cases: <INT>
prediction_rows: <INT>
metric_rows: <INT>
bootstrap_lines: <INT>

## Primary anchor: M1 minus B0
| method | balanced_accuracy | fpr | fnr | brier | ece | interval_status |
| --- | --- | --- | --- | --- | --- | --- |
| B0 | <D9_OR_NA> | <D9_OR_NA> | <D9_OR_NA> | <D9_OR_NA> | <D9_OR_NA> | <STATUS> |
| M1 | <D9_OR_NA> | <D9_OR_NA> | <D9_OR_NA> | <D9_OR_NA> | <D9_OR_NA> | <STATUS> |
| Delta M1-B0 | <D9_OR_NA> | <D9_OR_NA> | <D9_OR_NA> | <D9_OR_NA> | <D9_OR_NA> | <STATUS> |
interval_refs: primary|overall|balanced_accuracy|M1-B0;primary|overall|fpr|M1-B0;primary|overall|fnr|M1-B0;primary|overall|brier|M1-B0;primary|overall|ece|M1-B0
intervals: ba=<D9_OR_NA>,<D9_OR_NA>; fpr=<D9_OR_NA>,<D9_OR_NA>; fnr=<D9_OR_NA>,<D9_OR_NA>; brier=<D9_OR_NA>,<D9_OR_NA>; ece=<D9_OR_NA>,<D9_OR_NA>

## Co-primary specification stress
| diagnostic_id | method_pair_key | metric | support | delta | ci_lower | ci_upper | interval_status |
| --- | --- | --- | ---: | --- | --- | --- | --- |
| d1 | omit-M1 | fpr | <INT> | <D9_OR_NA> | <D9_OR_NA> | <D9_OR_NA> | <STATUS> |
| d2 | over-M1 | fnr | <INT> | <D9_OR_NA> | <D9_OR_NA> | <D9_OR_NA> | <STATUS> |
| d3 | stale-M1 | fnr | <INT> | <D9_OR_NA> | <D9_OR_NA> | <D9_OR_NA> | <STATUS> |

## H2
anchor_rule: overall delta BA CI lower greater-than 0; overall delta FPR CI upper less-than 0; overall point delta FNR less-than-or-equal-to 0; every nonempty cluster-type delta BA greater-than-or-equal-to 0; at least 4 of 6 cluster-type deltas greater-than 0
stress_rule: d1,d2,d3 lower CI endpoints strictly greater than 0; all required intervals valid with 10000 usable replicates
required_intervals: primary|overall|balanced_accuracy|M1-B0; primary|overall|fpr|M1-B0; stress|d1|fpr|omit-M1; stress|d2|fnr|over-M1; stress|d3|fnr|stale-M1
outcome: <H2_OUTCOME>
fnr_guardrail: <PASS_OR_FAIL_AND_DELTA>

## Secondary regimes and ablations
| method | raw_score/lookup | decision_summary | calibration_summary |
| --- | --- | --- | --- |
| M1-omit-conservation | lookup=<HASH>;scores=<INT_LIST> | <SECONDARY_METRICS> | <CALIBRATION_SUMMARY> |
| M1-overconstraint | lookup=<HASH>;scores=<INT_LIST> | <SECONDARY_METRICS> | <CALIBRATION_SUMMARY> |
| M1-stale-transition | lookup=<HASH>;scores=<INT_LIST> | <SECONDARY_METRICS> | <CALIBRATION_SUMMARY> |
| M1-no-semantic | lookup=<HASH>;scores=<INT_LIST> | <SECONDARY_METRICS> | <CALIBRATION_SUMMARY> |
| M1-no-state | lookup=<HASH>;scores=<INT_LIST> | <SECONDARY_METRICS> | <CALIBRATION_SUMMARY> |
| M1-no-calibration | lookup=none;scores=<INT_LIST> | exact M1 decisions | p_valid=binary decision |

## Calibration
lookup_manifest_sha256: <HASH>
lookup_status: frozen before confirmatory scoring; methods=B0,M1,M1-omit-conservation,M1-overconstraint,M1-stale-transition,M1-no-semantic,M1-no-state,M1-no-calibration

## Artifacts
- [predictions](../../../data/E002-v1-predictions.jsonl) sha256=<HASH>
- [metrics](../../../data/E002-v1-metrics.csv) sha256=<HASH>
- [bootstrap](../../../data/E002-v1-bootstrap.csv) sha256=<HASH>
- [result](run-<RUN_ID>.md)

## Deterministic internal hashes
raw_prediction_manifest: <HASH>
calibration_manifest: <HASH>
metric_manifest: <HASH>
bootstrap_manifest: <HASH>
prediction_bytes: <HASH>
metrics_bytes: <HASH>
bootstrap_bytes: <HASH>

## Deviations
none

## Limitations
- synthetic generator and finite recipe inventory
- independently implemented but hand-specified synthetic replay/conservation oracle
- bounded specification mutation and bounded multi-fault interaction
- designed cluster signatures, not a sampled population
- cluster bootstrap intervals describe this resampling design only
- no production, external-validity, novelty, safety, or generalization evidence
- public_claim_eligibility=false

## Run validity and stopping
run_validity: valid after all gates and two-build byte comparison
stopping_rule: one valid confirmatory run and artifact verification; no retries or post-hoc analyses
confirmatory_execution: completed exactly once for this run ID
```

On any failure, the only permitted result-path record is this exact concise
template, with no metric table and no evidence-like language:

```text
# E002-v1 invalid run — <RUN_ID>
status: invalid
protocol_id: E002-v1
protocol_commit: <PROTOCOL_COMMIT>
run_id: <RUN_ID>
failure_class: invalid-run
No metrics or evidence exist.
corrected_run_requires_new_id: true
```

The invalid template also ends with exactly one LF. The finalized valid result
file is written last; its own SHA-256 is computed and reported only externally
after finalization, and no draft or final report hash is embedded in either
template or any report-internal hash list. No redacted or preimage form is
serialized or hashed.

The locked per-file planning envelope is 7,296 prediction rows with an
implementation-enforced estimate below 8,000,000 bytes, 243 metrics rows with
an estimate below 500,000 bytes, 530,054 bootstrap lines with the exact upper
estimate above, and a result Markdown estimate below 40,000 bytes. The
bootstrap public-size gate is the binding artifact gate.

## Runtime gates and full determinism

All gates are required in the future implementation and are checked before
confirmatory metrics are presented:

1. Verify protocol path, exact protocol blob bytes and git blob hash, required
   ancestor, clean tracked and untracked tree, run ID format, and absent final
   output paths. Exact git bytes, not a line count, token count, or minimum
   handoff length, are the protocol-identity test.
   This gate runs before creating output_root, data directories, results
   directories, or staging directories.
2. Generate the entire in-memory population twice and compare canonical bytes,
   case IDs, base hashes, signature hashes, footprints, and split manifests.
   `build_pipeline` must invoke the following runtime sanity gate after this
   double generation and before calibration, prediction, metrics, or
   bootstrap construction; a direct metrics call without a passing sanity
   gate is invalid.
3. Assert the complete H0-H5 type manifest: exact type-to-tuple mapping,
   cases-per-cluster, signature input/digest, ordered recipe list, and split
   allocation. Assert that each generated cluster has the expected type,
   local index, signature, case count, and recipe IDs. Explicitly permute a
   type label, substitute one recipe, alter one case count, and alter one
   signature in development probes; each perturbation must make this runtime
   gate fail closed. For every generated case, assert B0 decision is true
   exactly when the independent schema result is valid: valid-base, R1, C1,
   T1, V1, and non-schema multi cases pass B0, while Q0-containing M04-M07
   cases fail B0. No case label is supplied to B0 for this assertion.
4. Assert exact counts 96 clusters, 912 cases, 228/228/456 split cases,
   24/24/48 split clusters, eight confirmatory clusters per type, six
   distinct non-type structural tuples and hashes, at least two case counts,
   and no duplicate confirmatory base hash. For each of the three splits,
   assert uniqueness within the base-hash set, cluster-ID set, and case-ID
   set; then assert pairwise disjointness of each of those three sets across
   development, calibration, and confirmatory splits. A mere case-count or
   confirmatory-only check is insufficient.
5. Use the independent reference oracle to assert every valid case passes,
   every single case is negative and has exactly its intended family failure,
   every multi case is negative, and every multi observed set is recorded
   against its intended set. Use the reference oracle for all truth and
   isolation sanity checks.
6. Apply every recipe to a base copy and assert exact mutation footprints in
   the operation-prefixed pointer representation and exact sorted order.
   Reject an extra or missing pointer.
7. Run schema sanitization probes for empty, None, list, missing, extra,
   boolean-as-integer, nested-extra, and wrong-cardinality inputs. Every
   malformed result is invalid without raising.
8. Prove checker/oracle independence with source inspection and the two
   perturbation probes. Prove validators cannot access labels or oracle
   metadata, at runtime and by static inspection.
9. Assert B0 is schema-only, M1 is exact-spec, regimes and ablations have
   the exact retained family sets, no-calibration preserves M1 decisions,
   and the H0-C00/H5-C00 in-population payload-hash and decision probes pass.
   The overconstraint checker must reject H0 and accept H5; the stale checker
   must accept H0 and reject H5.
10. Assert calibration consumes calibration labels only, freezes all lookups
   before confirmatory scoring, and uses method-specific raw-score mappings.
11. Verify prediction keys, 7,296 prediction rows, 243 metrics rows including
   d1-d3, 530,054 bootstrap lines including header, diagnostic method-pair
   keys, status/NA policy, unique keys, finite probabilities, defined
   diagnostic denominators, and exact output path allowlist. Assert
   case-kind single-class descriptive intervals can be partial or undefined
   without changing H2 required-interval status.
12. Extract the two fenced `text` template blocks by their exact first lines,
   extract every placeholder with regex `<[A-Z][A-Z0-9_]*>`, and assert that
   every extracted token belongs to the complete vocabulary above and that
   every vocabulary token occurs at least once. Reject any other angle-bracket
   token in either template. Render valid and invalid fixtures from typed
   field sources, then assert that no placeholder token remains, no CR or
   trailing whitespace exists, each byte string has exactly one final LF, and
   all substituted table-cell values satisfy the ASCII cell-safety rule.
   Build the complete valid result draft twice and compare the rendered bytes
   directly, byte for byte; do not hash a draft, redact a field, or compare a
   preimage. The invalid fixture is checked by the same renderer gate.
13. Recompute the complete in-memory pipeline independently before any write.
   Compare canonical hashes for raw predictions, calibration lookups,
   prediction rows, metric rows, all primary and diagnostic bootstrap delta
   and interval rows, and compare each intended serialized byte string. The
   complete rendered result draft bytes from the two builds are compared
   directly as required by gate 12; no report draft/final hash participates in
   the comparison. A mismatch aborts.
14. Verify the temporary/bootstrap size estimate and public-size budget,
   including the 530,054-line arithmetic and per-file planning envelopes.

Development tests must exercise development and calibration splits only and
must not print confirmatory metrics. A future confirmatory CLI invocation is
the only operation allowed to materialize the confirmatory output paths.

## Invalid-run, staging, and overwrite rules

The runner requires explicit run ID and output root arguments. A run ID must
match the locked form e002-YYYYMMDD-NNN, with decimal date and three-digit
serial. It refuses a dirty or untracked tree, protocol identity mismatch,
missing required ancestor, existing final output, an existing run ID, or a
size/determinism gate failure. These checks happen before any output-root or
staging mkdir.
Existing files are never overwritten.

After all read-only preflight checks, the runner creates a uniquely named
temporary staging directory and writes canonical predictions, metrics, and
bootstrap there. It verifies their bytes and schemas, writes the result
Markdown into staging last, fsyncs files, and finalizes data, metrics, and
bootstrap before finalizing the result Markdown last. It must not expose a
valid-looking result before every required artifact is ready.

On any failure after staging begins, the runner removes the staging directory
and any final files created by this invocation. If the final result path was
absent at entry, it may write only a concise invalid-run Markdown record at
that path after cleanup. That record must state status invalid, run ID,
protocol identity, failure class, and that no metrics or evidence exist; it
must contain no metric table and must not resemble a valid result. If cleanup
cannot be verified, the invocation is invalid and reports the cleanup
failure. A corrected attempt must use a new run ID. No retry is implicit.

## Secondary analyses, stopping rule, and limitations

The result must report the three misspecified regimes separately:
M1-omit-conservation, M1-overconstraint, and M1-stale-transition. It must
report d1, d2, and d3 as co-primary specification-stress diagnostics and
M1-no-semantic, M1-no-state, and M1-no-calibration as ablations. Their point
metrics and calibration metrics are included in the same metrics schema.
H2 requires both the M1-minus-B0 heterogeneous anchor and all three strictly
positive stress lower intervals; no ablation or descriptive regime row can
upgrade a failed co-primary condition.

The single-run stopping rule is fixed before implementation: after one valid
confirmatory run and its artifact verification, stop E002. Do not add recipes,
types, thresholds, retries, or post-hoc subgroup analyses. An invalid run
stops without evidence and can be corrected only under a new run ID and a
separately documented authorization. H2 support is not a reason to broaden
the run or to claim real-world validity.

The locked limitations are: synthetic generator and finite recipe inventory;
oracle truth is an independently implemented replay/conservation reference
but remains a hand-specified synthetic oracle; bounded rather than exhaustive
specification mutation; bounded rather than exhaustive multi-fault interaction;
cluster signatures are designed rather than sampled from a population;
bootstrap intervals describe this resampling design only; possible degenerate
intervals must be reported rather than hidden; no production, external,
novelty, safety, or generalization evidence; and no public-claim eligibility.

## Future implementation handoff

Implementation may begin only in a separate, explicitly authorized code
change descended from this lock commit. It must keep the reference oracle and
evaluated checkers independently maintained, use standard-library-only local
CPU code, run all gates before writes, and create no output in this protocol
commit. This protocol is complete enough for independent implementation but
does not itself authorize implementation, execution, result generation, or
publication.
