# Sparse rival constraints in the canonical accepting model

Date: 2026-10-23. This is a specialization of E008's dominance proof used by
the locked E011 implementation, not a separate claim of generic novelty.

Fix one protected target and normalize its projected values to zero. Consider
one rule g and a nonzero RHS value v absent from its original target group.
Under any canonical action, the following exhaustive cases apply:

1. An originally target-valued row keeps RHS 0 and may gain matching keys.
   It never contributes a nonzero RHS value to any group.
2. An originally nonzero row retaining its RHS may only lose matching keys.
   It cannot enter a group it did not originally belong to. In particular,
   an original-v row outside g cannot enter g while retaining v.
3. An originally nonzero row changing its RHS changes it to 0; it cannot
   introduce a nonzero rival value, irrespective of new group membership.

Consequently, count_g(v) stays zero. The protected target contributes one to
count_g(0) in every destination table, so count_g(0)>count_g(v) automatically.
Omitting this inequality leaves the feasible canonical accepting assignments
unchanged. All initially present rivals remain separate constraints; no
approximation of their frequencies or merger of their identities is used.

The full raw edit problem may introduce previously absent rivals, but E008's
rowwise cost-preserving dominance theorem maps every accepting raw edit to
an accepting canonical edit of no greater cost. The converse is immediate
because every canonical edit is a permitted raw edit. Thus sparse canonical,
full canonical and raw accepting optima agree. For fixed keys the same argument
holds after restricting each mask to its original value: every nonzero row may
stay or change to 0, and original-0 rows stay unchanged.

This argument applies only when seeking acceptance, with same-RHS plurality,
the protected target row and independent unit-cost context edits. It must not
be used to drop absent rivals in a rejection model: a new rival can create a
tie, including in the singleton-group examples. It does not cover arbitrary
query constraints, weighted edits or counterfactuals preserving other outputs.

E011 tests both sparse full/fixed implementations on all 162 pinned E010
fixtures using raw destination enumeration before parsing study CSV rows.
Those finite checks support implementation correctness; they are separate
from this general proof and from scientific originality.
