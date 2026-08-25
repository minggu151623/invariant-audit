# M08 — E002 corrected run 002 valid result

Status: one valid locked local confirmatory run is recorded; no public claim
or external action is authorized.

## Gate transition and provenance

M07 was the historical technical-readiness gate for candidate
`e002-20260825-002`. It recorded technical readiness subject to runtime
preflight, but did not itself authorize or execute a run. The current bounded
user brief then explicitly authorized exactly one corrected local run with
this run ID, its locked result recording, and no retry, push, publication, or
other external action. The user did not select the E002 technical design.

The implementation and review chain remains worker/reviewer provenance:
initial implementation `42cb62374c2b94ad6c567232acdac6d7365a9d8f`, result
validator hardening `6df4f3bc02f5f12feb243df21ec9eeaafd53d8fc`, independent-review
remediation `0977641f129d172dd4d11136197a82cb17654aeb`, exact-delta fix
`e090fa76be67a3cb1d52517bd93327ef821b8e75`, and final development-test-boundary
remediation `1fe42a7ebc6a9ce69d8a16654e068c0a9a891d08`.

## Runtime preflight

The run began from HEAD
`86ede8ac1fcd674b9cc559ee7ad2c381efa4f3d0` with a clean worktree. The locked
E002 protocol commit
`9e39c5defc89f2c2a896b53dda529f326e9dfcf8` was an ancestor and
`experiments/E002-heterogeneous-specification-stress/protocol.md` had blob
`f7d27a069ee3fd1600f89d9271e107c197033238`. The candidate final outputs and
all checked staging, temporary, and lock paths were absent before execution;
the repository cwd and `--output-root .` assumption were correct. Python was
`3.13.5` and `19,730,772` 1-KiB blocks were free (approximately `18.8 GiB`).
The protocol requires standard-library-only local CPU execution with no
network/API/GPU and does not pin a Python minor version, so this runtime was
nonblocking.

## Single execution

The exact command was started at `2026-08-25T22:40:19+07:00` and executed
exactly once:

```text
PYTHONDONTWRITEBYTECODE=1 python experiments/E002-heterogeneous-specification-stress/code/run_e002.py --run-id e002-20260825-002 --output-root .
```

It exited `0`. Runner stdout reported:

- `status: valid`;
- `run_id: e002-20260825-002`;
- `result_sha256: d1f11d17be3b91d246126dc36b88880a76f039f31fa7eeef63d5aff4cfe713fa`;
- `multi_fault_relation_sha256: a02432ead45db3633e7cbe2f07e5314fa19dd800d9c2441da34bbfbe08510dd5`;
- `multi_fault_relation_counts: equals=272;contains=160;differs=0`;
- a relation JSON whose rows contain no `differs` relation.

The generated report records all protocol gates as `pass`, the two-build byte
comparison as `pass`, literal `Deviations: none`, and
`confirmatory_execution: completed exactly once`.

## Artifact record

| Artifact | SHA-256 | Size | Count |
| --- | --- | ---: | ---: |
| `data/E002-v1-predictions.jsonl` | `bcb34aad4338fdfbffe07be1843769b360bf4e8c422d855a9ce605350fad13b7` | 6,556,304 B | 7,296 rows |
| `data/E002-v1-metrics.csv` | `f000348d385550745480066fce2d691686728ebe2bfcf7bd96e7231e4b1e5ca3` | 116,260 B | 243 rows + header |
| `data/E002-v1-bootstrap.csv` | `8c5919f709c9ad8ca673308053ecefbe94ca23b0c190b923f14957cbfeac7d5d` | 30,814,607 B | 530,053 rows + header |
| `experiments/E002-heterogeneous-specification-stress/results/run-e002-20260825-002.md` | `d1f11d17be3b91d246126dc36b88880a76f039f31fa7eeef63d5aff4cfe713fa` | 6,486 B | 100 lines |

The prior invalid report
[run-e002-20260825-001.md](../experiments/E002-heterogeneous-specification-stress/results/run-e002-20260825-001.md)
is preserved with SHA-256
`f441d55795b81d280e35b09980dcb6f79e58e7cfacbe9886ed094a207580aa34`; it was
not overwritten.

## Locked result and interpretation

The result report records the primary confirmatory M1-minus-B0 deltas:

| Metric | Delta |
| --- | ---: |
| balanced accuracy | `0.401960784` |
| FPR | `-0.803921569` |
| FNR | `0.000000000` |
| Brier | `-0.091689527` |
| ECE | `0.005222762` |

The co-primary stress intervals passed, H2 outcome is `supported`, and the
FNR guardrail passed at delta `0.000000000`. This is confirmatory evidence
only for the finite, synthetic, locked E002-v1 construction, its hand-
specified oracle, bounded recipe inventory, and cluster-bootstrap design. It
does not establish production performance, external validity, novelty, safety,
generalization, or a public claim. No exploratory run, retry, or post-hoc
analysis was performed.

## State transition and next gate

M08 is current and supersedes M07 as the current milestone. The one-run
corrected authorization is consumed: `run_001` remains invalid only,
`run_002` is valid, and the four result/data artifacts are present. The
documentary state is `results: present`, `data: present`, `metrics: present`,
`evidence: present`, `h2_outcome: supported_within_finite_synthetic_protocol`,
and `public_claim_eligibility: false`. The protocol commit/blob remain
unchanged. No additional E002 run, publication, push, or public claim is
authorized by M08; any future action needs separate explicit authority and a
new bounded gate.
