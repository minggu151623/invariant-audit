# InvariantAudit

- **Title**: InvariantAudit
- **Author**: TRAN VU BAO MINH
- **Author source**: existing public repository attribution in `LICENSE` only
- **Venue**: undecided
- **Research status**: preliminary; one valid finite-synthetic E001 result and
  one valid finite-synthetic E002 corrected result are recorded, while the
  earlier E002 attempt remains an invalid diagnostic record
- **Research question**: How can semantic and state invariants be validated while calibrating false positives and false negatives?
- **Experiments**: [E001-v1](../experiments/E001-synthetic-invariant-calibration/protocol.md)
  valid within its locked finite synthetic design; [E002-v1](../experiments/E002-heterogeneous-specification-stress/protocol.md)
  has one preserved invalid attempt and one valid corrected run recorded by
  M08, both bounded to the locked finite synthetic design
- **Results/data**: E001 published artifacts are bound to C01; E002 run
  `e002-20260825-002` artifacts and result are bound to C02, while run 001
  remains invalid diagnostic-only evidence
- **Calibrated metrics**: E001 primary M1-minus-B0 deltas are BA `+0.5`, FPR
  `-1`, and FNR `0`
- **Supported claims**: C01 supported strictly within finite synthetic E001-v1;
  C02 supported strictly within finite synthetic E002-v1
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

The E002 remediation and development-test-boundary review are accepted as
process evidence. M07 records the historical readiness gate, and M08 records
the subsequently authorized valid corrected run with C02 support strictly
within finite synthetic E002-v1. Run 001 remains invalid; no E002 public claim
or push/publication is authorized, and venue remains undecided.
