# Paper

Current working manuscript (2026-10-23): **Auditing Invariant Validation
Benchmarks: Construction, Error Attribution, and Probability Scores**.
The user selected arXiv as the destination; the framing is AI-proposed.

`main.md` is authoritative prose. `arxiv/` contains derived LaTeX and two
figures. The preview has 12 pages. The minimal draft source ZIP contains four
files: main.tex, body.tex and both referenced figure PDFs. These are owner-review
artifacts, not evidence of submission or acceptance.

Scientific evidence: E005/M18 at 8692937 audits the two original synthetic
designs; E006/M20 at 5adbb14 adds three fixed outside-reference datasets, a
cell-attribution tradeoff and a preserved mixed probability-score prediction.
The external policies are not the original M1, and no causal transfer or new
algorithm claim is made. E003-v1 stays invalid; E003-v2 remains unexecuted.

See `review-status.md`, `owner-review-vi.md`, `paper_outline.md` and
`render-verification.json` for scope, remaining gates and artifact checks.
Author name Trần Vũ Bảo Minh and affiliation Independent Researcher were
supplied by the user. Responsible owner review, independent scientific
assessment and public release of the new analysis remain pending.

Build both figures using a Python environment with Matplotlib:

```sh
python paper/plot_e005.py
python paper/plot_e006.py
python3 paper/build_manuscript.py --engine /path/to/tectonic
python3 paper/package_source.py
```

Pandoc is required for Markdown conversion. E005 itself is standard-library
only; E006 uses the frozen Python 3.13.5/NumPy 2.1.3 environment. Neither study
depends on the document-rendering tools. Original run paths are local; a portable
reproduction verifier/evidence bundle remains next release work.
