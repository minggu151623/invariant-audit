# E006-v1 — Rule attribution and probability scores against external references

Date: 2026-10-22. Classification: `predeclared_external_reference_validation`.
Source selection, published examples/results and CSV headers have been seen;
paired table rows, reference differences and candidate outcomes have not been
inspected. This is not a wholly blind study and does not rerun or validate
E003. The design is AI-proposed under the continuing user arXiv research goal.

## Question and fixed predictions

How do simple fixed constraint checkers behave when correctness is defined by
outside reference corrections, rather than the checker contract? Does empirical
lookup help probabilities when binary decisions are imperfect? Does attributing
a dependency violation to every involved cell differ from targeting a minority
right-hand-side value? This is a case-study extension, not a new algorithm or a
replication/comparison with the Raha system. Published prior work already notes
that involvement in a violation does not necessarily make a cell erroneous.

H6a: Rall makes at least one FP or FN against the external reference in each of
the three fixed datasets (finite point observation, not a population test).
H6b: Rmode lookup-minus-binary Brier has a strictly negative upper paired 95%
cluster-bootstrap endpoint in every dataset, with all 10000 replicates usable.
H6c: Rmode-minus-Rall FNR has a strictly negative upper paired endpoint in every
dataset, with all 10000 replicates usable. Report the accompanying FPR/BA tradeoff.
Each is separately supported or mixed/not supported; no pooled success label.
All other comparisons are descriptive and no multiplicity-adjusted population
significance claim is made. These predictions are design expectations, not
required validity gates. Valid contrary evidence must be retained.

## Frozen source and metadata

Use only the nine original files at
/Users/mac/Library/Caches/InvariantAudit/E006-v1-20261022/source/.
External manifest and committed mirror data/E006-v1-source-manifest.json must
match SHA-256 `96e7529355eac100de47f2c957b8a1a5252d4c220c285d5fd46d871d62716342`.
Source repository revision: 7be1334b8c7bbdac3f47ef514fb3e1e8c5fc181c.
Verify every source pin before parsing. Never download, substitute, rewrite or
repair sources during evaluation. A1 stays invalid; A2 applies exactly two
Beers header aliases and otherwise preserves original names and byte streams.
CSV source bodies remain outside Git; output contains coordinates, not cell text.

The paper describes Beers as manually cleaned and Rayyan as owner-cleaned;
Flights has an externally supplied reference. These references are independent
of this project's validators, not guaranteed infallible. They supply benchmark
cell-correction labels; no claim that every error was naturally generated.

## Parsing, normalization and alignment

Use strict Python csv.reader on UTF-8, first logical row header, skip only
fully empty logical rows, and require every remaining row to match header
width. Preserve original one-based data-row coordinates. Apply only A2 aliases
to Beers clean headers. Both headers must then match the locked manifest.
No column dropping, row selection, extra negative injection or oracle filtering.

Normalize every cell exactly as the pinned Raha dataset.py value_normalizer:
html.unescape, replace runs of tab/newline/ASCII space by one ASCII space, then
strip these three characters. Retain case, carriage returns, other Unicode
whitespace and strings such as 'nan'. No lowercasing, type inference or NA fill.
Truth=valid=1 precisely when aligned normalized dirty and reference strings are
equal. All other cells have truth 0. The unit is a cell, not a record.

Require paired row counts and shapes to match. Fixed alignment key is Beers
index, Flights tuple_id, Rayyan id. Require those keys to be nonempty, unique
and equal at every aligned position. A key mismatch stops the run; no fuzzy
matching or sorted realignment. Exclude that key column from the evaluated
cell universe, but no other columns. This checks positional reference alignment
under a stable-key assumption, not every possible semantic labeling error.
Require at least 100 source rows per dataset. Otherwise preserve invalid result.

## Fixed constraints (published context, explicit implementation choices)

Dataset-specific dependency inventory, chosen from the outside paper's check
configuration, with source spelling retained:

- Beers: brewery_id -> brewery_name, city, state (three unary-determinant FDs).
- Flights: flight -> sched_dep_time, act_dep_time, sched_arr_time, act_arr_time.
- Rayyan: jounral_abbreviation -> journal_title, journal_issn; journal_issn -> journal_title.

No inferred extra FD or threshold is allowed. Rules receive normalized dirty
strings only. A row with an empty determinant does not participate in that FD.
Empty dependent values do participate. A conflict means at least two distinct
observed dependent values for one determinant in the current split.

U checks each evaluated cell is nonempty. It additionally requires Beers
brewery_id to match ASCII [0-9]+ and state to match ASCII [A-Za-z]{2}. These are
explicit limited unary checks, not a complete schema language or domain oracle.
No other format/range/date rule is included; do not tune this inventory.

Four fixed base methods, raw_score = count of their triggered unary/FD checks:

1. U: unary checks only (at most two flags on a Beers cell).
2. Rall: U plus each conflicting FD flags its determinant and dependent cells
   in every row of the conflicting group. It never flags unrelated columns.
3. Rrhs: U plus each conflicting FD flags only dependent cells, in every row.
4. Rmode: U plus a conflicting FD flags dependent cells whose value is not the
   unique most frequent value. A modal tie flags every dependent cell in that
   group. No clean value is consulted to choose the modal value or break a tie.

Decision=valid iff raw_score=0. These simple transparent baselines are neither
new methods nor the original E001/E002 M1. Different tasks/methods prevent a
causal claim that moving the original M1 to external data caused a performance
change. Test the narrower probability/attribution questions directly.

## Dirty-only grouping and splits

Within each dataset, form connected components of rows sharing a nonempty
value in any FD determinant column. Union transitively across determinant
columns. The component identity is the lexicographically smallest alignment
key (UTF-8 string ordering), stored in outputs only as SHA-256(component key).
Every row, including a singleton with missing determinants, receives a component.
Assign a component using int(SHA256('E006-v1|split|dataset|component_key'),16)%4:
0/1 development, 2 calibration, 3 evaluation. No balancing or retry by seed.

Dirty-only scoring may use all dirty rows of the current split to detect FD
conflicts; this is a transductive diagnostic setting, disclosed as such. No FD
determinant group or component can cross splits by construction. Under erroneous
keys, true-world entity separation is not guaranteed. Require at least 8
components in calibration and evaluation and both truth classes in evaluation.
No labels are used in component/split construction or scoring. Development is
descriptive only; there is no tuning. Calibration outcomes never change a rule,
score, decision, component, bin or split.

Freeze raw scores/decisions for all splits and their SHA-256 before reference
label comparison. Then fit four lookups only on calibration cells, per dataset
and method, pooled over all evaluated columns: p_valid(s)=(k_s+1)/(n_s+2), with
global calibration fallback (k+1)/(n+2) for unseen scores. Freeze lookup hashes
before computing evaluation metrics. Each base method also has a binary
probability ablation p_valid=decision; there are eight metric method identities.
Evaluation reference changes must not alter raw scores or calibration lookups.

## Metrics and decomposition

Report per dataset, split, method and fixed scope: all evaluated cells, and
FD endpoint columns (the union of determinant/dependent columns, excluding key).
Lookup fitting remains over all cells; scope never changes probabilities.
Compute TP/TN/FP/FN, BA, FPR (invalid accepted), FNR (valid rejected), Brier,
ten-bin positive-class ECE with [i/10,(i+1)/10), p=1 in final bin, and exact-score
REL/RES/UNC as in E005. Undefined denominators are NA, not zero. Point metrics
use unrounded p lookup fractions; exported 12-place probabilities may differ
only within declared rounding tolerance 2e-12. Validate finite Brier identity
numerically to 1e-12 (group by exact lookup fraction, not rounded floats).

Compute outputs by two implementations: the new primary implementation and a
standard-library direct cellwise checker for point metrics. Differences must
be <=2e-12 for probabilities/scores and counts must agree exactly. This is a
separate implementation by the same agent, not independent reviewer acceptance.

## Paired component bootstrap (evaluation/all-cells only)

10000 replicates. Sort evaluation components by their stored 64-character
identity. For dataset d, replicate r, position j (zero based), draw index
int(SHA256('E006-v1|bootstrap|d|r|j'),16)%B, where B is the number of components.
The same B sampled components/multiplicities are used for every method and
comparison in that replicate. All cells of a component remain together.
Record a hash of draw indices in canonical r/j order; no seed search.

Pairs and metrics are fixed:
- Rall-U, Rrhs-U, Rmode-U, Rmode-Rall (lookup methods): BA, FPR, FNR, Brier, ECE.
- Each of U, Rall, Rrhs, Rmode lookup minus its binary variant: Brier, ECE.
Thus 28 intervals per dataset, 84 overall. Percentiles 0.025 and 0.975 use
linear interpolation. Missing-denominator replicates are NA and counted;
intervals show valid/partial/undefined/degenerate. Support claims require all
10000 usable replicates; partial intervals do not invalidate otherwise valid
point evidence. Intervals describe the fixed benchmark grouping, not a sampled
population; no cross-dataset pooled interval or multiplicity-adjusted claim.

## Implementation, evidence and stopping

Local CPU only, Python standard library plus already installed NumPy; no
package installs, ML fitting, external API/GPU or network during evaluation.
Record Python/NumPy versions and implementation commit. No E003 source access
or gate changes. Before data execution, synthetic tests must cover constraint
attribution, ties/empty determinants, normalization, key misalignment, component
isolation, calibration fallback, evaluation-label perturbations, independent
point-metric known answers, bootstrap pairing/draw known answers, output refusal,
late publication failure and locked source/protocol drift.

Commit protocol separately before implementation/results, commit implementation
before the single run e006-20261022-001. Verify lock ancestry and exact committed
implementation bytes. Build predictions, aggregate rows and all output bytes
twice using cached fixed sources; compare bytes. No partial valid report.
Publish report last via exclusive writes; rollback only this run's owned files
on failure and preserve a concise invalid record. No retry, new seed, replacement
source, reference edit or scientific-rule adjustment after seeing outcomes.

Outputs as a single provenance-linked set:
- data/E006-v1-predictions.csv.gz (coordinates and four base scores/probabilities;
  explicit p_lookup and p_binary columns; no source cell strings).
- data/E006-v1-metrics.csv (144 point rows).
- data/E006-v1-bootstrap.csv.gz (840000 replicate rows; 84 blocks x 10000).
- data/E006-v1-intervals.csv (84 intervals).
- data/E006-v1-checks.json (source/lock/implementation identities, row/split/label
  counts, score/lookup hashes, draw hashes, diversity and numerical audit).
- experiments/E006-external-reference-validation/results/run-e006-20261022-001.md.

Size limits: predictions 20 MB compressed/150 MB uncompressed, bootstrap 20 MB
compressed/150 MB uncompressed, metrics 1 MB, intervals 1 MB, checks 1 MB, report
100 KB. Export gzip with mtime=0 and no source filename; sorted UTF-8/LF rows.
Fixed hypotheses, all nulls and failures are reported. One valid run then stop
and reflect on the manuscript. Independent scientific acceptance, owner review,
public-release rights and submission remain separate gates.
