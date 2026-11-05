# Positioning the accepting-direction complexity result

Date: 2026-11-05. Targeted primary-source comparison, not an exhaustive novelty
search. Read alongside `direct-positioning-20261105.md` for repairs/causality.

## Primary sources

1. Richard M. Karp, *Reducibility Among Combinatorial Problems*, 1972,
   pp. 85-103. [Author's paper reprinted with introduction](https://www.cs.umd.edu/~gasarch/BLOGPAPERS/Karp.pdf).
   The original paper identifies Set Covering among its complete problems.
   Our reduction starts from that established problem, not from a newly claimed
   hardness fact about covering.
2. Robert Bredereck, Jiehua Chen, Sepp Hartung, Rolf Niedermeier, Ondřej Suchý,
   Stefan Kratsch, *A Multivariate Complexity Analysis of Lobbying in Multiple
   Referenda*, AAAI 2012, pp. 1292-1298.
   [Publisher record](https://ojs.aaai.org/index.php/AAAI/article/view/8248),
   [author-hosted manuscript](https://fpt.akt.tu-berlin.de/publications/lobbying-aaai12.pdf).
   The publisher migration lists a 2021 upload date; the volume, proceedings and
   PDF identify AAAI 2012. Do not misdate the research as 2021.

The lobbying paper's introduction defines row modifications of a binary voting
matrix to obtain a majority in every column. Sections 2-3, Reductions 1-2,
explicitly use Set Cover incidence matrices and balancing rows; Theorem 1
establishes a restricted NP-hardness result, while Theorem 3 concerns kernel
lower bounds. Section 4 studies tractable parameter restrictions. This is a
close antecedent to the covering/balancing proof idea. Its row-modification
operation and electorate semantics differ from the present shared-RHS cell
edits with mutable memberships.

## Precise claim boundary

We must not present “many coupled majority goals are hard,” the Set Cover
incidence construction, or balance-adjustment rows as inventions. The local
result states an optimum-preserving reduction for this exact protected-target
cell-Hamming model. Its converse explicitly handles arbitrary key edits: charge
each changed membership coordinate to a set covering that coordinate; unchanged
coordinates need an originally incident set-row RHS flip. This obligation is
not discharged merely by observing that fixed-key actions resemble lobbying.

The proof establishes the claimed problem's hardness if correct; it does not
establish historical priority. The finite grid does not settle novelty either.
Further literature may express the same specialized statement in different
language. A reasonable paper description is a restricted directional-complexity
result with an elementary reduction and explicit proof, not a breakthrough in
voting complexity or a new general NP-hardness technique.

## Implications for the manuscript

The previous rejection formula is polynomial even when the schema varies;
the accepting decision problem is NP-complete with varying binary singleton
rules. Fixed keys remain hard on the same construction, so do not attribute
hardness to key mutability. The reduction has identical full/fixed radii and
does not contradict E011's absence of observed accepting-direction savings.
For fixed key count and fixed RHS alphabet, a conventional margin-vector DP
is polynomial (potentially with a very large exponent); no practical/FPT claim
is inferred. These distinctions improve the algorithmic story without replacing
the negative reused-source outcomes or claiming better cleaning accuracy.
