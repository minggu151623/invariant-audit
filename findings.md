# Findings

This document separates user authority, protocol/design provenance, observed
E001 results, and reviewer/design inference. M02 is verified only within the
finite synthetic E001 design; `public_claim_eligibility` is `false`.

## M00 — research direction

M00 remains a verified documentary record of the user-approved pivot from a
generic metamorphic robustness benchmark toward semantic/state invariants and
false-positive/false-negative calibration. It is not experimental evidence and
does not establish performance, calibration, generalization, novelty, safety,
or public-claim eligibility.

The underlying design specification, scaffold commits, literature notes, and
M00 milestone preserve the original source boundary. Reviewer interpretation
of that pivot is not a user-selected result.

## M01 — protocol-lock documentary step

M01's documentary protocol-locking step is complete and published as an
ancestor of the E001 result. E001-v1 is the protocol at
`experiments/E001-synthetic-invariant-calibration/protocol.md`, locked in
commit `d8b26d21e9692ace19436d78461460940043f5c7`. M01 remains documentary
protocol evidence, not experimental evidence, and does not grant public-claim
eligibility.

The exact user authorization on 2026-08-25 was
`cả hai, nghiên cứu lâu đi, bao lâu cũng được`. It supplied high-level
authority for both the previously discussed public push and the E001
implementation/run. It did not select the technical design; the detailed
recipes, oracle, metrics, gates, and ablations remain reviewer/worker design
choices.

## E001 result — finite synthetic confirmatory finding

### Evidence chain

- Protocol: commit `d8b26d21e9692ace19436d78461460940043f5c7`.
- Implementation: commit `54f530d375372589e191e0231152a177d29c2a64`.
- Run: `e001-20260825-001`, status `valid`.
- Result: commit `31071ddf65ad9a1f0e5b28eb0d501899253cd17b`, published on
  `origin/main`; protocol ancestry and remote result hash were verified
  read-only.
- Split counts were development 256, calibration 256, and confirmatory 512;
  the confirmatory split had 64 clusters and the paired bootstrap used exactly
  10,000 replicates.
- The reviewed development suite contained 21 tests, and independent review
  approved the implementation. Deviations: none.

| Artifact | SHA-256 | Size | Count |
| --- | --- | ---: | ---: |
| `data/E001-v1-predictions.jsonl` | `be5e5e2a6c3f33778a34af69d79ec4f14e3b2c0cba2f371ecc004310b7c9559a` | 2,966,528 B | 5,120 rows |
| `data/E001-v1-metrics.csv` | `ae7c32be651b5dfe175ca0537aa3cb8283acbd7063b14e15b8ec386f0d6a20cb` | 162,200 B | 75 rows + header |
| `data/E001-v1-bootstrap.csv` | `63b86d44f3425f0c2a43c53191d13ce614b0d0726ff1e941da98d11ee545ede5` | 32,920,126 B | 450,270 rows + header |
| `experiments/E001-synthetic-invariant-calibration/results/run-e001-20260825-001.md` | `cc00b21deabb88fd51c55090fc642a80424f960ad6b51c50f75818e8ffa485d6` | 2,870 B | 60 lines |

### Primary result: M1 minus B0

The primary comparison is strictly M1 minus B0. On the confirmatory split:

| Method | BA | FPR | FNR | Brier | ECE |
| --- | ---: | ---: | ---: | ---: | ---: |
| B0 | 0.5 | 1 | 0 | 0.25 | 0 |
| M1 | 1 | 0 | 0 | 0.00005917159763 | 0.007692307692 |
| Delta M1 − B0 | +0.5 | −1 | 0 | −0.2499408284 | +0.007692307692 |

H1 was **supported within this synthetic design**: the paired 95% interval for
delta BA was entirely above zero, the paired interval for delta FPR was entirely
below zero, and the point delta FNR was non-positive. The FNR guardrail was
satisfied at delta FNR `0`. This is not a production or external-validity
claim.

### Ablations

Ablations were reported as secondary analysis and do not change the primary
paired deltas:

- M1-no-semantic: BA `0.75`, FPR `0.5`, FNR `0`, Brier `0.166726273`, ECE
  `0.005076538582`.
- M1-no-state: BA `0.75`, FPR `0.5`, FNR `0`, Brier `0.166726273`, ECE
  `0.005076538582`.
- M1-no-calibration: BA `1`, FPR `0`, FNR `0`, Brier `0`, ECE `0`.

### Uncertainty and limitations

All locked paired bootstrap intervals are degenerate because the 64-cluster
signatures were identical across all 10,000 replicates. Those point intervals
are a consequence of this finite construction, not evidence of broad
uncertainty characterization.

The oracle is coupled to the hand-designed recipes. E001 is finite, balanced,
synthetic, and single-fault. It establishes no production validity, external
validity, generalization, novelty, or safety, and it is not evidence that the
method is calibrated outside this design. Accordingly,
`public_claim_eligibility` remains `false`.

## Outer-loop decision

**Decision: deepen and broaden.** A future, separately locked E002 protocol
should test heterogeneous clusters, specification misspecification,
multi-faults, and stronger separation between oracle and method. This is a
reviewer/design inference for the next protocol, not an E002 result. No E002
protocol, implementation, run, result, or claim exists.

Future E002 work must preserve the protocol-before-results gate and repeat the
provenance separation between user authority, technical design, observed
results, and reviewer inference.
