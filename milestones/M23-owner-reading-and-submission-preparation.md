# M23 — owner reading and concrete submission preparation

Date: 2026-10-23. Status: `local_submission_fields_prepared_owner_review_pending`.
Previous goal turn classification: progress (M21 named paper and M22 portable
evidence). This turn also makes progress; it is not a verified wait or a
no-progress turn. The requested end state remains an actual arXiv posting.

## Work completed

Prepared a Vietnamese walkthrough of the manuscript, including the meaning of
195 metric comparisons, exact finite Brier decomposition, degenerate cluster
bootstrap, outside-reference labels, all three datasets' attribution tradeoffs,
mixed H6b and limited novelty. All 12 displayed FPR/FNR percentages were checked
against the frozen E006 CSV. The guide explicitly states that these baseline
policies are poor at locating erroneous cells in Beers/Rayyan.

Prepared local submission fields and an exact ASCII abstract (1419 characters),
with title/name/affiliation preserved and category/license still unconfirmed.
The Romanized name is only a fallback candidate, not an owner-approved name
change. Linked local files exist, the current PDF/source hashes match M21's
render record, and all members of the existing M22 bundle still match the
current included files. No scientific result, PDF or source ZIP was modified.

Checked current primary arXiv guidance for metadata, licenses, endorsement,
moderation, categories and TeX. XeLaTeX is supported; all four Latin Modern
OpenType filenames used in the source occur in arXiv's TeX Live 2025 font list.
The source already follows filename-based font loading. Instructions now
specify `xelatex`, `main.tex` and the four-file source ZIP, and distinguish
local Tectonic verification from the still-unperformed arXiv server build.
No hand-written 00README was added: current official guidance does not recommend
manually creating one for this ordinary submission.

## Completion audit and remaining dependency

Computational and rendering preparation do not prove the full goal achieved.
Current [readiness record](../paper/submission-readiness.json) binds the audit
to the actual manuscript/PDF/ZIP hashes and records each remaining requirement.

The concrete author-review request has been sent through the async user-input
tool: whether the owner has read/understood and accepts the named 12-page draft,
or needs explanation/revisions. There is no answer yet. Providing author name
and affiliation was not treated as manuscript approval. The new walkthrough
supports that review rather than presuming it.

Account registration, any required endorsement, owner-selected category/license,
live metadata verification, arXiv PDF verification, removal of working-draft
markers after approval, submission and public posting remain undone. Independent
scientific assessment and archival interest also remain unresolved; independent
peer review is not misrepresented as a universal arXiv submission prerequisite.

No external message, account, login, upload or submission was made. No process
is running whose completion would remove the owner-review dependency. Do not
invent progress by adding repeated status documents or running arbitrary new
experiments while awaiting human input. Investigate any concrete newly found
scientific/technical issue; otherwise apply the goal's consecutive-turn blocked
audit accurately. At this progress milestone the no-progress streak is zero.

## Artifacts

- [Reading walkthrough](../paper/reading-guide-vi.md).
- [Submission instructions](../paper/submission-guide-vi.md), with official links.
- [Fields draft](../paper/submission-fields-draft.json) and
  [exact abstract](../paper/abstract.txt).
- [Preparation script](../paper/prepare_submission.py) and
  [completion/readiness audit](../paper/submission-readiness.json).
