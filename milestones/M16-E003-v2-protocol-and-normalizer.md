# M16 — E003-v2 lock and tested source-normalization component

Date: 2026-09-21. Status: `protocol_locked_partial_implementation`.
This is engineering/protocol progress, not a scientific performance result.
Authority: user said `được rồi tiếp tục đi` after M15. Design is AI-suggested.
No network, raw-source analysis, scoring, delegation, publication, push or
epilogue writes were performed in this stage.

## Locked design

- [E003-v2 amendment](../experiments/E003-v2-exact-repeat-transfer/protocol.md),
  lock commit `b9cae977cfa9640e1ad4064bfccbbebe945b81fb`;
  raw SHA-256 `2c7b76290f0d9128910f7f3c565a68374a432f9f2507976a8fd68e8495bcba15`.
- The amendment incorporates the unchanged E003-v1 protocol by exact commit
  and hash, with explicit precedence. It preserves selection, mutations,
  methods, oracle contract and metric rules, while versioning all identities.
- Source normalization compares full raw bytes before type filtering or field
  projection, keeps the first exact occurrence with its original coordinates,
  and rejects any differing repeat or cross-shard repeated ID.
- All-type repository indexing is distinct from selected-event eligibility;
  no repeated event IDs does not establish repository isolation.
- All three sources were already inspected in E004. Classification is
  `exploratory_reused_sources`; H3-v2 cannot retroactively answer original H3.
- Original source manifest remains unchanged. The expected derived v2 manifest
  hash is `c6c43cbbc6f069d78c56c9d7b9c45a58120574c205f059c1fe1b0086f7f3fa47`.
  The expected digest was computed from original manifest metadata; no v2
  manifest file was written and no source content was read.

## Component implementation and checks

Implementation commit: `87ccd6922854ea8c6d5e4e2faaaff216b8bf0e1d`.
[source_v2.py](../experiments/E003-v2-exact-repeat-transfer/code/source_v2.py)
is pure in-memory code: no filesystem/network I/O, scoring or v1 imports.
It checks all supplied compressed pins before any parsing, strictly parses
gzip/JSON, returns no partial normalized collection, preserves immutable raw
bytes, accounts for collapsed occurrences and collects shared repository IDs.
The production inventory wrapper checks frozen pins and E004-informed counts.
The manifest helper returns derived bytes only, never overwrites a file.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s experiments/E003-v2-exact-repeat-transfer/code -p 'test_source_v2.py' -v
```

Observed: **22 tests passed**, 0.003 seconds. All compressed inputs are synthetic;
manifest tests reconstruct metadata from constants. Coverage includes exact
repeats/multiplicity, source order, CRLF/blanks/final-LF absence, only-one-CR
removal, spacing/key order, ignored fields, A/B/B, integer/string ID conflicts,
invalid IDs/types, duplicate JSON keys, invalid Unicode, nonfinite/overflowing
numbers, cross-shard excluded-type repeats, late-failure atomic return, all-type
repository indexing, hash/size/count gates, malformed/truncated/multimember gzip,
split identity, fixed inventory rejection and manifest derivation.

These tests establish bounded component behavior, not full pipeline correctness,
real-source v2 validity or independent acceptance. No full v2 runner exists.
The component alone does not check Git/review authority, select/filter cases,
fit calibration, compute bootstrap metrics or stage outputs.

## Prioritized remaining implementation and readiness gates

1. Integrate the component into a separately versioned v2 pipeline, preserving
   original source bytes/coordinates. Connect inherited projection, deterministic
   exclusion accounting and all-three-split repository isolation. Reconcile
   `raw=unique+collapsed` and `unique=excluded+eligible` before base selection.
2. Integrate inherited oracle/methods, mutations, calibration, exact metrics and
   bootstrap with v2 identities and paths. Preserve v1 code and evidence; no
   runtime monkeypatching or guard bypass. Test no-calibration marker and changed
   deterministic bootstrap prefix explicitly.
3. Implement both-lock ancestry/hash guards, manifest creation/verification,
   committed independent-acceptance validation and transactional four-artifact
   publication. Test late failures, output refusal and no partial valid report.
4. Run synthetic end-to-end regression tests plus guarded development/calibration
   integration refusing any 2021 file read. Do not infer three-split feasibility
   from the two-split integration. Record exact implementation commit for review.
5. Obtain independent acceptance addressing v2 and unresolved M12 issues before
   a single exploratory performance execution. Current no-delegation scope does
   not provide such acceptance. Do not treat this author's tests as independent.

E003-v1 remains invalid; E001/E002 remain the only valid performance results.
E004 remains a valid source diagnostic only. Public-claim eligibility is false.
Later confirmatory transfer needs separately preselected, uninspected sources.
Historical ARA claims are not current authority; ARA has not been updated.
