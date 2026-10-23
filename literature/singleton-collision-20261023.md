# Singleton characterization: primary-source collision check

Checked 2026-10-23 after E009's predictions and execution. This is a targeted
screen, not an exhaustive originality determination. Exact-phrase searches also
returned irrelevant material; their lack of a match is not novelty evidence.

## Voting operations

Lirong Xia, *How Many Vote Operations Are Needed to Manipulate a Voting System?*
(2012), [version 3](https://arxiv.org/html/1204.1231v3).
Read the abstract, definitions 3 and 6, and the ILP/application discussion.
The paper formalizes minimum operations for constructive/destructive goals,
includes plurality, and relates winner changes to margin of victory. It uses
integer optimization and studies asymptotic categories of required operations.
Consequently, defining a decision-flip cost, separating constructive/destructive
directions, and using integer optimization cannot be our novelty claims.

E009's nonsingleton margin calculation uses standard vote-count reasoning.
The narrower candidate is proving precisely when editable determinant cells
can improve that cost: only through singleton target groups, with an exact
import-cost condition. This source does not by itself establish that candidate's
originality. General election-control and multimode-intervention literature
could still subsume it; do not claim a first theorem based on this screen.

## Repairs and immutable cells

George Beskales, Ihab F. Ilyas and Lukasz Golab, *Sampling the Repairs of
Functional Dependency Violations under Hard Constraints* (PVLDB 2010),
[conference-hosted primary PDF](https://www.comp.nus.edu.sg/~vldb2010/proceedings/files/papers/R17.pdf).
Inspected definitions 1--5, algorithm 2 and sections 4.2--5.
They study value-update repairs that satisfy the complete FD set, including
minimum-change notions and trusted immutable cells. Their sampler uses cell
equivalence classes, and an optimization skips singleton blocks that are already
clean. Neither immutable cells nor using singleton structure is new in general.

Our singleton target group is a different object: rows matching a fixed target
on one determinant before any edit. E009 asks for the exact cost to reverse a
plurality detector decision, even though the resulting table may still violate
FDs. The paper's singleton blocks concern repair decomposition under global
FD satisfaction. This distinction avoids conflating the two results; it is not
a proof that our target-group characterization is original.

## Earlier close work remains relevant

The [mutable-key collision note](mutable-key-novelty-20261023.md) already records
view-conditioned causality and attribute-level interventions. Those generic
frameworks are more general than our model; specializing them is not enough
unless the structural theorem or resulting algorithm adds something substantive.
The [earlier screen](novelty-reset-20261023.md) records overlapping error-detection
and certified-voting work. No source has been discarded because it weakens the
story. The manuscript remains the preserved audit baseline until this new
direction has a defensible contribution and useful evaluation.

Next compare algorithms under a locked scaling design, then inspect general
election control and threshold-query sensitivity at theorem level. Report any
subsumption, including a negative novelty outcome.
