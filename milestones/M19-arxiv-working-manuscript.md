# M19 — Rendered arXiv-directed working manuscript

Date: 2026-10-22. Status: `verified_rendered_draft_pending_scientific_review`.
Scope: manuscript/artifact verification, not independent acceptance or submission.

The user selected arXiv as the destination. In reply to the metadata question,
the user said they have no account/materials yet and tentatively expect to be
the sole author. No actual name or affiliation has been supplied or invented.
See `paper/submission-metadata.json`; category/license are unconfirmed.

## Manuscript and evidence

- [Authoritative Markdown](../paper/main.md) now frames a bounded methods case
  study, retaining synthetic limitations and the failed external attempt.
- E005/M18 at 8692937 supports the new decomposition and statistic-diversity
  findings. Original E001/E002 point metrics and intervals remain bounded.
- Seven primary/institutional source notes and a focused comparison were added.
  Murphy full text was unavailable; metadata/abstract were verified and the
  manuscript proves its binary finite-group identity explicitly.
- Conditional statements do not claim causal identification of construction
  effects or a new theorem/method. Substantial generative-AI use is disclosed.
- [Self-review](../paper/review-status.md) identifies archival-interest, narrow
  design and absent independent-label evidence as open substantive issues.

## Rendering and source verification

- [PDF preview](../paper/arxiv-preview.pdf): 8 pages, all rendered and visually
  inspected after correcting long command wrapping and split tables.
- [Minimal source ZIP](../paper/arxiv-source-draft.zip): exactly main.tex,
  body.tex and images/brier-decomposition.pdf; CRC and member bytes pass.
- ZIP independently extracted into a temporary directory and compiled with
  Tectonic 0.17.0. All 8 pages have the same extracted text as the preview;
  zero overfull/underfull or missing-character warnings.
- Native editor's first compile timed out downloading TeX resources. The local
  fallback engine was isolated and hash-checked against its official release;
  no global TeX installation. E005 execution was separate and standard-library only.
- Full content hashes and page inspection record: `paper/render-verification.json`.

## Remaining work

This is a concrete review draft, not a submission-ready or accepted paper.
The contribution may be too narrow; deepen/broaden the scientific evidence or
obtain a substantive assessment before treating the paper as ready. In
particular, a controlled E003 mutation result alone would not establish
independent external truth. E003-v2 remains unexecuted and its gate unchanged.

Required owner inputs eventually include exact author name, affiliation if any,
responsible author review, category/license decisions and account/endorsement
setup. Do not fabricate these or represent endorsement as a guaranteed service.
The long-running arXiv research goal remains active. No public push, upload,
account creation, external message or scheduled automation occurred.
`public_claim_eligibility=false`.
