# Novelty reset after the owner's scientific feedback

Date: 2026-10-23. User-selected requirement: pursue an original contribution;
do not make independent peer review a prerequisite for continuing research or
ordinary arXiv preparation. Moderation is distinct from peer review:
[official policy](https://info.arxiv.org/help/moderation/index.html).

The current 12-page manuscript is a bounded audit draft, not an established
novel contribution. Its computations stay preserved. The next research direction
below is AI-proposed and is not an owner-approved scientific claim.

## Primary-source collision check

| Source inspected | Existing contribution relevant here | Consequence for this project |
| --- | --- | --- |
| [Wan and Han, 2026, arXiv:2610.08189v1](https://arxiv.org/html/2610.08189v1), sections 3.3 and 7.4 | AFD strength versus detection utility; Whole-Group versus Non-Majority attribution is explicitly compared. | Do not claim the generic attribution tradeoff or dependence-strength/utility distinction as new. This is closer than the original nine-reference draft acknowledged. |
| [Han et al., 2026, Auto-Relate](https://arxiv.org/html/2606.07060v1), sections 3.4 and 4 | Random perturbation tests for relationship reliability and computational shortcuts. | A generic proposal to perturb tables or test rule stability is already occupied. Distinguish relationship discovery from a fixed cell decision's minimum edit distance. |
| [Jäger and Biessmann, AISTATS 2024](https://proceedings.mlr.press/v238/jager24a.html) | Conformal Data Cleaning combines imputation and calibrated uncertainty. | Merely adding conformal calibration or rejection to cleaning is insufficient novelty. |
| [Schreiber and Amsterdamer, ICDE 2026 extended version](https://arxiv.org/abs/2603.08612v2) | MES quantifies query-output uncertainty and guides verification. | Do not claim the first uncertainty-aware verification allocation framework. Our candidate has no probabilistic query model. |
| [Fan and Koutris, ICDT 2022](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ICDT.2022.6) | k-NN predictions certified across database repairs under FDs. | Certifiable decisions and FD-constrained repairs are established. The object here would be a detector's own context-dependent decision under a stated edit budget. |
| [Hammoudeh and Lowd, certified regression/classification](https://arxiv.org/abs/2208.13904) | Voting robustness, overlapping training subsets and partial-cover formulations. | A majority margin, overlapping-set optimization or set-cover reduction alone cannot be sold as new. This remains the most important unresolved collision for the candidate. |

This was a targeted search, not a systematic or exhaustive review. Search hits
from aggregators were used for discovery only; the sources above are primary.
HTML snapshots and their identities are indexed in
`novelty-sources-20261023.json`; originals reside outside the repository cache.
For some sources only primary abstract/metadata and targeted passages were
inspected; do not describe this as a complete full-paper review of all six.

## Candidate chosen for a bounded mathematical feasibility check

Question: for a cell rejected by several overlapping FD plurality rules, what
is the **smallest number of edits to other RHS cells** that changes its final
decision, when determinant columns and the target row are protected?

The candidate object is a joint decision-edit radius with an explicit witness,
not estimated correctness probability. Several rules can depend on the same
editable cell. Counting their repair budgets separately loses that coupling.
The initial proposed formulation is a binary covering program over those cells;
E007 checks it against exhaustive counterfactual enumeration.

Potential eventual contribution would need a substantively distinct algorithm,
structural result or practical consequence beyond existing voting certification
and generic optimization. It is **not established yet**. A correct finite pilot
only establishes feasibility of the formulation. It cannot establish novelty,
external usefulness, improved accuracy or an arXiv acceptance prediction.

## Kill criteria before promoting the candidate into the paper

1. Reject any formulation contradicted by exhaustive E007 cases; preserve the
   counterexample, revise under a new version if justified.
2. If the full voting/repair literature already supplies this exact problem and
   result through a routine substitution, withdraw the algorithmic novelty claim.
3. If determinant protection cannot be justified for the intended application,
   either extend the threat model or state the limited certificate explicitly.
4. If an efficient, useful method or nontrivial structural result does not emerge,
   do not turn a trivial margin formula plus synthetic tests into a claimed new
   research contribution. Return to the other questions in the literature.

Original E001--E006 outputs and E003-v2's locked historical gate remain unchanged.
Owner content approval remains needed for eventual release, not for this local
research. No external peer-review acceptance is required to run E007.
