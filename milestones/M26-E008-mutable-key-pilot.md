# M26 — mutable-key exact-certificate pilot

Date: 2026-10-23. Status: `valid_finite_mathematical_check_theorem_draft`.
Previous goal turn: progress (M24/M25 novelty reset and E007 finite feasibility).
Current turn: progress, not waiting for owner review or external peer review.

Protocol lock efc1365d7e6f2a18324d9e5d6ef3c5ea46ef0ebc precedes implementation
14fe2147f345b6f496e7b91b0bc6066748aa2b1b. Nine unit tests pass. One run
e008-20261023-001 completes with byte-identical double builds.

The prototype computes exact minimum changed-context-cell counts for a target
decision with editable keys and RHS, target row protected. It uses canonical
row actions and margin dynamic programs. A separate reference enumerates raw
coordinate changes and every alternative raw value, without those restrictions.
Three-valued keys test that changed nonmatching values are not silently free.

- 5107 constructed tables; six rule families; 30642 exact-radius comparisons.
- All 30618 finite witnesses have exact raw cell costs and flip the decision.
- All 61854 row-action dominance checks pass; no edit-space nesting failures.
- 210 finite protected-key radii strictly decrease when keys may change.
- 7290 protected-key INF cases have finite mutable-key radii.
- The shared-key example has radius 2 with fixed keys and 1 with editable keys;
  the singleton-group example changes from INF to 1.

These counts describe the locked finite domain, not independent trials,
real-data prevalence, improved detector accuracy or a publication outcome.
See [checks](../data/E008-v1-checks.json), [summary](../data/E008-v1-domain-summary.csv),
[witnesses](../data/E008-v1-witnesses.json) and
[run report](../experiments/E008-mutable-key-certificates/results/run-e008-20261023-001.md).

The [theorem draft](../experiments/E008-mutable-key-certificates/theory.md)
gives a general target-relative key quotient, a three-case dominance proof,
an action-count bound of 2^q+1 per row and exact decision-direction programs.
It states same-RHS/unit-cell-cost assumptions and unfavorable rule/RHS scaling.
Its mathematical derivation is self-review, not independent verification.

Primary prior work on view-conditioned causality already allows changed input
values and SAT/MaxSAT reasoning. Attribute-level interventions are also established.
The candidate is the specialized cost-preserving action reduction, whose
originality and practical value remain unestablished. Do not call minimum edits,
generic optimization or the finite test counts themselves novel.

Next: compare the reduction to generic exact optimization, validate a useful
algorithm beyond toy correctness and perform a deeper theorem-level collision
review. Research proceeds autonomously; original E001--E007 outputs, M21 source
and M22 evidence bundle are preserved. No actual submission or release occurred.
