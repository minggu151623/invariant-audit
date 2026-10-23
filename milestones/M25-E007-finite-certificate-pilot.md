# M25 — finite decision-certificate feasibility pilot

Date: 2026-10-23. Status: `valid_finite_mathematical_check_novelty_unestablished`.

Protocol lock 2599ec2e14faa106ac684799360955a2f4610f15 precedes implementation
b6f8494917831e3519ae2d71a0528929e145a967. Nine synthetic unit tests pass.
One run e007-20261023-001 produced byte-identical double builds.

All 118002 comparisons over 39334 constructed tables match direct exhaustive
replacement-assignment enumeration; 114651 finite witnesses have correct cost
and change the decision. No compositional-bound failures occur. The strict
joint/local gap exists. The determinant-edit negative control correctly shows
that an RHS-only certificate does not cover an editable-key threat model.
See [checks](../data/E007-v1-checks.json),
[witnesses](../data/E007-v1-witnesses.json),
[domain summary](../data/E007-v1-domain-summary.csv) and
[run report](../experiments/E007-fd-decision-stability/results/run-e007-20261023-001.md).

This is not a detector performance result, a novelty proof or an independent
review. The binary fixed-group formulation reduces to a familiar overlapping
covering problem. It must not be promoted as an original contribution merely
because exhaustive verification passes. The current manuscript/PDF is unchanged.

The [analysis](../experiments/E007-fd-decision-stability/analysis.md) supplies the
dominance argument, records the prior-work collision, and develops the next
candidate: exact cell-cost decision certificates when shared determinant columns
are editable and alter group membership. That candidate needs a new protocol,
falsification against unrestricted edits and deeper comparison with repair and
voting-certification literature. No external peer-review gate blocks this work.

All original E001--E006 outputs and the E003-v2 execution gate are preserved.
No owner approval, public claim, external message, account or submission is
inferred. User's priority is a new contribution; further local research is the
next action, not waiting for approval of the weak baseline draft.
