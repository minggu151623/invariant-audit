# E003-v1 — External transfer validation on preselected GitHub event fixtures

## Protocol identity and boundary

- **Protocol ID:** `E003-v1`
- **Lock subject:** `research(protocol): lock E003 external transfer validation`
- **Protocol path:** `experiments/E003-external-transfer-validation/protocol.md`
- **Current status:** protocol-only design; source snapshot staged but not
  acquired; implementation, execution, result, data, and public claim absent.
- **Execution envelope:** one standard-library-only Python process on local
  CPU after a separately authorized read-only acquisition; no paid API, API
  key, GPU, package installation, live API scoring, or network access after the
  source manifest is frozen.

This lock is a preregistration of the external-transfer test. It contains no
E003 source bytes, predictions, metrics, bootstrap output, result report, or
implementation. The source hashes are intentionally not asserted here because
the current bounded task forbids downloading the fixture. A later acquisition
stage must fill the source manifest and hash it before any scoring begins. A
changed or unavailable source is a staged acquisition failure, not permission
to substitute another snapshot.

## Question, estimand, and hypothesis

**Research question.** When the input is an externally authored structured event
record rather than a hand-designed synthetic bundle, does the invariant-aware
validator M1 retain its reduction in false positives without increasing false
negatives relative to the schema-only baseline B0?

The positive class is `valid`: the event conforms to the E003 subset of the
external event contract and all selected cross-field semantic/state relations.
The negative class is `invalid`: a deterministic schema-preserving or
schema-breaking mutation violates exactly one oracle family. The unmutated
records are real public GitHub event records; the negative variants are
controlled probes derived from those records, not naturally observed invalid
GitHub events. This distinction is part of the estimand and limitation.

**Primary hypothesis H3.** On the frozen confirmatory source shard, M1 minus B0
has a strictly positive paired 95% cluster-bootstrap interval lower endpoint
for balanced-accuracy delta, a strictly negative paired interval upper endpoint
for FPR delta, and a confirmatory point FNR delta less than or equal to zero.
The same directional conditions must hold separately for the two event-type
subgroups. H3 is only an external-fixture result under this protocol; it is not
a production, population, safety, novelty, or generalization claim.

### Falsification and outcome rule

The primary pair is exactly `M1-B0`, with delta defined as method M1 minus B0.
The valid-run outcome is `supported` only when all of these are true:

1. overall delta BA CI lower `> 0`;
2. overall delta FPR CI upper `< 0`;
3. overall point delta FNR `<= 0`;
4. for both `type:IssuesEvent` and `type:PullRequestEvent`, delta BA CI
   lower `> 0`, delta FPR CI upper `< 0`, and point delta FNR `<= 0`; and
5. every required interval has 10,000 usable replicates and no partial or
   undefined status.

If the run passes all validity gates but any condition fails, the report must
say `mixed/not supported`; it must not be upgraded by an ablation or mutation
subgroup. A failure of source, schema, oracle, isolation, determinism,
calibration, size, or overwrite gates makes the run `invalid`, with no metrics
or evidence. There is no post-hoc threshold, subgroup, mutation, or source
selection.

## External source and staged acquisition

### Exact public fixture source

The source is the GH Archive hourly JSON event archive, not a live GitHub API
response. The three exact UTC shards are:

| Split | Archive filename | Exact URL | Intended temporal role |
| --- | --- | --- | --- |
| development | `2019-01-15-12.json.gz` | `https://data.gharchive.org/2019-01-15-12.json.gz` | rule/gate development only |
| calibration | `2020-01-15-12.json.gz` | `https://data.gharchive.org/2020-01-15-12.json.gz` | calibration only |
| confirmatory | `2021-01-15-12.json.gz` | `https://data.gharchive.org/2021-01-15-12.json.gz` | one frozen external holdout |

The three files are selected before acquisition as a time-separated external
holdout. The timestamped filenames are fixed URL choices in this protocol; the
source bytes remain unacquired and still require byte-hash verification before
use.

### Acquisition manifest and hash plan

The snapshot is **not acquired in this task**. At a later separately
authorized acquisition stage:

1. Create a temporary directory outside the repository, for example
   `/private/tmp/invariant-audit-e003-v1/source/`; never place raw public event
   data in Git history.
2. Download exactly the three URLs above with a read-only HTTP client using
   failure-on-error and redirect following. Do not query BigQuery or a live
   GitHub endpoint. Record UTC acquisition time, HTTP status, response byte
   count, `ETag` and `Last-Modified` when supplied, and the URL verbatim.
3. Compute `shasum -a 256` over each original `.json.gz` byte stream. Decompress
   with the Python standard library `gzip`; verify UTF-8 JSON Lines, one JSON
   object per nonempty line, and no trailing binary bytes. Record decompressed
   line count and the raw gzip SHA-256.
4. Write a canonical UTF-8/LF JSON source manifest outside Git with this exact
   structure and sorted object keys:

   ```json
   {"files":[{"bytes":0,"filename":"2019-01-15-12.json.gz","jsonl_lines":0,"sha256":"<64 lowercase hex>","split":"development","url":"https://data.gharchive.org/2019-01-15-12.json.gz"},{"bytes":0,"filename":"2020-01-15-12.json.gz","jsonl_lines":0,"sha256":"<64 lowercase hex>","split":"calibration","url":"https://data.gharchive.org/2020-01-15-12.json.gz"},{"bytes":0,"filename":"2021-01-15-12.json.gz","jsonl_lines":0,"sha256":"<64 lowercase hex>","split":"confirmatory","url":"https://data.gharchive.org/2021-01-15-12.json.gz"}],"protocol_id":"E003-v1"}
   ```

   `bytes` and `jsonl_lines` are nonnegative decimal integers after
   acquisition. The manifest itself is hashed with SHA-256; its digest is
   carried in future prediction/metric/result metadata.
5. Freeze the manifest and disconnect networking before parsing for scoring.
   The runner must recompute every file hash and refuse a mismatch, missing
   file, malformed gzip stream, malformed JSONL line, or changed URL. The
   source manifest hash and all three file hashes are required before the
   confirmatory split is touched.

No source hash, byte count, line count, HTTP header, or snapshot acquisition is
claimed by M09/M10. If any URL is unavailable, the acquisition stage stops
without a result. A new source date or changed byte hash requires a new
protocol version and new lock; it cannot be silently recorded as E003-v1.

## Source contract and canonical representation

The external source supplies raw event objects. The runner projects each
eligible raw object into a canonical event without filling missing values or
consulting an oracle label. Unknown top-level fields and unknown nested fields
are retained in the raw input but are ignored by the E003 projection; required
fields and selected relations are exact.

The canonical projection uses UTF-8, JSON object keys sorted lexicographically,
no insignificant whitespace, and LF termination. Decimal IDs are normalized to
their canonical decimal string form: a JSON integer or a nonempty decimal
string is allowed, but booleans, signs, leading zeroes (except `0`), floats,
and other strings are invalid. The projection records the raw source filename
and one-based source line only as evaluator metadata; actor login and raw text
are never emitted into a report or committed artifact.

### Common event contract

The required top-level keys are `id`, `type`, `actor`, `repo`, `payload`,
`public`, and `created_at`. `type` is one of `IssuesEvent` or
`PullRequestEvent`; `public` is a JSON boolean; `created_at` is an ISO-8601
UTC timestamp ending in `Z` and is parsed only for validity, not rewritten in
the method input. `actor` must be an object with a valid decimal `id` and
string `login`. `repo` must be an object with a valid decimal `id`, nonempty
string `name`, and HTTPS API URL. `payload` must be an object.

The canonical `repo_key` is the decimal `repo.id`. The URL form for a
repository is `https://api.github.com/repos/<owner>/<repo>` with exactly two
nonempty path components after `/repos/`; URL query and fragment are rejected.
The source record's raw `id` is the canonical `event_id` and must be unique
across all three shards. Any duplicate event ID, including a duplicate with
different bytes, is a source-integrity failure; no deduplication choice is
permitted.

### IssuesEvent contract

`payload` must contain `action` and `issue`. For E003 selection, `action` must
be one of `opened`, `closed`, or `reopened`; other documented actions are
excluded because this protocol does not assert a status relation for them.
`issue` must contain a valid decimal `id`, positive integer `number`,
`state` in `{open,closed}`, string `url`, and string `repository_url`.
Within the selected subset, `issue.url` has the exact form
`https://api.github.com/repos/<owner>/<repo>/issues/<number>` and
`issue.repository_url` has the exact top-level repository URL. The identity
relation also requires the URL repository and issue number to agree with the
top-level repository and the issue number.

### PullRequestEvent contract

`payload` must contain `action`, positive integer `number`, and
`pull_request`. For E003 selection, `action` must be one of `opened`, `closed`,
or `reopened`. `pull_request` must contain a valid decimal `id`,
positive integer `number`, `state` in `{open,closed}`, boolean `merged`, and
string `url`.
Within the selected subset, `pull_request.url` has the exact form
`https://api.github.com/repos/<owner>/<repo>/pulls/<payload.number>`. The
identity relation requires `pull_request.number`, `payload.number`, and the
URL number to be equal, and requires the URL repository to agree with the
top-level repository. The state relation is exactly: `opened` and `reopened`
require `state=open` and `merged=false`; `closed` requires `state=closed` with
either value of `merged`. E003 represents a merged pull request as
`action=closed` and `merged=true`; it does not define a separate `merged`
action.

For IssuesEvent, the identity relation requires `issue.number` to equal the
terminal URL number and `issue.repository_url` to equal the top-level
repository URL. Its state relation is exactly `opened` and `reopened` require
`issue.state=open`, while `closed` requires `issue.state=closed`.

The required fields above define the frozen E003 subset. A raw event with a
different but otherwise legitimate historical payload shape is excluded and
counted by split and reason; it is not coerced into the subset.

## Inclusion, exclusion, and case construction

### Raw-record filters

After the source hashes pass, scan each shard in source-line order. Apply these
filters before selecting bases:

1. Parse one JSON object per nonempty line; reject the entire run if a line is
   malformed, duplicated by event ID, or not an object.
2. Keep only the two exact event types and the status actions listed above.
   Exclude all other event types/actions, recording counts by split and raw
   type/action. Excluded rows never enter a metric denominator.
3. Apply the common and event-specific subset contract. Exclude a source event
   that fails the contract, recording the first deterministic reason in the
   order: common schema, event-specific schema, identity relation, state
   relation.
4. Keep only source events accepted by the independent reference oracle with
   an empty failure set. A naturally irregular source event is excluded as a
   base; it is not relabeled as a synthetic negative.
5. Remove every repository ID that occurs in more than one of the three source
   shards. This is a strict group-isolation rule, not a sampled split. The
   remaining repository sets must be pairwise disjoint.

### Deterministic base selection

The selection recipe is fixed before acquisition. Within each split, sort
eligible bases by `(event_type_rank, repo_id_integer, event_id_integer,
source_filename, source_line)`, where `IssuesEvent` has rank 0 and
`PullRequestEvent` rank 1. Greedily retain at most four base events per
`(repo_id,event_type)` and stop at exactly 64 `IssuesEvent` bases and 64
`PullRequestEvent` bases. If either quota cannot be reached, the run is
invalid; do not expand the date range or loosen a filter. Each split must have
at least 24 distinct repository IDs overall and at least 16 distinct repository
IDs within each event type. These are feasibility gates, not post-hoc sample
targets.

Each retained base produces exactly four paired cases:

| Variant | Truth | Oracle failure set | Purpose |
| --- | ---: | --- | --- |
| `clean` | 1 | `[]` | unmutated external record |
| `S1-missing-resource` | 0 | `[schema]` | remove `issue` or `pull_request` |
| `I1-wrong-repository` | 0 | `[identity]` | preserve types, break repository relation |
| `T1-status-contradiction` | 0 | `[state]` | preserve types, break action/state relation |

The mutation input is a deep copy of the canonical raw event. Mutation order
is `S1`, `I1`, `T1`; no mutation is applied cumulatively. The oracle must
recompute the failure set from the mutated payload, not trust the variant name.
Each variant is paired to its base event and remains in the same repository
cluster.

### Exact mutations

- `S1-missing-resource`: delete `payload.issue` for `IssuesEvent` or
  `payload.pull_request` for `PullRequestEvent`. Do not alter any other key.
- `I1-wrong-repository`: use the fixed sentinel repository URL
  `https://api.github.com/repos/e003-fixture-sentinel/repository`. For an
  `IssuesEvent`, replace only `issue.repository_url`; for a
  `PullRequestEvent`, replace only `pull_request.url` with the sentinel plus
  `/pulls/<payload.number>`. The sentinel must differ from the base URL. The
  URL remains schema-valid, while the nested resource no longer belongs to
  the top-level repository.
- `T1-status-contradiction`: for an `IssuesEvent`, replace `issue.state` with
  `closed` for `opened`/`reopened`, and with `open` for `closed`. For a
  `PullRequestEvent`, replace `pull_request.state` with `closed` for
  `opened`/`reopened`, and with `open` for `closed`. All other fields remain
  unchanged.

The source oracle must confirm that every clean base has no failure, each
mutation has exactly the named one-family failure, and the mutation remains
schema-valid for I1 and T1. Any mismatch invalidates the run before metrics.

Total planned cases are 512 per split, 1,536 across all three splits, and
3,072 primary B0/M1 prediction rows. Including the three secondary ablations,
the future prediction artifact has 7,680 rows. These are protocol arithmetic,
not acquired counts.

## Development, calibration, and confirmatory isolation

- **Development:** the 2019 shard is used only for source parsing, projection,
  independent-oracle checks, mutation known answers, split/leakage checks,
  method invariants, determinism, and footprint tests. It is not used to fit
  calibration and must not print confirmatory metrics.
- **Calibration:** the 2020 shard contributes exactly the selected 64+64
  bases and their four variants. Each method is scored once, and only these
  labels fit its frozen empirical probability lookup. No confirmatory record,
  event ID, repository ID, or source line can enter calibration.
- **Confirmatory:** the 2021 shard contributes exactly the selected 64+64
  bases and their four variants. It is scored only after all calibration
  lookups and source hashes are frozen. The method receives only the canonical
  event payload, never `split`, `truth`, `variant`, `repo_key`, oracle output,
  or source metadata.

There is no learned model or train split in E003. “Development” is a gate and
adapter test split; “calibration” fits only method-specific confidence
lookups; “confirmatory” is untouched until the lock and all deterministic
preflight checks pass.

## Methods and baselines

### B0 — schema-only baseline

B0 checks only the common and event-specific local schema: required keys,
strict scalar/container types, ID/date/URL formats, event-type/action enums,
and positive integer fields. It does not compare top-level repository fields to
nested resource fields and does not enforce action/state relations. Its raw
score is the count of local schema failure families in `{0,1}`; its decision is
`valid` exactly when raw score is zero.

### M1 — invariant-aware validator

M1 runs B0 plus two cross-field families:

1. **identity:** for an issue, `issue.repository_url` and the repository
   encoded in `issue.url` agree with top-level `repo.url`, and `issue.number`
   equals the issue URL suffix; for a pull request,
   `pull_request.number`, `payload.number`, and the URL number are equal and
   the URL repository agrees with top-level `repo.url`;
2. **state:** the selected action agrees with the resource state and, for a
   pull request, `opened`/`reopened` also require `merged=false`.

M1's raw score is the number of failed families in `{0,1,2}` (schema,
identity, state), its decision is `valid` iff raw score is zero, and it receives
no oracle or variant metadata.

Predeclared secondary ablations are `M1-no-identity` (B0 plus state),
`M1-no-state` (B0 plus identity), and `M1-no-calibration` (the exact M1
decision with binary confidence). They are descriptive and cannot change H3.
The full calibrated methods are B0, M1, M1-no-identity, and M1-no-state;
each has a separate lookup. No method may use a source line, event ID,
repository ID, variant label, or oracle output as a feature.

### Calibration lookup

For each calibrated method and each raw score `s`, fit only on the calibration
cases:

```text
p_valid(s) = (positive calibration cases with score s + 1)
             / (all calibration cases with score s + 2)
```

An unseen score uses the same smoothed calibration-wide fraction for that
method. The lookup is serialized canonically and hashed before confirmatory
scoring. `M1-no-calibration` uses binary `p_valid` equal to its decision and
does not fit or read the calibration lookup. Its
`calibration_lookup_sha256` field is instead the SHA-256 digest of the exact
UTF-8 marker `E003-v1|calibration_lookup|M1-no-calibration|none`; this is a
no-lookup marker, not a fitted lookup.

## Independent reference oracle

The oracle is a separately maintained, fail-closed evaluator of the E003
contract. It is not B0, M1, an ablation, or the mutation generator. It must
use distinct source code, field-path declarations, relation calculations, and
immutable constants; it may not import or call a method checker, share a
predicate/table/object, or read method output. It receives only the candidate
event payload and returns `schema_valid`, `truth`, and an ordered
`oracle_failure_set` from `{schema, identity, state}`.

The oracle calculates identity by parsing URL path components and comparing
normalized resource repository/number components to the top-level repository
and event number. It calculates state from a separate action-to-allowed-state
table, including the merged pull-request condition. It labels truth 1 only if
the three oracle families all pass. It never reads `variant_id`, intended
failure, split, source metadata, or method labels.

Independence gates require source inspection and two perturbation probes: a
method predicate/table alteration must leave oracle output unchanged, and an
oracle relation alteration must leave method output unchanged. The runner
must also prove that a validator call cannot access oracle-only metadata. This
is structural independence under a shared external contract, not proof that
the documented subset is a perfect ground truth.

## Metrics and uncertainty

The positive class is `truth=1`. Compute support, TP, TN, FP, FN, balanced
accuracy, FPR, FNR, Brier score, and ten-bin equal-width ECE for every method
on each split and each exact subgroup:

```text
overall
type:IssuesEvent
type:PullRequestEvent
```

Bins are `[0.0,0.1), ..., [0.9,1.0]`, with `1.0` included only in the final
bin. Empty metric denominators serialize as `NA`; they are never replaced with
zero. Brier is the mean squared probability error, and ECE is the support-
weighted absolute difference between bin mean confidence and valid frequency.
For each method, `support = positive_count + negative_count`, `TP` and `FN`
are counts among `truth=1`, and `TN` and `FP` are counts among `truth=0`.
Define `BA = (TP/(TP+FN) + TN/(TN+FP))/2`, `FPR = FP/(FP+TN)`, and
`FNR = FN/(FN+TP)`. `BA` is `NA` if either class denominator is zero;
`FPR`/`FNR` are `NA` when their respective denominator is zero; Brier and ECE
are `NA` when support is zero. The method and pair rows preserve these exact
counts and the denominator-reconstructing fields.

The primary confirmatory analysis reports paired M1-minus-B0 deltas for BA,
FPR, FNR, Brier, and ECE. The result report separately records acceptance or
rejection rates for `clean`, `S1`, `I1`, and `T1`, plus the three ablation
methods; these summaries are not additional metric rows. They are descriptive
and cannot upgrade H3.

### Paired repository bootstrap

Use the repository ID as the resampling unit because all variants of a base
event are paired and events from a repository are not independent. Sort the
confirmatory repository IDs numerically. Let `B` be the number of selected
confirmatory repositories; the feasibility gate requires `B >= 24`. For each
replicate `r` from 0 through 9,999 and position `j` from 0 through `B-1`,
compute:

```text
index = int(SHA256("E003-v1|bootstrap|<subgroup>|<metric>|<r>|<j>").hexdigest(), 16) mod B
```

Select the repository at `index`, with replacement, preserving all its base
events and four variants. Recompute paired method metrics on that resampled
case multiset. Store the delta, not a rounded intermediate. Sort the `n`
usable deltas and define percentile `q` by linear interpolation at
`h=(n-1)q`: use the value at `floor(h)` when `h` is integral, otherwise use
`(ceil(h)-h)*x[floor(h)] + (h-floor(h))*x[ceil(h)]`. The 95% interval is the
2.5th and 97.5th percentile of the 10,000 usable deltas. A degenerate interval
is reported as degenerate; it is not hidden or interpreted as population
certainty. Required interval blocks are:

```text
overall × {balanced_accuracy, fpr, fnr, brier, ece}
type:IssuesEvent × {balanced_accuracy, fpr, fnr, brier, ece}
type:PullRequestEvent × {balanced_accuracy, fpr, fnr, brier, ece}
```

The planned bootstrap artifact has 150,000 data rows plus one header. The
actual source-selected cluster count may vary above the minimum; the exact
count is recorded in the future result and does not alter the fixed replicate
count or hash rule.

## Artifact schemas and output boundary

The following paths are future output names only. None exists in this
protocol-only task, and no E003 output may be committed as part of the protocol
lock:

```text
data/E003-v1-predictions.jsonl
data/E003-v1-metrics.csv
data/E003-v1-bootstrap.csv
experiments/E003-external-transfer-validation/results/run-<run_id>.md
```

Raw source files and the acquisition manifest remain outside Git. All output is
UTF-8/LF, deterministic, and written only after read-only preflight.

### Prediction JSONL

One canonical JSON object per `(split, base event, variant, method)`, ordered by
`split_rank`, `event_type_rank`, `repo_id_integer`, `event_id_integer`,
`variant_rank`, and `method_rank`. The exact keys are:

```text
protocol_id, run_id, source_file, source_sha256, source_line, split,
repo_id, event_id, event_type, base_event_id, variant_id, case_kind, truth,
oracle_failure_set, schema_valid, method, decision, raw_score, p_valid,
input_sha256, source_manifest_sha256, calibration_lookup_sha256, status
```

`truth` and `oracle_failure_set` are evaluator metadata written after scoring;
they are never passed to a method. `oracle_failure_set` is an ordered list
with the exact family order `schema, identity, state`; empty is `[]`.
`decision` and `schema_valid` are booleans, `raw_score` is a nonnegative
integer, `p_valid` is a finite decimal in `[0,1]`, and all hashes are 64
lowercase hexadecimal characters. `source_sha256` is the raw gzip-byte digest
from the frozen source manifest. `input_sha256` is the SHA-256 digest of the
canonical UTF-8 JSON bytes, including the LF terminator, supplied to the
method; it excludes split, truth, variant, oracle, source-line, and other
evaluator metadata. For `M1-no-calibration`, the calibration hash is the
no-lookup marker digest defined above. No actor login, issue title, comment
body, or other raw text is serialized.

### Metrics CSV

The exact header is:

```text
row_kind,run_id,protocol_id,source_manifest_sha256,split,subgroup,method,method_pair,variant_scope,support,positive_count,negative_count,tp,tn,fp,fn,balanced_accuracy,fpr,fnr,brier,ece,delta_ba_ci_lower,delta_ba_ci_upper,delta_fpr_ci_lower,delta_fpr_ci_upper,delta_fnr_ci_lower,delta_fnr_ci_upper,delta_brier_ci_lower,delta_brier_ci_upper,delta_ece_ci_lower,delta_ece_ci_upper,interval_status
```

There are 45 `method` rows (5 methods × 3 splits × 3 subgroups) and 9
`pair` rows (M1-B0 × 3 splits × 3 subgroups), for 54 data rows. Method rows
have `variant_scope=all` and `method_pair=NA`; pair rows have method metrics
`NA` where not applicable and exact M1-B0 delta fields. The confirmatory pair
rows carry the five required interval pairs; all undefined or partial values
are literal `NA` with an explicit status.

### Bootstrap CSV

The exact header is:

```text
run_id,replicate,subgroup,metric,method_pair,delta,status
```

Rows are ordered by replicate, subgroup rank, and metric rank, with subgroup
order `overall`, `type:IssuesEvent`, `type:PullRequestEvent` and metric order
`balanced_accuracy`, `fpr`, `fnr`, `brier`, `ece`. The only method pair is
`M1-B0`; `status` is `available` for a finite delta and `undefined` otherwise.

### Result report

A valid report must state protocol ID/path and lock commit, source-manifest
hash, all three source hashes, run ID, environment, exact selected counts,
exclusion counts, all gate statuses, calibration lookup hashes, primary
confirmatory point deltas and intervals, H3 outcome, secondary mutation and
ablation summaries, artifact hashes, deviations, limitations, and the exact
stopping statement. It is finalized last and its own SHA-256 is computed only
externally after finalization.

On any failure, the only permitted result-path record is:

```text
# E003-v1 invalid run — <RUN_ID>
status: invalid
protocol_id: E003-v1
protocol_commit: <40 lowercase hex>
run_id: <RUN_ID>
failure_class: invalid-run
No metrics or evidence exist.
corrected_run_requires_new_id: true
```

The invalid record contains no metric table, interval, source claim, or
evidence-like language. A run ID has the exact form
`e003-YYYYMMDD-NNN`; existing files and IDs are never overwritten.

## Runtime and sanity gates

All gates run before confirmatory metrics are presented or final output is
made visible:

1. Verify the exact protocol bytes/identity, required future lock ancestry,
   clean tracked and untracked worktree, run-ID grammar, output-path absence,
   and source-manifest presence. No output directory is created before these
   checks.
2. Verify all three frozen gzip hashes and parse the complete JSONL streams;
   assert exact URL, byte, line, and manifest values and no network after the
   manifest is frozen.
3. Build the canonical source projection twice and compare bytes, line maps,
   IDs, repository keys, and exclusion counts.
4. Assert the common/event-specific schemas, unique event IDs, URL formats,
   status-action eligibility, source-contract counts, and all independent
   oracle outputs.
5. Assert repository group isolation across shards and exact 64+64 base
   quotas, per-repository caps, minimum repository counts, 512 cases per
   split, and no duplicate base hash.
6. Apply S1/I1/T1 from independent deep copies; assert exact mutation
   footprints, schema behavior, and exactly one oracle family for every
   negative variant.
7. Prove method/oracle and method/label separation by static inspection and
   runtime probes. Mutate a method predicate and an oracle predicate in
   separate probes and require the other side's output to stay unchanged.
8. Assert B0 does not inspect identity/state relations, M1 does, the ablations
   retain exactly their named family, and no method reads labels or source
   metadata.
9. Score calibration cases once, serialize and hash every lookup, freeze the
   lookups, then score confirmatory cases. A calibration hash change aborts.
10. Verify every prediction key, row count, metric row count, bootstrap row
    count, order, boolean/decimal/NA policy, finite probability, and output
    allowlist. Rebuild the complete in-memory pipeline twice and compare all
    canonical bytes before finalization.
11. Verify the bootstrap has exactly 10,000 usable replicates for each required
    block and that all required intervals are defined. Partial required
    intervals cannot support H3.
12. Enforce an implementation-planned size envelope before writes: predictions
    under 8,000,000 bytes, metrics under 500,000 bytes, bootstrap under
    20,000,000 bytes, and report under 50,000 bytes. These are safety limits,
    not observed artifact sizes.

The development suite must not construct or print confirmatory metrics. The
future confirmatory CLI is the only operation allowed to create the four final
E003 output paths.

## Invalid-run, staging, and stopping rules

The future runner requires an explicit run ID and external source-manifest
path. It refuses dirty or untracked trees, missing/mismatched source hashes,
protocol identity drift, missing quotas, duplicate IDs, oracle/mutation drift,
calibration leakage, existing outputs, and size/determinism failures. It must
write to a uniquely named temporary staging directory, fsync data, finalize
predictions/metrics/bootstrap first, and finalize the result Markdown last.

On any failure after staging begins, remove the staging directory and any
final files made by this invocation. If cleanup is verified and the result path
was absent at entry, write only the concise invalid-run record. If cleanup
cannot be verified, the run is invalid and no valid-looking result may remain.
A corrected attempt requires a new run ID, a new separately authorized gate,
and, if the protocol or source changes, a new protocol version.

The E003 stopping rule is one valid confirmatory run and verification of its
four artifacts, followed by stop. Do not add source shards, event types,
actions, mutations, thresholds, retries, post-hoc subgroups, or live API
checks. A valid `mixed/not supported` outcome is the terminal E003-v1 outcome;
it is not a reason to expand the run.

## Limitations and source boundary

- GH Archive is one public GitHub ecosystem and three historical hourly
  shards, not a representative sample of all real-world structured data.
- The source records are externally authored, but the negative cases are
  deterministic mutations and the clean positives are filtered by the
  protocol's oracle. Natural invalid prevalence and naturally occurring error
  rates are not estimated.
- The effective contract is a deliberately narrow subset of evolving event
  payloads. Excluding unknown historical shapes can hide failure modes; the
  exclusion counts must be reported.
- E003 tests event-level action/resource-state relations, not a complete issue
  or pull-request event history. It does not assert a global transition graph.
- The independent oracle and M1 share the selected external contract, so
  structural separation does not remove shared-specification risk.
- Repository group bootstrap intervals describe this finite selected sample;
  they are not population uncertainty or external-validity proof.
- Public raw data are kept outside Git and no actor identity or raw text is
  emitted. License, terms, and redistribution review are a future acquisition
  gate, not silently assumed here.
- No production, safety, novelty, generalization, or public-claim eligibility
  follows from E003. `public_claim_eligibility` remains `false`.

## Current stopping gate

The only action authorized in this task is local protocol/state/documentation
work. The three source files are **not acquired**, E003 is **not implemented**,
no E003 run or result/data/code exists, and no external or public action is
authorized. The next future gate is separate authority for source acquisition,
independent implementation review, and exactly one confirmatory execution.
