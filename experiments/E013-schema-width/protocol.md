# E013: schema width and the maximum benefit of mutable keys

2026-11-05. Owner resumed local research after declining submission approval
and after the assistant corrected an overly optimistic readiness assessment.
No publication or license authority. R3 and previous experiments stay frozen.
This protocol is committed before implementation and execution.

## Analytical hypotheses derived before the finite check

All original model assumptions remain: protected target row, common RHS,
unit-cost independent categorical cell edits, nonempty determinants, ties
reject, all checks must accept. This study concerns initially rejected targets.
Remove duplicate determinants. For key j, partially order the determinants
containing j by inclusion. Let w_j be the size of a largest pairwise
incomparable subfamily, and w = max_j w_j >= 1.

H13a (stronger normalization): an optimal accepting witness needs only these
row actions: retain an original rival row unchanged, or use target-valued RHS
and add matches without removing original matches. In particular, any nonzero
row that retains its RHS but changes a key is dominated by a single RHS-to-zero
edit at its original keys. This strengthens the earlier canonical lemma.

H13b (exchange bound): every accepting full witness can be converted into a
fixed-key one of cost at most R + sum_j w_j K_j after normalization, where R
is the count of RHS changes and K_j counts edits in key column j. Consequently
rho_full <= rho_fixed <= w*rho_full. Proposed proof: do RHS changes first,
then replace each positive-row key import by at most one RHS flip per chain
of the affected determinants. Maintain domination of margins capped at one.
Dilworth's chain decomposition is established prior art, not our invention.

H13c (tightness for every schema): choose a key j and a maximum antichain
A_1,...,A_w containing j. Use a protected all-zero target, one RHS-1 row whose
zero-key mask is A_i for each i, and one RHS-0 row with every key zero except j.
For every rule C containing none of the A_i, add w RHS-0 support rows with
zero-key mask exactly C. The critical A_i groups should each be a target/r_i
tie; other groups should already accept. One j edit imports the positive row
into every critical group. Fixed-key acceptance requires all w distinct r_i
RHS flips. Predict exact costs (full,fixed)=(1,w).

If true, universal equality of the two accepting costs holds exactly for
laminar determinant families (every intersecting pair is nested), equivalently
w=1. Hardness may persist there: E012 uses singleton determinants, whose w=1.
No claim of a polynomial optimum algorithm for every laminar schema is made.

These statements are analytical conjectures until reviewed and checked. The
finite check does not prove a universal theorem or historical originality.

## Locked exhaustive domains

In every grid the protected target is all zero, context rows are individually
identified, and every multiset of context row values of the given size is used
in nondecreasing row-code order. Rules range over EVERY nonempty family of
distinct nonempty key subsets. No outcome-based selection or randomness.

1. Binary keys/RHS: q in {1,2,3}, context-row count in {1,2,3}.
2. Binary keys, ternary RHS: q=3, context-row count in {1,2}.
3. Ternary keys/RHS: q=2, context-row count in {1,2}.

For each source table enumerate ALL ordered raw categorical destination tables
on the same context rows. Compute decision masks directly from group counts
and exact Hamming costs (row-distance caching is allowed). Separately enumerate
all RHS-only destinations for the fixed-key oracle. Neither oracle may use the
new bound, normalization, action reduction or MILP. Group raw destinations by
their accepted-rule mask to reuse work across families, retaining minimum cost
and a concrete witness. Record raw evaluation counts without calling overlapping
families or destinations independent replications.

For every initially rejected family/table pair, check the exact inequality,
the w=1 equality prediction, and the constructive conversion of an optimal
full witness. Check every conversion's raw cost, unchanged keys, protected
target, final acceptance, and capped-margin invariant after each full key edit.
Also check normalization directly on every single-row source/destination pair
for each distinct q/key-domain/RHS-domain configuration in these grids, against
all possible determinants/rival margins and actual Hamming cost.

Compute w_j by exhaustive antichain subsets, independently of a minimum chain
partition computed by exhaustive chain-cover dynamic programming. Check both
sizes agree and every partition is a disjoint cover of comparable chains.

## Tightness checks

Generate the proposed construction for every nonempty schema with q<=3, and
for these fixed larger schemas:
- q=4: all singleton determinants;
- q=4: all nonempty determinants;
- q=4: {0,1}, {0,2}, {0,3}, {0}, {0,1,2,3}, {1};
- q=5: {0} union every two-element subset of {1,2,3,4}, together with
  {0}, {0,1,2,3,4}, {1} (predicted width six).

Validate initial and final group counts, the cost-one full witness, a cost-w
fixed witness, and the structural lower certificate: every critical group
contains exactly target and its distinct RHS-1 row, forcing w distinct RHS
changes under fixed keys. This is a certificate check, NOT unrestricted raw
enumeration for the larger constructed tables. Record this distinction.

## Outputs and failure handling

Commit implementation before execution. Retain a summary with code/protocol
hashes and implementation commit, complete case records with concrete witnesses
(compressed JSONL allowed), normalization denominators, construction records and
any failure. Halt on a mathematical mismatch and preserve the counterexample;
implementation fixes require a new commit and separately preserved runs.

Success criterion: all stated finite predictions and constructive witnesses
pass the complete grids. There is no timing target and no source-data claim.
Write a separate proof and close-prior-work comparison, then reassess whether
the extension is substantial enough to develop further. Do not make a new
submission-ready claim merely because these tests pass.
