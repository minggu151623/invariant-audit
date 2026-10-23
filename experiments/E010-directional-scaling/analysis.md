# E010 analysis: useful exact structure, bounded performance evidence

Date: 2026-10-23. Post-run analysis of the single locked run; no new solves,
retuning or selection of a successful-only result set.

## Observed result

All 162 preflight fixtures match unrestricted raw-destination enumeration for
both the specialization and the generic MILP. They cover 2/4/6 keys, binary
and ternary domains, both decision directions and up to three total rows.

The constructed benchmark contains 72 cases and 288 measured method calls
(two methods, two order-balanced repetitions). Every returned witness passes
the declared raw/integer/linear checks. Whenever methods certify optimality,
their exact costs agree, including across repetitions. The specialized method
finishes exactly on all 72 cases; the generic model finishes exactly in both
repetitions on 65, with 14 timeouts across the other seven dense-accepted cases.
There is no generic incorrect optimum or unexpected infeasibility.

| Regime | Cases | Both exact twice | Median paired generic/specialized time ratio | Specialized slower |
| --- | ---: | ---: | ---: | ---: |
| Accepted, dense groups | 24 | 17 | 5555.42 | 0 |
| Accepted, singleton groups | 24 | 24 | 669.87 | 0 |
| Rejected, coupled groups | 24 | 24 | 3.00 | 1 |

Ratios are medians of case-level ratios of median total times. They are not
ratios of pooled medians. The seven censored cases remain in the full data and
denominators; their limit times are not substituted into a speedup calculation.
Large accepted-direction ratios compare a direct formula with a general MILP,
including Python model construction; they are not evidence that integer
optimization as a field has improved by thousands of times.

The slower rejected case is q6-n128-d2-pairs-rejected_coupled. Median total
time is 81.27 ms generic versus 124.92 ms canonical (ratio 0.651). Both certify
cost 36 in both repetitions. It is retained. The generic model has 4445 binary
variables and 4321 constraints; canonical has 3585 variables and 130 constraints.
A smaller formulation therefore does not guarantee a faster solve.

Across rejected cases the generic model has 195--6731 binary variables; the
canonical model has 69--3647. The largest observed checked linear residual is
5.5289106626332796e-14, below 1e-7. The one-second option limits solver search;
build/decoding add time, and no total-call one-second bound is claimed.

## Interpretation

The accepted-target theorem supports an actual inexpensive implementation,
including singleton import witnesses, rather than only a correct but expensive
enumeration. The rejected-target action reduction also provides a usable exact
MILP in this bounded study. Its modest mixed timing outcome is separate from
the accepted formula's much cheaper calculation.

The study does not establish uniform scaling: n is only 16 or 128, q only
2/4/6, RHS alphabet only 2/4 and key alphabet fixed at 4. The 72 instances are
deterministic designed cases, not independent draws from a population.
The paired rule families coincide when q=2. The two timing repetitions on one
shared Mac do not estimate hardware-independent performance or significance.
No multiple-solver comparison, general-model best-performance claim or
independent assessment is made.

The generated regimes deliberately enforce their decision state. Dense blocks
repeat keys across three target-valued and one rival row. Singleton rows have
all nonmatching keys. Rejected contexts contain no target-valued RHS cells.
These simplify control of margins and can favor specialized algorithms. They
do not represent mixed, noisy real tables. Larger q can still make canonical
action enumeration exponential; the study does not remove that limitation.

## Next research decision

There is enough computational evidence to pursue a contribution-centered
manuscript, with an explicit narrow scope: exact counterfactual stability of
same-RHS plurality decisions when context keys can change. Candidate technical
content is the accepting-action dominance reduction plus the accepted-target
singleton characterization. Generic intervention objectives, vote margins and
integer optimization remain credited to prior work.

Next lock a study on meaningful source tables, treating the already inspected
E006 tables as reused evidence rather than unseen data. Measure where singleton
imports actually affect fixed-key stability, retain both decision directions,
and keep decision stability separate from reference correctness. Inspect the
closest prior theorems before making an originality claim. A new paper draft
can then be written around the scoped results; owner approval of the old audit
draft and external peer review are not prerequisites to this local work.
