# Context-edit stability: R3 working preprint

2026-11-05. Author: Trần Vũ Bảo Minh, Independent Researcher.
Local manuscript for substantive author review; not approved or submitted.

`tex/main.tex` is the source; `preview.pdf` has 10 pages, three tables and ten
references. `source.zip` contains only `main.tex`. It compiles locally using
XeLaTeX-compatible Tectonic with embedded fonts; no arXiv server compilation
is claimed. The PDF and original E008--E011 evidence are distinct artifacts.

## Change from R2

The new Theorem 3 proves that accepting a rejected target within a cell-edit
budget is NP-complete when the schema varies, even for binary columns,
singleton determinants and initially tied target groups. A Set Cover reduction
preserves the optimum with fixed keys AND with editable keys. The converse
handles arbitrary membership/key edits. This complements the polynomial
rejection formula and the exact canonical accepting optimization.

The covering technique is established prior art in lobbying complexity and is
credited. Neither the proof nor the small check certifies historical priority.
The standard margin-vector DP paragraph explains polynomial solvability for
fixed key count and fixed RHS alphabet; it is not implemented or benchmarked.

E012 checks every coverable multiset of 1-3 subsets of universes of size 1-3.
All 111 instances / 222 radii agree with independently enumerated minimum
covers. It checks 147523 destinations across two overlapping edit models and
successfully extracts covers from all 25490 accepting destinations. This is
finite consistency evidence, not a proof or independent review.

## Packet and reproduction

The R3 supplement contains this README, the revised main.tex, `replay_e012.py`,
the frozen E012 protocol/code/outcomes/analysis/proof in `E012/`, the complexity
positioning note, Vietnamese owner guide and delivery verification, with a
SHA-256 manifest. It contains no raw source CSVs, third-party paper bodies,
account information or unrelated workspace files.

After extracting the supplement into a fresh directory:

```sh
python3 -I -S replay_e012.py
```

This read-only replay checks code/protocol hashes, the complete input grid,
all stored case counts and optimum witnesses, and repeats the frozen raw-cell
enumeration/extraction. It requires no Git, NumPy, SciPy or source downloads.
It is delivery verification of the same cases, not additional research evidence.
The archived original enumerator additionally recorded the Git implementation
commit at execution and expects a Git checkout if its main function is invoked.

Original E008--E011 evidence remains in the frozen M31 companion; R2 examples
and their checker remain in the separate R2 supplement. These previous packets
and all 197 inventoried scientific files are preserved byte for byte. This R3
supplement adds to them, rather than silently replacing older snapshots.

The E011 evidence remains 30 exact rejected pairs with equal fixed/full costs
and two unresolved full-model timeouts. There is no new source reproduction,
performance benchmark, holdout, or measured cleaning accuracy improvement.
The formerly recorded original source CSV cache is unavailable.

The local scientific assessment is that this is now a coherent, limited
theory/algorithm preprint for author review. No independent endorsement,
arXiv acceptance or worldwide first claim is established. The owner's earlier
request for explanation remains relevant; content approval and license choice
have not been inferred from continuation authority.
