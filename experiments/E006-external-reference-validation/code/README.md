# E006: external reference diagnostic

The protocol is fixed before any paired source-row inspection. Run with the
existing local NumPy environment; no package install or Raha execution is needed.
Tested runtime: Python 3.13.5, NumPy 2.1.3 at `/opt/anaconda3/bin/python`.

```sh
PYTHONDONTWRITEBYTECODE=1 /opt/anaconda3/bin/python -m unittest discover -s experiments/E006-external-reference-validation/code -p 'test_*.py' -v
```

Commit implementation before the single fixed-source data run:

```sh
PYTHONDONTWRITEBYTECODE=1 /opt/anaconda3/bin/python experiments/E006-external-reference-validation/code/run_e006.py
```

The runner verifies the protocol ancestry, committed implementation, source
manifest and nine raw byte pins; builds all six outputs twice; compares every
serialized byte; and publishes the report last. The raw data must remain in the
external pinned cache. It refuses existing destinations and preserves an invalid
record after a failed study attempt. Do not re-run in place or alter rules to
obtain a favorable result. Reproduction needs a separate checkout at the
implementation commit and the exact source manifest/cache.

`evaluate.py` scores dirty strings before loading reference tables and fits
lookups from calibration cells only. `point_reference.py` supplies a rational,
direct cellwise cross-check without importing NumPy or the primary metrics.
Both were authored by the same agent; this is numerical self-review, not
independent reviewer acceptance. Published source labels can contain errors.

The source acquisition history is separate: A1 failed on two Beers header names,
then A2 explicitly mapped those aliases without changing or re-downloading data.
Never describe A1 as valid or hide this metadata correction. No E003 cache or
E003-v2 execution/review gate is involved in E006.
