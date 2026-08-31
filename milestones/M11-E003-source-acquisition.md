# M11 — E003 source acquisition freeze

M11 records the completed, read-only acquisition stage for the locked
E003-v1 protocol. It is source provenance and format-validation evidence only;
it is not an E003 implementation, execution, metric, result, or public claim.

## Authority and boundary

The bounded user instruction on 2026-09-01 authorized only verification and
recording of the already acquired exact fixture set, local documentation, and
one local commit. Network access was not used for this record. The protocol
commit `163e44dcabc698f101dee70dd7f3aa1bb7c8d5fb` remains unchanged and is an
ancestor of this milestone commit.

The canonical manifest is deliberately not copied into Git: E003-v1 requires
the raw `.json.gz` sources and acquisition manifest to remain outside Git.
The frozen cache is `/private/tmp/invariant-audit-e003-v1/source/`; the
canonical manifest is
`/private/tmp/invariant-audit-e003-v1/source-manifest.json`, and the HTTP
metadata sidecar is
`/private/tmp/invariant-audit-e003-v1/acquisition-metadata.json`.

## Frozen acquisition record

Manifest SHA-256:
`683eef39cd26d2a7f6622689adc2cd9e357e78a770f77bf91e98513b859e4633`

| Split | Filename | URL | HTTP | ETag | Last-Modified | SHA-256 | Bytes | JSONL lines |
| --- | --- | --- | ---: | --- | --- | --- | ---: | ---: |
| development | `2019-01-15-12.json.gz` | `https://data.gharchive.org/2019-01-15-12.json.gz` | 200 | `"0af4633b81d16ebcd1e681e34128abf9"` | `Tue, 15 Jan 2019 13:05:10 GMT` | `ae451576f78417d75f135b29ee67ea8e666dc5f6cb16e78cef04e20342b42b50` | 29278679 | 67145 |
| calibration | `2020-01-15-12.json.gz` | `https://data.gharchive.org/2020-01-15-12.json.gz` | 200 | `"99bfbdadc0c9fe40e0b56cbbd30580da"` | `Wed, 15 Jan 2020 13:05:14 GMT` | `624a0d2a2fc575afb1e63bece53521e2b078ddfd1caf60026e313ad36d83cddd` | 46372480 | 90940 |
| confirmatory | `2021-01-15-12.json.gz` | `https://data.gharchive.org/2021-01-15-12.json.gz` | 200 | `"8105aef4fa8d8a4c5cf52480f2e58f35"` | `Fri, 15 Jan 2021 13:05:17 GMT` | `a4a80c97153c691866d52b7e06ea0051f2449f0c6f8060dad9f441a69cd13788` | 61805367 | 117780 |

The captured HTTP `Date` was `Mon, 31 Aug 2026 19:05:54 GMT` for all three
responses. The local file-completion acquisition timestamps recorded in the
external metadata are `2026-08-31T19:05:59Z` (development),
`2026-08-31T19:06:09Z` (calibration), and `2026-08-31T19:06:07Z`
(confirmatory). The streams passed Python-standard-library gzip decompression,
UTF-8 decoding, and one-JSON-object-per-nonempty-line validation. No network
access occurred after the manifest was frozen.

## Confirmatory isolation and next gate

The confirmatory shard was touched only for the protocol-required acquisition
validation above: raw SHA-256, byte count, gzip decoding, UTF-8 decoding, and
decompressed JSONL line count. No source event was selected, projected into a
case, scored, calibrated, or used for metrics/bootstrap. No output or result
path exists.

Current state is `acquisition_complete_implementation_absent`:

- implementation: absent;
- confirmatory run: absent and unauthorized;
- predictions, metrics, bootstrap, result: absent; and
- `public_claim_eligibility: false`.

Separate authority and independent review are required before implementation
or the single confirmatory run. A changed or unavailable source requires a new
protocol version; no substitution or retry is authorized.
