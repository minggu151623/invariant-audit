# E014: does the width factor survive at larger optima?

2026-11-10. The owner decided to post R4 on Zenodo and asked for one more
review of the paper, with rewriting where needed. The review found that the
first open question in R4 ("is the factor w(F) attained with rho_full = k for
every k?") has a short analytical answer. This protocol fixes the finite check
of that answer. It is committed before any implementation or execution.

No publication or license authority is inferred. E001–E013, R3 and the
preserved artifacts stay unchanged. All statements below were derived by an AI
session in this project; no independent review exists.

## Analytical hypotheses derived before the finite check

Model as in E013: protected all-zero target, common RHS with d values,
unit-cost independent cell edits, ties reject, every listed check must accept,
initially rejected target. w, w_j and F_j are as in E013.

**H14a (every scale, enough RHS values).** Let k >= 1 and d >= k+1. Choose
the smallest key j with w_j = w and the lexicographically first maximum
antichain A_1,...,A_w of F_j. Build a table with binary keys:

- for each i and each value v in {1,...,k}: k rows with RHS v and zero-key
  mask exactly A_i (k*k rival rows per critical group);
- k rows with RHS 0 and every key zero except j;
- for each rule C that contains no A_i: w*k rows with RHS 0 and zero-key mask
  exactly C.

Prediction: rho_full = k and rho_fixed = w*k exactly.

Proof sketch. The group of A_i is the target plus its own k*k rivals, so each
rival value has k votes against one zero. Other checks accept: no rival at
all, or at most w*k rivals of a value against w*k+1 zeros. Setting key j of
the k zero rows to 0 gives every critical group k+1 zeros: rho_full <= k. With
fixed keys, fewer than k changed cells in one critical group leave some rival
value with all k rows, while zeros number at most k; so each group needs k
changes of its own, and one flip to 0 per value suffices: rho_fixed = w*k. The
exchange bound then gives rho_full >= k.

**H14b (binary RHS can fall short).** For d = 2 and F = {{0,1},{0,2}}, every
table with an initially rejected target has rho_fixed <= rho_full + 1. So the
factor 2 is attained only at rho_full = 1.

Proof sketch. Take a normalized optimal editable-key witness with R RHS edits
and K key edits, and apply the R edits. Let n_X = max(0, 1 - margin of X).
Key edits only add RHS-0 rows to groups, one margin unit per added row, and
each added row has at least one key edit, so n_X <= K. With fixed keys,
flipping ceil(n_X / 2) rivals of the group of X closes its deficit. Hence
rho_fixed <= R + 2*ceil(K/2) <= R + K + 1.

Both are conjectures until checked and reviewed. The finite check proves no
universal statement and no historical originality.

## Solvers

1. **Row dynamic program (both edit models).** Rows are processed one at a
   time. A state is the vector of margins m_{X,v} over rules X and rival
   values v. Each row may move to every destination allowed by the edit model
   (editable keys: every combination of key and RHS values; fixed keys: the
   original keys with every RHS value) at its Hamming cost. Destinations with
   the same contribution vector are merged, keeping the least cost. States
   costlier than a directly verified accepting witness are dropped. The
   program uses no normalization, exchange, bound or action reduction.
2. **Raw bounded enumeration (Part A).** Every set of changed context cells of
   size at most k-1 (editable keys) and at most w*k-1 (RHS cells only), with
   every alternative domain value, is evaluated by counting votes directly from
   the definition. None may accept. It runs for a case and edit model only if
   the number of edited tables is at most 10^7; the count is recorded either
   way.
3. **Raw full enumeration (Part B, at most three context rows).** Every
   destination table is evaluated by direct counting for both edit models.
   The minima must equal the dynamic program's values.

The stated witnesses of cost k and w*k are also evaluated by direct counting.
Width is computed by exhaustive antichain search.

## Locked domains

Keys are numbered from 0. No randomness and no outcome-based selection.

**Part A (construction).** Cases (family; q; k; d):

| Case | Family | q | k | d |
|---|---|---|---|---|
| A1 | {0,1},{0,2} | 3 | 1 | 2 |
| A2 | {0,1},{0,2} | 3 | 2 | 3 |
| A3 | {0,1},{0,2} | 3 | 2 | 4 |
| A4 | {0,1},{0,2} | 3 | 3 | 4 |
| A5 | {0},{0,1},{0,2} | 3 | 2 | 3 |
| A6 | {0,1},{0,2},{0,1,2} | 3 | 2 | 3 |
| A7 | {0,1},{0,2},{1,2} | 3 | 2 | 3 |
| A8 | {0,1},{0,2},{0,3} | 4 | 2 | 3 |
| A9 | all seven nonempty subsets | 3 | 2 | 3 |

Predicted (rho_full, rho_fixed) = (k, w*k) in every case.

**Control (the condition d >= k+1 matters).** Family {0,1},{0,2}, q = 3,
d = 2: each critical group gets two rows with RHS 1, and there are two rows
with RHS 0 and every key zero except key 0. Prediction: (rho_full, rho_fixed)
= (2, 2), not (2, 4).

**Part B (binary bound).** q = 3, binary keys and RHS, F = {{0,1},{0,2}},
every multiset of one to six context rows (74,612 tables). For every
initially rejected table both radii are computed by the dynamic program.
Predictions: rho_fixed <= rho_full + 1; rho_fixed <= 2*rho_full; equality
rho_fixed = 2*rho_full only when rho_full = 1. The cross-tabulation of
(rho_full, rho_fixed) is recorded. Tables overlap heavily and are not
independent replications.

## Outputs and failure handling

The implementation is committed before execution. A summary records protocol
and code hashes, the implementation commit, per-case rows, radii, evaluation
counts and the Part B cross-tabulation. On any mismatch the run halts and the
counterexample is kept; a fix needs a new commit and a separately kept run.

Success: every prediction above holds on the locked domains. There is no
timing target and no source-data claim. Passing does not by itself change the
status of the manuscript.
