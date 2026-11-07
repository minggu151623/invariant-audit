# arXiv submission fields for R4

Prepared 2026-11-07. Copy these fields into the arXiv form. The author
submits; nothing here has been submitted.

## Files

Upload `source.zip`. It contains only `main.tex`, and arXiv compiles it with
pdfLaTeX. This was checked locally with TeX Live 2026: 11 pages, no warnings.
Do not upload `preview.pdf` instead; arXiv prefers TeX source.

## Title

Schema Width Bounds the Benefit of Editable Keys for Plurality-Based Functional-Dependency Checks

## Authors

Trần Vũ Bảo Minh

Affiliation in the paper: Independent Researcher.

## Abstract

```
A plurality-based functional-dependency check accepts a target's dependent value when it is the unique plurality among rows that agree with the target on a determinant. We study the minimum number of context-cell edits that makes every listed check accept a protected, initially rejected target, and ask how much cheaper this becomes when determinant (key) cells may change as well as dependent cells. For a family F of determinants sharing one dependent attribute, let w(F) be the size of a largest inclusion antichain among the determinants that contain a common key. We prove that the fixed-key optimum is at most w(F) times the editable-key optimum, and that every family has a binary table attaining exactly this factor. Hence the two optima agree on every such table if and only if F is laminar. The upper bound uses a margin-capped exchange that replaces each key edit by at most one dependent-cell flip per inclusion chain. The classification concerns the listed checks, not logical FD equivalence, and laminarity does not make optimization easy: acceptance within a budget remains NP-complete for singleton determinants. For the reverse direction we give an exact formula. Exhaustive finite checks cover 81,893 rejected table/family pairs. On Beers, Flights and Rayyan, all nine check families of an earlier study are laminar, which explains, post hoc, why a predicted accepting gain from editable keys could not occur.
```

The abstract is about 1,430 characters; arXiv's limit is 1,920.

## Comments

```
11 pages, 3 tables. Code, frozen protocols and a replay script: https://github.com/minggu151623/invariant-audit
```

## Categories

- **Primary:** cs.DB (Databases)
- **Cross-list (optional):** cs.DS (Data Structures and Algorithms)

## License (the author's choice)

- **arXiv non-exclusive license.** The most restrictive option. It leaves the
  most room if a journal later wants exclusive rights.
- **CC BY 4.0.** Anyone may reuse the work with attribution. Many open-access
  venues accept it.

The license cannot be made more restrictive after submission.

## Before pressing Submit

1. Read the paper, at least Section 3. You are the sole author and answer for
   every claim.
2. arXiv may ask for an endorsement for cs.DB. If it does, ask someone who has
   already posted in cs.DB to endorse you.
3. Check arXiv's compiled PDF preview against `preview.pdf` before confirming.
