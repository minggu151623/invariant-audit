# M37: larger optima (E014) and preparation for Zenodo

2026-11-10. Owner instruction: "tôi đã quyết định đăng lên zenodo trước, nhưng
tôi vẫn cần bạn rà soát bài báo xem còn gì cần phải làm và cần thiết thì viết
lại bài báo". The upload, the account and the license choice remain the
owner's own actions.

## Review findings and changes to R4

- **The first open question could be answered.** R4 asked whether the factor
  w(F) is attained when the editable-key optimum is k > 1. New Proposition 1:
  - (a) with d >= k+1 dependent values, every family has a binary-key table
    with rho_full = k and rho_fixed = w(F) k;
  - (b) with d = 2 and F = {{a,b},{a,c}}, rho_fixed <= rho_full + 1, so the
    factor 2 occurs only at rho_full = 1.
  The case d <= k is open in general and is now the first open question.
- **E014** (`experiments/E014-scale-sharpness/`) checks both parts. Protocol
  `6c8827a` was committed before the implementation `d98e454`; the single run
  is recorded at `27ca9b2`. All locked predictions passed with no fix commit.
  - Part A: nine constructions and one binary control; 5,594,099 edited tables
    enumerated below the predicted radii, none accepts.
  - Part B: 74,612 tables, 34,393 rejected, 332 strict gaps (309 at (1,2), 23
    at (2,3)); the dynamic program agrees with raw enumeration of 3,377,408
    destination tables on the 968 tables with at most three rows.
- The abstract and Section 6 called E011 "an earlier study", which reads like
  someone else's work. They now say it was our own benchmark experiment.
- "RHS" was used without a definition; Section 2 defines it.
- Section 9 named a supplement without saying where it is; it now gives the
  path in the repository.
- The PDF had no title or author metadata; `hypersetup` sets both.
- The date is 2026-11-10. The separation result is now Proposition 2;
  `review/review-20261107.md` is a dated record and still calls it
  Proposition 1.
- The bibliography item spacing was reduced so that the paper is 12 pages
  rather than 13 with one reference on the last page.

## Zenodo package

- `paper/context-edit-stability-r4/zenodo/schema-width-editable-keys.pdf` and
  `schema-width-editable-keys-supplement.zip` are byte-identical copies of
  `preview.pdf` and `supplement.zip`.
- `zenodo-metadata.md` lists the record fields and the license options.
- `to_human/M37-zenodo-vi.md` is the Vietnamese guide.
- The supplement no longer contains the stale Vietnamese progress note. It
  now contains the E014 protocol, code, analysis and summary (19 members with
  the manifest).

## Verification

`check_revision.py` passed on 2026-11-10: 197 M33-baseline artifacts, the R3
hashes and the M35 artifacts unchanged; Tectonic and pdfLaTeX builds with zero
log warnings, 12 pages each, all fonts embedded; the extracted source ZIP
compiles to identical text; supplement hashes match after extraction; both
E013 replay modes and the E014 recomputation pass from the extracted
supplement. All 12 XeTeX pages were rendered; pages 1, 5, 6, 8, 11 and 12 were
inspected at full size in the XeTeX build and on a contact sheet in the
pdfLaTeX build. No layout defect was found.

## Status

Ready to post as a preprint, in the same sense as M36. Remaining weaknesses,
all stated in the paper: no independent human review (Proposition 1 included);
Proposition 1(b) covers one two-rule family; d <= k is open; the literature
search is targeted; no real data with a nonlaminar schema; a narrow model. The
full text of Tao et al. (FAW 2021) was not obtained.

Nothing has been uploaded. The three E014 commits and the paper commit must be
on `origin/main` before the upload, because the PDF cites them.

## Addendum: author name without diacritics (2026-11-11)

The owner asked: "tôi muốn để tên mình ở dạng không dấu". The author line and
the PDF metadata now read "Tran Vu Bao Minh" (same word order as before). The
name is ASCII, so the pdfLaTeX branch no longer loads the T5 encoding
(`vntex`); T1 with `lmodern` remains. The date on the paper is 2026-11-11. No
scientific content changed.

`check_revision.py` passed again on 2026-11-11: 12 pages, zero warnings, all
fonts embedded, 197 preserved artifacts unchanged, the extracted supplement
replays E013 and recomputes E014. A separate pdfLaTeX build has 12 pages and
zero warnings. Page 1 was rendered and inspected in both builds; Miclăuș and
Mureșan still display correctly without T5. New hashes are in
`state/workspace.yaml` (M37). The README, the arXiv and Zenodo field files and
the Vietnamese guide carry the new form of the name. Older records keep the
accented name as written at the time.

The owner also asked whether to rename the GitHub repository. Advice given:
not needed, because the repository holds the whole project and not only this
paper. Renaming is the owner's own action; if done, the URL in Section 9 and
in the field files must be updated and the files rebuilt before the upload.
