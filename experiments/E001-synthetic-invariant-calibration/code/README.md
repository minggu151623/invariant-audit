# E001 evaluation harness

This directory contains the standard-library-only implementation of the
locked `E001-v1` protocol at commit
`d8b26d21e9692ace19436d78461460940043f5c7`. The generator, independently
maintained reference oracle, B0/M1 validators, pre-specified ablations, frozen
calibration lookups, metrics, and deterministic cluster bootstrap are
implemented in `e001.py`.

Run the development/unit checks with:

```sh
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover \
  -s experiments/E001-synthetic-invariant-calibration/code \
  -p 'test_*.py' -v
```

The future explicit run command is:

```sh
python experiments/E001-synthetic-invariant-calibration/code/run_e001.py \
  --run-id e001-YYYYMMDD-001 \
  --output-root .
```

The CLI requires both arguments, checks the clean locked protocol identity and
ancestor gate, refuses existing output files, and writes only the protocol's
future `experiments/E001-synthetic-invariant-calibration/results/` and root
`data/` files when explicitly invoked. It does not run on import.

The future bootstrap CSV is deliberately paired-only at the replicate level
(M1 minus B0) and is expected to remain below the public 52,428,800-byte file
gate; interval-summary rows carry method and paired intervals without copying
every method's replicate series.

The confirmatory run was **not executed in this commit**. No confirmatory
metrics, results, data, state, findings, figures, or ARA records are produced
by the development tests.
