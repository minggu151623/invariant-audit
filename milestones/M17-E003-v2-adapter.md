# M17 — E003-v2 source filtering and selection adapter

Date: 2026-09-21. Status: `partial_implementation_adapter_verified`.
This is engineering/adapter progress, not a scientific performance result.
Authority: user said `được rồi tiếp tục công việc nghiên cứu đi` after M16.
Design is AI-suggested; author is Gemini 3.8 Flash high via AGY in Herdr ipse.
No network, source cache/real shards, run/scoring/calibration, protocol edits,
E001-E004 evidence edits, publication, push or external actions were performed.

## Design and protocol pins

- Both locked protocol SHA-256 digests remain unchanged:
  - [E003-v2 amendment](../experiments/E003-v2-exact-repeat-transfer/protocol.md),
    lock commit `b9cae977cfa9640e1ad4064bfccbbebe945b81fb`;
    raw SHA-256 `2c7b76290f0d9128910f7f3c565a68374a432f9f2507976a8fd68e8495bcba15`.
  - [E003-v1 protocol](../experiments/E003-external-transfer-validation/protocol.md),
    raw SHA-256 `8ec0ebc9b3420a2d71eebfe579ae2d1c87aa74c419dd3f38d1f0dc06c5c1e2a6`.
- Helper hash pins: unversioned pure helpers are loaded via `_load_pinned_v1_module`
  with explicit SHA-256 digest checks before execution:
  - `experiments/E003-external-transfer-validation/code/e003.py`:
    SHA-256 `cd21b21a69565385408edbcb5df1beb91a20534b452219662c1902c82dfa934c`.
  - `experiments/E003-external-transfer-validation/code/oracle_e003.py`:
    SHA-256 `0bfc2be8135d71bcaed8ccfd16fae38f53299023b9c3d185592af3ff628442d4`.
- Classification remains `exploratory_reused_sources`; public-claim eligibility is `false`.

## Adapter implementation and verification

Implementation commit: `28f74d56eb9d4813139279da445c32fd10ec973e`.
Files:
- [adapter_v2.py](../experiments/E003-v2-exact-repeat-transfer/code/adapter_v2.py)
- [test_adapter_v2.py](../experiments/E003-v2-exact-repeat-transfer/code/test_adapter_v2.py)
- [README.md](../experiments/E003-v2-exact-repeat-transfer/code/README.md)

The source adapter is pure in-memory code implementing:
`normalization -> v1 pinned pure projection/oracle helpers -> first reason exclusions -> all-type/all-requested-split repo isolation -> deterministic quotas/caps/diversity`, retaining original source coordinates throughout.

Key architectural properties:
1. Strict fail-closed semantics: raises `AdapterError` on any pin mismatch, missing
   requirement, or quota deficit; returns no partial collection.
2. Exact per-split quotas: 64 IssuesEvent, 64 PullRequestEvent (128 bases per split).
3. Repository diversity: minimum 24 selected repositories overall, minimum 16 per
   event type, maximum 4 bases per repository per event type.
4. Repository isolation across all requested splits: removes all repository IDs
   shared between any requested splits across all raw normalized event types.
5. Deterministic exclusion accounting: tracks and reconciles `raw = unique + collapsed`
   and `unique = excluded + eligible` before base selection. Original coordinates
   (line numbers, source indices) are preserved.

### Test execution and bounded review scope

Orchestrator independently ran all 39 synthetic tests (22 source normalizer + 17 adapter):

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s experiments/E003-v2-exact-repeat-transfer/code -p 'test_*.py' -v
```

Observed: **39 tests passed**, 0.312 seconds (all pass, exit code 0).
Test progression: initial 35 tests had 1 failure and 9 errors; after the first
remediation 2 fixture failures remained; with final adjustments all 39 tests pass.

Bounded review scope: these synthetic tests verify bounded in-memory adapter logic
under controlled fixtures. They do not constitute independent full-pipeline
acceptance. No real source shards were read; old and new raw data, metrics,
and run records remain absent.

## Remaining M16 priorities (priorities 2–5)

1. **Priority 2 (Evaluation & calibration version identities):** Integrate inherited
   oracle/methods, mutations, calibration, exact metrics and bootstrap with v2
   version identities and paths. Preserve v1 code and evidence; no runtime monkeypatching
   or guard bypass. Test no-calibration marker and changed deterministic bootstrap prefix explicitly.
2. **Priority 3 (Guards & transactionality):** Implement both-lock ancestry/hash guards,
   manifest creation/verification, committed independent-acceptance validation and
   transactional four-artifact publication. Test late failures, output refusal and no partial valid report.
3. **Priority 4 (Guarded 2019/2020 integration):** Run synthetic end-to-end regression
   tests plus guarded development/calibration integration refusing any 2021 file read.
   Do not infer three-split feasibility from the two-split integration. Record exact
   implementation commit for review.
4. **Priority 5 (Independent acceptance before execution):** Obtain independent acceptance
   addressing v2 and unresolved M12 issues before a single exploratory performance execution.
   Current worker/no-delegation scope does not provide such acceptance. Do not treat author
   or orchestrator tests as independent acceptance.

E003-v1 remains invalid; E001/E002 remain the only valid performance results.
E004 remains a valid source diagnostic only. Public-claim eligibility is false.
