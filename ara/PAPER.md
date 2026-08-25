# InvariantAudit

- **Title**: InvariantAudit
- **Author**: TRAN VU BAO MINH
- **Author source**: existing public repository attribution in `LICENSE` only
- **Venue**: undecided
- **Research status**: preliminary; one valid finite-synthetic E001 result is
  recorded, while E002 has only one invalid diagnostic attempt
- **Research question**: How can semantic and state invariants be validated while calibrating false positives and false negatives?
- **Experiments**: [E001-v1](../experiments/E001-synthetic-invariant-calibration/protocol.md)
  valid within its locked finite synthetic design; [E002-v1](../experiments/E002-heterogeneous-specification-stress/protocol.md)
  has one invalid attempt only
- **Results/data**: E001 published artifacts are bound to C01; E002 has only
  a preserved invalid report and no scientific data/result
- **Calibrated metrics**: E001 primary M1-minus-B0 deltas are BA `+0.5`, FPR
  `-1`, and FNR `0`
- **Supported claims**: C01 supported strictly within finite synthetic E001-v1
- **Untested claims**: C02 is the AI-suggested locked E002 H2 hypothesis; proof
  is pending
- **Public-claim eligibility**: false
- **Provenance note**: User authority records process decisions and continued
  research only. Technical designs, implementation choices, and reviewer
  checks are AI-suggested or AI-executed; repository artifacts are kept
  separate from worker claims and independent-review evidence.

## ARA layer index

- [Problem](logic/problem.md)
- [Claims](logic/claims.md)
- [Heuristics](logic/solution/heuristics.md)
- [Evidence index](evidence/README.md)
- [Exploration tree](trace/exploration_tree.yaml)
- [Session index](trace/sessions/session_index.yaml)

The E002 remediation is reviewed, but a corrected run requires a new run ID
and separate explicit authorization. No E002 public claim or push is
authorized; venue remains undecided.
