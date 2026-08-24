"""Side-effect-free, standard-library implementation of locked E001-v1.

The reference oracle and M1 predicates are intentionally maintained as two
separate implementations. The evaluator keeps oracle metadata in ``Case``
objects and passes only the exact sanitized payload to every validator.
"""

from __future__ import annotations

import copy
import csv
import hashlib
import io
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Mapping, Sequence


PROTOCOL_VERSION = "E001-v1"
PROTOCOL_COMMIT = "d8b26d21e9692ace19436d78461460940043f5c7"
PROTOCOL_PATH = "experiments/E001-synthetic-invariant-calibration/protocol.md"

FAMILIES = ("S1", "S2", "T1", "T2")
METHODS = ("B0", "M1", "M1-no-semantic", "M1-no-state", "M1-no-calibration")
CALIBRATED_METHODS = ("B0", "M1", "M1-no-semantic", "M1-no-state")
PRIMARY_METHODS = ("B0", "M1")
ABLATION_METHODS = ("M1-no-semantic", "M1-no-state", "M1-no-calibration")
METHOD_FAMILIES = {
    "M1": FAMILIES,
    "M1-no-semantic": ("T1", "T2"),
    "M1-no-state": ("S1", "S2"),
    "M1-no-calibration": FAMILIES,
}
SPLIT_SEEDS = {
    "development": (101, 102),
    "calibration": (201, 202),
    "confirmatory": (301, 302, 303, 304),
}
BASE_BUNDLES_PER_SEED = 16
CASES_PER_BASE = 8
BOOTSTRAP_REPLICATES = 10_000
BOOTSTRAP_CONFIDENCE = 0.95
BOOTSTRAP_CLUSTER_COUNT = 64
PUBLIC_LARGE_FILE_LIMIT = 52_428_800

ALLOWED_STATES = frozenset(("pending", "active", "closed"))
ALLOWED_TRANSITIONS = frozenset(
    (("pending", "active"), ("active", "active"), ("active", "closed"))
)
PAYLOAD_FIELDS = frozenset(("meta", "entities", "ledger", "events"))
ORACLE_ONLY_FIELDS = frozenset(
    (
        "base_case_id",
        "calibration_label",
        "case_id",
        "fault_id",
        "input_sha256",
        "oracle_manifest",
        "oracle_manifest_sha256",
        "oracle_reason",
        "seed",
        "split",
        "target_family",
        "transform",
        "truth",
    )
)
METRIC_NAMES = (
    "fpr",
    "fnr",
    "precision",
    "recall",
    "specificity",
    "f1",
    "balanced_accuracy",
    "brier",
    "ece",
)
SUBGROUPS = ("overall",) + FAMILIES
NA = "NA"

PREDICTION_FIELDS = (
    "run_id",
    "protocol_path",
    "protocol_commit",
    "method",
    "split",
    "seed",
    "base_case_id",
    "case_id",
    "target_family",
    "truth",
    "decision",
    "raw_score",
    "p_valid",
    "input_sha256",
    "oracle_manifest_sha256",
    "status",
)
METRIC_FIELDS = (
    "method",
    "split",
    "subgroup",
    "support",
    "TP",
    "TN",
    "FP",
    "FN",
    "FPR",
    "FNR",
    "precision",
    "recall",
    "specificity",
    "F1",
    "balanced_accuracy",
    "Brier",
    "ECE",
    "denominators",
    "ece_bins",
    "intervals",
    "interval_reference",
    "ci_lower",
    "ci_upper",
    "ci_usable_replicates",
    "ci_status",
    "paired_delta",
    "paired_deltas",
    "paired_ci_lower",
    "paired_ci_upper",
    "paired_ci_usable_replicates",
    "paired_ci_status",
    "paired_intervals",
    "paired_interval_reference",
)
BOOTSTRAP_FIELDS = (
    "row_type",
    "replicate",
    "method",
    "method_pair",
    "subgroup",
    "metric",
    "value",
    "delta_m1_minus_b0",
    "ci_lower",
    "ci_upper",
    "usable_replicates",
    "status",
)


class ProtocolError(ValueError):
    """Raised when an E001 invariant or output contract is violated."""


@dataclass(frozen=True)
class ValidationResult:
    decision: bool
    raw_score: int
    failed_families: tuple[str, ...] = ()


@dataclass(frozen=True)
class OracleResult:
    family_passes: tuple[tuple[str, bool], ...]
    truth: int
    reason: str


@dataclass(frozen=True)
class Case:
    split: str
    seed: int
    base_index: int
    base_case_id: str
    case_id: str
    target_family: str
    valid: bool
    truth: int
    fault_id: str | None
    oracle_reason: str
    family_passes: tuple[tuple[str, bool], ...]
    payload: dict[str, Any]
    input_sha256: str


@dataclass(frozen=True)
class CalibrationLookup:
    method: str
    by_score: tuple[tuple[int, float], ...]
    global_p_valid: float

    def lookup(self, raw_score: int) -> float:
        for score, probability in self.by_score:
            if score == raw_score:
                return probability
        return self.global_p_valid

    def record(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "by_score": [[score, probability] for score, probability in self.by_score],
            "global_p_valid": self.global_p_valid,
        }


@dataclass(frozen=True)
class BootstrapResult:
    replicate_count: int
    cluster_ids: tuple[str, ...]
    available_methods: tuple[str, ...]
    method_values: tuple[tuple[str, str, str, tuple[float | None, ...]], ...]
    delta_values: tuple[tuple[str, str, tuple[float | None, ...]], ...]
    intervals: tuple[dict[str, Any], ...]

    @property
    def metric_values(self) -> tuple[tuple[str, str, str, tuple[float | None, ...]], ...]:
        """Backward-compatible name for the retained method series."""

        return self.method_values

    def method_series(
        self, method: str, subgroup: str, metric: str
    ) -> tuple[float | None, ...]:
        for stored_method, stored_subgroup, stored_metric, values in self.method_values:
            if (stored_method, stored_subgroup, stored_metric) == (
                method,
                subgroup,
                metric,
            ):
                return values
        raise KeyError((method, subgroup, metric))

    def delta_series(self, subgroup: str, metric: str) -> tuple[float | None, ...]:
        for stored_subgroup, stored_metric, values in self.delta_values:
            if (stored_subgroup, stored_metric) == (subgroup, metric):
                return values
        raise KeyError((subgroup, metric))

    def interval(self, method: str | None, subgroup: str, metric: str) -> dict[str, Any]:
        for row in self.intervals:
            if (
                row["method"] == method
                and row["subgroup"] == subgroup
                and row["metric"] == metric
            ):
                return row
        raise KeyError((method, subgroup, metric))


@dataclass(frozen=True)
class PipelineArtifacts:
    run_id: str
    sanity: dict[str, Any]
    raw_rows: tuple[dict[str, Any], ...]
    calibration_lookups: tuple[CalibrationLookup, ...]
    prediction_rows: tuple[dict[str, Any], ...]
    metric_rows: tuple[dict[str, Any], ...]
    bootstrap: BootstrapResult
    result_markdown: str
    serialized_outputs: tuple[tuple[str, bytes], ...]

    def serialized(self, name: str) -> bytes:
        for stored_name, content in self.serialized_outputs:
            if stored_name == name:
                return content
        raise KeyError(name)

    def hashes(self) -> dict[str, str]:
        lookup_records = [lookup.record() for lookup in self.calibration_lookups]
        delta_rows = list(iter_bootstrap_rows(self.bootstrap, row_type="replicate"))
        interval_rows = list(iter_bootstrap_rows(self.bootstrap, row_type="interval"))
        return {
            "raw_predictions": sha256_hex(canonical_json_bytes(list(self.raw_rows))),
            "calibration_lookups": sha256_hex(canonical_json_bytes(lookup_records)),
            "prediction_rows": sha256_hex(canonical_json_bytes(list(self.prediction_rows))),
            "metric_rows": sha256_hex(canonical_json_bytes(list(self.metric_rows))),
            "bootstrap_delta_rows": sha256_hex(canonical_json_bytes(delta_rows)),
            "bootstrap_intervals": sha256_hex(canonical_json_bytes(interval_rows)),
            "result_markdown": sha256_hex(self.result_markdown.encode("utf-8")),
            **{
                f"serialized_{name}": sha256_hex(content)
                for name, content in self.serialized_outputs
            },
        }


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def canonical_json_text(value: Any) -> str:
    return canonical_json_bytes(value).decode("utf-8")


def sha256_hex(value: bytes | str) -> str:
    if isinstance(value, str):
        value = value.encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def payload_sha256(payload: Mapping[str, Any]) -> str:
    return sha256_hex(canonical_json_bytes(payload))


def _to_serializable(value: Any) -> Any:
    if value is None:
        return NA
    if isinstance(value, dict):
        return {key: _to_serializable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_serializable(item) for item in value]
    return value


def csv_value(value: Any) -> Any:
    """Serialize missing/undefined values as literal ``NA``."""

    if value is None:
        return NA
    if isinstance(value, (dict, list, tuple)):
        return canonical_json_text(_to_serializable(value))
    if isinstance(value, bool):
        return "true" if value else "false"
    return value


def serialize_jsonl(rows: Sequence[Mapping[str, Any]]) -> bytes:
    output = io.StringIO(newline="\n")
    for row in rows:
        output.write(canonical_json_text(row))
        output.write("\n")
    return output.getvalue().encode("utf-8")


def serialize_csv(rows: Iterable[Mapping[str, Any]], fieldnames: Sequence[str]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(
        output, fieldnames=fieldnames, extrasaction="raise", lineterminator="\n"
    )
    writer.writeheader()
    for row in rows:
        writer.writerow({field: csv_value(row.get(field)) for field in fieldnames})
    return output.getvalue().encode("utf-8")


def deterministic_amount(split: str, seed: int, base_index: int, draw_index: int) -> int:
    if split not in SPLIT_SEEDS or seed not in SPLIT_SEEDS[split]:
        raise ProtocolError("amount draw has an unassigned split/seed")
    if not 0 <= base_index < BASE_BUNDLES_PER_SEED or not 0 <= draw_index < 4:
        raise ProtocolError("amount draw index is out of range")
    material = f"{PROTOCOL_VERSION}|value|{split}|{seed}|{base_index}|{draw_index}"
    digest = hashlib.sha256(material.encode("utf-8")).digest()
    u64 = int.from_bytes(digest[:8], "big", signed=False)
    return 200 + (u64 % 300)


def _base_payload(split: str, seed: int, base_index: int) -> dict[str, Any]:
    amounts = [deterministic_amount(split, seed, base_index, index) for index in range(4)]
    entities = [
        {
            "entity_id": f"entity-{index}",
            "current_state": "closed" if index < 3 else "active",
            "revision": 2 if index < 3 else 1,
        }
        for index in range(4)
    ]
    ledger = [
        {
            "entry_id": f"ledger-{index}",
            "entity_id": f"entity-{index}",
            "amount_cents": amount,
        }
        for index, amount in enumerate(amounts)
    ]
    events = [
        {
            "event_id": "event-0-0",
            "entity_id": "entity-0",
            "from_state": "pending",
            "to_state": "active",
            "revision": 1,
        },
        {
            "event_id": "event-0-1",
            "entity_id": "entity-0",
            "from_state": "active",
            "to_state": "closed",
            "revision": 2,
        },
        {
            "event_id": "event-1-0",
            "entity_id": "entity-1",
            "from_state": "pending",
            "to_state": "active",
            "revision": 1,
        },
        {
            "event_id": "event-1-1",
            "entity_id": "entity-1",
            "from_state": "active",
            "to_state": "closed",
            "revision": 2,
        },
        {
            "event_id": "event-2-0",
            "entity_id": "entity-2",
            "from_state": "pending",
            "to_state": "active",
            "revision": 1,
        },
        {
            "event_id": "event-2-1",
            "entity_id": "entity-2",
            "from_state": "active",
            "to_state": "closed",
            "revision": 2,
        },
        {
            "event_id": "event-3-0",
            "entity_id": "entity-3",
            "from_state": "pending",
            "to_state": "active",
            "revision": 1,
        },
    ]
    return {
        "meta": {"schema_version": PROTOCOL_VERSION, "declared_total_cents": sum(amounts)},
        "entities": entities,
        "ledger": ledger,
        "events": events,
    }


# ---------------------------------------------------------------------------
# Independent reference oracle. These functions are not used by M1 below.


def reference_s1(payload: Mapping[str, Any]) -> bool:
    try:
        entities = payload["entities"]
        ledger = payload["ledger"]
        events = payload["events"]
        entity_ids = [row["entity_id"] for row in entities]
        ledger_ids = [row["entry_id"] for row in ledger]
        event_ids = [row["event_id"] for row in events]
        entity_set = set(entity_ids)
        return (
            len(entity_ids) == len(entity_set)
            and len(ledger_ids) == len(set(ledger_ids))
            and len(event_ids) == len(set(event_ids))
            and all(row["entity_id"] in entity_set for row in ledger)
            and all(row["entity_id"] in entity_set for row in events)
        )
    except (KeyError, TypeError, AttributeError):
        return False


def reference_s2(payload: Mapping[str, Any]) -> bool:
    try:
        declared = payload["meta"]["declared_total_cents"]
        return declared == sum(row["amount_cents"] for row in payload["ledger"])
    except (KeyError, TypeError, AttributeError):
        return False


def reference_t1(payload: Mapping[str, Any]) -> bool:
    """Reference path oracle: ordered continuity plus legal terminal behavior."""

    try:
        entity_ids = {row["entity_id"] for row in payload["entities"]}
        paths: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
        for event in payload["events"]:
            if event["entity_id"] not in entity_ids:
                return False
            paths[event["entity_id"]].append(event)
        for entity_id in entity_ids:
            sequence = paths[entity_id]
            if not sequence:
                return False
            current = "pending"
            for event in sequence:
                if event["from_state"] != current:
                    return False
                if (event["from_state"], event["to_state"]) not in ALLOWED_TRANSITIONS:
                    return False
                if current == "closed":
                    return False
                current = event["to_state"]
        return True
    except (KeyError, TypeError, AttributeError):
        return False


def reference_t2(payload: Mapping[str, Any]) -> bool:
    try:
        entities = payload["entities"]
        events = payload["events"]
        entity_rows = {row["entity_id"]: row for row in entities}
        if len(entity_rows) != len(entities):
            return False
        paths: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
        for event in events:
            if event["entity_id"] not in entity_rows:
                return False
            paths[event["entity_id"]].append(event)
        for entity_id, entity in entity_rows.items():
            sequence = paths[entity_id]
            if not sequence:
                return False
            revisions = [event["revision"] for event in sequence]
            if revisions != list(range(1, len(sequence) + 1)):
                return False
            if entity["revision"] != revisions[-1]:
                return False
            if entity["current_state"] != sequence[-1]["to_state"]:
                return False
        return True
    except (KeyError, TypeError, AttributeError):
        return False


REFERENCE_CHECKS: dict[str, Callable[[Mapping[str, Any]], bool]] = {
    "S1": reference_s1,
    "S2": reference_s2,
    "T1": reference_t1,
    "T2": reference_t2,
}


def reference_oracle(payload: Mapping[str, Any]) -> OracleResult:
    passes = {family: bool(REFERENCE_CHECKS[family](payload)) for family in FAMILIES}
    failed = tuple(family for family in FAMILIES if not passes[family])
    return OracleResult(
        family_passes=tuple((family, passes[family]) for family in FAMILIES),
        truth=int(not failed),
        reason="all families pass" if not failed else f"failed families: {','.join(failed)}",
    )


# ---------------------------------------------------------------------------
# Exact generator and recipe application.


def _apply_recipe(
    base_payload: Mapping[str, Any], family: str, valid: bool
) -> tuple[dict[str, Any], str | None]:
    payload = copy.deepcopy(base_payload)
    if family == "S1" and valid:
        entities = {row["entity_id"]: row for row in payload["entities"]}
        ledger = {row["entry_id"]: row for row in payload["ledger"]}
        events = {row["event_id"]: row for row in payload["events"]}
        payload["entities"] = [entities[key] for key in ("entity-2", "entity-0", "entity-3", "entity-1")]
        payload["ledger"] = [ledger[key] for key in ("ledger-3", "ledger-1", "ledger-0", "ledger-2")]
        payload["events"] = [
            events[key]
            for key in (
                "event-2-0", "event-0-0", "event-3-0", "event-1-0",
                "event-2-1", "event-0-1", "event-1-1",
            )
        ]
        return payload, None
    if family == "S1":
        for row in payload["ledger"]:
            if row["entry_id"] == "ledger-1":
                row["entry_id"] = "ledger-0"
                return payload, "S1-ledger-entry-id-collision"
    if family == "S2" and valid:
        new_ledger: list[dict[str, Any]] = []
        for row in payload["ledger"]:
            if row["entry_id"] != "ledger-0":
                new_ledger.append(row)
                continue
            amount = row["amount_cents"]
            first = amount // 2
            new_ledger.extend(
                (
                    {"entry_id": "ledger-0a", "entity_id": "entity-0", "amount_cents": first},
                    {"entry_id": "ledger-0b", "entity_id": "entity-0", "amount_cents": amount - first},
                )
            )
        payload["ledger"] = new_ledger
        return payload, None
    if family == "S2":
        for row in payload["ledger"]:
            if row["entry_id"] == "ledger-1":
                row["amount_cents"] += 1
                return payload, "S2-ledger-amount-conservation"
    if family == "T1" and valid:
        events = {row["event_id"]: row for row in payload["events"]}
        payload["events"] = [
            events[key]
            for key in (
                "event-1-0", "event-0-0", "event-2-0", "event-0-1",
                "event-1-1", "event-2-1", "event-3-0",
            )
        ]
        return payload, None
    if family == "T1":
        for row in payload["events"]:
            if row["event_id"] == "event-0-1":
                row["to_state"] = "pending"
        for row in payload["entities"]:
            if row["entity_id"] == "entity-0":
                row["current_state"] = "pending"
        return payload, "T1-illegal-transition"
    if family == "T2" and valid:
        payload["events"].append(
            {
                "event_id": "event-3-1",
                "entity_id": "entity-3",
                "from_state": "active",
                "to_state": "active",
                "revision": 2,
            }
        )
        for row in payload["entities"]:
            if row["entity_id"] == "entity-3":
                row["revision"] = 2
        return payload, None
    if family == "T2":
        for row in payload["events"]:
            if row["event_id"] == "event-0-1":
                row["revision"] = 1
                return payload, "T2-revision-sequence"
    raise ProtocolError(f"unhandled recipe {family}/{valid}")


def _expected_recipe_payload(
    base_payload: Mapping[str, Any], family: str, valid: bool
) -> tuple[dict[str, Any], str | None]:
    """Independently reconstruct the locked recipe for runtime footprint checks.

    This is deliberately separate from _apply_recipe. It is a protocol
    manifest implementation, not an oracle or validator, and must continue to
    disagree with a faulty generator rather than inheriting its mutation.
    """

    payload = copy.deepcopy(base_payload)
    if family == "S1" and valid:
        entities = {row["entity_id"]: row for row in payload["entities"]}
        ledger = {row["entry_id"]: row for row in payload["ledger"]}
        events = {row["event_id"]: row for row in payload["events"]}
        payload["entities"] = [
            entities[key] for key in ("entity-2", "entity-0", "entity-3", "entity-1")
        ]
        payload["ledger"] = [
            ledger[key] for key in ("ledger-3", "ledger-1", "ledger-0", "ledger-2")
        ]
        payload["events"] = [
            events[key]
            for key in (
                "event-2-0", "event-0-0", "event-3-0", "event-1-0",
                "event-2-1", "event-0-1", "event-1-1",
            )
        ]
        return payload, None
    if family == "S1" and not valid:
        payload["ledger"][1]["entry_id"] = "ledger-0"
        return payload, "S1-ledger-entry-id-collision"
    if family == "S2" and valid:
        original = payload["ledger"][0]
        first = original["amount_cents"] // 2
        payload["ledger"] = [
            {"entry_id": "ledger-0a", "entity_id": "entity-0", "amount_cents": first},
            {
                "entry_id": "ledger-0b",
                "entity_id": "entity-0",
                "amount_cents": original["amount_cents"] - first,
            },
            *payload["ledger"][1:],
        ]
        return payload, None
    if family == "S2" and not valid:
        payload["ledger"][1]["amount_cents"] += 1
        return payload, "S2-ledger-amount-conservation"
    if family == "T1" and valid:
        events = {row["event_id"]: row for row in payload["events"]}
        payload["events"] = [
            events[key]
            for key in (
                "event-1-0", "event-0-0", "event-2-0", "event-0-1",
                "event-1-1", "event-2-1", "event-3-0",
            )
        ]
        return payload, None
    if family == "T1" and not valid:
        payload["events"][1]["to_state"] = "pending"
        payload["entities"][0]["current_state"] = "pending"
        return payload, "T1-illegal-transition"
    if family == "T2" and valid:
        payload["events"].append(
            {
                "event_id": "event-3-1",
                "entity_id": "entity-3",
                "from_state": "active",
                "to_state": "active",
                "revision": 2,
            }
        )
        payload["entities"][3]["revision"] = 2
        return payload, None
    if family == "T2" and not valid:
        payload["events"][1]["revision"] = 1
        return payload, "T2-revision-sequence"
    raise ProtocolError(f"unhandled expected recipe {family}/{valid}")


def _case_from_payload(
    split: str,
    seed: int,
    base_index: int,
    family: str,
    valid: bool,
    payload: dict[str, Any],
    fault_id: str | None,
) -> Case:
    base_case_id = f"{split}-{seed}-{base_index:02d}"
    case_id = f"{base_case_id}-{family}-{'valid' if valid else 'invalid'}"
    oracle = reference_oracle(payload)
    failed = tuple(family_id for family_id, passed in oracle.family_passes if not passed)
    expected_failed = () if valid else (family,)
    if oracle.truth != int(valid) or failed != expected_failed:
        raise ProtocolError(f"reference oracle mismatch for {case_id}: {oracle}")
    return Case(
        split=split,
        seed=seed,
        base_index=base_index,
        base_case_id=base_case_id,
        case_id=case_id,
        target_family=family,
        valid=valid,
        truth=oracle.truth,
        fault_id=fault_id,
        oracle_reason=oracle.reason,
        family_passes=oracle.family_passes,
        payload=payload,
        input_sha256=sha256_hex(canonical_json_bytes(payload)),
    )


def generate_base_payload(split: str, seed: int, base_index: int) -> dict[str, Any]:
    payload = _base_payload(split, seed, base_index)
    if reference_oracle(payload).truth != 1:
        raise ProtocolError("base payload failed the independent reference oracle")
    return payload


def generate_split(split: str) -> list[Case]:
    if split not in SPLIT_SEEDS:
        raise ProtocolError(f"unknown split: {split}")
    cases: list[Case] = []
    for seed in SPLIT_SEEDS[split]:
        for base_index in range(BASE_BUNDLES_PER_SEED):
            base = generate_base_payload(split, seed, base_index)
            for family in FAMILIES:
                positive, positive_fault = _apply_recipe(base, family, True)
                negative, negative_fault = _apply_recipe(base, family, False)
                cases.append(_case_from_payload(split, seed, base_index, family, True, positive, positive_fault))
                cases.append(_case_from_payload(split, seed, base_index, family, False, negative, negative_fault))
    return cases


def generate_all_splits() -> dict[str, list[Case]]:
    return {split: generate_split(split) for split in SPLIT_SEEDS}


def _case_record(case: Case) -> dict[str, Any]:
    return {
        "split": case.split,
        "seed": case.seed,
        "base_index": case.base_index,
        "base_case_id": case.base_case_id,
        "case_id": case.case_id,
        "target_family": case.target_family,
        "valid": case.valid,
        "truth": case.truth,
        "fault_id": case.fault_id,
        "oracle_reason": case.oracle_reason,
        "family_passes": dict(case.family_passes),
        "payload": case.payload,
        "input_sha256": case.input_sha256,
    }


def dataset_canonical_bytes(cases_by_split: Mapping[str, Sequence[Case]]) -> bytes:
    records: list[dict[str, Any]] = []
    for split in SPLIT_SEEDS:
        records.extend(_case_record(case) for case in cases_by_split[split])
    return canonical_json_bytes(records)


def dataset_sha256(cases_by_split: Mapping[str, Sequence[Case]]) -> str:
    return sha256_hex(dataset_canonical_bytes(cases_by_split))


def oracle_manifest(cases: Sequence[Case]) -> dict[str, Any]:
    return {
        "protocol_version": PROTOCOL_VERSION,
        "cases": [
            {
                "base_case_id": case.base_case_id,
                "case_id": case.case_id,
                "target_family": case.target_family,
                "truth": case.truth,
                "fault_id": case.fault_id,
                "oracle_reason": case.oracle_reason,
                "family_passes": dict(case.family_passes),
            }
            for case in cases
        ],
    }


def oracle_manifest_sha256(cases: Sequence[Case]) -> str:
    return sha256_hex(canonical_json_bytes(oracle_manifest(cases)))


# ---------------------------------------------------------------------------
# Exact nested schema and validator implementations.


def _is_int(value: Any) -> bool:
    return type(value) is int


def _is_identifier(value: Any) -> bool:
    return (
        type(value) is str
        and bool(value)
        and value.isascii()
        and all(character.isalnum() or character in "-_" for character in value)
    )


def _exact_keys(value: Any, expected: set[str]) -> bool:
    return type(value) is dict and set(value) == expected


def _exact_schema(payload: Any) -> bool:
    """Reject malformed, vacuous, extra, or unexpected nested structures."""

    try:
        if not _exact_keys(payload, set(PAYLOAD_FIELDS)):
            return False
        meta = payload["meta"]
        if not _exact_keys(meta, {"schema_version", "declared_total_cents"}):
            return False
        if meta["schema_version"] != PROTOCOL_VERSION or not _is_int(meta["declared_total_cents"]):
            return False
        entities = payload["entities"]
        ledger = payload["ledger"]
        events = payload["events"]
        if type(entities) is not list or len(entities) != 4:
            return False
        if type(ledger) is not list or len(ledger) not in (4, 5):
            return False
        if type(events) is not list or len(events) not in (7, 8):
            return False
        for entity in entities:
            if not _exact_keys(entity, {"entity_id", "current_state", "revision"}):
                return False
            if (
                not _is_identifier(entity["entity_id"])
                or entity["current_state"] not in ALLOWED_STATES
                or not _is_int(entity["revision"])
                or entity["revision"] < 1
            ):
                return False
        for row in ledger:
            if not _exact_keys(row, {"entry_id", "entity_id", "amount_cents"}):
                return False
            if (
                not _is_identifier(row["entry_id"])
                or not _is_identifier(row["entity_id"])
                or not _is_int(row["amount_cents"])
                or not 100 <= row["amount_cents"] <= 500
            ):
                return False
        for event in events:
            if not _exact_keys(event, {"event_id", "entity_id", "from_state", "to_state", "revision"}):
                return False
            if (
                not _is_identifier(event["event_id"])
                or not _is_identifier(event["entity_id"])
                or event["from_state"] not in ALLOWED_STATES
                or event["to_state"] not in ALLOWED_STATES
                or not _is_int(event["revision"])
                or event["revision"] < 1
            ):
                return False
        return True
    except (AttributeError, KeyError, TypeError, ValueError):
        return False


def sanitize_payload(payload: Any) -> dict[str, Any] | None:
    if not _exact_schema(payload):
        return None
    try:
        return copy.deepcopy(payload)
    except (TypeError, ValueError):
        return None


def payload_is_sanitized(payload: Any) -> bool:
    return sanitize_payload(payload) is not None


# ---------------------------------------------------------------------------
# Independently maintained M1 predicates. Do not alias the reference checks.


def _m1_s1(payload: Mapping[str, Any]) -> bool:
    try:
        entity_ids = [row["entity_id"] for row in payload["entities"]]
        known = set(entity_ids)
        ledger_ids = [row["entry_id"] for row in payload["ledger"]]
        event_ids = [row["event_id"] for row in payload["events"]]
        if len(entity_ids) != len(known):
            return False
        if len(ledger_ids) != len(set(ledger_ids)) or len(event_ids) != len(set(event_ids)):
            return False
        if any(row["entity_id"] not in known for row in payload["ledger"]):
            return False
        if any(row["entity_id"] not in known for row in payload["events"]):
            return False
        return True
    except (AttributeError, KeyError, TypeError, ValueError):
        return False


def _m1_s2(payload: Mapping[str, Any]) -> bool:
    try:
        total = 0
        for row in payload["ledger"]:
            total += row["amount_cents"]
        return payload["meta"]["declared_total_cents"] == total
    except (AttributeError, KeyError, TypeError, ValueError):
        return False


def _m1_t1(payload: Mapping[str, Any]) -> bool:
    """M1's own ordered transition-path implementation."""

    try:
        entity_rows = {row["entity_id"]: row for row in payload["entities"]}
        if len(entity_rows) != len(payload["entities"]):
            return False
        paths: dict[str, list[Mapping[str, Any]]] = {entity_id: [] for entity_id in entity_rows}
        for event in payload["events"]:
            entity_id = event["entity_id"]
            if entity_id not in paths:
                return False
            paths[entity_id].append(event)
        for entity_id in entity_rows:
            sequence = paths[entity_id]
            if not sequence:
                return False
            previous_to = "pending"
            for event in sequence:
                if event["from_state"] != previous_to:
                    return False
                if (event["from_state"], event["to_state"]) not in ALLOWED_TRANSITIONS:
                    return False
                if previous_to == "closed":
                    return False
                previous_to = event["to_state"]
        return True
    except (AttributeError, KeyError, TypeError, ValueError):
        return False


def _m1_t2(payload: Mapping[str, Any]) -> bool:
    try:
        entity_rows = {row["entity_id"]: row for row in payload["entities"]}
        if len(entity_rows) != len(payload["entities"]):
            return False
        paths: dict[str, list[Mapping[str, Any]]] = {entity_id: [] for entity_id in entity_rows}
        for event in payload["events"]:
            entity_id = event["entity_id"]
            if entity_id not in paths:
                return False
            paths[entity_id].append(event)
        for entity_id, entity in entity_rows.items():
            sequence = paths[entity_id]
            if not sequence:
                return False
            expected = 1
            for event in sequence:
                if event["revision"] != expected:
                    return False
                expected += 1
            if entity["revision"] != sequence[-1]["revision"]:
                return False
            if entity["current_state"] != sequence[-1]["to_state"]:
                return False
        return True
    except (AttributeError, KeyError, TypeError, ValueError):
        return False


M1_CHECKS: dict[str, Callable[[Mapping[str, Any]], bool]] = {
    "S1": _m1_s1,
    "S2": _m1_s2,
    "T1": _m1_t1,
    "T2": _m1_t2,
}


def _validate_family_subset(payload: Any, families: Sequence[str]) -> ValidationResult:
    sanitized = sanitize_payload(payload)
    if sanitized is None:
        return ValidationResult(False, len(families), tuple(families))
    failed: list[str] = []
    for family in families:
        try:
            passed = bool(M1_CHECKS[family](sanitized))
        except Exception:
            passed = False
        if not passed:
            failed.append(family)
    return ValidationResult(not failed, len(failed), tuple(failed))


def validate_b0(payload: Any) -> ValidationResult:
    sanitized = sanitize_payload(payload)
    return ValidationResult(sanitized is not None, int(sanitized is not None), ())


def validate_m1(payload: Any) -> ValidationResult:
    return _validate_family_subset(payload, FAMILIES)


def validate_method(payload: Any, method: str) -> ValidationResult:
    if method == "B0":
        return validate_b0(payload)
    if method == "M1":
        return validate_m1(payload)
    if method == "M1-no-semantic":
        return _validate_family_subset(payload, ("T1", "T2"))
    if method == "M1-no-state":
        return _validate_family_subset(payload, ("S1", "S2"))
    if method == "M1-no-calibration":
        return validate_m1(payload)
    raise ProtocolError(f"unknown method: {method}")


def evaluate_raw(cases: Sequence[Case], method: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for case in cases:
        # Only the exact payload enters the validator; evaluator metadata stays outside.
        result = validate_method(case.payload, method)
        rows.append(
            {
                "method": method,
                "split": case.split,
                "seed": case.seed,
                "base_case_id": case.base_case_id,
                "case_id": case.case_id,
                "target_family": case.target_family,
                "truth": case.truth,
                "decision": bool(result.decision),
                "raw_score": result.raw_score,
                "input_sha256": case.input_sha256,
            }
        )
    return rows


# ---------------------------------------------------------------------------
# Dataset sanity and calibration.


def sanity_check_dataset(cases_by_split: Mapping[str, Sequence[Case]]) -> dict[str, Any]:
    expected_counts = {"development": 256, "calibration": 256, "confirmatory": 512}
    seen_cases: set[str] = set()
    seen_bases: dict[str, str] = {}
    total = 0
    for split, expected_count in expected_counts.items():
        cases = list(cases_by_split.get(split, ()))
        if len(cases) != expected_count:
            raise ProtocolError(f"{split} count mismatch")
        family_counts = {family: 0 for family in FAMILIES}
        groups: dict[str, list[Case]] = defaultdict(list)
        for case in cases:
            if case.case_id in seen_cases:
                raise ProtocolError("duplicate case ID")
            if case.base_case_id in seen_bases and seen_bases[case.base_case_id] != split:
                raise ProtocolError("base ID leaked across splits")
            seen_cases.add(case.case_id)
            seen_bases[case.base_case_id] = split
            groups[case.base_case_id].append(case)
            family_counts[case.target_family] += 1
            recomputed = reference_oracle(case.payload)
            stored = OracleResult(case.family_passes, case.truth, case.oracle_reason)
            if recomputed != stored:
                raise ProtocolError(f"stored oracle differs for {case.case_id}")
            expected_failed = () if case.valid else (case.target_family,)
            actual_failed = tuple(name for name, passed in recomputed.family_passes if not passed)
            if recomputed.truth != int(case.valid) or actual_failed != expected_failed:
                raise ProtocolError(f"oracle isolation failure for {case.case_id}")
            if not payload_is_sanitized(case.payload):
                raise ProtocolError(f"unsanitized payload for {case.case_id}")
            total += 1
        if family_counts != {family: expected_count // 4 for family in FAMILIES}:
            raise ProtocolError(f"family quotas mismatch for {split}")
        for base_id, base_cases in groups.items():
            if len(base_cases) != CASES_PER_BASE:
                raise ProtocolError(f"cluster size mismatch for {base_id}")
            if {(case.target_family, case.valid) for case in base_cases} != {
                (family, valid) for family in FAMILIES for valid in (True, False)
            }:
                raise ProtocolError(f"cluster recipe quota mismatch for {base_id}")
    return {
        "protocol_version": PROTOCOL_VERSION,
        "split_counts": {split: len(cases_by_split[split]) for split in expected_counts},
        "total_cases": total,
        "confirmatory_clusters": len({case.base_case_id for case in cases_by_split["confirmatory"]}),
        "validity": "passed",
    }


def runtime_sanity_check(cases_by_split: Mapping[str, Sequence[Case]]) -> dict[str, Any]:
    """Run the pre-analysis gate used by the real in-memory pipeline.

    In addition to the independent oracle/schema checks, this gate verifies the
    schema-only baseline accepts every generated payload and compares every
    generated recipe against a separately maintained protocol reconstruction.
    """

    sanity = sanity_check_dataset(cases_by_split)
    b0_checked = 0
    footprints_checked = 0
    for split in SPLIT_SEEDS:
        for case in cases_by_split[split]:
            try:
                baseline = validate_b0(case.payload)
                baseline_decision = baseline.decision
                baseline_score = baseline.raw_score
                baseline_failed = baseline.failed_families
            except Exception as exc:
                raise ProtocolError(
                    f"runtime B0 sanity check raised for {case.case_id}"
                ) from exc
            if (
                type(baseline_decision) is not bool
                or not baseline_decision
                or baseline_score != 1
                or baseline_failed
            ):
                raise ProtocolError(f"runtime B0 sanity check failed for {case.case_id}")
            b0_checked += 1

            base = generate_base_payload(case.split, case.seed, case.base_index)
            expected_payload, expected_fault_id = _expected_recipe_payload(
                base, case.target_family, case.valid
            )
            if case.payload != expected_payload:
                raise ProtocolError(f"recipe footprint mismatch for {case.case_id}")
            if case.fault_id != expected_fault_id:
                raise ProtocolError(f"recipe fault metadata mismatch for {case.case_id}")
            footprints_checked += 1
    return {
        **sanity,
        "runtime_b0_cases": b0_checked,
        "recipe_footprints_checked": footprints_checked,
    }


def fit_calibration_lookup(method: str, calibration_rows: Sequence[Mapping[str, Any]]) -> CalibrationLookup:
    if method not in CALIBRATED_METHODS:
        raise ProtocolError(f"method has no calibration lookup: {method}")
    if not calibration_rows:
        raise ProtocolError("empty calibration rows")
    counts: dict[int, list[int]] = defaultdict(lambda: [0, 0])
    seen: set[str] = set()
    total = 0
    valid_total = 0
    for row in calibration_rows:
        if row.get("method") != method or row.get("split") != "calibration":
            raise ProtocolError("calibration lookup received non-calibration row")
        case_id = row.get("case_id")
        score = row.get("raw_score")
        truth = row.get("truth")
        if (
            type(case_id) is not str
            or case_id in seen
            or not _is_int(score)
            or type(truth) is not int
            or truth not in (0, 1)
        ):
            raise ProtocolError("malformed or duplicate calibration row")
        seen.add(case_id)
        counts[score][truth] += 1
        total += 1
        valid_total += int(truth)
    global_p = (valid_total + 1) / (total + 2)
    by_score = tuple(
        (score, (bucket[1] + 1) / (sum(bucket) + 2))
        for score, bucket in sorted(counts.items())
    )
    return CalibrationLookup(method, by_score, global_p)


def fit_all_calibrations(raw_rows: Sequence[Mapping[str, Any]]) -> tuple[CalibrationLookup, ...]:
    return tuple(
        fit_calibration_lookup(
            method,
            [row for row in raw_rows if row["method"] == method and row["split"] == "calibration"],
        )
        for method in CALIBRATED_METHODS
    )


def _lookup_map(lookups: Sequence[CalibrationLookup]) -> dict[str, CalibrationLookup]:
    return {lookup.method: lookup for lookup in lookups}


def build_prediction_rows(
    run_id: str,
    cases: Sequence[Case],
    raw_rows: Sequence[Mapping[str, Any]],
    lookups: Sequence[CalibrationLookup],
    manifest_hash: str,
) -> list[dict[str, Any]]:
    expected = {(method, case.case_id) for method in METHODS for case in cases}
    by_key: dict[tuple[str, str], Mapping[str, Any]] = {}
    for row in raw_rows:
        key = (row.get("method"), row.get("case_id"))
        if key in by_key or key not in expected:
            raise ProtocolError(f"duplicate/unexpected raw row {key}")
        by_key[key] = row
    if set(by_key) != expected:
        raise ProtocolError("raw rows are incomplete")
    lookup_by_method = _lookup_map(lookups)
    output: list[dict[str, Any]] = []
    for case in cases:
        for method in METHODS:
            raw = by_key[(method, case.case_id)]
            expected_fields = {
                "method": method,
                "split": case.split,
                "seed": case.seed,
                "base_case_id": case.base_case_id,
                "case_id": case.case_id,
                "target_family": case.target_family,
                "truth": case.truth,
                "input_sha256": case.input_sha256,
            }
            if any(raw.get(key) != value for key, value in expected_fields.items()):
                raise ProtocolError(f"raw metadata mismatch for {method}/{case.case_id}")
            if type(raw.get("decision")) is not bool or not _is_int(raw.get("raw_score")):
                raise ProtocolError("malformed raw decision/score")
            max_score = 1 if method == "B0" else len(METHOD_FAMILIES.get(method, FAMILIES))
            if not 0 <= raw["raw_score"] <= max_score:
                raise ProtocolError("raw score outside method range")
            if method == "M1-no-calibration":
                probability = float(raw["decision"])
            else:
                lookup = lookup_by_method.get(method)
                if lookup is None:
                    raise ProtocolError(f"missing lookup for {method}")
                probability = lookup.lookup(raw["raw_score"])
            if not math.isfinite(probability) or not 0 <= probability <= 1:
                raise ProtocolError("invalid p_valid")
            output.append(
                {
                    "run_id": run_id,
                    "protocol_path": PROTOCOL_PATH,
                    "protocol_commit": PROTOCOL_COMMIT,
                    "method": method,
                    "split": case.split,
                    "seed": case.seed,
                    "base_case_id": case.base_case_id,
                    "case_id": case.case_id,
                    "target_family": case.target_family,
                    "truth": case.truth,
                    "decision": raw["decision"],
                    "raw_score": raw["raw_score"],
                    "p_valid": probability,
                    "input_sha256": case.input_sha256,
                    "oracle_manifest_sha256": manifest_hash,
                    "status": "valid",
                }
            )
    return output


# ---------------------------------------------------------------------------
# Point metrics.


def _empty_aggregate() -> dict[str, Any]:
    return {
        "support": 0,
        "tp": 0,
        "tn": 0,
        "fp": 0,
        "fn": 0,
        "brier_sum": 0.0,
        "bin_counts": [0] * 10,
        "bin_p_sums": [0.0] * 10,
        "bin_y_sums": [0] * 10,
    }


def _add_metric_row(aggregate: dict[str, Any], row: Mapping[str, Any]) -> None:
    truth = row.get("truth")
    decision = row.get("decision")
    probability = row.get("p_valid")
    if type(truth) is not int or truth not in (0, 1) or type(decision) is not bool:
        raise ProtocolError("malformed metric classification")
    if type(probability) not in (int, float) or isinstance(probability, bool):
        raise ProtocolError("malformed metric probability")
    probability = float(probability)
    if not math.isfinite(probability) or not 0 <= probability <= 1:
        raise ProtocolError("non-finite metric probability")
    aggregate["support"] += 1
    if truth == 1 and decision:
        aggregate["tp"] += 1
    elif truth == 0 and not decision:
        aggregate["tn"] += 1
    elif truth == 0:
        aggregate["fp"] += 1
    else:
        aggregate["fn"] += 1
    aggregate["brier_sum"] += (probability - truth) ** 2
    index = min(int(probability * 10), 9)
    aggregate["bin_counts"][index] += 1
    aggregate["bin_p_sums"][index] += probability
    aggregate["bin_y_sums"][index] += truth


def _safe_rate(numerator: int, denominator: int) -> float | None:
    return None if denominator == 0 else numerator / denominator


def _metrics_from_aggregate(aggregate: Mapping[str, Any]) -> dict[str, Any]:
    support = aggregate["support"]
    tp, tn, fp, fn = (aggregate[field] for field in ("tp", "tn", "fp", "fn"))
    denominators = {
        "support": support,
        "fpr": fp + tn,
        "fnr": fn + tp,
        "precision": tp + fp,
        "recall": tp + fn,
        "specificity": tn + fp,
        "f1": 2 * tp + fp + fn,
        "balanced_accuracy_recall": tp + fn,
        "balanced_accuracy_specificity": tn + fp,
        "brier": support,
        "ece": support,
    }
    recall = _safe_rate(tp, denominators["recall"])
    specificity = _safe_rate(tn, denominators["specificity"])
    balanced = None if recall is None or specificity is None else (recall + specificity) / 2
    bins: list[dict[str, Any]] = []
    ece = None if support == 0 else 0.0
    for index in range(10):
        count = aggregate["bin_counts"][index]
        if count:
            mean_conf = aggregate["bin_p_sums"][index] / count
            valid_frequency = aggregate["bin_y_sums"][index] / count
            if ece is not None:
                ece += count / support * abs(mean_conf - valid_frequency)
        else:
            mean_conf = None
            valid_frequency = None
        bins.append(
            {
                "bin": index,
                "lower": index / 10,
                "upper": 1.0 if index == 9 else (index + 1) / 10,
                "count": count,
                "mean_confidence": mean_conf,
                "valid_frequency": valid_frequency,
            }
        )
    return {
        "support": support,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "fpr": _safe_rate(fp, denominators["fpr"]),
        "fnr": _safe_rate(fn, denominators["fnr"]),
        "precision": _safe_rate(tp, denominators["precision"]),
        "recall": recall,
        "specificity": specificity,
        "f1": _safe_rate(2 * tp, denominators["f1"]),
        "balanced_accuracy": balanced,
        "brier": None if support == 0 else aggregate["brier_sum"] / support,
        "ece": ece,
        "denominators": denominators,
        "ece_bins": bins,
    }


def compute_metrics(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    aggregate = _empty_aggregate()
    for row in rows:
        _add_metric_row(aggregate, row)
    return _metrics_from_aggregate(aggregate)


def _point_metric_rows(
    prediction_rows: Sequence[Mapping[str, Any]], split: str
) -> dict[tuple[str, str], dict[str, Any]]:
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for method in METHODS:
        method_rows = [
            row for row in prediction_rows if row["method"] == method and row["split"] == split
        ]
        for subgroup in SUBGROUPS:
            rows = (
                method_rows
                if subgroup == "overall"
                else [row for row in method_rows if row["target_family"] == subgroup]
            )
            result[(method, subgroup)] = compute_metrics(rows)
    return result


def build_metric_rows(
    prediction_rows: Sequence[Mapping[str, Any]],
    splits: Sequence[str] = ("confirmatory",),
    bootstrap: BootstrapResult | None = None,
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for split in splits:
        point = _point_metric_rows(prediction_rows, split)
        for method in METHODS:
            for subgroup in SUBGROUPS:
                summary = point[(method, subgroup)]
                ci = (
                    bootstrap.interval(method, subgroup, "balanced_accuracy")
                    if bootstrap is not None
                    and split == "confirmatory"
                    and method in bootstrap.available_methods
                    else None
                )
                paired = (
                    bootstrap.interval(None, subgroup, "balanced_accuracy")
                    if bootstrap is not None and split == "confirmatory" and method == "M1"
                    else None
                )
                method_intervals = {}
                paired_intervals = {}
                if (
                    bootstrap is not None
                    and split == "confirmatory"
                    and method in bootstrap.available_methods
                ):
                    method_intervals = {
                        metric: bootstrap.interval(method, subgroup, metric)
                        for metric in METRIC_NAMES
                    }
                if bootstrap is not None and split == "confirmatory" and method == "M1":
                    paired_intervals = {
                        metric: bootstrap.interval(None, subgroup, metric)
                        for metric in METRIC_NAMES
                    }
                paired_point = None
                paired_deltas = {}
                if split == "confirmatory" and method == "M1":
                    m1 = point[("M1", subgroup)]
                    b0 = point[("B0", subgroup)]
                    paired_deltas = {
                        metric: (
                            None
                            if m1[metric] is None or b0[metric] is None
                            else m1[metric] - b0[metric]
                        )
                        for metric in METRIC_NAMES
                    }
                    paired_point = (
                        None
                        if m1["balanced_accuracy"] is None
                        or b0["balanced_accuracy"] is None
                        else m1["balanced_accuracy"] - b0["balanced_accuracy"]
                    )
                output.append(
                    {
                        "method": method,
                        "split": split,
                        "subgroup": subgroup,
                        "support": summary["support"],
                        "TP": summary["tp"],
                        "TN": summary["tn"],
                        "FP": summary["fp"],
                        "FN": summary["fn"],
                        "FPR": summary["fpr"],
                        "FNR": summary["fnr"],
                        "precision": summary["precision"],
                        "recall": summary["recall"],
                        "specificity": summary["specificity"],
                        "F1": summary["f1"],
                        "balanced_accuracy": summary["balanced_accuracy"],
                        "Brier": summary["brier"],
                        "ECE": summary["ece"],
                        "denominators": summary["denominators"],
                        "ece_bins": summary["ece_bins"],
                        "intervals": method_intervals,
                        "interval_reference": (
                            f"bootstrap:method={method}:split={split}:subgroup={subgroup}:metrics=all"
                            if method_intervals
                            else None
                        ),
                        "ci_lower": ci["lower"] if ci else None,
                        "ci_upper": ci["upper"] if ci else None,
                        "ci_usable_replicates": ci["usable_replicates"] if ci else None,
                        "ci_status": ci["status"] if ci else None,
                        "paired_delta": paired_point,
                        "paired_deltas": paired_deltas,
                        "paired_ci_lower": paired["lower"] if paired else None,
                        "paired_ci_upper": paired["upper"] if paired else None,
                        "paired_ci_usable_replicates": paired["usable_replicates"] if paired else None,
                        "paired_ci_status": paired["status"] if paired else None,
                        "paired_intervals": paired_intervals,
                        "paired_interval_reference": (
                            f"bootstrap:pair=M1-minus-B0:split={split}:subgroup={subgroup}:metrics=all"
                            if paired_intervals
                            else None
                        ),
                    }
                )
    return output


# ---------------------------------------------------------------------------
# Exact cluster bootstrap and auditable paired artifact.


def bootstrap_cluster_indices(
    replicate: int, cluster_count: int = BOOTSTRAP_CLUSTER_COUNT
) -> tuple[int, ...]:
    if not 0 <= replicate < BOOTSTRAP_REPLICATES or cluster_count < 1:
        raise ProtocolError("invalid bootstrap index/count")
    selected = []
    for draw_index in range(cluster_count):
        material = f"{PROTOCOL_VERSION}|bootstrap|{replicate}|{draw_index}"
        digest = hashlib.sha256(material.encode("utf-8")).digest()
        selected.append(int.from_bytes(digest[:8], "big", signed=False) % cluster_count)
    return tuple(selected)


def _aggregate_add(target: dict[str, Any], source: Mapping[str, Any]) -> None:
    target["support"] += source["support"]
    for field in ("tp", "tn", "fp", "fn"):
        target[field] += source[field]
    target["brier_sum"] += source["brier_sum"]
    for index in range(10):
        target["bin_counts"][index] += source["bin_counts"][index]
        target["bin_p_sums"][index] += source["bin_p_sums"][index]
        target["bin_y_sums"][index] += source["bin_y_sums"][index]


def _aggregate_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    aggregate = _empty_aggregate()
    for row in rows:
        _add_metric_row(aggregate, row)
    return aggregate


def _percentile(values: Sequence[float], probability: float) -> float:
    if not values:
        raise ProtocolError("percentile has no usable values")
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] + fraction * (ordered[upper] - ordered[lower])


def _interval(
    method: str | None,
    subgroup: str,
    metric: str,
    values: Sequence[float | None],
    replicate_count: int,
) -> dict[str, Any]:
    usable = [value for value in values if value is not None]
    available = len(usable) == replicate_count and bool(usable)
    return {
        "method": method,
        "method_pair": "M1-minus-B0" if method is None else None,
        "subgroup": subgroup,
        "metric": metric,
        "lower": _percentile(usable, 0.025) if available else None,
        "upper": _percentile(usable, 0.975) if available else None,
        "usable_replicates": len(usable),
        "status": "available" if available else "undefined",
    }


def bootstrap_confirmatory(
    prediction_rows: Sequence[Mapping[str, Any]],
    n_replicates: int = BOOTSTRAP_REPLICATES,
    split: str = "confirmatory",
) -> BootstrapResult:
    if n_replicates != BOOTSTRAP_REPLICATES:
        raise ProtocolError("E001 requires exactly 10,000 bootstrap replicates")
    rows = [row for row in prediction_rows if row.get("split") == split]
    if not rows:
        raise ProtocolError("bootstrap input is empty")
    cluster_ids = tuple(sorted({str(row["base_case_id"]) for row in rows}))
    if len(cluster_ids) != BOOTSTRAP_CLUSTER_COUNT:
        raise ProtocolError("bootstrap requires 64 sorted clusters")
    cluster_index = {cluster_id: index for index, cluster_id in enumerate(cluster_ids)}
    available_methods = tuple(
        method for method in METHODS if any(row.get("method") == method for row in rows)
    )
    if not set(PRIMARY_METHODS).issubset(available_methods):
        raise ProtocolError("bootstrap requires both B0 and M1")
    grouped: dict[tuple[int, str, str], list[Mapping[str, Any]]] = defaultdict(list)
    seen: set[tuple[str, str]] = set()
    for row in rows:
        method = row.get("method")
        case_id = row.get("case_id")
        family = row.get("target_family")
        if method not in available_methods or type(case_id) is not str or family not in FAMILIES:
            raise ProtocolError("malformed bootstrap row")
        key = (method, case_id)
        if key in seen:
            raise ProtocolError("duplicate bootstrap prediction")
        seen.add(key)
        grouped[(cluster_index[str(row["base_case_id"])], method, family)].append(row)
    expected_pairs = {(family, truth) for family in FAMILIES for truth in (0, 1)}
    for index, cluster_id in enumerate(cluster_ids):
        for method in available_methods:
            cluster_rows = [
                row
                for (stored_index, stored_method, _), grouped_rows in grouped.items()
                if stored_index == index and stored_method == method
                for row in grouped_rows
            ]
            if len(cluster_rows) != CASES_PER_BASE or {
                (row["target_family"], row["truth"]) for row in cluster_rows
            } != expected_pairs:
                raise ProtocolError(f"incomplete bootstrap cluster {cluster_id}/{method}")

    contributions: dict[tuple[int, str, str], dict[str, Any]] = {}
    for index in range(len(cluster_ids)):
        for method in available_methods:
            for subgroup in SUBGROUPS:
                if subgroup == "overall":
                    selected = [
                        row
                        for (stored_index, stored_method, _), grouped_rows in grouped.items()
                        if stored_index == index and stored_method == method
                        for row in grouped_rows
                    ]
                else:
                    selected = grouped.get((index, method, subgroup), [])
                contributions[(index, method, subgroup)] = _aggregate_rows(selected)

    method_series: dict[tuple[str, str, str], list[float | None]] = {
        (method, subgroup, metric): []
        for method in available_methods
        for subgroup in SUBGROUPS
        for metric in METRIC_NAMES
    }
    delta_series: dict[tuple[str, str], list[float | None]] = {
        (subgroup, metric): [] for subgroup in SUBGROUPS for metric in METRIC_NAMES
    }
    for replicate in range(n_replicates):
        selected_indices = bootstrap_cluster_indices(replicate, len(cluster_ids))
        replicate_metrics: dict[tuple[str, str], dict[str, Any]] = {}
        for method in available_methods:
            for subgroup in SUBGROUPS:
                aggregate = _empty_aggregate()
                for index in selected_indices:
                    _aggregate_add(aggregate, contributions[(index, method, subgroup)])
                summary = _metrics_from_aggregate(aggregate)
                replicate_metrics[(method, subgroup)] = summary
                for metric in METRIC_NAMES:
                    method_series[(method, subgroup, metric)].append(summary[metric])
        for subgroup in SUBGROUPS:
            for metric in METRIC_NAMES:
                left = replicate_metrics[("M1", subgroup)][metric]
                right = replicate_metrics[("B0", subgroup)][metric]
                delta_series[(subgroup, metric)].append(
                    None if left is None or right is None else left - right
                )
    intervals = [
        _interval(method, subgroup, metric, method_series[(method, subgroup, metric)], n_replicates)
        for method in available_methods
        for subgroup in SUBGROUPS
        for metric in METRIC_NAMES
    ]
    intervals.extend(
        _interval(None, subgroup, metric, delta_series[(subgroup, metric)], n_replicates)
        for subgroup in SUBGROUPS
        for metric in METRIC_NAMES
    )
    return BootstrapResult(
        replicate_count=n_replicates,
        cluster_ids=cluster_ids,
        available_methods=available_methods,
        method_values=tuple(
            (method, subgroup, metric, tuple(values))
            for (method, subgroup, metric), values in sorted(method_series.items())
        ),
        delta_values=tuple(
            (subgroup, metric, tuple(values))
            for (subgroup, metric), values in sorted(delta_series.items())
        ),
        intervals=tuple(intervals),
    )


def iter_bootstrap_rows(
    result: BootstrapResult, row_type: str | None = None
) -> Iterable[dict[str, Any]]:
    if row_type in (None, "replicate"):
        for subgroup, metric, values in result.delta_values:
            for replicate, value in enumerate(values):
                yield {
                    "row_type": "replicate",
                    "replicate": replicate,
                    "method": None,
                    "method_pair": "M1-minus-B0",
                    "subgroup": subgroup,
                    "metric": metric,
                    "value": None,
                    "delta_m1_minus_b0": value,
                    "ci_lower": None,
                    "ci_upper": None,
                    "usable_replicates": result.replicate_count,
                    "status": "usable" if value is not None else "undefined",
                }
    if row_type in (None, "interval"):
        for interval in result.intervals:
            yield {
                "row_type": "interval",
                "replicate": None,
                "method": interval["method"],
                "method_pair": interval["method_pair"],
                "subgroup": interval["subgroup"],
                "metric": interval["metric"],
                "value": None,
                "delta_m1_minus_b0": None,
                "ci_lower": interval["lower"],
                "ci_upper": interval["upper"],
                "usable_replicates": interval["usable_replicates"],
                "status": interval["status"],
            }


def build_bootstrap_rows(result: BootstrapResult) -> list[dict[str, Any]]:
    return list(iter_bootstrap_rows(result))


def expected_bootstrap_row_count(result: BootstrapResult) -> int:
    return result.replicate_count * len(SUBGROUPS) * len(METRIC_NAMES) + len(result.intervals)


def bootstrap_size_estimate(result: BootstrapResult) -> int:
    """Measure the intended CSV bytes before a future writer touches disk."""

    return len(serialize_csv(iter_bootstrap_rows(result), BOOTSTRAP_FIELDS))


# ---------------------------------------------------------------------------
# Complete in-memory pipeline and reporting.


def _format(value: Any) -> str:
    if value is None:
        return NA
    if isinstance(value, float):
        return f"{value:.10g}"
    return str(value)


def _metric_row_index(rows: Sequence[Mapping[str, Any]]) -> dict[tuple[str, str, str], Mapping[str, Any]]:
    return {(row["method"], row["split"], row["subgroup"]): row for row in rows}


def build_results_markdown(
    run_id: str,
    sanity: Mapping[str, Any],
    metric_rows: Sequence[Mapping[str, Any]],
    bootstrap: BootstrapResult,
) -> str:
    index = _metric_row_index(metric_rows)
    overall = [index[(method, "confirmatory", "overall")] for method in METHODS]
    primary_metrics = ("balanced_accuracy", "fpr", "fnr", "brier", "ece")
    lines = [
        f"# E001 run {run_id}",
        "",
        f"- Protocol: `{PROTOCOL_PATH}`",
        f"- Protocol version: `{PROTOCOL_VERSION}`",
        f"- Protocol commit: `{PROTOCOL_COMMIT}`",
        f"- Run ID: `{run_id}`",
        "- Run validity: `valid` (all deterministic, schema, oracle, calibration, and bootstrap gates passed).",
        "- Environment: one standard-library Python process on local CPU; no network/API/GPU/dependencies.",
        "- Deviations: none.",
        "",
        "## Sanity status",
        "",
        f"- Split counts: `{canonical_json_text(sanity['split_counts'])}`",
        f"- Confirmatory clusters: `{sanity['confirmatory_clusters']}`",
        f"- Bootstrap replicates: `{bootstrap.replicate_count}`",
        "",
        "## Confirmatory point metrics and method intervals",
        "",
        "| Method | BA | BA CI | FPR | FPR CI | FNR | FNR CI | Brier | ECE |",
        "| --- | ---: | --- | ---: | --- | ---: | --- | ---: | ---: |",
    ]
    for row in overall:
        fpr_ci = bootstrap.interval(row["method"], "overall", "fpr")
        fnr_ci = bootstrap.interval(row["method"], "overall", "fnr")
        lines.append(
            f"| {row['method']} | {_format(row['balanced_accuracy'])} | "
            f"[{_format(row['ci_lower'])}, {_format(row['ci_upper'])}] | "
            f"{_format(row['FPR'])} | [{_format(fpr_ci['lower'])}, {_format(fpr_ci['upper'])}] | "
            f"{_format(row['FNR'])} | [{_format(fnr_ci['lower'])}, {_format(fnr_ci['upper'])}] | "
            f"{_format(row['Brier'])} | {_format(row['ECE'])} |"
        )
    m1 = index[("M1", "confirmatory", "overall")]
    b0 = index[("B0", "confirmatory", "overall")]
    lines.extend(
        (
            "",
            "## Primary paired deltas (M1 minus B0)",
            "",
            "| Metric | Point delta | 95% CI | Interval reference |",
            "| --- | ---: | --- | --- |",
        )
    )
    for metric in primary_metrics:
        if metric == "balanced_accuracy":
            point = m1["paired_delta"]
        else:
            key = {"brier": "Brier", "ece": "ECE"}.get(metric, metric.upper())
            point = None if m1[key] is None or b0[key] is None else m1[key] - b0[key]
        interval = bootstrap.interval(None, "overall", metric)
        lines.append(
            f"| {metric} | {_format(point)} | [{_format(interval['lower'])}, {_format(interval['upper'])}] | "
            f"bootstrap:pair=M1-minus-B0:overall:{metric} |"
        )
    ba_interval = bootstrap.interval(None, "overall", "balanced_accuracy")
    fpr_interval = bootstrap.interval(None, "overall", "fpr")
    fnr_point = None if m1["FNR"] is None or b0["FNR"] is None else m1["FNR"] - b0["FNR"]
    supported = (
        ba_interval["status"] == "available"
        and fpr_interval["status"] == "available"
        and ba_interval["lower"] is not None
        and ba_interval["lower"] > 0
        and fpr_interval["upper"] is not None
        and fpr_interval["upper"] < 0
        and fnr_point is not None
        and fnr_point <= 0
    )
    lines.extend(
        (
            "",
            "## H1 decision rule",
            "",
            "H1 is supported within this synthetic design only when the paired "
            "95% CI for ΔBA is entirely > 0, the paired 95% CI for ΔFPR (M1 − B0) "
            "is entirely < 0, and the point estimate ΔFNR (M1 − B0) is <= 0. "
            "The FNR condition is a co-primary guardrail; it is not hidden.",
            "",
            f"- ΔFNR point estimate: `{_format(fnr_point)}`",
            f"- H1 status: `{'supported' if supported else 'mixed/not supported'}`",
            "",
            "## Ablation secondary summaries",
            "",
            "| Method | BA | BA CI | FPR | FNR | Brier | ECE |",
            "| --- | ---: | --- | ---: | ---: | ---: | ---: |",
        )
    )
    for method in ABLATION_METHODS:
        row = index[(method, "confirmatory", "overall")]
        ci = bootstrap.interval(method, "overall", "balanced_accuracy")
        lines.append(
            f"| {method} | {_format(row['balanced_accuracy'])} | "
            f"[{_format(ci['lower'])}, {_format(ci['upper'])}] | {_format(row['FPR'])} | "
            f"{_format(row['FNR'])} | {_format(row['Brier'])} | {_format(row['ECE'])} |"
        )
    lines.extend(
        (
            "",
            "## Data links",
            "",
            "- [Predictions](../../../data/E001-v1-predictions.jsonl)",
            "- [Metrics](../../../data/E001-v1-metrics.csv)",
            "- [Bootstrap deltas and intervals](../../../data/E001-v1-bootstrap.csv)",
            "",
            "## Limitations",
            "",
            "E001 is finite, hand-designed, balanced, synthetic, and single-fault. "
            "Its oracle is coupled to the recipes and does not establish production "
            "performance, external validity, safety, novelty, or public-claim eligibility.",
            "",
        )
    )
    return "\n".join(lines)


def build_pipeline(run_id: str) -> PipelineArtifacts:
    """Build every future output in memory; no filesystem or console writes."""

    cases_by_split = generate_all_splits()
    sanity = runtime_sanity_check(cases_by_split)
    first_bytes = dataset_canonical_bytes(cases_by_split)
    second_bytes = dataset_canonical_bytes(generate_all_splits())
    if first_bytes != second_bytes:
        raise ProtocolError("dataset determinism gate failed")
    all_cases = [case for split in SPLIT_SEEDS for case in cases_by_split[split]]
    raw_rows = tuple(row for method in METHODS for row in evaluate_raw(all_cases, method))
    lookups = fit_all_calibrations(raw_rows)
    manifest_hash = oracle_manifest_sha256(all_cases)
    prediction_rows = tuple(
        build_prediction_rows(run_id, all_cases, raw_rows, lookups, manifest_hash)
    )
    bootstrap = bootstrap_confirmatory([row for row in prediction_rows if row["split"] == "confirmatory"])
    metric_rows = tuple(
        build_metric_rows(
            prediction_rows,
            splits=("development", "calibration", "confirmatory"),
            bootstrap=bootstrap,
        )
    )
    result_markdown = build_results_markdown(run_id, sanity, metric_rows, bootstrap)
    serialized = (
        ("predictions", serialize_jsonl(prediction_rows)),
        ("metrics", serialize_csv(metric_rows, METRIC_FIELDS)),
        ("bootstrap", serialize_csv(iter_bootstrap_rows(bootstrap), BOOTSTRAP_FIELDS)),
        ("result", result_markdown.encode("utf-8")),
    )
    return PipelineArtifacts(
        run_id=run_id,
        sanity=sanity,
        raw_rows=raw_rows,
        calibration_lookups=lookups,
        prediction_rows=prediction_rows,
        metric_rows=metric_rows,
        bootstrap=bootstrap,
        result_markdown=result_markdown,
        serialized_outputs=serialized,
    )


def deterministic_pipeline(run_id: str) -> PipelineArtifacts:
    first = build_pipeline(run_id)
    second = build_pipeline(run_id)
    if first.hashes() != second.hashes():
        raise ProtocolError("full in-memory determinism gate failed")
    for name, content in first.serialized_outputs:
        if content != second.serialized(name):
            raise ProtocolError(f"serialized determinism gate failed for {name}")
    return first


def oracle_family_passes(payload: Mapping[str, Any]) -> dict[str, bool]:
    """Compatibility helper exposing only the independent reference oracle."""

    return dict(reference_oracle(payload).family_passes)


__all__ = [
    "ABLATION_METHODS",
    "ALLOWED_STATES",
    "ALLOWED_TRANSITIONS",
    "BASE_BUNDLES_PER_SEED",
    "BOOTSTRAP_CLUSTER_COUNT",
    "BOOTSTRAP_FIELDS",
    "BOOTSTRAP_REPLICATES",
    "BOOTSTRAP_CONFIDENCE",
    "CASES_PER_BASE",
    "BootstrapResult",
    "CALIBRATED_METHODS",
    "Case",
    "CalibrationLookup",
    "FAMILIES",
    "METRIC_FIELDS",
    "METRIC_NAMES",
    "M1_CHECKS",
    "METHODS",
    "NA",
    "ORACLE_ONLY_FIELDS",
    "PREDICTION_FIELDS",
    "PRIMARY_METHODS",
    "PROTOCOL_COMMIT",
    "PROTOCOL_PATH",
    "PROTOCOL_VERSION",
    "PUBLIC_LARGE_FILE_LIMIT",
    "PipelineArtifacts",
    "OracleResult",
    "REFERENCE_CHECKS",
    "SPLIT_SEEDS",
    "SUBGROUPS",
    "ValidationResult",
    "bootstrap_cluster_indices",
    "bootstrap_confirmatory",
    "bootstrap_size_estimate",
    "build_bootstrap_rows",
    "build_metric_rows",
    "build_pipeline",
    "build_prediction_rows",
    "build_results_markdown",
    "canonical_json_bytes",
    "canonical_json_text",
    "compute_metrics",
    "csv_value",
    "dataset_canonical_bytes",
    "dataset_sha256",
    "deterministic_amount",
    "deterministic_pipeline",
    "evaluate_raw",
    "expected_bootstrap_row_count",
    "fit_all_calibrations",
    "fit_calibration_lookup",
    "generate_all_splits",
    "generate_base_payload",
    "generate_split",
    "iter_bootstrap_rows",
    "oracle_family_passes",
    "oracle_manifest",
    "oracle_manifest_sha256",
    "payload_sha256",
    "payload_is_sanitized",
    "reference_oracle",
    "reference_s1",
    "reference_s2",
    "reference_t1",
    "reference_t2",
    "runtime_sanity_check",
    "sanitize_payload",
    "sanity_check_dataset",
    "serialize_csv",
    "serialize_jsonl",
    "sha256_hex",
    "validate_b0",
    "validate_m1",
    "validate_method",
]
