# E006-A1 — fixed-source acquisition and schema-only inspection

Date: 2026-10-22. Purpose: acquire external reference tables for the arXiv
research continuation. Lock before acquisition. This is not an evaluation
protocol or permission to inspect reference differences or compute performance.

## Fixed inventory

Official repository: https://github.com/BigDaMa/raha
Commit: 7be1334b8c7bbdac3f47ef514fb3e1e8c5fc181c (git ls-remote verified).
Exactly three datasets in this order: beers, flights, rayyan.
For each, acquire datasets/<name>/dirty.csv and datasets/<name>/clean.csv.
Also acquire README.md, LICENSE.md and raha/dataset.py as provenance metadata.
All URLs use https://raw.githubusercontent.com/BigDaMa/raha/<commit>/<path>.
No alternate revision, mirror, replacement dataset, installs or package execution.
HTTP HEAD checked the six CSV paths before this lock; no CSV body was read.
Published paper samples and performance tables have been seen; disclose this.

## Source reason and boundary

The original paper describes manually cleaned/owner-cleaned external records
for Beers/Rayyan, and an externally supplied reference for Flights. They were
chosen for small CPU-feasible size, three domains and reference provenance,
not our observed metrics. The reference may be incomplete or imperfect.
Do not describe all corruptions as naturally generated without further evidence.
Known close prior work (Jung et al. 2025) already studies error-model effects;
the new study cannot claim that broad insight as novel.

## Acquisition and allowed inspection

Download nine pinned files outside Git under
/Users/mac/Library/Caches/InvariantAudit/E006-v1-20261022/source/.
Use exclusive creation; never overwrite a cache file. Refuse an existing
manifest. Each response must be HTTP 200 and at most 20 MB. No automatic retry
or source substitution. Record URL, status, bytes, SHA-256 and source commit.
Build a canonical manifest plus aggregate digest. Preserve metadata/license.

After all files have arrived, the only CSV content inspection allowed by this
stage is reading each first logical header record to ensure unique names and
matching dirty/clean headers. Record header lists. Do not traverse table rows,
compare dirty/clean values, calculate error rates, choose examples, fit methods,
inspect any candidate evaluation outcomes or read E003 caches. Payloads remain
outside Git and no raw cell values enter committed artifacts.

A new evaluation protocol must lock exact selectors, normalization, splits,
methods, probability rules, metrics, uncertainty and stopping before row reads.
Source shape/row counts are validated only after that lock; do not fit the
protocol to observed reference outcomes. Separate acquisition manifest metadata
is permitted before evaluation, and does not count as a performance result.

## Failure and output rules

One acquisition attempt. Any missing file, size/header mismatch, parse error or
non-200 response stops the phase, preserving a concise invalid acquisition
record and any downloaded original bytes. Do not retry under the same attempt.
No incomplete manifest is marked valid. Valid outputs are a source-manifest.json
outside Git and its metadata-only mirror data/E006-v1-source-manifest.json,
plus a stage report in this experiment's results/. No execution result or
scientific claim is established by acquisition success. E003-v2 gates remain
unchanged and no public push, account action or submission is authorized here.
