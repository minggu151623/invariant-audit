# E005 independent metric reimplementation

Python standard library only. No E001/E002/E003 metric or validator code is
imported. The author and environment are shared, so this is self-review and a
separate implementation, not independent reviewer acceptance.

Run synthetic tests before the locked data audit:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s experiments/E005-benchmark-evidence-audit/code -p 'test_*.py' -v
```

Commit implementation before executing the one run:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 experiments/E005-benchmark-evidence-audit/code/audit.py
```

The command verifies protocol ancestry/bytes, committed implementation and all
four input hashes; checks original overall metrics against the independent
recomputation; builds all four audit artifacts twice; publishes the report last;
and refuses existing output paths. It does not rerun old experiments or read GH
Archive sources. An audit failure writes a concise invalid record after cleanup.
The historical run-ID and destinations are fixed by the locked protocol; use a
separate checkout at the implementation commit to reproduce, not an in-place retry.
