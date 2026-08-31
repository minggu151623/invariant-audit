# M11 — E003 source acquisition freeze and cache remediation

M11 records the completed, read-only acquisition audit and reversible cache
remediation for the locked E003-v1 protocol. It is source provenance and
format-validation evidence only; it is not an E003 implementation, execution,
metric, result, or public claim.

## Authority and boundary

The bounded user instruction on 2026-09-01 authorized local verification of the
already acquired exact fixture set, reversible sidecar remediation, metadata
chronology reconciliation, scoped documentation/state writes, and one local
commit. Network access was not used, no worker was delegated, and no protocol,
implementation, event selection, scoring, or confirmatory execution was
authorized.

The starting Git HEAD was
`b68424e756fb86f05c866647b2471d36e24da716`. The locked protocol commit
`163e44dcabc698f101dee70dd7f3aa1bb7c8d5fb` remains an ancestor; the protocol
blob SHA-256 remains
`8ec0ebc9b3420a2d71eebfe579ae2d1c87aa74c419dd3f38d1f0dc06c5c1e2a6`.

The raw `.json.gz` sources and canonical manifest remain outside Git. The
audited source cache is `/private/tmp/invariant-audit-e003-v1/source/`; the
manifest is `/private/tmp/invariant-audit-e003-v1/source-manifest.json`; and
the updated metadata sidecar is
`/private/tmp/invariant-audit-e003-v1/acquisition-metadata.json`.

## Manifest, payloads, and authoritative freeze event

Manifest SHA-256:
`683eef39cd26d2a7f6622689adc2cd9e357e78a770f77bf91e98513b859e4633`

Updated metadata SHA-256:
`5937fbf7d8583ed3954b7d107146af331d29f2a14e224d883e892c74ce52388a`

Canonical local-freeze-event SHA-256 (UTF-8 JSON, sorted keys, compact
separators, LF):
`17ac5e9eb4386ef2d6f4f34996f240e600b16d7521fdcc6b91dfd10630c27ed7`

The authoritative local-only freeze event occurred at
`2026-08-31T19:59:22Z` UTC, after the existing manifest and all three gzip
payloads were verified locally. It records the manifest hash, exact cache
inventory, starting Git HEAD, and `network_used_during_remediation: false`.
The metadata records `network_after_manifest_freeze: false` as well.

| Split | Filename | URL | HTTP | SHA-256 | Bytes | JSONL lines |
| --- | --- | --- | ---: | --- | ---: | ---: |
| development | `2019-01-15-12.json.gz` | `https://data.gharchive.org/2019-01-15-12.json.gz` | 200 | `ae451576f78417d75f135b29ee67ea8e666dc5f6cb16e78cef04e20342b42b50` | 29278679 | 67145 |
| calibration | `2020-01-15-12.json.gz` | `https://data.gharchive.org/2020-01-15-12.json.gz` | 200 | `624a0d2a2fc575afb1e63bece53521e2b078ddfd1caf60026e313ad36d83cddd` | 46372480 | 90940 |
| confirmatory | `2021-01-15-12.json.gz` | `https://data.gharchive.org/2021-01-15-12.json.gz` | 200 | `a4a80c97153c691866d52b7e06ea0051f2449f0c6f8060dad9f441a69cd13788` | 61805367 | 117780 |

The three streams passed standard-library gzip decompression, strict UTF-8
decoding, and one-JSON-object-per-nonempty-line validation. The confirmatory
shard was touched only for hash, byte, line-count, and format validation; no
event selection, projection, calibration, scoring, metrics, bootstrap, or
result operation was performed.

## Cache remediation and provenance

Before remediation, the source directory contained these six files:

```text
2019-01-15-12.headers       1095 B  0e9f751b9c213201b49900c94d58776488ddc6c1b7994b06d7530574b100dfd8
2019-01-15-12.json.gz  29278679 B  ae451576f78417d75f135b29ee67ea8e666dc5f6cb16e78cef04e20342b42b50
2020-01-15-12.headers       1084 B  d33afd6da92f991d7fabef3d27a2e7df05ba21984aa04b27da01764c19636322
2020-01-15-12.json.gz  46372480 B  624a0d2a2fc575afb1e63bece53521e2b078ddfd1caf60026e313ad36d83cddd
2021-01-15-12.headers       1098 B  761ffd6482919336cb57682c9c211843770ad187ed280bec7faf49d59d4d8815
2021-01-15-12.json.gz  61805367 B  a4a80c97153c691866d52b7e06ea0051f2449f0c6f8060dad9f441a69cd13788
```

The post-remediation source inventory is exactly:

```text
2019-01-15-12.json.gz  29278679 B  ae451576f78417d75f135b29ee67ea8e666dc5f6cb16e78cef04e20342b42b50
2020-01-15-12.json.gz  46372480 B  624a0d2a2fc575afb1e63bece53521e2b078ddfd1caf60026e313ad36d83cddd
2021-01-15-12.json.gz  61805367 B  a4a80c97153c691866d52b7e06ea0051f2449f0c6f8060dad9f441a69cd13788
```

The three `.headers` files were moved, not deleted, to the clearly named
archive `/private/tmp/invariant-audit-e003-v1-remediation-archive-20260901/`:

| Moved file | Archive destination | SHA-256 |
| --- | --- | --- |
| `2019-01-15-12.headers` | `/private/tmp/invariant-audit-e003-v1-remediation-archive-20260901/headers/2019-01-15-12.headers` | `0e9f751b9c213201b49900c94d58776488ddc6c1b7994b06d7530574b100dfd8` |
| `2020-01-15-12.headers` | `/private/tmp/invariant-audit-e003-v1-remediation-archive-20260901/headers/2020-01-15-12.headers` | `d33afd6da92f991d7fabef3d27a2e7df05ba21984aa04b27da01764c19636322` |
| `2021-01-15-12.headers` | `/private/tmp/invariant-audit-e003-v1-remediation-archive-20260901/headers/2021-01-15-12.headers` | `761ffd6482919336cb57682c9c211843770ad187ed280bec7faf49d59d4d8815` |

The pre-remediation metadata was preserved at
`/private/tmp/invariant-audit-e003-v1-remediation-archive-20260901/acquisition-metadata.pre-remediation.json`,
SHA-256
`6d47ea164f42a02b69fad37c466cd7253bb7f07b3f6a1985534fc2b657b9554f`.

## Chronology reconciliation and next gate

The old metadata asserted `network_frozen_at_utc` as
`2026-08-31T19:06:24Z`, while the observed manifest filesystem mtime was
`2026-08-31T19:07:45Z`. That original mtime ordering is not independently
supported and is retained only in the updated metadata's historical section;
history was not rewritten or backdated. The new local event is explicitly
post-verification and is the authoritative boundary for the audited source
set.

Current state is `acquisition_complete_audited_implementation_absent`:

- implementation: absent;
- confirmatory run: absent and unauthorized;
- predictions, metrics, bootstrap, result, and code: absent; and
- `public_claim_eligibility: false`.

Separate authority and independent review are required before implementation
or the single confirmatory run. A changed or unavailable source requires a new
protocol version; no substitution or retry is authorized.
