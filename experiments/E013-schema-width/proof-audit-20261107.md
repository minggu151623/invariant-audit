# E013 proof re-audit

2026-11-07. Second line-by-line reading of `theory.md` by a different agent
session than the one that wrote it. Still an AI self-review inside the same
project, not independent human peer review. No new computation was run.

## Scope

The handoff asked for scrutiny of (a) the capped invariant, (b) the
noncritical groups in the tightness construction, (c) domain/cost assumptions.
All three plus Lemma 1 and Corollary 4 were re-derived. No error was found.
Points worth stating more explicitly in a manuscript are listed below.

## Lemma 1 (normalization)

Case split re-checked exhaustively over (r.y = 0 or not) x (u.y = 0, = r.y,
other nonzero) x (keys changed or not):

- r.y != 0, u.y = r.y, keys unchanged: u = r, form 1.
- r.y != 0, u.y = r.y, some key changed: H(r,u) >= 1 = H(r,c) for c = (keys of
  r, y = 0). Contributions of c are >= 0, those of u are <= 0. Form 2.
- All remaining cases: c.y = 0 with zero mask M(r) U M(u). The only key cells
  c changes are in M(u) \ M(r), which u also changes. The y cost of c is 0 if
  r.y = 0, else 1, and in the latter case u.y != r.y, so u also pays 1.
  Domination: if u.y = 0, M(c) contains M(u); otherwise u's contributions are
  nonpositive. Includes r.y = 0 with u.y != 0 (c strictly cheaper).

Margins are sums over rows, so rowwise replacement is valid. Duplicated rows
and arbitrary categorical domains are handled; no fresh value is needed.

## Theorem 2 (exchange)

- Ordering: all y edits first, so every key edit of H occurs in a row whose
  current y is 0 (form 2 guarantees final y = 0). The edit changes a key in
  column j to 0, so the newly joined groups are exactly determinants X with
  j in X, X subset of the new mask, X not subset of the old mask: a subset of
  F_j. Each of their margins rises by exactly 1 for every rival v.
- Per chain: among affected X whose L-group still has a nonzero-y context
  row, the inclusion-largest X has the smallest L-group, contained in the
  L-group of every other such X' (X' subset X). One flip of a row in it raises
  all those margins by >= 1 (by 2 for the flipped row's old value).
- Affected X with no nonzero-y row in L: m_L >= 1 from the target alone.
- Capped invariant: if m_L >= 1 the cap holds trivially; if m_L < 1 then
  m_L >= m_H by the invariant, and both gain (L at least 1), so it persists.
  Unaffected margins: H unchanged, L can only increase (a flip to 0 never
  decreases any margin). Verified.
- Cost: flipped rows have nonzero y in L, hence distinct from the R rows and
  from each other; L's Hamming cost is R + (number of flips) <=
  R + sum_j w_j K_j <= w (R + sum_j K_j). Uses w_j <= w and w >= 1.
- Termination: H accepts at the end (Lemma 1 preserves acceptance), so every
  m_H >= 1, so every min(m_L,1) = 1.

Dilworth is needed only to partition F_j into w_j chains; the minimum-size
partition gives the constant. Any chain partition gives a valid weaker bound.

## Theorem 3 (tightness)

- Critical group A_i = {t, r_i}: r_l (l != i) would need A_i subset A_l
  (antichain forbids), p fails key j in A_i, a support row with mask C would
  need A_i subset C (excluded by the choice of C).
- Noncritical C containing no A_i: >= w+1 zeros (t plus its w supports) vs at
  most w rivals. Strict, so accepts even when all w rivals match.
- Noncritical C containing some A_i: a rival r_l in it forces
  A_i subset C subset A_l, hence l = i and C = A_i, contradiction. No rivals.
- p's single key edit makes p all-zero, entering every group: critical groups
  become 2:1. rho_full = 1 because the table initially rejects.
- Fixed keys: each critical group's only mutable cell is r_i.y, distinct per i,
  so rho_fixed >= w; flipping them gives an all-zero y column, so = w.
- Needs a binary alternative in every key domain and one rival y value. The
  lower bound also holds for larger domains.
- When w = 1 the construction is a valid but trivial ratio-1 instance.

## Corollary 4

Both directions re-checked; an intersecting incomparable pair is exactly a
2-antichain inside some F_j.

## Items to make explicit in the manuscript

1. The per-column refinement rho_fixed <= R + sum_j w_j K_j for a normalized
   optimal witness, which is sometimes stronger than the factor w.
2. The theorem is about listed checks; logically implied FDs change the
   detector (the {a},{a,b},{a,c} example).
3. Tie convention matters for the construction (ties reject); the voting
   literature often uses co-winner semantics.
4. Nested-set dominance is a known technique family (EMMI chain shifting,
   Dilworth). The claim is the specific ratio, its sharpness for every
   family, and the laminar characterization, not the technique.
5. The exchange is constructive but not an approximation algorithm: it
   needs an optimal full witness. Hardness from E012 remains.

## Open question noticed during audit (not resolved)

Does the ratio stay tight at every scale, i.e. for each k is there a table
with rho_full = k and rho_fixed = w k? Taking k disjoint-coordinate copies is
not available inside a single target's groups (all groups share t). This is
not needed for any claim and is recorded only as a possible extension.
