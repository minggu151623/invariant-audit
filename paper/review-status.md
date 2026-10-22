# Manuscript review status

Updated 2026-10-23 after E006/M20 and the named manuscript expansion. Scope: computational and manuscript self-review.
No independent acceptance, submission or arXiv moderation outcome is claimed.

## Completed evidence checks

- E005/M18 at 8692937: 195 overall metric comparisons reproduce; finite exact
  score-group decomposition and original cluster-signature counts are checked.
- E006/M20 at 5adbb14: one predeclared external-reference run, four fixed rule
  policies across Beers/Flights/Rayyan. Twenty-two synthetic tests pass. The
  193424 predictions, 144 point rows, 840000 bootstrap rows and 84 intervals
  have double-build byte agreement. A post-run serialized audit verifies 720
  point comparisons, all quantiles and nine source pins within 2e-12.
- H6b remains mixed because Flights' lookup-minus-binary Brier interval crosses
  zero. H6c's lower false rejection is shown together with false acceptance
  increases. Rayyan's BA difference interval crosses zero and is not hidden.
- Rall is described as a conservative suspect set, not a promise of precise
  error localization. Correctness of FD conflict detection is a different task
  from agreement with cell corrections. Shared empty reference values illustrate
  a distinction between reference-correct and application-valid.
- Lookup uses raw-score granularity; binary collapses nonzero scores. Their
  score difference can change both reliability and resolution, and is not a
  calibration-only causal effect. No claim of causal M1 transfer is made.
- Two perfect synthetic constructions and the external policies are distinct
  methods/tasks. E003-v1 stays invalid; E004 stays diagnostic; E003-v2 stays
  unexecuted at its original gate. Source A1's header failure and A2 correction
  are preserved rather than retroactively marked valid.
- Nine references now include close work: Raha already notes attribution
  ambiguity, Jung 2025 already studies error-model effects. Neither broad idea,
  the Brier decomposition nor simple constraint checking is claimed as new.
- Mathematical explanations are conditional and distinguish finite empirical
  REL from population calibration. Signature counts are not effective sample
  sizes. External intervals describe fixed datasets/components.
- Significant generative-AI use is disclosed. There is no assertion that a human
  has already independently verified or approved the contents.

## Remaining substantive issues

1. Archival interest: external-reference evidence improves the case beyond two
   internally designed benchmarks, but the general ideas and simple policies
   are established. Whether the integrated quantitative case is substantial
   enough remains a review question, not something a PDF build proves.
2. Reference semantics: outside corrected tables are not independently adjudicated
   world truth. Normalization and retained reference blanks affect labels; the
   transductive dirty-defined components may not represent true entities.
3. Common authorship: rational arithmetic and separate implementations detect
   numerical mistakes but are not independent scientific review. The owner must
   understand and review the exact bounded claims before taking authorship.
4. Reproduction: original runs are preserved at exact implementation commits and
   source pins. A portable standard-library evidence verifier and review bundle
   now reconstruct E005 and audit E006 serialized metrics/intervals without Git
   or the original cache. Optional --source-root checks all nine external pins.
   This is an evidence audit, not full performance-harness reexecution; original
   full-run paths remain machine-specific. See ../reproducibility/README.md.
5. Sources: Murphy metadata/three-part abstract were verified from the publisher
   index; direct full text returned 403. The manuscript gives its own binary
   identity proof. The related-work search is focused rather than systematic.

## Owner and submission status

The user tentatively expects sole authorship and stated they have no arXiv
account. On 2026-10-23 they supplied the exact name Trần Vũ Bảo Minh and
affiliation Independent Researcher; both appear in the manuscript. Category
and license remain unconfirmed. Endorsement requirements have not been checked against an account.
The owner has not reviewed the updated E006 manuscript. Do not invent these
facts, create an identity from Git metadata, contact endorsers, or mark this
working draft as submitted/accepted.

## Rendering

`render-verification.json` records the current preview and minimal-source checks.
The preview/source ZIP are derived review artifacts; the Markdown and frozen
study artifacts remain authoritative. The first native compile previously
 timed out downloading resources; an isolated hash-checked official Tectonic
0.17.0 binary is the local fallback. No global TeX installation was made.
