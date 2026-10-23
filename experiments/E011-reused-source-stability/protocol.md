# E011-v1 — stability on reused external source tables

Date: 2026-10-23. Classification: exploratory_reused_source_stability_study.
E006 source rows and outcomes have previously been inspected. E008--E010 results
are known. No E011 implementation, target selection or computation exists at
lock. This is not pristine holdout evidence or detector-accuracy improvement.

## Questions and fixed predictions

Do mutable context keys change exact stability radii on the three fixed source
tables, and does decision stability differ from reference correctness?

H11a (empirical): at least one initially accepted target in the complete study
universe has a smaller mutable-key radius than its fixed-key radius.
H11b (empirical): at least one selected initially rejected target in the two-key
Rayyan journal_title task has a strictly smaller full radius, when both solves
are certified optimal. A timeout gives no support or refutation for that target.
H11c (mathematical check): no accepted target without singleton target groups
has a radius reduction; all concrete finite witnesses flip at the reported cost.
H11d (empirical): at least one initially accepted target differs from its
reference value despite a full radius>=2. This is an existence check illustrating
that robustness is not correctness, not a correlation or calibration claim.

Empirical predictions may fail; retain a valid negative outcome. There is no
seed, rule or target replacement after outcomes, and no population inference.

## Fixed source and exact task universe

Use the same nine pinned E006 files, source root
/Users/mac/Library/Caches/InvariantAudit/E006-v1-20261022/source,
repository revision 7be1334b8c7bbdac3f47ef514fb3e1e8c5fc181c. Committed manifest
data/E006-v1-source-manifest.json SHA-256
96e7529355eac100de47f2c957b8a1a5252d4c220c285d5fd46d871d62716342.
Verify all nine hashes/sizes before CSV parsing. No download, replacement or
source alteration. The historical A1 failure and A2 header aliases stay unchanged.

Parse UTF-8 with strict csv.reader, skip only fully empty rows, reject ragged
rows. Normalize exactly by html.unescape, collapse runs of tab/newline/ASCII
space to ASCII space, and strip those three characters. Preserve all other
characters/case. Apply the two manifest Beers clean header aliases only. Require
the manifest headers, >=100 rows, equal dirty/clean shapes, and nonempty unique
alignment keys equal positionally: beers index, flights tuple_id, rayyan id.

Fixed tasks, in this order:

- beers: brewery_id -> brewery_name; brewery_id -> city; brewery_id -> state.
- flights: flight -> sched_dep_time; flight -> act_dep_time;
  flight -> sched_arr_time; flight -> act_arr_time.
- rayyan: jounral_abbreviation -> journal_issn;
  {jounral_abbreviation -> journal_title, journal_issn -> journal_title} jointly.

Thus nine tasks, with one target RHS cell for every source row in each task.
Project only the task's determinant union and RHS. Every context row in the
full source table participates; no split/subsampling of context. The entire
projected target row is protected. Context keys and RHS are independent unit-cost
editable cells. Acceptance requires the target RHS to be a unique plurality in
every applicable target group; ties reject.

Empty strings are ordinary categorical values here, including determinant
empties; there are no missing-value or unary-format rules. This differs from
E006 Rmode/U and must not be called the same detector or pooled with its metrics.
No FD discovery, reference-informed filtering or input corruption is added.

Encode dirty categorical strings by sorted unique values separately per column.
Use at least two allowed symbols per column, adding one abstract alternative
only when a dirty column is monomorphic. For each target, swap its code with 0
in each projected column. Other nonzero values remain distinct. No dictionary
of source cell strings or clean values enters published outputs. Witnesses use
original row/column coordinates and target-relative destination integer codes.

## All initially accepted targets

For every accepted target compute full and fixed-key radii. Use E010's pinned
generalized accepted_formula for the full result; SHA-256 of its models.py:
c99a7b0bb17929891aa71eb48d8fa59300f7d87b7286707063217f143e8a58f6.
Its imports also require the E009 generic_milp.py pin from E010. The fixed-key
formula is the minimum ceil((target_count-largest_rival_count)/2) over
nonsingleton target groups, INF if none. Export concrete finite witnesses,
group sizes and all radii. Check actual cell cost and direct raw decision flip,
not merely the formula's return code. Verify fixed witnesses never edit keys.

Calculate the entire accepted-target stage twice before any reference rows are
parsed and require byte-identical decisions/radii/witnesses (exclude no outcomes;
do not export formula timing fields). Dirty source rows were seen historically;
this staging is computational label isolation, not restored blindness.

## Bounded initially rejected subset

Within each task, sort all rejected row coordinates by
SHA256('E011-v1|rejected|dataset|task_RHS|one_based_row_index') hexadecimal digest,
then row index; select the first four, or all if fewer. No reference labels
are used. Record full rejected counts, selected IDs/hashes and selection rate.
Do not report this subset as representative of all rejected targets.

For each selected target solve the full and fixed-key accepting problems once
each, in that order, with an exact canonical-action MILP. Full actions are the
E008/E010 supermask/submask reduction. Fixed-key actions restrict each row's
mask to its original one, so a nonzero RHS may stay or change to target 0;
an original 0 stays unchanged. Same unit Hamming objective and one action per
row. Never copy the full-method optimum into the fixed-method model.

Sparse active-rival reduction: for each rule constrain only nonzero RHS values
present in that rule's original target group. A canonical unchanged nonzero RHS
can only leave groups; all other canonical RHS changes go to 0. Thus a rival
absent from a group cannot appear there, while its target count remains >=1.
Its omitted inequality is automatically satisfied. This is a specialization
of the existing dominance proof, not an approximation. State this proof and
preflight it before source execution. Do not merge distinct nonzero rivals.

Runtime: Python 3.13.5, NumPy 2.1.3, SciPy 1.17.1; scipy.optimize.milp options
presolve=True, mip_rel_gap=0.0, time_limit=5.0 seconds per solve. No warm starts,
extra solver options, retuning or retry. Record status, objective, dual bound,
gap and primal/witness when available. Require raw cost, domain, target, linear
and integrality checks <=1e-7. Status 0 is exact only with feasible checked
primal and matching optimal bound/gap. Status 1 is censored even if its incumbent
matches the other method. All tasks have finite accepting edits; 2/3/4 are
unexpected errors, retained as validation failures. Do not replace a timeout.

## Preflight and reference labels

Before parsing any study source row, run all 162 E010 fixtures (pinned design.py)
against unrestricted raw destination enumeration and a separate fixed-key
RHS-only enumeration. For accepted targets check both formulas; for rejected
targets check full and fixed sparse-action MILPs. Every finite witness must
verify. Require exact objective equality or correctly predicted fixed-key INF.
Any failure stops source execution and saves failed-preflight evidence.

Freeze the complete dirty-only decisions, accepted radii/witnesses and selected
rejected results by SHA-256 before parsing clean CSV rows. Then align references
and label target correctness iff normalized dirty RHS equals normalized clean
RHS at the same coordinate. No reference-dependent optimization or target changes.

Report, separately per task: total/accepted/rejected counts; singleton presence;
full and fixed radius distributions; strict finite decreases and fixed-INF to
finite transitions; selected-rejected exact-pair denominators and timeouts.
For all accepted targets tabulate reference correctness by full-radius buckets
1, 2, >=3, INF, including empty buckets. Never pool the rejected sample with
the complete accepted universe. These are finite counts with no bootstrap,
significance, calibration or population-prevalence claim.

## Transaction and artifacts

Protocol commit before implementation commit before one run
e011-20261023-001. Guard source/module/protocol/runtime pins and refuse existing
destinations. On a validation failure preserve the failed record; never relabel
it a successful study. Save coordinate-only outputs:

- data/E011-v1-preflight.json.gz;
- data/E011-v1-targets.jsonl.gz (every target decision; accepted radii/witnesses;
  reference labels attached after dirty-stage freeze);
- data/E011-v1-rejected-solves.jsonl.gz (every selected target/method/status);
- data/E011-v1-summary.csv;
- data/E011-v1-reference-buckets.csv;
- data/E011-v1-checks.json;
- experiments/E011-reused-source-stability/results/run-e011-20261023-001.md.

Do not modify previous studies, manuscript/PDF, M22 archive or unrelated user
files. This reused-source study and theorem-level prior-work comparison will
inform a contribution-centered manuscript; source outcomes do not prove novelty.
