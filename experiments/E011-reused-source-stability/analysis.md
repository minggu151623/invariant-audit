# E011 analysis: source impact with a negative accepting-direction result

Date: 2026-10-23. Post-run interpretation of one locked reused-source study.
All three source tables had been inspected during E006; none is a pristine
holdout. No detector, target or timeout was replaced after outcomes.

The nine tasks contain all 18734 RHS target cells: 13762 initially accepted and
4972 rejected. Every target uses its entire dirty source table as context.
Empty strings are ordinary categorical values, so this is not the E006 U/Rmode
detector and its metrics must not be pooled with E006 results.

## Accepted targets: complete finite table census

| Dataset/task | Accepted | Fixed INF becomes finite | Finite radius decreases | Accepted differing from reference |
| --- | ---: | ---: | ---: | ---: |
| Beers brewery_name | 2410 | 127 | 0 | 0 |
| Beers city | 2275 | 127 | 0 | 8 |
| Beers state | 2275 | 127 | 0 | 8 |
| Flights sched_dep_time | 1663 | 0 | 0 | 403 |
| Flights act_dep_time | 1133 | 0 | 0 | 740 |
| Flights sched_arr_time | 1411 | 0 | 0 | 399 |
| Flights act_arr_time | 1166 | 0 | 0 | 248 |
| Rayyan journal_issn | 768 | 384 | 0 | 6 |
| Rayyan journal_title, joint rules | 661 | 368 | 1 | 4 |

The 1134 strict reductions consist of 1133 fixed-INF transitions and only one
finite-to-finite decrease. This imbalance matters: most evidence concerns
singleton groups that the fixed-key model cannot change, rather than broadly
smaller finite certificates. No no-singleton target has a reduction. H11a and
the mathematical check H11c hold within the fixed study universe.

The sole finite reduction is Rayyan one-based row 644, journal_title. Its two
target groups have sizes 4 and 1. Fixed-key radius is 2, witnessed by changing
the journal_title cells at rows 746 and 853. Full radius is 1: change the
journal_issn at row 1 to the target's value. That imports a rival into the
singleton group and creates a tie. The target row stays protected. The source
label marks the original target correct. This is a post-run selected explanatory
example from the complete exported census, not an additional experiment.

The full radius distribution for both edit models is exported as a post-run
derivative, data/E011-v1-radius-distribution.csv. Its categories are exact
integer costs and INF, not chosen performance bins.

## Rejected subset: no observed strict gain; two censored cases

The declared dirty-only hash selection yields 32 rejected targets: the Beers
brewery_name task has no rejected target, and the other eight tasks contribute
four each. All 32 fixed-key solves certify optimality. Full solves certify 30;
two reach the five-second search limit without a primal witness or dual bound.
The source code does not infer their optima from another run.

All 30 exact full/fixed pairs have equal cost. Therefore H11b is not supported.
For the two-key Rayyan title task, the exact pairs are rows 271 and 138, each
with both costs 104. Rows 509 and 146 time out in the full model; their fixed
costs are 104. Both full models have 4774 binary variables, 1396 constraints
and 397 active rival inequalities. A fixed-key witness is a valid full-model
upper bound of 104, but does not establish its full optimum. No retry, warm
start, longer cap, alternative target or favorable subset has been substituted.

This is a bounded deterministic subset, not a census of rejected radii or a
representative prevalence estimate. The negative result and timeouts limit the
practical claim for canonical accepting optimization, even though the theorem
and finite validation remain intact.

## Robustness is not reference correctness

Among accepted targets, 1816 differ from the aligned reference. Of these,
1493 have full radius at least 2. Thus H11d holds: a stable accepted decision
can still disagree with the reference. These are finite source-coordinate
counts, not independent trials, error probabilities or calibration results.
References themselves are not adjudicated truth, and no accuracy improvement
or automatic correction is claimed.

## Verification and research consequence

Before source parsing, all 162 raw/fixed oracle fixtures pass. The full accepted
stage matches byte for byte across two complete builds, and the final
dirty-stage hash is frozen before parsing reference rows. A separate post-run
checker uses original categorical codes, direct count formulas and incremental
witness updates to recheck all decisions/radii and 26453 finite source witnesses.
It also rechecks selection hashes, reference labels, bucket arithmetic, nine
source pins, 145 earlier files and every M22 bundle member. This is self-review,
not an independent scientific assessment.

There is enough evidence to draft a focused structural preprint with explicit
negative results. Its candidate contribution is the canonical row-action
dominance lemma and exact singleton rejection characterization. Predicate
quotients, minimum-change objectives and generic optimization are prior-work
ingredients. Do not launch more studies solely to obtain a positive H11b.
The next step is a contribution-centered manuscript, artifact packaging and
responsible owner explanation of this exact scope.
