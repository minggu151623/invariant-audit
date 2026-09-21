"""Pure in-memory E003-v2 source-to-eligible-to-selected adapter."""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any, Callable, Iterable, Mapping, Sequence

import source_v2

PROTOCOL_VERSION = "E003-v2"
PROTOCOL_COMMIT = "b9cae977cfa9640e1ad4064bfccbbebe945b81fb"
PROTOCOL_SHA256 = "2c7b76290f0d9128910f7f3c565a68374a432f9f2507976a8fd68e8495bcba15"

SPLITS = ("development", "calibration", "confirmatory")
EVENT_TYPES = ("IssuesEvent", "PullRequestEvent")
EVENT_TYPE_RANK = {name: index for index, name in enumerate(EVENT_TYPES)}
STATUS_ACTIONS = frozenset(("opened", "closed", "reopened"))

BASES_PER_EVENT_TYPE = 64
MAX_BASES_PER_REPOSITORY_EVENT_TYPE = 4
MIN_REPOSITORIES_OVERALL = 24
MIN_REPOSITORIES_PER_TYPE = 16

V1_E003_PATH = Path(__file__).resolve().parents[2] / "E003-external-transfer-validation" / "code" / "e003.py"
V1_E003_SHA256 = "cd21b21a69565385408edbcb5df1beb91a20534b452219662c1902c82dfa934c"

V1_ORACLE_PATH = Path(__file__).resolve().parents[2] / "E003-external-transfer-validation" / "code" / "oracle_e003.py"
V1_ORACLE_SHA256 = "0bfc2be8135d71bcaed8ccfd16fae38f53299023b9c3d185592af3ff628442d4"


class AdapterError(source_v2.SourceError):
    """Fail-closed error for v2 source adapter; no partial returns."""


def _load_pinned_v1_module(module_name: str, path: Path, expected_sha256: str) -> Any:
    if not path.is_file():
        raise AdapterError(f"Pinned reference file missing: {path}")
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != expected_sha256:
        raise AdapterError(f"Pinned reference {module_name} SHA-256 mismatch")
    spec = importlib.util.spec_from_file_location(module_name, str(path))
    if spec is None or spec.loader is None:
        raise AdapterError(f"Cannot create module spec for {module_name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


_V1_E003 = _load_pinned_v1_module("e003_v1_reference", V1_E003_PATH, V1_E003_SHA256)
_V1_ORACLE = _load_pinned_v1_module("oracle_e003_reference", V1_ORACLE_PATH, V1_ORACLE_SHA256)

# Pure unversioned helpers reused from pinned v1 reference module
project_event = _V1_E003.project_event
canonical_json_text = _V1_E003.canonical_json_text
input_sha256 = _V1_E003.input_sha256
_raw_label = _V1_E003._raw_label
_strict_decimal_id = _V1_E003._strict_decimal_id
reference_oracle = _V1_ORACLE.reference_oracle


@dataclass(frozen=True)
class SourceEvent:
    """Shallow frozen attributes; mutable nested dicts aren't immutable."""
    split: str
    source_file: str
    source_sha256: str
    source_line: int
    repo_id: str
    event_id: str
    event_type: str
    action: str
    payload: dict[str, Any] = field(repr=False)
    input_sha256: str

    @property
    def repo_id_integer(self) -> int:
        return int(self.repo_id)

    @property
    def event_id_integer(self) -> int:
        return int(self.event_id)

    @property
    def source_key(self) -> tuple[str, str, int, str]:
        return (self.split, self.source_file, self.source_line, self.event_id)


@dataclass(frozen=True)
class SplitScan:
    """Shallow frozen attributes; mutable nested dicts aren't immutable."""
    split: str
    raw_count: int
    unique_count: int
    collapsed_extras: int
    repo_ids: frozenset[str] = field(repr=False)
    eligible: tuple[SourceEvent, ...] = field(repr=False)
    selected: tuple[SourceEvent, ...] = field(repr=False)
    unselected: tuple[SourceEvent, ...] = field(repr=False)
    exclusion_counts: tuple[tuple[str, int], ...]

    def exclusions(self) -> dict[str, int]:
        return dict(self.exclusion_counts)


@dataclass(frozen=True)
class AdapterResult:
    """Shallow frozen attributes; mutable nested dicts aren't immutable."""
    scans: tuple[SplitScan, ...]
    shared_repo_ids: frozenset[str] = field(repr=False)
    selected_by_split: dict[str, tuple[SourceEvent, ...]] = field(repr=False)
    normalized: source_v2.Normalized = field(repr=False)

    def scan_for(self, split: str) -> SplitScan:
        for scan in self.scans:
            if scan.split == split:
                return scan
        raise AdapterError(f"result has no split: {split}")

    def eligible(self, split: str) -> tuple[SourceEvent, ...]:
        return self.scan_for(split).eligible

    def selected(self, split: str) -> tuple[SourceEvent, ...]:
        if split not in self.selected_by_split:
            raise AdapterError(f"result has no selected bases for split: {split}")
        return self.selected_by_split[split]

    def unselected(self, split: str) -> tuple[SourceEvent, ...]:
        return self.scan_for(split).unselected

    def exclusion_counts(self) -> dict[str, dict[str, int]]:
        return {scan.split: scan.exclusions() for scan in self.scans}


SourceBundle = AdapterResult


def selection_sort_key(event: SourceEvent) -> tuple[Any, ...]:
    return (
        EVENT_TYPE_RANK[event.event_type],
        event.repo_id_integer,
        event.event_id_integer,
        event.source_file,
        event.source_line,
    )


def select_bases(
    eligible_by_split: Mapping[str, Sequence[SourceEvent]],
) -> tuple[dict[str, tuple[SourceEvent, ...]], dict[str, tuple[SourceEvent, ...]]]:
    """Select deterministic bases per split enforcing quotas and repository diversity."""
    selected_by_split: dict[str, tuple[SourceEvent, ...]] = {}
    unselected_by_split: dict[str, tuple[SourceEvent, ...]] = {}
    seen_base_hashes: set[str] = set()

    for split, eligible in eligible_by_split.items():
        counts: Counter[tuple[str, str]] = Counter()
        selected: list[SourceEvent] = []
        for event in sorted(eligible, key=selection_sort_key):
            key = (event.repo_id, event.event_type)
            if counts[key] >= MAX_BASES_PER_REPOSITORY_EVENT_TYPE:
                continue
            target = sum(event.event_type == item.event_type for item in selected)
            if target >= BASES_PER_EVENT_TYPE:
                continue
            selected.append(event)
            counts[key] += 1

        for event_type in EVENT_TYPES:
            type_events = [event for event in selected if event.event_type == event_type]
            if len(type_events) != BASES_PER_EVENT_TYPE:
                raise AdapterError(
                    f"{split} cannot reach exact {event_type} base quota: got {len(type_events)}, expected {BASES_PER_EVENT_TYPE}"
                )

        repo_ids = {event.repo_id for event in selected}
        if len(repo_ids) < MIN_REPOSITORIES_OVERALL:
            raise AdapterError(
                f"{split} has fewer than {MIN_REPOSITORIES_OVERALL} selected repositories: got {len(repo_ids)}"
            )

        # Defense-in-depth: with BASES_PER_EVENT_TYPE=64 and MAX_BASES_PER_REPOSITORY_EVENT_TYPE=4,
        # reaching 64 bases mathematically requires at least ceil(64/4) = 16 distinct repositories.
        # This check confirms that structural invariant.
        for event_type in EVENT_TYPES:
            type_repo_ids = {event.repo_id for event in selected if event.event_type == event_type}
            if len(type_repo_ids) < MIN_REPOSITORIES_PER_TYPE:
                raise AdapterError(
                    f"{split} has fewer than {MIN_REPOSITORIES_PER_TYPE} repositories for {event_type}: got {len(type_repo_ids)}"
                )

        for event in selected:
            if event.input_sha256 in seen_base_hashes:
                raise AdapterError("duplicate selected base hash")
            seen_base_hashes.add(event.input_sha256)

        sorted_selected = tuple(sorted(selected, key=selection_sort_key))
        selected_keys = {event.source_key for event in sorted_selected}
        unselected = tuple(event for event in eligible if event.source_key not in selected_keys)

        selected_by_split[split] = sorted_selected
        unselected_by_split[split] = unselected

    return selected_by_split, unselected_by_split


def adapt_normalized(
    normalized: source_v2.Normalized,
    source_digests: Mapping[str, str],
    oracle_fn: Callable[[Mapping[str, Any]], Any] | None = None,
) -> AdapterResult:
    """Pure in-memory adapter from normalized records to eligible and selected bases."""
    if oracle_fn is None:
        oracle_fn = reference_oracle

    # Group unique retained records by split
    records_by_split: dict[str, list[source_v2.Record]] = defaultdict(list)
    for record in normalized.records:
        records_by_split[record.split].append(record)

    eligible_by_split: dict[str, list[SourceEvent]] = {}
    exclusions_by_split: dict[str, Counter[str]] = {}

    for s in normalized.summaries:
        split = s.split
        # 1. Validate raw = unique + collapsed
        if s.raw_count != s.unique_count + s.collapsed_extras:
            raise AdapterError(
                f"Split {split} normalization accounting mismatch: "
                f"raw ({s.raw_count}) != unique ({s.unique_count}) + collapsed ({s.collapsed_extras})"
            )

        unique_records = records_by_split[split]
        if len(unique_records) != s.unique_count:
            raise AdapterError(
                f"Split {split} record count mismatch: "
                f"retained ({len(unique_records)}) != summary unique ({s.unique_count})"
            )

        if split not in source_digests:
            raise AdapterError(f"Missing source digest for split: {split}")
        split_digest = source_digests[split]

        exclusions: Counter[str] = Counter()
        eligible: list[SourceEvent] = []

        for record in unique_records:
            try:
                obj = json.loads(record.raw.decode("utf-8"))
            except Exception as err:
                raise AdapterError(f"Failed to parse record JSON at {record.split}:{record.line}") from err

            event_type = obj.get("type")
            raw_payload = obj.get("payload")
            action = raw_payload.get("action") if type(raw_payload) is dict else None

            # Step 1: Type and Action
            if event_type not in EVENT_TYPES or action not in STATUS_ACTIONS:
                exclusions[
                    "raw_type_action:" + canonical_json_text(
                        [_raw_label(event_type), _raw_label(action)]
                    )
                ] += 1
                continue

            # Step 2: Projection
            projected, reason = project_event(obj)
            if projected is None:
                if reason is None:
                    raise AdapterError("projection returned no reason")
                exclusions[reason] += 1
                continue

            # Step 3: Oracle
            try:
                oracle_result = oracle_fn(projected)
            except Exception as err:
                raise AdapterError(f"Oracle failed at {record.split}:{record.line}") from err

            if not hasattr(oracle_result, "oracle_failure_set") or oracle_result.oracle_failure_set is None:
                raise AdapterError(
                    f"Malformed oracle result: missing oracle_failure_set at {record.split}:{record.line}"
                )

            failure_set = tuple(oracle_result.oracle_failure_set)
            if getattr(oracle_result, "schema_valid", False) is not True:
                exclusions["oracle_schema"] += 1
                continue
            if failure_set:
                exclusions["oracle_" + failure_set[0]] += 1
                continue
            if getattr(oracle_result, "truth", None) != 1:
                raise AdapterError(
                    f"Malformed oracle result: truth != 1 with schema_valid True and empty failure set at {record.split}:{record.line}"
                )

            # Step 4: Strict decimal IDs
            normalized_event_id = _strict_decimal_id(projected["id"])
            raw_repo = projected.get("repo")
            repo_id = _strict_decimal_id(raw_repo.get("id")) if type(raw_repo) is dict else None
            if normalized_event_id is None or repo_id is None:
                exclusions["common_schema"] += 1
                continue

            # Step 5: Cross-split repository isolation
            if repo_id in normalized.shared_repository_ids:
                exclusions["cross_split_repository"] += 1
                continue

            # Survived all filters -> eligible
            eligible.append(
                SourceEvent(
                    split=record.split,
                    source_file=record.filename,
                    source_sha256=split_digest,
                    source_line=record.line,
                    repo_id=repo_id,
                    event_id=normalized_event_id,
                    event_type=projected["type"],
                    action=projected["payload"]["action"],
                    payload=projected,
                    input_sha256=input_sha256(projected),
                )
            )

        # 2. Validate unique = excluded + eligible BEFORE selection
        excluded_count = sum(exclusions.values())
        eligible_count = len(eligible)
        if s.unique_count != excluded_count + eligible_count:
            raise AdapterError(
                f"Split {split} filter accounting mismatch: "
                f"unique ({s.unique_count}) != excluded ({excluded_count}) + eligible ({eligible_count})"
            )

        eligible_by_split[split] = eligible
        exclusions_by_split[split] = exclusions

    # Step 6: Selection
    selected_by_split, unselected_by_split = select_bases(eligible_by_split)

    # Step 7: Build split scans and result
    scans = []
    for s in normalized.summaries:
        split = s.split
        scans.append(
            SplitScan(
                split=split,
                raw_count=s.raw_count,
                unique_count=s.unique_count,
                collapsed_extras=s.collapsed_extras,
                repo_ids=s.repository_ids,
                eligible=tuple(eligible_by_split[split]),
                selected=selected_by_split[split],
                unselected=unselected_by_split[split],
                exclusion_counts=tuple(sorted(exclusions_by_split[split].items())),
            )
        )

    return AdapterResult(
        scans=tuple(scans),
        shared_repo_ids=normalized.shared_repository_ids,
        selected_by_split=selected_by_split,
        normalized=normalized,
    )


def adapt_sources(
    sources: Iterable[source_v2.SourceInput],
    oracle_fn: Callable[[Mapping[str, Any]], Any] | None = None,
    *,
    pinned: bool = False,
) -> AdapterResult:
    """Consume SourceInputs, normalize via source_v2, and return adapted result."""
    sources_tuple = tuple(sources)
    if not sources_tuple:
        raise AdapterError("no source inputs provided")

    if pinned:
        normalized = source_v2.normalize_pinned(sources_tuple)
    else:
        normalized = source_v2.normalize_sources(sources_tuple)

    source_digests = {s.split: s.expected_sha256 for s in sources_tuple}
    return adapt_normalized(normalized, source_digests, oracle_fn=oracle_fn)


def adapt_pinned(
    sources: Iterable[source_v2.SourceInput],
    oracle_fn: Callable[[Mapping[str, Any]], Any] | None = None,
) -> AdapterResult:
    """Full pinned inventory adapter."""
    return adapt_sources(sources, oracle_fn=oracle_fn, pinned=True)
