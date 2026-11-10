# Schema width and editable keys: R4 working preprint

2026-11-10. Author: Trần Vũ Bảo Minh, Independent Researcher.
On 2026-11-10 the author decided to post the paper on Zenodo first. The upload
and the license choice are the author's own actions; this directory only
prepares the files. R3 and every earlier packet are preserved unchanged.

`tex/main.tex` is the source; `preview.pdf` is the compiled 12-page paper.
`zenodo/` holds byte-identical copies of `preview.pdf` and `supplement.zip`
under descriptive names for the upload, and `zenodo-metadata.md` lists the
record fields. `source.zip` contains only `main.tex` (for a later arXiv
submission). The source compiles with two engines:

- XeTeX (Tectonic, Latin Modern OpenType fonts) produces `preview.pdf`.
- pdfLaTeX, the engine arXiv uses, gets a separate preamble branch: T1 encoding
  with `lmodern`, plus T5 (`vntex`) for the Vietnamese author name only.
  `check_revision.py` builds the extracted source this way with TinyTeX
  (TeX Live 2026): 12 pages, no log warnings, all fonts embedded.

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

## Change on 2026-11-10: larger optima (E014)

The earlier text left open whether the factor w(F) is attained when the
editable-key optimum is larger than one. Proposition 1 now answers part of it:

- with at least k+1 dependent values, every family has a binary-key table
  with rho_full = k and rho_fixed = w(F) * k;
- with a binary dependent attribute and the family {{a,b},{a,c}},
  rho_fixed <= rho_full + 1, so the factor 2 occurs only at rho_full = 1.

The case of d <= k dependent values is open in general. E014 checks the
construction on nine locked cases and the binary bound on all 74,612 tables
with at most six context rows; its protocol was committed before the code
(`6c8827a`, `d98e454`), and the single run passed (`27ca9b2`). The separation
result of R3 is now Proposition 2; `review/review-20261107.md` predates this
change and calls it Proposition 1.

Other edits on the same day: the abstract and Section 6 say that the benchmark
experiment was our own; "RHS" is defined; Section 9 says where the supplement
is; the PDF carries title and author metadata.

## Supplement and replay

`supplement.zip` contains this README, `main.tex`, `replay_e013.py`, the
frozen E013 protocol/code/results/proof/analysis and E011 reanalysis in
`E013/`, the proof re-audit, the E014 protocol/code/results/analysis in
`E014/`, the literature note, the verification record and a SHA-256 manifest. No source CSVs, third-party paper
bodies or unrelated workspace files are included.

After extracting into a fresh directory:

```sh
python3 -I -S replay_e013.py
python3 -I -S replay_e013.py --reenumerate
python3 -I -S E014/verify_scale.py --verify
```

The first command checks hashes, coverage of every initially rejected
table/family pair, every stored witness (decoded rows, direct vote counts,
Hamming costs, fixed keys, ratio, laminar equality, converted witness) and all
139 constructions, with code written separately from the archived run. The
second repeats the frozen raw enumeration with the archived implementation and
compares it line by line with the stored records (about ten seconds on the
author's Mac). The third recomputes every E014 case and compares the result
with the stored summary (about thirty seconds). All three are delivery checks
of the same cases, not new evidence.

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

Proposition 1 and its proofs were also written and checked by AI sessions in
this project. Part (b) covers one two-rule family only.
