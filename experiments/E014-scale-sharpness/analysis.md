# E014 analysis

2026-11-10. Protocol `6c8827a`, implementation `d98e454`, one run, no fix
commit, no mismatch. `python3 verify_scale.py --verify` recomputed everything
and matched the stored summary (about 30 seconds on the author's Mac).

## Part A: the construction of H14a

| Case | Family | q | k | d | w | Context rows | (rho_full, rho_fixed) | Raw tables, editable / fixed |
|---|---|---|---|---|---|---|---|---|
| A1 | {0,1},{0,2} | 3 | 1 | 2 | 2 | 3 | (1, 2) | 1 / 4 |
| A2 | {0,1},{0,2} | 3 | 2 | 3 | 2 | 10 | (2, 4) | 51 / 1,161 |
| A3 | {0,1},{0,2} | 3 | 2 | 4 | 2 | 10 | (2, 4) | 61 / 3,676 |
| A4 | {0,1},{0,2} | 3 | 3 | 4 | 2 | 21 | (3, 6) | 7,939 / 5,467,456 |
| A5 | {0},{0,1},{0,2} | 3 | 2 | 3 | 2 | 14 | (2, 4) | 71 / 3,305 |
| A6 | {0,1},{0,2},{0,1,2} | 3 | 2 | 3 | 2 | 10 | (2, 4) | 51 / 1,161 |
| A7 | {0,1},{0,2},{1,2} | 3 | 2 | 3 | 2 | 14 | (2, 4) | 71 / 3,305 |
| A8 | {0,1},{0,2},{0,3} | 4 | 2 | 3 | 3 | 14 | (2, 6) | 85 / 83,385 |
| A9 | all seven subsets | 3 | 2 | 3 | 2 | 26 | (2, 4) | 131 / 22,153 |

Every case equals the predicted (k, w*k). In every case and both edit models
the raw bounded enumeration ran (no case exceeded the 10^7 limit) and found no
accepting table below the predicted radius; the row dynamic program returned
the same value; the stated witnesses accept by direct counting. The raw
enumeration evaluated 5,594,099 edited tables in total, the control included.

**Control.** Binary RHS, k = 2: (rho_full, rho_fixed) = (2, 2), as predicted.
The construction's condition d >= k+1 is therefore not removable in this case.

## Part B: binary two-rule family

74,612 tables (all multisets of one to six context rows), 34,393 with a
rejected target. Cross-tabulation of (rho_full, rho_fixed):

| rho_full | rho_fixed = rho_full | rho_fixed = rho_full + 1 |
|---|---|---|
| 1 | 28,293 | 309 |
| 2 | 5,440 | 23 |
| 3 | 325 | 0 |
| 4 | 3 | 0 |

rho_fixed <= rho_full + 1 on every rejected table; the factor 2 occurs only at
rho_full = 1. The 23 tables with (2, 3) show that the additive slack of H14b
is attained at rho_full = 2. No table with at most six rows has (3, 4); the
check says nothing about larger tables. For the 968 tables with at most three
rows, raw enumeration of all 3,377,408 destination tables matched the dynamic
program in both edit models.

## What this does and does not show

- The finite predictions of H14a and H14b hold on the locked domains. The
  universal statements rest on the written proofs, which were derived and
  checked by AI sessions in this project; no independent review exists.
- Tables in Part B overlap heavily and are not independent replications.
- Nothing here concerns source data, runtime, or historical originality.
- Open: the best ratio at rho_full = k when 2 < d <= k, and for families other
  than the two-rule one when d = 2.
