# Schema width and the exact worst-case benefit of mutable keys

2026-11-05. Analytical result with an explicit proof and internal finite checks.
This is not an independent review or a historical originality certificate.
The frozen protocol states H13a–H13c; the proof below supplies the universal
argument that enumeration cannot supply. R3 remains an unchanged snapshot.

## Model and notation

There are q key attributes and one common dependent attribute y. A table is a
finite list of identified rows, so duplicate values are allowed. The protected
target row t is immutable. Relabel each attribute's target value as 0. A
nonempty family F of distinct nonempty subsets of the key attributes specifies
the checks. A row belongs to the target group for X in F when all its keys in
X equal 0. The target itself belongs to every group. A check accepts exactly
when 0 has strictly more votes than each other y value; ties reject. All checks
must accept. Every permitted change of a context cell has unit cost, with no
additional validity constraints, insertions, deletions, or changes to t.

Write rho_full(T,F) for the minimum number of cell changes making all checks
accept, and rho_fixed(T,F) for the same minimum when keys cannot change.
We consider initially rejected targets. Both radii are positive and finite:
changing every nonzero context y to 0 always succeeds. The bounds also apply
to initially accepted targets, with both costs zero, but their ratio is unused.

For a context row r let M(r) be its set of zero-valued key coordinates. For a
rule X and rival value v != 0, its contribution is

    a_Xv(r) = 1[X subset M(r)] * (1[r.y = 0] - 1[r.y = v]).

The margin m_Xv(T) is 1 plus the sum of these contributions over context
rows. Acceptance means m_Xv >= 1 for every X,v. Domains are categorical and
finite, with 0 available in each. The upper bound works for arbitrary domain
sizes. Binary domains suffice for the tightness construction below.

For each key j, order F_j = {X in F : j in X} by inclusion. Let w_j be the
largest size of an antichain in F_j, or zero if F_j is empty, and put

    w(F) = max_j w_j.

Thus w >= 1. This parameter is computed on the *listed checks*: duplicate
determinants may be removed, but logically implied FDs may not. Logical FD
equivalence does not imply equivalence of plurality checks (see below).

## Lemma 1: stronger normalization

For every original context row r and arbitrary destination u, there is a
destination c with no greater Hamming cost from r, whose contribution to
every rule/rival margin is at least that of u, and of one of these forms:

1. r is unchanged and r.y != 0; or
2. c.y = 0, M(c) contains M(r), and every changed key becomes 0.

**Proof.** If r.y != 0 and u.y = r.y, retain r when its keys are unchanged.
Otherwise set c to the original keys and y=0. Its cost is one, no more than
the at-least-one key change in u. All contributions of c are nonnegative,
whereas all contributions of u are nonpositive, proving domination.

In all other cases set c.y=0, give c zero keys on M(r) union M(u), and retain
the original concrete key value elsewhere. Its key cost is at most that of
u. Its y cost is zero if r.y=0, and otherwise one, the same as u's y cost.
If u.y=0, every group receiving u's positive contribution also receives c's;
if u.y!=0, c's nonnegative contributions dominate u's nonpositive ones.
This covers every case. Apply the construction independently to all context
rows. Summation preserves all margins and never increases total cost. QED.

In particular, an optimal full witness can be chosen so that every key edit
adds a target-key match in a row with final y=0. No rival-row key exclusion is
needed. This strengthens R3's action reduction under its unit-cost model.

## Theorem 2: a constructive exchange bound

For every table and listed family F,

    rho_full <= rho_fixed <= w(F) * rho_full.

More precisely, a normalized accepting witness with R dependent-cell edits
and K_j key edits in column j can be converted into a fixed-key accepting
witness of cost at most R + sum_j w_j K_j.

**Proof.** The first inequality is inclusion of feasible edit sets. For the
second, normalize a full witness using Lemma 1. By Dilworth's theorem,
partition each F_j into w_j inclusion chains. This chain decomposition is a
classical ingredient, not a new result [1, Theorem 1.1].

Apply all R dependent-cell changes first, leaving the original keys. Start
two tables at this point: H, which will execute the normalized key edits,
and L, which keeps the original keys throughout and may change additional
nonzero y values to 0. Maintain, for every X,v, the invariant

    min(m_Xv(L), 1) >= min(m_Xv(H), 1).

It initially holds with equality. Take the next key edit in H, in column j.
It changes a nonzero key to 0 in a row whose y=0. The affected checks are
exactly those target groups newly joined by this row, a subset of F_j. Every
affected margin increases by one; all other margins are unchanged.

For each chain in the partition of F_j, consider its affected checks whose
target groups in L still contain a nonzero-y context row. If there are none,
do nothing. Otherwise choose the largest determinant X among them and flip
one nonzero-y context row in its group to y=0. Every other affected group in
this chain that has a nonzero row contains the chosen group, because group
inclusion reverses determinant inclusion. Thus that single flip increases
each of its margins by at least one: by two for the flipped row's old value,
by one for every other rival. An affected group with no nonzero row already
has margin at least one, from the protected target alone. It needs no edit.

No other margin decreases. Consequently, for each affected margin either L
was already at least one, or it gains at least the one gained by H. This
preserves the capped invariant. Processing other chains can only help; a row
already flipped is never flipped again. There are at most w_j new flips for
this key edit. Iterate over all key edits. At the end H accepts, so the
invariant implies that L accepts. Its cost is at most R + sum_j w_j K_j.
The target cannot be chosen for a flip because its y is 0. Keys in L have
never changed. Finally,

    R + sum_j w_j K_j <= w * (R + sum_j K_j) <= w * rho_full

when normalization starts from an optimal full witness. QED.

The cap at one matters: a rival-free group might have a smaller numerical
margin than H after an import, but already satisfies the acceptance condition.
The argument promises a witness conversion, not a polynomial-time algorithm
for finding either optimum. In particular, it does not remove E012 hardness.

## Theorem 3: tightness for every listed family

For every F, the maximum of rho_fixed/rho_full over initially rejected
binary tables with protected zero target is exactly w(F). It is attained,
not merely approached by an infinite sequence.

**Proof.** Choose j and an antichain A_1,...,A_w in F_j of maximum size.
Construct these context rows, using 1 on every key not in a specified zero mask:

- For each i, one row r_i with y=1 and zero mask exactly A_i.
- One row p with y=0, all keys 0 except key j=1.
- For every C in F containing none of the A_i as a subset, w support rows
  with y=0 and zero mask exactly C.

For each critical group A_i, the only members are t and r_i. No r_l with
l!=i matches because the A_i form an antichain. Row p fails key j. No support
row matches, since its mask was required to contain no A_i. Thus each such
group has a 1:1 tie and initially rejects.

Every other group C already accepts. If C contains no A_i, its own w support
zeros and t outnumber the at most w rival rows. Otherwise A_i subset C for
some i. If a rival r_l matched C, then A_i subset C subset A_l. The antichain
property would force l=i and C=A_i, contrary to C being noncritical. Thus
this group has no rival rows and accepts from t alone.

Changing only p.j from 1 to 0 imports p into all critical groups, making them
2:1, and cannot harm other groups. Initial rejection proves rho_full=1.
With keys fixed, each isolated critical group requires changing its distinct
r_i.y; hence rho_fixed >= w. Flipping precisely these w cells makes every
row's y zero, so rho_fixed=w. Theorem 2 gives the matching upper bound for
all tables. The construction uses at most w+1+w|F| context rows. QED.

## Corollary 4: universal equality is exactly laminarity

The following are equivalent:

1. rho_fixed(T,F)=rho_full(T,F) for every table T.
2. w(F)=1.
3. F is laminar: every intersecting pair of determinants is nested.

An intersecting incomparable pair shares a key j and is an antichain of size
two in F_j. Conversely, any antichain of size two in F_j is such a pair.
This proves (2) iff (3). Theorems 2 and 3 prove (1) iff (2). Binary tables
already suffice to disprove universal equality for every nonlaminar family.

For a particular table with w>1, equality can still hold. The theorem gives
the largest *possible* gain allowed by a schema, not the gain on every table.
Singleton families are laminar, even when they contain many distinct keys;
E012 proves that finding their accepting optimum is NP-complete when the
schema varies. Laminarity eliminates a need for key edits, not search hardness.

## Small example and logical-equivalence warning

Take F={{a,b},{a,c}}, so w=2. The following binary table realizes the ratio:

| Row | a | b | c | y |
|---|---:|---:|---:|---:|
| protected t | 0 | 0 | 0 | 0 |
| r_1 | 0 | 0 | 1 | 1 |
| r_2 | 0 | 1 | 0 | 1 |
| p | 1 | 0 | 0 | 0 |

Both groups tie. Changing p.a costs one and fixes both; fixed keys require
changing both r_1.y and r_2.y, costing two.

Now add the check {a}, and add two support rows (0,1,1,0). The {a} group
has three zeros and two ones; the two original critical groups remain ties.
The ratio is still two. As *logical FDs*, however, a->y implies ab->y and
ac->y, so that FD set is equivalent to {a->y}. Using only the {a} plurality
check accepts this very table and has universal width one. Removing implied
FDs would therefore change the detector. Our classification is deliberately
about the supplied checks, not logical equivalence classes of FD theories.

## Proof audit and limits

- Every normalization case handles actual categorical values, not just binary
  masks. Cost decreases follow per-cell Hamming distance.
- The exchange uses nested *fixed-key* target groups. Groups from different
  chains need not be disjoint; shared benefits only reduce the number of flips.
- The lower bound uses distinct isolated rival rows, so one fixed-key edit
  cannot pay for two critical groups. All noncritical checks are accounted for.
- The upper bound needs no fresh domain values. Tightness uses binary values.
- A common dependent attribute, unit costs, unrestricted independent edits,
  an immutable accepting-valued target, and tie rejection are essential to
  this proof. Different dependents, weighted costs, or validity restrictions
  are outside the established statement.
- Internal checks cover finite tables; the mathematical argument above is
  the basis for universal claims. No independent mathematical review occurred.
- Comparisons with known repair bounds are recorded separately. No assertion
  of first discovery is supported by a finite literature search.

## Reference

[1] R. P. Dilworth, “A Decomposition Theorem for Partially Ordered Sets,”
Annals of Mathematics 51(1), 161–166, 1950, Theorem 1.1.
DOI: https://doi.org/10.2307/1969503.
Inspected reproduction: https://daiwz.net/course/disc_math/2023/Dilworth.pdf.
