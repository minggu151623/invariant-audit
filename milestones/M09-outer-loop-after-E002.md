# M09 — Outer-loop reflection after E002

Status: verified documentary reflection; no public claim or external action is
authorized.

## Scope and provenance

M09 synthesizes the two verified local confirmatory records, M02/E001 and
M08/E002. The observed numbers below come only from their locked result
Markdown and row artifacts. The mechanism interpretation, remaining-gap
analysis, and direction choice are reviewer/design inference, not user-selected
technical design and not new experimental evidence.

## Evidence reviewed

- E001 run `e001-20260825-001` is valid under E001-v1. Its confirmatory split
  has 512 cases, 64 clusters, and 10,000 paired bootstrap replicates.
- E002 run `e002-20260825-002` is valid under E002-v1. Its confirmatory split
  has 456 cases from 48 clusters, and its full design has 96 clusters and
  10,000 bootstrap replicates. The preserved E002 run `e002-20260825-001`
  remains invalid and is not pooled with the valid run.

## Quantitative synthesis

The primary comparison in both experiments is M1 minus the schema-only B0
baseline.

| Experiment | Confirmatory cases / clusters | ΔBA | ΔFPR | ΔFNR | ΔBrier | ΔECE | Locked outcome |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| E001 synthetic, single-fault | 512 / 64 | `+0.5` | `-1` | `0` | `-0.2499408284` | `+0.007692307692` | H1 supported |
| E002 heterogeneous synthetic | 456 / 48 | `+0.401960784` | `-0.803921569` | `0.000000000` | `-0.091689527` | `+0.005222762` | H2 supported |

E001's confirmatory method points were B0 BA/FPR/FNR `0.5/1/0` and M1
`1/0/0`. E002's were B0 `0.598039216/0.803921569/0.000000000` and M1
`1/0/0`. E002 also passed all three co-primary specification-stress
diagnostics: omit-conservation FPR delta `0.352941176` with interval
`[0.340425532, 0.366412214]`, overconstraint FNR delta `1.000000000`, and
stale-transition FNR delta `1.000000000`.

## Supported pattern and mechanism

The repeated pattern is that schema-only acceptance is too permissive on
schema-valid semantic/state faults, while M1's retained identity,
conservation, transition, and revision checks separate valid cases from those
faults in both locked synthetic constructions. E001's semantic and state
ablations each fell to BA `0.75` and FPR `0.5`; E002's no-semantic and no-state
ablations each had BA `0.823529412` and FPR `0.352941176`. Inference: the gain
is attributable to cross-field semantic/state checks rather than schema
parsing alone within these constructions. It is not a claim about a deployed
system.

## Lessons and constraints

1. Synthetic protocol stress was useful: E002 added heterogeneous cluster
   signatures, bounded misspecification, bounded multi-faults, co-primary
   stress diagnostics, and an independently maintained replay/conservation
   oracle. It did not remove the synthetic source boundary.
2. The first E002 execution failed before evidence because the validator
   subtracted rounded metric cells instead of exact fractions. The corrected
   run passed after remediation. Exact arithmetic, protocol-before-results,
   independent validation, and preserved invalid-run records remain mandatory.
3. E001's intervals were degenerate because all 64 cluster signatures were
   identical. E002 produced nondegenerate primary intervals, but they still
   describe its designed finite cluster resampling, not population uncertainty.
4. Calibration and ablation bookkeeping are now exercised, but both experiments
   use hand-designed or generated cases. Positive results can still reflect
   alignment between the checker and its synthetic oracle.

## Remaining gaps

- external/real-world transfer to records authored outside this repository;
- natural invalid-rate and naturally occurring false-positive/false-negative
  behavior rather than only deterministic synthetic faults;
- source/schema drift and optional-field irregularity in a frozen public input;
- sequence-level state behavior beyond E002's bounded recipe inventory; and
- a stronger external reference boundary than a hand-specified synthetic
  oracle, while retaining reproducible, privacy-preserving inputs.

## Direction decision

**Decision: BROADEN.** DEEPEN would add more synthetic subcases to a question
already supported twice inside synthetic designs, while CONCLUDE would ignore
the explicit external-validity gap. PIVOT is not warranted because E001 and
E002 show a coherent repeated pattern rather than an invalidated research
question. The next experiment should therefore test the frozen method on an
externally authored structured-event fixture, with a predeclared adapter,
independent oracle boundary, source hash, and split isolation.

This decision is not a public claim. `public_claim_eligibility` remains
`false`.

## Next gate

Design and locally lock E003-v1 as a protocol-only external-transfer
validation. The fixture must be acquired and hashed only in a later separately
authorized stage. Until then, E003 has no snapshot, code, run, result, metric,
data, or public output.

## Verification

- Primary records: [M02](M02-E001-results.md) and
  [M08](M08-E002-run-002-valid.md).
- E001 result: `experiments/E001-synthetic-invariant-calibration/results/run-e001-20260825-001.md`.
- E002 result: `experiments/E002-heterogeneous-specification-stress/results/run-e002-20260825-002.md`.
- Report: [M09 progress presentation](../to_human/progress-M09.html).
