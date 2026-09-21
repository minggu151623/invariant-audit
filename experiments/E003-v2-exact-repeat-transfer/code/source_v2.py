"""Pure E003-v2 source normalization; no I/O, scoring, or v1 imports."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from hashlib import sha256
import json
import math
import re
import zlib

SPLITS = ("development", "calibration", "confirmatory")
PROTOCOL_COMMIT = "b9cae977cfa9640e1ad4064bfccbbebe945b81fb"
PROTOCOL_SHA256 = "2c7b76290f0d9128910f7f3c565a68374a432f9f2507976a8fd68e8495bcba15"
V1_MANIFEST_SHA256 = "683eef39cd26d2a7f6622689adc2cd9e357e78a770f77bf91e98513b859e4633"
V2_MANIFEST_SHA256 = "c6c43cbbc6f069d78c56c9d7b9c45a58120574c205f059c1fe1b0086f7f3fa47"
PINS = (
    ("2019-01-15-12.json.gz", 29278679, 67145,
     "ae451576f78417d75f135b29ee67ea8e666dc5f6cb16e78cef04e20342b42b50"),
    ("2020-01-15-12.json.gz", 46372480, 90940,
     "624a0d2a2fc575afb1e63bece53521e2b078ddfd1caf60026e313ad36d83cddd"),
    ("2021-01-15-12.json.gz", 61805367, 117780,
     "a4a80c97153c691866d52b7e06ea0051f2449f0c6f8060dad9f441a69cd13788"),
)


class SourceError(ValueError):
    """Fail closed, with no partial return or source values in messages."""


def decimal_id(value):
    if type(value) is int and value >= 0:
        return str(value)
    if type(value) is str and re.fullmatch(r"0|[1-9][0-9]*", value):
        return value
    raise SourceError("invalid decimal ID")


def _pairs(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise SourceError("duplicate JSON key")
        obj[key] = value
    return obj


def _constant(_):
    raise SourceError("nonfinite JSON number")


def _finite_float(text):
    value = float(text)
    if not math.isfinite(value):
        raise SourceError("overflowing JSON number")
    return value


def parse_record(raw):
    try:
        obj = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs,
                         parse_constant=_constant, parse_float=_finite_float)
        # Validate all strings, including unused payload fields and object keys.
        json.dumps(obj, ensure_ascii=False, allow_nan=False).encode("utf-8")
        if type(obj) is not dict or type(obj.get("type")) is not str:
            raise SourceError("object and string event type required")
        decimal_id(obj.get("id"))
        return obj
    except (ValueError, UnicodeError, RecursionError, OverflowError):
        raise SourceError("invalid JSON record") from None


@dataclass(frozen=True)
class SourceInput:
    split: str
    filename: str
    compressed: bytes = field(repr=False)
    expected_bytes: int
    expected_sha256: str
    expected_records: int


@dataclass(frozen=True)
class Record:
    split: str
    filename: str
    line: int
    event_id: str = field(repr=False)
    event_type: str
    raw: bytes = field(repr=False)


@dataclass(frozen=True)
class Summary:
    split: str
    raw_count: int
    unique_count: int
    collapsed_extras: int
    repeated_groups: int
    maximum_multiplicity: int
    first_collision: tuple[int, int] | None
    extras_by_type: tuple[tuple[str, int], ...]
    repository_ids: frozenset[str] = field(repr=False)


@dataclass(frozen=True)
class Normalized:
    records: tuple[Record, ...] = field(repr=False)
    summaries: tuple[Summary, ...]
    shared_repository_ids: frozenset[str] = field(repr=False)


def _decompress(data):
    decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
    try:
        plain = decoder.decompress(data) + decoder.flush()
    except zlib.error:
        raise SourceError("malformed gzip") from None
    if not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
        raise SourceError("truncated or trailing gzip data")
    return plain


def normalize_sources(sources):
    """Pure atomic return. Caller supplies pins; production must use pinned API.

    Partial development scans may contain development/calibration only, in order.
    This API is also used with explicitly synthetic fixtures in development tests.
    """
    sources = tuple(sources)
    splits = tuple(s.split for s in sources)
    if not splits or splits != tuple(s for s in SPLITS if s in splits):
        raise SourceError("invalid split order or repeated split")
    # Validate every compressed payload before parsing any of them.
    for s in sources:
        if (type(s.compressed) is not bytes or type(s.expected_bytes) is not int
                or type(s.expected_records) is not int or s.expected_records < 0
                or len(s.compressed) != s.expected_bytes
                or sha256(s.compressed).hexdigest() != s.expected_sha256):
            raise SourceError("source pin mismatch")
    seen, retained, summaries = {}, [], []
    for source in sources:
        counts, extras, repos = Counter(), Counter(), set()
        raw_count, unique, first_collision = 0, 0, None
        for line, raw in enumerate(_decompress(source.compressed).split(b"\n"), 1):
            raw = raw[:-1] if raw.endswith(b"\r") else raw
            if not raw.strip():
                continue
            raw_count += 1
            try:
                obj = parse_record(raw)
            except SourceError:
                raise SourceError(f"invalid record at {source.split}:{line}") from None
            key = decimal_id(obj["id"])
            counts[key] += 1
            if key in seen:
                previous = seen[key]
                if previous.split != source.split:
                    raise SourceError(f"cross-shard ID at {source.split}:{line}")
                if previous.raw != raw:
                    raise SourceError(f"nonidentical repeated ID at {source.split}:{line}")
                if first_collision is None:
                    first_collision = (previous.line, line)
                extras[obj["type"]] += 1
                continue
            record = Record(source.split, source.filename, line, key, obj["type"], raw)
            seen[key] = record
            retained.append(record)
            unique += 1
            repo = obj.get("repo")
            if type(repo) is dict:
                try:
                    repos.add(decimal_id(repo.get("id")))
                except SourceError:
                    pass  # Not a selected-base eligibility decision.
        if raw_count != source.expected_records:
            raise SourceError("source nonempty record count mismatch")
        if raw_count - unique != sum(extras.values()):
            raise SourceError("normalization accounting mismatch")
        summaries.append(Summary(source.split, raw_count, unique, raw_count - unique,
                                 sum(n > 1 for n in counts.values()),
                                 max(counts.values(), default=0), first_collision,
                                 tuple(sorted(extras.items())), frozenset(repos)))
    repo_occurrences = Counter(repo for s in summaries for repo in s.repository_ids)
    return Normalized(tuple(retained), tuple(summaries),
                      frozenset(repo for repo, n in repo_occurrences.items() if n > 1))


def normalize_pinned(sources):
    """Full production inventory gate, not a performance runner/review gate."""
    sources = tuple(sources)
    if len(sources) != 3:
        raise SourceError("full pinned inventory required")
    for source, split, pin in zip(sources, SPLITS, PINS):
        name, size, count, digest = pin
        if (source.split, source.filename, source.expected_bytes,
            source.expected_records, source.expected_sha256) != (split, name, size, count, digest):
            raise SourceError("pinned inventory identity mismatch")
    result = normalize_sources(sources)
    for s, expected in zip(result.summaries, ((67145,67145,0), (90940,90940,0), (117780,117243,537))):
        if (s.raw_count, s.unique_count, s.collapsed_extras) != expected:
            raise SourceError("E004-informed count regression")
    final = result.summaries[-1]
    if final.repeated_groups != 537 or final.maximum_multiplicity != 2:
        raise SourceError("E004-informed multiplicity regression")
    return result


def derive_manifest_v2(original):
    """Return bytes only. Caller must exclusively create or verify an external file."""
    if sha256(original).hexdigest() != V1_MANIFEST_SHA256:
        raise SourceError("original manifest identity mismatch")
    obj = json.loads(original)
    obj["protocol_id"] = "E003-v2"
    encoded = (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()
    if sha256(encoded).hexdigest() != V2_MANIFEST_SHA256:
        raise SourceError("derived manifest identity mismatch")
    return encoded
