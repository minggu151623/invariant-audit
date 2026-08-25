"""Standard-library E002-v1 implementation.

The module is deliberately side-effect free on import.  It contains the
deterministic population generator, a separately maintained reference oracle,
the evaluated checker family, calibration, metrics, bootstrap, serialization,
and the in-memory gates used by the runner.
"""

from __future__ import annotations

import copy
import ast
import csv
import datetime as _datetime
import hashlib
import io
import inspect
import json
import math
import os
import re
import subprocess
import textwrap
import types
from collections import Counter, defaultdict
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
from types import MappingProxyType


PROTOCOL_VERSION = "E002-v1"
PROTOCOL_COMMIT = "9e39c5defc89f2c2a896b53dda529f326e9dfcf8"
PROTOCOL_BLOB = "f7d27a069ee3fd1600f89d9271e107c197033238"
PROTOCOL_PATH = "experiments/E002-heterogeneous-specification-stress/protocol.md"

METHODS = (
    "B0",
    "M1",
    "M1-omit-conservation",
    "M1-overconstraint",
    "M1-stale-transition",
    "M1-no-semantic",
    "M1-no-state",
    "M1-no-calibration",
)
PRIMARY_METHODS = ("B0", "M1")
MISSPECIFIED_METHODS = (
    "M1-omit-conservation",
    "M1-overconstraint",
    "M1-stale-transition",
)
ABLATION_METHODS = ("M1-no-semantic", "M1-no-state", "M1-no-calibration")
SPLITS = ("development", "calibration", "confirmatory")
SPLIT_RANK = {name: index for index, name in enumerate(SPLITS)}
REPLICATES = 10_000
PUBLIC_LIMIT = 52_428_800
# Independent serializer-planning arithmetic from protocol §11.  This is a
# byte-budget gate only; it does not materialize confirmatory rows.
INDEPENDENT_BOOTSTRAP_BLOCKS = 53
INDEPENDENT_BOOTSTRAP_REPLICATE_LINES = INDEPENDENT_BOOTSTRAP_BLOCKS * REPLICATES
INDEPENDENT_BOOTSTRAP_REPLICATE_BYTES = 90
INDEPENDENT_BOOTSTRAP_INTERVAL_BYTES = 180
INDEPENDENT_BOOTSTRAP_FIXED_BYTES = 1_024
INDEPENDENT_BOOTSTRAP_ESTIMATE = (
    INDEPENDENT_BOOTSTRAP_REPLICATE_LINES * INDEPENDENT_BOOTSTRAP_REPLICATE_BYTES
    + INDEPENDENT_BOOTSTRAP_BLOCKS * INDEPENDENT_BOOTSTRAP_INTERVAL_BYTES
    + INDEPENDENT_BOOTSTRAP_FIXED_BYTES
)
BOOTSTRAP_ESTIMATE = INDEPENDENT_BOOTSTRAP_ESTIMATE
NA = "NA"

FAMILIES = ("schema", "identity", "conservation", "transition", "revision")
NON_SCHEMA_FAMILIES = FAMILIES[1:]
# This literal belongs only to the reference-oracle implementation.  The
# evaluated checker uses its own retained-name literals below.
ORACLE_FAMILY_ORDER = ("schema", "identity", "conservation", "transition", "revision")
ORACLE_ALLOWED_EDGES = frozenset(
    {
        ("pending", "active"),
        ("pending", "closed"),
        ("active", "active"),
        ("active", "closed"),
    }
)
SUBGROUPS = (
    "overall",
    "cluster:H0",
    "cluster:H1",
    "cluster:H2",
    "cluster:H3",
    "cluster:H4",
    "cluster:H5",
    "case_kind:valid",
    "case_kind:single",
    "case_kind:multi",
)
METRICS = ("balanced_accuracy", "fpr", "fnr", "brier", "ece")
REPORT_METRICS = (
    "balanced_accuracy",
    "fpr",
    "fnr",
    "precision",
    "recall",
    "specificity",
    "f1",
    "brier",
    "ece",
)
DIAGNOSTICS = ("d1", "d2", "d3")
DIAGNOSTIC_METRIC = {"d1": "fpr", "d2": "fnr", "d3": "fnr"}
DIAGNOSTIC_PAIR = {
    "d1": ("M1-omit-conservation", "M1"),
    "d2": ("M1-overconstraint", "M1"),
    "d3": ("M1-stale-transition", "M1"),
}
DIAGNOSTIC_PAIR_CODE = {"d1": "omit-m1", "d2": "over-m1", "d3": "stale-m1"}
SUBGROUP_CODE = {
    "overall": "o",
    "cluster:H0": "h0",
    "cluster:H1": "h1",
    "cluster:H2": "h2",
    "cluster:H3": "h3",
    "cluster:H4": "h4",
    "cluster:H5": "h5",
    "case_kind:valid": "v",
    "case_kind:single": "s",
    "case_kind:multi": "m",
}
METRIC_CODE = {
    "balanced_accuracy": "ba",
    "fpr": "fpr",
    "fnr": "fnr",
    "brier": "brier",
    "ece": "ece",
}
METHOD_RANK = {name: index for index, name in enumerate(METHODS)}
SUBGROUP_RANK = {name: index for index, name in enumerate(SUBGROUPS)}
METRIC_RANK = {name: index for index, name in enumerate(METRICS)}
DIAGNOSTIC_RANK = {name: index for index, name in enumerate(DIAGNOSTICS)}

STATES = ("pending", "active", "closed")
STATE_SET = frozenset(STATES)


class ProtocolError(ValueError):
    """A locked protocol invariant failed."""


class JsonNumber(str):
    """A fixed-format JSON number token used by the canonical serializer."""


def _json_scalar(value: Any) -> str:
    if isinstance(value, JsonNumber):
        if not re.fullmatch(r"-?(?:0|[1-9][0-9]*)\.[0-9]{9}", str(value)):
            raise ProtocolError("invalid fixed JSON number")
        return str(value)
    if value is None:
        raise ProtocolError("JSON null is not permitted in locked output")
    if type(value) is bool:
        return "true" if value else "false"
    if type(value) is int:
        if value < 0:
            return "-" + str(-value)
        return str(value)
    if type(value) is str:
        return json.dumps(value, ensure_ascii=True, separators=(",", ":"))
    raise ProtocolError(f"unsupported canonical JSON scalar: {type(value)!r}")


def _canonical_json(value: Any) -> str:
    if isinstance(value, dict):
        if any(type(key) is not str for key in value):
            raise ProtocolError("canonical JSON object keys must be strings")
        pairs = []
        for key in sorted(value, key=lambda item: item.encode("utf-8")):
            pairs.append(
                _json_scalar(key) + ":" + _canonical_json(value[key])
            )
        return "{" + ",".join(pairs) + "}"
    if type(value) is list or type(value) is tuple:
        return "[" + ",".join(_canonical_json(item) for item in value) + "]"
    return _json_scalar(value)


def canonical_json_text(value: Any) -> str:
    return _canonical_json(value)


def canonical_json_bytes(value: Any) -> bytes:
    return canonical_json_text(value).encode("utf-8")


def sha256_hex(data: bytes | str) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def canonical_sha256(value: Any) -> str:
    return sha256_hex(canonical_json_bytes(value))


def _as_fraction(value: Fraction | Decimal | int | float) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, Decimal):
        return Fraction(value)
    if isinstance(value, float):
        return Fraction(str(value))
    return Fraction(value)


def d9(value: Fraction | Decimal | int | float | None) -> str:
    if value is None:
        return NA
    fraction = _as_fraction(value)
    with localcontext() as context:
        context.prec = 100
        decimal_value = (
            Decimal(fraction.numerator) / Decimal(fraction.denominator)
        ).quantize(Decimal("0.000000001"), rounding=ROUND_HALF_EVEN)
    if decimal_value == 0:
        return "0.000000000"
    text = format(decimal_value, "f")
    if "." not in text:
        text += ".000000000"
    whole, fractional = text.split(".", 1)
    return whole + "." + fractional.ljust(9, "0")[:9]


def json_number(value: Fraction | Decimal | int | float) -> JsonNumber:
    return JsonNumber(d9(value))


def _utf8_sorted(values: Iterable[str]) -> list[str]:
    return sorted(values, key=lambda item: item.encode("utf-8"))


def _strict_int(value: Any) -> bool:
    return type(value) is int


def _valid_date(text: str) -> bool:
    try:
        _datetime.date(int(text[:4]), int(text[4:6]), int(text[6:8]))
    except (ValueError, TypeError):
        return False
    return True


def validate_run_id(run_id: str) -> bool:
    return (
        type(run_id) is str
        and re.fullmatch(r"e002-[0-9]{8}-[0-9]{3}", run_id) is not None
        and _valid_date(run_id[5:13])
    )


TRACE_TABLE = {
    "H0": (
        ("pending", "active", "active", "closed"),
        ("pending", "active", "closed"),
        ("pending", "active", "active", "closed"),
    ),
    "H1": (
        ("pending", "active", "active", "closed"),
        ("pending", "active", "closed"),
        ("pending", "closed"),
        ("pending", "active", "closed"),
    ),
    "H2": (
        ("pending", "active", "active", "closed"),
        ("pending", "active", "closed"),
        ("pending", "closed"),
        ("pending", "active", "closed"),
        ("pending", "closed"),
    ),
    "H3": (
        ("pending", "active", "closed"),
        ("pending", "active", "active", "closed"),
        ("pending", "closed"),
        ("pending", "active", "active", "closed"),
    ),
    "H4": (
        ("pending", "active", "active", "closed"),
        ("pending", "active", "closed"),
        ("pending", "closed"),
        ("pending", "active", "closed"),
        ("pending", "active", "closed"),
        ("pending", "active", "closed"),
    ),
    "H5": (
        ("pending", "active", "closed"),
        ("pending", "active", "closed"),
        ("pending", "active", "closed"),
        ("pending", "active", "closed"),
        ("pending", "active", "closed"),
        ("pending", "closed"),
        ("pending", "closed"),
    ),
}

TYPE_MANIFEST = {
    "H0": {
        "tuple": (3, 3, 8, 2, 0, 0, 2, 7),
        "multi": 2,
        "signature": "2e80ccf18dad2a97d8d3e975b0f726f6cf15687fa6e4f50ddf55a940e6d29e9b",
    },
    "H1": {
        "tuple": (4, 4, 8, 1, 1, 0, 3, 8),
        "multi": 3,
        "signature": "0195af9dd2a1ef0f4348c6fc6f082b626d7c9ab1c310c9487d5760bf74afa574",
    },
    "H2": {
        "tuple": (5, 5, 9, 1, 2, 0, 4, 9),
        "multi": 4,
        "signature": "0863b001f0a85dc2582be68a41d33afc2c7d8b28bb52e224e66c4124b8a42d45",
    },
    "H3": {
        "tuple": (4, 5, 9, 2, 1, 1, 5, 10),
        "multi": 5,
        "signature": "278251e55ee1daf215d42e1f534bf811529ab9da39069e488c448f88014d3272",
    },
    "H4": {
        "tuple": (6, 6, 12, 1, 1, 0, 6, 11),
        "multi": 6,
        "signature": "d96362a72a4bd443d8e750ced1cebca4521ff28a9e5116bfe6e65c57d2cfbaf3",
    },
    "H5": {
        "tuple": (7, 7, 12, 0, 2, 0, 7, 12),
        "multi": 7,
        "signature": "9a0568400739c46729f811419f84a144a0dfd5de1031f30bd9a47834f101bdcd",
    },
}
TYPE_ORDER = tuple(TYPE_MANIFEST)
RECIPE_ORDER = (
    "valid-base",
    "R1",
    "C1",
    "T1",
    "V1",
    "M01",
    "M02",
    "M03",
    "M04",
    "M05",
    "M06",
    "M07",
)
RECIPE_RANK = {name: index for index, name in enumerate(RECIPE_ORDER)}
MULTI_RECIPE = {
    "M01": ("R1", "C1"),
    "M02": ("T1", "V1"),
    "M03": ("C1", "V1"),
    "M04": ("Q0-missing", "T1"),
    "M05": ("Q0-extra", "C1"),
    "M06": ("Q0-bool", "R1"),
    "M07": ("Q0-extra", "V1"),
}
RECIPE_FAMILIES = {
    "valid-base": (),
    "R1": ("identity",),
    "C1": ("conservation",),
    "T1": ("transition",),
    "V1": ("revision",),
    "Q0-missing": ("schema",),
    "Q0-extra": ("schema",),
    "Q0-bool": ("schema",),
}
SINGLE_RECIPE = {"R1", "C1", "T1", "V1"}

# These are immutable, independently transcribed protocol fixtures.  They are
# intentionally not built from TRACE_TABLE, RECIPE_ORDER, _recipe_ids,
# MULTI_RECIPE, or _apply_recipe.  Runtime sanity compares generated objects
# against these literals before any scoring is allowed.
INDEPENDENT_TRACE_MANIFEST = MappingProxyType(
    {
        "H0": (
            ("pending", "active", "active", "closed"),
            ("pending", "active", "closed"),
            ("pending", "active", "active", "closed"),
        ),
        "H1": (
            ("pending", "active", "active", "closed"),
            ("pending", "active", "closed"),
            ("pending", "closed"),
            ("pending", "active", "closed"),
        ),
        "H2": (
            ("pending", "active", "active", "closed"),
            ("pending", "active", "closed"),
            ("pending", "closed"),
            ("pending", "active", "closed"),
            ("pending", "closed"),
        ),
        "H3": (
            ("pending", "active", "closed"),
            ("pending", "active", "active", "closed"),
            ("pending", "closed"),
            ("pending", "active", "active", "closed"),
        ),
        "H4": (
            ("pending", "active", "active", "closed"),
            ("pending", "active", "closed"),
            ("pending", "closed"),
            ("pending", "active", "closed"),
            ("pending", "active", "closed"),
            ("pending", "active", "closed"),
        ),
        "H5": (
            ("pending", "active", "closed"),
            ("pending", "active", "closed"),
            ("pending", "active", "closed"),
            ("pending", "active", "closed"),
            ("pending", "active", "closed"),
            ("pending", "closed"),
            ("pending", "closed"),
        ),
    }
)
INDEPENDENT_TYPE_ORDER = ("H0", "H1", "H2", "H3", "H4", "H5")
INDEPENDENT_RECIPE_MANIFEST = MappingProxyType(
    {
        "H0": ("valid-base", "R1", "C1", "T1", "V1", "M01", "M02"),
        "H1": ("valid-base", "R1", "C1", "T1", "V1", "M01", "M02", "M03"),
        "H2": ("valid-base", "R1", "C1", "T1", "V1", "M01", "M02", "M03", "M04"),
        "H3": ("valid-base", "R1", "C1", "T1", "V1", "M01", "M02", "M03", "M04", "M05"),
        "H4": ("valid-base", "R1", "C1", "T1", "V1", "M01", "M02", "M03", "M04", "M05", "M06"),
        "H5": ("valid-base", "R1", "C1", "T1", "V1", "M01", "M02", "M03", "M04", "M05", "M06", "M07"),
    }
)
INDEPENDENT_SIGNATURE_MANIFEST = MappingProxyType(
    {
        "H0": ((3, 3, 8, 2, 0, 0, 2, 7), "2e80ccf18dad2a97d8d3e975b0f726f6cf15687fa6e4f50ddf55a940e6d29e9b"),
        "H1": ((4, 4, 8, 1, 1, 0, 3, 8), "0195af9dd2a1ef0f4348c6fc6f082b626d7c9ab1c310c9487d5760bf74afa574"),
        "H2": ((5, 5, 9, 1, 2, 0, 4, 9), "0863b001f0a85dc2582be68a41d33afc2c7d8b28bb52e224e66c4124b8a42d45"),
        "H3": ((4, 5, 9, 2, 1, 1, 5, 10), "278251e55ee1daf215d42e1f534bf811529ab9da39069e488c448f88014d3272"),
        "H4": ((6, 6, 12, 1, 1, 0, 6, 11), "d96362a72a4bd443d8e750ced1cebca4521ff28a9e5116bfe6e65c57d2cfbaf3"),
        "H5": ((7, 7, 12, 0, 2, 0, 7, 12), "9a0568400739c46729f811419f84a144a0dfd5de1031f30bd9a47834f101bdcd"),
    }
)
INDEPENDENT_CASE_KIND_MANIFEST = MappingProxyType(
    {
        "valid-base": "valid",
        "R1": "single",
        "C1": "single",
        "T1": "single",
        "V1": "single",
        "M01": "multi",
        "M02": "multi",
        "M03": "multi",
        "M04": "multi",
        "M05": "multi",
        "M06": "multi",
        "M07": "multi",
    }
)
INDEPENDENT_FAULT_MANIFEST = MappingProxyType(
    {
        "valid-base": (),
        "R1": ("identity",),
        "C1": ("conservation",),
        "T1": ("transition",),
        "V1": ("revision",),
        "M01": ("conservation", "identity"),
        "M02": ("revision", "transition"),
        "M03": ("conservation", "revision"),
        "M04": ("schema", "transition"),
        "M05": ("conservation", "schema"),
        "M06": ("identity", "schema"),
        "M07": ("revision", "schema"),
    }
)
INDEPENDENT_MULTI_OBSERVED_FAILURES = MappingProxyType(
    {
        "M01": ("conservation", "identity"),
        "M02": ("revision", "transition"),
        "M03": ("conservation", "revision"),
        "M04": ("conservation", "identity", "revision", "schema", "transition"),
        "M05": ("conservation", "identity", "revision", "schema", "transition"),
        "M06": ("conservation", "identity", "revision", "schema", "transition"),
        "M07": ("conservation", "identity", "revision", "schema", "transition"),
    }
)
INDEPENDENT_MULTI_RELATION = MappingProxyType(
    {
        "M01": "equals", "M02": "equals", "M03": "equals",
        "M04": "contains", "M05": "contains", "M06": "contains", "M07": "contains",
    }
)


def _immutable_footprints(
    amount_pointer: str,
) -> Mapping[str, tuple[str, ...]]:
    """Return a frozen copy of one literal footprint table.

    The operation strings below are literal; only the H3/non-H3 ledger
    pointer differs in the independently transcribed tables.
    """

    return MappingProxyType(
        {
            "valid-base": (),
            "R1": ("replace:/ledger/1/entry_id",),
            "C1": (f"replace:{amount_pointer}",),
            "T1": ("replace:/events/1/to_state",),
            "V1": ("replace:/events/1/revision",),
            "M01": ("replace:/ledger/1/entry_id", f"replace:{amount_pointer}"),
            "M02": ("replace:/events/1/revision", "replace:/events/1/to_state"),
            "M03": ("replace:/events/1/revision", f"replace:{amount_pointer}"),
            "M04": ("remove:/events/0/revision", "replace:/events/1/to_state"),
            "M05": ("add:/ledger/0/debug", f"replace:{amount_pointer}"),
            "M06": ("replace:/ledger/1/entry_id", "replace:/meta/declared_total_cents"),
            "M07": ("add:/ledger/0/debug", "replace:/events/1/revision"),
        }
    )


INDEPENDENT_FOOTPRINT_MANIFEST = MappingProxyType(
    {
        "H0": _immutable_footprints("/ledger/2/amount_cents"),
        "H1": _immutable_footprints("/ledger/3/amount_cents"),
        "H2": _immutable_footprints("/ledger/4/amount_cents"),
        "H3": _immutable_footprints("/ledger/4/amount_cents"),
        "H4": _immutable_footprints("/ledger/5/amount_cents"),
        "H5": _immutable_footprints("/ledger/6/amount_cents"),
    }
)
INDEPENDENT_DIAGNOSTIC_CLUSTER_IDS = MappingProxyType(
    {
        "d1": tuple(
            f"{cluster_type}-C{local_index:02d}"
            for cluster_type in ("H0", "H1", "H2", "H3", "H4", "H5")
            for local_index in range(8, 16)
        ),
        "d2": tuple(
            f"{cluster_type}-C{local_index:02d}"
            for cluster_type in ("H0", "H1", "H2", "H3", "H4")
            for local_index in range(8, 16)
        ),
        "d3": tuple(
            f"{cluster_type}-C{local_index:02d}"
            for cluster_type in ("H1", "H2", "H3", "H4", "H5")
            for local_index in range(8, 16)
        ),
    }
)

# The following fixtures are a second transcription of the *construction*
# contract.  They are deliberately literal rather than projections of the
# producer tables above.  In particular, changing TRACE_TABLE, a recipe
# sequence, or a mutation helper cannot silently change the expected payload.
INDEPENDENT_PAYLOAD_PROTOCOL = "E002-v1"
INDEPENDENT_ENTITY_ID_FORMAT = "entity-{entity_index}"
INDEPENDENT_LEDGER_ID_FORMAT = "ledger-{ledger_index}"
INDEPENDENT_EVENT_ID_FORMAT = "event-{entity_index}-{revision}"
INDEPENDENT_BASE_STATES = ("pending", "active", "closed")
INDEPENDENT_SPLIT_CLUSTER_TYPE = "H3"
INDEPENDENT_SPLIT_ENTITY_INDEX = 0
INDEPENDENT_AMOUNT_MODULUS = 800
INDEPENDENT_AMOUNT_OFFSET = 200
INDEPENDENT_RECIPE_ORDER = (
    "valid-base", "R1", "C1", "T1", "V1", "M01", "M02", "M03",
    "M04", "M05", "M06", "M07",
)
INDEPENDENT_RECIPE_SEQUENCE = MappingProxyType(
    {
        "valid-base": (),
        "R1": ("R1",),
        "C1": ("C1",),
        "T1": ("T1",),
        "V1": ("V1",),
        "M01": ("R1", "C1"),
        "M02": ("T1", "V1"),
        "M03": ("C1", "V1"),
        "M04": ("Q0-missing", "T1"),
        "M05": ("Q0-extra", "C1"),
        "M06": ("Q0-bool", "R1"),
        "M07": ("Q0-extra", "V1"),
    }
)
INDEPENDENT_RECIPE_OPERATION_MANIFEST = MappingProxyType(
    {
        "valid-base": (),
        "R1": (("copy", "/ledger/1/entry_id", "/ledger/0/entry_id"),),
        "C1": (("increment", "/ledger/last/amount_cents", 1),),
        "T1": (("set", "/events/1/to_state", "pending"),),
        "V1": (("set", "/events/1/revision", 1),),
        "Q0-missing": (("remove", "/events/0/revision"),),
        "Q0-extra": (("add", "/ledger/0/debug", "unexpected"),),
        "Q0-bool": (("set", "/meta/declared_total_cents", True),),
        "M01": (
            ("copy", "/ledger/1/entry_id", "/ledger/0/entry_id"),
            ("increment", "/ledger/last/amount_cents", 1),
        ),
        "M02": (
            ("set", "/events/1/to_state", "pending"),
            ("set", "/events/1/revision", 1),
        ),
        "M03": (
            ("increment", "/ledger/last/amount_cents", 1),
            ("set", "/events/1/revision", 1),
        ),
        "M04": (
            ("remove", "/events/0/revision"),
            ("set", "/events/1/to_state", "pending"),
        ),
        "M05": (
            ("add", "/ledger/0/debug", "unexpected"),
            ("increment", "/ledger/last/amount_cents", 1),
        ),
        "M06": (
            ("set", "/meta/declared_total_cents", True),
            ("copy", "/ledger/1/entry_id", "/ledger/0/entry_id"),
        ),
        "M07": (
            ("add", "/ledger/0/debug", "unexpected"),
            ("set", "/events/1/revision", 1),
        ),
    }
)


def _independent_amount_cents(cluster_index: int, entity_index: int) -> int:
    material = f"E002-v1|amount|{cluster_index}|{entity_index}".encode("utf-8")
    return 200 + int.from_bytes(hashlib.sha256(material).digest()[:8], "big") % 800


def independently_rebuild_base_payload(
    cluster_index: int, cluster_type: str
) -> dict[str, Any]:
    """Rebuild a base payload from the locked literal construction contract."""

    if cluster_type not in INDEPENDENT_TRACE_MANIFEST:
        raise ProtocolError("unknown independent cluster type")
    entities: list[dict[str, Any]] = []
    ledger: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    total = 0
    ledger_index = 0
    for entity_index, trace in enumerate(INDEPENDENT_TRACE_MANIFEST[cluster_type]):
        amount = _independent_amount_cents(cluster_index, entity_index)
        parts = (
            (amount // 2, amount - amount // 2)
            if cluster_type == INDEPENDENT_SPLIT_CLUSTER_TYPE
            and entity_index == INDEPENDENT_SPLIT_ENTITY_INDEX
            else (amount,)
        )
        for part in parts:
            ledger.append(
                {
                    "entry_id": f"ledger-{ledger_index}",
                    "entity_id": f"entity-{entity_index}",
                    "amount_cents": part,
                }
            )
            ledger_index += 1
            total += part
        entities.append(
            {
                "entity_id": f"entity-{entity_index}",
                "current_state": "closed",
                "revision": len(trace) - 1,
            }
        )
        for revision in range(1, len(trace)):
            events.append(
                {
                    "event_id": f"event-{entity_index}-{revision}",
                    "entity_id": f"entity-{entity_index}",
                    "from_state": trace[revision - 1],
                    "to_state": trace[revision],
                    "revision": revision,
                }
            )
    return {
        "meta": {
            "schema_version": INDEPENDENT_PAYLOAD_PROTOCOL,
            "declared_total_cents": total,
        },
        "entities": entities,
        "ledger": ledger,
        "events": events,
    }


def _independent_set(payload: dict[str, Any], pointer: str, value: Any) -> None:
    parts = pointer.strip("/").split("/")
    target: Any = payload
    for part in parts[:-1]:
        if isinstance(target, list):
            target = target[-1] if part == "last" else target[int(part)]
        else:
            target = target[part]
    final = parts[-1]
    if isinstance(target, list):
        target[-1 if final == "last" else int(final)] = value
    else:
        target[final] = value


def _independent_get(payload: Mapping[str, Any], pointer: str) -> Any:
    target: Any = payload
    for part in pointer.strip("/").split("/"):
        if isinstance(target, list):
            target = target[-1] if part == "last" else target[int(part)]
        else:
            target = target[part]
    return target


def _independent_remove(payload: dict[str, Any], pointer: str) -> None:
    parts = pointer.strip("/").split("/")
    target: Any = payload
    for part in parts[:-1]:
        if isinstance(target, list):
            target = target[-1] if part == "last" else target[int(part)]
        else:
            target = target[part]
    final = parts[-1]
    if isinstance(target, list):
        del target[-1 if final == "last" else int(final)]
    else:
        del target[final]


def independently_apply_recipe(
    base_payload: Mapping[str, Any], recipe_id: str
) -> dict[str, Any]:
    """Apply the independently locked operation/value/order recipe."""

    if recipe_id not in INDEPENDENT_RECIPE_OPERATION_MANIFEST:
        raise ProtocolError("unknown independent recipe")
    output = copy.deepcopy(base_payload)
    for operation in INDEPENDENT_RECIPE_OPERATION_MANIFEST[recipe_id]:
        kind = operation[0]
        if kind == "copy":
            _independent_set(output, operation[1], copy.deepcopy(
                _independent_get(output, operation[2])
            ))
        elif kind == "increment":
            current = _independent_get(output, operation[1])
            _independent_set(output, operation[1], current + operation[2])
        elif kind == "set":
            _independent_set(output, operation[1], operation[2])
        elif kind == "remove":
            _independent_remove(output, operation[1])
        elif kind == "add":
            _independent_set(output, operation[1], operation[2])
        else:
            raise ProtocolError("unknown independent operation")
    return output


def _signature_input(cluster_type: str) -> str:
    values = TYPE_MANIFEST[cluster_type]["tuple"]
    return (
        f"{PROTOCOL_VERSION}|signature|entities={values[0]}|ledger={values[1]}"
        f"|events={values[2]}|active_active={values[3]}"
        f"|pending_closed={values[4]}|split={values[5]}"
        f"|multi={values[6]}|cases={values[7]}"
    )


def _recipe_ids(cluster_type: str) -> tuple[str, ...]:
    count = TYPE_MANIFEST[cluster_type]["multi"]
    return RECIPE_ORDER[: 5 + count]


@dataclass(frozen=True)
class ValidationResult:
    decision: bool
    raw_score: int
    failed_families: tuple[str, ...] = ()


@dataclass(frozen=True)
class OracleResult:
    schema_valid: bool
    truth: int
    failed_families: tuple[str, ...]
    base_structure_flags: tuple[str, ...]
    family_passes: tuple[tuple[str, bool], ...]


@dataclass(frozen=True)
class Case:
    split: str
    cluster_id: str
    cluster_type: str
    local_index: int
    cluster_index: int
    case_id: str
    case_kind: str
    recipe_id: str
    fault_set: tuple[str, ...]
    footprint: tuple[str, ...]
    base_hash: str
    input_sha256: str
    base_structure_flags: tuple[str, ...]
    schema_valid: bool
    truth: int
    oracle_failure_set: tuple[str, ...]
    payload: dict[str, Any]


@dataclass(frozen=True)
class Cluster:
    split: str
    cluster_type: str
    local_index: int
    cluster_index: int
    cluster_id: str
    structural_signature: tuple[int, ...]
    signature_sha256: str
    base_hash: str
    cases: tuple[Case, ...]


@dataclass(frozen=True)
class Population:
    clusters: tuple[Cluster, ...]

    @property
    def cases(self) -> tuple[Case, ...]:
        return tuple(case for cluster in self.clusters for case in cluster.cases)

    def by_split(self) -> dict[str, tuple[Case, ...]]:
        return {
            split: tuple(case for case in self.cases if case.split == split)
            for split in SPLITS
        }

    def clusters_by_split(self) -> dict[str, tuple[Cluster, ...]]:
        return {
            split: tuple(cluster for cluster in self.clusters if cluster.split == split)
            for split in SPLITS
        }


def _amount_cents(cluster_index: int, entity_index: int) -> int:
    material = f"{PROTOCOL_VERSION}|amount|{cluster_index}|{entity_index}".encode()
    return 200 + int.from_bytes(hashlib.sha256(material).digest()[:8], "big") % 800


def generate_base_payload(cluster_index: int, cluster_type: str) -> dict[str, Any]:
    if cluster_type not in TRACE_TABLE:
        raise ProtocolError("unknown cluster type")
    traces = TRACE_TABLE[cluster_type]
    entities: list[dict[str, Any]] = []
    ledger: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    total = 0
    ledger_index = 0
    split_entity = 0 if cluster_type == "H3" else -1
    for entity_index, trace in enumerate(traces):
        amount = _amount_cents(cluster_index, entity_index)
        amounts = (
            (amount // 2, amount - amount // 2)
            if entity_index == split_entity
            else (amount,)
        )
        for part in amounts:
            ledger.append(
                {
                    "entry_id": f"ledger-{ledger_index}",
                    "entity_id": f"entity-{entity_index}",
                    "amount_cents": part,
                }
            )
            ledger_index += 1
            total += part
        entities.append(
            {
                "entity_id": f"entity-{entity_index}",
                "current_state": "closed",
                "revision": len(trace) - 1,
            }
        )
        for revision, (from_state, to_state) in enumerate(
            zip(trace, trace[1:]), start=1
        ):
            events.append(
                {
                    "event_id": f"event-{entity_index}-{revision}",
                    "entity_id": f"entity-{entity_index}",
                    "from_state": from_state,
                    "to_state": to_state,
                    "revision": revision,
                }
            )
    return {
        "meta": {
            "schema_version": PROTOCOL_VERSION,
            "declared_total_cents": total,
        },
        "entities": entities,
        "ledger": ledger,
        "events": events,
    }


def _set_pointer(payload: dict[str, Any], pointer: str, value: Any) -> None:
    parts = pointer.strip("/").split("/")
    target: Any = payload
    for part in parts[:-1]:
        target = target[int(part)] if isinstance(target, list) else target[part]
    final = parts[-1]
    if isinstance(target, list):
        target[int(final)] = value
    else:
        target[final] = value


def _remove_pointer(payload: dict[str, Any], pointer: str) -> None:
    parts = pointer.strip("/").split("/")
    target: Any = payload
    for part in parts[:-1]:
        target = target[int(part)] if isinstance(target, list) else target[part]
    final = parts[-1]
    if isinstance(target, list):
        del target[int(final)]
    else:
        del target[final]


def _apply_named_mutation(
    payload: dict[str, Any], mutation: str
) -> None:
    if mutation == "R1":
        _set_pointer(payload, "/ledger/1/entry_id", payload["ledger"][0]["entry_id"])
    elif mutation == "C1":
        payload["ledger"][-1]["amount_cents"] += 1
    elif mutation == "T1":
        _set_pointer(payload, "/events/1/to_state", "pending")
    elif mutation == "V1":
        _set_pointer(payload, "/events/1/revision", 1)
    elif mutation == "Q0-missing":
        _remove_pointer(payload, "/events/0/revision")
    elif mutation == "Q0-extra":
        _set_pointer(payload, "/ledger/0/debug", "unexpected")
    elif mutation == "Q0-bool":
        _set_pointer(payload, "/meta/declared_total_cents", True)
    else:
        raise ProtocolError(f"unknown mutation {mutation}")


def _pointer_differences(
    left: Any, right: Any, pointer: str = ""
) -> list[str]:
    if type(left) is not type(right):
        return [f"replace:{pointer or '/'}"]
    if isinstance(left, dict):
        output: list[str] = []
        for key in _utf8_sorted(set(left) | set(right)):
            child = pointer + "/" + key
            if key not in left:
                output.append(f"add:{child}")
            elif key not in right:
                output.append(f"remove:{child}")
            else:
                output.extend(_pointer_differences(left[key], right[key], child))
        return output
    if isinstance(left, list):
        if len(left) != len(right):
            return [f"replace:{pointer or '/'}"]
        output = []
        for index, (left_item, right_item) in enumerate(zip(left, right)):
            output.extend(_pointer_differences(left_item, right_item, f"{pointer}/{index}"))
        return output
    if left != right:
        return [f"replace:{pointer or '/'}"]
    return []


def _apply_recipe(
    base_payload: dict[str, Any], recipe_id: str
) -> tuple[dict[str, Any], tuple[str, ...]]:
    mutated = copy.deepcopy(base_payload)
    if recipe_id == "valid-base":
        operations = ()
    elif recipe_id in RECIPE_FAMILIES:
        operations = (recipe_id,)
    else:
        operations = MULTI_RECIPE[recipe_id]
    for operation in operations:
        _apply_named_mutation(mutated, operation)
    footprint = tuple(sorted(_pointer_differences(base_payload, mutated), key=lambda x: x.encode()))
    return mutated, footprint


def _case_kind(recipe_id: str) -> str:
    if recipe_id == "valid-base":
        return "valid"
    if recipe_id in SINGLE_RECIPE:
        return "single"
    return "multi"


def _intended_families(recipe_id: str) -> tuple[str, ...]:
    if recipe_id in RECIPE_FAMILIES:
        return tuple(sorted(RECIPE_FAMILIES[recipe_id]))
    families = set()
    for operation in MULTI_RECIPE[recipe_id]:
        families.update(RECIPE_FAMILIES[operation])
    return tuple(sorted(families))


def _split_for_local(local_index: int) -> str:
    if local_index < 4:
        return "development"
    if local_index < 8:
        return "calibration"
    return "confirmatory"


def _generate_population_once() -> Population:
    clusters: list[Cluster] = []
    for type_index, cluster_type in enumerate(TYPE_ORDER):
        info = TYPE_MANIFEST[cluster_type]
        for local_index in range(16):
            split = _split_for_local(local_index)
            cluster_index = type_index * 16 + local_index
            cluster_id = f"{cluster_type}-C{local_index:02d}"
            base = generate_base_payload(cluster_index, cluster_type)
            base_hash = canonical_sha256(base)
            flags = reference_oracle(base).base_structure_flags
            cases: list[Case] = []
            for recipe_id in _recipe_ids(cluster_type):
                payload, footprint = _apply_recipe(base, recipe_id)
                oracle = reference_oracle(payload)
                case_id = f"{cluster_id}::{recipe_id}"
                cases.append(
                    Case(
                        split=split,
                        cluster_id=cluster_id,
                        cluster_type=cluster_type,
                        local_index=local_index,
                        cluster_index=cluster_index,
                        case_id=case_id,
                        case_kind=_case_kind(recipe_id),
                        recipe_id=recipe_id,
                        fault_set=_intended_families(recipe_id),
                        footprint=footprint,
                        base_hash=base_hash,
                        input_sha256=canonical_sha256(payload),
                        base_structure_flags=flags,
                        schema_valid=oracle.schema_valid,
                        truth=oracle.truth,
                        oracle_failure_set=oracle.failed_families,
                        payload=payload,
                    )
                )
            expected = info["tuple"]
            signature_input = _signature_input(cluster_type)
            clusters.append(
                Cluster(
                    split=split,
                    cluster_type=cluster_type,
                    local_index=local_index,
                    cluster_index=cluster_index,
                    cluster_id=cluster_id,
                    structural_signature=expected,
                    signature_sha256=sha256_hex(signature_input),
                    base_hash=base_hash,
                    cases=tuple(cases),
                )
            )
    return Population(tuple(clusters))


def generate_population() -> Population:
    return _generate_population_once()


def generate_all_splits() -> dict[str, tuple[Case, ...]]:
    return generate_population().by_split()


def independent_payload_traces(payload: Mapping[str, Any]) -> tuple[tuple[str, ...], ...]:
    """Recover traces from payload records without consulting generator tables."""

    by_entity: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for event in payload["events"]:
        by_entity[event["entity_id"]].append(event)
    traces: list[tuple[str, ...]] = []
    for entity in payload["entities"]:
        sequence = by_entity[entity["entity_id"]]
        if not sequence:
            raise ProtocolError("trace extraction found an entity without events")
        traces.append(
            (sequence[0]["from_state"],)
            + tuple(event["to_state"] for event in sequence)
        )
    return tuple(traces)


# ---------------------------------------------------------------------------
# Independently maintained reference oracle.
# ---------------------------------------------------------------------------


def reference_oracle(payload: Any) -> OracleResult:
    """Evaluate truth using a literal reference implementation only."""

    oracle_schema_ok = True
    try:
        if type(payload) is not dict or set(payload) != {"meta", "entities", "ledger", "events"}:
            oracle_schema_ok = False
        meta = payload["meta"] if oracle_schema_ok else None
        entities = payload["entities"] if oracle_schema_ok else None
        ledger = payload["ledger"] if oracle_schema_ok else None
        events = payload["events"] if oracle_schema_ok else None
        if oracle_schema_ok and type(meta) is not dict:
            oracle_schema_ok = False
        if oracle_schema_ok and set(meta) != {"schema_version", "declared_total_cents"}:
            oracle_schema_ok = False
        if oracle_schema_ok and (
            type(meta["schema_version"]) is not str
            or not re.fullmatch(r"E002-v1", meta["schema_version"])
            or type(meta["declared_total_cents"]) is not int
            or type(meta["declared_total_cents"]) is bool
            or not 600 <= meta["declared_total_cents"] <= 6994
        ):
            oracle_schema_ok = False
        if oracle_schema_ok and (
            type(entities) is not list or not 3 <= len(entities) <= 7
            or type(ledger) is not list or not 3 <= len(ledger) <= 7
            or type(events) is not list or not 8 <= len(events) <= 12
        ):
            oracle_schema_ok = False
        entity_pattern = re.compile(r"entity-[0-6]")
        ledger_pattern = re.compile(r"ledger-[0-6]")
        event_pattern = re.compile(r"event-[0-6]-([1-9]|1[0-2])")
        if oracle_schema_ok:
            for entity in entities:
                if (
                    type(entity) is not dict
                    or set(entity) != {"entity_id", "current_state", "revision"}
                    or type(entity["entity_id"]) is not str
                    or entity_pattern.fullmatch(entity["entity_id"]) is None
                    or entity["current_state"] not in {"pending", "active", "closed"}
                    or type(entity["revision"]) is not int
                    or type(entity["revision"]) is bool
                    or not 1 <= entity["revision"] <= 12
                ):
                    oracle_schema_ok = False
                    break
        if oracle_schema_ok:
            for entry in ledger:
                if (
                    type(entry) is not dict
                    or set(entry) != {"entry_id", "entity_id", "amount_cents"}
                    or type(entry["entry_id"]) is not str
                    or ledger_pattern.fullmatch(entry["entry_id"]) is None
                    or type(entry["entity_id"]) is not str
                    or entity_pattern.fullmatch(entry["entity_id"]) is None
                    or type(entry["amount_cents"]) is not int
                    or type(entry["amount_cents"]) is bool
                    or not 1 <= entry["amount_cents"] <= 200000
                ):
                    oracle_schema_ok = False
                    break
        if oracle_schema_ok:
            for event in events:
                if (
                    type(event) is not dict
                    or set(event) != {"event_id", "entity_id", "from_state", "to_state", "revision"}
                    or type(event["event_id"]) is not str
                    or event_pattern.fullmatch(event["event_id"]) is None
                    or type(event["entity_id"]) is not str
                    or entity_pattern.fullmatch(event["entity_id"]) is None
                    or event["from_state"] not in {"pending", "active", "closed"}
                    or event["to_state"] not in {"pending", "active", "closed"}
                    or type(event["revision"]) is not int
                    or type(event["revision"]) is bool
                    or not 1 <= event["revision"] <= 12
                ):
                    oracle_schema_ok = False
                    break
    except (KeyError, TypeError, AttributeError):
        oracle_schema_ok = False

    flags = set()
    if isinstance(payload, dict) and isinstance(payload.get("events"), list):
        for event in payload["events"]:
            if isinstance(event, dict):
                edge = (event.get("from_state"), event.get("to_state"))
                if edge == ("active", "active"):
                    flags.add("active-active")
                if edge == ("pending", "closed"):
                    flags.add("pending-closed")
    structure_flags = tuple(sorted(flags))
    if not oracle_schema_ok:
        failed = tuple(sorted(ORACLE_FAMILY_ORDER, key=lambda item: item.encode("utf-8")))
        return OracleResult(
            False,
            0,
            failed,
            structure_flags,
            tuple((name, False) for name in ORACLE_FAMILY_ORDER),
        )

    entity_ids = [entity["entity_id"] for entity in entities]
    ledger_ids = [entry["entry_id"] for entry in ledger]
    ledger_entities = [entry["entity_id"] for entry in ledger]
    identity_ok = (
        len(set(entity_ids)) == len(entity_ids)
        and len(set(ledger_ids)) == len(ledger_ids)
        and all(reference in entity_ids for reference in ledger_entities)
        and set(ledger_entities) == set(entity_ids)
    )
    conservation_ok = (
        all(entry["amount_cents"] > 0 for entry in ledger)
        and sum(entry["amount_cents"] for entry in ledger) == meta["declared_total_cents"]
    )
    events_by_entity: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        events_by_entity[event["entity_id"]].append(event)
    transition_ok = True
    if set(events_by_entity) != set(entity_ids):
        transition_ok = False
    for entity in entities:
        current = "pending"
        sequence = events_by_entity.get(entity["entity_id"], [])
        for event in sequence:
            edge = (event["from_state"], event["to_state"])
            if current == "closed" or event["from_state"] != current:
                transition_ok = False
            if edge not in ORACLE_ALLOWED_EDGES:
                transition_ok = False
            current = event["to_state"]
        if current != "closed" or entity["current_state"] != "closed":
            transition_ok = False
    revision_ok = True
    if set(events_by_entity) != set(entity_ids):
        revision_ok = False
    for entity in entities:
        sequence = events_by_entity.get(entity["entity_id"], [])
        revisions = [event["revision"] for event in sequence]
        if revisions != list(range(1, len(sequence) + 1)):
            revision_ok = False
        if entity["revision"] != len(sequence):
            revision_ok = False
    family_values = {
        "schema": True,
        "identity": identity_ok,
        "conservation": conservation_ok,
        "transition": transition_ok,
        "revision": revision_ok,
    }
    failed = tuple(
        sorted(
            (name for name in ORACLE_FAMILY_ORDER if not family_values[name]),
            key=lambda item: item.encode("utf-8"),
        )
    )
    return OracleResult(
        True,
        int(not failed),
        failed,
        structure_flags,
        tuple((name, family_values[name]) for name in ORACLE_FAMILY_ORDER),
    )


# ---------------------------------------------------------------------------
# Payload-only B0 and evaluated checker implementation.
# ---------------------------------------------------------------------------


def sanitize_payload(payload: Any) -> dict[str, Any] | None:
    """Return a fresh exact-schema payload or None, never raising."""

    try:
        if type(payload) is not dict or set(payload) != {"meta", "entities", "ledger", "events"}:
            return None
        meta = payload["meta"]
        entities = payload["entities"]
        ledger = payload["ledger"]
        events = payload["events"]
        if type(meta) is not dict or set(meta) != {"schema_version", "declared_total_cents"}:
            return None
        if type(meta["schema_version"]) is not str or re.fullmatch(r"^E002-v1$", meta["schema_version"]) is None:
            return None
        if (
            type(meta["declared_total_cents"]) is not int
            or type(meta["declared_total_cents"]) is bool
            or not 600 <= meta["declared_total_cents"] <= 6994
        ):
            return None
        if type(entities) is not list or not 3 <= len(entities) <= 7:
            return None
        if type(ledger) is not list or not 3 <= len(ledger) <= 7:
            return None
        if type(events) is not list or not 8 <= len(events) <= 12:
            return None
        for entity in entities:
            if type(entity) is not dict or set(entity) != {"entity_id", "current_state", "revision"}:
                return None
            if type(entity["entity_id"]) is not str or re.fullmatch(r"^entity-[0-6]$", entity["entity_id"]) is None:
                return None
            if entity["current_state"] not in {"pending", "active", "closed"}:
                return None
            if type(entity["revision"]) is not int or type(entity["revision"]) is bool or not 1 <= entity["revision"] <= 12:
                return None
        for entry in ledger:
            if type(entry) is not dict or set(entry) != {"entry_id", "entity_id", "amount_cents"}:
                return None
            if type(entry["entry_id"]) is not str or re.fullmatch(r"^ledger-[0-6]$", entry["entry_id"]) is None:
                return None
            if type(entry["entity_id"]) is not str or re.fullmatch(r"^entity-[0-6]$", entry["entity_id"]) is None:
                return None
            if type(entry["amount_cents"]) is not int or type(entry["amount_cents"]) is bool or not 1 <= entry["amount_cents"] <= 200000:
                return None
        for event in events:
            if type(event) is not dict or set(event) != {"event_id", "entity_id", "from_state", "to_state", "revision"}:
                return None
            if type(event["event_id"]) is not str or re.fullmatch(r"^event-[0-6]-([1-9]|1[0-2])$", event["event_id"]) is None:
                return None
            if type(event["entity_id"]) is not str or re.fullmatch(r"^entity-[0-6]$", event["entity_id"]) is None:
                return None
            if event["from_state"] not in {"pending", "active", "closed"} or event["to_state"] not in {"pending", "active", "closed"}:
                return None
            if type(event["revision"]) is not int or type(event["revision"]) is bool or not 1 <= event["revision"] <= 12:
                return None
        return copy.deepcopy(payload)
    except (KeyError, TypeError, AttributeError, ValueError):
        return None


def validate_b0(payload: Any) -> ValidationResult:
    cleaned = sanitize_payload(payload)
    return ValidationResult(cleaned is not None, 0 if cleaned is not None else 1, () if cleaned is not None else ("schema",))


def _checker_schema_copy(payload: Any) -> dict[str, Any] | None:
    """Checker-owned schema path; it intentionally does not call B0 or oracle."""

    try:
        if type(payload) is not dict or set(payload) != {"meta", "entities", "ledger", "events"}:
            return None
        meta = payload["meta"]
        if type(meta) is not dict or set(meta) != {"schema_version", "declared_total_cents"}:
            return None
        if type(meta.get("schema_version")) is not str or meta["schema_version"] != "E002-v1":
            return None
        total = meta.get("declared_total_cents")
        if type(total) is not int or type(total) is bool or total < 600 or total > 6994:
            return None
        entities = payload["entities"]
        ledger = payload["ledger"]
        events = payload["events"]
        if type(entities) is not list or len(entities) < 3 or len(entities) > 7:
            return None
        if type(ledger) is not list or len(ledger) < 3 or len(ledger) > 7:
            return None
        if type(events) is not list or len(events) < 8 or len(events) > 12:
            return None
        for item in entities:
            if type(item) is not dict or set(item.keys()) != {"entity_id", "current_state", "revision"}:
                return None
            if type(item["entity_id"]) is not str or re.fullmatch(r"^entity-[0-6]$", item["entity_id"]) is None:
                return None
            if item["current_state"] not in ("pending", "active", "closed"):
                return None
            if type(item["revision"]) is not int or type(item["revision"]) is bool or not (1 <= item["revision"] <= 12):
                return None
        for item in ledger:
            if type(item) is not dict or set(item.keys()) != {"entry_id", "entity_id", "amount_cents"}:
                return None
            if type(item["entry_id"]) is not str or re.fullmatch(r"^ledger-[0-6]$", item["entry_id"]) is None:
                return None
            if type(item["entity_id"]) is not str or re.fullmatch(r"^entity-[0-6]$", item["entity_id"]) is None:
                return None
            if type(item["amount_cents"]) is not int or type(item["amount_cents"]) is bool or not (1 <= item["amount_cents"] <= 200000):
                return None
        for item in events:
            if type(item) is not dict or set(item.keys()) != {"event_id", "entity_id", "from_state", "to_state", "revision"}:
                return None
            if type(item["event_id"]) is not str or re.fullmatch(r"^event-[0-6]-([1-9]|1[0-2])$", item["event_id"]) is None:
                return None
            if type(item["entity_id"]) is not str or re.fullmatch(r"^entity-[0-6]$", item["entity_id"]) is None:
                return None
            if item["from_state"] not in ("pending", "active", "closed") or item["to_state"] not in ("pending", "active", "closed"):
                return None
            if type(item["revision"]) is not int or type(item["revision"]) is bool or not (1 <= item["revision"] <= 12):
                return None
        return copy.deepcopy(payload)
    except (KeyError, TypeError, AttributeError, ValueError):
        return None


def _checker_identity(cleaned: dict[str, Any]) -> bool:
    entity_ids = [item["entity_id"] for item in cleaned["entities"]]
    entry_ids = [item["entry_id"] for item in cleaned["ledger"]]
    references = [item["entity_id"] for item in cleaned["ledger"]]
    return (
        len(set(entity_ids)) == len(entity_ids)
        and len(set(entry_ids)) == len(entry_ids)
        and set(references) == set(entity_ids)
    )


def _checker_conservation(cleaned: dict[str, Any]) -> bool:
    return (
        all(item["amount_cents"] > 0 for item in cleaned["ledger"])
        and sum(item["amount_cents"] for item in cleaned["ledger"])
        == cleaned["meta"]["declared_total_cents"]
    )


def _checker_ordered_replay(cleaned: dict[str, Any], allowed_edges: set[tuple[str, str]]) -> bool:
    per_entity: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in cleaned["events"]:
        per_entity[item["entity_id"]].append(item)
    if set(per_entity) != {item["entity_id"] for item in cleaned["entities"]}:
        return False
    for entity in cleaned["entities"]:
        state = "pending"
        for event in per_entity.get(entity["entity_id"], []):
            if state == "closed" or event["from_state"] != state:
                return False
            if (event["from_state"], event["to_state"]) not in allowed_edges:
                return False
            state = event["to_state"]
        if state != "closed" or entity["current_state"] != "closed":
            return False
    return True


def _checker_revision(cleaned: dict[str, Any]) -> bool:
    per_entity: dict[str, list[int]] = defaultdict(list)
    for item in cleaned["events"]:
        per_entity[item["entity_id"]].append(item["revision"])
    entity_revisions = {
        entity["entity_id"]: entity["revision"] for entity in cleaned["entities"]
    }
    if set(entity_revisions) != set(per_entity):
        return False
    return all(
        revisions == list(range(1, len(revisions) + 1))
        and entity_revisions[entity_id] == len(revisions)
        for entity_id, revisions in per_entity.items()
    )


def _checker_overconstraint(cleaned: dict[str, Any]) -> bool:
    return all(
        not (event["from_state"] == "active" and event["to_state"] == "active")
        for event in cleaned["events"]
    )


def _checker_stale_replay(cleaned: dict[str, Any]) -> bool:
    stale_edges = {
        ("pending", "active"),
        ("active", "active"),
        ("active", "closed"),
    }
    return _checker_ordered_replay(cleaned, stale_edges)


def checker_validation(payload: Any, method: str = "M1") -> ValidationResult:
    if method not in METHODS:
        raise ProtocolError(f"unknown method {method}")
    if method == "B0":
        return validate_b0(payload)
    cleaned = _checker_schema_copy(payload)
    if cleaned is None:
        retained = ("schema",)
        return ValidationResult(False, 1, retained)
    if method in {"M1", "M1-no-calibration"}:
        retained = ("schema", "identity", "conservation", "transition", "revision")
    elif method == "M1-omit-conservation":
        retained = ("schema", "identity", "transition", "revision")
    elif method == "M1-overconstraint":
        retained = (
            "schema",
            "identity",
            "conservation",
            "transition",
            "revision",
            "overconstraint",
        )
    elif method == "M1-stale-transition":
        retained = ("schema", "identity", "conservation", "transition", "revision")
    elif method == "M1-no-semantic":
        retained = ("schema", "transition", "revision")
    elif method == "M1-no-state":
        retained = ("schema", "identity", "conservation")
    else:
        raise ProtocolError(f"unsupported checker method {method}")
    checks: list[tuple[str, bool]] = [("schema", True)]
    if "identity" in retained:
        checks.append(("identity", _checker_identity(cleaned)))
    if "conservation" in retained:
        checks.append(("conservation", _checker_conservation(cleaned)))
    if "transition" in retained:
        allowed_edges = {
            ("pending", "active"),
            ("pending", "closed"),
            ("active", "active"),
            ("active", "closed"),
        }
        if method == "M1-stale-transition":
            allowed_edges = {
                ("pending", "active"),
                ("active", "active"),
                ("active", "closed"),
            }
        checks.append(
            (
                "transition",
                _checker_ordered_replay(cleaned, allowed_edges),
            )
        )
    if "revision" in retained:
        checks.append(("revision", _checker_revision(cleaned)))
    if "overconstraint" in retained:
        checks.append(("overconstraint", _checker_overconstraint(cleaned)))
    failed = tuple(name for name, passed in checks if not passed)
    return ValidationResult(not failed, len(failed), failed)


def validate_m1(payload: Any) -> ValidationResult:
    return checker_validation(payload, "M1")


def validate_m1_omit_conservation(payload: Any) -> ValidationResult:
    return checker_validation(payload, "M1-omit-conservation")


def validate_m1_overconstraint(payload: Any) -> ValidationResult:
    return checker_validation(payload, "M1-overconstraint")


def validate_m1_stale_transition(payload: Any) -> ValidationResult:
    return checker_validation(payload, "M1-stale-transition")


def validate_method(payload: Any, method: str) -> ValidationResult:
    return checker_validation(payload, method)


def _inspect_function_ast(function: Any) -> ast.AST:
    try:
        source = textwrap.dedent(inspect.getsource(function))
        return ast.parse(source)
    except (OSError, TypeError, SyntaxError) as error:
        raise ProtocolError(f"independence inspection failed for {function!r}") from error


def _is_semantic_reachable_object(value: Any) -> bool:
    return isinstance(value, (dict, list, set, frozenset, tuple, MappingProxyType))


# These are the only non-implementation Python callables that the graph walker
# may encounter through an imported module attribute.  They are serialization,
# inspection, container, or scalar-runtime primitives; a helper from an
# application/test module is never implicitly trusted.
_NON_SEMANTIC_EXTERNAL_MODULES = frozenset(
    {
        "ast", "builtins", "collections", "copy", "csv", "dataclasses",
        "datetime", "decimal", "fractions", "hashlib", "inspect", "io",
        "json", "math", "os", "pathlib", "re", "subprocess", "textwrap",
        "tempfile", "types", "typing",
    }
)


def _callable_module(value: Any) -> str | None:
    owner = getattr(value, "__func__", value)
    module = getattr(owner, "__module__", None)
    if module is None and callable(value) and not isinstance(value, type):
        module = getattr(type(value), "__module__", None)
    return module


def _callable_function(value: Any) -> Any | None:
    if inspect.isfunction(value):
        return value
    if inspect.ismethod(value):
        return getattr(value, "__func__", None)
    if callable(value) and not isinstance(value, type):
        candidate = getattr(type(value), "__call__", None)
        if inspect.isfunction(candidate):
            return candidate
    return None


def _is_explicitly_nonsemantic_callable(value: Any) -> bool:
    if isinstance(value, type) or inspect.isbuiltin(value):
        return True
    return _callable_module(value) in _NON_SEMANTIC_EXTERNAL_MODULES


def _independence_graph_detailed(
    root_names: Sequence[str],
) -> tuple[set[str], set[str], set[int], set[int]]:
    """Resolve functions, aliases, closures, and semantic object identities."""

    reachable: set[str] = set()
    global_names: set[str] = set()
    semantic_ids: set[int] = set()
    function_ids: set[int] = set()
    pending: list[tuple[str, Any]] = [
        (name, globals().get(name)) for name in root_names
    ]
    seen_functions: set[int] = set()
    seen_semantic_objects: set[int] = set()

    def record(name: str, value: Any) -> None:
        if isinstance(value, types.ModuleType) or value is None:
            return
        if callable(value):
            if _is_explicitly_nonsemantic_callable(value):
                return
            function = _callable_function(value)
            if (
                function is None
                or _callable_module(value) != __name__
                or getattr(function, "__module__", None) != __name__
            ):
                raise ProtocolError(
                    f"independence graph reached external callable: {name}"
                )
            pending.append((name, function))
            return
        if _is_semantic_reachable_object(value):
            object_id = id(value)
            semantic_ids.add(object_id)
            if object_id in seen_semantic_objects:
                return
            seen_semantic_objects.add(object_id)
            if isinstance(value, Mapping):
                children = tuple(value.keys()) + tuple(value.values())
            else:
                children = tuple(value)
            for index, child in enumerate(children):
                record(f"{name}[{index}]", child)

    while pending:
        label, candidate = pending.pop()
        if isinstance(candidate, types.ModuleType) or candidate is None:
            continue
        if not callable(candidate):
            continue
        if _is_explicitly_nonsemantic_callable(candidate):
            continue
        candidate = _callable_function(candidate)
        if (
            candidate is None
            or _callable_module(candidate) != __name__
            or getattr(candidate, "__module__", None) != __name__
        ):
            raise ProtocolError("independence graph reached external callable")
        candidate_id = id(candidate)
        if candidate_id in seen_functions:
            continue
        seen_functions.add(candidate_id)
        function_ids.add(candidate_id)
        reachable.add(label)
        reachable.add(getattr(candidate, "__name__", label))
        tree = _inspect_function_ast(candidate)
        try:
            closure = inspect.getclosurevars(candidate)
            environment = {
                **closure.globals,
                **closure.nonlocals,
                **closure.builtins,
            }
        except (OSError, TypeError):
            environment = {}
        for name, value in environment.items():
            if name in globals():
                global_names.add(name)

        def resolve(expression: ast.AST) -> Any:
            if isinstance(expression, ast.Name):
                return environment.get(expression.id, globals().get(expression.id))
            if isinstance(expression, ast.Attribute):
                parent = resolve(expression.value)
                try:
                    return getattr(parent, expression.attr)
                except (AttributeError, TypeError):
                    return None
            return None

        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                value = environment.get(node.id, globals().get(node.id))
                if node.id in globals():
                    global_names.add(node.id)
                record(node.id, value)
            elif isinstance(node, ast.Attribute):
                value = resolve(node)
                parent = resolve(node.value)
                if (
                    isinstance(parent, types.ModuleType)
                    and getattr(parent, "__name__", None) == __name__
                    and node.attr in globals()
                ):
                    global_names.add(node.attr)
                record(node.attr, value)
        # Closure values can be aliases that never appear as module globals.
        for value in environment.values():
            record(getattr(value, "__name__", "closure"), value)
    return reachable, global_names, semantic_ids, function_ids


def _independence_graph(root_names: Sequence[str]) -> tuple[set[str], set[str]]:
    functions, globals_found, _semantic, _function_ids = _independence_graph_detailed(root_names)
    return functions, globals_found


def oracle_checker_call_graph() -> dict[str, tuple[str, ...]]:
    oracle_functions, oracle_globals = _independence_graph(("reference_oracle",))
    checker_functions, checker_globals = _independence_graph(
        (
            "checker_validation",
            "validate_b0",
            "sanitize_payload",
            "_checker_schema_copy",
            "_checker_identity",
            "_checker_conservation",
            "_checker_ordered_replay",
            "_checker_revision",
            "_checker_overconstraint",
            "_checker_stale_replay",
        )
    )
    return {
        "oracle_functions": tuple(sorted(oracle_functions)),
        "checker_functions": tuple(sorted(checker_functions)),
        "oracle_globals": tuple(sorted(oracle_globals)),
        "checker_globals": tuple(sorted(checker_globals)),
    }


def _semantic_global_names(names: Iterable[str]) -> set[str]:
    excluded = {
        "Any",
        "Iterable",
        "Mapping",
        "Sequence",
        "Path",
        "Counter",
        "defaultdict",
        "MappingProxyType",
    }
    output: set[str] = set()
    for name in names:
        if name in excluded:
            continue
        value = globals().get(name)
        if isinstance(value, (types.ModuleType, type)):
            continue
        if getattr(value, "__module__", None) in {"typing", "builtins"}:
            continue
        if inspect.isfunction(value):
            continue
        output.add(name)
    return output


def assert_oracle_checker_independence() -> None:
    oracle_functions, oracle_globals, oracle_objects, oracle_function_ids = _independence_graph_detailed(
        ("reference_oracle",)
    )
    checker_functions, checker_globals, checker_objects, checker_function_ids = _independence_graph_detailed(
        (
            "checker_validation", "validate_b0", "sanitize_payload",
            "_checker_schema_copy", "_checker_identity", "_checker_conservation",
            "_checker_ordered_replay", "_checker_revision", "_checker_overconstraint",
            "_checker_stale_replay",
        )
    )
    if "reference_oracle" in checker_functions:
        raise ProtocolError("checker transitive call graph reaches reference oracle")
    if any(name.startswith(("validate_", "_checker")) for name in oracle_functions):
        raise ProtocolError("oracle transitive call graph reaches checker code")
    shared_functions = oracle_functions & checker_functions
    if shared_functions:
        raise ProtocolError(f"shared oracle/checker helper: {sorted(shared_functions)}")
    oracle_globals = _semantic_global_names(oracle_globals)
    checker_globals = _semantic_global_names(checker_globals)
    shared_globals = oracle_globals & checker_globals
    if shared_globals:
        raise ProtocolError(f"shared oracle/checker table/global: {sorted(shared_globals)}")
    if oracle_objects & checker_objects:
        raise ProtocolError("shared oracle/checker semantic object identity")
    if oracle_function_ids & checker_function_ids:
        raise ProtocolError("shared oracle/checker function identity")


def _runtime_sanity_check_impl(
    population: Population | Mapping[str, Sequence[Case]]
) -> dict[str, Any]:
    if isinstance(population, Population):
        cases = population.cases
        clusters = population.clusters
    else:
        cases = tuple(case for split in SPLITS for case in population[split])
        cluster_map: dict[str, list[Case]] = defaultdict(list)
        for case in cases:
            cluster_map[case.cluster_id].append(case)
        clusters = tuple(
            Cluster(
                split=group[0].split,
                cluster_type=group[0].cluster_type,
                local_index=group[0].local_index,
                cluster_index=group[0].cluster_index,
                cluster_id=group[0].cluster_id,
                structural_signature=TYPE_MANIFEST[group[0].cluster_type]["tuple"],
                signature_sha256=sha256_hex(_signature_input(group[0].cluster_type)),
                base_hash=group[0].base_hash,
                cases=tuple(group),
            )
            for group in cluster_map.values()
        )
    assert_oracle_checker_independence()
    if len(clusters) != 96 or len(cases) != 912:
        raise ProtocolError("population count drift")
    if (
        BOOTSTRAP_ESTIMATE != INDEPENDENT_BOOTSTRAP_ESTIMATE
        or INDEPENDENT_BOOTSTRAP_ESTIMATE != 47_710_564
    ):
        raise ProtocolError("bootstrap serializer estimate drift")
    if tuple(TYPE_ORDER) != INDEPENDENT_TYPE_ORDER:
        raise ProtocolError("type order drift")
    if tuple(RECIPE_ORDER) != INDEPENDENT_RECIPE_ORDER:
        raise ProtocolError("recipe order drift")
    for recipe_id, expected_sequence in INDEPENDENT_RECIPE_SEQUENCE.items():
        if recipe_id in MULTI_RECIPE:
            actual_sequence = tuple(MULTI_RECIPE[recipe_id])
        elif recipe_id in SINGLE_RECIPE:
            actual_sequence = (recipe_id,)
        else:
            actual_sequence = ()
        if actual_sequence != expected_sequence:
            raise ProtocolError("recipe operation sequence drift")
    for recipe_id, expected_operations in INDEPENDENT_RECIPE_OPERATION_MANIFEST.items():
        if recipe_id not in INDEPENDENT_RECIPE_SEQUENCE:
            if recipe_id not in {"Q0-missing", "Q0-extra", "Q0-bool"}:
                raise ProtocolError("independent recipe manifest incomplete")
            continue
        if recipe_id == "valid-base":
            continue
        if recipe_id in MULTI_RECIPE:
            producer_operations = tuple(
                operation
                for operation_name in MULTI_RECIPE[recipe_id]
                for operation in INDEPENDENT_RECIPE_OPERATION_MANIFEST.get(
                    operation_name, ()
                )
            )
        else:
            producer_operations = tuple(
                INDEPENDENT_RECIPE_OPERATION_MANIFEST.get(recipe_id, ())
            )
        if producer_operations != expected_operations:
            raise ProtocolError("recipe operation manifest drift")
    split_cases = {split: [case for case in cases if case.split == split] for split in SPLITS}
    split_clusters = {split: [cluster for cluster in clusters if cluster.split == split] for split in SPLITS}
    if {key: len(value) for key, value in split_cases.items()} != {
        "development": 228,
        "calibration": 228,
        "confirmatory": 456,
    }:
        raise ProtocolError("split case count drift")
    if {key: len(value) for key, value in split_clusters.items()} != {
        "development": 24,
        "calibration": 24,
        "confirmatory": 48,
    }:
        raise ProtocolError("split cluster count drift")
    for split in SPLITS:
        base_hashes = [cluster.base_hash for cluster in split_clusters[split]]
        cluster_ids = [cluster.cluster_id for cluster in split_clusters[split]]
        case_ids = [case.case_id for case in split_cases[split]]
        if len(set(base_hashes)) != len(base_hashes) or len(set(cluster_ids)) != len(cluster_ids) or len(set(case_ids)) != len(case_ids):
            raise ProtocolError("within-split uniqueness drift")
    for left_index, left_split in enumerate(SPLITS):
        for right_split in SPLITS[left_index + 1:]:
            for attribute in ("base_hash", "cluster_id", "case_id"):
                left_values = (
                    {cluster.base_hash for cluster in split_clusters[left_split]}
                    if attribute == "base_hash"
                    else {cluster.cluster_id for cluster in split_clusters[left_split]}
                    if attribute == "cluster_id"
                    else {case.case_id for case in split_cases[left_split]}
                )
                right_values = (
                    {cluster.base_hash for cluster in split_clusters[right_split]}
                    if attribute == "base_hash"
                    else {cluster.cluster_id for cluster in split_clusters[right_split]}
                    if attribute == "cluster_id"
                    else {case.case_id for case in split_cases[right_split]}
                )
                if left_values & right_values:
                    raise ProtocolError("pairwise leakage detected")
    expected_types = set(INDEPENDENT_TYPE_ORDER)
    if {cluster.cluster_type for cluster in clusters} != expected_types:
        raise ProtocolError("type label drift")
    for cluster in clusters:
        if cluster.cluster_type not in expected_types:
            raise ProtocolError("unknown type label")
        expected_tuple, expected_signature = INDEPENDENT_SIGNATURE_MANIFEST[cluster.cluster_type]
        expected_recipes = INDEPENDENT_RECIPE_MANIFEST[cluster.cluster_type]
        if (
            cluster.structural_signature != expected_tuple
            or cluster.signature_sha256 != expected_signature
            or len(cluster.cases) != expected_tuple[-1]
            or tuple(case.recipe_id for case in cluster.cases) != expected_recipes
            or tuple(case.recipe_id for case in cluster.cases) != _recipe_ids(cluster.cluster_type)
            or cluster.local_index != int(cluster.cluster_id[-2:])
        ):
            raise ProtocolError("type manifest drift")
        expected_cluster_index = INDEPENDENT_TYPE_ORDER.index(cluster.cluster_type) * 16 + cluster.local_index
        if cluster.cluster_index != expected_cluster_index:
            raise ProtocolError("cluster allocation drift")
        base_payload = generate_base_payload(cluster.cluster_index, cluster.cluster_type)
        independent_base_payload = independently_rebuild_base_payload(
            cluster.cluster_index, cluster.cluster_type
        )
        if base_payload != independent_base_payload:
            raise ProtocolError("independent base payload construction drift")
        if canonical_sha256(base_payload) != cluster.base_hash:
            raise ProtocolError("base hash drift")
        if independent_payload_traces(base_payload) != INDEPENDENT_TRACE_MANIFEST[cluster.cluster_type]:
            raise ProtocolError("independent trace manifest drift")
        if sha256_hex(_signature_input(cluster.cluster_type)) != expected_signature:
            raise ProtocolError("independent signature digest drift")
        expected_footprints = INDEPENDENT_FOOTPRINT_MANIFEST[cluster.cluster_type]
        expected_base_flags = reference_oracle(
            base_payload
        ).base_structure_flags
        for case in cluster.cases:
            if (
                case.case_id != f"{cluster.cluster_id}::{case.recipe_id}"
                or case.cluster_id != cluster.cluster_id
                or case.cluster_type != cluster.cluster_type
                or case.split != cluster.split
                or case.local_index != cluster.local_index
                or case.cluster_index != cluster.cluster_index
                or case.case_kind != INDEPENDENT_CASE_KIND_MANIFEST.get(case.recipe_id)
                or case.case_kind != _case_kind(case.recipe_id)
                or case.fault_set != INDEPENDENT_FAULT_MANIFEST.get(case.recipe_id)
                or case.fault_set != _intended_families(case.recipe_id)
                or case.base_hash != cluster.base_hash
                or case.base_structure_flags != expected_base_flags
                or case.footprint != expected_footprints.get(case.recipe_id)
            ):
                raise ProtocolError("case manifest identity drift")
            expected_payload = independently_apply_recipe(
                independent_base_payload, case.recipe_id
            )
            producer_payload, producer_footprint = _apply_recipe(
                base_payload, case.recipe_id
            )
            expected_footprint = expected_footprints[case.recipe_id]
            if (
                case.footprint != expected_footprint
                or case.payload != expected_payload
                or producer_payload != expected_payload
                or producer_footprint != expected_footprint
            ):
                raise ProtocolError("recipe footprint or payload drift")
            if case.input_sha256 != canonical_sha256(case.payload):
                raise ProtocolError("case input hash drift")
            oracle = reference_oracle(case.payload)
            if (
                oracle.truth != case.truth
                or oracle.failed_families != case.oracle_failure_set
                or oracle.schema_valid != case.schema_valid
            ):
                raise ProtocolError("oracle manifest drift")
            b0 = validate_b0(case.payload)
            if b0.decision != oracle.schema_valid:
                raise ProtocolError("runtime B0/schema mismatch")
            if case.case_kind == "valid" and oracle.truth != 1:
                raise ProtocolError("valid case rejected by reference oracle")
            if case.case_kind == "single":
                if oracle.truth != 0 or oracle.failed_families != INDEPENDENT_FAULT_MANIFEST[case.recipe_id]:
                    raise ProtocolError("single-fault oracle isolation drift")
            if case.case_kind == "multi" and oracle.truth != 0:
                raise ProtocolError("multi-fault case unexpectedly valid")
            if case.case_kind == "multi":
                expected_observed = INDEPENDENT_MULTI_OBSERVED_FAILURES[case.recipe_id]
                if oracle.failed_families != expected_observed:
                    raise ProtocolError("multi-fault oracle relation drift")
                intended = set(INDEPENDENT_FAULT_MANIFEST[case.recipe_id])
                observed = set(expected_observed)
                relation = (
                    "equals" if intended == observed
                    else "contains" if intended < observed
                    else "differs"
                )
                if relation != INDEPENDENT_MULTI_RELATION[case.recipe_id]:
                    raise ProtocolError("multi-fault relation classification drift")
    if len({cluster.structural_signature for cluster in clusters}) != 6:
        raise ProtocolError("non-type signature tuple collision")
    if len({cluster.signature_sha256 for cluster in clusters}) != 6:
        raise ProtocolError("signature digest collision")
    if len({len(cluster.cases) for cluster in clusters}) < 2:
        raise ProtocolError("case-count distinctness gate failed")
    confirmatory = split_clusters["confirmatory"]
    if any(
        sum(cluster.cluster_type == cluster_type for cluster in confirmatory) != 8
        for cluster_type in INDEPENDENT_TYPE_ORDER
    ):
        raise ProtocolError("confirmatory type allocation drift")
    if len({cluster.base_hash for cluster in confirmatory}) != len(confirmatory):
        raise ProtocolError("duplicate confirmatory base payload")
    # Exact locked vectors.
    if sha256_hex("E002-v1|amount|0|0") != "6211e62d437c6210a1c02e41c02c49f5dcce723a6ee0d69a6af036803cf629f4":
        raise ProtocolError("amount known-answer drift")
    if 200 + int.from_bytes(hashlib.sha256(b"E002-v1|amount|0|0").digest()[:8], "big") % 800 != 920:
        raise ProtocolError("amount known-answer value drift")
    if sha256_hex("H0-C00::valid-base") != "bc4c1aa9ecb37f29ec8f1acebb4040d61cca0bf3c3d2de061af53dd1d4876911":
        raise ProtocolError("case ID vector drift")
    if sha256_hex("H0-C00::R1") != "0a23225dd76b7860dcbbd24aa80e96666a8cde41a14700bb339c205a108ca6a5":
        raise ProtocolError("case ID vector drift")
    bootstrap_material = "E002-v1|bootstrap|overall|balanced_accuracy|0|0"
    bootstrap_digest = sha256_hex(bootstrap_material)
    if bootstrap_digest != "ec4fb50879c8319c8000ee52e5d68a1d4617e570c3874457ce9dbb1b727ee050":
        raise ProtocolError("bootstrap vector drift")
    if int.from_bytes(bytes.fromhex(bootstrap_digest)[:8], "big") % 48 != 28:
        raise ProtocolError("bootstrap index vector drift")
    h0 = next(case for case in cases if case.case_id == "H0-C00::valid-base")
    h5 = next(case for case in cases if case.case_id == "H5-C00::valid-base")
    if canonical_sha256(h0.payload) != "8ddb5fbd84a64ef811a261ad72359f647d0757e8c83c864bd206bbb03b8dd07b":
        raise ProtocolError("H0 payload vector drift")
    if canonical_sha256(h5.payload) != "97935beb48f281d1d1fe8317d8ee7f300089bd2e6ad523fc06aaaaf47d4c6db3":
        raise ProtocolError("H5 payload vector drift")
    if not validate_m1(h0.payload).decision or validate_m1_overconstraint(h0.payload).decision or not validate_m1_stale_transition(h0.payload).decision:
        raise ProtocolError("H0 separation probe drift")
    if not validate_m1(h5.payload).decision or not validate_m1_overconstraint(h5.payload).decision or validate_m1_stale_transition(h5.payload).decision:
        raise ProtocolError("H5 separation probe drift")
    return {
        "clusters": len(clusters),
        "cases": len(cases),
        "split_cases": {split: len(split_cases[split]) for split in SPLITS},
        "split_clusters": {split: len(split_clusters[split]) for split in SPLITS},
        "confirmatory_clusters_per_type": 8,
        "recipes_checked": len(cases),
        "runtime_b0_cases": len(cases),
        "signature_vectors": 6,
    }


def runtime_sanity_check(
    population: Population | Mapping[str, Sequence[Case]]
) -> dict[str, Any]:
    """Run the locked sanity gate and convert table faults to ProtocolError."""

    try:
        return _runtime_sanity_check_impl(population)
    except ProtocolError:
        raise
    except (KeyError, TypeError, AttributeError, IndexError, ValueError) as error:
        raise ProtocolError("runtime sanity generation/table failure") from error


@dataclass(frozen=True)
class CalibrationLookup:
    method: str
    entries: tuple[tuple[int, int, int, Fraction], ...]
    fallback: Fraction | None

    def lookup(self, raw_score: int) -> Fraction | None:
        for score, _positive, _count, probability in self.entries:
            if score == raw_score:
                return probability
        return self.fallback

    def score_list(self) -> tuple[int, ...]:
        return tuple(entry[0] for entry in self.entries)

    def summary(self, lookup_hash: str) -> str:
        if self.fallback is None:
            return "lookup=none;scores=none;p_valid=none"
        scores = ", ".join(str(score) for score in self.score_list())
        probabilities = ", ".join(d9(entry[3]) for entry in self.entries)
        return f"lookup={lookup_hash};scores={scores or 'none'};p_valid={probabilities or 'none'}"

    def manifest_rows(self) -> list[dict[str, Any]]:
        if self.fallback is None:
            return [
                {
                    "method": self.method,
                    "raw_score": 0,
                    "positive_count": 0,
                    "count": 0,
                    "p_valid": JsonNumber("0.000000000"),
                    "fallback": JsonNumber("0.000000000"),
                }
            ]
        fallback = JsonNumber(d9(self.fallback))
        return [
            {
                "method": self.method,
                "raw_score": score,
                "positive_count": positive,
                "count": count,
                "p_valid": JsonNumber(d9(probability)),
                "fallback": fallback,
            }
            for score, positive, count, probability in self.entries
        ]


@dataclass
class _Stats:
    support: int = 0
    positive_count: int = 0
    negative_count: int = 0
    tp: int = 0
    tn: int = 0
    fp: int = 0
    fn: int = 0
    brier_numerator: Fraction = Fraction(0)
    bin_counts: list[int] | None = None
    bin_probability_sums: list[Fraction] | None = None
    bin_truth_sums: list[int] | None = None

    def __post_init__(self) -> None:
        if self.bin_counts is None:
            self.bin_counts = [0] * 10
        if self.bin_probability_sums is None:
            self.bin_probability_sums = [Fraction(0)] * 10
        if self.bin_truth_sums is None:
            self.bin_truth_sums = [0] * 10

    def add(self, truth: int, decision: bool, probability: Fraction, multiplicity: int = 1) -> None:
        for _ in range(multiplicity):
            self.support += 1
            if truth:
                self.positive_count += 1
            else:
                self.negative_count += 1
            if truth and decision:
                self.tp += 1
            elif truth and not decision:
                self.fn += 1
            elif not truth and decision:
                self.fp += 1
            else:
                self.tn += 1
            self.brier_numerator += (probability - truth) ** 2
            bin_index = min(9, int(probability * 10))
            self.bin_counts[bin_index] += 1
            self.bin_probability_sums[bin_index] += probability
            self.bin_truth_sums[bin_index] += truth

    def merge(self, other: "_Stats", multiplicity: int = 1) -> None:
        self.support += other.support * multiplicity
        self.positive_count += other.positive_count * multiplicity
        self.negative_count += other.negative_count * multiplicity
        self.tp += other.tp * multiplicity
        self.tn += other.tn * multiplicity
        self.fp += other.fp * multiplicity
        self.fn += other.fn * multiplicity
        self.brier_numerator += other.brier_numerator * multiplicity
        for index in range(10):
            self.bin_counts[index] += other.bin_counts[index] * multiplicity
            self.bin_probability_sums[index] += other.bin_probability_sums[index] * multiplicity
            self.bin_truth_sums[index] += other.bin_truth_sums[index] * multiplicity


def _stats_from_predictions(
    cases: Iterable[Case],
    predictions: Mapping[tuple[str, str], Mapping[str, Any]],
    method: str,
) -> _Stats:
    stats = _Stats()
    for case in cases:
        row = predictions[(method, case.case_id)]
        stats.add(case.truth, bool(row["decision"]), row["p_valid"])
    return stats


def _metric_from_stats(stats: _Stats, metric: str) -> Fraction | None:
    if metric == "fpr":
        denominator = stats.tn + stats.fp
        return Fraction(stats.fp, denominator) if denominator else None
    if metric == "fnr":
        denominator = stats.tp + stats.fn
        return Fraction(stats.fn, denominator) if denominator else None
    if metric == "precision":
        denominator = stats.tp + stats.fp
        return Fraction(stats.tp, denominator) if denominator else None
    if metric == "recall":
        denominator = stats.tp + stats.fn
        return Fraction(stats.tp, denominator) if denominator else None
    if metric == "specificity":
        denominator = stats.tn + stats.fp
        return Fraction(stats.tn, denominator) if denominator else None
    if metric == "f1":
        denominator = 2 * stats.tp + stats.fp + stats.fn
        return Fraction(2 * stats.tp, denominator) if denominator else None
    if metric == "balanced_accuracy":
        recall = _metric_from_stats(stats, "recall")
        specificity = _metric_from_stats(stats, "specificity")
        return (recall + specificity) / 2 if recall is not None and specificity is not None else None
    if metric == "brier":
        return stats.brier_numerator / stats.support if stats.support else None
    if metric == "ece":
        if not stats.support:
            return None
        total = Fraction(0)
        for count, probability_sum, truth_sum in zip(
            stats.bin_counts, stats.bin_probability_sums, stats.bin_truth_sums
        ):
            if count:
                total += Fraction(count, stats.support) * abs(
                    probability_sum / count - Fraction(truth_sum, count)
                )
        return total
    raise ProtocolError(f"unknown metric {metric}")


def _metric_denominators(stats: _Stats) -> dict[str, int]:
    return {
        "fpr": stats.tn + stats.fp,
        "fnr": stats.tp + stats.fn,
        "precision": stats.tp + stats.fp,
        "recall": stats.tp + stats.fn,
        "specificity": stats.tn + stats.fp,
        "f1": 2 * stats.tp + stats.fp + stats.fn,
        "balanced_accuracy": int(bool(stats.tp + stats.fn and stats.tn + stats.fp)),
        "brier": stats.support,
        "ece": stats.support,
    }


def _subgroup_cases(cases: Iterable[Case], subgroup: str) -> list[Case]:
    if subgroup == "overall":
        return list(cases)
    if subgroup.startswith("cluster:"):
        return [case for case in cases if case.cluster_type == subgroup.split(":", 1)[1]]
    if subgroup.startswith("case_kind:"):
        return [case for case in cases if case.case_kind == subgroup.split(":", 1)[1]]
    raise ProtocolError(f"unknown subgroup {subgroup}")


def _prediction_for_case(
    case: Case,
    method: str,
    lookup: CalibrationLookup,
    calibration_hash: str,
    oracle_hash: str,
) -> dict[str, Any]:
    result = checker_validation(case.payload, method)
    if method == "M1-no-calibration":
        probability = Fraction(int(result.decision), 1)
    else:
        probability = lookup.lookup(result.raw_score)
        if probability is None:
            raise ProtocolError("calibration lookup missing for calibrated method")
    return {
        "run_id": "",
        "protocol_path": PROTOCOL_PATH,
        "protocol_commit": PROTOCOL_COMMIT,
        "method": method,
        "split": case.split,
        "cluster_id": case.cluster_id,
        "cluster_type": case.cluster_type,
        "cluster_signature_sha256": sha256_hex(_signature_input(case.cluster_type)),
        "case_id": case.case_id,
        "case_kind": case.case_kind,
        "recipe_id": case.recipe_id,
        "fault_set": list(case.fault_set),
        "oracle_failure_set": list(case.oracle_failure_set),
        "base_structure_flags": list(case.base_structure_flags),
        "truth": case.truth,
        "decision": bool(result.decision),
        "raw_score": result.raw_score,
        "p_valid": probability,
        "input_sha256": case.input_sha256,
        "oracle_manifest_sha256": oracle_hash,
        "calibration_lookup_sha256": _lookup_hash(lookup),
        "status": "valid",
    }


def _score_cases(cases: Sequence[Case], method: str) -> dict[str, ValidationResult]:
    return {case.case_id: checker_validation(case.payload, method) for case in cases}


def _calibrate(
    cases: Sequence[Case],
    score_table: Mapping[str, Mapping[str, ValidationResult]],
) -> tuple[CalibrationLookup, ...]:
    lookups: list[CalibrationLookup] = []
    for method in METHODS:
        if method == "M1-no-calibration":
            lookups.append(CalibrationLookup(method, (), None))
            continue
        counts: Counter[int] = Counter()
        positives: Counter[int] = Counter()
        for case in cases:
            score = score_table[method][case.case_id].raw_score
            counts[score] += 1
            positives[score] += case.truth
        total = sum(counts.values())
        positive_total = sum(positives.values())
        fallback = Fraction(positive_total + 1, total + 2)
        entries = tuple(
            (
                score,
                positives[score],
                counts[score],
                Fraction(positives[score] + 1, counts[score] + 2),
            )
            for score in sorted(counts)
        )
        lookups.append(CalibrationLookup(method, entries, fallback))
    return tuple(lookups)


def calibration_manifest(lookups: Sequence[CalibrationLookup]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for method in METHODS:
        lookup = next(item for item in lookups if item.method == method)
        rows.extend(lookup.manifest_rows())
    return {"protocol_id": PROTOCOL_VERSION, "methods": rows}


def population_manifest(population: Population) -> dict[str, Any]:
    clusters = []
    for cluster in sorted(
        population.clusters,
        key=lambda item: (
            SPLIT_RANK[item.split],
            TYPE_ORDER.index(item.cluster_type),
            item.local_index,
        ),
    ):
        clusters.append(
            {
                "cluster_id": cluster.cluster_id,
                "cluster_type": cluster.cluster_type,
                "split": cluster.split,
                "structural_signature": list(cluster.structural_signature),
                "signature_sha256": cluster.signature_sha256,
                "base_hash": cluster.base_hash,
                "cases": [
                    {
                        "case_id": case.case_id,
                        "case_kind": case.case_kind,
                        "recipe_id": case.recipe_id,
                        "fault_set": list(case.fault_set),
                        "footprint": list(case.footprint),
                        "input_sha256": case.input_sha256,
                        "base_structure_flags": list(case.base_structure_flags),
                    }
                    for case in cluster.cases
                ],
            }
        )
    return {"protocol_id": PROTOCOL_VERSION, "clusters": clusters}


def oracle_manifest(population: Population) -> dict[str, Any]:
    ordered_cases = sorted(
        population.cases,
        key=lambda case: (
            SPLIT_RANK[case.split],
            TYPE_ORDER.index(case.cluster_type),
            case.local_index,
            RECIPE_RANK[case.recipe_id],
        ),
    )
    return {
        "protocol_id": PROTOCOL_VERSION,
        "cases": [
            {
                "case_id": case.case_id,
                "schema_valid": case.schema_valid,
                "truth": case.truth,
                "oracle_failure_set": list(case.oracle_failure_set),
                "base_structure_flags": list(case.base_structure_flags),
            }
            for case in ordered_cases
        ],
    }


def multi_fault_relation_evidence(
    population: Population,
) -> tuple[tuple[dict[str, Any], ...], dict[str, int], bytes, str]:
    """Build deterministic external-only multi-fault relation evidence."""

    rows: list[dict[str, Any]] = []
    for case in sorted(
        (item for item in population.cases if item.case_kind == "multi"),
        key=lambda item: item.case_id.encode("utf-8"),
    ):
        intended = tuple(INDEPENDENT_FAULT_MANIFEST[case.recipe_id])
        observed = tuple(reference_oracle(case.payload).failed_families)
        if observed != INDEPENDENT_MULTI_OBSERVED_FAILURES[case.recipe_id]:
            raise ProtocolError("multi-fault external oracle vector drift")
        intended_set = set(intended)
        observed_set = set(observed)
        relation = INDEPENDENT_MULTI_RELATION[case.recipe_id]
        expected_relation = (
            "equals" if intended_set == observed_set
            else "contains" if intended_set < observed_set
            else "differs"
        )
        if relation != expected_relation:
            raise ProtocolError("multi-fault external relation vector drift")
        rows.append(
            {
                "case_id": case.case_id,
                "intended_fault_set": list(intended),
                "observed_oracle_failure_set": list(observed),
                "relation": relation,
            }
        )
    counts = {
        "equals": sum(row["relation"] == "equals" for row in rows),
        "contains": sum(row["relation"] == "contains" for row in rows),
        "differs": sum(row["relation"] == "differs" for row in rows),
    }
    evidence = {"protocol_id": PROTOCOL_VERSION, "rows": rows}
    evidence_bytes = canonical_json_bytes(evidence)
    return tuple(rows), counts, evidence_bytes, sha256_hex(evidence_bytes)


def raw_prediction_manifest(predictions: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    ordered = sorted(
        predictions,
        key=lambda row: (
            SPLIT_RANK[row["split"]],
            TYPE_ORDER.index(row["cluster_type"]),
            int(row["cluster_id"][-2:]),
            RECIPE_RANK[row["recipe_id"]],
            METHOD_RANK[row["method"]],
        ),
    )
    return {
        "protocol_id": PROTOCOL_VERSION,
        "rows": [
            {
                "split": row["split"],
                "case_id": row["case_id"],
                "method": row["method"],
                "raw_score": row["raw_score"],
                "decision": row["decision"],
                "input_sha256": row["input_sha256"],
            }
            for row in ordered
        ],
    }


def _bootstrap_index(
    subgroup: str, metric: str, replicate: int, position: int, count: int
) -> int:
    material = f"{PROTOCOL_VERSION}|bootstrap|{subgroup}|{metric}|{replicate}|{position}"
    digest = hashlib.sha256(material.encode()).digest()
    return int.from_bytes(digest[:8], "big") % count


def _diagnostic_cases(case: Case, diagnostic: str) -> bool:
    if diagnostic == "d1":
        return case.truth == 0 and case.schema_valid and "conservation" in case.oracle_failure_set
    if diagnostic == "d2":
        return case.truth == 1 and case.case_kind == "valid" and "active-active" in case.base_structure_flags
    if diagnostic == "d3":
        return case.truth == 1 and case.case_kind == "valid" and "pending-closed" in case.base_structure_flags
    raise ProtocolError(f"unknown diagnostic {diagnostic}")


def diagnostic_eligibility(population: Population) -> dict[str, tuple[str, ...]]:
    confirmatory = [case for case in population.cases if case.split == "confirmatory"]
    output: dict[str, tuple[str, ...]] = {}
    for diagnostic in DIAGNOSTICS:
        selected = [case for case in confirmatory if _diagnostic_cases(case, diagnostic)]
        clusters = tuple(_utf8_sorted({case.cluster_id for case in selected}))
        if not clusters or any(not any(case.cluster_id == cluster_id for case in selected) for cluster_id in clusters):
            raise ProtocolError(f"{diagnostic} has an empty eligible cluster")
        if not all(any(case.cluster_id == cluster_id for case in selected) for cluster_id in clusters):
            raise ProtocolError(f"{diagnostic} cluster denominator drift")
        output[diagnostic] = clusters
    if any(
        output[diagnostic] != INDEPENDENT_DIAGNOSTIC_CLUSTER_IDS[diagnostic]
        for diagnostic in DIAGNOSTICS
    ):
        raise ProtocolError("diagnostic eligibility drift")
    return output


@dataclass(frozen=True)
class BootstrapResult:
    rows: tuple[dict[str, str], ...]
    intervals: Mapping[tuple[str, str, str], dict[str, str]]
    block_count: int
    replicate_count: int


def _nearest_rank_interval(values: Sequence[Fraction], replicate_count: int) -> tuple[str, str, str, int]:
    usable = sorted(values)
    count = len(usable)
    if count == 0:
        return NA, NA, "undefined", 0
    lower_index = max(0, min(count - 1, math.ceil(0.025 * count) - 1))
    upper_index = max(0, min(count - 1, math.ceil(0.975 * count) - 1))
    status = "valid" if count == replicate_count == REPLICATES else "partial"
    return d9(usable[lower_index]), d9(usable[upper_index]), status, count


def _block_stats(
    cluster: Cluster,
    cases: Sequence[Case],
    predictions: Mapping[tuple[str, str], Mapping[str, Any]],
    method: str,
    predicate: Any,
) -> _Stats:
    return _stats_from_predictions(
        (case for case in cases if case.cluster_id == cluster.cluster_id and predicate(case)),
        predictions,
        method,
    )


def _bootstrap_block(
    block_subgroup: str,
    block_metric: str,
    method_a: str,
    method_b: str,
    eligible_clusters: Sequence[Cluster],
    all_cases: Sequence[Case],
    predictions: Mapping[tuple[str, str], Mapping[str, Any]],
    predicate: Any,
    replicate_count: int,
    diagnostic_id: str | None = None,
) -> tuple[list[dict[str, str]], dict[str, str]]:
    ordered_clusters = sorted(eligible_clusters, key=lambda item: item.cluster_id.encode("utf-8"))
    stats_a = {
        cluster.cluster_id: _block_stats(cluster, all_cases, predictions, method_a, predicate)
        for cluster in ordered_clusters
    }
    stats_b = {
        cluster.cluster_id: _block_stats(cluster, all_cases, predictions, method_b, predicate)
        for cluster in ordered_clusters
    }
    values: list[Fraction] = []
    replicate_rows: list[dict[str, str]] = []
    for replicate in range(replicate_count):
        aggregate_a = _Stats()
        aggregate_b = _Stats()
        for position in range(len(ordered_clusters)):
            if diagnostic_id is None:
                selected_index = _bootstrap_index(
                    block_subgroup, block_metric, replicate, position, len(ordered_clusters)
                )
            else:
                material = (
                    f"{PROTOCOL_VERSION}|bootstrap|diagnostic|{diagnostic_id}"
                    f"|{replicate}|{position}"
                )
                digest = hashlib.sha256(material.encode()).digest()
                selected_index = int.from_bytes(digest[:8], "big") % len(ordered_clusters)
            cluster_id = ordered_clusters[selected_index].cluster_id
            aggregate_a.merge(stats_a[cluster_id])
            aggregate_b.merge(stats_b[cluster_id])
        value_a = _metric_from_stats(aggregate_a, block_metric)
        value_b = _metric_from_stats(aggregate_b, block_metric)
        delta = value_a - value_b if value_a is not None and value_b is not None else None
        if delta is not None:
            values.append(delta)
        replicate_rows.append(
            {
                "row_type": "replicate",
                "replicate": str(replicate),
                "subgroup_code": (
                    SUBGROUP_CODE[block_subgroup]
                    if diagnostic_id is None
                    else diagnostic_id
                ),
                "metric_code": METRIC_CODE[block_metric],
                "method_pair_key": (
                    "m1-b0" if diagnostic_id is None else DIAGNOSTIC_PAIR_CODE[diagnostic_id]
                ),
                "delta": d9(delta),
                "ci_lower": NA,
                "ci_upper": NA,
                "usable_replicates": "0",
                "status": "usable" if delta is not None else "undefined",
            }
        )
    lower, upper, status, usable = _nearest_rank_interval(values, replicate_count)
    for row in replicate_rows:
        row["usable_replicates"] = str(usable)
    interval_row = {
        "row_type": "interval",
        "replicate": NA,
        "subgroup_code": SUBGROUP_CODE[block_subgroup] if diagnostic_id is None else diagnostic_id,
        "metric_code": METRIC_CODE[block_metric],
        "method_pair_key": "m1-b0" if diagnostic_id is None else DIAGNOSTIC_PAIR_CODE[diagnostic_id],
        "delta": NA,
        "ci_lower": lower,
        "ci_upper": upper,
        "usable_replicates": str(usable),
        "status": status,
    }
    key = (
        block_subgroup if diagnostic_id is None else f"diagnostic:{diagnostic_id}",
        block_metric,
        "M1-B0" if diagnostic_id is None else DIAGNOSTIC_PAIR_CODE[diagnostic_id],
    )
    return replicate_rows + [interval_row], {
        "ci_lower": lower,
        "ci_upper": upper,
        "usable_replicates": str(usable),
        "status": status,
        "key": "|".join(
            (
                "primary" if diagnostic_id is None else "stress",
                block_subgroup if diagnostic_id is None else diagnostic_id,
                block_metric,
                "M1-B0" if diagnostic_id is None else (
                    "omit-M1" if diagnostic_id == "d1" else "over-M1" if diagnostic_id == "d2" else "stale-M1"
                ),
            )
        ),
        "_lookup": key,
    }


def run_bootstrap(
    population: Population,
    predictions: Mapping[tuple[str, str], Mapping[str, Any]],
    *,
    replicate_count: int = REPLICATES,
    bootstrap_splits: Sequence[str] | None = None,
    include_diagnostics: bool | None = None,
) -> BootstrapResult:
    if replicate_count <= 0 or replicate_count > REPLICATES:
        raise ProtocolError("invalid bootstrap replicate count")
    selected_splits = tuple(bootstrap_splits or ("confirmatory",))
    if not selected_splits or any(split not in SPLITS for split in selected_splits):
        raise ProtocolError("invalid bootstrap split selection")
    if len(set(selected_splits)) != len(selected_splits):
        raise ProtocolError("duplicate bootstrap split selection")
    if include_diagnostics is None:
        include_diagnostics = selected_splits == ("confirmatory",)
    if include_diagnostics and selected_splits != ("confirmatory",):
        raise ProtocolError("diagnostics require the confirmatory split")
    selected_split_set = set(selected_splits)
    eligible_clusters = [
        cluster for cluster in population.clusters if cluster.split in selected_split_set
    ]
    diagnostics = diagnostic_eligibility(population) if include_diagnostics else {}
    all_cases = tuple(
        case for case in population.cases if case.split in selected_split_set
    )
    rows: list[dict[str, str]] = []
    intervals: dict[tuple[str, str, str], dict[str, str]] = {}
    for subgroup in SUBGROUPS:
        if subgroup.startswith("cluster:"):
            eligible = [
                cluster
                for cluster in eligible_clusters
                if cluster.cluster_type == subgroup.split(":", 1)[1]
            ]
        else:
            eligible = eligible_clusters
        predicate = lambda case, subgroup=subgroup: (
            subgroup == "overall"
            or (subgroup.startswith("cluster:") and case.cluster_type == subgroup.split(":", 1)[1])
            or (subgroup.startswith("case_kind:") and case.case_kind == subgroup.split(":", 1)[1])
        )
        for metric in METRICS:
            block_rows, interval = _bootstrap_block(
                subgroup,
                metric,
                "M1",
                "B0",
                eligible,
                all_cases,
                predictions,
                predicate,
                replicate_count,
            )
            rows.extend(block_rows)
            intervals[(subgroup, metric, "M1-B0")] = interval
    for diagnostic in DIAGNOSTICS if include_diagnostics else ():
        eligible = [
            cluster for cluster in eligible_clusters if cluster.cluster_id in diagnostics[diagnostic]
        ]
        predicate = lambda case, diagnostic=diagnostic: _diagnostic_cases(case, diagnostic)
        method_a, method_b = DIAGNOSTIC_PAIR[diagnostic]
        block_rows, interval = _bootstrap_block(
            diagnostic,
            DIAGNOSTIC_METRIC[diagnostic],
            method_a,
            method_b,
            eligible,
            all_cases,
            predictions,
            predicate,
            replicate_count,
            diagnostic,
        )
        rows.extend(block_rows)
        intervals[(f"diagnostic:{diagnostic}", DIAGNOSTIC_METRIC[diagnostic], DIAGNOSTIC_PAIR_CODE[diagnostic])] = interval
    expected_blocks = len(SUBGROUPS) * len(METRICS) + (
        len(DIAGNOSTICS) if include_diagnostics else 0
    )
    if len(intervals) != expected_blocks:
        raise ProtocolError("bootstrap block count drift")
    return BootstrapResult(tuple(rows), intervals, expected_blocks, replicate_count)


PREDICTION_FIELDS = (
    "run_id",
    "protocol_path",
    "protocol_commit",
    "method",
    "split",
    "cluster_id",
    "cluster_type",
    "cluster_signature_sha256",
    "case_id",
    "case_kind",
    "recipe_id",
    "fault_set",
    "oracle_failure_set",
    "base_structure_flags",
    "truth",
    "decision",
    "raw_score",
    "p_valid",
    "input_sha256",
    "oracle_manifest_sha256",
    "calibration_lookup_sha256",
    "status",
)
METRIC_FIELDS = (
    "row_kind",
    "run_id",
    "protocol_path",
    "protocol_commit",
    "split",
    "subgroup",
    "method",
    "method_pair",
    "diagnostic_id",
    "calibration_lookup_sha256",
    "support",
    "positive_count",
    "negative_count",
    "tp",
    "tn",
    "fp",
    "fn",
    "fpr_denominator",
    "fnr_denominator",
    "precision_denominator",
    "recall_denominator",
    "specificity_denominator",
    "f1_denominator",
    "ece_denominator",
    "balanced_accuracy",
    "fpr",
    "fnr",
    "precision",
    "recall",
    "specificity",
    "f1",
    "brier",
    "ece",
    "paired_interval_ref",
    "delta_ba_ci_lower",
    "delta_ba_ci_upper",
    "delta_fpr_ci_lower",
    "delta_fpr_ci_upper",
    "delta_fnr_ci_lower",
    "delta_fnr_ci_upper",
    "delta_brier_ci_lower",
    "delta_brier_ci_upper",
    "delta_ece_ci_lower",
    "delta_ece_ci_upper",
    "interval_status",
    "diagnostic_metric",
    "diagnostic_support",
    "diagnostic_positive_count",
    "diagnostic_negative_count",
    "diagnostic_denominator",
    "diagnostic_method_a_error_count",
    "diagnostic_method_b_error_count",
    "diagnostic_delta",
    "diagnostic_interval_ref",
    "diagnostic_ci_lower",
    "diagnostic_ci_upper",
)
BOOTSTRAP_FIELDS = (
    "row_type",
    "replicate",
    "subgroup_code",
    "metric_code",
    "method_pair_key",
    "delta",
    "ci_lower",
    "ci_upper",
    "usable_replicates",
    "status",
)


def _metric_row_values(stats: _Stats) -> dict[str, str]:
    values = {
        metric: d9(_metric_from_stats(stats, metric)) for metric in REPORT_METRICS
    }
    denominators = _metric_denominators(stats)
    return {
        "support": str(stats.support),
        "positive_count": str(stats.positive_count),
        "negative_count": str(stats.negative_count),
        "tp": str(stats.tp),
        "tn": str(stats.tn),
        "fp": str(stats.fp),
        "fn": str(stats.fn),
        "fpr_denominator": str(denominators["fpr"]),
        "fnr_denominator": str(denominators["fnr"]),
        "precision_denominator": str(denominators["precision"]),
        "recall_denominator": str(denominators["recall"]),
        "specificity_denominator": str(denominators["specificity"]),
        "f1_denominator": str(denominators["f1"]),
        "ece_denominator": str(denominators["ece"]),
        "balanced_accuracy": values["balanced_accuracy"],
        "fpr": values["fpr"],
        "fnr": values["fnr"],
        "precision": values["precision"],
        "recall": values["recall"],
        "specificity": values["specificity"],
        "f1": values["f1"],
        "brier": values["brier"],
        "ece": values["ece"],
    }


def _interval_ref(subgroup: str, metric: str) -> str:
    return f"primary|{subgroup}|{metric}|M1-B0"


def _metric_row(
    run_id: str,
    split: str,
    subgroup: str,
    method: str,
    cases: Sequence[Case],
    predictions: Mapping[tuple[str, str], Mapping[str, Any]],
    calibration_hash: str,
    bootstrap: BootstrapResult,
) -> dict[str, str]:
    stats = _stats_from_predictions(cases, predictions, method)
    row = {field: NA for field in METRIC_FIELDS}
    row.update(
        {
            "row_kind": "method",
            "run_id": run_id,
            "protocol_path": PROTOCOL_PATH,
            "protocol_commit": PROTOCOL_COMMIT,
            "split": split,
            "subgroup": subgroup,
            "method": method,
            "method_pair": NA,
            "diagnostic_id": NA,
            "calibration_lookup_sha256": calibration_hash,
            "interval_status": "descriptive-only",
        }
    )
    row.update(_metric_row_values(stats))
    if split == "confirmatory" and method in PRIMARY_METHODS:
        statuses = []
        interval_refs = []
        for metric in METRICS:
            interval = bootstrap.intervals[(subgroup, metric, "M1-B0")]
            statuses.append(interval["status"])
            interval_refs.append(_interval_ref(subgroup, metric))
            row[f"delta_{metric if metric != 'balanced_accuracy' else 'ba'}_ci_lower"] = interval["ci_lower"]
            row[f"delta_{metric if metric != 'balanced_accuracy' else 'ba'}_ci_upper"] = interval["ci_upper"]
        row["paired_interval_ref"] = ";".join(interval_refs)
        row["interval_status"] = (
            "undefined" if "undefined" in statuses else "partial" if "partial" in statuses else "valid"
        )
    return row


def _diagnostic_row(
    run_id: str,
    diagnostic: str,
    cases: Sequence[Case],
    predictions: Mapping[tuple[str, str], Mapping[str, Any]],
    calibration_hash: str,
    bootstrap: BootstrapResult,
) -> dict[str, str]:
    method_a, method_b = DIAGNOSTIC_PAIR[diagnostic]
    subset = [case for case in cases if _diagnostic_cases(case, diagnostic)]
    stats_a = _stats_from_predictions(subset, predictions, method_a)
    stats_b = _stats_from_predictions(subset, predictions, method_b)
    metric = DIAGNOSTIC_METRIC[diagnostic]
    value_a = _metric_from_stats(stats_a, metric)
    value_b = _metric_from_stats(stats_b, metric)
    if value_a is None or value_b is None:
        raise ProtocolError(f"{diagnostic} has undefined point denominator")
    interval = bootstrap.intervals[(
        f"diagnostic:{diagnostic}",
        metric,
        DIAGNOSTIC_PAIR_CODE[diagnostic],
    )]
    denominator = (
        stats_a.tn + stats_a.fp if metric == "fpr" else stats_a.tp + stats_a.fn
    )
    error_a = stats_a.fp if metric == "fpr" else stats_a.fn
    error_b = stats_b.fp if metric == "fpr" else stats_b.fn
    row = {field: NA for field in METRIC_FIELDS}
    row.update(
        {
            "row_kind": "diagnostic",
            "run_id": run_id,
            "protocol_path": PROTOCOL_PATH,
            "protocol_commit": PROTOCOL_COMMIT,
            "split": "confirmatory",
            "subgroup": f"diagnostic:{diagnostic}",
            "method": NA,
            "method_pair": (
                "omit-M1" if diagnostic == "d1" else "over-M1" if diagnostic == "d2" else "stale-M1"
            ),
            "diagnostic_id": diagnostic,
            "calibration_lookup_sha256": NA,
            "interval_status": interval["status"],
            "diagnostic_metric": metric,
            "diagnostic_support": str(len(subset)),
            "diagnostic_positive_count": str(sum(case.truth for case in subset)),
            "diagnostic_negative_count": str(sum(1 - case.truth for case in subset)),
            "diagnostic_denominator": str(denominator),
            "diagnostic_method_a_error_count": str(error_a),
            "diagnostic_method_b_error_count": str(error_b),
            "diagnostic_delta": d9(value_a - value_b),
            "diagnostic_interval_ref": (
                f"stress|{diagnostic}|{metric}|"
                f"{'omit-M1' if diagnostic == 'd1' else 'over-M1' if diagnostic == 'd2' else 'stale-M1'}"
            ),
            "diagnostic_ci_lower": interval["ci_lower"],
            "diagnostic_ci_upper": interval["ci_upper"],
        }
    )
    return row


def build_metric_rows(
    run_id: str,
    population: Population,
    predictions: Mapping[tuple[str, str], Mapping[str, Any]],
    calibration_hash: str | Mapping[str, str],
    bootstrap: BootstrapResult,
    *,
    splits: Sequence[str] = SPLITS,
    include_diagnostics: bool | None = None,
) -> tuple[dict[str, str], ...]:
    selected_splits = tuple(splits)
    if not selected_splits or any(split not in SPLITS for split in selected_splits):
        raise ProtocolError("invalid metric split selection")
    if len(set(selected_splits)) != len(selected_splits):
        raise ProtocolError("duplicate metric split selection")
    if include_diagnostics is None:
        include_diagnostics = selected_splits == SPLITS
    if include_diagnostics and "confirmatory" not in selected_splits:
        raise ProtocolError("diagnostics require confirmatory metric rows")
    rows: list[dict[str, str]] = []
    for split in selected_splits:
        split_cases = [case for case in population.cases if case.split == split]
        for subgroup in SUBGROUPS:
            subgroup_cases = _subgroup_cases(split_cases, subgroup)
            for method in METHODS:
                rows.append(
                    _metric_row(
                        run_id,
                        split,
                        subgroup,
                        method,
                        subgroup_cases,
                        predictions,
                        (
                            calibration_hash[method]
                            if isinstance(calibration_hash, Mapping)
                            else calibration_hash
                        ),
                        bootstrap,
                    )
                )
    if include_diagnostics:
        confirmatory_cases = [
            case for case in population.cases if case.split == "confirmatory"
        ]
        rows.extend(
            _diagnostic_row(
                run_id,
                diagnostic,
                confirmatory_cases,
                predictions,
                calibration_hash,
                bootstrap,
            )
            for diagnostic in DIAGNOSTICS
        )
    expected_rows = len(selected_splits) * len(SUBGROUPS) * len(METHODS) + (
        len(DIAGNOSTICS) if include_diagnostics else 0
    )
    if len(rows) != expected_rows:
        raise ProtocolError(f"metric row count drift: {len(rows)}")
    return tuple(rows)


def _csv_bytes(rows: Sequence[Mapping[str, Any]], fields: Sequence[str]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=list(fields),
        delimiter=",",
        quotechar='"',
        doublequote=True,
        lineterminator="\n",
        quoting=csv.QUOTE_MINIMAL,
        extrasaction="raise",
    )
    writer.writeheader()
    for row in rows:
        writer.writerow({field: str(row[field]) for field in fields})
    text = output.getvalue()
    if not text.endswith("\n") or text.endswith("\n\n") or "\r" in text:
        raise ProtocolError("CSV newline contract failed")
    if any(line.endswith((" ", "\t")) for line in text.splitlines()):
        raise ProtocolError("CSV trailing whitespace contract failed")
    return text.encode("utf-8")


def _prediction_json_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "run_id": row["run_id"],
        "protocol_path": row["protocol_path"],
        "protocol_commit": row["protocol_commit"],
        "method": row["method"],
        "split": row["split"],
        "cluster_id": row["cluster_id"],
        "cluster_type": row["cluster_type"],
        "cluster_signature_sha256": row["cluster_signature_sha256"],
        "case_id": row["case_id"],
        "case_kind": row["case_kind"],
        "recipe_id": row["recipe_id"],
        "fault_set": row["fault_set"],
        "oracle_failure_set": row["oracle_failure_set"],
        "base_structure_flags": row["base_structure_flags"],
        "truth": row["truth"],
        "decision": row["decision"],
        "raw_score": row["raw_score"],
        "p_valid": json_number(row["p_valid"]),
        "input_sha256": row["input_sha256"],
        "oracle_manifest_sha256": row["oracle_manifest_sha256"],
        "calibration_lookup_sha256": row["calibration_lookup_sha256"],
        "status": row["status"],
    }


def serialize_predictions(predictions: Sequence[Mapping[str, Any]]) -> bytes:
    ordered = sorted(
        predictions,
        key=lambda row: (
            SPLIT_RANK[row["split"]],
            TYPE_ORDER.index(row["cluster_type"]),
            int(row["cluster_id"][-2:]),
            RECIPE_RANK[row["recipe_id"]],
            METHOD_RANK[row["method"]],
        ),
    )
    return b"".join(
        canonical_json_bytes(_prediction_json_row(row)) + b"\n" for row in ordered
    )


def serialize_metrics(rows: Sequence[Mapping[str, Any]]) -> bytes:
    return _csv_bytes(rows, METRIC_FIELDS)


def serialize_bootstrap(rows: Sequence[Mapping[str, Any]]) -> bytes:
    return _csv_bytes(rows, BOOTSTRAP_FIELDS)


def _method_score_table(
    cases: Sequence[Case],
) -> dict[str, dict[str, ValidationResult]]:
    return {method: _score_cases(cases, method) for method in METHODS}


def build_predictions(
    run_id: str,
    population: Population,
    calibration_cases: Sequence[Case],
    *,
    scoring_cases: Sequence[Case] | None = None,
) -> tuple[
    tuple[CalibrationLookup, ...],
    dict[str, Any],
    str,
    tuple[dict[str, Any], ...],
    dict[tuple[str, str], dict[str, Any]],
]:
    all_cases = tuple(scoring_cases) if scoring_cases is not None else population.cases
    population_case_ids = {case.case_id for case in population.cases}
    if any(case.case_id not in population_case_ids for case in all_cases):
        raise ProtocolError("scoring case is outside population")
    if not all_cases:
        raise ProtocolError("empty scoring case selection")
    calibration_ids = {case.case_id for case in calibration_cases}
    if not calibration_ids.issubset(population_case_ids):
        raise ProtocolError("calibration case is outside population")
    expected_calibration_ids = {
        f"{cluster_type}-C{local_index:02d}::{recipe_id}"
        for cluster_type in INDEPENDENT_TYPE_ORDER
        for local_index in range(4, 8)
        for recipe_id in INDEPENDENT_RECIPE_MANIFEST[cluster_type]
    }
    if (
        len(calibration_cases) != 228
        or len(calibration_ids) != 228
        or calibration_ids != expected_calibration_ids
        or any(case.split != "calibration" for case in calibration_cases)
        or any(case.split == "confirmatory" for case in calibration_cases)
    ):
        raise ProtocolError("calibration inventory or split drift")
    calibration_scores = {
        method: _score_cases(calibration_cases, method) for method in METHODS
    }
    lookups = _calibrate(calibration_cases, calibration_scores)
    score_table = _method_score_table(all_cases)
    calibration_object = calibration_manifest(lookups)
    calibration_hash = canonical_sha256(calibration_object)
    oracle_object = oracle_manifest(population)
    oracle_hash = canonical_sha256(oracle_object)
    rows: list[dict[str, Any]] = []
    mapping: dict[tuple[str, str], dict[str, Any]] = {}
    for case in all_cases:
        for method in METHODS:
            lookup = next(item for item in lookups if item.method == method)
            row = _prediction_for_case(
                case, method, lookup, calibration_hash, oracle_hash
            )
            row["run_id"] = run_id
            rows.append(row)
            mapping[(method, case.case_id)] = row
    if len(rows) != len(all_cases) * len(METHODS):
        raise ProtocolError("prediction row count drift")
    return lookups, calibration_object, calibration_hash, tuple(rows), mapping


def _point_metric(
    cases: Sequence[Case],
    predictions: Mapping[tuple[str, str], Mapping[str, Any]],
    method: str,
    metric: str,
) -> Fraction | None:
    return _metric_from_stats(
        _stats_from_predictions(cases, predictions, method), metric
    )


def _interval_ref(subgroup: str, metric: str) -> str:
    return f"primary|{subgroup}|{metric}|M1-B0"


def _h2_summary(
    population: Population,
    predictions: Mapping[tuple[str, str], Mapping[str, Any]],
    bootstrap: BootstrapResult,
    diagnostic_rows: Sequence[Mapping[str, str]],
) -> dict[str, Any]:
    confirmatory = [
        case for case in population.cases if case.split == "confirmatory"
    ]
    delta_values: dict[str, Fraction | None] = {}
    for metric in METRICS:
        left = _point_metric(confirmatory, predictions, "M1", metric)
        right = _point_metric(confirmatory, predictions, "B0", metric)
        delta_values[metric] = (
            left - right
            if left is not None and right is not None
            else None
        )
    cluster_ba: dict[str, Fraction | None] = {}
    for cluster_type in TYPE_ORDER:
        selected = [
            case for case in confirmatory if case.cluster_type == cluster_type
        ]
        left = _point_metric(selected, predictions, "M1", "balanced_accuracy")
        right = _point_metric(selected, predictions, "B0", "balanced_accuracy")
        cluster_ba[cluster_type] = (
            left - right if left is not None and right is not None else None
        )
    stress = {
        diagnostic: next(
            row
            for row in diagnostic_rows
            if row["diagnostic_id"] == diagnostic
        )
        for diagnostic in DIAGNOSTICS
    }
    ba_interval = bootstrap.intervals[("overall", "balanced_accuracy", "M1-B0")]
    fpr_interval = bootstrap.intervals[("overall", "fpr", "M1-B0")]
    anchor_ok = (
        ba_interval["status"] == "valid"
        and fpr_interval["status"] == "valid"
        and ba_interval["ci_lower"] != NA
        and Fraction(ba_interval["ci_lower"]) > 0
        and fpr_interval["ci_upper"] != NA
        and Fraction(fpr_interval["ci_upper"]) < 0
        and delta_values["fnr"] is not None
        and delta_values["fnr"] <= 0
        and all(
            value is not None and value >= 0 for value in cluster_ba.values()
        )
        and sum(
            value is not None and value > 0 for value in cluster_ba.values()
        ) >= 4
    )
    stress_ok = all(
        row["interval_status"] == "valid"
        and row["diagnostic_ci_lower"] != NA
        and Fraction(row["diagnostic_ci_lower"]) > 0
        for row in stress.values()
    )
    return {
        "delta_ba": delta_values["balanced_accuracy"],
        "delta_fpr": delta_values["fpr"],
        "delta_fnr": delta_values["fnr"],
        "delta_values": delta_values,
        "cluster_ba": cluster_ba,
        "anchor_interval": ba_interval,
        "anchor_fpr_interval": fpr_interval,
        "anchor_ok": anchor_ok,
        "stress": stress,
        "stress_ok": stress_ok,
        "outcome": "supported" if anchor_ok and stress_ok else "mixed/not supported",
    }


def _protocol_text(repo_root: Path | None = None) -> str:
    root = (
        Path(repo_root)
        if repo_root is not None
        else Path(__file__).resolve().parents[3]
    )
    return (root / PROTOCOL_PATH).read_text(encoding="utf-8")


def _template_blocks(protocol_text: str) -> tuple[str, str]:
    blocks = re.findall(r"\x60\x60\x60text\n(.*?)\n\x60\x60\x60", protocol_text, flags=re.S)
    if len(blocks) != 2:
        raise ProtocolError("expected exactly two result templates")
    if not blocks[0].startswith("# E002-v1 result — <RUN_ID>\n"):
        raise ProtocolError("valid result template identity drift")
    if not blocks[1].startswith("# E002-v1 invalid run — <RUN_ID>\n"):
        raise ProtocolError("invalid result template identity drift")
    return blocks[0], blocks[1]


TEMPLATE_VOCABULARY = {
    "RUN_ID",
    "PROTOCOL_COMMIT",
    "PASS_OR_FAIL",
    "INT",
    "D9_OR_NA",
    "STATUS",
    "H2_OUTCOME",
    "HASH",
    "INT_LIST",
    "PASS_OR_FAIL_AND_DELTA",
    "SECONDARY_METRICS",
    "CALIBRATION_SUMMARY",
}


def _assert_template_grammar(valid_template: str, invalid_template: str) -> None:
    tokens = re.findall(
        r"<([A-Z][A-Z0-9_]*)>", valid_template + invalid_template
    )
    if set(tokens) != TEMPLATE_VOCABULARY:
        raise ProtocolError("template placeholder vocabulary drift")
    if set(
        re.findall(r"<([^>\n]+)>", valid_template + invalid_template)
    ) != TEMPLATE_VOCABULARY:
        raise ProtocolError("template contains an undeclared angle token")


def _lookup_hash(lookup: CalibrationLookup) -> str:
    return canonical_sha256(
        {
            "protocol_id": PROTOCOL_VERSION,
            "method": lookup.method,
            "rows": lookup.manifest_rows(),
        }
    )


def _render_result(
    run_id: str,
    population: Population,
    lookups: Sequence[CalibrationLookup],
    calibration_hash: str,
    manifest_hashes: Mapping[str, str],
    artifact_hashes: Mapping[str, str],
    prediction_rows: Sequence[Mapping[str, Any]],
    metric_rows: Sequence[Mapping[str, str]],
    bootstrap: BootstrapResult,
    h2: Mapping[str, Any],
    repo_root: Path | None = None,
) -> bytes:
    valid_template, invalid_template = _template_blocks(_protocol_text(repo_root))
    _assert_template_grammar(valid_template, invalid_template)
    lookup_by_method = {lookup.method: lookup for lookup in lookups}
    confirmatory = [
        case for case in population.cases if case.split == "confirmatory"
    ]
    prediction_map = {
        (row["method"], row["case_id"]): row for row in prediction_rows
    }
    metric_lookup = {
        (row["split"], row["subgroup"], row["method"]): row
        for row in metric_rows
        if row["row_kind"] == "method"
    }
    diagnostic_rows = [
        row for row in metric_rows if row["row_kind"] == "diagnostic"
    ]

    d9_values: list[str] = []
    for method in ("B0", "M1"):
        for metric in METRICS:
            d9_values.append(
                d9(_point_metric(confirmatory, prediction_map, method, metric))
            )
    for metric in METRICS:
        left = _point_metric(confirmatory, prediction_map, "M1", metric)
        right = _point_metric(confirmatory, prediction_map, "B0", metric)
        d9_values.append(d9(left - right if left is not None and right is not None else None))
    for metric in METRICS:
        d9_values.extend(
            (
                bootstrap.intervals[("overall", metric, "M1-B0")]["ci_lower"],
                bootstrap.intervals[("overall", metric, "M1-B0")]["ci_upper"],
            )
        )
    diagnostic_d9: list[str] = []
    diagnostic_ints: list[str] = []
    diagnostic_statuses: list[str] = []
    for diagnostic in DIAGNOSTICS:
        row = next(
            item for item in diagnostic_rows
            if item["diagnostic_id"] == diagnostic
        )
        diagnostic_ints.append(row["diagnostic_support"])
        diagnostic_d9.extend(
            [
                row["diagnostic_delta"],
                row["diagnostic_ci_lower"],
                row["diagnostic_ci_upper"],
            ]
        )
        diagnostic_statuses.append(row["interval_status"])
    d9_values.extend(diagnostic_d9)

    int_values = [
        str(len(population.clusters)),
        str(len(population.cases)),
        str(sum(case.split == "development" for case in population.cases)),
        str(sum(case.split == "calibration" for case in population.cases)),
        str(len(confirmatory)),
        str(len(prediction_rows)),
        str(len(metric_rows)),
        str(len(bootstrap.rows) + 1),
        *diagnostic_ints,
    ]
    if len(int_values) != 11 or len(d9_values) != 34:
        raise ProtocolError("template semantic value count drift")

    primary_statuses = [
        metric_lookup[("confirmatory", "overall", method)]["interval_status"]
        for method in ("B0", "M1")
    ]
    status_values = primary_statuses + [primary_statuses[0], *diagnostic_statuses]
    gate_values = ["pass"] * 8
    score_values: list[str] = []
    for method in (
        "M1-omit-conservation",
        "M1-overconstraint",
        "M1-stale-transition",
        "M1-no-semantic",
        "M1-no-state",
    ):
        scores = lookup_by_method[method].score_list()
        score_values.append(", ".join(str(score) for score in scores) or "none")
    score_values.append(
        ", ".join(str(score) for score in lookup_by_method["M1"].score_list())
        or "none"
    )

    secondary_values: list[str] = []
    for method in (
        "M1-omit-conservation",
        "M1-overconstraint",
        "M1-stale-transition",
        "M1-no-semantic",
        "M1-no-state",
    ):
        row = metric_lookup[("confirmatory", "overall", method)]
        secondary_values.append(
            ";".join(
                f"{short}={row[metric]}"
                for short, metric in (
                    ("ba", "balanced_accuracy"),
                    ("fpr", "fpr"),
                    ("fnr", "fnr"),
                    ("brier", "brier"),
                    ("ece", "ece"),
                )
            )
        )
    calibration_values = [
        lookup_by_method[method].summary(_lookup_hash(lookup_by_method[method]))
        for method in (
            "M1-omit-conservation",
            "M1-overconstraint",
            "M1-stale-transition",
            "M1-no-semantic",
            "M1-no-state",
        )
    ]

    hash_values = [
        *(_lookup_hash(lookup_by_method[method]) for method in (
            "M1-omit-conservation",
            "M1-overconstraint",
            "M1-stale-transition",
            "M1-no-semantic",
            "M1-no-state",
        )),
        calibration_hash,
        artifact_hashes["predictions"],
        artifact_hashes["metrics"],
        artifact_hashes["bootstrap"],
        manifest_hashes["raw_prediction"],
        manifest_hashes["calibration"],
        manifest_hashes["metric"],
        manifest_hashes["bootstrap"],
        sha256_hex(serialize_predictions(prediction_rows)),
        sha256_hex(serialize_metrics(metric_rows)),
        sha256_hex(serialize_bootstrap(bootstrap.rows)),
    ]
    if len(hash_values) != 16:
        raise ProtocolError("result hash value count drift")

    primary_rows = {
        method: metric_lookup[("confirmatory", "overall", method)]
        for method in PRIMARY_METHODS
    }
    primary_d9: list[str] = []
    for method in PRIMARY_METHODS:
        primary_d9.extend(primary_rows[method][metric] for metric in METRICS)
    delta_row_values: list[str] = []
    for metric in METRICS:
        left = _point_metric(confirmatory, prediction_map, "M1", metric)
        right = _point_metric(confirmatory, prediction_map, "B0", metric)
        delta_row_values.append(d9(left - right if left is not None and right is not None else None))
    primary_d9.extend(delta_row_values)
    interval_d9: list[str] = []
    for metric in METRICS:
        interval = bootstrap.intervals[("overall", metric, "M1-B0")]
        interval_d9.extend((interval["ci_lower"], interval["ci_upper"]))
    rendered_d9_values = primary_d9 + interval_d9 + diagnostic_d9
    if rendered_d9_values != d9_values:
        raise ProtocolError("result metric value reconstruction drift")

    interval_status_values = [
        primary_rows[method]["interval_status"] for method in PRIMARY_METHODS
    ]
    status_values = interval_status_values + [
        "valid" if all(status == "valid" for status in interval_status_values) else "partial",
        *diagnostic_statuses,
    ]
    if len(status_values) != 6:
        raise ProtocolError("result status value count drift")

    fnr_delta = h2["delta_fnr"]
    fnr_guardrail = (
        f"status={'pass' if fnr_delta is not None and fnr_delta <= 0 else 'fail'};"
        f"delta={d9(fnr_delta)}"
    )
    replacements: dict[str, list[str]] = {
        "RUN_ID": [run_id, run_id, run_id],
        "PROTOCOL_COMMIT": [PROTOCOL_COMMIT],
        "PASS_OR_FAIL": gate_values,
        "INT": int_values,
        "D9_OR_NA": rendered_d9_values,
        "STATUS": status_values,
        "H2_OUTCOME": [h2["outcome"]],
        "HASH": hash_values,
        "INT_LIST": score_values,
        "PASS_OR_FAIL_AND_DELTA": [fnr_guardrail],
        "SECONDARY_METRICS": secondary_values,
        "CALIBRATION_SUMMARY": calibration_values,
    }
    rendered = _substitute_template(valid_template, replacements)
    if rendered.count("\n") != len(rendered.splitlines()):
        raise ProtocolError("result template newline drift")
    return rendered.encode("utf-8")


def _substitute_template(template: str, replacements: Mapping[str, Sequence[str]]) -> str:
    remaining = {key: list(values) for key, values in replacements.items()}

    def replace(match: re.Match[str]) -> str:
        token = match.group(1)
        if token not in remaining or not remaining[token]:
            raise ProtocolError(f"missing replacement for <{token}>")
        value = remaining[token].pop(0)
        if (
            not value
            or any(character in value for character in ("\r", "\n", "`", "|"))
        ):
            raise ProtocolError(f"unsafe replacement for <{token}>")
        return value

    result = re.sub(r"<([A-Z][A-Z0-9_]*)>", replace, template)
    if any(values for values in remaining.values()):
        raise ProtocolError("unused template replacement")
    if re.search(r"<[^>\n]+>", result):
        raise ProtocolError("unresolved result placeholder")
    if not result.endswith("\n"):
        result += "\n"
    if "\r" in result or result.endswith("\n\n"):
        raise ProtocolError("result newline contract failed")
    if any(line.endswith((" ", "\t")) for line in result.splitlines()):
        raise ProtocolError("result trailing whitespace contract failed")
    return result


def render_invalid_result(run_id: str) -> bytes:
    if not validate_run_id(run_id):
        raise ProtocolError("invalid run ID")
    _valid_template, invalid_template = _template_blocks(_protocol_text())
    return _substitute_template(
        invalid_template,
        {"RUN_ID": [run_id, run_id], "PROTOCOL_COMMIT": [PROTOCOL_COMMIT]},
    ).encode("utf-8")


@dataclass(frozen=True)
class PipelineArtifacts:
    run_id: str
    population: Population
    lookups: tuple[CalibrationLookup, ...]
    calibration_hash: str
    prediction_rows: tuple[dict[str, Any], ...]
    metric_rows: tuple[dict[str, str], ...]
    bootstrap: BootstrapResult
    manifest_hashes: Mapping[str, str]
    artifact_hashes: Mapping[str, str]
    serialized: Mapping[str, bytes]
    h2: Mapping[str, Any]
    gate_status: Mapping[str, str]
    internal_hashes: Mapping[str, str]
    multi_fault_relation_rows: tuple[dict[str, Any], ...]
    multi_fault_relation_counts: Mapping[str, int]
    multi_fault_relation_bytes: bytes
    multi_fault_relation_hash: str

    def fingerprint(self) -> dict[str, str]:
        return {
            **{f"manifest:{key}": value for key, value in sorted(self.manifest_hashes.items())},
            **{f"artifact:{key}": value for key, value in sorted(self.artifact_hashes.items())},
            **{
                f"bytes:{key}": sha256_hex(value)
                for key, value in sorted(self.serialized.items())
                if key != "result"
            },
            **{f"internal:{key}": value for key, value in sorted(self.internal_hashes.items())},
            "h2_outcome": self.h2["outcome"],
            "bootstrap_rows": str(len(self.bootstrap.rows)),
            "metric_rows": str(len(self.metric_rows)),
            "prediction_rows": str(len(self.prediction_rows)),
            "multi_fault_relation_hash": self.multi_fault_relation_hash,
        }


def _manifest_hashes(
    population: Population,
    predictions: Sequence[Mapping[str, Any]],
    lookups: Sequence[CalibrationLookup],
    metric_rows: Sequence[Mapping[str, Any]],
    bootstrap: BootstrapResult,
) -> dict[str, str]:
    bootstrap_manifest = {
        "protocol_id": PROTOCOL_VERSION,
        "rows": [dict(row) for row in bootstrap.rows],
    }
    metric_manifest = {
        "protocol_id": PROTOCOL_VERSION,
        "rows": [dict(row) for row in metric_rows],
    }
    return {
        "population": canonical_sha256(population_manifest(population)),
        "oracle": canonical_sha256(oracle_manifest(population)),
        "raw_prediction": canonical_sha256(raw_prediction_manifest(predictions)),
        "calibration": canonical_sha256(calibration_manifest(lookups)),
        "metric": canonical_sha256(metric_manifest),
        "bootstrap": canonical_sha256(bootstrap_manifest),
    }


def _build_pipeline_once(run_id: str, repo_root: Path | None = None) -> PipelineArtifacts:
    if not validate_run_id(run_id):
        raise ProtocolError("invalid run ID")
    population = generate_population()
    independent_population = generate_population()
    if (
        canonical_sha256(population_manifest(population))
        != canonical_sha256(population_manifest(independent_population))
        or canonical_sha256(oracle_manifest(population))
        != canonical_sha256(oracle_manifest(independent_population))
    ):
        raise ProtocolError("double population generation determinism failed")
    runtime_sanity_check(population)
    calibration_cases = tuple(
        case for case in population.cases if case.split == "calibration"
    )
    lookups, _calibration_object, calibration_hash, prediction_rows, prediction_map = build_predictions(
        run_id, population, calibration_cases
    )
    lookup_hashes = {lookup.method: _lookup_hash(lookup) for lookup in lookups}
    bootstrap = run_bootstrap(population, prediction_map)
    metric_rows = build_metric_rows(
        run_id, population, prediction_map, lookup_hashes, bootstrap
    )
    prediction_bytes = serialize_predictions(prediction_rows)
    metric_bytes = serialize_metrics(metric_rows)
    bootstrap_bytes = serialize_bootstrap(bootstrap.rows)
    manifest_hashes = _manifest_hashes(
        population, prediction_rows, lookups, metric_rows, bootstrap
    )
    internal_hashes = {
        "raw_predictions": manifest_hashes["raw_prediction"],
        "calibration_lookup": manifest_hashes["calibration"],
        "prediction_rows": canonical_sha256(
            {
                "protocol_id": PROTOCOL_VERSION,
                "rows": [_prediction_json_row(row) for row in prediction_rows],
            }
        ),
        "calibration_lookups": manifest_hashes["calibration"],
        "metric_rows": canonical_sha256(
            {
                "protocol_id": PROTOCOL_VERSION,
                "rows": [dict(row) for row in metric_rows],
            }
        ),
        "bootstrap_rows": canonical_sha256(
            {
                "protocol_id": PROTOCOL_VERSION,
                "rows": [dict(row) for row in bootstrap.rows],
            }
        ),
        "bootstrap_delta_rows": canonical_sha256(
            {
                "protocol_id": PROTOCOL_VERSION,
                "rows": [dict(row) for row in bootstrap.rows],
            }
        ),
        "bootstrap_intervals": canonical_sha256(
            {
                "protocol_id": PROTOCOL_VERSION,
                "intervals": [
                    {"key": "|".join(key), **dict(value)}
                    for key, value in sorted(bootstrap.intervals.items())
                ],
            }
        ),
    }
    artifact_hashes = {
        "predictions": sha256_hex(prediction_bytes),
        "metrics": sha256_hex(metric_bytes),
        "bootstrap": sha256_hex(bootstrap_bytes),
    }
    multi_rows, multi_counts, multi_bytes, multi_hash = multi_fault_relation_evidence(population)
    diagnostic_rows = [row for row in metric_rows if row["row_kind"] == "diagnostic"]
    h2 = _h2_summary(population, prediction_map, bootstrap, diagnostic_rows)
    result_bytes = _render_result(
        run_id,
        population,
        lookups,
        calibration_hash,
        manifest_hashes,
        artifact_hashes,
        prediction_rows,
        metric_rows,
        bootstrap,
        h2,
        repo_root,
    )
    serialized = {
        "predictions": prediction_bytes,
        "metrics": metric_bytes,
        "bootstrap": bootstrap_bytes,
        "result": result_bytes,
    }
    if len(prediction_rows) != 7296 or len(metric_rows) != 243:
        raise ProtocolError("serialized row count drift")
    if len(bootstrap.rows) != 530053 or len(bootstrap_bytes.splitlines()) != 530054:
        raise ProtocolError("serialized bootstrap count drift")
    if (
        len(prediction_bytes) >= 8_000_000
        or len(metric_bytes) >= 500_000
        or len(bootstrap_bytes) >= 50_000_000
        or len(result_bytes) >= 40_000
        or BOOTSTRAP_ESTIMATE >= PUBLIC_LIMIT
    ):
        raise ProtocolError("public file-size gate failed")
    return PipelineArtifacts(
        run_id=run_id,
        population=population,
        lookups=lookups,
        calibration_hash=calibration_hash,
        prediction_rows=prediction_rows,
        metric_rows=metric_rows,
        bootstrap=bootstrap,
        manifest_hashes=manifest_hashes,
        artifact_hashes=artifact_hashes,
        serialized=serialized,
        h2=h2,
        gate_status={
            "protocol_identity": "pass",
            "clean_tree": "pass",
            "split_disjointness": "pass",
            "oracle": "pass",
            "footprints": "pass",
            "calibration_isolation": "pass",
            "determinism": "pass",
            "size": "pass",
        },
        internal_hashes=internal_hashes,
        multi_fault_relation_rows=multi_rows,
        multi_fault_relation_counts=multi_counts,
        multi_fault_relation_bytes=multi_bytes,
        multi_fault_relation_hash=multi_hash,
    )


def build_pipeline(run_id: str, repo_root: Path | None = None) -> PipelineArtifacts:
    """Build twice in memory and compare every locked hash/serialized byte."""

    first = _build_pipeline_once(run_id, repo_root)
    second = _build_pipeline_once(run_id, repo_root)
    if first.fingerprint() != second.fingerprint():
        raise ProtocolError("complete two-build determinism gate failed")
    for key in first.serialized:
        if first.serialized[key] != second.serialized[key]:
            raise ProtocolError(f"serialized byte determinism failed: {key}")
    return first
