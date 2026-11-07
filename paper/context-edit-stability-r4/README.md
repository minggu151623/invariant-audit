# Schema width and editable keys: R4 working preprint

2026-11-07. Author: Trần Vũ Bảo Minh, Independent Researcher.
Prepared for arXiv: the draft-only status sentences have been removed from the
text. It is not submitted, and no license has been chosen. R3 and every
earlier packet are preserved unchanged.

`tex/main.tex` is the source; `preview.pdf` is the compiled 11-page draft.
`source.zip` contains only `main.tex`. It compiles with two engines:

- XeTeX (Tectonic, Latin Modern OpenType fonts) produces `preview.pdf`.
- pdfLaTeX, the engine arXiv uses, gets a separate preamble branch: T1 encoding
  with `lmodern`, plus T5 (`vntex`) for the Vietnamese author name only.
  `check_revision.py` builds the extracted source this way with TinyTeX
  (TeX Live 2026): 11 pages, no log warnings, all fonts embedded.

The pdfLaTeX pages were rendered and inspected. In that build, `ș` is
assembled from "s" plus a comma accent, so the PDF text layer reads "s,".

arXiv may run a different TeX Live version, and arXiv's own compile has not
been tried.

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

A post-draft proof review (`review/review-20261107.md`) was done by an AI
session in the same project, so it is not independent. It found no
mathematical error. It did find that Theorem 1 and Corollary 1 omitted their
scope, an initially rejected target; this is now fixed, with a counterexample
for accepted targets. An independent random brute force
(`review/review_bruteforce.py`, ternary keys and y, 10,900 tables) agreed with
Theorems 1–3. It was written and run after the fact; it is not preregistered.
