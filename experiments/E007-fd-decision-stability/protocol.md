# E007-v1 — joint decision-edit certificates for overlapping FD plurality rules

Date: 2026-10-23. Classification: finite constructed mathematical validation.
Design provenance: AI-proposed after the owner required a novel contribution.
Status at lock: no implementation or execution. This is a feasibility pilot,
not a claim that the proposed formulation is new in the literature.

## Question and model

Fix two nonempty determinant columns X1/X2 and a single dependent column Y.
The target row is index 0, with both determinants equal to 0 and Y=0. Other
rows have determinants in {0,1}; equivalently a two-bit mask indicates which
of the target's determinant groups contain that row. Masks range from 0 to 3.
The target's mask is always 3. Every Y value is nonempty.

The target cell is accepted exactly when value 0 is the **unique plurality**
in each applicable determinant group. Ties reject. This is the FD portion of
E006's Rmode semantics, with no formatting/empty-value predicates to confound
the mathematical question. It does not replace E006's method or rerun E006.

An adversary may change Y in any other row. Each changed cell costs 1. All
determinants and the entire target row are protected. No insertion, deletion,
row movement, trusted truth, reference labels or probability calibration is
allowed. For alphabet size d use Y in {0,...,d-1}. The radius r is the minimum
Hamming distance of an allowed counterfactual that flips the final decision;
if no such counterfactual exists, r=INF. Stability at budget b means b<r.
Stability is not correctness.

## Proposed calculation to falsify

For an initially rejected target, let n_gv be the count of value v in target
group g and n_g0 its count of target value 0. Introduce binary z_j for every
non-target row whose current Y is not 0. The proposed optimum is min sum z_j,
subject for every group g and competitor v!=0 to

    sum_{j in g} z_j + sum_{j in g, Y_j=v} z_j >= n_gv - n_g0 + 1.

A selected z_j changes that row's Y to 0. Proposed rationale: replacing any
nonzero-to-nonzero edit by nonzero-to-zero weakly improves every target-group
plurality margin. Edits away from 0 cannot help target acceptance. Consequently
some optimum uses exactly this restricted edit form. This needs checking.

For an initially accepted target, proposed r is the minimum over groups with
at least two rows of ceil((n_g0 - max_{v!=0} n_gv)/2). A singleton group alone
cannot be destabilized by protected-determinant RHS-only edits. Construct a
witness by changing that many non-target zero values to a strongest competitor.

An implementation may enumerate subsets to solve the proposed binary program.
That is a prototype, not a scalability result or an optimization novelty claim.
The reference must instead enumerate **all** replacement assignments for other
rows and independently recalculate unique plurality directly from table values.
It must not import the proposed decision checker, margins or constraints.

## Locked finite domains

- Binary: d=2, table lengths n=1,...,6. Enumerate every ordered non-target
  sequence from symbols (mask,value), masks 0,...,3 and values 0,1.
- Ternary: d=3, n=1,...,4, similarly enumerated.
- No random seed, sampling, cherry-picked subset or external table access.
- Each table is tested with the two-rule set and each single rule separately.
- Canonical order: d ascending, n ascending, product order mask then value;
  rule subsets (0), (1), (0,1). Duplicate-valued rows remain distinct cells.
- Expected table count is sum(8**k for k=0..5)+sum(12**k for k=0..3)=39334.
  Expected decision-radius comparisons: three times that count, 118002.

## Predictions and outcomes

H7a: proposed radius equals reference minimum for every comparison; every
finite witness has exactly the reported Hamming cost and flips the decision.
One mismatch refutes H7a for this domain. Aggregate error rate is not a substitute.

H7b: for at least one initially rejected two-rule table, joint minimum exceeds
the maximum of the independently computed single-rule repair minima. This
shows a strict gap in a simple compositional bound, not a new general theorem.
Record the count, maximum additive gap and first canonical witness, including
the cases of complete overlap and disjoint editable support.

H7c: RHS-only certificates cannot be used for determinant edits. The fixed
negative control has target (X1=0,X2=0,Y=0) and another row (1,1,1). Under
RHS-only edits the target is stable for every budget; changing the other row's
X1 to 0 costs one determinant edit and makes it rejected by rule 1. Report this
scope counterexample, not as failure of a certificate under its stated model.

Also check that max(single-group repair minima) <= joint minimum <= sum(single-
group repair minima) on initially rejected two-rule cases. Report full domain
counts and the number of initially accepted/rejected and infinite-radius cases.
No statistical confidence interval or independent-observation claim applies to
this exhaustive finite calculation.

## Execution, artifacts and stopping

Lock this protocol in Git before implementation. Commit the implementation
before one deterministic execution. The runner verifies protocol/code against
their commits, refuses existing destinations, and compares two complete builds
byte for byte. Use only Python's standard library. A result failure must be
retained; do not silently fix the model and reuse a valid-looking run ID.

Run ID: e007-20261023-001. Outputs:

- data/E007-v1-checks.json: counts, all mismatch details or zero, bounds, scope.
- data/E007-v1-domain-summary.csv: each alphabet/n/rule-set aggregate.
- data/E007-v1-witnesses.json: first gap example, maximum-gap example and H7c.
- experiments/E007-fd-decision-stability/results/run-e007-20261023-001.md.

Build comparison concerns deterministic artifact bytes; timestamps and runtime
must not appear in those bytes. Print runtime only as a diagnostic if needed.
Use one locked run, no threshold tuning, expansion or real-source experiment.
Unit verification should cover ties, protected target, singleton groups,
disjoint/overlapping groups and witness correctness. It is self-review.

The novelty review in literature/novelty-reset-20261023.md is a separate gate
before claiming a contribution. E007 can pass while the novelty candidate fails.
Do not change the manuscript/PDF to claim a new method from this pilot alone.
