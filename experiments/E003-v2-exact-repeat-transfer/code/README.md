# E003-v2 source normalization and adapter components

This is a partial implementation, NOT a performance runner.

## Components

- `source_v2.py`: Pure in-memory source validation, exact-repeat collapse, original line mapping, all-type repository indexing, fixed inventory gates, and derived manifest bytes.
- `adapter_v2.py`: Pure in-memory adapter connecting normalized sources to eligible and selected bases. Enforces exact per-split quotas (64 IssuesEvent, 64 PullRequestEvent), repository diversity (minimum 24 selected repositories overall, minimum 16 per event type, maximum 4 bases per repository per event type), cross-split repository isolation across all raw types, and deterministic fail-closed exclusion accounting.

## Hash-Pinned Unversioned V1 Pure Helpers

`adapter_v2.py` reuses unversioned pure helpers (`project_event`, `canonical_json_text`, `input_sha256`, `_raw_label`, `_strict_decimal_id`, `reference_oracle`) by loading pinned v1 reference modules with SHA-256 digest validation (`_load_pinned_v1_module`). It does not mutate or rewrite any existing v1 files.

## Running Tests

All unit tests run on synthetic in-memory compressed records. They do not open real shards, read from source cache, access network, execute scoring, or create a v2 manifest:

```sh
# Full synthetic unittest discovery
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s experiments/E003-v2-exact-repeat-transfer/code -p 'test_*.py' -v

# Adapter tests only
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s experiments/E003-v2-exact-repeat-transfer/code -p 'test_adapter_v2.py' -v

# Source normalizer tests only
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s experiments/E003-v2-exact-repeat-transfer/code -p 'test_source_v2.py' -v
```

## Constraints and Status

- **No real data reads**: Tests use synthetic fixtures exclusively and reconstruct metadata from locked constants without reading source caches or disk shards.
- **No full runner / review / performance result**: The full runner must use `adapt_pinned`/`normalize_pinned`, verify both protocol locks and independent review acceptance, then integrate evaluation, calibration, metrics, and bootstrapping. Full evaluation integration, review acceptance, and guarded 2019/2020 execution remain pending. No v2 performance result exists.
