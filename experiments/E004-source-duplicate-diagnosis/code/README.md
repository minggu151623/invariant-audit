# E004 source diagnostic implementation

`recover.py` downloads only the three protocol-pinned public shards to the
external durable cache; it verifies compressed bytes and reconstructs the exact
historical manifest. It never invokes E003 or chooses another fixture.

`audit.py` is the explicit source diagnostic CLI. Tests use synthetic records
only. It preserves full-object distinctions and uses dictionary and sorted
aggregation paths, with a shared strict parser. This is single-agent differential
verification, not independent review. The protocol was locked before this code.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s experiments/E004-source-duplicate-diagnosis/code -p 'test_audit.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 experiments/E004-source-duplicate-diagnosis/code/recover.py
PYTHONDONTWRITEBYTECODE=1 python3 experiments/E004-source-duplicate-diagnosis/code/audit.py --run-id e004-20260917-001 --cache /Users/mac/Library/Caches/InvariantAudit/E003-v1-20260917
```

The audit requires a clean committed worktree. Existing outputs are refused.
One completed diagnostic ends E004; no E003 performance scoring is authorized
by these commands. All reports omit source IDs, names, actor data and payloads.
