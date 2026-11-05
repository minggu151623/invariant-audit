# Direct positioning of the schema-width result

2026-11-05. Targeted primary-source comparison, not an exhaustive novelty
review. Read with `experiments/E013-schema-width/theory.md`. The newly developed
claim concerns protected-target plurality checks, not restoration of all FDs.

## Classical ingredient: Dilworth

R. P. Dilworth, *A Decomposition Theorem for Partially Ordered Sets*, Annals of
Mathematics 51(1), 161–166 (1950), DOI 10.2307/1969503.
[Primary-paper reproduction](https://daiwz.net/course/disc_math/2023/Dilworth.pdf).
Theorem 1.1 equates antichain width and the minimum number of chains partitioning
a finite poset. E013 uses this fact without claiming it as new. The application
requiring proof is the capped-margin exchange: one fixed-key RHS flip per chain
can replace a positive-row key import. Dilworth alone says nothing about votes,
Hamming costs, protected rows or accepting counterfactuals. E013 also supplies a
table attaining the factor for every listed family, using isolated critical
groups and supports that satisfy all other checks.

## Closest inspected schema-dependent witness bound

Ester Livshits, Benny Kimelfeld and Sudeepa Roy, *Computing Optimal Repairs for
Functional Dependencies*, arXiv:1712.07705v1 (20 December 2017).
[Primary paper](https://arxiv.org/pdf/1712.07705).
Inspected Section 4.2, Proposition 4.4 and its proof, Corollaries 4.5–4.8,
and Section 4.4, Theorem 4.12. This note identifies the inspected arXiv version,
not an unchecked later journal theorem numbering.

Their Proposition 4.4 converts a consistent update into a consistent subset
without extra cost, and a consistent subset into an update with factor mlc
for consensus-free FDs. Here mlc is the minimum attribute set hitting every
left-hand side. The latter construction assigns fresh values to edited keys
of deleted rows. Corollary 4.5 compares the two optima; Theorem 4.12 combines
this conversion with subset repair approximation to obtain a 2*mlc algorithm.

E013 compares two *cell-edit* optima for the same protected-target decision.
It keeps every row, uses existing target values, and replaces key imports
with RHS flips through nested groups. Its parameter is incident inclusion
width, and its bound alone is not a polynomial approximation algorithm:
finding the fixed-key optimum remains hard in combined complexity.

Two analytical distinctions prevent identifying our w with their mlc:

- F={{a,b},{a,c}} has minimum hitting set {a}, hence mlc=1, but w=2. The
  four-row example in E013 attains a fixed/full ratio of two.
- F={{a_1},...,{a_q}} has mlc=q but w=1; all its accepting radii agree
  under fixed and mutable keys.

These are parameter and objective distinctions, not evidence that no more
general known theorem could imply our result. In particular, merely using
different problem terminology would not establish originality. Our claimed
technical work is the explicit margin exchange, its sharp construction for
each listed family, and the resulting universal-equality characterization.

## Boundaries and unfinished search

Palash Dey, *Gerrymandering: A Briber's Perspective*, arXiv:1909.01583v1
(2019), https://arxiv.org/pdf/1909.01583: inspected the voting setting and
Problem Definitions 1–4, plus the stated complexity map. These optimize
voter transfers between districts, with graph restrictions in some variants,
and aggregate district winners to determine the election winner. E013's
target groups overlap and all must individually accept; a key edit may change
membership in several of them. E013 also permits changing y votes and compares
that restricted cost with the cost allowing both types of cell edit. This
source establishes that membership-changing plurality interventions themselves
are prior art; its inspected definitions do not state E013's exchange ratio.

A second search found Adrian Miclaus, Luca Mureșan and Alexandru Popa,
*Minimum-Cost Electoral Manipulation Under Media Influence: Hardness,
Approximation, and Algorithms*, SYNASC 2026 author slide page:
https://easychair.org/smart-slide/slide/TstX.
Its abstract explicitly discusses laminar influence sets and chain-based
parameterized algorithms. This is a closer methodological lead than a generic
bribery citation. Only the abstract/slide landing page was inspected, not the
proofs: do not assert theorem-level separation yet. Its described actions
select media strategies that trigger voters after influence thresholds; E013
instead bounds the exchange between key edits and RHS flips. Comparing those
chain arguments is outstanding before a stronger originality assessment.

Earlier R2/R3 comparisons to cell-based causality, vote operations and lobbying
remain relevant (`direct-positioning-20261105.md` and the E012 comparison).
The 2023 ICDT paper *The Consistency of Probabilistic Databases with Independent
Cells* by Gilad, Imber and Kimelfeld was identified as another relevant lead:
https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ICDT.2023.22.
Only its abstract was inspected in the preceding search; no theorem-level
nonoverlap conclusion is drawn from it here.

Searches for plurality/FD robustness, laminar bribery, antichain interventions
and schema-dependent repair approximations produced no verified identical
statement in the inspected sources. Negative search results are not a novelty
certificate. Next inspect fixed-versus-mutable intervention classifications
and voting models with nested constituencies; compare formal statements and
proofs, not titles alone. Historical priority and independent assessment
remain unestablished. No external publication action follows from this note.
