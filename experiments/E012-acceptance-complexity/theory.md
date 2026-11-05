# Acceptance is NP-complete even for binary singleton checks

AI-derived proof, 2026-11-05. Internal mathematical review, not independent
review or a novelty certificate. This extends the working paper's stated model.

## Decision problem and scope

Input: an explicitly represented binary table with identified rows, an immutable
target row, one or more nonempty determinant rules sharing an RHS, and a
nonnegative integer budget B. Each rule accepts the target iff its own RHS value
is strictly more frequent than the other binary value in its determinant group.
All rules must accept; ties reject. The input target is rejected. Question:
can at most B context-cell changes make it accept? Either all context cells may
change, or a separate fixed-key version allows only RHS changes.

**Theorem.** Both decision problems are NP-complete in combined complexity,
even when every determinant consists of one key column and every target group
is initially tied. There is a polynomial optimum-preserving reduction from
nonempty, coverable Set Cover to each version, with identical constructed table.

The number of keys and rules varies with the input. This is not a fixed-schema
data-complexity claim. Binary restriction suffices for the claimed hardness.

## Proof

Let U = {1,...,q}, q >= 1, and S_1,...,S_l be a family with union U. Let c_g
be the number of input sets containing g, so c_g >= 1. A minimum cover has
size tau <= q (choose one set per element and discard repetitions).

Use binary columns x_1,...,x_q,y and rules x_g -> y for all g. Protect the
all-zero target t. For each S_i introduce one identified set row r_i with
y = 1 and x_g = 0 exactly when g belongs to S_i. For each element g add
c_g - 1 identified support rows with y = 0, x_g = 0, and all other keys 1.
Repeated tuples remain distinct identified rows as in the paper's model.

The group for x_g contains c_g set rows with RHS 1, the target, and its c_g - 1
support rows. Supports belonging to other elements do not match x_g.
Hence its zero/one counts are exactly (c_g,c_g). The target initially rejects.
The number of context rows is l + sum_g(c_g - 1) <= l + q*l, and writing
the complete binary table takes polynomial space and time in the Set Cover
input. The same input budget B is used.

**Upper bound.** Given any cover C, change y from 1 to 0 in each set row
indexed by C. Membership stays unchanged. Every group has at least one such
row, increasing its zero-minus-one margin from zero by at least two. All rules
accept. The cost is |C| under either edit model, so both radii are at most tau.

**Lower bound for unrestricted edits.** Take any accepting destination T' at
Hamming cost K. Extract an input-set subfamily C' as follows:

* For every changed key cell in column x_g, select any fixed original input set
  containing g. Such a set exists. Several edits may select the same set.
* For every original set row r_i whose final RHS is zero, select S_i.

Each selection is charged to one distinct changed cell before duplicate sets
are discarded: a key cell for the first rule or that set row's RHS cell for the
second. Thus |C'| <= K. Edits changing a support RHS from zero to one are not
charged; this only strengthens the inequality.

To show coverage, fix g. If any key cell in column x_g changed, the first
selection rule covers g. Otherwise membership in the singleton-determinant
group x_g is exactly its original membership, regardless of edits in other
columns. Initially its zero-minus-one margin was zero. In that unchanged group,
flipping an original zero RHS to one decreases the margin by two, and flipping
an original one RHS to zero increases it by two. A positive final margin
therefore requires at least one original one-to-zero flip in the group. Every
original one in this group is a set row for a set containing g. The second
selection rule covers g. This holds for every element, so C' is a cover.
Consequently tau <= |C'| <= K. The argument includes simultaneous key/RHS
changes and edits to support rows; it does not assume canonical actions.

The full optimum is tau; restricting to fixed keys cannot lower it, and the
upper-bound witness uses only RHS edits. Thus both optima equal tau.
Set Cover remains NP-hard on coverable, nonempty instances: empty universes
and uncovered elements can be decided immediately, mapping respectively to
fixed yes/no instances if reducing from its unrestricted formulation. The
constructed destination table is a polynomial-size certificate; its cost,
protected target, key restrictions and per-rule counts are checkable in
polynomial time. This proves NP membership and NP-completeness for each version.

## What follows, and what does not

Together with the existing rejection formula, the theorem supplies a worst-case
directional complexity distinction: destroying acceptance is polynomial in the
explicit table/rule input, whereas enforcing all checks is NP-complete already
in the binary singleton subcase. It does not prove key edits are the source of
hardness: the fixed-key version is hard on the same instances. On this reduction
family keys never lower the optimum. No empirical speed or accuracy claim follows.

For a fixed number q of keys and fixed RHS alphabet size d, the earlier
canonical-action lemma also gives a simple polynomial algorithm. Remove
duplicate rules, so m <= 2^q - 1. Process rows one at a time, retaining the
minimum cost for each vector of their accumulated m(d-1) rival-margin
contributions. Each coordinate lies in [-n,n]; choose among at most 2^q+1
canonical actions per row. After all context rows, accept vectors componentwise
nonnegative (the protected row contributes one). This is at most
O(n (2n+1)^{m(d-1)} (2^q+1) m(d-1)) elementary transition work, apart from
action construction. It is a standard finite-state dynamic program, not an
FPT claim or a proposed practical solver. This observation is analytical only;
E012 tests the reduction, not a DP implementation. More refined parameterized
bounds are outside this revision.

## Finite check and prior art

The frozen protocol and raw enumeration are in this directory. They test small
instances and extraction behavior, not the universal proof. Known lobbying
hardness uses Set Cover-style incidence matrices; this method is explicitly
credited, not presented as newly invented. The additional obligation here is
that arbitrary membership/key-cell edits cannot evade the extracted-cover
lower bound. See `literature/acceptance-complexity-positioning-20261105.md`.
