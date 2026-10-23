# Exact rejection radius and the singleton bottleneck

Date: 2026-10-23. Mathematical derivation by the research agent, with finite
implementation checks in E009. Originality is not established by this proof.

## Model and notation

Use the E008 model: n identified rows, q categorical keys, one RHS y, a fixed
finite RHS domain of size d>=2, and nonempty determinants X_g excluding y.
Protect the entire target row t. All other cells may independently change to
any value of their column domain at unit Hamming cost. Domains contain the
target values and an alternative value; no other constraints apply. Relabel
the target values to 0 independently in each column.

For rule g, its target group G_g contains rows agreeing with t on X_g. Let
a_g count its RHS-0 rows and b_g be the largest count of any one nonzero RHS
value, including absent values with count 0. A target is accepted exactly when
a_g>b_g for every g. Ties reject. This is unique plurality, not strict majority.
Assume the target is initially accepted throughout this document.

Let rho_full be the minimum changed-context-cell count making the target reject,
or INF if impossible. Let rho_fixed be the corresponding value with key cells
protected. The desired certificate is stability within any integer budget
strictly below rho, not a statement that the target value is factually correct.

## Lemma 1: a nonsingleton group's radius

If |G_g|>=2, the minimum cost of making rule g reject, even with editable keys,
is c_g=ceil((a_g-b_g)/2).

Lower bound. Fix a rival v. The margin count(0)-count(v) initially is at least
a_g-b_g. A key-cell change only moves one row into or out of this group, and
changes this margin by at most 1. An RHS-cell change changes one row's
contribution among -1,0,+1, hence by at most 2. These bounds apply at every
intermediate table, including after other key changes. Any sequence of k
distinct final cell changes therefore reduces any chosen margin by at most 2k.
If the final table rejects this rule, some rival margin is <=0, requiring
k>=ceil((a_g-b_g)/2). Arbitrary multistep editing cannot improve final Hamming
cost: apply just the final changed value to each differing cell once.

Upper bound. Choose a strongest rival v and change c_g context RHS-0 cells in
G_g to v, keeping keys fixed. The selected margin falls by 2c_g to <=0.
There are enough editable RHS-0 cells: a_g>=2, since otherwise initial
acceptance and |G_g|>=2 would contradict one another. Then
ceil((a_g-b_g)/2)<=ceil(a_g/2)<=a_g-1. The target stays protected. This
constructs a counterfactual at the lower bound. QED.

The margin argument itself is standard voting reasoning. The point here is to
check whether membership-changing key edits can beat it under the stated model.

## Lemma 2: a singleton group's radius

If G_g={t}, let h_g(r) be the number of keys in X_g where context row r differs
from t. Define

    s_g = min over r != t of (h_g(r) + 1[r_y = 0]),

with an empty minimum INF. The exact minimum cost of making rule g reject is s_g.

Lower bound. The target remains in its group and contributes one RHS-0 vote.
A rejecting final table must contain at least one context row with a nonzero
RHS in this group. For that row, every originally differing determinant cell
must change, at cost h_g(r). If its original RHS was 0, that cell must also
change. These are distinct cells, so the total edit cost is at least the
displayed row cost, and hence at least s_g.

Upper bound. Choose a minimizing row, set its differing X_g keys to the target
values and, only if needed, its RHS to any allowed nonzero value. Keep all
other cells unchanged. Initially no other context row was in this group; its
final votes are therefore exactly one target vote and one rival vote. The tie
rejects, at cost s_g. For n=1 no context row can enter, so rejection is
impossible. QED.

## Theorem: exact accepted-target radius

For every rule define c_g by Lemma 1 if its initial group is nonsingleton, and
by Lemma 2 otherwise. Then

    rho_full = min_g c_g.

Global rejection is the disjunction of rule rejections. Any successful edit
must reject one rule and thus costs at least its rule minimum, hence at least
min_g c_g. A witness for a minimizing rule already rejects the global
conjunction, regardless of what happens to other rules. This also explains why
overlapping groups do not require a joint optimization in this direction. QED.

## Exact condition for keys to help

Let A be the least Lemma-1 cost over nonsingleton groups, and S the least
Lemma-2 cost over singleton groups, with missing minima INF. Then

    rho_fixed = A,    rho_full = min(A,S).

A singleton group cannot be made to reject with fixed keys because it contains
only the protected target. Thus keys strictly reduce the radius exactly when
S<A. Having a singleton group is necessary, but is not sufficient.

Example without reduction despite a singleton: target (0,0,0,0), context
(0,1,1,0), rules {a}->y and {b}->y. The first group's radius is 1; the second
is singleton and costs 2 to import a rival. Both global radii are 1.

If there are no singleton target groups, rho_full=rho_fixed. If all target
groups are singleton and n>1, rho_fixed=INF but rho_full is finite. Moreover,
any singleton rule g has s_g<=|X_g|+1. For n>1,

    rho_full <= min(ceil(n/2), min_singleton_g (|X_g|+1))

when both kinds of group exist; omit a minimum for an absent kind. The
ceil(n/2) term alone is not asserted when all groups are singleton.

## Algorithm and implementation boundary

The value and a compact witness description can be found by scanning the rows
for each rule: collect RHS counts, retain editable target-valued row indices,
and compute the best singleton import if needed. With sparse counts and
constant-time categorical equality/hashing, this takes
O(n sum_g(|X_g|+1)) expected operations. An unused rival value can be chosen
from the fixed domain when all current rows have RHS 0. Construct one complete
output table only after selecting the cheapest rule. Space includes the counts
and O(n) witness indices, plus the output table if materialized.

The frozen E009 prototype eagerly copies complete tables for every singleton
candidate, so its implementation can be quadratic in n. The mathematical scan
bound is not an empirical speed claim about that code. A separately locked
implementation and scaling study are required before reporting speedups.

## Evidence and limits

E009-v1 agrees with an unrestricted raw-edit oracle on all 18779 initially
accepted cases from the declared finite domain, including 24 INF cases.
All 18755 finite formula witnesses verify. The 6509 no-singleton cases show no
radius reduction. Among 12270 singleton-containing cases, 180 finite radii
strictly decrease, 7290 protected-INF radii become finite, and 4800 do not
decrease. These are constructed-domain counts, not prevalence estimates.

An independent raw-cell-factorized MILP matches the oracle in 2118 cases:
2100 optimal witnesses and 18 infeasible cases. Full double builds are byte
identical. This validates a future baseline formulation, not comparative runtime.

None of these statements covers initially rejected targets, unequal edit
costs, mutable targets, row insertion/deletion, NULL semantics, extra validity
constraints, different RHS attributes, or a detector that resolves ties
differently. In particular, accepting a rejected target remains a joint
problem in E008; the disjunction proof does not transfer to it.

Prior work already covers voting margins, minimum cell changes, trusted cells,
and SAT-based counterfactual database reasoning. A publishable contribution
requires a precise comparison of this specialized characterization and E008's
accepting-action reduction, together with evidence of their usefulness.
