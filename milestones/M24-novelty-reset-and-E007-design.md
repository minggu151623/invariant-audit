# M24 — novelty reset and E007 feasibility design

Date: 2026-10-23. Status: primary-source novelty screen and protocol design.

The owner explicitly requires a new research contribution and correctly notes
that arXiv does not require peer review. Earlier submission-preparation focus
and waiting for owner review do not prevent further authorized local research.
Independent peer review is not added as an arXiv prerequisite. Eventual owner
approval and license selection remain actual release decisions.

A targeted primary-source search found a close October 2026 AFD study that
already compares whole-group and non-majority detection. Conformal cleaning,
query-aware uncertainty, FD repair certification and overlapping-vote robustness
also have direct prior work. The old audit manuscript is preserved, not promoted
as original. See the [collision matrix](../literature/novelty-reset-20261023.md).

The AI-proposed candidate asks for the minimum context-cell edit budget that
flips one cell decision under several overlapping FD plurality rules. An initial
binary optimization formulation and its threat model are now explicit. The
candidate may still collapse to existing voting certification; no novelty claim
is established. E007 first tests its mathematical correctness on an exhaustive
finite domain, not real data or a performance benchmark.

[Protocol](../experiments/E007-fd-decision-stability/protocol.md): 39334 ordered
constructed tables, 118002 decision-radius comparisons, direct exhaustive oracle,
strict local-vs-joint gap check and a determinant-edit scope counterexample.
Lock precedes implementation and execution. Existing protocols/data/results,
M21 PDF/source and M22 evidence bundle are preserved. No external actions.
