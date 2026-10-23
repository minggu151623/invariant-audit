# E007 interpretation and the next scientific question

Date: 2026-10-23. Evidence: one locked finite run e007-20261023-001.
This note contains mathematical reasoning by the same agent, not independent
review or a novelty certificate.

## Finite outcome

39334 tables and 118002 single/joint-rule radius comparisons pass. All 114651
finite witnesses have the reported Hamming cost and flip the direct reference
decision. No radius, decision, witness or compositional-bound mismatch occurs.
Both complete builds have identical bytes. The smallest strict-gap table is
target (mask=3,Y=0), one rival (1,1) and one rival (2,1). Each individual rule
needs one repair; the conjunction needs two distinct repairs. These are finite
mathematical checks, not a claim of improved detection or representative data.

## Why the fixed-determinant formulation is correct

For a rejected target, all relevant rules have the same RHS value 0 and fixed
membership. Restoring any changed original-0 cell to 0 cannot hurt target
acceptance. Replacing a nonzero-to-nonzero edit by a nonzero-to-0 edit weakly
improves every relevant target-versus-competitor count. Edits outside all target
groups can be omitted. Hence some minimum accepting counterfactual edits only
nonzero cells to 0. For selected set S, each target-group count of 0 increases
by |S intersect G| and each competitor v decreases by |S intersect G_v|. Strict
plurality is exactly the covering inequality in the locked protocol. This proves
the formulation for any finite alphabet and number of fixed groups, separately
from E007's finite enumeration. Mathematical novelty of this argument is not
asserted.

For an accepted target, a single edit can decrease a target-versus-rival margin
by at most two. In any non-singleton group, changing ceil(margin/2) editable zero
values to a strongest rival attains rejection, including ties. The target row
is protected, and unique plurality plus non-singleton size ensures enough other
zero values are available. Singleton groups cannot be changed by this model.
Taking the minimum across rules therefore gives the flip distance.

Individually necessary repair counts give a max-of-local lower bound. The union
of individual all-to-0 repairs is feasible jointly because extra changes to 0
cannot hurt any group, giving a sum-of-local upper bound. E007 verifies both
inequalities on its domain but does not originate their general optimization
principle.

## Novelty assessment: do not promote the easy result

With binary RHS values, each selected rival gives two units of margin in every
group containing it. The joint problem becomes a standard lower-quota covering
problem over overlapping sets. Existing overlapping-vote robustness literature
already studies covering formulations. Thus the current exact subset solver,
single-group margin and observed strict gap are **insufficient by themselves**
to claim an original algorithmic contribution. E007 passes mathematical validity;
the candidate's novelty remains unresolved and weak in this restricted form.

## Next candidate: mutable determinants and shared key columns

The substantive extension is to allow edits to determinant columns, so group
membership itself changes. This is a different threat model; the old certificate
must not be reused. A shared key column can change membership in several rules
with one edit, which a fixed-group repair formulation cannot express.

Analytic design example (not a new measured dataset): rules (a,b)->y and
(a,c)->y; target row (a,b,c,y)=(0,0,0,0); other rows (0,0,1,1), (0,1,0,1),
and (1,0,0,0). The first two rows create separate ties. With protected keys,
both rival RHS cells must change to 0. If keys are editable, changing a from
1 to 0 in the last row adds a supporting 0 to both target groups in one edit.
Its two group counts then become 0:2 versus 1:1. This illustrates why row/key
roles must be represented in a joint model; it is not claimed as a new theorem.

For several rules with the same RHS and target row protected, investigate a
canonical finite set of context-row actions:

- An original-0 row can only benefit target acceptance by changing nonmatching
  determinant values to the target's values, thereby entering groups.
- An unchanged nonzero RHS row can only benefit acceptance by leaving groups;
  it may change matching determinant values to nonmatching values.
- If a nonzero RHS changes to 0, entering additional target groups can help;
  leaving a group after that change does not help target acceptance.

These are conjectured dominance restrictions for a same-RHS target-cell task,
not proved for row-level validators, different RHS columns, arbitrary constraints
or joint repair correctness. A multiple-choice optimization over these row
actions could encode shared key edits and yield a witness with an actual cell
cost. Its equivalence to unrestricted edits, complexity, practical efficiency,
and distinctness from existing repair/certification methods all require work.

Next action: fully define and literature-check this mutable-key problem, then
lock a separate falsifiable protocol before implementing/executing it. No source
acquisition, E006 reevaluation or changes to earlier outcomes are needed yet.
