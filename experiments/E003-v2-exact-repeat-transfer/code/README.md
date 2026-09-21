# E003-v2 source-normalization component

This is a partial implementation, NOT a performance runner. `source_v2.py`
provides pure in-memory source validation, exact-repeat collapse, original line
mapping, all-type repository indexing, fixed inventory gates and derived
manifest bytes. It neither writes files nor imports/mutates E003-v1 code.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s experiments/E003-v2-exact-repeat-transfer/code -p 'test_source_v2.py' -v
```

Tests use synthetic compressed records and reconstruct manifest metadata from
locked constants. They do not open real shards, execute scoring or create a
v2 manifest. The full runner must use `normalize_pinned`, verify both protocol
locks and independent review acceptance, then integrate projection/exclusions,
selection, methods/oracle, calibration, metrics, bootstrap and staged output.
`normalize_sources` permits synthetic/dev-subset inputs and is not a substitute
for production pins or runner authority checks.

Full evaluation integration, full-suite regression tests, guarded 2019/2020
integration and independent acceptance are still pending. No v2 result exists.
