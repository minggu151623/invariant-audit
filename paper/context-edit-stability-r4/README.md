# Schema width and editable keys: R4 working preprint

2026-11-07. Author: Trần Vũ Bảo Minh, Independent Researcher.
Local manuscript for author review. Not approved, not submitted, no license
chosen. R3 and every earlier packet are preserved unchanged.

`tex/main.tex` is the source; `preview.pdf` is the compiled 10-page draft.
`source.zip` contains only `main.tex` and compiles with XeLaTeX-compatible
Tectonic using Latin Modern OpenType fonts. No arXiv server compile is claimed.

## Change from R3

R4 is recentered on the E013 result. For a listed determinant family F with a
common dependent attribute, let w(F) be the largest inclusion antichain among
determinants containing a common key. Then

    rho_full <= rho_fixed <= w(F) * rho_full

for making a protected rejected target accept, the factor is attained by a
binary table for every family, and the two optima agree on all tables exactly
when F is laminar. R3's rejection formula, NP-completeness for binary
singleton schemas and repair-distance separation are kept as complementary
results with shortened proofs. The E011 section adds the post hoc reanalysis
(all nine schemas laminar; rows 509 and 146 deduced full optimum 104) while
keeping the original 30 exact pairs and two timeouts as recorded.

Related work now covers Dilworth, the Livshits/Kimelfeld/Roy mlc conversion,
and the SYNASC 2026 media-influence slides (chain dominance on laminar
influence sets), inspected on 2026-11-07; see
`literature/schema-width-positioning-20261105.md` (addendum).

## Supplement and replay

`supplement.zip` contains this README, `main.tex`, `replay_e013.py`, the
frozen E013 protocol/code/results/proof/analysis and E011 reanalysis in
`E013/`, the proof re-audit, the literature note, the Vietnamese guide, the
verification record and a SHA-256 manifest. No source CSVs, third-party paper
bodies or unrelated workspace files are included.

After extracting into a fresh directory:

```sh
python3 -I -S replay_e013.py
python3 -I -S replay_e013.py --reenumerate
```

The first command checks hashes, coverage of every initially rejected
table/family pair, every stored witness (decoded rows, direct vote counts,
Hamming costs, fixed keys, ratio, laminar equality, converted witness) and all
139 constructions, with code written separately from the archived run. The
second repeats the frozen raw enumeration with the archived implementation and
compares it line by line with the stored records (about ten seconds on the
author's Mac). Both are delivery checks of the same cases, not new evidence.

## Honest status

The width theorem is the strongest contribution so far. Its proof was written
and then re-read by AI sessions inside this project; no independent human or
peer review exists. The literature search is targeted; the closest neighbour
(chain dominance in laminar election manipulation) was inspected from slides
only. The source study is exploratory, and its accepting-gain prediction was
structurally impossible, a disclosed design error.
