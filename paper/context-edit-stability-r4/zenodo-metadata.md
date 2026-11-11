# Zenodo record fields for R4

Prepared 2026-11-10. The author creates the record, chooses the license and
presses Publish. Nothing here has been uploaded.

## Files to upload

Both are in `paper/context-edit-stability-r4/zenodo/`:

- `schema-width-editable-keys.pdf`: the 12-page paper (a byte-identical copy
  of `preview.pdf`).
- `schema-width-editable-keys-supplement.zip`: protocols, code, results and
  replay scripts (a byte-identical copy of `supplement.zip`).

Their SHA-256 hashes are in `supplement-verification.json` under
`zenodo_upload`.

## Basic information

| Field | Value |
|---|---|
| DOI | Choose "No" (the work has no DOI yet). Zenodo assigns one. |
| Resource type | Publication → Preprint |
| Title | Schema Width Bounds the Benefit of Editable Keys for Plurality-Based Functional-Dependency Checks |
| Publication date | The day you publish the record. The PDF is dated 2026-11-11. |
| Creators | Family name: Tran. Given names: Vu Bao Minh (written without diacritics, as in the PDF). Affiliation: Independent Researcher. ORCID: optional. |
| Languages | English |
| Version | R4 (optional) |

## Description

```
A plurality-based functional-dependency check accepts a target's dependent value when it is the unique plurality among rows that agree with the target on a determinant. We study the minimum number of context-cell edits that makes every listed check accept a protected, initially rejected target, and ask how much cheaper this becomes when determinant (key) cells may change as well as dependent cells. For a family F of determinants sharing one dependent attribute, let w(F) be the size of a largest inclusion antichain among the determinants that contain a common key. We prove that the fixed-key optimum is at most w(F) times the editable-key optimum, and that every family has a binary table attaining exactly this factor. Hence the two optima agree on every such table if and only if F is laminar. With at least k+1 dependent values the factor is also attained at editable-key optimum k, whereas for a binary dependent attribute and two overlapping determinants the optima differ by at most one edit. The upper bound uses a margin-capped exchange that replaces each key edit by at most one dependent-cell flip per inclusion chain. The classification concerns the listed checks, not logical FD equivalence, and laminarity does not make optimization easy: acceptance within a budget remains NP-complete for singleton determinants. For the reverse direction we give an exact formula. Exhaustive finite checks of the main theorems cover 81,893 rejected table/family pairs. On Beers, Flights and Rayyan, all nine check families of our own earlier benchmark experiment are laminar, which explains, post hoc, why the accepting gain it predicted from editable keys could not occur.
```

## Keywords

functional dependencies; data cleaning; plurality voting; minimum edit
distance; robustness; laminar families; Dilworth's theorem; NP-completeness

## Related works

| Relation | Identifier | Scheme | Resource type |
|---|---|---|---|
| Is supplemented by | https://github.com/minggu151623/invariant-audit | URL | Software |

## License (the author's choice)

Zenodo asks for a license on a public record and suggests CC BY 4.0.

- **CC BY 4.0.** Anyone may reuse and adapt the work with attribution. It is
  the usual choice for preprints and is accepted by arXiv and most journals.
- **CC BY-NC-ND 4.0** or another restrictive license. Less reuse; some
  open-access venues do not accept it.

The supplement contains code. The repository is under the MIT license, and a
Zenodo record may list a second license for the code (MIT).

A Creative Commons license cannot be withdrawn from copies already
distributed.

## Before pressing Publish

1. Read the PDF. You are the sole author and answer for every claim.
2. Check that the commits cited in Section 9 are on GitHub (`6c8827a`,
   `d98e454`, `27ca9b2` are the new ones).
3. Use Preview. After Publish the files cannot be replaced or deleted; a
   correction needs a new version, which gets its own DOI.
