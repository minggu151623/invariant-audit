# E001 — Synthetic invariant calibration

## Protocol identity and gate

- **Protocol version:** `E001-v1`
- **Milestone:** [M01 — protocol design](../../milestones/M01-protocol-design.md)
- **Status:** protocol-ready local draft; it becomes locked only after the
  required dedicated protocol commit.
- **Planned commit subject:** `research(protocol): lock E001 synthetic invariant calibration`
- **Protocol commit:** intentionally not recorded until that commit exists.

This protocol is documentary work only. No experiment, run, result, metric,
figure, or data file is created by this task. No future run is valid until this
file is committed in its own commit before any run/result/data record. A future
result must record this path, the exact protocol commit hash, and its run ID;
the protocol commit must be an ancestor of the result commit. A protocol change
after a run begins requires a new protocol version and a new run.

The experiment is local-only: one ordinary CPU process, deterministic local
files, no paid API, no network, no external GPU, no credentials, and no
dependency installation. The implementation is intentionally not part of this
protocol-only change.

## Research question and hypothesis

**Research question.** On a deterministic synthetic dataset with exact oracle
truth, does an invariant-aware validator detect semantic and state violations
with better false-positive/false-negative balance and confidence calibration
than a schema-only validator?

**Primary hypothesis H1.** On the locked confirmatory split, the invariant-aware
method M1 will have higher balanced accuracy and a lower false-positive rate
than the schema-only baseline B0. The false-negative rate is a co-primary
guardrail: any increase is reported rather than hidden. Secondary predictions
are lower Brier score and lower fixed-bin expected calibration error for M1's
confidence output after the pre-specified calibration step. These are directional
predictions, not observed results or claims about production systems.

The positive class is **valid**: a case satisfies all applicable invariants.
Therefore `TP` means a valid case accepted, `TN` an invalid case rejected,
`FP` an invalid case accepted, and `FN` a valid case rejected.

## Invariant taxonomy and oracle

Each source bundle is valid before transformation. The oracle independently
evaluates all four families below. A case's target family is metadata for the
evaluator and analysis only; it is not passed to either validator.

| ID | Family | Required invariant | Positive transformation | Single-fault negative |
| --- | --- | --- | --- | --- |
| S1 | Semantic identity/reference | Entity IDs, ledger entry IDs, and event IDs are each unique; every ledger/event reference resolves to exactly one entity. | Apply the fixed record-order permutation below without changing IDs, amounts, or references. | Change `ledger-1.entry_id` from `ledger-1` to the existing value `ledger-0`; leave all records, amounts, and references otherwise unchanged. |
| S2 | Semantic conservation | `declared_total_cents = sum(ledger.amount_cents)` for the bundle. | Split one ledger entry into two entries whose integer amounts sum to the original. | Change one amount without changing the declared total. |
| T1 | State transition legality | Each event follows the finite transition relation `pending -> active`, `active -> active`, or `active -> closed`; no event leaves `closed`. | Apply the fixed event-order permutation below, preserving each entity's event sequence. | For entity 0's second event, change `to_state` from `closed` to `pending` and change `entity-0.current_state` from `closed` to `pending` so T2 remains satisfied. |
| T2 | State revision consistency | Revisions for each entity increase by one per event and `current_state` equals the final event's target state. | Append the fixed `event-3-1` `active -> active` revision with revision 2. | For entity 0's second event, change `revision` from 2 to 1 while leaving `entity-0.revision` at 2 and all transitions unchanged. |

### Locked identifiers and case recipes

Every base bundle uses the following exact identifiers and base order:

- Entities are `entity-0`, `entity-1`, `entity-2`, and `entity-3`, in that
  order. Ledger rows are `ledger-0` through `ledger-3`, where `ledger-i`
  references `entity-i`. Events are ordered as
  `event-0-0`, `event-0-1`, `event-1-0`, `event-1-1`, `event-2-0`,
  `event-2-1`, `event-3-0`.
- `event-0-0`, `event-1-0`, and `event-2-0` are `pending -> active` at revision
  1; `event-0-1`, `event-1-1`, and `event-2-1` are `active -> closed` at
  revision 2; `event-3-0` is `pending -> active` at revision 1.
- The valid base has `entity-0` through `entity-2` at `closed` with final
  revision 2, and `entity-3` at `active` with final revision 1. The declared
  total is the sum of the four base ledger amounts.

For each base and target family, apply exactly one recipe below. Do not choose
another entity, row, event, permutation, delta, or fault form:

- **S1 positive:** reorder `entities` as
  `[entity-2, entity-0, entity-3, entity-1]`, `ledger` as
  `[ledger-3, ledger-1, ledger-0, ledger-2]`, and `events` as
  `[event-2-0, event-0-0, event-3-0, event-1-0, event-2-1, event-0-1,
  event-1-1]`. No field values change.
- **S1 negative:** set only `ledger-1.entry_id` to `ledger-0`. Keep the
  `ledger-1.entity_id`, amount, all entity rows, all event rows, and all
  references unchanged. The only intended failure is the ledger-ID collision.
- **S2 positive:** replace `ledger-0` with `ledger-0a` and `ledger-0b`, both
  referencing `entity-0`. If the base amount is `a0`, set their amounts to
  `floor(a0 / 2)` and `a0 - floor(a0 / 2)`, respectively, and place them in
  the original `ledger-0` position. Keep `declared_total_cents` unchanged.
- **S2 negative:** set only `ledger-1.amount_cents` to its base value plus 1;
  keep `declared_total_cents` and every other field unchanged. The base range
  makes the resulting amount remain in the allowed `[100, 500]` range.
- **T1 positive:** reorder `events` as
  `[event-1-0, event-0-0, event-2-0, event-0-1, event-1-1, event-2-1,
  event-3-0]`. No event fields change, and each entity's within-entity order
  remains unchanged.
- **T1 negative:** change exactly these two fields: set `event-0-1.to_state`
  from `closed` to `pending`, and set `entity-0.current_state` from `closed`
  to `pending` so the T2 final-state condition remains true. Keep
  `from_state=active`, revision 2, and every other field unchanged.
- **T2 positive:** append `event-3-1` after `event-3-0` with
  `{event_id: event-3-1, entity_id: entity-3, from_state: active,
  to_state: active, revision: 2}` and set `entity-3.revision` to 2. Keep its
  current state `active`.
- **T2 negative:** in `event-0-1`, change only `revision` from 2 to 1. Keep
  `entity-0.revision=2`, both transition states, `entity-0.current_state`, and
  every other field unchanged.

The oracle must verify after each recipe that the positive case passes all four
families and the negative case fails only its named family. No recipe is
combined with another recipe.

The oracle labels a case `truth=1` only when all four families pass and
`truth=0` otherwise. It also records `target_family`, `fault_id`, and an
`oracle_reason` in evaluator-only metadata. The intended positive/negative label
and the independently recomputed all-family oracle label must agree; otherwise
the run is invalid. The oracle manifest is never included in the sanitized
validator input.

## Synthetic input and generator

The generated payload has only these fields:

```text
meta: {schema_version: "E001-v1", declared_total_cents: integer}
entities: [{entity_id, current_state, revision}]
ledger: [{entry_id, entity_id, amount_cents}]
events: [{event_id, entity_id, from_state, to_state, revision}]
```

All identifiers are ASCII strings. States are exactly `pending`, `active`, or
`closed`; amounts and revisions are integers; every payload amount must be in
`[100, 500]` cents. Fixed base-shape parameters are four entities, four ledger
entries, and seven events: entities 0–2 follow `pending -> active -> closed`,
while entity 3 follows `pending -> active` and remains active for the T2
positive transformation. Each base ledger amount is drawn in `[200, 499]`
cents, and event revisions start at 1 and increase by one. The generator
constructs the base so that all four invariant families pass. Negative
mutations preserve the payload schema and target only the named family. The
methods receive only the payload above, not `truth`, split, seed, target family,
transform name, fault ID,
oracle reason, or calibration labels.

The generator is deterministic and dependency-light:

- Version string: `E001-v1`.
- Split seeds: development `[101, 102]`, calibration `[201, 202]`, and
  confirmatory `[301, 302, 303, 304]`.
- Each seed produces exactly 16 base bundles. Each base produces eight cases:
  one valid and one single-fault invalid case for each of S1, S2, T1, and T2.
- The arithmetic is fixed: `2 + 2 + 4 = 8` seeds, `8 * 16 = 128` base
  bundles, and `128 * 8 = 1,024` cases. Splits are 256 development cases
  (`2 * 16 * 8`), 256 calibration cases (`2 * 16 * 8`), and 512 confirmatory
  cases (`4 * 16 * 8`); each split has equal valid/invalid and per-family
  counts. The confirmatory split has 64 base-case clusters (`4 * 16`).
- `base_case_id` is `{split}-{seed}-{index:02d}` and `case_id` is
  `{base_case_id}-{family}-{valid|invalid}`. Base IDs never overlap splits.
- For every amount draw, let `split` be the literal split name, let `seed` and
  zero-based `base_index` be decimal ASCII, and let `draw_index` be the decimal
  index `0`, `1`, `2`, or `3` for `ledger-0` through `ledger-3`. Form the exact
  UTF-8 input string
  `E001-v1|value|<split>|<seed>|<base_index>|<draw_index>`, hash it with
  SHA-256, interpret bytes 0–7 as an unsigned 64-bit integer in big-endian
  order, and compute
  `value = lo + (u64 mod (hi - lo + 1))`. Use `lo=200`, `hi=499` for each
  base amount. There are no other value draws; IDs, states, revisions, and
  recipes are fixed above. No system clock, locale, UUID, process order,
  parallel scheduling, or library-specific random-state behavior may affect
  generated values.
- Canonical payload hashes use UTF-8 JSON with recursively sorted object keys,
  no insignificant whitespace, and integer values serialized as integers.

The pair of valid and invalid cases for each base/family is retained for audit
and clustered for uncertainty, but validators run cases independently. The
design uses transformations to exercise semantic/state invariance and uses
fault injections to supply known negatives; it does not claim that these four
families cover all real invariants.

## Baseline, method, and confidence calibration

### B0 — schema-only baseline

B0 parses the payload, checks required fields, scalar types, allowed state
values, integer ranges, and local record shape; it accepts valid transformation
cardinalities such as the S2 split and T2 append. It does not check
cross-record identity/reference, sums, transition paths, revisions, or
final-state consistency.
Its decision is `valid` iff the shape checks pass; its pre-calibration raw score
is `shape_pass ∈ {0,1}`. The generator is designed so the targeted negative
mutations remain shape-valid, but this must be verified as a sanity check rather
than assumed from a result.

### M1 — invariant-aware validator

M1 runs all four invariant families S1, S2, T1, and T2 on the sanitized payload.
Its decision is `valid` iff zero families fail, and its pre-calibration raw score
is the integer `violated_family_count ∈ {0,1,2,3,4}`. M1 may report which
predicates failed, but it may not use any oracle-only metadata or target-family
hint.

### Fixed confidence mapping

The classification decision is kept separate from confidence so that calibration
cannot silently change FP/FN accounting. After the method has produced its raw
score, fit one deterministic empirical mapping on the **calibration split only**:

```text
p_valid(score) = (number of calibration cases with truth=1 and this score + 1)
                 / (number of calibration cases with this score + 2)
```

This is Laplace-smoothed lookup by the exact raw score. If a score is absent from
the calibration split, use the same smoothed global calibration-split fraction.
The mapping is fit separately for B0 and M1, is frozen before confirmatory
evaluation, and uses no confirmatory labels. `p_valid` is required to be in
`[0,1]`; it is an evaluation confidence output, not an assertion that the
synthetic benchmark represents a real-world probability distribution.

## Dataset split and analysis boundary

- **Development:** implementation smoke tests, generator sanity checks, and
  debugging only. Development observations cannot change this protocol,
  seeds, transformations, thresholds, or primary metrics.
- **Calibration:** fit the fixed confidence lookup above. It is disjoint by
  seed from development and confirmatory cases. No transformation, invariant,
  or decision rule may be selected using confirmatory labels.
- **Confirmatory:** one locked evaluation of B0 and M1 on all 512 cases. The
  primary H1 comparison, confidence intervals, and pre-specified secondary
  family summaries use this split only.

## Metrics

For each method, report counts and rates on the confirmatory split, overall and
by target family. Use `y=1` for valid and `y_hat=1` for accepted.

```text
FPR = FP / (FP + TN)
FNR = FN / (FN + TP)
precision = TP / (TP + FP)
recall = TP / (TP + FN)
specificity = TN / (TN + FP)
F1 = 2*TP / (2*TP + FP + FN)
balanced_accuracy = (recall + specificity) / 2
```

Also report support, TP, TN, FP, and FN. If a subgroup denominator is zero,
report `NA` with the denominator rather than imputing zero; the aggregate
design has both truth classes by construction.

For confidence calibration, report:

- **Brier score:** `mean((p_valid - y)^2)`, lower is better. It is reported as
  a proper probability score and not interpreted as a pure calibration-only
  measure.
- **Expected calibration error (ECE):** use ten fixed equal-width bins
  `[0,.1), ...,[.9,1]`, with the final bin closed at 1. For each non-empty bin
  `b`, compute `(|b|/N) * |mean(p_valid_b) - mean(y_b)|` and sum over bins.
  Lower is better. Report bin counts, mean confidence, and empirical valid
  frequency so ECE is auditable.

The primary endpoint is the paired difference in balanced accuracy
`ΔBA = M1 - B0`. Report directional differences for FPR, FNR, Brier, and ECE
without turning a favorable point estimate into a claim. No multiple-comparison
claim is made for the secondary metrics. The pre-registered H1 support rule is
unambiguous: label H1 supported within this synthetic design only if the paired
95% bootstrap confidence interval for `ΔBA` is entirely greater than 0, the
paired 95% bootstrap confidence interval for `ΔFPR = M1 - B0` is entirely less
than 0, and the confirmatory point estimate satisfies `ΔFNR = M1 - B0 <= 0`.
Otherwise label the result **mixed/not supported**. Always report the
secondary-metric estimates and intervals, with the existing no-overclaim
boundary.

## Uncertainty and confidence intervals

Use a deterministic **10,000-replicate, 95% percentile cluster bootstrap** on
the confirmatory split. First sort its 64 `base_case_id` values by their exact
UTF-8 lexicographic string order and assign indices `0..63`. For replicate
`r=0..9,999` and within-replicate draw `j=0..63`, form the exact UTF-8 input
string `E001-v1|bootstrap|<r>|<j>`, hash it with SHA-256, interpret bytes 0–7
as an unsigned 64-bit big-endian integer `u64`, and select cluster index
`k = u64 mod 64`. The replicate is the ordered sequence of the 64 selected
clusters; each selected cluster contributes all eight of its cases. Keep the
calibration lookup frozen while resampling confirmatory predictions.

For each replicate, recompute every metric and the paired M1-minus-B0 delta on
the same resampled clusters. The interval is the 2.5th to 97.5th percentile.
Do not replace undefined replicate metrics with zero; report the number of
usable replicates and mark the interval unavailable if the pre-specified
denominator rule makes it undefined. These intervals describe resampling
uncertainty over this finite synthetic design, not a confidence statement about
production data or an unobserved population.

## Sanity checks before trusting metrics

The harness must stop before analysis unless all checks pass:

1. Regenerating every split twice gives byte-identical canonical payloads,
   case IDs, oracle labels, and payload hashes.
2. Counts equal 256/256/512 by split, with equal valid/invalid counts and equal
   family quotas; no base ID appears in more than one split.
3. Every generated base passes all four oracle families; every positive
   transformation remains valid; every negative mutation fails its target
   family and passes all non-target families.
4. Each mutation changes the intended payload fields and nothing outside its
   declared fault footprint; each valid transformation preserves its intended
   semantic/state relation.
5. Validator inputs contain no oracle-only fields; calibration labels are used
   only after calibration cases are isolated; confirmatory labels are not read
   while fitting any mapping.
6. Every output has a unique case/method key, a Boolean decision, finite
   `p_valid` in `[0,1]`, and an allowed raw score. No NaN, infinity, missing row,
   duplicate row, crash, or silent exception is accepted.
7. Re-running the evaluator with the same protocol and inputs produces the same
   output hashes. A rerun is a determinism check, not an additional sample.

## Ablations

These are pre-specified secondary analyses and cannot alter the primary H1
comparison:

- `M1-no-semantic`: remove S1 and S2 while retaining T1 and T2.
- `M1-no-state`: remove T1 and T2 while retaining S1 and S2.
- `M1-no-calibration`: use the frozen binary raw decision as `p_valid ∈ {0,1}`
  for Brier/ECE, leaving the classification decision unchanged.

Run each ablation with the same confirmatory cases and report its own counts and
calibration metrics. Any new ablation, alternative score, threshold, weight,
seed, transformation, or fault is exploratory and must not be mixed into the
confirmatory result.

## Expected future outputs and schemas

This protocol does not create these files. A future valid run may create only
after the protocol commit:

- `experiments/E001-synthetic-invariant-calibration/results/run-<run_id>.md`:
  protocol path/version/commit, run ID, environment, exact deviations, sanity
  status, summary tables, invalid-run status, limitations, and links to data.
- `data/E001-v1-predictions.jsonl`: one row per method/case with
  `run_id`, `protocol_path`, `protocol_commit`, `method`, `split`, `seed`,
  `base_case_id`, `case_id`, `target_family`, `truth`, `decision`, `raw_score`,
  `p_valid`, `input_sha256`, `oracle_manifest_sha256`, and `status`.
- `data/E001-v1-metrics.csv`: one row per method/split/subgroup with support,
  TP, TN, FP, FN, FPR, FNR, precision, recall, specificity, F1, balanced
  accuracy, Brier, ECE, and interval references.
- `data/E001-v1-bootstrap.csv`: replicate index, method pair, subgroup,
  metric, M1-minus-B0 delta where applicable, and bootstrap status.

The evaluator may keep oracle reason/fault metadata in a separate restricted
join or manifest, but it must not expose those fields to the methods. Markdown
interpretation remains the narrative source; JSONL/CSV remains row-data source.

## Stopping and invalid-run criteria

There is no metric-based early stopping. A valid primary run processes all
development checks, all 256 calibration cases, and all 512 confirmatory cases
for B0 and M1, then freezes outputs and computes the pre-specified bootstrap.
The run stops successfully only when all sanity checks, schema checks, and
determinism checks pass. Resource use is limited to one local CPU process and a
small synthetic workload; external services and GPUs are prohibited.

Mark the run **invalid**, do not report its metrics as evidence, and preserve a
failure record if any of the following occurs: missing protocol commit; changed
protocol inputs or parameters; wrong generator version/seed/count; oracle
positive/negative mismatch; split leakage; oracle or calibration-label leakage;
missing/duplicate/malformed/non-finite outputs; nondeterministic regeneration;
unrecorded manual intervention; dependency/network/API/GPU use; or incomplete
case processing. A corrected rerun gets a new run ID and must still reference
the same protocol commit, unless the protocol itself is versioned before the
rerun.

## Confirmatory versus exploratory boundary

**Confirmatory** means only the locked E001-v1 primary B0-versus-M1 comparison
on the exact confirmatory seeds, transformations, truth definition, decisions,
metrics, calibration mapping, and bootstrap procedure written here. The listed
family summaries and ablations are pre-specified secondary analyses and cannot
upgrade the primary conclusion.

**Exploratory** includes development observations, per-case debugging, new
seeds, new transformations or faults, post-hoc thresholds/weights, alternative
confidence mappings, unplanned subgroups, and metrics added after seeing
confirmatory outputs. Exploratory observations must be labeled as such and
cannot be used to rewrite H1 or the protocol retrospectively.

## Limitations and no-overclaim language

E001 uses a finite hand-designed ontology, exact synthetic truth, balanced
classes, single-fault mutations, and transformations coupled to the same
invariant specification that defines the oracle. It omits real data noise,
ambiguous semantics, distribution shift, adversarial adaptation, implementation
bugs outside the four families, and production cost or usability. The baseline
is intentionally surface-only and is a calibration floor, not a representative
competitor. Cluster-bootstrap intervals are conditional on this generator and
do not establish external validity.

Before results exist, the only accurate statement is that E001 specifies a
calibration protocol. Even after a valid run, results would support claims only
about this synthetic design and its recorded methods. They would not establish
general invariant validity, real-world performance, novelty, safety,
production readiness, or public-claim eligibility. A future verified milestone
and human review remain required.
