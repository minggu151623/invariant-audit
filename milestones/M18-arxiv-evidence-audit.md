# M18 — arXiv direction and benchmark evidence audit

Date: 2026-10-22. Status: `verified_within_exploratory_reanalysis`.
Verification scope: artifact integrity and numerical reimplementation by the
same agent; independent scientific/manuscript acceptance remains absent.
User chose arXiv as the destination; the case-study framing is AI-proposed.

## Evidence chain

- Protocol: E005-v1, commit `2e6f7c2ec236ebce2bf72f3a026b2ea6de3a80e1`,
  SHA-256 `9bae4acac225afd19a14fefb1dc7ab322a50b6d0b3331547d6e270f8910c5baa`.
- Implementation: `167f721565d68cc80b54340a3533e3b414deedd8`; 21 synthetic
  tests pass, including exact known answers, parsing, leakage-compatibility
  checks, output refusal and late publication rollback.
- Run: `e005-20261022-001`, valid; two complete output builds agree byte for byte.
- [Report](../experiments/E005-benchmark-evidence-audit/results/run-e005-20261022-001.md),
  SHA-256 `bae6a2d3e209d2604d8c7688e8c2d4647e9fac23cb9c23992d694411edefa852`.
- [39-row summary](../data/E005-v1-summary.csv),
  SHA-256 `a5d90edf854a9383bd475e956a00fc5c52f1321de11c01dd3f52c92117e48579`.
- [12 score groups](../data/E005-v1-score-groups.csv),
  SHA-256 `b6856afc0f38fadb1639cd4ef1cd3f9d0a85fb16f135d47303537a79b7c550ac`.
- [Checks](../data/E005-v1-checks.json),
  SHA-256 `01db855a971e843312ace54370f2a791fe98d8b8e10810146b51ae8ab13dd2aa`.

## Verified computations

All four pinned E001/E002 input hashes and counts match. Across every split
and method, confusion counts agree exactly and 195 metric comparisons agree
within the locked serialization tolerances: maximum absolute discrepancy is
1.013e-15 for E001 and 4.70588235e-10 for E002. Full method coverage, per-case
truth/input/cluster alignment, base/cluster split disjointness, and paired
binary-ablation decisions pass. No cross-split input-hash overlap was found.
All serialized probabilities match calibration-only lookup reconstruction
within tolerance; this establishes compatibility, not historical proof of no leakage.

The Brier decomposition has exactly zero rational residual in all 39 rows.
On the confirmatory split, E001 B0 reliability/resolution/uncertainty are
0/0/0.25; M1 values are 0.000059171597633136/0.25/0.25. Thus the Brier decrease
coexists with worse score-group reliability. E002 B0 values are
0.000112121472633867/0.002357517534036659/0.094182825484764543; M1 values are
0.000247902918518730/0.094182825484764543/0.094182825484764543. Resolution
again improves while empirical reliability worsens. These are finite score-group
statistics, distinct from population calibration.

E001 has 1 distinct statistic signature among 64 confirmatory clusters for
each method. E002 has 6 among 48. These counts do not estimate effective sample
size. M1-no-calibration has Brier=ECE=0 on both evaluation splits, with exactly
the same decisions as M1. This does not recommend hard probabilities on new data.

## Synthesis and manuscript use

The methods contribution proposed for the paper is a transparent case study of
measurement and construction effects, with these finite results and conditional
mathematical explanations. Neither invariant checking nor Brier decomposition
is claimed as new. Novelty and independent assessment are still open.
Do not interpret source provenance as independently authored truth labels.

E003-v2 remains at M17 with its independent-acceptance gate; no external
performance evidence has been added. E003-v1 stays invalid; E004 stays diagnostic.
Original protocols/artifacts and unrelated user files were preserved.
`public_claim_eligibility=false`; no submission, push or automation occurred.

Next: source-verified related-work comparison, complete English manuscript and
rendered LaTeX preview, then substantive review and owner metadata.
