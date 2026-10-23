# M27 — accepted-target characterization and independent baseline

Date: 2026-10-23. Status: valid finite mathematical validation, proof recorded.
This goal turn makes research progress; the arXiv objective remains incomplete.

E009 was locked at 96962bee9eb2ca7680ec8a5a069baa78e65d686d, implemented at
05a2b071636b0d17f3e8441f81566c5a00a4bb5b, and run once under
e009-20261023-001. Nine unit tests pass. The complete two builds match byte for
byte, including MILP witnesses and numerical residuals.

- The formula matches unrestricted raw-edit search on 18779 accepted targets;
  all 18755 finite witnesses pass, with 24 impossible one-row cases.
- All 6509 cases without singleton target groups retain the fixed-key radius.
- Among 12270 singleton-containing cases: 180 finite reductions, 7290
  fixed-key INF to finite transitions, and 4800 cases with no reduction.
- A separate raw-cell MILP matches the oracle on 2118 cases: 2100 optimal
  witnesses, 18 infeasible cases, and no status/time-limit failures.
- Maximum linear-constraint residual is 8.881784197001252e-16; maximum
  integrality error is 6.661338147750939e-16, below the locked 1e-7 tolerance.

The [proof](../experiments/E009-singleton-characterization/theory.md) establishes
the formula and the exact condition S<A for key edits to reduce the accepted
target's radius. It applies to the protected-target, same-RHS, independent
unit-cell-cost model only. Rejected-to-accepted edits still require joint
optimization. The proof is same-agent derivation, not independent assessment.

The frozen formula prototype eagerly constructs witnesses and is not yet a
linear-scan implementation. No runtime comparison or detector-accuracy claim
has been made. See the [result](../experiments/E009-singleton-characterization/results/run-e009-20261023-001.md)
and [primary-source collision check](../literature/singleton-collision-20261023.md).
Voting margins, minimum interventions and trusted cells already exist in prior
work. Originality of the specialized structural results remains open.

Next: separately lock and execute a bounded comparison against the verified
generic MILP, treating both decision directions separately and retaining
timeouts and unfavorable outcomes. Manuscript, PDF, archived evidence and prior
studies remain unchanged. No account, upload, external message or public push.
