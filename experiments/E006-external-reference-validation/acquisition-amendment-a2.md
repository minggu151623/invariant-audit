# E006-A2 — explicit header aliases on the acquired original bytes

Date: 2026-10-22. Lock before metadata recovery. A1 remains invalid.
Its single attempt downloaded all nine files but stopped on header mismatch,
without writing a valid manifest or inspecting data rows. A header-only
follow-up identified two spelling differences in Beers: dirty `beer_name`
corresponds positionally to clean `beer-name`, and dirty `brewery_name` to clean
`brewery-name`. All other headers match exactly. Rayyan's original misspellings
are present on both sides and are preserved as source names.

## Narrow amendment

Reuse the nine existing original byte streams, never re-download or rewrite.
Require exact sizes/SHA-256 and source commit from `source-pins-a2.json` before
header parsing. Acquire no alternate file, revision or dataset. Only the two
explicit Beers clean-header aliases are allowed. After those mappings, require
paired headers to be equal in the same order, nonempty and unique. Mapping
changes metadata only; original CSV bytes and column positions remain intact.
All A1 no-row/no-reference-difference/no-performance restrictions remain.

Create the external source-manifest.json only if absent, and its identical
metadata mirror data/E006-v1-source-manifest.json. Include both lock identities,
the original invalid attempt identity, hashes/bytes/URLs, original header lists,
canonical header lists, exact aliases and the no-row-inspection declaration.
A2 report has a new path `results/source-recovery-e006-20261022-002.md`.
Do not overwrite the invalid A1 record or mark it valid retroactively.

This is a reviewed-by-author metadata correction informed by header inspection,
not independent acceptance. No labels, rates, method predictions or candidate
performance were inspected to choose it. Positional semantic alignment remains
an assumption to validate against fixed row-key checks in a separately locked
evaluation protocol. Stop on any additional mismatch; no automatic relaxation.
