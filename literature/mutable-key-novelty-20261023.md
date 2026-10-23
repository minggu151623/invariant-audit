# Mutable-key certificates: prior-work boundary and falsifiable candidate

Date: 2026-10-23. This is a targeted primary-source review and a proposed research
direction, not an established novelty result or systematic literature search.

## Further collisions beyond E007

[Meliou, Gatterbauer, Nath and Suciu, SIGMOD 2011](https://gatterbauer.name/download/sigmod2011_View-Conditioned_Causality.pdf)
define view-conditioned counterfactual causes, use sets of changed input values,
and reduce reasoning to SAT/weighted MaxSAT. Their formal transformations include
Boolean combinations of threshold predicates. Generic minimum input changes and
SAT-based error explanations are therefore already occupied concepts. Read
sections 2--4, especially definitions of VCC/VC causes and the input-variable model.

[Bertossi, final 2020 version](https://arxiv.org/abs/1712.01001v7)
includes attribute-level causes via repair semantics and integrity constraints.
Do not present cell interventions under constraints as a first contribution.
The primary abstract/version metadata were inspected; a complete theorem-by-
theorem comparison remains pending.

The earlier [voting/repair collision matrix](novelty-reset-20261023.md) remains
applicable. Searching for no exact phrase is not evidence that a problem is new.

## Narrow candidate still worth falsifying

For a fixed target cell and several same-RHS plurality FD rules, determinant
edits can enter/leave overlapping groups. A single shared key edit can affect
several rules. The candidate is a cost-preserving reduction from raw categorical
cell edits to target-relative match masks and a small set of monotone context-row
actions, followed by exact margin dynamic programs in both decision directions.

The proposed technical distinction is **specialized action reduction with actual
cell costs when group membership changes**, rather than merely defining minimum
edits or invoking a generic solver. Its scope is same-RHS target-cell decisions,
not multi-output view conditioning, arbitrary FDs or discovering correct labels.
Whether that reduction yields an original theorem or a useful efficient method
still requires comparison and evidence. It is not yet claimed as a contribution.

E008 locks an exhaustive finite falsification gate, including a three-valued key
domain to expose errors hidden by equating raw edits with match-mask changes.
The raw-domain reference is independent of the proposed reduction. After it,
derive a full proof and compare against a generic existing SAT/MaxSAT formulation,
then assess scaling and usefulness on a separately declared design. Do not equate
another large count of toy comparisons with sufficient research novelty.
