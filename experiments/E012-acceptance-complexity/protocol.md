# E012: accepting-direction complexity under editable keys

Date: 2026-11-05. AI-proposed research continuation under the owner's existing
local-work authority. No external submission, paid calls or delegation.

## Analytical conjecture, before execution

The decision problem of making a rejected protected target accept within a
cell-edit budget is NP-complete in combined complexity, even with binary key
and RHS domains, singleton determinants, and every initial target group tied.
The same construction should work with keys either fixed or editable. This
does not assert hardness for a fixed schema, nor that key editing causes the
hardness, nor originality of the Set Cover technique.

Candidate reduction from a coverable nonempty Set Cover instance (U, S): one
key per element, one singleton-determinant rule per key, protected all-zero
target. Each set produces an RHS-1 row matching exactly its elements. For an
element with incidence count c, add c-1 RHS-0 rows matching only that element.
Thus each group starts with c zero votes and c one votes. Flipping the RHSs
of a cover accepts at the cover's cost. The proposed converse charges each
edited key cell in column g to any original set containing g, and each
original set row whose RHS flips to zero to that set. An untouched key column
can acquire positive margin only through one of the latter set-row flips.
The optimum should therefore equal the minimum cover size in both edit models.

This construction and its informal reasoning were derived before the finite
check. Finite checks are confirmatory for the stated implementation predictions;
the universal proof must be reviewed separately. Prior-work search is ongoing,
including known Set Cover reductions for lobbying in multiple referenda.

## Frozen finite check

Enumerate every multiset of 1, 2 or 3 subsets of universes of size 1, 2 or 3,
including empty and repeated subsets. Retain exactly those whose union is the
whole universe. Use nondecreasing integer bitmasks as the deterministic order.
No instance selection based on outcomes; no seeds, source tables or timings.

For each instance:

1. Compute minimum cover by raw enumeration of subsets of the input set indices.
2. Construct the identified-row binary table and assert that every initial
   target group is tied (and hence the detector rejects).
3. Separately enumerate all binary destination tables at Hamming distance
   0 through |U|, for each of the fixed-key and editable-key models. Enumerate
   differing cell subsets directly, not canonical actions or an existing MILP.
   Since a cover of size at most |U| exists, this range contains an optimum.
4. Evaluate each destination using direct per-rule vote counts. Compute the
   exact minimum cost among accepting destinations, without the reduction as
   oracle. Predict both radii equal the independently enumerated cover optimum.
5. For EVERY accepting destination in the enumerated range, run the proposed
   reverse extraction; require its union to cover U and its cardinality to be
   at most the destination's actual cost. This includes mixed key/RHS edits,
   edits to support rows, empty sets and duplicate identified rows.
6. Materialize and recheck a minimum witness in each edit model and the forward
   witness from an optimal cover.

Keep all case records, case/destination/success denominators, failures, script
digest and Git implementation commit. Stop on a substantive mismatch and retain
the failure. Expected acceptance criterion: no failures across the entire grid.
A pass is bounded consistency evidence, not proof, independent review, novelty
validation, performance evidence or real-data validation.

## Order and deliverables

Commit this protocol before implementation; commit implementation before running.
Write a full proof and primary-source comparison. If correct, create a new local
R3 manuscript/packet, preserving every R2 and earlier scientific artifact.
Retain E011's negative result and timeouts. Explain the new result in Vietnamese,
especially the growing-schema limitation. Do not infer content/license approval.
