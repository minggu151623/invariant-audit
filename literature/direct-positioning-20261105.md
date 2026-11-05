# Direct positioning of the context-edit note

Date: 2026-11-05. Targeted primary-source comparison, not a systematic review
or independent originality assessment. M32 follows the owner's instruction
to continue after the October internal review. Sources below were reopened
and the listed definitions/theorems inspected in this turn.

## Close-source comparison

| Source and inspected location | Existing content credited | Difference requiring an additional argument here |
| --- | --- | --- |
| [Debosschere & Geerts, TaPP 2015](https://www.usenix.org/system/files/tapp15-debosschere.pdf), Section 2 Definitions 1–3; Section 3 Definitions 4–5, Propositions 1–3 | Cell positions, modification distance, cardinality FD repairs, cause/repair correspondence and responsibility complexity. | Their destination restores whole-table FD consistency. Our destination flips a protected target's plurality decision and may violate FDs. The rowwise dominance and singleton cost formula are additional specialized statements; neither follows simply by renaming the objective. |
| [Bertossi v7, 2020](https://arxiv.org/html/1712.01001v7), Sections 3.1 and 4, Definition 3 and Proposition 2 | Abstract repair orders, attribute-level causes and minimum-change responsibility using NULL-based repairs. | Our categorical destinations are unrestricted within fixed domains, and we do not assign responsibility to one cause or impose SQL NULL behavior. Their abstract framework can motivate encodings; a different instantiation alone is not originality. |
| [Meliou et al., SIGMOD 2011](https://homes.cs.washington.edu/~suciu/causality-sigmod2011.pdf), Sections 4.1–4.4, Lemma 10, Theorems 14/15/17/18 | Predicate-equivalent partitions, consistency constraints, cause/responsibility equivalence, SAT/weighted-MaxSAT. | Boolean encoding and minimum interventions are prior ingredients. Our proof must additionally construct componentwise dominating row destinations at actual cell cost, and attain the rejection lower bound. |
| [Xia v3](https://arxiv.org/html/1204.1231v3), Definitions 2–3, Section 4 and Lemma 1 | Minimum constructive/destructive/change-winner operations and integer score constraints. | Generic score optimization can express related problems. Our formulation enforces one final action per identified row with determinant-dependent membership and raw cell costs. This capacity/encoding difference by itself is not a theorem novelty claim. |

The 2011 PDF was recovered from a coauthor's University of Washington site;
the two previously failing author URLs were not needed. Sources were used
for mathematical scope comparison, not to endorse the present manuscript.

## Which proof content remains after removing generic ingredients?

1. The rejecting formula uses a standard margin lower bound, shows it is
   attained by editable in-group target votes whenever the group is not a
   singleton, then supplies the exact cheapest rival import for a singleton.
   Rejection of the conjunction is disjunctive, so the minimum over rules is
   exact despite overlap. This is elementary specialized structure, not a new
   generic intervention framework.
2. For acceptance, a row initially supporting the target keeps that RHS and
   expands its match mask; a rival row either retains its RHS and shrinks its
   match mask, or changes to the target RHS and expands its mask. The proof
   constructs an alternative to every raw destination, at no greater cost and
   with no worse contribution to any margin. That uniform dominance is the
   precise claim; exact MILP solving after it is a consequence, not a separate
   invention.

None of the inspected theorem statements gives these exact two specialized
claims. This narrows a defensible description; it does not establish absence
from all literature or that the claims are sufficiently important by themselves.
The different objective is a positioning fact, not evidence of usefulness.

## Analytical separation used to make the distinction concrete

For comparison under the present identified-row/protected-target semantics,
let R(T) be minimum whole-table FD-repair cost. This comparison is deliberately
not asserted to equal every variant of the 2015 V-repair model.

Family A: target (0,0), 2h context copies (0,0), one (0,1), binary domains,
single rule x -> y. R=1 by changing the lone rival, whereas the target's flip
radius is h. Family B: target (0,0), and (i,0),(i,1) for each i=1..k. Each
disjoint original conflict requires one edited cell, so R=k, while importing
one rival into the target's singleton costs one. Both ratios are unbounded.
The universal arguments appear in the R2 source. Finite enumeration for h,k
in {1,2,3} checks the examples, not the universal statement.

These examples prevent substituting a repair number for a decision radius.
They do not rule out computational reductions or general constraint solvers,
and are presented as explanatory consequences without a priority claim.

## Significance and current limit

The justified use is an exact answer to a stated sensitivity question: can
some context edit within a declared budget flip this fixed detector decision?
The formula supplies a cheap accepted-target answer, while the acceptance
reduction permits a smaller exact optimization formulation. The coupled
four-row example illustrates shared determinant effects. No demonstrated
improvement to an auditing workflow, cleaning accuracy or correctness follows.

E011 remains mostly singleton INF-to-finite effects, zero strict gains among
30 exact rejected pairs and two unknown full optima. R2 preserves these facts.
The missing original source cache at resumption means this revision must not
claim fresh E011 reconstruction. M31's historical source checks and archive
are retained as dated evidence, not a check newly run today.

## Decision

Revise as a narrow theory/algorithm note. Add explicit citations and objective
comparison, elementary separation families and a worked coupled example.
Preserve the two main structural statements and negative evidence at their
actual scope. The revision improves positioning and explanation but does not
by itself resolve whether the specialized contribution has enough scientific
significance. The next research question should target a substantive limitation
or application, rather than add favorable measurements or label this review
as independent acceptance.
