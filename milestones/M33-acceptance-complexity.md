# M33: binary accepting complexity and R3

Date: 2026-11-05. Continued existing local research authority after M32. No
subagents, paid calls, external messages, publication approval or submission.
The active goal remains achieving an arXiv preprint, not just a compiled file.

## Research result

The previously unverified Set Cover lead now has a full internal proof:
accepting a rejected protected target within a cell-edit budget is NP-complete
in combined complexity, even with binary columns, singleton determinants and
every initial group tied. The polynomial construction preserves the cover
optimum for both fixed-key and unrestricted-key models. The crucial converse
extracts a cover from every accepting Hamming edit, charging changed keys to
sets covering their columns and unchanged groups to incident set-row RHS flips.

This supplies a directional complexity distinction from the polynomial
rejection formula. It does not attribute hardness to mutable keys, imply a
practical slowdown or establish fixed-schema hardness. A standard margin-vector
DP observation covers fixed key count and fixed RHS alphabet (no implementation
or FPT claim). The paper credits existing lobbying reductions using incidence
matrices and balancing rows. Historical priority remains unverified.

## Internal proof audit

| Potential defect | Resolution in the proof |
|---|---|
| Support rows might enter unintended initial groups | Each has only its own element's key zero; all others are one. |
| Duplicate tuples might collapse | The model uses identified rows; duplicates are retained. |
| Arbitrary key edits could evade a fixed-key lower bound | Each changed key selects a set containing its column element; columns without edits retain exact membership. |
| Mixed key/RHS edits might be double-counted | The extraction charges separate selections to distinct changed cells; duplicate sets are then discarded. |
| Support RHS flips might help an unchanged group | Original-zero to one reduces its margin; positive final margin still requires an original set-row one-to-zero flip. |
| Construction could be superpolynomial | At most l + q*l context rows, each q+1 bits. |
| Certificate could be too large for NP | The complete binary destination has input-table dimensions and is checked directly. |
| Hardness could be misstated as fixed-schema | Theorem and abstract explicitly allow growing schema; fixed q,d DP noted. |

This is same-agent internal review. No human review or formal proof assistant
validation is represented by this table.

## Evidence and provenance

E012 protocol was committed as `9f14171`, implementation as `65ad518`, before
execution. The pre-run conjecture, full grid and extraction checks were frozen.
All 111 instances and 222 optimum comparisons pass. Raw enumeration evaluates
147523 destinations across two overlapping edit models; all 25490 accepting
destinations permit a valid budget-respecting cover extraction. Of the full-edit
successes, 24288 use key edits. All outcomes and witnesses are retained.

The construction and proof are analytical; finite agreement is a limited check.
There is no new source-data experiment, timing comparison, independent
replication, or favorable replacement of E011's negative result.

Primary sources inspected: Karp's original Main Theorem and Set Covering entry
(1972 p.94, in an author-introduced reprint); Bredereck et al. AAAI 2012
introduction and Sections 2-3, Reductions 1-2, via publisher and author-hosted
PDF. The publisher's 2021 migration date is not the conference year.

## Delivered revision

- R3 source: `paper/context-edit-stability-r3/tex/main.tex`.
- PDF: `paper/context-edit-stability-r3/preview.pdf`, 10 pages, 3 tables,
  10 references, 12 embedded fonts, exact Unicode author name.
- New theorem is Theorem 3 in Section 6; previous five structural blocks and
  E008--E011 empirical section text remain byte-identical to R2.
- Tectonic cached build and extracted one-file source ZIP build pass without
  warnings; extracted page texts match. All ten pages visually inspected.
- 197 prior scientific artifacts match the pre-revision hash inventory.
- Supplement has 12 members; manifest hashes and ZIP CRC pass. Its extracted
  read-only replay reproduces every frozen E012 case with no Git or third-party
  imports. This is packaging verification, not additional scientific evidence.
- Supplement SHA-256:
  `c30fd26b92fbb0f616a0bbb004e7e978a4e998219d5970a8e828c86875ed24bd`.
- Vietnamese explanation: `to_human/M33-theory-progress-vi.md`.

## Assessment and next action

Internal assessment has improved from M32: the draft now forms a coherent
limited theory/algorithm preprint suitable for substantive author review. The
new theorem is a substantive extension, not a new name for the same empirical
outcomes. Do not describe it as a major breakthrough, worldwide first result,
or an accuracy-improving cleaning method. Independent peer review is not being
imposed as a gate to preparing an arXiv submission.

Next, let the owner read the Vietnamese explanation and the revised theorem,
resolve substantive questions, then obtain their explicit content approval and
license choice before external submission. The owner is still recorded as
having no arXiv account. No new question was treated as answered, and “continue”
was not treated as approval to publish. The goal is active, incomplete; this
turn made substantive progress and the repeated-blocker threshold is not met.
