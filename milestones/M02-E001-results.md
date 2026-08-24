# M02 — E001 synthetic calibration results

## ID

M02

## Status

verified within the finite synthetic E001 design

This milestone records one valid, published E001-v1 confirmatory run. It does
not establish production validity, external validity, generalization, novelty,
safety, or public-claim eligibility.

## Authority and provenance

**User authority (Provenance: user):** On 2026-08-25 the exact user message
was `cả hai, nghiên cứu lâu đi, bao lâu cũng được`. It supplied high-level
authority for both the previously discussed public push and the E001
implementation/run. It did not select the technical design.

The detailed E001 oracle, recipes, invariant families, metrics, bootstrap,
ablations, and validation gates are reviewer/worker design choices. They are
not user-selected technical design and are not observations. The observed
result is limited to the published artifacts below.

## Protocol, implementation, run, and result chain

- Protocol: [E001-v1](../experiments/E001-synthetic-invariant-calibration/protocol.md),
  commit `d8b26d21e9692ace19436d78461460940043f5c7`.
- Implementation: [E001 harness](../experiments/E001-synthetic-invariant-calibration/code/e001.py),
  commit `54f530d375372589e191e0231152a177d29c2a64`.
- Run: `e001-20260825-001`, status `valid`.
- Result: [run Markdown](../experiments/E001-synthetic-invariant-calibration/results/run-e001-20260825-001.md),
  commit `31071ddf65ad9a1f0e5b28eb0d501899253cd17b`, verified on
  `origin/main`.
- Read-only ancestry checks verified that the protocol commit precedes the
  implementation/result chain and that the remote result hash equals the
  result commit.

## Run validation

- Split counts: development 256, calibration 256, confirmatory 512.
- Confirmatory clusters: 64.
- Paired cluster-bootstrap replicates: exactly 10,000.
- Reviewed development tests: 21.
- Independent review: approved.
- Deviations: none.

## Published artifacts

| Path | SHA-256 | Size | Count |
| --- | --- | ---: | ---: |
| [Predictions](../data/E001-v1-predictions.jsonl) | `be5e5e2a6c3f33778a34af69d79ec4f14e3b2c0cba2f371ecc004310b7c9559a` | 2,966,528 B | 5,120 rows |
| [Metrics](../data/E001-v1-metrics.csv) | `ae7c32be651b5dfe175ca0537aa3cb8283acbd7063b14e15b8ec386f0d6a20cb` | 162,200 B | 75 rows + header |
| [Bootstrap](../data/E001-v1-bootstrap.csv) | `63b86d44f3425f0c2a43c53191d13ce614b0d0726ff1e941da98d11ee545ede5` | 32,920,126 B | 450,270 rows + header |
| [Result Markdown](../experiments/E001-synthetic-invariant-calibration/results/run-e001-20260825-001.md) | `cc00b21deabb88fd51c55090fc642a80424f960ad6b51c50f75818e8ffa485d6` | 2,870 B | 60 lines |

## Confirmatory finding

The primary analysis is strictly M1 minus B0. B0 had balanced accuracy `0.5`,
FPR `1`, FNR `0`, Brier `0.25`, and ECE `0`. M1 had balanced accuracy `1`, FPR
`0`, FNR `0`, Brier `0.00005917159763`, and ECE `0.007692307692`.

The primary deltas (M1 minus B0) were:

- balanced accuracy: `+0.5`
- FPR: `-1`
- FNR: `0`
- Brier: `-0.2499408284`
- ECE: `+0.007692307692`

H1 was **supported within this synthetic design** under the locked rule: the
paired 95% interval for delta balanced accuracy was entirely greater than zero,
the paired interval for delta FPR was entirely less than zero, and the point
delta FNR was at most zero. The FNR guardrail was satisfied.

### Secondary ablations

- M1-no-semantic: BA `0.75`, FPR `0.5`, FNR `0`, Brier `0.166726273`, ECE
  `0.005076538582`.
- M1-no-state: BA `0.75`, FPR `0.5`, FNR `0`, Brier `0.166726273`, ECE
  `0.005076538582`.
- M1-no-calibration: BA `1`, FPR `0`, FNR `0`, Brier `0`, ECE `0`.

These ablations are secondary analysis and do not change the primary paired
M1-minus-B0 deltas.

## Limitations and eligibility

The paired intervals are degenerate because the locked 64-cluster signatures
were identical across all 10,000 replicates. This reflects the finite synthetic
construction, not broad uncertainty evidence.

The oracle is coupled to the hand-designed recipes. E001 is finite, balanced,
synthetic, and single-fault. It does not establish production validity,
external validity, generalization, novelty, or safety. Therefore:

```yaml
public_claim_eligibility: false
```

## M01 completion and outer-loop decision

M01's documentary protocol-locking step is complete and published as an
ancestor of this result. M02 is the separate experimental milestone record;
it does not conflate protocol provenance with observed performance.

**Decision: deepen and broaden.** A future, separately locked E002 protocol
should address heterogeneous clusters, specification misspecification,
multi-faults, and stronger oracle-method separation. This is reviewer/design
inference, not an E002 result. No E002 protocol, implementation, run, result,
or claim exists.
