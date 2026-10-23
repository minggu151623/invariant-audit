# Structural contribution: theorem-level boundary after E010

Date: 2026-10-23. Targeted primary-source comparison, not a systematic review.
No claim of being first follows from failing to find an exact phrase.

## Closest generic database framework

Meliou, Gatterbauer, Nath and Suciu, *Tracing Data Errors with View-Conditioned
Causality*, SIGMOD 2011. Read sections 4.1--4.4 and the statements of theorems
14, 15 and 17 from the [author-hosted PDF](https://people.cs.umass.edu/~ameli/projects/causality/papers/sigmod320-Meliou.pdf).
It partitions scalar input domains into predicate-equivalent regions, uses
Boolean variables with consistency constraints, proves cause equivalence and
reduces reasoning to SAT. Responsibility measures minimum additional changed
inputs. These results substantially precede our generic intervention framing.

**Decision:** remove predicate-equivalent target-relative key domains from the
proposed novelty list. Treat that quotient and generic optimization as setup.
The inspected theorems do not state our particular canonical-row dominance or
singleton-import formula. This is a narrow observation about those statements,
not proof that the specialized results are absent from all prior literature.

PDF SHA-256: 53af4aeacea0a6d4a5a489afd5a31efda8799b02fe1f03aa2f465efcb42862e6;
999569 bytes, 12 pages. Cached outside Git under the literature cache.

## Generic vote-operation optimization

Xia, *How Many Vote Operations Are Needed to Manipulate a Voting System?*
(2012), [version 3](https://arxiv.org/html/1204.1231v3). Read section 4,
definitions 3/6 and lemma 1. Minimum constructive/destructive changes and
integer constraints on score differences are established. Its principal
theorem concerns asymptotic operation-count categories under a random-vote
model. Our deterministic finite-row problem has individual row-choice
constraints and cell costs, but those differences alone are not a novelty claim.

**Decision:** do not claim newness for splitting decision directions, defining
a minimum-change radius, or introducing a score-margin MILP. The useful claim
must rest on the actual structural result and its consequences.

## Candidate content that survives this comparison

| Component | Treatment in a new manuscript |
| --- | --- |
| Minimum input edits / counterfactual view reasoning | Cite prior work; not a contribution. |
| Predicate-equivalent categorical domain reduction | Setup specialization; not a contribution. |
| Vote-margin bounds and generic MILP | Standard ingredients; not a contribution. |
| Rowwise dominance for accepting same-RHS plurality decisions | State and prove the exact specialized lemma, its assumptions and action bound. |
| Exact accepted-target radius and S<A condition | State the singleton characterization as the specialized theorem, without a worldwide first claim. |
| Sparse accepting rival constraints | Implementation corollary of dominance, not a separate headline contribution. |
| Locked synthetic and reused-source results | New bounded evidence from this project; cannot establish generic originality or accuracy gains. |

The same-RHS, protected-target, independent unit-cell-cost model is narrow.
The draft should explain what it enables and what breaks outside it. Strong
generic optimization can express the problem already; the research question
is whether its exact specialized structure makes a useful and substantive
contribution. E010 supplies bounded computational evidence; E011 tests source
impact. Retain negative empirical outcomes. The owner does not need to accept
the old audit manuscript for this local research to continue.
