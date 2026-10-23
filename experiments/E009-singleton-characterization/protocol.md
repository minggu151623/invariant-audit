# E009-v1 — singleton bottleneck characterization and generic exact baseline

Date: 2026-10-23. Classification: finite mathematical validation and baseline
formulation verification. Previous E008 outputs are known. No implementation or
E009 execution exists at lock. This is not a runtime scaling benchmark yet.

## New structural prediction

Retain E008's model: same RHS y; nonempty key subsets; all context cells editable
at unit Hamming cost; protected target row; target-relative equality grouping;
unique plurality; no other validity or edit constraints. Only consider an
**initially accepted** target for the new closed-form calculation.

For each rule g, let n_g0 be target-value count and M_g the largest count of a
competing RHS value, allowing absent competitors with count 0. If its group has
at least two rows, predict minimum cost to make that rule reject is

    ceil((n_g0-M_g)/2).

Rationale to test: any cell edit changes a selected target/rival margin by at
most 2, and changing that many non-target target-valued RHS cells to a strongest
rival attains the lower bound. Under initial acceptance, a non-singleton group
has enough such editable cells. Thus key edits cannot improve this group's cost.

If the group consists only of the target, predict minimum rule-rejection cost
is the least over context rows r of

    number of keys in X_g where r differs from target + 1[r_y equals target_y].

One row joins the target group with a competing RHS value. A successful rejection
must include at least one such row, supplying the matching lower bound. If no
context row exists, this minimum is INF. Final target rejection is the OR of
rule rejections, so take the least of these costs across rules.

Consequently, on initially accepted targets with **no singleton target groups**,
the full mutable-key radius equals the protected-key radius. Singleton groups
are the only route by which editable keys can reduce an accepted target's radius.
This does not cover initially rejected targets, arbitrary classifiers, unequal
edit costs, editable targets, joint database validity or correctness labels.

The closed-form algorithm must output an actual raw-cell witness at its claimed
cost; the protected target row must remain unchanged. Use raw equality/counts,
not the E008 candidate's mask/action DP implementation.

## Part A: reuse the locked E008 domain as mathematical falsification

Re-enumerate E008's four finite raw domains and six rule families, without
modifying or rerunning its original transaction/output files. This is a new
read-only comparison under a new protocol, not an untouched replication.
There are 18779 initially accepted cases in the frozen E008 summary.

Compare the new formula and witness to the pinned E008 unrestricted raw-edit
reference on **all 18779 accepted cases**, including n=1 and three-valued keys.
Also compare to the pinned E007 protected-key calculation by raw target-group
membership. Record no-singleton case counts, equality failures, finite-cost
reductions, protected-INF transitions and singleton-containing cases without
strict reduction. Do not silently infer that every singleton reduces the radius.

H9a: every formula radius and concrete witness agrees with the unrestricted
reference. Any mismatch refutes the prediction in this domain.
H9b: no-singleton accepted cases all have full radius=protected radius. The
new minimum-over-singleton/import costs must also explain every strict reduction.
H9c: the singleton triple-key example target 0000/context 1110 has exact full
radius 4 and protected radius INF; the shared-key singleton example from E008
has full radius 1 and protected radius INF. Record those witnesses explicitly.

## Part B: verify a strong generic optimization baseline before scaling

Implement an independent raw-cell-factorized mixed-integer linear program. It
must not use target-relative key masks, canonical row actions, the closed form,
dynamic programs or the specialized candidate's predicted cost. It is a generic
formulation for this model, not claimed to reproduce a published system's code.

For each editable cell use one-hot choices over its full raw domain. Cost 1 for
each choice differing from the original cell. For each context row and rule,
binary membership equals the AND of key-equality choices. For each RHS value,
linearize membership AND RHS choice; these variables give group counts. Enforce
all target/rival margins>=1 when an initially rejected target must accept.
For an initially accepted target use a binary rule/rival selector and big-M=n
to require at least one margin<=0. The entire target row is a fixed contribution.

Use /opt/anaconda3/bin/python: Python 3.13.5, NumPy 2.1.3, SciPy 1.17.1, HiGHS
through scipy.optimize.milp. Confirm these versions before the locked run.
Options: presolve=True, mip_rel_gap=0.0, time_limit=10 seconds per solve. No
thread/seed options, warm starts, approximate objective acceptance or retuning.
Require status=0 and an independently checked integer-feasible witness, or
status=2 when the direct reference is INF. Status=1/3/4 is a recorded failure
of the baseline verification; do not call a timeout an optimum or retry it.

Integrality and constraint residual tolerance: 1e-7. After selecting the one-hot
assignments, the raw Hamming cost must equal the integer objective and the
separate direct reference checker must see a decision flip. A solver success
flag alone is insufficient. Preserve baseline failure details.

Locked baseline domain (all decisions, not only accepted):

- key alphabet 2, RHS alphabet 2, n=1..3, six E008 families: 1638 cases;
- key alphabet 2, RHS alphabet 3, n=1..2, six families: 150 cases;
- key alphabet 3, RHS alphabet 2, n=1..2, six families: 330 cases.

Total 2118 generic-baseline comparisons with the unrestricted raw reference.
Order domains as listed, then n ascending, raw rows lexicographic, families in
E008 order. H9d: every optimal objective/infeasibility matches the raw reference
and every finite baseline witness passes raw/linear checks. Retain case-level
objectives, statuses and witnesses, including infeasible singleton targets.

This part verifies baseline equivalence, not method speed or solver superiority.
Build/solve wall times and machine load are not scientific outcomes here. Do
not compare these timings with closed-form execution or call it a scaling study.

## Source pins and execution

Read-only pinned modules from completed studies:

- E008 exhaustive_reference.py SHA-256 a9955309307a1c10388f750494c2546312c3cfa568ff90834a031bec189beac2.
- E007 certificate.py SHA-256 aad95f5c6bed01e8741750f9d1d8ea792f97922c37ae01d27f255ca7a3eec70c.
- E008 finite family/domain definition is copied from its locked protocol;
  importing the candidate action or DP code into the MILP module is forbidden.

Commit protocol before implementation and implementation before one run
e009-20261023-001. Guard protocol/code commits and the pinned modules. Refuse
existing destinations. Compare two complete result builds byte for byte,
excluding no numerical/witness outcomes and adding no wall-clock fields.
SciPy's milp wraps a deterministic HiGHS optimizer; if the complete builds differ,
record the divergence as a failed validation, not an ignored nuisance.

Outputs: data/E009-v1-checks.json; data/E009-v1-formula-summary.csv;
data/E009-v1-baseline-cases.jsonl.gz; data/E009-v1-witnesses.json;
results/run-e009-20261023-001.md under this experiment directory.

One locked run only. Failed mathematical/baseline comparisons must remain failed
under this identity. No domain adjustment or successful-only subset after results.
Existing E001--E008 outputs, manuscript, ZIPs and unrelated user files are protected.

## Next scientific gate

If this holds, write a full proof of the accepted-direction characterization
and separately lock a scaling comparison for the now-verified generic baseline,
the direct formula and a canonical-action optimization for rejected targets.
Assess directions separately so a cheap accepted formula cannot conceal poor
rejected-target scaling. Primary novelty still requires a precise distinction
from prior counterfactual/repair work; finite test counts are not novelty.
