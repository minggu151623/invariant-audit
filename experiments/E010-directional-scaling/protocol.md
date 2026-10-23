# E010-v1 — bounded, direction-separated algorithm comparison

Date: 2026-10-23. E009 outcomes are known. Implementation and execution are
absent at lock. This is a constructed computational study, not detector accuracy
or real-data validation. No new source data, paid services or GPUs are used.

## Question and predictions

Does the accepted-target closed form and the rejected-target canonical-action
reduction yield useful exact computations beyond tiny raw enumeration?
Compare against E009's verified, raw-cell-factorized MILP; do not enumerate
whole raw rows as a deliberately weak optimization baseline.

H10a: generalized implementations agree with an unrestricted raw-domain oracle
on every preflight fixture, and all returned finite witnesses have the claimed
cell cost and reverse the raw decision.
H10b: on initially accepted benchmark cases, the direct formula returns an
exact witness and agrees with every independently verified generic optimum.
Report its time separately for dense and singleton groups.
H10c: on initially rejected cases, the canonical-action MILP agrees with every
generic optimum when both certify optimality. Its practical advantage is an
open question: retain timeouts, slower cases and larger action formulations.

No speedup threshold is a validity gate. Failing to improve runtime is a
negative scientific outcome, not grounds to change cases or time limits.

## Implementations

Freeze E009's generic_milp.py, SHA-256
`2be4637ab7b58efea07495fedba3da1ed678c719df0008bce0ac54e4699bfebb`.
Reuse its raw-cell
`build` implementation without action masks or formula bounds. A new execution
wrapper may change the solve time limit and record witnesses/incumbents/bounds;
it must not alter the generic mathematical formulation or inject candidate costs.

Accepted specialization: compute rule counts and singleton import costs in a
scan, retain compact candidate descriptions, then materialize only one winning
witness. No repeated complete-table copying per singleton row.

Rejected specialization: enumerate E008's canonical row destinations for q
keys (all supermasks for original RHS=0; unchanged-RHS submasks and RHS=0
supermasks otherwise). Give each row exactly one selected action. Binary
action variables have actual row-Hamming costs. For each rule and nonzero RHS
value enforce sum(context contributions)>=0, since the protected target adds
1. This is an exact accepting MILP by E008's dominance proof. Do not aggregate
identical rows, prune actions using outcomes, warm-start, add candidate bounds
to the generic model, or tune solver parameters after execution.

Use Python 3.13.5, NumPy 2.1.3, SciPy 1.17.1 and scipy.optimize.milp. Both MILPs:
presolve=True, mip_rel_gap=0.0, time_limit=1.0 second per solve. No hidden retry,
thread or seed options. Time limits bound solver search, not Python model build
or total process time. Record build time, solve time and total method time.
An accepted formula has no solve time; its total includes witness construction.

Status 0 is exact only with independently checked integer-feasible primal,
objective/cell-cost equality and raw decision flip (tolerance 1e-7). Retain
status 1 timeouts and their incumbent/bound/gap when available, but never label
them exact, even if an incumbent matches the other method. Check any available
incumbent with the same raw/integer/linear tests and record infeasible ones.
Status 2/3/4 is retained; all benchmark cases have a finite flip, so these
statuses are unexpected and invalidate correctness, not silently skipped.

## Preflight fixtures

For q in (2,4,6), key alphabet k in (2,3), RHS alphabet d in (2,3), and each
of the two rule families below, use a protected all-zero target plus each of
six context rows: all-zero keys/RHS 0; all-zero keys/RHS 1; all-one keys/RHS 0;
all-one keys/RHS 1; keys alternating 0,k-1 starting at 0/RHS d-1; all k-1
keys/RHS d-1. Keep duplicates: 144 fixtures.

Also use binary domains, each q and family, with two context rows as follows:
(all-zero keys/RHS 1, all-zero keys/RHS 1);
(alternating 0,1 keys/RHS 1, complementary keys/RHS 1);
(all-one keys/RHS 0, all-zero keys/RHS 1). This adds 18 fixtures.

For all 162 fixtures, enumerate all raw destination context tables and compute
minimum Hamming flip cost independently of actions, masks, formulas and MILP.
Compare the applicable specialization AND generic MILP to that optimum.
Save every preflight case and result. Any mismatch or solver status other than
0 aborts benchmark execution and produces a failed-preflight report.

## Frozen benchmark: 72 cases

Cartesian product, in this order: q=(2,4,6), n=(16,128) total rows,
d=(2,4), family=(star,pairs), regime=(accepted_dense,accepted_singleton,
rejected_coupled). Key alphabet is fixed k=4. Target row is all zero.

Star determinants are (0,j) for j=1..q-1. Pairs are (0,1),(2,3),...,(q-2,q-1).
At q=2 both families coincide: retain this deliberate duplicate-family control.

Each case ID is `q{q}-n{n}-d{d}-{family}-{regime}`. Create a fresh Python
Random(int.from_bytes(SHA256(case_id UTF-8).digest(),'big')) per case.
No source labels or observed runtimes determine the generated table.

- accepted_dense: process context rows in successive blocks of four. The
  first block has all keys 0. Each later block draws one common key vector,
  independently per key: 0 if rng.random()<0.65, otherwise rng.randrange(1,4).
  The first three rows of each block have RHS 0; the fourth has RHS
  1+(block_index mod (d-1)). The final partial block uses the same rule.
  Every target group is nonsingleton and initially accepted.
- accepted_singleton: each context key is independently rng.randrange(1,4),
  RHS rng.randrange(d). Override only the first context RHS to 1 as part of
  this declared generator. Every target group initially contains only the target.
- rejected_coupled: first four context rows have all keys 0 and RHS 1.
  Each later row draws independent keys by the same 0.65 rule as dense, then
  RHS rng.randrange(1,d). Every target group initially rejects.

Generate each table twice before timing and require byte-identical values.
Check declared decision and singleton/nonsingleton structure before any solve;
do not repair a failed generator. Store full generated tables and their hashes.

## Timing, ordering and reporting

One untimed warmup: target zero plus one all-zero/RHS-1 context, q=2,d=2,
star family. Solve both MILPs and run the accepted formula on the analogous
all-zero/RHS-0 table. Warmup is not a benchmark observation.

Run exactly two measured repetitions per case, sequentially on this machine.
First repetition executes generic then specialized; second reverses that order.
No case retries, early stopping or successful-only reporting. Reuse no built
models, solver solutions or cached actions across measured calls. Model build
and witness decoding belong to total time. Common serialized result export and
posthoc verification time are not included. Record Python/runtime/machine info;
no isolated hardware or controlled machine-load claim is made.

Store each method result, time, model dimensions, status, raw witness, bounds
and errors. Analyze all cases by decision regime, q, n, d and family. For a
pair compare median total time across the two repetitions only if both methods
are exact in both repetitions. Count all censored/failed cases in denominators
and tables. Do not replace timeouts with their cap when calculating speedup.
Report variable/constraint sizes and cases where specialization is slower.
Timing data need not match byte for byte and must not be regenerated for that
reason. No inferential significance or population prevalence from these cases.

## Transaction and scope

Protocol commit precedes implementation commit and a single run ID
`e010-20261023-001`. Refuse existing output destinations. Pin the imported E009
module and check committed E010 source/protocol/runtime before running. Save:

- data/E010-v1-preflight.json.gz;
- data/E010-v1-cases.json.gz;
- data/E010-v1-observations.jsonl.gz;
- data/E010-v1-summary.csv;
- data/E010-v1-checks.json;
- experiments/E010-directional-scaling/results/run-e010-20261023-001.md.

Preserve earlier experiments, manuscript and bundles. This is a constructed
algorithm comparison; even a large speedup does not establish novelty or
correctness labels on external data. Next decide whether the specialized result
is useful enough for a source-table study and a contribution-centered manuscript.
