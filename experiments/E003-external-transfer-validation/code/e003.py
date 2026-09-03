"""Side-effect-free standard-library implementation of locked E003-v1.

The module contains the source adapter, deterministic base/case construction,
evaluated validators, calibration, metrics, bootstrap, and canonical
serialization.  It never writes files and it does not import the independent
oracle until a pipeline is explicitly requested by a caller.  The
development/calibration preflight has a separate split allowlist and therefore
cannot open the future holdout stream.
"""

from __future__ import annotations

import copy
import csv
import datetime as _datetime
import hashlib
import io
import inspect
import json
import math
import re
import zlib
from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from decimal import Decimal, ROUND_HALF_EVEN, localcontext
from fractions import Fraction
from pathlib import Path
from types import MappingProxyType
from typing import Any, Callable, Iterable, Mapping, Sequence
from urllib.parse import urlsplit


PROTOCOL_VERSION = "E003-v1"
PROTOCOL_COMMIT = "163e44dcabc698f101dee70dd7f3aa1bb7c8d5fb"
PROTOCOL_BLOB_SHA256 = "8ec0ebc9b3420a2d71eebfe579ae2d1c87aa74c419dd3f38d1f0dc06c5c1e2a6"
PROTOCOL_PATH = "experiments/E003-external-transfer-validation/protocol.md"

SPLITS = ("development", "calibration", "confirmatory")
SPLIT_RANK = {name: index for index, name in enumerate(SPLITS)}
SOURCE_FILES = MappingProxyType(
    {
        "development": "2019-01-15-12.json.gz",
        "calibration": "2020-01-15-12.json.gz",
        "confirmatory": "2021-01-15-12.json.gz",
    }
)
SOURCE_URLS = MappingProxyType(
    {
        "development": "https://data.gharchive.org/2019-01-15-12.json.gz",
        "calibration": "https://data.gharchive.org/2020-01-15-12.json.gz",
        "confirmatory": "https://data.gharchive.org/2021-01-15-12.json.gz",
    }
)

EVENT_TYPES = ("IssuesEvent", "PullRequestEvent")
EVENT_TYPE_RANK = {name: index for index, name in enumerate(EVENT_TYPES)}
STATUS_ACTIONS = frozenset(("opened", "closed", "reopened"))
RESOURCE_STATES = frozenset(("open", "closed"))
VARIANTS = (
    "clean",
    "S1-missing-resource",
    "I1-wrong-repository",
    "T1-status-contradiction",
)
VARIANT_RANK = {name: index for index, name in enumerate(VARIANTS)}
VARIANT_KIND = MappingProxyType(
    {
        "clean": "clean",
        "S1-missing-resource": "S1",
        "I1-wrong-repository": "I1",
        "T1-status-contradiction": "T1",
    }
)
FAMILIES = ("schema", "identity", "state")
METHODS = (
    "B0",
    "M1",
    "M1-no-identity",
    "M1-no-state",
    "M1-no-calibration",
)
CALIBRATED_METHODS = ("B0", "M1", "M1-no-identity", "M1-no-state")
PRIMARY_METHODS = ("B0", "M1")
ABLATION_METHODS = ("M1-no-identity", "M1-no-state", "M1-no-calibration")
METHOD_RANK = {name: index for index, name in enumerate(METHODS)}
SUBGROUPS = ("overall", "type:IssuesEvent", "type:PullRequestEvent")
SUBGROUP_RANK = {name: index for index, name in enumerate(SUBGROUPS)}
METRICS = ("balanced_accuracy", "fpr", "fnr", "brier", "ece")
METRIC_RANK = {name: index for index, name in enumerate(METRICS)}
BOOTSTRAP_REPLICATES = 10_000
BASES_PER_EVENT_TYPE = 64
MAX_BASES_PER_REPOSITORY_EVENT_TYPE = 4
CASES_PER_BASE = 4
CASES_PER_SPLIT = 512
PREDICTIONS_PER_SPLIT = CASES_PER_SPLIT * len(METHODS)
EXPECTED_METRIC_ROWS = len(SPLITS) * len(SUBGROUPS) * (len(METHODS) + 1)
EXPECTED_BOOTSTRAP_ROWS = len(SUBGROUPS) * len(METRICS) * BOOTSTRAP_REPLICATES
NA = "NA"
DECIMAL_PLACES = 12
PUBLIC_SIZE_LIMITS = MappingProxyType(
    {
        "predictions": 8_000_000,
        "metrics": 500_000,
        "bootstrap": 20_000_000,
        "result": 50_000,
    }
)
SENTINEL_REPOSITORY_URL = "https://api.github.com/repos/e003-fixture-sentinel/repository"
NO_CALIBRATION_MARKER = (
    "E003-v1|calibration_lookup|M1-no-calibration|none"
)
NO_CALIBRATION_MARKER_SHA256 = hashlib.sha256(
    NO_CALIBRATION_MARKER.encode("utf-8")
).hexdigest()
METRIC_FIELDS = (
    "row_kind",
    "run_id",
    "protocol_id",
    "source_manifest_sha256",
    "split",
    "subgroup",
    "method",
    "method_pair",
    "variant_scope",
    "support",
    "positive_count",
    "negative_count",
    "tp",
    "tn",
    "fp",
    "fn",
    "balanced_accuracy",
    "fpr",
    "fnr",
    "brier",
    "ece",
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
)
BOOTSTRAP_FIELDS = (
    "run_id",
    "replicate",
    "subgroup",
    "metric",
    "method_pair",
    "delta",
    "status",
)
PREDICTION_FIELDS = (
    "protocol_id",
    "run_id",
    "source_file",
    "source_sha256",
    "source_line",
    "split",
    "repo_id",
    "event_id",
    "event_type",
    "base_event_id",
    "variant_id",
    "case_kind",
    "truth",
    "oracle_failure_set",
    "schema_valid",
    "method",
    "decision",
    "raw_score",
    "p_valid",
    "input_sha256",
    "source_manifest_sha256",
    "calibration_lookup_sha256",
    "status",
)


class ProtocolError(ValueError):
    """A locked E003 invariant failed."""


class JsonNumber(str):
    """A fixed decimal token emitted as a JSON number by the serializer."""


def _as_fraction(value: Fraction | Decimal | int | float | JsonNumber) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, Decimal):
        return Fraction(value)
    if isinstance(value, JsonNumber):
        return Fraction(str(value))
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ProtocolError("non-finite decimal")
        return Fraction(str(value))
    return Fraction(value)


def decimal_token(value: Fraction | Decimal | int | float, places: int = DECIMAL_PLACES) -> str:
    """Round only at the serialization boundary using exact rational input."""

    fraction = _as_fraction(value)
    if places < 0:
        raise ValueError("places must be nonnegative")
    quantum = Decimal(1).scaleb(-places)
    with localcontext() as context:
        context.prec = max(100, places * 4 + 32)
        rounded = (
            Decimal(fraction.numerator) / Decimal(fraction.denominator)
        ).quantize(quantum, rounding=ROUND_HALF_EVEN)
    if rounded == 0:
        return "0" if places == 0 else "0." + ("0" * places)
    text = format(rounded, "f")
    if places == 0:
        return text.split(".", 1)[0]
    whole, _, fractional = text.partition(".")
    return whole + "." + fractional.ljust(places, "0")[:places]


def _canonical_json(value: Any) -> str:
    if isinstance(value, JsonNumber):
        if re.fullmatch(r"-?(?:0|[1-9][0-9]*)\.[0-9]{1,18}", str(value)) is None:
            raise ProtocolError("invalid canonical JSON number")
        return str(value)
    if type(value) is dict:
        if any(type(key) is not str for key in value):
            raise ProtocolError("canonical JSON object keys must be strings")
        return "{" + ",".join(
            _canonical_json(key) + ":" + _canonical_json(value[key])
            for key in sorted(value, key=lambda item: item.encode("utf-8"))
        ) + "}"
    if type(value) in (list, tuple):
        return "[" + ",".join(_canonical_json(item) for item in value) + "]"
    if value is None:
        return "null"
    if type(value) is bool:
        return "true" if value else "false"
    if type(value) is int:
        return str(value)
    if isinstance(value, (Fraction, Decimal, float)):
        return decimal_token(value)
    if type(value) is str:
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    raise ProtocolError(f"unsupported canonical JSON value: {type(value)!r}")


def canonical_json_text(value: Any) -> str:
    return _canonical_json(value)


def canonical_json_bytes(value: Any) -> bytes:
    return canonical_json_text(value).encode("utf-8")


def canonical_jsonl_bytes(value: Any) -> bytes:
    return canonical_json_bytes(value) + b"\n"


def sha256_hex(value: bytes | str) -> str:
    if isinstance(value, str):
        value = value.encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def input_sha256(payload: Mapping[str, Any]) -> str:
    return sha256_hex(canonical_jsonl_bytes(payload))


def _reject_json_constant(token: str) -> None:
    raise ValueError(f"non-standard JSON constant: {token}")


def _strict_object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def strict_json_loads(text: str) -> Any:
    return json.loads(
        text,
        object_pairs_hook=_strict_object_pairs,
        parse_constant=_reject_json_constant,
    )


def _strict_decimal_id(value: Any) -> str | None:
    if type(value) is int:
        return str(value) if value >= 0 else None
    if type(value) is str and re.fullmatch(r"(?:0|[1-9][0-9]*)", value):
        return value
    return None


def _positive_integer(value: Any) -> bool:
    return type(value) is int and value > 0


def _valid_utc_timestamp(value: Any) -> bool:
    if type(value) is not str:
        return False
    if re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?Z",
        value,
    ) is None:
        return False
    try:
        _datetime.datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return False
    return True


def repository_components(url: Any) -> tuple[str, str] | None:
    if type(url) is not str:
        return None
    try:
        parsed = urlsplit(url)
        if parsed.scheme != "https" or parsed.netloc != "api.github.com":
            return None
        if parsed.query or parsed.fragment or parsed.username or parsed.password:
            return None
        if parsed.port is not None:
            return None
    except ValueError:
        return None
    parts = parsed.path.split("/")
    if len(parts) != 4 or parts[:2] != ["", "repos"]:
        return None
    if not parts[2] or not parts[3]:
        return None
    return parts[2], parts[3]


def resource_components(url: Any, resource: str) -> tuple[str, str, int] | None:
    if type(url) is not str:
        return None
    try:
        parsed = urlsplit(url)
        if parsed.scheme != "https" or parsed.netloc != "api.github.com":
            return None
        if parsed.query or parsed.fragment or parsed.username or parsed.password:
            return None
        if parsed.port is not None:
            return None
    except ValueError:
        return None
    parts = parsed.path.split("/")
    if len(parts) != 6 or parts[:2] != ["", "repos"]:
        return None
    if not parts[2] or not parts[3] or parts[4] != resource:
        return None
    if re.fullmatch(r"[1-9][0-9]*", parts[5]) is None:
        return None
    return parts[2], parts[3], int(parts[5])


def _has_fields(value: Any, fields: set[str] | frozenset[str]) -> bool:
    return type(value) is dict and fields.issubset(value)


_TOP_LEVEL_FIELDS = frozenset(
    ("id", "type", "actor", "repo", "payload", "public", "created_at")
)
_ACTOR_FIELDS = frozenset(("id", "login"))
_REPOSITORY_FIELDS = frozenset(("id", "name", "url"))
_ISSUE_FIELDS = frozenset(("id", "number", "state", "url", "repository_url"))
_PULL_REQUEST_FIELDS = frozenset(("id", "number", "state", "merged", "url"))


def _common_schema(payload: Any) -> bool:
    if type(payload) is not dict or not _TOP_LEVEL_FIELDS.issubset(payload):
        return False
    if _strict_decimal_id(payload.get("id")) is None:
        return False
    if payload.get("type") not in EVENT_TYPES:
        return False
    actor = payload.get("actor")
    if not _has_fields(actor, _ACTOR_FIELDS):
        return False
    if _strict_decimal_id(actor.get("id")) is None or type(actor.get("login")) is not str:
        return False
    repository = payload.get("repo")
    if not _has_fields(repository, _REPOSITORY_FIELDS):
        return False
    if (
        _strict_decimal_id(repository.get("id")) is None
        or type(repository.get("name")) is not str
        or not repository.get("name")
        or repository_components(repository.get("url")) is None
    ):
        return False
    if type(payload.get("public")) is not bool:
        return False
    if not _valid_utc_timestamp(payload.get("created_at")):
        return False
    return type(payload.get("payload")) is dict


def _event_schema(payload: Mapping[str, Any]) -> bool:
    event_payload = payload.get("payload")
    if type(event_payload) is not dict:
        return False
    if type(event_payload.get("action")) is not str:
        return False
    if event_payload.get("action") not in STATUS_ACTIONS:
        return False
    if payload.get("type") == "IssuesEvent":
        issue = event_payload.get("issue")
        return (
            _has_fields(issue, _ISSUE_FIELDS)
            and _strict_decimal_id(issue.get("id")) is not None
            and _positive_integer(issue.get("number"))
            and issue.get("state") in RESOURCE_STATES
            and resource_components(issue.get("url"), "issues") is not None
            and repository_components(issue.get("repository_url")) is not None
        )
    if payload.get("type") == "PullRequestEvent":
        pull_request = event_payload.get("pull_request")
        return (
            _positive_integer(event_payload.get("number"))
            and _has_fields(pull_request, _PULL_REQUEST_FIELDS)
            and _strict_decimal_id(pull_request.get("id")) is not None
            and _positive_integer(pull_request.get("number"))
            and pull_request.get("state") in RESOURCE_STATES
            and type(pull_request.get("merged")) is bool
            and resource_components(pull_request.get("url"), "pulls") is not None
        )
    return False


def _identity_relation(payload: Mapping[str, Any]) -> bool:
    top_repository = repository_components(payload["repo"]["url"])
    if top_repository is None:
        return False
    event_payload = payload["payload"]
    if payload["type"] == "IssuesEvent":
        issue = event_payload["issue"]
        nested_repository = repository_components(issue["repository_url"])
        issue_url = resource_components(issue["url"], "issues")
        return (
            nested_repository == top_repository
            and issue_url is not None
            and issue_url[:2] == top_repository
            and issue_url[2] == issue["number"]
        )
    pull_request = event_payload["pull_request"]
    pull_url = resource_components(pull_request["url"], "pulls")
    return (
        pull_url is not None
        and pull_url[:2] == top_repository
        and pull_url[2] == pull_request["number"] == event_payload["number"]
    )


def _state_relation(payload: Mapping[str, Any]) -> bool:
    action = payload["payload"]["action"]
    if payload["type"] == "IssuesEvent":
        expected = {"opened": "open", "reopened": "open", "closed": "closed"}
        return payload["payload"]["issue"]["state"] == expected.get(action)
    pull_request = payload["payload"]["pull_request"]
    if action in ("opened", "reopened"):
        return pull_request["state"] == "open" and pull_request["merged"] is False
    return action == "closed" and pull_request["state"] == "closed"


def schema_valid(payload: Any) -> bool:
    return _common_schema(payload) and _event_schema(payload)


# These are intentionally mutable test seams.  The oracle has no reference to
# them and the runtime perturbation test can show that the two implementations
# are not one table or predicate under another name.
M1_CHECKS: dict[str, Callable[[Mapping[str, Any]], bool]] = {
    "identity": _identity_relation,
    "state": _state_relation,
}

ORACLE_ONLY_METADATA_FIELDS = frozenset(
    {
        "truth",
        "oracle_failure_set",
        "schema_valid",
        "split",
        "source_file",
        "source_line",
        "source_sha256",
        "source_manifest_sha256",
        "input_sha256",
        "variant_id",
        "case_kind",
        "status",
    }
)
INDEPENDENCE_EVIDENCE_KEY = "oracle_independence"


@dataclass(frozen=True)
class ValidationResult:
    decision: bool
    raw_score: int
    failed_families: tuple[str, ...]
    schema_valid: bool


def _validate_families(payload: Any, families: Sequence[str]) -> ValidationResult:
    if not schema_valid(payload):
        return ValidationResult(False, 1, ("schema",), False)
    failures = tuple(
        family for family in families if not M1_CHECKS[family](payload)
    )
    return ValidationResult(not failures, len(failures), failures, True)


def validate_b0(payload: Any) -> ValidationResult:
    return _validate_families(payload, ())


def validate_m1(payload: Any) -> ValidationResult:
    return _validate_families(payload, ("identity", "state"))


def validate_method(payload: Any, method: str) -> ValidationResult:
    if method == "B0":
        return validate_b0(payload)
    if method in ("M1", "M1-no-calibration"):
        return validate_m1(payload)
    if method == "M1-no-identity":
        return _validate_families(payload, ("state",))
    if method == "M1-no-state":
        return _validate_families(payload, ("identity",))
    raise ProtocolError(f"unknown method: {method}")


def _source_text(value: Any, label: str) -> str:
    try:
        return inspect.getsource(value)
    except (OSError, TypeError) as error:
        raise ProtocolError(f"independence source inspection failed: {label}") from error


def _metadata_references(source: str) -> tuple[str, ...]:
    return tuple(
        sorted(
            field
            for field in ORACLE_ONLY_METADATA_FIELDS
            if re.search(rf"[\"']{re.escape(field)}[\"']", source)
        )
    )


def _inspect_independence_sources(oracle_fn: Callable[[Mapping[str, Any]], Any]) -> dict[str, Any]:
    """Inspect the locked oracle and method call boundary before probing it."""

    oracle_module = inspect.getmodule(oracle_fn)
    if oracle_module is None or oracle_module.__name__ != "oracle_e003":
        raise ProtocolError("independence oracle module identity drift")
    if getattr(oracle_fn, "__name__", None) != "reference_oracle":
        raise ProtocolError("independence oracle callable identity drift")
    oracle_source = _source_text(oracle_module, "oracle_e003")
    if re.search(r"(?m)^\s*(?:from|import)\s+(?:e003|run_e003)\b", oracle_source):
        raise ProtocolError("oracle source imports method or runner code")
    oracle_method_references = tuple(
        sorted(
            token
            for token in ("validate_method", "validate_b0", "validate_m1", "M1_CHECKS")
            if re.search(rf"\b{re.escape(token)}\b", oracle_source)
        )
    )
    if oracle_method_references:
        raise ProtocolError("oracle source references method implementation")

    validator_functions = (
        ("validate_method", validate_method),
        ("validate_b0", validate_b0),
        ("validate_m1", validate_m1),
        ("_validate_families", _validate_families),
        ("schema_valid", schema_valid),
        ("_common_schema", _common_schema),
        ("_event_schema", _event_schema),
        ("_identity_relation", _identity_relation),
        ("_state_relation", _state_relation),
    )
    validator_sources = {
        name: _source_text(function, name) for name, function in validator_functions
    }
    validator_metadata_references = tuple(
        sorted(
            {
                field
                for source in validator_sources.values()
                for field in _metadata_references(source)
            }
        )
    )
    if validator_metadata_references:
        raise ProtocolError("validator source accesses evaluator metadata")
    for family in ("identity", "state"):
        function = M1_CHECKS.get(family)
        if not callable(function) or getattr(function, "__module__", None) != __name__:
            raise ProtocolError("method predicate source identity drift")
        if _metadata_references(_source_text(function, f"M1_CHECKS.{family}")):
            raise ProtocolError("method predicate accesses evaluator metadata")

    validator_digest = sha256_hex(
        canonical_json_bytes(
            {
                name: sha256_hex(source.encode("utf-8"))
                for name, source in validator_sources.items()
            }
        )
    )
    return {
        "status": "pass",
        "oracle_module": oracle_module.__name__,
        "oracle_callable": oracle_fn.__name__,
        "oracle_source_sha256": sha256_hex(oracle_source.encode("utf-8")),
        "validator_source_sha256": validator_digest,
        "oracle_method_references": list(oracle_method_references),
        "validator_metadata_references": list(validator_metadata_references),
        "metadata_fields_checked": sorted(ORACLE_ONLY_METADATA_FIELDS),
    }


class _MetadataAccessGuard(dict[str, Any]):
    """Dictionary probe that fails if a method asks for evaluator metadata."""

    @staticmethod
    def _check(key: Any) -> None:
        if key in ORACLE_ONLY_METADATA_FIELDS:
            raise ProtocolError(f"method accessed evaluator metadata: {key}")

    def __getitem__(self, key: Any) -> Any:
        self._check(key)
        return super().__getitem__(key)

    def get(self, key: Any, default: Any = None) -> Any:
        self._check(key)
        return super().get(key, default)

    def __contains__(self, key: object) -> bool:
        self._check(key)
        return super().__contains__(key)

    def pop(self, key: Any, default: Any = None) -> Any:
        self._check(key)
        return super().pop(key, default)

    def setdefault(self, key: Any, default: Any = None) -> Any:
        self._check(key)
        return super().setdefault(key, default)


def _guard_metadata_payload(value: Any) -> Any:
    if type(value) is dict:
        return _MetadataAccessGuard(
            {key: _guard_metadata_payload(item) for key, item in value.items()}
        )
    if type(value) is list:
        return [_guard_metadata_payload(item) for item in value]
    return value


def _run_metadata_tripwire(payload: Mapping[str, Any]) -> dict[str, Any]:
    guarded = _guard_metadata_payload(copy.deepcopy(payload))
    if not isinstance(guarded, _MetadataAccessGuard):
        raise ProtocolError("metadata tripwire payload construction failed")
    for field in ORACLE_ONLY_METADATA_FIELDS:
        guarded[field] = None

    original_schema_valid = schema_valid
    original_checks = dict(M1_CHECKS)

    def _always_true(_payload: Mapping[str, Any]) -> bool:
        return True

    try:
        globals()["schema_valid"] = lambda _payload: True
        M1_CHECKS.clear()
        M1_CHECKS.update({"identity": _always_true, "state": _always_true})
        for method in METHODS:
            result = validate_method(guarded, method)
            if type(result.decision) is not bool:
                raise ProtocolError("metadata tripwire returned a malformed decision")
    finally:
        globals()["schema_valid"] = original_schema_valid
        M1_CHECKS.clear()
        M1_CHECKS.update(original_checks)
    return {
        "status": "pass",
        "methods_checked": list(METHODS),
        "payload_count": 1,
        "forbidden_fields": sorted(ORACLE_ONLY_METADATA_FIELDS),
    }


def project_event(raw: Any) -> tuple[dict[str, Any] | None, str | None]:
    """Project an eligible raw object while retaining no unknown raw fields."""

    if not _common_schema(raw):
        return None, "common_schema"
    if not _event_schema(raw):
        return None, "event_specific_schema"
    actor = raw["actor"]
    repository = raw["repo"]
    event_payload = raw["payload"]
    projected: dict[str, Any] = {
        "actor": {
            "id": _strict_decimal_id(actor["id"]),
            "login": actor["login"],
        },
        "created_at": raw["created_at"],
        "id": _strict_decimal_id(raw["id"]),
        "payload": {"action": event_payload["action"]},
        "public": raw["public"],
        "repo": {
            "id": _strict_decimal_id(repository["id"]),
            "name": repository["name"],
            "url": repository["url"],
        },
        "type": raw["type"],
    }
    if raw["type"] == "IssuesEvent":
        issue = event_payload["issue"]
        projected["payload"]["issue"] = {
            "id": _strict_decimal_id(issue["id"]),
            "number": issue["number"],
            "repository_url": issue["repository_url"],
            "state": issue["state"],
            "url": issue["url"],
        }
    else:
        pull_request = event_payload["pull_request"]
        projected["payload"]["number"] = event_payload["number"]
        projected["payload"]["pull_request"] = {
            "id": _strict_decimal_id(pull_request["id"]),
            "merged": pull_request["merged"],
            "number": pull_request["number"],
            "state": pull_request["state"],
            "url": pull_request["url"],
        }
    if not _identity_relation(projected):
        return None, "identity"
    if not _state_relation(projected):
        return None, "state"
    return projected, None


@dataclass(frozen=True)
class ManifestFile:
    split: str
    filename: str
    url: str
    bytes: int
    jsonl_lines: int
    sha256: str


@dataclass(frozen=True)
class SourceManifest:
    protocol_id: str
    files: tuple[ManifestFile, ...]
    manifest_path: Path
    source_root: Path
    manifest_sha256: str

    def file_for(self, split: str) -> ManifestFile:
        for item in self.files:
            if item.split == split:
                return item
        raise ProtocolError(f"manifest has no split: {split}")


def load_manifest(manifest_path: Path | str, source_root: Path | str | None = None) -> SourceManifest:
    path = Path(manifest_path).expanduser().resolve()
    try:
        data_bytes = path.read_bytes()
    except OSError as error:
        raise ProtocolError(f"cannot read source manifest: {path}") from error
    if not data_bytes.endswith(b"\n"):
        raise ProtocolError("source manifest must have LF termination")
    try:
        data = strict_json_loads(data_bytes[:-1].decode("utf-8"))
    except (UnicodeDecodeError, ValueError, json.JSONDecodeError) as error:
        raise ProtocolError("source manifest is not strict JSON") from error
    if canonical_jsonl_bytes(data) != data_bytes:
        raise ProtocolError("source manifest is not canonical UTF-8/LF JSON")
    if type(data) is not dict or set(data) != {"files", "protocol_id"}:
        raise ProtocolError("source manifest root schema mismatch")
    if data["protocol_id"] != PROTOCOL_VERSION or type(data["files"]) is not list:
        raise ProtocolError("source manifest protocol identity mismatch")
    if len(data["files"]) != len(SPLITS):
        raise ProtocolError("source manifest file count mismatch")
    files: list[ManifestFile] = []
    for index, item in enumerate(data["files"]):
        if type(item) is not dict or set(item) != {
            "bytes", "filename", "jsonl_lines", "sha256", "split", "url"
        }:
            raise ProtocolError("source manifest file schema mismatch")
        split = SPLITS[index]
        if item["split"] != split or item["filename"] != SOURCE_FILES[split]:
            raise ProtocolError("source manifest split or filename mismatch")
        if item["url"] != SOURCE_URLS[split]:
            raise ProtocolError("source manifest URL mismatch")
        if (
            type(item["bytes"]) is not int
            or item["bytes"] < 0
            or type(item["jsonl_lines"]) is not int
            or item["jsonl_lines"] < 0
            or type(item["sha256"]) is not str
            or re.fullmatch(r"[0-9a-f]{64}", item["sha256"]) is None
        ):
            raise ProtocolError("source manifest numeric/hash field mismatch")
        files.append(
            ManifestFile(
                split=split,
                filename=item["filename"],
                url=item["url"],
                bytes=item["bytes"],
                jsonl_lines=item["jsonl_lines"],
                sha256=item["sha256"],
            )
        )
    root = (
        Path(source_root).expanduser().resolve()
        if source_root is not None
        else path.parent.joinpath("source").resolve()
    )
    return SourceManifest(
        protocol_id=PROTOCOL_VERSION,
        files=tuple(files),
        manifest_path=path,
        source_root=root,
        manifest_sha256=sha256_hex(data_bytes),
    )


def _read_source_bytes(path: Path) -> bytes:
    """Read one source file; the development guard replaces this seam."""

    with path.open("rb") as stream:
        chunks: list[bytes] = []
        while True:
            chunk = stream.read(1024 * 1024)
            if not chunk:
                return b"".join(chunks)
            chunks.append(chunk)


def verify_source_hashes(
    manifest: SourceManifest,
    splits: Sequence[str] = SPLITS,
) -> dict[str, tuple[int, str]]:
    """Verify only the requested raw gzip bytes; no decompression occurs here."""

    requested = tuple(splits)
    if not requested or any(split not in SPLITS for split in requested):
        raise ProtocolError("invalid source-hash split allowlist")
    if len(set(requested)) != len(requested):
        raise ProtocolError("duplicate source-hash split")
    if not manifest.source_root.is_dir():
        raise ProtocolError("source root is missing")
    expected_names = {manifest.file_for(split).filename for split in requested}
    for split in requested:
        item = manifest.file_for(split)
        if "/" in item.filename or "\\" in item.filename:
            raise ProtocolError("manifest filename is not a basename")
        path = manifest.source_root / item.filename
        if not path.is_file():
            raise ProtocolError(f"source file is missing: {item.filename}")
        data = _read_source_bytes(path)
        digest = sha256_hex(data)
        if len(data) != item.bytes or digest != item.sha256:
            raise ProtocolError(f"source hash/byte mismatch: {item.filename}")
    if set(requested) == set(SPLITS):
        actual_files = {
            path.name for path in manifest.source_root.iterdir() if path.is_file()
        }
        expected_all = {manifest.file_for(split).filename for split in SPLITS}
        if actual_files != expected_all:
            raise ProtocolError("source cache contains an unmanifested file")
    return {
        split: (
            manifest.file_for(split).bytes,
            manifest.file_for(split).sha256,
        )
        for split in requested
    }


def _strict_gzip_decompress(data: bytes) -> bytes:
    if not data.startswith(b"\x1f\x8b"):
        raise ProtocolError("source is not gzip")
    remaining = data
    output: list[bytes] = []
    while remaining:
        decompressor = zlib.decompressobj(16 + zlib.MAX_WBITS)
        try:
            output.append(decompressor.decompress(remaining))
            output.append(decompressor.flush())
        except zlib.error as error:
            raise ProtocolError("malformed gzip stream") from error
        if not decompressor.eof:
            raise ProtocolError("truncated gzip stream")
        remaining = decompressor.unused_data
        if remaining and not remaining.startswith(b"\x1f\x8b"):
            raise ProtocolError("trailing binary after gzip stream")
    return b"".join(output)


def _iter_source_records(manifest: SourceManifest, split: str):
    item = manifest.file_for(split)
    path = manifest.source_root / item.filename
    try:
        decompressed = _strict_gzip_decompress(_read_source_bytes(path))
        text = decompressed.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ProtocolError(f"source is not strict UTF-8: {item.filename}") from error
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    if len(lines) != item.jsonl_lines:
        raise ProtocolError(f"JSONL line count mismatch: {item.filename}")
    for source_line, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            value = strict_json_loads(line)
        except (ValueError, json.JSONDecodeError) as error:
            raise ProtocolError(
                f"malformed JSONL at {item.filename}:{source_line}"
            ) from error
        yield source_line, value


def _raw_label(value: Any) -> str:
    if value is None:
        return "<missing>"
    if type(value) is str:
        return value
    try:
        return canonical_json_text(value)
    except ProtocolError:
        return f"<{type(value).__name__}>"


def _event_id_key(raw: Mapping[str, Any]) -> str | None:
    if "id" not in raw:
        return None
    normalized = _strict_decimal_id(raw["id"])
    if normalized is not None:
        return "decimal:" + normalized
    return "invalid:" + canonical_json_text(raw["id"])


@dataclass(frozen=True)
class SourceEvent:
    split: str
    source_file: str
    source_sha256: str
    source_line: int
    repo_id: str
    event_id: str
    event_type: str
    action: str
    payload: dict[str, Any]
    input_sha256: str

    @property
    def repo_id_integer(self) -> int:
        return int(self.repo_id)

    @property
    def event_id_integer(self) -> int:
        return int(self.event_id)


@dataclass(frozen=True)
class SourceScan:
    split: str
    line_count: int
    repo_ids: frozenset[str]
    eligible: tuple[SourceEvent, ...]
    exclusion_counts: tuple[tuple[str, int], ...]

    def exclusions(self) -> dict[str, int]:
        return dict(self.exclusion_counts)


@dataclass(frozen=True)
class SourceBundle:
    manifest: SourceManifest
    scans: tuple[SourceScan, ...]
    shared_repo_ids: frozenset[str]

    def scan_for(self, split: str) -> SourceScan:
        for scan in self.scans:
            if scan.split == split:
                return scan
        raise ProtocolError(f"bundle has no split: {split}")

    def eligible(self, split: str) -> tuple[SourceEvent, ...]:
        return self.scan_for(split).eligible

    def exclusion_counts(self) -> dict[str, dict[str, int]]:
        return {scan.split: scan.exclusions() for scan in self.scans}


def _selection_sort_key(event: SourceEvent) -> tuple[Any, ...]:
    return (
        EVENT_TYPE_RANK[event.event_type],
        event.repo_id_integer,
        event.event_id_integer,
        event.source_file,
        event.source_line,
    )


def scan_source_split(
    manifest: SourceManifest,
    split: str,
    oracle_fn: Callable[[Mapping[str, Any]], Any],
    seen_event_ids: dict[str, tuple[str, int]] | None = None,
) -> SourceScan:
    if split not in SPLITS:
        raise ProtocolError(f"unknown source split: {split}")
    seen = seen_event_ids if seen_event_ids is not None else {}
    exclusions: Counter[str] = Counter()
    repo_ids: set[str] = set()
    eligible: list[SourceEvent] = []
    for source_line, raw in _iter_source_records(manifest, split):
        if type(raw) is not dict:
            raise ProtocolError(f"JSONL record is not an object: {split}:{source_line}")
        event_key = _event_id_key(raw)
        if event_key is not None:
            if event_key in seen:
                previous = seen[event_key]
                raise ProtocolError(
                    f"duplicate event ID across source: {previous[0]}:{previous[1]} and {split}:{source_line}"
                )
            seen[event_key] = (split, source_line)
        raw_repo = raw.get("repo")
        repo_id = (
            _strict_decimal_id(raw_repo.get("id"))
            if type(raw_repo) is dict
            else None
        )
        if repo_id is not None:
            repo_ids.add(repo_id)
        event_type = raw.get("type")
        raw_payload = raw.get("payload")
        action = raw_payload.get("action") if type(raw_payload) is dict else None
        if event_type not in EVENT_TYPES or action not in STATUS_ACTIONS:
            exclusions[
                "raw_type_action:" + canonical_json_text(
                    [_raw_label(event_type), _raw_label(action)]
                )
            ] += 1
            continue
        projected, reason = project_event(raw)
        if projected is None:
            if reason is None:
                raise ProtocolError("projection returned no reason")
            exclusions[reason] += 1
            continue
        oracle_result = oracle_fn(projected)
        failure_set = tuple(getattr(oracle_result, "oracle_failure_set", ()))
        if getattr(oracle_result, "schema_valid", False) is not True:
            exclusions["oracle_schema"] += 1
            continue
        if failure_set:
            exclusions["oracle_" + failure_set[0]] += 1
            continue
        normalized_event_id = _strict_decimal_id(projected["id"])
        if normalized_event_id is None or repo_id is None:
            exclusions["common_schema"] += 1
            continue
        source_file = manifest.file_for(split).filename
        eligible.append(
            SourceEvent(
                split=split,
                source_file=source_file,
                source_sha256=manifest.file_for(split).sha256,
                source_line=source_line,
                repo_id=repo_id,
                event_id=normalized_event_id,
                event_type=projected["type"],
                action=projected["payload"]["action"],
                payload=projected,
                input_sha256=input_sha256(projected),
            )
        )
    return SourceScan(
        split=split,
        line_count=manifest.file_for(split).jsonl_lines,
        repo_ids=frozenset(repo_ids),
        eligible=tuple(eligible),
        exclusion_counts=tuple(sorted(exclusions.items())),
    )


def _scan_signature(bundle: SourceBundle) -> tuple[Any, ...]:
    return tuple(
        (
            scan.split,
            scan.line_count,
            tuple(sorted(scan.repo_ids, key=int)),
            scan.exclusion_counts,
            tuple(
                (
                    event.source_line,
                    event.event_id,
                    event.repo_id,
                    event.event_type,
                    event.input_sha256,
                    canonical_json_text(event.payload),
                )
                for event in scan.eligible
            ),
        )
        for scan in bundle.scans
    ) + (tuple(sorted(bundle.shared_repo_ids, key=int)),)


def scan_sources(
    manifest: SourceManifest,
    oracle_fn: Callable[[Mapping[str, Any]], Any],
    splits: Sequence[str] = SPLITS,
) -> SourceBundle:
    requested = tuple(splits)
    if not requested or len(set(requested)) != len(requested):
        raise ProtocolError("invalid source scan split set")
    seen: dict[str, tuple[str, int]] = {}
    raw_scans = tuple(
        scan_source_split(manifest, split, oracle_fn, seen) for split in requested
    )
    occurrences: defaultdict[str, set[str]] = defaultdict(set)
    for scan in raw_scans:
        for repo_id in scan.repo_ids:
            occurrences[repo_id].add(scan.split)
    shared = frozenset(
        repo_id for repo_id, present_splits in occurrences.items() if len(present_splits) > 1
    )
    filtered: list[SourceScan] = []
    for scan in raw_scans:
        exclusions = Counter(dict(scan.exclusion_counts))
        kept = []
        for event in scan.eligible:
            if event.repo_id in shared:
                exclusions["cross_split_repository"] += 1
            else:
                kept.append(event)
        filtered.append(
            replace(
                scan,
                eligible=tuple(kept),
                exclusion_counts=tuple(sorted(exclusions.items())),
            )
        )
    return SourceBundle(manifest, tuple(filtered), shared)


@dataclass(frozen=True)
class Case:
    split: str
    source_file: str
    source_sha256: str
    source_line: int
    repo_id: str
    event_id: str
    event_type: str
    base_event_id: str
    variant_id: str
    case_kind: str
    truth: int
    oracle_failure_set: tuple[str, ...]
    schema_valid: bool
    payload: dict[str, Any]
    input_sha256: str

    @property
    def repo_id_integer(self) -> int:
        return int(self.repo_id)

    @property
    def event_id_integer(self) -> int:
        return int(self.event_id)


def select_bases(bundle: SourceBundle) -> dict[str, tuple[SourceEvent, ...]]:
    selected_by_split: dict[str, tuple[SourceEvent, ...]] = {}
    seen_base_hashes: set[str] = set()
    for scan in bundle.scans:
        counts: Counter[tuple[str, str]] = Counter()
        selected: list[SourceEvent] = []
        for event in sorted(scan.eligible, key=_selection_sort_key):
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
                raise ProtocolError(
                    f"{scan.split} cannot reach exact {event_type} base quota"
                )
        repo_ids = {event.repo_id for event in selected}
        if len(repo_ids) < 24:
            raise ProtocolError(f"{scan.split} has fewer than 24 selected repositories")
        for event_type in EVENT_TYPES:
            if len({event.repo_id for event in selected if event.event_type == event_type}) < 16:
                raise ProtocolError(f"{scan.split} has fewer than 16 repositories for {event_type}")
        for event in selected:
            if event.input_sha256 in seen_base_hashes:
                raise ProtocolError("duplicate selected base hash")
            seen_base_hashes.add(event.input_sha256)
        selected_by_split[scan.split] = tuple(sorted(selected, key=_selection_sort_key))
    return selected_by_split


def _mutate_payload(base: SourceEvent, variant_id: str) -> dict[str, Any]:
    payload = copy.deepcopy(base.payload)
    event_payload = payload["payload"]
    if variant_id == "clean":
        return payload
    if variant_id == "S1-missing-resource":
        resource = "issue" if base.event_type == "IssuesEvent" else "pull_request"
        del event_payload[resource]
        return payload
    if variant_id == "I1-wrong-repository":
        if base.event_type == "IssuesEvent":
            event_payload["issue"]["repository_url"] = SENTINEL_REPOSITORY_URL
        else:
            number = event_payload["number"]
            event_payload["pull_request"]["url"] = SENTINEL_REPOSITORY_URL + f"/pulls/{number}"
        return payload
    if variant_id == "T1-status-contradiction":
        resource = event_payload["issue"] if base.event_type == "IssuesEvent" else event_payload["pull_request"]
        resource["state"] = "closed" if base.action in ("opened", "reopened") else "open"
        return payload
    raise ProtocolError(f"unknown mutation variant: {variant_id}")


def _diff_paths(left: Any, right: Any, path: tuple[Any, ...] = ()) -> set[tuple[Any, ...]]:
    missing = object()
    if type(left) is not type(right):
        return {path}
    if type(left) is dict:
        differences: set[tuple[Any, ...]] = set()
        for key in set(left) | set(right):
            differences.update(
                _diff_paths(left.get(key, missing), right.get(key, missing), path + (key,))
            )
        return differences
    if type(left) is list:
        differences = set()
        if len(left) != len(right):
            differences.add(path + ("length",))
        for index in range(min(len(left), len(right))):
            differences.update(_diff_paths(left[index], right[index], path + (index,)))
        return differences
    return set() if left == right else {path}


def mutation_diff_paths(base: Mapping[str, Any], mutated: Mapping[str, Any]) -> set[tuple[Any, ...]]:
    return _diff_paths(base, mutated)


def build_cases(
    selected_by_split: Mapping[str, Sequence[SourceEvent]],
    oracle_fn: Callable[[Mapping[str, Any]], Any],
) -> dict[str, tuple[Case, ...]]:
    cases: dict[str, tuple[Case, ...]] = {}
    for split in (name for name in SPLITS if name in selected_by_split):
        produced: list[Case] = []
        for base in sorted(selected_by_split[split], key=_selection_sort_key):
            for variant_id in VARIANTS:
                candidate = _mutate_payload(base, variant_id)
                oracle_result = oracle_fn(candidate)
                failure_set = tuple(getattr(oracle_result, "oracle_failure_set", ()))
                produced.append(
                    Case(
                        split=split,
                        source_file=base.source_file,
                        source_sha256=base.source_sha256,
                        source_line=base.source_line,
                        repo_id=base.repo_id,
                        event_id=base.event_id,
                        event_type=base.event_type,
                        base_event_id=base.event_id,
                        variant_id=variant_id,
                        case_kind=VARIANT_KIND[variant_id],
                        truth=int(getattr(oracle_result, "truth", 0)),
                        oracle_failure_set=failure_set,
                        schema_valid=bool(getattr(oracle_result, "schema_valid", False)),
                        payload=candidate,
                        input_sha256=input_sha256(candidate),
                    )
                )
        cases[split] = tuple(produced)
    validate_case_construction(cases)
    return cases


def _case_sort_key(case: Case) -> tuple[Any, ...]:
    return (
        EVENT_TYPE_RANK[case.event_type],
        case.repo_id_integer,
        case.event_id_integer,
        case.source_file,
        case.source_line,
        VARIANT_RANK[case.variant_id],
    )


def validate_case_construction(cases_by_split: Mapping[str, Sequence[Case]]) -> None:
    expected_failures = {
        "clean": (),
        "S1-missing-resource": ("schema",),
        "I1-wrong-repository": ("identity",),
        "T1-status-contradiction": ("state",),
    }
    expected_paths = {
        "clean": set(),
        "S1-missing-resource": {
            ("payload", "issue"),
        },
        "I1-wrong-repository": None,
        "T1-status-contradiction": None,
    }
    seen: set[tuple[str, str, str]] = set()
    for split, cases in cases_by_split.items():
        by_base: defaultdict[tuple[str, str], list[Case]] = defaultdict(list)
        for case in cases:
            key = (split, case.event_id, case.variant_id)
            if key in seen:
                raise ProtocolError("duplicate constructed case")
            seen.add(key)
            by_base[(case.event_id, case.event_type)].append(case)
        for (_, event_type), cluster in by_base.items():
            if len(cluster) != CASES_PER_BASE:
                raise ProtocolError("base event does not have four variants")
            variants = {case.variant_id for case in cluster}
            if variants != set(VARIANTS):
                raise ProtocolError("variant inventory mismatch")
            clean = next(case for case in cluster if case.variant_id == "clean")
            for case in cluster:
                if tuple(case.oracle_failure_set) != expected_failures[case.variant_id]:
                    raise ProtocolError("oracle mutation known-answer drift")
                if case.truth != int(not case.oracle_failure_set):
                    raise ProtocolError("oracle truth drift")
                if case.variant_id in ("clean", "I1-wrong-repository", "T1-status-contradiction"):
                    if not case.schema_valid:
                        raise ProtocolError("schema-valid mutation became schema-invalid")
                else:
                    if case.schema_valid:
                        raise ProtocolError("missing-resource mutation remained schema-valid")
                if case.variant_id == "clean":
                    expected = set()
                elif case.variant_id == "S1-missing-resource":
                    expected = {("payload", "issue")} if event_type == "IssuesEvent" else {
                        ("payload", "pull_request")
                    }
                elif case.variant_id == "I1-wrong-repository":
                    expected = (
                        {("payload", "issue", "repository_url")}
                        if event_type == "IssuesEvent"
                        else {("payload", "pull_request", "url")}
                    )
                else:
                    expected = (
                        {("payload", "issue", "state")}
                        if event_type == "IssuesEvent"
                        else {("payload", "pull_request", "state")}
                    )
                if mutation_diff_paths(clean.payload, case.payload) != expected:
                    raise ProtocolError("mutation footprint drift")


def case_key(case: Case) -> tuple[str, str, str]:
    return case.split, case.event_id, case.variant_id


def _ordered_cases(cases_by_split: Mapping[str, Sequence[Case]]) -> tuple[Case, ...]:
    result: list[Case] = []
    for split in SPLITS:
        result.extend(sorted(cases_by_split.get(split, ()), key=_case_sort_key))
    return tuple(result)


def _oracle_observation(result: Any) -> dict[str, Any]:
    return {
        "schema_valid": bool(getattr(result, "schema_valid", False)),
        "truth": int(getattr(result, "truth", 0)),
        "oracle_failure_set": list(getattr(result, "oracle_failure_set", ())),
    }


def _oracle_signature(
    oracle_fn: Callable[[Mapping[str, Any]], Any],
    payloads: Sequence[Mapping[str, Any]],
) -> str:
    return sha256_hex(
        canonical_json_bytes([_oracle_observation(oracle_fn(payload)) for payload in payloads])
    )


def _method_signature(
    payloads: Sequence[Mapping[str, Any]],
    method: str,
) -> str:
    return sha256_hex(
        canonical_json_bytes(
            [
                {
                    "decision": result.decision,
                    "raw_score": result.raw_score,
                    "failed_families": list(result.failed_families),
                    "schema_valid": result.schema_valid,
                }
                for result in (validate_method(payload, method) for payload in payloads)
            ]
        )
    )


def run_independence_gates(
    cases_by_split: Mapping[str, Sequence[Case]],
    oracle_fn: Callable[[Mapping[str, Any]], Any],
) -> dict[str, Any]:
    """Run the locked source, perturbation, and metadata-independence probes."""

    cases = _ordered_cases(cases_by_split)
    if not cases:
        raise ProtocolError("independence gate has no probe cases")
    oracle_probe_cases = tuple(
        case for case in cases if case.variant_id == "I1-wrong-repository"
    )
    if not oracle_probe_cases:
        raise ProtocolError("independence gate has no identity perturbation cases")
    payloads = tuple(case.payload for case in cases)
    oracle_probe_payloads = tuple(case.payload for case in oracle_probe_cases)

    source_evidence = _inspect_independence_sources(oracle_fn)
    metadata_evidence = _run_metadata_tripwire(payloads[0])
    oracle_before = _oracle_signature(oracle_fn, payloads)
    method_before = _method_signature(payloads, "M1")

    original_checks = dict(M1_CHECKS)

    def _always_true(_payload: Mapping[str, Any]) -> bool:
        return True

    try:
        M1_CHECKS["identity"] = _always_true
        method_after_method_perturbation = _method_signature(payloads, "M1")
        oracle_after_method_perturbation = _oracle_signature(oracle_fn, payloads)
    finally:
        M1_CHECKS.clear()
        M1_CHECKS.update(original_checks)
    method_perturbation = {
        "status": "pass",
        "perturbed": "M1_CHECKS.identity=always_true",
        "payload_count": len(payloads),
        "method_signature_before": method_before,
        "method_signature_after": method_after_method_perturbation,
        "oracle_signature_before": oracle_before,
        "oracle_signature_after": oracle_after_method_perturbation,
        "method_changed": method_after_method_perturbation != method_before,
        "oracle_unchanged": oracle_after_method_perturbation == oracle_before,
    }
    if not method_perturbation["method_changed"]:
        raise ProtocolError("method predicate perturbation did not change method output")
    if not method_perturbation["oracle_unchanged"]:
        raise ProtocolError("method predicate perturbation changed oracle output")

    oracle_module = inspect.getmodule(oracle_fn)
    if oracle_module is None:
        raise ProtocolError("oracle relation perturbation module is unavailable")
    original_identity_relation = getattr(oracle_module, "_identity_relation", None)
    if not callable(original_identity_relation):
        raise ProtocolError("oracle identity relation is unavailable")

    try:
        setattr(oracle_module, "_identity_relation", _always_true)
        oracle_after_oracle_perturbation = _oracle_signature(oracle_fn, payloads)
        method_after_oracle_perturbation = _method_signature(payloads, "M1")
    finally:
        setattr(oracle_module, "_identity_relation", original_identity_relation)
    oracle_perturbation = {
        "status": "pass",
        "perturbed": "oracle._identity_relation=always_true",
        "payload_count": len(oracle_probe_payloads),
        "method_signature_before": method_before,
        "method_signature_after": method_after_oracle_perturbation,
        "oracle_signature_before": oracle_before,
        "oracle_signature_after": oracle_after_oracle_perturbation,
        "method_unchanged": method_after_oracle_perturbation == method_before,
        "oracle_changed": oracle_after_oracle_perturbation != oracle_before,
        "identity_probe_case_count": len(oracle_probe_payloads),
    }
    if not oracle_perturbation["method_unchanged"]:
        raise ProtocolError("oracle relation perturbation changed method output")
    if not oracle_perturbation["oracle_changed"]:
        raise ProtocolError("oracle relation perturbation did not change oracle output")

    return {
        "status": "pass",
        "source_inspection": source_evidence,
        "method_predicate_perturbation": method_perturbation,
        "oracle_relation_perturbation": oracle_perturbation,
        "validator_metadata_tripwire": metadata_evidence,
    }


def validate_independence_evidence(evidence: Any) -> None:
    if not isinstance(evidence, Mapping) or evidence.get("status") != "pass":
        raise ProtocolError("oracle-independence evidence is missing or failed")
    required = (
        "source_inspection",
        "method_predicate_perturbation",
        "oracle_relation_perturbation",
        "validator_metadata_tripwire",
    )
    if any(not isinstance(evidence.get(name), Mapping) for name in required):
        raise ProtocolError("oracle-independence evidence is incomplete")
    source = evidence["source_inspection"]
    if source.get("status") != "pass" or source.get("oracle_method_references"):
        raise ProtocolError("oracle source-independence evidence is incomplete")
    if source.get("validator_metadata_references"):
        raise ProtocolError("validator metadata-independence evidence is incomplete")
    method = evidence["method_predicate_perturbation"]
    if (
        method.get("status") != "pass"
        or method.get("method_changed") is not True
        or method.get("oracle_unchanged") is not True
    ):
        raise ProtocolError("method perturbation evidence is incomplete")
    oracle = evidence["oracle_relation_perturbation"]
    if (
        oracle.get("status") != "pass"
        or oracle.get("method_unchanged") is not True
        or oracle.get("oracle_changed") is not True
    ):
        raise ProtocolError("oracle perturbation evidence is incomplete")
    metadata = evidence["validator_metadata_tripwire"]
    if metadata.get("status") != "pass" or not metadata.get("methods_checked"):
        raise ProtocolError("metadata tripwire evidence is incomplete")
    for section, fields in (
        (source, ("oracle_source_sha256", "validator_source_sha256")),
        (
            method,
            (
                "method_signature_before",
                "method_signature_after",
                "oracle_signature_before",
                "oracle_signature_after",
            ),
        ),
        (
            oracle,
            (
                "method_signature_before",
                "method_signature_after",
                "oracle_signature_before",
                "oracle_signature_after",
            ),
        ),
    ):
        for field in fields:
            if not isinstance(section.get(field), str) or re.fullmatch(
                r"[0-9a-f]{64}", section[field]
            ) is None:
                raise ProtocolError("oracle-independence evidence hash is malformed")
    for section in (method, oracle, metadata):
        if type(section.get("payload_count")) is not int or section["payload_count"] <= 0:
            raise ProtocolError("oracle-independence evidence count is malformed")


def evaluate_cases(cases: Sequence[Case], method: str) -> list[dict[str, Any]]:
    if method not in METHODS:
        raise ProtocolError(f"unknown method: {method}")
    rows: list[dict[str, Any]] = []
    for case in sorted(cases, key=_case_sort_key):
        result = validate_method(case.payload, method)
        rows.append(
            {
                "split": case.split,
                "source_file": case.source_file,
                "source_line": case.source_line,
                "repo_id": case.repo_id,
                "event_id": case.event_id,
                "event_type": case.event_type,
                "variant_id": case.variant_id,
                "case_kind": case.case_kind,
                "case_key": case_key(case),
                "truth": case.truth,
                "input_sha256": case.input_sha256,
                "method": method,
                "raw_score": result.raw_score,
                "decision": result.decision,
            }
        )
    return rows


def evaluate_all_methods(cases_by_split: Mapping[str, Sequence[Case]]) -> tuple[dict[str, Any], ...]:
    all_cases = _ordered_cases(cases_by_split)
    rows: list[dict[str, Any]] = []
    for method in METHODS:
        rows.extend(evaluate_cases(all_cases, method))
    return tuple(rows)


@dataclass(frozen=True)
class CalibrationLookup:
    method: str
    entries: tuple[tuple[int, int, int, Fraction], ...]
    global_p_valid: Fraction

    def lookup(self, raw_score: int) -> Fraction:
        for score, _positive, _count, probability in self.entries:
            if score == raw_score:
                return probability
        return self.global_p_valid

    def record(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "entries": [
                {
                    "raw_score": score,
                    "positive_count": positive,
                    "count": count,
                    "p_valid": probability,
                }
                for score, positive, count, probability in self.entries
            ],
            "global_p_valid": self.global_p_valid,
        }

    def serialized(self) -> bytes:
        return canonical_jsonl_bytes(self.record())

    def sha256(self) -> str:
        return sha256_hex(self.serialized())


def fit_calibration_lookup(
    method: str,
    rows: Sequence[Mapping[str, Any]],
) -> CalibrationLookup:
    if method not in CALIBRATED_METHODS:
        raise ProtocolError("only calibrated methods may fit a lookup")
    relevant = [row for row in rows if row.get("method") == method]
    if not relevant or any(row.get("split") != "calibration" for row in relevant):
        raise ProtocolError("calibration lookup received a non-calibration row")
    keys = [row.get("case_key") for row in relevant]
    if any(key is None for key in keys) or len(set(keys)) != len(keys):
        raise ProtocolError("duplicate calibration case")
    counts: Counter[int] = Counter()
    positives: Counter[int] = Counter()
    for row in relevant:
        score = row.get("raw_score")
        truth = row.get("truth")
        if type(score) is not int or score < 0 or truth not in (0, 1):
            raise ProtocolError("malformed calibration row")
        counts[score] += 1
        positives[score] += int(truth)
    total = sum(counts.values())
    positive_total = sum(positives.values())
    entries = tuple(
        (
            score,
            positives[score],
            counts[score],
            Fraction(positives[score] + 1, counts[score] + 2),
        )
        for score in sorted(counts)
    )
    return CalibrationLookup(
        method=method,
        entries=entries,
        global_p_valid=Fraction(positive_total + 1, total + 2),
    )


def fit_all_calibrations(rows: Sequence[Mapping[str, Any]]) -> tuple[CalibrationLookup, ...]:
    return tuple(fit_calibration_lookup(method, rows) for method in CALIBRATED_METHODS)


def build_prediction_rows(
    run_id: str,
    cases_by_split: Mapping[str, Sequence[Case]],
    raw_rows: Sequence[Mapping[str, Any]],
    lookups: Sequence[CalibrationLookup],
    source_manifest_sha256: str,
) -> tuple[dict[str, Any], ...]:
    raw_map = {
        (row["method"], row["case_key"]): row
        for row in raw_rows
    }
    lookup_map = {lookup.method: lookup for lookup in lookups}
    lookup_hashes = {lookup.method: lookup.sha256() for lookup in lookups}
    rows: list[dict[str, Any]] = []
    for case in _ordered_cases(cases_by_split):
        for method in METHODS:
            raw = raw_map.get((method, case_key(case)))
            if raw is None:
                raise ProtocolError("missing raw score for prediction")
            if method == "M1-no-calibration":
                probability = Fraction(int(raw["decision"]), 1)
                lookup_hash = NO_CALIBRATION_MARKER_SHA256
            else:
                probability = lookup_map[method].lookup(raw["raw_score"])
                lookup_hash = lookup_hashes[method]
            rows.append(
                {
                    "protocol_id": PROTOCOL_VERSION,
                    "run_id": run_id,
                    "source_file": case.source_file,
                    "source_sha256": case.source_sha256,
                    "source_line": case.source_line,
                    "split": case.split,
                    "repo_id": case.repo_id,
                    "event_id": case.event_id,
                    "event_type": case.event_type,
                    "base_event_id": case.base_event_id,
                    "variant_id": case.variant_id,
                    "case_kind": case.case_kind,
                    "truth": case.truth,
                    "oracle_failure_set": list(case.oracle_failure_set),
                    "schema_valid": case.schema_valid,
                    "method": method,
                    "decision": bool(raw["decision"]),
                    "raw_score": raw["raw_score"],
                    "p_valid": probability,
                    "input_sha256": case.input_sha256,
                    "source_manifest_sha256": source_manifest_sha256,
                    "calibration_lookup_sha256": lookup_hash,
                    "status": "valid",
                }
            )
    rows.sort(
        key=lambda row: (
            SPLIT_RANK[row["split"]],
            EVENT_TYPE_RANK[row["event_type"]],
            int(row["repo_id"]),
            int(row["event_id"]),
            VARIANT_RANK[row["variant_id"]],
            METHOD_RANK[row["method"]],
        )
    )
    return tuple(rows)


def _probability_fraction(value: Any) -> Fraction:
    if isinstance(value, Fraction):
        result = value
    elif isinstance(value, (int, float, Decimal, JsonNumber)) and type(value) is not bool:
        result = _as_fraction(value)
    elif type(value) is str:
        result = Fraction(value)
    else:
        raise ProtocolError("invalid probability")
    if result < 0 or result > 1:
        raise ProtocolError("probability outside [0,1]")
    return result


def _empty_stats() -> dict[str, Any]:
    return {
        "support": 0,
        "positive_count": 0,
        "negative_count": 0,
        "tp": 0,
        "tn": 0,
        "fp": 0,
        "fn": 0,
        "brier_numerator": Fraction(0),
        "bin_counts": [0] * 10,
        "bin_probability_sums": [Fraction(0)] * 10,
        "bin_truth_sums": [0] * 10,
    }


def _bin_for_probability(probability: Fraction) -> int:
    if probability == 1:
        return 9
    index = int(probability * 10)
    return max(0, min(9, index))


def _add_prediction_to_stats(stats: dict[str, Any], row: Mapping[str, Any]) -> None:
    truth = row.get("truth")
    decision = row.get("decision")
    if truth not in (0, 1) or type(decision) is not bool:
        raise ProtocolError("malformed prediction classification")
    probability = _probability_fraction(row.get("p_valid"))
    stats["support"] += 1
    if truth:
        stats["positive_count"] += 1
        if decision:
            stats["tp"] += 1
        else:
            stats["fn"] += 1
    else:
        stats["negative_count"] += 1
        if decision:
            stats["fp"] += 1
        else:
            stats["tn"] += 1
    stats["brier_numerator"] += (probability - truth) ** 2
    index = _bin_for_probability(probability)
    stats["bin_counts"][index] += 1
    stats["bin_probability_sums"][index] += probability
    stats["bin_truth_sums"][index] += truth


def _merge_stats(target: dict[str, Any], source: Mapping[str, Any]) -> None:
    for field in ("support", "positive_count", "negative_count", "tp", "tn", "fp", "fn"):
        target[field] += source[field]
    target["brier_numerator"] += source["brier_numerator"]
    for index in range(10):
        target["bin_counts"][index] += source["bin_counts"][index]
        target["bin_probability_sums"][index] += source["bin_probability_sums"][index]
        target["bin_truth_sums"][index] += source["bin_truth_sums"][index]


def _safe_rate(numerator: int, denominator: int) -> Fraction | None:
    return Fraction(numerator, denominator) if denominator else None


def _metrics_from_stats(stats: Mapping[str, Any]) -> dict[str, Any]:
    positive_denominator = stats["tp"] + stats["fn"]
    negative_denominator = stats["tn"] + stats["fp"]
    sensitivity = _safe_rate(stats["tp"], positive_denominator)
    specificity = _safe_rate(stats["tn"], negative_denominator)
    balanced_accuracy = (
        (sensitivity + specificity) / 2
        if sensitivity is not None and specificity is not None
        else None
    )
    fpr = _safe_rate(stats["fp"], negative_denominator)
    fnr = _safe_rate(stats["fn"], positive_denominator)
    support = stats["support"]
    brier = stats["brier_numerator"] / support if support else None
    ece_numerator = Fraction(0)
    if support:
        for count, probability_sum, truth_sum in zip(
            stats["bin_counts"],
            stats["bin_probability_sums"],
            stats["bin_truth_sums"],
        ):
            if count:
                ece_numerator += abs(probability_sum / count - Fraction(truth_sum, count)) * count
    ece = ece_numerator / support if support else None
    return {
        "support": support,
        "positive_count": stats["positive_count"],
        "negative_count": stats["negative_count"],
        "tp": stats["tp"],
        "tn": stats["tn"],
        "fp": stats["fp"],
        "fn": stats["fn"],
        "balanced_accuracy": balanced_accuracy,
        "fpr": fpr,
        "fnr": fnr,
        "brier": brier,
        "ece": ece,
    }


def subgroup_matches(row: Mapping[str, Any], subgroup: str) -> bool:
    if subgroup == "overall":
        return True
    if subgroup == "type:IssuesEvent":
        return row.get("event_type") == "IssuesEvent"
    if subgroup == "type:PullRequestEvent":
        return row.get("event_type") == "PullRequestEvent"
    raise ProtocolError(f"unknown subgroup: {subgroup}")


def compute_metrics(
    rows: Sequence[Mapping[str, Any]],
    *,
    method: str | None = None,
    split: str | None = None,
    subgroup: str = "overall",
) -> dict[str, Any]:
    stats = _empty_stats()
    for row in rows:
        if method is not None and row.get("method") != method:
            continue
        if split is not None and row.get("split") != split:
            continue
        if subgroup_matches(row, subgroup):
            _add_prediction_to_stats(stats, row)
    return _metrics_from_stats(stats)


def pair_deltas(rows: Sequence[Mapping[str, Any]], split: str, subgroup: str) -> dict[str, Fraction | None]:
    b0 = compute_metrics(rows, method="B0", split=split, subgroup=subgroup)
    m1 = compute_metrics(rows, method="M1", split=split, subgroup=subgroup)
    return {
        metric: (
            m1[metric] - b0[metric]
            if m1[metric] is not None and b0[metric] is not None
            else None
        )
        for metric in METRICS
    }


@dataclass(frozen=True)
class BootstrapResult:
    replicate_count: int
    cluster_ids: tuple[str, ...]
    delta_values: tuple[tuple[str, str, tuple[Fraction | None, ...]], ...]
    intervals: tuple[dict[str, Any], ...]

    def delta_series(self, subgroup: str, metric: str) -> tuple[Fraction | None, ...]:
        for stored_subgroup, stored_metric, values in self.delta_values:
            if stored_subgroup == subgroup and stored_metric == metric:
                return values
        raise KeyError((subgroup, metric))

    def interval(self, subgroup: str, metric: str) -> dict[str, Any]:
        for row in self.intervals:
            if row["subgroup"] == subgroup and row["metric"] == metric:
                return row
        raise KeyError((subgroup, metric))


def bootstrap_index(subgroup: str, metric: str, replicate: int, position: int, cluster_count: int) -> int:
    if subgroup not in SUBGROUPS or metric not in METRICS:
        raise ProtocolError("unknown bootstrap block")
    if replicate < 0 or position < 0 or cluster_count <= 0:
        raise ProtocolError("invalid bootstrap index arguments")
    material = f"{PROTOCOL_VERSION}|bootstrap|{subgroup}|{metric}|{replicate}|{position}"
    return int(hashlib.sha256(material.encode("utf-8")).hexdigest(), 16) % cluster_count


def percentile(values: Sequence[Fraction], probability: Fraction | float) -> Fraction:
    if not values:
        raise ProtocolError("percentile requires a nonempty sequence")
    sorted_values = sorted(values)
    q = _as_fraction(probability)
    if q < 0 or q > 1:
        raise ProtocolError("percentile probability outside [0,1]")
    h = Fraction(len(sorted_values) - 1) * q
    lower_index = h.numerator // h.denominator
    if h.denominator == 1:
        return sorted_values[lower_index]
    upper_index = lower_index + 1
    weight = h - lower_index
    return (1 - weight) * sorted_values[lower_index] + weight * sorted_values[upper_index]


def _cluster_stats(
    prediction_rows: Sequence[Mapping[str, Any]],
) -> tuple[tuple[str, ...], dict[tuple[str, str, str], dict[str, Any]]]:
    cluster_ids = tuple(
        sorted(
            {str(row["repo_id"]) for row in prediction_rows if row.get("split") == "confirmatory"},
            key=int,
        )
    )
    if not cluster_ids:
        raise ProtocolError("confirmatory bootstrap has no repositories")
    aggregate: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in prediction_rows:
        if row.get("split") != "confirmatory" or row.get("method") not in PRIMARY_METHODS:
            continue
        repo_id = str(row["repo_id"])
        method = str(row["method"])
        for subgroup in SUBGROUPS:
            if subgroup_matches(row, subgroup):
                key = (repo_id, method, subgroup)
                stats = aggregate.setdefault(key, _empty_stats())
                _add_prediction_to_stats(stats, row)
    return cluster_ids, aggregate


def bootstrap_confirmatory(
    prediction_rows: Sequence[Mapping[str, Any]],
    *,
    replicates: int = BOOTSTRAP_REPLICATES,
    enforce_minimum: bool = True,
) -> BootstrapResult:
    if replicates <= 0:
        raise ProtocolError("bootstrap replicate count must be positive")
    cluster_ids, cluster_stats = _cluster_stats(prediction_rows)
    if enforce_minimum and len(cluster_ids) < 24:
        raise ProtocolError("confirmatory repository cluster minimum is not met")
    all_series: list[tuple[str, str, tuple[Fraction | None, ...]]] = []
    interval_rows: list[dict[str, Any]] = []
    for subgroup in SUBGROUPS:
        for metric in METRICS:
            values: list[Fraction | None] = []
            for replicate in range(replicates):
                totals = {method: _empty_stats() for method in PRIMARY_METHODS}
                for position in range(len(cluster_ids)):
                    index = bootstrap_index(
                        subgroup, metric, replicate, position, len(cluster_ids)
                    )
                    repo_id = cluster_ids[index]
                    for method in PRIMARY_METHODS:
                        source = cluster_stats.get((repo_id, method, subgroup))
                        if source is not None:
                            _merge_stats(totals[method], source)
                method_a = _metrics_from_stats(totals["M1"])[metric]
                method_b = _metrics_from_stats(totals["B0"])[metric]
                values.append(
                    method_a - method_b
                    if method_a is not None and method_b is not None
                    else None
                )
            usable = [value for value in values if value is not None]
            if not usable:
                lower = upper = None
                status = "undefined"
            else:
                lower = percentile(usable, Fraction(1, 40))
                upper = percentile(usable, Fraction(39, 40))
                if len(usable) != replicates:
                    status = "partial"
                elif lower == upper:
                    status = "degenerate"
                else:
                    status = "valid"
            all_series.append((subgroup, metric, tuple(values)))
            interval_rows.append(
                {
                    "subgroup": subgroup,
                    "metric": metric,
                    "method_pair": "M1-B0",
                    "lower": lower,
                    "upper": upper,
                    "usable_replicates": len(usable),
                    "status": status,
                }
            )
    return BootstrapResult(
        replicate_count=replicates,
        cluster_ids=cluster_ids,
        delta_values=tuple(all_series),
        intervals=tuple(interval_rows),
    )


def build_bootstrap_rows(result: BootstrapResult, run_id: str) -> tuple[dict[str, Any], ...]:
    rows: list[dict[str, Any]] = []
    for replicate in range(result.replicate_count):
        for subgroup in SUBGROUPS:
            for metric in METRICS:
                value = result.delta_series(subgroup, metric)[replicate]
                rows.append(
                    {
                        "run_id": run_id,
                        "replicate": replicate,
                        "subgroup": subgroup,
                        "metric": metric,
                        "method_pair": "M1-B0",
                        "delta": value,
                        "status": "available" if value is not None else "undefined",
                    }
                )
    return tuple(rows)


def expected_bootstrap_row_count(result: BootstrapResult | None = None) -> int:
    return (result.replicate_count if result is not None else BOOTSTRAP_REPLICATES) * len(SUBGROUPS) * len(METRICS)


def _metric_row_base(
    run_id: str,
    source_manifest_sha256: str,
    split: str,
    subgroup: str,
) -> dict[str, Any]:
    return {
        "row_kind": "method",
        "run_id": run_id,
        "protocol_id": PROTOCOL_VERSION,
        "source_manifest_sha256": source_manifest_sha256,
        "split": split,
        "subgroup": subgroup,
        "method": None,
        "method_pair": None,
        "variant_scope": "all",
        "support": None,
        "positive_count": None,
        "negative_count": None,
        "tp": None,
        "tn": None,
        "fp": None,
        "fn": None,
        "balanced_accuracy": None,
        "fpr": None,
        "fnr": None,
        "brier": None,
        "ece": None,
        "delta_ba_ci_lower": None,
        "delta_ba_ci_upper": None,
        "delta_fpr_ci_lower": None,
        "delta_fpr_ci_upper": None,
        "delta_fnr_ci_lower": None,
        "delta_fnr_ci_upper": None,
        "delta_brier_ci_lower": None,
        "delta_brier_ci_upper": None,
        "delta_ece_ci_lower": None,
        "delta_ece_ci_upper": None,
        "interval_status": "descriptive-only",
    }


def build_metric_rows(
    prediction_rows: Sequence[Mapping[str, Any]],
    *,
    run_id: str,
    source_manifest_sha256: str,
    bootstrap: BootstrapResult | None = None,
) -> tuple[dict[str, Any], ...]:
    result: list[dict[str, Any]] = []
    for split in SPLITS:
        for subgroup in SUBGROUPS:
            for method in METHODS:
                row = _metric_row_base(run_id, source_manifest_sha256, split, subgroup)
                row["method"] = method
                row.update(compute_metrics(prediction_rows, method=method, split=split, subgroup=subgroup))
                result.append(row)
            pair = _metric_row_base(run_id, source_manifest_sha256, split, subgroup)
            pair["row_kind"] = "pair"
            pair["method"] = None
            pair["method_pair"] = "M1-B0"
            pair["interval_status"] = "not-computed"
            if bootstrap is not None and split == "confirmatory":
                interval = {
                    metric: bootstrap.interval(subgroup, metric) for metric in METRICS
                }
                for metric, lower_field, upper_field in (
                    ("balanced_accuracy", "delta_ba_ci_lower", "delta_ba_ci_upper"),
                    ("fpr", "delta_fpr_ci_lower", "delta_fpr_ci_upper"),
                    ("fnr", "delta_fnr_ci_lower", "delta_fnr_ci_upper"),
                    ("brier", "delta_brier_ci_lower", "delta_brier_ci_upper"),
                    ("ece", "delta_ece_ci_lower", "delta_ece_ci_upper"),
                ):
                    pair[lower_field] = interval[metric]["lower"]
                    pair[upper_field] = interval[metric]["upper"]
                statuses = {item["status"] for item in interval.values()}
                pair["interval_status"] = (
                    "valid" if statuses == {"valid"} else
                    "degenerate" if statuses <= {"valid", "degenerate"} and "degenerate" in statuses else
                    "partial" if "partial" in statuses else
                    "undefined"
                )
            result.append(pair)
    return tuple(result)


def csv_value(value: Any) -> str | int:
    if value is None:
        return NA
    if type(value) is bool:
        return "true" if value else "false"
    if isinstance(value, (Fraction, Decimal, float)):
        return decimal_token(value)
    if isinstance(value, (dict, list, tuple)):
        return canonical_json_text(value)
    return value


def serialize_jsonl(rows: Iterable[Mapping[str, Any]]) -> bytes:
    output = io.StringIO(newline="\n")
    for row in rows:
        output.write(canonical_json_text(row))
        output.write("\n")
    return output.getvalue().encode("utf-8")


def serialize_csv(rows: Iterable[Mapping[str, Any]], fields: Sequence[str]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=list(fields),
        extrasaction="raise",
        lineterminator="\n",
    )
    writer.writeheader()
    for row in rows:
        writer.writerow({field: csv_value(row.get(field)) for field in fields})
    return output.getvalue().encode("utf-8")


def _h3_outcome(bootstrap: BootstrapResult, point_deltas: Mapping[str, Mapping[str, Fraction | None]]) -> str:
    required = ("overall", "type:IssuesEvent", "type:PullRequestEvent")
    for subgroup in required:
        if point_deltas[subgroup]["fnr"] is None or point_deltas[subgroup]["fnr"] > 0:
            return "mixed/not supported"
        for metric, comparator in (("balanced_accuracy", lambda value: value > 0), ("fpr", lambda value: value < 0)):
            interval = bootstrap.interval(subgroup, metric)
            if (
                interval["usable_replicates"] != BOOTSTRAP_REPLICATES
                or interval["status"] not in ("valid", "degenerate")
                or interval["lower"] is None and metric == "balanced_accuracy"
                or interval["upper"] is None and metric == "fpr"
            ):
                return "mixed/not supported"
            endpoint = interval["lower"] if metric == "balanced_accuracy" else interval["upper"]
            if not comparator(endpoint):
                return "mixed/not supported"
    return "supported"


def _format_report_value(value: Any) -> str:
    if value is None:
        return NA
    if isinstance(value, (Fraction, Decimal, float, int)) and type(value) is not bool:
        return decimal_token(value)
    return str(value)


def _mutation_summary(
    predictions: Sequence[Mapping[str, Any]],
    method: str,
) -> str:
    pieces: list[str] = []
    for variant in VARIANTS:
        selected = [
            row for row in predictions
            if row["method"] == method and row["variant_id"] == variant
        ]
        accepted = sum(bool(row["decision"]) for row in selected)
        pieces.append(f"{variant}={accepted}/{len(selected)}")
    return ", ".join(pieces)


def _validate_result_exclusion_counts(
    result_markdown: str,
    bundle: SourceBundle,
) -> None:
    scans = {scan.split: scan for scan in bundle.scans}
    if len(scans) != len(bundle.scans) or set(scans) != set(SPLITS):
        raise ProtocolError("result report requires one scan for every source split")
    expected = {split: scans[split].exclusions() for split in SPLITS}
    lines = result_markdown.splitlines()
    if lines.count("exclusion_counts:") != 1 or lines.count("gate_status:") != 1:
        raise ProtocolError("result report exclusion-count section is missing")
    start = lines.index("exclusion_counts:")
    end = lines.index("gate_status:")
    entries = lines[start + 1:end]
    if len(entries) != len(SPLITS):
        raise ProtocolError("result report exclusion-count section is incomplete")
    reported: dict[str, dict[str, int]] = {}
    for expected_split, line in zip(SPLITS, entries):
        prefix = f"  {expected_split}: "
        if not line.startswith(prefix):
            raise ProtocolError("result report exclusion-count split is missing")
        encoded = line[len(prefix):]
        try:
            decoded = strict_json_loads(encoded)
        except (ValueError, json.JSONDecodeError) as error:
            raise ProtocolError("result report exclusion counts are not strict JSON") from error
        if type(decoded) is not dict or canonical_json_text(decoded) != encoded:
            raise ProtocolError("result report exclusion counts are not canonical JSON")
        if any(type(value) is not int or value < 0 for value in decoded.values()):
            raise ProtocolError("result report exclusion count is malformed")
        reported[expected_split] = decoded
    if reported != expected:
        raise ProtocolError("result report exclusion counts are incomplete or incorrect")


def _validate_result_independence_evidence(
    result_markdown: str,
    evidence: Mapping[str, Any],
) -> None:
    validate_independence_evidence(evidence)
    prefix = "oracle_independence_evidence: "
    lines = result_markdown.splitlines()
    matches = [line[len(prefix):] for line in lines if line.startswith(prefix)]
    if len(matches) != 1:
        raise ProtocolError("result report independence evidence is missing")
    encoded = matches[0]
    try:
        reported = strict_json_loads(encoded)
    except (ValueError, json.JSONDecodeError) as error:
        raise ProtocolError("result report independence evidence is not strict JSON") from error
    if type(reported) is not dict or canonical_json_text(reported) != encoded:
        raise ProtocolError("result report independence evidence is not canonical JSON")
    if reported != dict(evidence):
        raise ProtocolError("result report independence evidence does not match pipeline evidence")
    expected_status = f"  method_oracle_independence: {evidence['status']}"
    if lines.count(expected_status) != 1:
        raise ProtocolError("result report independence gate status is missing")


def build_result_markdown(
    run_id: str,
    manifest: SourceManifest,
    bundle: SourceBundle,
    cases_by_split: Mapping[str, Sequence[Case]],
    prediction_rows: Sequence[Mapping[str, Any]],
    metric_rows: Sequence[Mapping[str, Any]],
    bootstrap: BootstrapResult,
    lookup_hashes: Mapping[str, str],
    artifact_hashes: Mapping[str, str],
    independence_evidence: Mapping[str, Any] | None = None,
) -> str:
    if independence_evidence is None:
        raise ProtocolError("result report requires measured independence evidence")
    validate_independence_evidence(independence_evidence)
    point_deltas = {
        subgroup: pair_deltas(
            prediction_rows, "confirmatory", subgroup
        )
        for subgroup in SUBGROUPS
    }
    outcome = _h3_outcome(bootstrap, point_deltas)
    lines = [
        f"# E003-v1 external-transfer validation — {run_id}",
        "",
        "status: valid",
        f"protocol_id: {PROTOCOL_VERSION}",
        f"protocol_path: {PROTOCOL_PATH}",
        f"protocol_commit: {PROTOCOL_COMMIT}",
        f"source_manifest_sha256: {manifest.manifest_sha256}",
        "source_hashes:",
    ]
    for split in SPLITS:
        item = manifest.file_for(split)
        lines.append(f"  {split}: {item.sha256}")
    lines.extend(
        [
            "environment: standard-library Python process; local CPU; network disabled after manifest freeze",
            "selected_counts:",
        ]
    )
    for split in (name for name in SPLITS if name in cases_by_split):
        bases = len(cases_by_split[split]) // CASES_PER_BASE
        repos = len({case.repo_id for case in cases_by_split[split]})
        lines.append(f"  {split}: bases={bases}, cases={len(cases_by_split[split])}, repositories={repos}")
    lines.append("exclusion_counts:")
    for split in SPLITS:
        counts = bundle.scan_for(split).exclusions()
        lines.append(f"  {split}: {canonical_json_text(counts)}")
    lines.extend(
        [
            "gate_status:",
            "  protocol_identity: pass",
            "  source_hashes_and_jsonl: pass",
            "  projection_and_selection_determinism: pass",
            "  schema_oracle_and_mutation_known_answers: pass",
            "  repository_isolation_and_quotas: pass",
            f"  method_oracle_independence: {independence_evidence['status']}",
            "  calibration_isolation: pass",
            "  artifact_schema_and_size: pass",
            "  two_build_determinism: pass",
            "  bootstrap_replicates: pass",
            "calibration_lookup_sha256:",
        ]
    )
    lines.append(
        "oracle_independence_evidence: "
        + canonical_json_text(independence_evidence)
    )
    for method in CALIBRATED_METHODS:
        lines.append(f"  {method}: {lookup_hashes[method]}")
    lines.append(f"  M1-no-calibration: {NO_CALIBRATION_MARKER_SHA256}")
    lines.extend(["primary_confirmatory_M1_minus_B0:"])
    for subgroup in SUBGROUPS:
        deltas = point_deltas[subgroup]
        lines.append(
            f"  {subgroup}: " + ", ".join(
                f"{metric}={_format_report_value(deltas[metric])}" for metric in METRICS
            )
        )
        for metric in METRICS:
            interval = bootstrap.interval(subgroup, metric)
            lines.append(
                f"    {metric}_ci={_format_report_value(interval['lower'])},{_format_report_value(interval['upper'])}; "
                f"usable={interval['usable_replicates']}; status={interval['status']}"
            )
    lines.extend(
        [
            f"H3_outcome: {outcome}",
            "confirmatory_mutation_acceptance:",
        ]
    )
    confirmatory_predictions = [row for row in prediction_rows if row["split"] == "confirmatory"]
    for method in METHODS:
        lines.append(f"  {method}: {_mutation_summary(confirmatory_predictions, method)}")
    lines.extend(
        [
            "artifact_sha256:",
            f"  predictions: {artifact_hashes['predictions']}",
            f"  metrics: {artifact_hashes['metrics']}",
            f"  bootstrap: {artifact_hashes['bootstrap']}",
            "deviations: none",
            "limitations: GH Archive hourly shards, narrow external subset, controlled negatives, finite repository-cluster bootstrap, and shared contract risk; no production, safety, novelty, generalization, or public claim follows.",
            "stopping: one valid confirmatory run and verification of its four artifacts, followed by stop; no retry or post-hoc expansion.",
            "",
        ]
    )
    return "\n".join(lines)


@dataclass(frozen=True)
class DevelopmentCalibrationPreflight:
    manifest_sha256: str
    split_base_counts: tuple[tuple[str, int], ...]
    split_case_counts: tuple[tuple[str, int], ...]
    split_repository_counts: tuple[tuple[str, int], ...]
    exclusion_counts: tuple[tuple[str, tuple[tuple[str, int], ...]], ...]
    calibration_lookup_hashes: tuple[tuple[str, str], ...]
    calibration_lookup_bytes: tuple[tuple[str, bytes], ...]
    source_projection_signature_sha256: str
    raw_row_count: int
    confirmatory_scored: bool = False
    confirmatory_metrics_constructed: bool = False


def _default_oracle() -> Callable[[Mapping[str, Any]], Any]:
    from oracle_e003 import reference_oracle

    return reference_oracle


def _assert_scan_determinism(left: SourceBundle, right: SourceBundle) -> None:
    if _scan_signature(left) != _scan_signature(right):
        raise ProtocolError("source projection determinism gate failed")


def _case_signature(cases_by_split: Mapping[str, Sequence[Case]]) -> tuple[Any, ...]:
    return tuple(
        (
            split,
            tuple(
                (
                    case.source_line,
                    case.event_id,
                    case.variant_id,
                    case.truth,
                    case.oracle_failure_set,
                    case.schema_valid,
                    case.input_sha256,
                    canonical_json_bytes(case.payload),
                )
                for case in cases_by_split.get(split, ())
            ),
        )
        for split in SPLITS
        if split in cases_by_split
    )


def build_development_calibration_preflight(
    manifest_path: Path | str,
    source_root: Path | str | None = None,
    *,
    oracle_fn: Callable[[Mapping[str, Any]], Any] | None = None,
) -> DevelopmentCalibrationPreflight:
    """Prove the two non-holdout quotas and calibration lookup determinism.

    The function has a literal two-split allowlist.  It verifies and opens only
    the development and calibration files, and it does not create predictions,
    metrics, bootstrap rows, or a result document for the future holdout.
    """

    oracle = oracle_fn or _default_oracle()
    manifest = load_manifest(manifest_path, source_root)
    verify_source_hashes(manifest, ("development", "calibration"))
    first = scan_sources(manifest, oracle, ("development", "calibration"))
    second = scan_sources(manifest, oracle, ("development", "calibration"))
    _assert_scan_determinism(first, second)
    selected = select_bases(first)
    cases = build_cases(selected, oracle)
    selected_again = select_bases(second)
    cases_again = build_cases(selected_again, oracle)
    if _case_signature(cases) != _case_signature(cases_again):
        raise ProtocolError("development/calibration case determinism gate failed")
    raw_rows = evaluate_all_methods(cases)
    calibration_rows = tuple(
        row for row in raw_rows if row.get("split") == "calibration"
    )
    lookups = fit_all_calibrations(calibration_rows)
    hashes = tuple((lookup.method, lookup.sha256()) for lookup in lookups)
    artifacts = tuple((lookup.method, lookup.serialized()) for lookup in lookups)
    return DevelopmentCalibrationPreflight(
        manifest_sha256=manifest.manifest_sha256,
        split_base_counts=tuple(
            (split, len(selected[split]) // 2)
            for split in ("development", "calibration")
        ),
        split_case_counts=tuple(
            (split, len(cases[split])) for split in ("development", "calibration")
        ),
        split_repository_counts=tuple(
            (split, len({case.repo_id for case in cases[split]}))
            for split in ("development", "calibration")
        ),
        exclusion_counts=tuple(
            (split, tuple(sorted(first.scan_for(split).exclusions().items())))
            for split in ("development", "calibration")
        ),
        calibration_lookup_hashes=hashes,
        calibration_lookup_bytes=artifacts,
        source_projection_signature_sha256=sha256_hex(canonical_json_bytes(_scan_signature(first))),
        raw_row_count=len(raw_rows),
    )


@dataclass(frozen=True)
class PipelineArtifacts:
    run_id: str
    manifest: SourceManifest
    bundle: SourceBundle
    cases_by_split: Mapping[str, tuple[Case, ...]]
    raw_rows: tuple[dict[str, Any], ...]
    calibration_lookups: tuple[CalibrationLookup, ...]
    prediction_rows: tuple[dict[str, Any], ...]
    metric_rows: tuple[dict[str, Any], ...]
    bootstrap: BootstrapResult
    result_markdown: str
    serialized_outputs: tuple[tuple[str, bytes], ...]
    sanity: Mapping[str, Any]

    def serialized(self, name: str) -> bytes:
        for stored_name, data in self.serialized_outputs:
            if stored_name == name:
                return data
        raise KeyError(name)

    def hashes(self) -> dict[str, str]:
        return {
            name: sha256_hex(data) for name, data in self.serialized_outputs
        } | {
            "manifest": self.manifest.manifest_sha256,
            "calibration_lookups": sha256_hex(
                canonical_json_bytes([lookup.record() for lookup in self.calibration_lookups])
            ),
        }


def validate_pipeline_artifacts(artifacts: PipelineArtifacts) -> None:
    sanity = getattr(artifacts, "sanity", None)
    if not isinstance(sanity, Mapping):
        raise ProtocolError("pipeline sanity evidence is missing")
    independence_evidence = sanity.get(INDEPENDENCE_EVIDENCE_KEY)
    validate_independence_evidence(independence_evidence)
    _validate_result_exclusion_counts(artifacts.result_markdown, artifacts.bundle)
    _validate_result_independence_evidence(
        artifacts.result_markdown,
        independence_evidence,
    )
    if len(artifacts.prediction_rows) != len(SPLITS) * PREDICTIONS_PER_SPLIT:
        raise ProtocolError("prediction row count mismatch")
    if len(artifacts.metric_rows) != EXPECTED_METRIC_ROWS:
        raise ProtocolError("metric row count mismatch")
    bootstrap_rows = build_bootstrap_rows(artifacts.bootstrap, artifacts.run_id)
    if len(bootstrap_rows) != EXPECTED_BOOTSTRAP_ROWS:
        raise ProtocolError("bootstrap row count mismatch")
    for row in artifacts.prediction_rows:
        if tuple(row) != PREDICTION_FIELDS:
            raise ProtocolError("prediction key schema mismatch")
        if not re.fullmatch(r"[0-9a-f]{64}", row["input_sha256"]):
            raise ProtocolError("prediction input hash mismatch")
        if not re.fullmatch(r"[0-9a-f]{64}", row["source_sha256"]):
            raise ProtocolError("prediction source hash mismatch")
        if not re.fullmatch(r"[0-9a-f]{64}", row["source_manifest_sha256"]):
            raise ProtocolError("prediction manifest hash mismatch")
        if not (0 <= _probability_fraction(row["p_valid"]) <= 1):
            raise ProtocolError("prediction probability mismatch")
    serialized = {
        "predictions": serialize_jsonl(artifacts.prediction_rows),
        "metrics": serialize_csv(artifacts.metric_rows, METRIC_FIELDS),
        "bootstrap": serialize_csv(bootstrap_rows, BOOTSTRAP_FIELDS),
        "result": artifacts.result_markdown.encode("utf-8"),
    }
    for name, expected in serialized.items():
        if artifacts.serialized(name) != expected:
            raise ProtocolError(f"serialized artifact mismatch: {name}")
        if len(expected) >= PUBLIC_SIZE_LIMITS[name]:
            raise ProtocolError(f"serialized artifact exceeds size gate: {name}")
    for subgroup in SUBGROUPS:
        for metric in METRICS:
            interval = artifacts.bootstrap.interval(subgroup, metric)
            if interval["usable_replicates"] != BOOTSTRAP_REPLICATES:
                raise ProtocolError("required bootstrap block is partial")
            if interval["status"] not in ("valid", "degenerate"):
                raise ProtocolError("required bootstrap block is undefined")


def build_pipeline(
    run_id: str,
    repository_root: Path | str,
    manifest_path: Path | str,
    source_root: Path | str | None = None,
    *,
    oracle_fn: Callable[[Mapping[str, Any]], Any] | None = None,
    independence_gate_fn: Callable[
        [Mapping[str, Sequence[Case]], Callable[[Mapping[str, Any]], Any]],
        Mapping[str, Any],
    ] | None = None,
) -> PipelineArtifacts:
    """Build the complete future run in memory; this function never writes."""

    if type(run_id) is not str or re.fullmatch(r"e003-[0-9]{8}-[0-9]{3}", run_id) is None:
        raise ProtocolError("invalid E003 run ID")
    # The repository argument is deliberately accepted for the runner's
    # protocol/tree gate; no repository files are read by the core build.
    _ = Path(repository_root).resolve()
    oracle = oracle_fn or _default_oracle()
    manifest = load_manifest(manifest_path, source_root)
    verify_source_hashes(manifest, SPLITS)
    first = scan_sources(manifest, oracle, SPLITS)
    second = scan_sources(manifest, oracle, SPLITS)
    _assert_scan_determinism(first, second)
    selected = select_bases(first)
    cases = build_cases(selected, oracle)
    selected_again = select_bases(second)
    cases_again = build_cases(selected_again, oracle)
    if _case_signature(cases) != _case_signature(cases_again):
        raise ProtocolError("complete case determinism gate failed")
    independence_gate = independence_gate_fn or run_independence_gates
    independence_evidence = independence_gate(cases, oracle)
    validate_independence_evidence(independence_evidence)
    raw_rows = evaluate_all_methods(cases)
    calibration_rows = tuple(
        row for row in raw_rows if row.get("split") == "calibration"
    )
    lookups = fit_all_calibrations(calibration_rows)
    predictions = build_prediction_rows(
        run_id, cases, raw_rows, lookups, manifest.manifest_sha256
    )
    bootstrap = bootstrap_confirmatory(predictions)
    metric_rows = build_metric_rows(
        predictions,
        run_id=run_id,
        source_manifest_sha256=manifest.manifest_sha256,
        bootstrap=bootstrap,
    )
    lookup_hashes = {lookup.method: lookup.sha256() for lookup in lookups}
    preliminary_serialized = {
        "predictions": serialize_jsonl(predictions),
        "metrics": serialize_csv(metric_rows, METRIC_FIELDS),
        "bootstrap": serialize_csv(
            build_bootstrap_rows(bootstrap, run_id), BOOTSTRAP_FIELDS
        ),
    }
    result_markdown = build_result_markdown(
        run_id,
        manifest,
        first,
        cases,
        predictions,
        metric_rows,
        bootstrap,
        lookup_hashes,
        {name: sha256_hex(data) for name, data in preliminary_serialized.items()},
        independence_evidence,
    )
    outputs = tuple(
        (
            name,
            data,
        )
        for name, data in (
            (*preliminary_serialized.items(), ("result", result_markdown.encode("utf-8")))
        )
    )
    artifacts = PipelineArtifacts(
        run_id=run_id,
        manifest=manifest,
        bundle=first,
        cases_by_split={split: tuple(rows) for split, rows in cases.items()},
        raw_rows=tuple(raw_rows),
        calibration_lookups=tuple(lookups),
        prediction_rows=tuple(predictions),
        metric_rows=tuple(metric_rows),
        bootstrap=bootstrap,
        result_markdown=result_markdown,
        serialized_outputs=outputs,
        sanity={
            "source_projection_twice": True,
            "selected_bases": {split: len(rows) for split, rows in selected.items()},
            "cases": {split: len(rows) for split, rows in cases.items()},
            "calibration_only": True,
            "bootstrap_replicates": bootstrap.replicate_count,
            "confirmatory_cases_scored": True,
            INDEPENDENCE_EVIDENCE_KEY: independence_evidence,
        },
    )
    validate_pipeline_artifacts(artifacts)
    return artifacts
