# Manuscript review status

Date: 2026-10-22. Scope: author self-review of the arXiv-directed draft.
No independent acceptance or arXiv moderation outcome is claimed.

## Scientific review

- Numerical support: E005 independently reimplements metric arithmetic and
  reproduces all 195 overall comparisons. Source hashes, 39 summary rows,
  12 score groups and exact Brier identities are recorded by M18 at 8692937.
- Interpretation: the abstract and conclusion are a finite case study. They do
  not claim new invariant-checking technology, improved calibration, external
  accuracy, causal duplicate mechanisms, or representative uncertainty.
- Formal statements: the agreement proposition is conditional, not a causal
  test that oracle independence forces perfection. The smoothing statement
  assumes label-pure raw-score groups across both splits, and the ECE result
  additionally excludes cancellation within bins. The resampling statement
  concerns identical sufficient-statistic vectors and a fixed resample size.
- Calibration: REL is empirical exact-score grouping, not a population estimate.
  ECE is positive-class, ten-bin ECE, not maximum-confidence ECE. Serialization
  tolerances and calibration-reconstruction limitations are explicit.
- Statistical scope: signature counts are not effective sample sizes. The old
  bootstrap intervals are quoted as fixed-design results and were not rerun.
- Generative-AI use: a dedicated disclosure names its substantial roles in
  planning, implementation, audit analysis and drafting. It does not claim
  completed human verification or list AI as an author.
- External evidence: E003-v1 is invalid; E004 is a source diagnostic; E003-v2 is
  incomplete and unexecuted. None is described as external performance validation.

## Unresolved substantive objections

1. Archival interest: the mathematical mechanisms are elementary and known.
   Two constructions from one project may be too narrow a contribution. The
   paper now presents a reproducible case study and clearly credits the known
   ideas, but an independent reviewer still needs to judge whether the combined
   empirical account is useful enough. If not, broaden the study before submission.
2. External correctness: no independently labeled natural-error dataset exists
   in this evidence set. Any stronger generalization claim needs new evidence;
   completing a controlled mutation pipeline alone would not resolve this issue.
3. Common author: a fresh metric implementation and synthetic tests do not
   constitute independent scientific review. Neither the analysis nor the
   manuscript is independently accepted.
4. Source verification: Murphy metadata and the three-component abstract were
   verified through the publisher index; direct full text returned 403. The
   manuscript proves its finite binary identity explicitly and does not quote an
   unchecked equation from that source. Remaining references have primary or
   institutional records; the related-work search was focused, not exhaustive.

## Owner inputs and submission gate

Actual author names/order, affiliations, responsible submitter, category and
license remain unconfirmed. Account/endorsement status is unknown. The preview
and source bundle are review drafts. The owner must review a concrete final
manuscript before a separate external submission action. No upload, push or
external messaging has occurred in this continuation.

## Rendering verification

Recorded in `render-verification.json` after compilation and page inspection.
Native editor compilation initially timed out downloading TeX resources; an
isolated official Tectonic 0.17.0 binary is used as a local rendering fallback.
The downloaded archive SHA-256 was checked against the official release asset:
`a3f1cac7c5678f01661a92212f58480ae3b0634115d880dbc59e2953ded45667`.
No global TeX installation was made. This rendering runtime is separate from
E005, which used only Python's standard library and did not access the network.
