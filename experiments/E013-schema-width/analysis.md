# E013 analysis

2026-11-05. Frozen protocol e25655d; frozen implementation b93695a.
The run completed successfully and retained full compressed case witnesses.
The results' code, protocol and case-record SHA-256 values match current files.

## Confirmatory finite checks

All hypotheses' finite predictions passed; no counterexample was found.

| Quantity | Count |
|---|---:|
| Source tables | 1,895 |
| Rejected table/family pairs checked | 81,893 |
| Laminar pairs checked | 39,379 |
| Strict accepting gains from key edits | 62 |
| Full raw destination evaluations | 3,892,339 |
| Fixed-key raw destination evaluations | 14,687 |
| Key imports processed by witness conversion | 11,944 |
| Replacement RHS flips | 12,014 |
| Single-row normalization source/destination pairs | 1,641 |
| Tightness constructions checked | 139 |

The grids include binary and ternary RHS values and binary or ternary keys.
Every family of distinct nonempty determinants is included at each grid size.
Accepted pairs are skipped (86,208); their two accepting radii are both zero.
The strict gains all occur in the binary q=3/context-size=3 grid. They are not
62 independent trials: families reuse source and destination tables. Full and
fixed searches overlap. Counts measure validation coverage, not probabilities.

The raw oracles enumerate destinations and count votes directly; neither
depends on the exchange bound or normalization. Width and chain cover are
computed separately. Every full/fixed optimum and converted witness is retained.
The 139 constructions cover every family with q<=3 plus four larger families,
with widths 1, 2, 3 and 6. Their exact lower bounds are checked using isolated
critical groups; the larger tables are not exhaustively optimized.

## Analytical result

`theory.md` proves rho_full <= rho_fixed <= w*rho_full and attains factor w
for every listed family. It characterizes universal equality exactly by
laminarity. This gives a structural interpretation of when key mutability can
matter. It does not imply that every nonlaminar table benefits, nor that
laminar optimization is easy. E012's hard singleton family has width one.

The protocol called these conjectures before checking. The proof and internal
review now support their universal statement within the model; finite success
is additional error checking, not the proof or a novelty certificate.

## Post-result follow-up, outside the locked grid

All E011 listed determinant families are singleton families. Applying the
laminar corollary therefore predicts equality for every rejected target there.
`reanalyze_e011.py` and its separate output audit archived schemas and fixed
certificates to document this consequence. This was discovered after E013's
finite run and is explicitly exploratory analytical reanalysis. It is not a
new solver experiment, source reconstruction, or held-out validation study.

This changes the interpretation of E011's failed accepting-gain prediction:
that prediction was impossible for its selected schema under this edit model.
The negative outcome is preserved, and the design limitation must be disclosed.
To evaluate observed accepting gains on external data, future work would need
a justified nonlaminar check family selected before outcomes, not selected to
make the new theorem look favorable.

## Next research

The strongest current candidate contribution is the sharp schema-dependent
gap and universal-equality characterization. Direct comparison with classical
chain decompositions and schema-dependent repair bounds is in the new literature
note. A broader theorem-level prior-work check and further proof scrutiny are
still warranted before recentering the manuscript. R3 and all older scientific
results remain historical snapshots. Submission readiness is not asserted.
