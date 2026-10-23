# E008-v1 — exact certificates with mutable determinant columns

Date: 2026-10-23. Classification: finite constructed mathematical validation.
Design provenance: AI-proposed continuation of the owner's novelty requirement.
No implementation or E008 execution exists at lock. E007 is completed and known.
Novelty is a separate question, not inferred from passing this protocol.

## Scientific target and scope

Find the minimum number of **context cells** whose categorical values must be
changed to flip one target cell's FD-plurality decision. Unlike E007, determinant
columns may change. Entire target row, row count, column count and FD family are
protected. No row insertion/deletion, nulls, schema changes or external labels.

The table has keys a,b,c and RHS y. Target row 0 is (0,0,0,0). A rule X->y
accepts the target precisely when y=0 is the unique plurality among rows whose
X coordinates all equal the target's X coordinates. Ties reject. Final decision
is conjunction across rules. These are same-RHS target-cell semantics; this is
not whole-row validity, joint repair of all FDs, reference correctness or a
probabilistic claim. Every context cell is editable; cost is ordinary cellwise
Hamming distance. INF means no counterfactual exists.

For a key domain {0,...,k-1}, value 0 matches target and every nonzero value is
nonmatching. For y use {0,...,d-1}; nonzero RHS values remain distinct competitors.
The two key values 1 and 2 must not be treated as an edit when left unchanged.

## Candidate finite quotient and canonical actions

Represent context keys by a three-bit **match mask** (bit set iff raw key=0).
A rule group contains the row when every bit in its determinant set is set.
For any chosen destination mask, minimal key cost is popcount(old XOR new).
Reconstruct each changed matching cell as 0; each newly nonmatching cell as 1;
retain original raw values for unchanged nonmatching cells. This is conjectured
to preserve optimum under these equality-to-target membership tests.

For making an initially rejected target accepted, conjecture that some optimum
uses only the following actions independently per context row:

1. Original y=0: keep y=0 and choose a supermask of the original key match mask.
2. Original y!=0, y unchanged: choose a submask of the original match mask.
3. Original y!=0, y changed: set y=0 and choose a supermask of the original mask.

Action cost is key-bit Hamming distance plus the RHS change indicator. Each
row chooses exactly one action, including no-op. For each rule g and rival v,
its final contribution to the target-versus-v margin is +1 if inside with y=0,
-1 if inside with y=v, else 0. Start every margin at +1 for the target row.
The target accepts iff every final margin is >=1. A dynamic program over these
integer margin vectors finds the least-cost accepting action selection. Retain
a concrete witness. No heuristic pruning that can remove an optimum is allowed.

For an initially accepted target, reject by selecting any rule and competitor.
Enumerate all destination masks/RHS values for each row, retaining the cheapest
concrete action for each contribution in {-1,0,+1} to that rule/rival margin.
A scalar-margin dynamic program finds a minimum with final margin <=0. Take
the minimum over rule/rival pairs. This treats both decision directions; do not
silently restrict the task to initially rejected targets.

These are proposed algorithms. Calling generic finite optimization or Hamming
counterfactuals new is forbidden: see the novelty note linked below.

## Independent reference

Write a separate direct table checker that groups rows by raw tuples of key
values and counts raw RHS values. It must not import candidate masks, actions,
contributions, dominance restrictions or dynamic programs. For minimum edits,
enumerate changed subsets of actual context-cell coordinates in increasing
cardinality, and every alternative raw value at those coordinates. The first
decision-flipping assignment gives the exact radius.

Search may stop at a proven feasible upper bound: an initially rejected target
can always accept by setting every context y to 0, costing at most n-1; an
accepted target with n>=2 can reject by changing one context row to match all
three target keys with y=1, costing at most 4. For n=1 there is no allowed edit
and the radius is INF. The reference must not use candidate output as a bound.

## Exhaustive locked domains and order

All ordered context sequences, with target row prepended:

| Key domain size k | RHS domain size d | Table lengths n | Number of tables |
| --- | --- | --- | ---: |
| 2 | 2 | 1..4 | 4369 |
| 2 | 3 | 1..3 | 601 |
| 3 | 2 | 1..2 | 55 |
| 3 | 3 | 1..2 | 82 |

Total 5107 tables. Each table is checked under these six ordered FD families:

- unary_disjoint: a->y, b->y;
- shared_compound: (a,b)->y, (a,c)->y;
- nested: a->y, (a,b)->y;
- single_triple: (a,b,c)->y;
- triangle: (a,b)->y, (a,c)->y, (b,c)->y;
- unary_compound: a->y, (b,c)->y.

Expected radius comparisons: 30642. Order domains as above, n ascending, row
symbols lexicographic raw (a,b,c,y), then families in the listed order. Retain
duplicate-valued rows as distinct context cells. No seeds or external sources.

Separately test row-action dominance: for every raw origin and raw destination
row in each of the four (k,d) domains, and every rule family, there must exist
a canonical accepting action of no greater **raw Hamming cost** whose full
margin-contribution vector is componentwise >= the destination's vector.
Expected comparisons: 6*(16^2+24^2+54^2+81^2)=61854 row-pair/family checks.

## Predictions and failures

H8a: candidate and direct-reference radii agree on all 30642 comparisons; all
initial decisions agree and every finite witness changes the direct decision
with its exact claimed cell cost and an unchanged target row. Any counterexample
refutes this prediction. Preserve every mismatch and the complete locked domain.

H8b: mutable-key radius is <= protected-key radius in every case, strictly less
in at least one; record strict reductions and INF-to-finite cases separately.
Protected-key baseline uses the immutable E007 certificate module, mapping raw
rows to their rule-membership masks, with a file hash checked before import.
The runner pins its SHA-256 in implementation before execution; no E007 rerun.

H8c: all 61854 row-action dominance checks pass. This is finite evidence for a
dominance proof, not proof over arbitrary constraints or target-row mutations.

H8d: shared-key example from E007 analysis has protected-key minimum 2 and full
minimum 1: target 0000; contexts 0011, 0101, 1000; family shared_compound. The
last context's a=1->0 joins both target groups. Record direct witnesses for it.
Also record an accepted singleton-group example with protected radius INF and
mutable radius 1: target 0000, context 1001, same family.

A failure must be reported and retained under this run ID. Do not adjust domains,
algorithms or expected counts after viewing a failed run and reuse its identity.
No confidence intervals or independent-sample performance claims apply.

## Execution and artifacts

Commit protocol before implementation, and implementation before one run
e008-20261023-001. Standard-library Python only. Runner checks protocol/code
commits and baseline hash, refuses existing outputs, compares two complete builds
byte for byte, and publishes exclusively with rollback of its own partial writes.
Runtime is diagnostic only and excluded from deterministic artifact bytes.

Outputs: data/E008-v1-checks.json; data/E008-v1-domain-summary.csv;
data/E008-v1-witnesses.json; results/run-e008-20261023-001.md under this folder.
Unit tests cover both directions, raw alternate nonmatching values, ties,
shared-key synergy, singleton target and target protection.

## Novelty and stop conditions

See literature/mutable-key-novelty-20261023.md. Counterfactual causes, attribute
interventions and SAT/optimization-based explanations have established prior
work. E008 may validate a specialized structural reduction; it does not prove
the reduction or implementation is original. Before promoting it into the paper,
identify a precise difference from the strongest generic existing method and
test meaningful efficiency or a nontrivial structural consequence. If that
difference disappears, drop the novelty claim and change the research question.

No original performance study, manuscript, PDF, source archive or E003 gate is
modified. No peer-review acceptance or owner approval is needed for this local
research. Final publication decisions remain separate.
