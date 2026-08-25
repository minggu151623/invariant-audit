"""Safe staged CLI for the E002-v1 confirmatory run.

Importing this module performs no repository or output writes.  The default
runner is intentionally strict: protocol identity and tree checks happen
before output-root creation, final files are exclusive, and the result is
published last.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import re
import os
import shutil
import subprocess
import sys
import tempfile
import time
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from types import MappingProxyType
from typing import Any, Callable, Iterator, Mapping, Sequence

import e002


class InvalidRunError(RuntimeError):
    """The invocation was invalid or could not be finalized safely."""


_RECEIPT_TOKEN = object()


class _PublicationReceipt:
    __slots__ = ("path", "identity", "_token")

    def __init__(self, path: Path, identity: tuple[int, int]) -> None:
        self.path = path
        self.identity = identity
        self._token = _RECEIPT_TOKEN


def _repository_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _git(repository_root: Path, *arguments: str) -> str:
    try:
        completed = subprocess.run(
            ["git", *arguments],
            cwd=str(repository_root),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        detail = getattr(error, "stderr", "") or str(error)
        raise InvalidRunError(f"git gate failed: {' '.join(arguments)}: {detail.strip()}") from error
    return completed.stdout


def _final_paths(output_root: Path, run_id: str) -> dict[str, Path]:
    return {
        "predictions": output_root / "data" / "E002-v1-predictions.jsonl",
        "metrics": output_root / "data" / "E002-v1-metrics.csv",
        "bootstrap": output_root / "data" / "E002-v1-bootstrap.csv",
        "result": output_root
        / "experiments"
        / "E002-heterogeneous-specification-stress"
        / "results"
        / f"run-{run_id}.md",
    }


def _protocol_guard(
    repository_root: Path,
    output_root: Path,
    final_paths: Mapping[str, Path],
) -> None:
    if not e002.validate_run_id(final_paths["result"].stem.removeprefix("run-")):
        raise InvalidRunError("invalid run ID")
    status = _git(
        repository_root,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    )
    if status:
        raise InvalidRunError("working tree is not clean")
    protocol_file = repository_root / e002.PROTOCOL_PATH
    if not protocol_file.is_file():
        raise InvalidRunError("locked protocol file is missing")
    try:
        committed_protocol = subprocess.run(
            ["git", "show", f"{e002.PROTOCOL_COMMIT}:{e002.PROTOCOL_PATH}"],
            cwd=str(repository_root),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
    except (OSError, subprocess.CalledProcessError) as error:
        raise InvalidRunError("locked protocol commit/path is unavailable") from error
    working_protocol = protocol_file.read_bytes()
    if committed_protocol != working_protocol:
        raise InvalidRunError("working protocol bytes differ from locked commit")
    blob = _git(
        repository_root,
        "rev-parse",
        f"{e002.PROTOCOL_COMMIT}:{e002.PROTOCOL_PATH}",
    ).strip()
    if blob != e002.PROTOCOL_BLOB:
        raise InvalidRunError("locked protocol blob hash mismatch")
    _git(repository_root, "merge-base", "--is-ancestor", e002.PROTOCOL_COMMIT, "HEAD")
    if output_root.resolve() != repository_root.resolve():
        raise InvalidRunError("confirmatory output root must be repository root")
    if output_root.exists() and not output_root.is_dir():
        raise InvalidRunError("output root is not a directory")
    for label, target in final_paths.items():
        if target.exists():
            raise InvalidRunError(f"output already exists: {label}")


def _write_exclusive(file_path: Path, content: bytes) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(
        file_path,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL,
        0o644,
    )
    try:
        with os.fdopen(descriptor, "wb") as stream:
            descriptor = -1
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        if descriptor != -1:
            os.close(descriptor)


def _file_identity(file_path: Path) -> tuple[int, int] | None:
    try:
        stat_result = file_path.stat()
    except FileNotFoundError:
        return None
    if not file_path.is_file():
        raise InvalidRunError(f"published destination is not a regular file: {file_path}")
    return stat_result.st_dev, stat_result.st_ino


def _publish_exclusive(source: Path, destination: Path) -> _PublicationReceipt:
    # The runner tracks and creates the parent immediately before this
    # primitive is called.  Keeping directory creation out of the primitive
    # prevents a race from creating an untracked parent that cleanup could
    # later mistake for runner-owned state.
    if not destination.parent.is_dir():
        raise InvalidRunError(f"published destination parent is unavailable: {destination.parent}")
    if destination.exists():
        raise InvalidRunError(f"output appeared during run: {destination}")
    try:
        os.link(source, destination)
    except OSError as error:
        raise InvalidRunError(f"exclusive finalization failed: {destination}") from error
    identity = _file_identity(destination)
    if identity is None:
        raise InvalidRunError(f"published destination disappeared: {destination}")
    # The receipt is created immediately after the runner-owned exclusive
    # link.  Staging cleanup removes the still-linked source later.
    return _PublicationReceipt(destination, identity)


def _mkdir_tracked(directory: Path, created: list[Path] | None = None) -> list[Path]:
    owned = created if created is not None else []
    missing: list[Path] = []
    cursor = directory
    while not cursor.exists():
        missing.append(cursor)
        cursor = cursor.parent
    if not cursor.is_dir():
        raise InvalidRunError(f"output parent is not a directory: {cursor}")
    for new_directory in reversed(missing):
        try:
            new_directory.mkdir()
        except FileExistsError:
            if not new_directory.is_dir():
                raise InvalidRunError(f"output parent race is not a directory: {new_directory}")
            continue
        owned.append(new_directory)
    return list(owned)


def _remove_tree_verified(directory: Path) -> None:
    if not directory.exists():
        return
    last_error: OSError | None = None
    for attempt in range(3):
        try:
            shutil.rmtree(directory)
        except FileNotFoundError:
            return
        except OSError as error:
            last_error = error
        if not directory.exists():
            return
        if attempt < 2:
            time.sleep(0.01)
    raise InvalidRunError(f"persistent staging cleanup failure: {directory}") from last_error


def _remove_owned_files_verified(
    owned_files: Sequence[tuple[Path, tuple[int, int]]],
) -> None:
    errors: list[BaseException] = []
    for file_path, expected_identity in reversed(tuple(owned_files)):
        try:
            current_identity = _file_identity(file_path)
            if current_identity is None:
                continue
            if current_identity == expected_identity:
                file_path.unlink()
            else:
                errors.append(InvalidRunError(f"destination ownership changed: {file_path}"))
        except OSError as error:
            errors.append(error)
    leftovers = [
        file_path for file_path, expected_identity in owned_files
        if _file_identity(file_path) == expected_identity
    ]
    if errors or leftovers:
        detail = ", ".join(str(file_path) for file_path in leftovers)
        raise InvalidRunError(f"persistent final cleanup failure: {detail}") from (
            errors[0] if errors else None
        )


def _remove_directories_verified(directories: Sequence[Path]) -> None:
    errors: list[BaseException] = []
    unique_directories = tuple(dict.fromkeys(directories))
    for directory in sorted(
        unique_directories, key=lambda item: len(item.parts), reverse=True
    ):
        try:
            if directory.exists():
                directory.rmdir()
        except OSError as error:
            errors.append(error)
    leftovers = [directory for directory in unique_directories if directory.exists()]
    if errors or leftovers:
        detail = ", ".join(str(directory) for directory in leftovers)
        raise InvalidRunError(f"persistent output-root cleanup failure: {detail}") from (
            errors[0] if errors else None
        )


_D9_OR_NA = re.compile(r"^-?(?:0|[1-9][0-9]*)\.[0-9]{9}$|^NA$")
_NEGATIVE_ZERO_TOKEN = re.compile(
    rb"(?<![0-9A-Za-z_.-])-0\.000000000(?![0-9A-Za-z_.-])"
)
_INT_OR_NA = re.compile(r"^(?:0|[1-9][0-9]*|NA)$")
_HASH = re.compile(r"^[0-9a-f]{64}$")
_RUN_ID = re.compile(r"^e002-[0-9]{8}-[0-9]{3}$")
_LOCKED_DIAGNOSTICS = ("d1", "d2", "d3")
_LOCKED_DIAGNOSTIC_METRIC = {"d1": "fpr", "d2": "fnr", "d3": "fnr"}
_LOCKED_DIAGNOSTIC_PAIR = {
    "d1": "omit-M1",
    "d2": "over-M1",
    "d3": "stale-M1",
}
_LOCKED_BOOTSTRAP_DIAGNOSTIC_PAIR = {
    "d1": "omit-m1",
    "d2": "over-m1",
    "d3": "stale-m1",
}
_LOCKED_METHODS = (
    "B0",
    "M1",
    "M1-omit-conservation",
    "M1-overconstraint",
    "M1-stale-transition",
    "M1-no-semantic",
    "M1-no-state",
    "M1-no-calibration",
)
_LOCKED_SPLITS = ("development", "calibration", "confirmatory")
_LOCKED_TYPES = ("H0", "H1", "H2", "H3", "H4", "H5")
_LOCKED_CASE_KINDS = ("valid", "single", "multi")
_LOCKED_RECIPES = (
    "valid-base", "R1", "C1", "T1", "V1", "M01", "M02", "M03",
    "M04", "M05", "M06", "M07",
)
_LOCKED_FAMILIES = ("schema", "identity", "conservation", "transition", "revision")
_LOCKED_REPLICATES = 10_000
_LOCKED_SUBGROUP_CODES = {
    "o", "h0", "h1", "h2", "h3", "h4", "h5", "v", "s", "m",
}
_LOCKED_METRIC_CODES = {"ba", "fpr", "fnr", "brier", "ece"}
_LOCKED_SUBGROUPS = (
    "overall", "cluster:H0", "cluster:H1", "cluster:H2", "cluster:H3",
    "cluster:H4", "cluster:H5", "case_kind:valid", "case_kind:single",
    "case_kind:multi",
)
_LOCKED_METRICS = ("balanced_accuracy", "fpr", "fnr", "brier", "ece")
_LOCKED_SPLIT_RANK = {name: index for index, name in enumerate(_LOCKED_SPLITS)}
_LOCKED_TYPE_RANK = {name: index for index, name in enumerate(_LOCKED_TYPES)}
_LOCKED_RECIPE_RANK = {name: index for index, name in enumerate(_LOCKED_RECIPES)}
_LOCKED_METHOD_RANK = {name: index for index, name in enumerate(_LOCKED_METHODS)}
_LOCKED_PREDICTION_FIELDS = (
    "run_id", "protocol_path", "protocol_commit", "method", "split",
    "cluster_id", "cluster_type", "cluster_signature_sha256", "case_id",
    "case_kind", "recipe_id", "fault_set", "oracle_failure_set",
    "base_structure_flags", "truth", "decision", "raw_score", "p_valid",
    "input_sha256", "oracle_manifest_sha256", "calibration_lookup_sha256",
    "status",
)
_LOCKED_METRIC_FIELDS = (
    "row_kind", "run_id", "protocol_path", "protocol_commit", "split",
    "subgroup", "method", "method_pair", "diagnostic_id",
    "calibration_lookup_sha256", "support", "positive_count",
    "negative_count", "tp", "tn", "fp", "fn", "fpr_denominator",
    "fnr_denominator", "precision_denominator", "recall_denominator",
    "specificity_denominator", "f1_denominator", "ece_denominator",
    "balanced_accuracy", "fpr", "fnr", "precision", "recall",
    "specificity", "f1", "brier", "ece", "paired_interval_ref",
    "delta_ba_ci_lower", "delta_ba_ci_upper", "delta_fpr_ci_lower",
    "delta_fpr_ci_upper", "delta_fnr_ci_lower", "delta_fnr_ci_upper",
    "delta_brier_ci_lower", "delta_brier_ci_upper", "delta_ece_ci_lower",
    "delta_ece_ci_upper", "interval_status", "diagnostic_metric",
    "diagnostic_support", "diagnostic_positive_count",
    "diagnostic_negative_count", "diagnostic_denominator",
    "diagnostic_method_a_error_count", "diagnostic_method_b_error_count",
    "diagnostic_delta", "diagnostic_interval_ref", "diagnostic_ci_lower",
    "diagnostic_ci_upper",
)
_LOCKED_BOOTSTRAP_FIELDS = (
    "row_type", "replicate", "subgroup_code", "metric_code",
    "method_pair_key", "delta", "ci_lower", "ci_upper",
    "usable_replicates", "status",
)
_LOCKED_FLAGS = ("active-active", "pending-closed")
_VALIDATOR_NA = "NA"
_VALIDATOR_PROTOCOL_PATH = "experiments/E002-heterogeneous-specification-stress/protocol.md"
_VALIDATOR_PROTOCOL_COMMIT = "9e39c5defc89f2c2a896b53dda529f326e9dfcf8"
_LOCKED_METHOD_METRIC_FIELDS = (
    "support", "positive_count", "negative_count", "tp", "tn", "fp", "fn",
    "fpr_denominator", "fnr_denominator", "precision_denominator",
    "recall_denominator", "specificity_denominator", "f1_denominator",
    "ece_denominator", "balanced_accuracy", "fpr", "fnr", "precision",
    "recall", "specificity", "f1", "brier", "ece", "paired_interval_ref",
    "delta_ba_ci_lower", "delta_ba_ci_upper", "delta_fpr_ci_lower",
    "delta_fpr_ci_upper", "delta_fnr_ci_lower", "delta_fnr_ci_upper",
    "delta_brier_ci_lower", "delta_brier_ci_upper", "delta_ece_ci_lower",
    "delta_ece_ci_upper",
)
_LOCKED_DIAGNOSTIC_METRIC_FIELDS = (
    *_LOCKED_METHOD_METRIC_FIELDS,
    "diagnostic_metric", "diagnostic_support", "diagnostic_positive_count",
    "diagnostic_negative_count", "diagnostic_denominator",
    "diagnostic_method_a_error_count", "diagnostic_method_b_error_count",
    "diagnostic_delta", "diagnostic_interval_ref", "diagnostic_ci_lower",
    "diagnostic_ci_upper",
)
_VALID_RESULT_DEVIATIONS_MARKER = b"## Deviations\nnone\n"

# Staged validation has its own immutable protocol transcription.  These
# values intentionally do not reference producer tables in e002.py.  The
# producer may therefore be changed consistently with an in-memory artifact
# object without making a malformed staged file acceptable.
_VALIDATOR_TYPE_ORDER = ("H0", "H1", "H2", "H3", "H4", "H5")
_VALIDATOR_TRACES = MappingProxyType(
    {
        "H0": (("pending", "active", "active", "closed"), ("pending", "active", "closed"), ("pending", "active", "active", "closed")),
        "H1": (("pending", "active", "active", "closed"), ("pending", "active", "closed"), ("pending", "closed"), ("pending", "active", "closed")),
        "H2": (("pending", "active", "active", "closed"), ("pending", "active", "closed"), ("pending", "closed"), ("pending", "active", "closed"), ("pending", "closed")),
        "H3": (("pending", "active", "closed"), ("pending", "active", "active", "closed"), ("pending", "closed"), ("pending", "active", "active", "closed")),
        "H4": (("pending", "active", "active", "closed"), ("pending", "active", "closed"), ("pending", "closed"), ("pending", "active", "closed"), ("pending", "active", "closed"), ("pending", "active", "closed")),
        "H5": (("pending", "active", "closed"), ("pending", "active", "closed"), ("pending", "active", "closed"), ("pending", "active", "closed"), ("pending", "active", "closed"), ("pending", "closed"), ("pending", "closed")),
    }
)
_VALIDATOR_RECIPES = MappingProxyType(
    {
        "H0": ("valid-base", "R1", "C1", "T1", "V1", "M01", "M02"),
        "H1": ("valid-base", "R1", "C1", "T1", "V1", "M01", "M02", "M03"),
        "H2": ("valid-base", "R1", "C1", "T1", "V1", "M01", "M02", "M03", "M04"),
        "H3": ("valid-base", "R1", "C1", "T1", "V1", "M01", "M02", "M03", "M04", "M05"),
        "H4": ("valid-base", "R1", "C1", "T1", "V1", "M01", "M02", "M03", "M04", "M05", "M06"),
        "H5": ("valid-base", "R1", "C1", "T1", "V1", "M01", "M02", "M03", "M04", "M05", "M06", "M07"),
    }
)
_VALIDATOR_RECIPE_OPERATIONS = MappingProxyType(
    {
        "valid-base": (),
        "R1": (("copy", "/ledger/1/entry_id", "/ledger/0/entry_id"),),
        "C1": (("increment", "/ledger/last/amount_cents", 1),),
        "T1": (("set", "/events/1/to_state", "pending"),),
        "V1": (("set", "/events/1/revision", 1),),
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
_VALIDATOR_SIGNATURE_TUPLES = MappingProxyType(
    {
        "H0": (3, 3, 8, 2, 0, 0, 2, 7),
        "H1": (4, 4, 8, 1, 1, 0, 3, 8),
        "H2": (5, 5, 9, 1, 2, 0, 4, 9),
        "H3": (4, 5, 9, 2, 1, 1, 5, 10),
        "H4": (6, 6, 12, 1, 1, 0, 6, 11),
        "H5": (7, 7, 12, 0, 2, 0, 7, 12),
    }
)
_VALIDATOR_SIGNATURES = MappingProxyType(
    {
        "H0": "2e80ccf18dad2a97d8d3e975b0f726f6cf15687fa6e4f50ddf55a940e6d29e9b",
        "H1": "0195af9dd2a1ef0f4348c6fc6f082b626d7c9ab1c310c9487d5760bf74afa574",
        "H2": "0863b001f0a85dc2582be68a41d33afc2c7d8b28bb52e224e66c4124b8a42d45",
        "H3": "278251e55ee1daf215d42e1f534bf811529ab9da39069e488c448f88014d3272",
        "H4": "d96362a72a4bd443d8e750ced1cebca4521ff28a9e5116bfe6e65c57d2cfbaf3",
        "H5": "9a0568400739c46729f811419f84a144a0dfd5de1031f30bd9a47834f101bdcd",
    }
)
_VALIDATOR_FAULTS = MappingProxyType(
    {
        "valid-base": (), "R1": ("identity",), "C1": ("conservation",),
        "T1": ("transition",), "V1": ("revision",),
        "M01": ("conservation", "identity"),
        "M02": ("revision", "transition"),
        "M03": ("conservation", "revision"),
        "M04": ("schema", "transition"),
        "M05": ("conservation", "schema"),
        "M06": ("identity", "schema"),
        "M07": ("revision", "schema"),
    }
)
_VALIDATOR_FOOTPRINTS = MappingProxyType(
    {
        cluster_type: MappingProxyType({
            "valid-base": (),
            "R1": ("replace:/ledger/1/entry_id",),
            "C1": (f"replace:/ledger/{tuple_value[1]}/amount_cents",),
            "T1": ("replace:/events/1/to_state",),
            "V1": ("replace:/events/1/revision",),
            "M01": ("replace:/ledger/1/entry_id", f"replace:/ledger/{tuple_value[1]}/amount_cents"),
            "M02": ("replace:/events/1/revision", "replace:/events/1/to_state"),
            "M03": ("replace:/events/1/revision", f"replace:/ledger/{tuple_value[1]}/amount_cents"),
            "M04": ("remove:/events/0/revision", "replace:/events/1/to_state"),
            "M05": ("add:/ledger/0/debug", f"replace:/ledger/{tuple_value[1]}/amount_cents"),
            "M06": ("replace:/ledger/1/entry_id", "replace:/meta/declared_total_cents"),
            "M07": ("add:/ledger/0/debug", "replace:/events/1/revision"),
        })
        for cluster_type, tuple_value in (
            ("H0", (3, 2)), ("H1", (4, 3)), ("H2", (5, 4)),
            ("H3", (4, 4)), ("H4", (6, 5)), ("H5", (7, 6)),
        )
    }
)
_VALIDATOR_SUBGROUP_CODE = MappingProxyType({
    "overall": "o", "cluster:H0": "h0", "cluster:H1": "h1",
    "cluster:H2": "h2", "cluster:H3": "h3", "cluster:H4": "h4",
    "cluster:H5": "h5", "case_kind:valid": "v", "case_kind:single": "s",
    "case_kind:multi": "m",
})
_VALIDATOR_METRIC_CODE = MappingProxyType({
    "balanced_accuracy": "ba", "fpr": "fpr", "fnr": "fnr",
    "brier": "brier", "ece": "ece",
})
_VALIDATOR_DIAGNOSTIC_PAIR = MappingProxyType({
    "d1": ("M1-omit-conservation", "M1", "fpr", "omit-M1", "omit-m1"),
    "d2": ("M1-overconstraint", "M1", "fnr", "over-M1", "over-m1"),
    "d3": ("M1-stale-transition", "M1", "fnr", "stale-M1", "stale-m1"),
})
_VALIDATOR_DIAGNOSTIC_CLUSTER_IDS = MappingProxyType({
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
})
_VALIDATOR_ALLOWED_EDGES = frozenset({
    ("pending", "active"), ("pending", "closed"),
    ("active", "active"), ("active", "closed"),
})
_VALIDATOR_STALE_EDGES = frozenset({
    ("pending", "active"), ("active", "active"), ("active", "closed"),
})


def _is_d9_or_na(token: str) -> bool:
    return token != "-0.000000000" and _D9_OR_NA.fullmatch(token) is not None


def _reject_negative_zero_bytes(content: bytes, label: str) -> None:
    """Reject the exact forbidden D9 token without matching identifiers."""

    if _NEGATIVE_ZERO_TOKEN.search(content):
        raise InvalidRunError(f"negative-zero {label} token")


def _validator_d9(value: Fraction | None) -> str:
    if value is None:
        return "NA"
    from decimal import Decimal, ROUND_HALF_EVEN, localcontext

    with localcontext() as context:
        context.prec = 100
        quantized = (
            Decimal(value.numerator) / Decimal(value.denominator)
        ).quantize(Decimal("0.000000001"), rounding=ROUND_HALF_EVEN)
    if quantized == 0:
        return "0.000000000"
    text = format(quantized, "f")
    if "." not in text:
        text += ".000000000"
    whole, fractional = text.split(".", 1)
    return whole + "." + fractional.ljust(9, "0")[:9]


def _validator_amount(cluster_index: int, entity_index: int) -> int:
    material = f"E002-v1|amount|{cluster_index}|{entity_index}".encode("utf-8")
    return 200 + int.from_bytes(hashlib.sha256(material).digest()[:8], "big") % 800


def _validator_base_payload(cluster_index: int, cluster_type: str) -> dict[str, Any]:
    traces = _VALIDATOR_TRACES[cluster_type]
    entities: list[dict[str, Any]] = []
    ledger: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    ledger_index = 0
    total = 0
    for entity_index, trace in enumerate(traces):
        amount = _validator_amount(cluster_index, entity_index)
        parts = (
            (amount // 2, amount - amount // 2)
            if cluster_type == "H3" and entity_index == 0 else (amount,)
        )
        for part in parts:
            ledger.append({
                "entry_id": f"ledger-{ledger_index}",
                "entity_id": f"entity-{entity_index}",
                "amount_cents": part,
            })
            ledger_index += 1
            total += part
        entities.append({
            "entity_id": f"entity-{entity_index}",
            "current_state": "closed",
            "revision": len(trace) - 1,
        })
        for revision in range(1, len(trace)):
            events.append({
                "event_id": f"event-{entity_index}-{revision}",
                "entity_id": f"entity-{entity_index}",
                "from_state": trace[revision - 1],
                "to_state": trace[revision],
                "revision": revision,
            })
    return {
        "meta": {"schema_version": "E002-v1", "declared_total_cents": total},
        "entities": entities,
        "ledger": ledger,
        "events": events,
    }


def _validator_apply_recipe(base: Mapping[str, Any], recipe_id: str) -> dict[str, Any]:
    output = json.loads(json.dumps(base, ensure_ascii=True, separators=(",", ":")))
    if recipe_id not in _VALIDATOR_RECIPE_OPERATIONS:
        raise InvalidRunError("validator recipe operation drift")

    def get_pointer(pointer: str) -> Any:
        target: Any = output
        for part in pointer.strip("/").split("/"):
            if isinstance(target, list):
                target = target[-1] if part == "last" else target[int(part)]
            else:
                target = target[part]
        return target

    def set_pointer(pointer: str, value: Any) -> None:
        parts = pointer.strip("/").split("/")
        target: Any = output
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

    def remove_pointer(pointer: str) -> None:
        parts = pointer.strip("/").split("/")
        target: Any = output
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

    for operation in _VALIDATOR_RECIPE_OPERATIONS[recipe_id]:
        kind = operation[0]
        if kind == "copy":
            set_pointer(operation[1], get_pointer(operation[2]))
        elif kind == "increment":
            set_pointer(operation[1], get_pointer(operation[1]) + operation[2])
        elif kind in {"set", "add"}:
            set_pointer(operation[1], operation[2])
        elif kind == "remove":
            remove_pointer(operation[1])
        else:
            raise InvalidRunError("validator recipe operation drift")
    return output


def _validator_schema(payload: Any) -> bool:
    try:
        if type(payload) is not dict or set(payload) != {"meta", "entities", "ledger", "events"}:
            return False
        meta = payload["meta"]
        entities = payload["entities"]
        ledger = payload["ledger"]
        events = payload["events"]
        if type(meta) is not dict or set(meta) != {"schema_version", "declared_total_cents"}:
            return False
        if meta["schema_version"] != "E002-v1":
            return False
        if type(meta["declared_total_cents"]) is not int or type(meta["declared_total_cents"]) is bool:
            return False
        if not 600 <= meta["declared_total_cents"] <= 6994:
            return False
        if type(entities) is not list or not 3 <= len(entities) <= 7:
            return False
        if type(ledger) is not list or not 3 <= len(ledger) <= 7:
            return False
        if type(events) is not list or not 8 <= len(events) <= 12:
            return False
        for item in entities:
            if type(item) is not dict or set(item) != {"entity_id", "current_state", "revision"}:
                return False
            if type(item["entity_id"]) is not str or re.fullmatch(r"entity-[0-6]", item["entity_id"]) is None:
                return False
            if item["current_state"] not in {"pending", "active", "closed"}:
                return False
            if type(item["revision"]) is not int or type(item["revision"]) is bool or not 1 <= item["revision"] <= 12:
                return False
        for item in ledger:
            if type(item) is not dict or set(item) != {"entry_id", "entity_id", "amount_cents"}:
                return False
            if type(item["entry_id"]) is not str or re.fullmatch(r"ledger-[0-6]", item["entry_id"]) is None:
                return False
            if type(item["entity_id"]) is not str or re.fullmatch(r"entity-[0-6]", item["entity_id"]) is None:
                return False
            if type(item["amount_cents"]) is not int or type(item["amount_cents"]) is bool or not 1 <= item["amount_cents"] <= 200000:
                return False
        for item in events:
            if type(item) is not dict or set(item) != {"event_id", "entity_id", "from_state", "to_state", "revision"}:
                return False
            if type(item["event_id"]) is not str or re.fullmatch(r"event-[0-6]-(?:[1-9]|1[0-2])", item["event_id"]) is None:
                return False
            if type(item["entity_id"]) is not str or re.fullmatch(r"entity-[0-6]", item["entity_id"]) is None:
                return False
            if item["from_state"] not in {"pending", "active", "closed"} or item["to_state"] not in {"pending", "active", "closed"}:
                return False
            if type(item["revision"]) is not int or type(item["revision"]) is bool or not 1 <= item["revision"] <= 12:
                return False
        return True
    except (KeyError, TypeError, AttributeError, ValueError):
        return False


def _validator_flags(payload: Mapping[str, Any]) -> tuple[str, ...]:
    flags = set()
    for event in payload.get("events", ()):
        edge = (event.get("from_state"), event.get("to_state"))
        if edge == ("active", "active"):
            flags.add("active-active")
        if edge == ("pending", "closed"):
            flags.add("pending-closed")
    return tuple(sorted(flags))


def _validator_family_truth(payload: Mapping[str, Any]) -> tuple[bool, tuple[str, ...]]:
    if not _validator_schema(payload):
        return False, tuple(sorted(
            ("schema", "identity", "conservation", "revision", "transition"),
            key=lambda value: value.encode("utf-8"),
        ))
    entities = payload["entities"]
    ledger = payload["ledger"]
    events = payload["events"]
    entity_ids = [item["entity_id"] for item in entities]
    ledger_ids = [item["entry_id"] for item in ledger]
    identity = (
        len(set(entity_ids)) == len(entity_ids)
        and len(set(ledger_ids)) == len(ledger_ids)
        and all(item["entity_id"] in entity_ids for item in ledger)
        and set(item["entity_id"] for item in ledger) == set(entity_ids)
    )
    conservation = (
        all(item["amount_cents"] > 0 for item in ledger)
        and sum(item["amount_cents"] for item in ledger) == payload["meta"]["declared_total_cents"]
    )
    by_entity: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for event in events:
        by_entity[event["entity_id"]].append(event)
    transition = set(by_entity) == set(entity_ids)
    revision = set(by_entity) == set(entity_ids)
    for entity in entities:
        sequence = by_entity.get(entity["entity_id"], ())
        state = "pending"
        revisions: list[int] = []
        for event in sequence:
            edge = (event["from_state"], event["to_state"])
            if state == "closed" or event["from_state"] != state or edge not in _VALIDATOR_ALLOWED_EDGES:
                transition = False
            state = event["to_state"]
            revisions.append(event["revision"])
        if state != "closed" or entity["current_state"] != "closed":
            transition = False
        if revisions != list(range(1, len(sequence) + 1)) or entity["revision"] != len(sequence):
            revision = False
    failures = tuple(sorted((
        name for name, passed in (
            ("identity", identity), ("conservation", conservation),
            ("revision", revision), ("transition", transition),
        ) if not passed
    ), key=lambda value: value.encode("utf-8")))
    return not failures, failures


def _validator_checker(payload: Mapping[str, Any], method: str) -> tuple[int, bool]:
    schema = _validator_schema(payload)
    if not schema:
        return 1, False
    entities = payload["entities"]
    ledger = payload["ledger"]
    events = payload["events"]
    entity_ids = [item["entity_id"] for item in entities]
    identity = (
        len(set(entity_ids)) == len(entity_ids)
        and len({item["entry_id"] for item in ledger}) == len(ledger)
        and {item["entity_id"] for item in ledger} == set(entity_ids)
    )
    conservation = (
        all(item["amount_cents"] > 0 for item in ledger)
        and sum(item["amount_cents"] for item in ledger) == payload["meta"]["declared_total_cents"]
    )
    by_entity: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for event in events:
        by_entity[event["entity_id"]].append(event)
    edges = _VALIDATOR_STALE_EDGES if method == "M1-stale-transition" else _VALIDATOR_ALLOWED_EDGES
    transition = set(by_entity) == set(entity_ids)
    revision = set(by_entity) == set(entity_ids)
    for entity in entities:
        sequence = by_entity.get(entity["entity_id"], ())
        state = "pending"
        revision_values: list[int] = []
        for event in sequence:
            edge = (event["from_state"], event["to_state"])
            if state == "closed" or event["from_state"] != state or edge not in edges:
                transition = False
            state = event["to_state"]
            revision_values.append(event["revision"])
        if state != "closed" or entity["current_state"] != "closed":
            transition = False
        if revision_values != list(range(1, len(sequence) + 1)) or entity["revision"] != len(sequence):
            revision = False
    checks: list[bool]
    if method in {"M1", "M1-no-calibration"}:
        checks = [identity, conservation, transition, revision]
    elif method == "M1-omit-conservation":
        checks = [identity, transition, revision]
    elif method == "M1-overconstraint":
        checks = [identity, conservation, transition, revision, "active-active" not in _validator_flags(payload)]
    elif method == "M1-stale-transition":
        checks = [identity, conservation, transition, revision]
    elif method == "M1-no-semantic":
        checks = [transition, revision]
    elif method == "M1-no-state":
        checks = [identity, conservation]
    elif method == "B0":
        checks = []
    else:
        raise InvalidRunError("validator method drift")
    failed = sum(not check for check in checks)
    return failed, failed == 0


def _scan_lf_file(file_path: Path) -> None:
    last_two = b""
    total = 0
    with file_path.open("rb") as stream:
        while True:
            chunk = stream.read(1024 * 1024)
            if not chunk:
                break
            if b"\r" in chunk:
                raise InvalidRunError(f"CR byte in staged file: {file_path.name}")
            total += len(chunk)
            last_two = (last_two + chunk)[-2:]
    if total == 0 or not last_two.endswith(b"\n") or last_two == b"\n\n":
        raise InvalidRunError(f"LF/final-newline contract failed: {file_path.name}")


def _iter_lf_lines(file_path: Path):
    _scan_lf_file(file_path)
    with file_path.open("rb") as stream:
        for raw_line in stream:
            if not raw_line.endswith(b"\n") or raw_line == b"\n":
                raise InvalidRunError(f"blank/non-LF line in {file_path.name}")
            yield raw_line[:-1]


def _prediction_sort_key(row: Mapping[str, object]) -> tuple[object, ...]:
    return (
        _LOCKED_SPLIT_RANK[row["split"]],
        _LOCKED_TYPE_RANK[row["cluster_type"]],
        int(str(row["cluster_id"])[-2:]),
        _LOCKED_RECIPE_RANK[row["recipe_id"]],
        _LOCKED_METHOD_RANK[row["method"]],
    )


def _validator_case_facts() -> tuple[dict[str, Any], ...]:
    facts: list[dict[str, Any]] = []
    for type_index, cluster_type in enumerate(_VALIDATOR_TYPE_ORDER):
        for local_index in range(16):
            split = (
                "development" if local_index < 4
                else "calibration" if local_index < 8
                else "confirmatory"
            )
            cluster_index = type_index * 16 + local_index
            cluster_id = f"{cluster_type}-C{local_index:02d}"
            base = _validator_base_payload(cluster_index, cluster_type)
            base_hash = e002.canonical_sha256(base)
            flags = _validator_flags(base)
            for recipe_id in _VALIDATOR_RECIPES[cluster_type]:
                payload = _validator_apply_recipe(base, recipe_id)
                schema_valid = _validator_schema(payload)
                truth, failures = _validator_family_truth(payload)
                case_kind = (
                    "valid" if recipe_id == "valid-base"
                    else "single" if recipe_id in {"R1", "C1", "T1", "V1"}
                    else "multi"
                )
                facts.append({
                    "split": split,
                    "cluster_id": cluster_id,
                    "cluster_type": cluster_type,
                    "local_index": local_index,
                    "cluster_index": cluster_index,
                    "case_id": f"{cluster_id}::{recipe_id}",
                    "case_kind": case_kind,
                    "recipe_id": recipe_id,
                    "fault_set": tuple(_VALIDATOR_FAULTS[recipe_id]),
                    "footprint": tuple(_VALIDATOR_FOOTPRINTS[cluster_type][recipe_id]),
                    "base_hash": base_hash,
                    "input_sha256": e002.canonical_sha256(payload),
                    "base_structure_flags": flags,
                    "schema_valid": schema_valid,
                    "truth": int(truth),
                    "oracle_failure_set": tuple(failures),
                    "payload": payload,
                    "structural_signature": _VALIDATOR_SIGNATURE_TUPLES[cluster_type],
                    "signature_sha256": _VALIDATOR_SIGNATURES[cluster_type],
                })
    return tuple(facts)


def _validator_case_sort_key(case: Mapping[str, Any]) -> tuple[int, int, int, int]:
    return (
        _LOCKED_SPLIT_RANK[case["split"]],
        _LOCKED_TYPE_RANK[case["cluster_type"]],
        int(case["local_index"]),
        _LOCKED_RECIPE_RANK[case["recipe_id"]],
    )


def _validator_oracle_manifest_hash(facts: Sequence[Mapping[str, Any]]) -> str:
    return e002.canonical_sha256({
        "protocol_id": "E002-v1",
        "cases": [
            {
                "case_id": case["case_id"],
                "schema_valid": case["schema_valid"],
                "truth": case["truth"],
                "oracle_failure_set": list(case["oracle_failure_set"]),
                "base_structure_flags": list(case["base_structure_flags"]),
            }
            for case in sorted(facts, key=_validator_case_sort_key)
        ],
    })


def _validator_lookup_rows(lookups: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for method in _LOCKED_METHODS:
        lookup = lookups[method]
        if lookup["fallback"] is None:
            rows.append({
                "method": method,
                "raw_score": 0,
                "positive_count": 0,
                "count": 0,
                "p_valid": e002.JsonNumber("0.000000000"),
                "fallback": e002.JsonNumber("0.000000000"),
            })
        else:
            fallback = e002.JsonNumber(_validator_d9(lookup["fallback"]))
            rows.extend({
                "method": method,
                "raw_score": score,
                "positive_count": positive,
                "count": count,
                "p_valid": e002.JsonNumber(_validator_d9(probability)),
                "fallback": fallback,
            } for score, positive, count, probability in lookup["entries"])
    return rows


def _validator_lookups(
    facts: Sequence[Mapping[str, Any]],
) -> tuple[dict[str, Mapping[str, Any]], dict[str, str], str]:
    calibration = [case for case in facts if case["split"] == "calibration"]
    expected_ids = {
        f"{cluster_type}-C{local_index:02d}::{recipe_id}"
        for cluster_type in _VALIDATOR_TYPE_ORDER
        for local_index in range(4, 8)
        for recipe_id in _VALIDATOR_RECIPES[cluster_type]
    }
    if {case["case_id"] for case in calibration} != expected_ids or len(calibration) != 228:
        raise InvalidRunError("independent calibration inventory drift")
    lookups: dict[str, Mapping[str, Any]] = {}
    lookup_hashes: dict[str, str] = {}
    for method in _LOCKED_METHODS:
        if method == "M1-no-calibration":
            lookup = {"method": method, "entries": (), "fallback": None}
        else:
            counts: dict[int, int] = defaultdict(int)
            positives: dict[int, int] = defaultdict(int)
            for case in calibration:
                raw_score, _decision = _validator_checker(case["payload"], method)
                counts[raw_score] += 1
                positives[raw_score] += case["truth"]
            total = sum(counts.values())
            positive_total = sum(positives.values())
            lookup = {
                "method": method,
                "entries": tuple(
                    (
                        score, positives[score], counts[score],
                        Fraction(positives[score] + 1, counts[score] + 2),
                    )
                    for score in sorted(counts)
                ),
                "fallback": Fraction(positive_total + 1, total + 2),
            }
        lookups[method] = lookup
        lookup_hashes[method] = e002.canonical_sha256({
            "protocol_id": "E002-v1",
            "method": method,
            "rows": [
                {
                    "method": method,
                    "raw_score": score,
                    "positive_count": positive,
                    "count": count,
                    "p_valid": e002.JsonNumber(_validator_d9(probability)),
                    "fallback": e002.JsonNumber(_validator_d9(lookup["fallback"])),
                }
                for score, positive, count, probability in lookup["entries"]
            ] or [{
                "method": method,
                "raw_score": 0,
                "positive_count": 0,
                "count": 0,
                "p_valid": e002.JsonNumber("0.000000000"),
                "fallback": e002.JsonNumber("0.000000000"),
            }],
        })
    calibration_hash = e002.canonical_sha256({
        "protocol_id": "E002-v1",
        "methods": _validator_lookup_rows(lookups),
    })
    return lookups, lookup_hashes, calibration_hash


def _validator_prediction_row(
    run_id: str,
    case: Mapping[str, Any],
    method: str,
    lookups: Mapping[str, Mapping[str, Any]],
    lookup_hashes: Mapping[str, str],
    calibration_hash: str,
    oracle_hash: str,
) -> dict[str, Any]:
    raw_score, decision = _validator_checker(case["payload"], method)
    if method == "M1-no-calibration":
        probability = Fraction(int(decision), 1)
    else:
        probability = next(
            entry[3] for entry in lookups[method]["entries"] if entry[0] == raw_score
        ) if any(entry[0] == raw_score for entry in lookups[method]["entries"]) else lookups[method]["fallback"]
    if probability is None:
        raise InvalidRunError("independent calibration lookup missing")
    return {
        "run_id": run_id,
        "protocol_path": "experiments/E002-heterogeneous-specification-stress/protocol.md",
        "protocol_commit": "9e39c5defc89f2c2a896b53dda529f326e9dfcf8",
        "method": method,
        "split": case["split"],
        "cluster_id": case["cluster_id"],
        "cluster_type": case["cluster_type"],
        "cluster_signature_sha256": case["signature_sha256"],
        "case_id": case["case_id"],
        "case_kind": case["case_kind"],
        "recipe_id": case["recipe_id"],
        "fault_set": list(case["fault_set"]),
        "oracle_failure_set": list(case["oracle_failure_set"]),
        "base_structure_flags": list(case["base_structure_flags"]),
        "truth": case["truth"],
        "decision": decision,
        "raw_score": raw_score,
        "p_valid": e002.JsonNumber(_validator_d9(probability)),
        "input_sha256": case["input_sha256"],
        "oracle_manifest_sha256": oracle_hash,
        "calibration_lookup_sha256": lookup_hashes[method],
        "status": "valid",
    }


def _validator_prediction_object(row: Mapping[str, Any]) -> dict[str, Any]:
    return {field: row[field] for field in _LOCKED_PREDICTION_FIELDS}


def _validator_expected_predictions(
    run_id: str, required_splits: Sequence[str]
) -> tuple[tuple[dict[str, Any], ...], dict[str, Any]]:
    facts = _validator_case_facts()
    if tuple(required_splits) == _LOCKED_SPLITS:
        if len(facts) != 912:
            raise InvalidRunError("independent population count drift")
    selected = [case for case in facts if case["split"] in set(required_splits)]
    lookups, lookup_hashes, calibration_hash = _validator_lookups(facts)
    oracle_hash = _validator_oracle_manifest_hash(facts)
    rows = [
        _validator_prediction_row(
            run_id, case, method, lookups, lookup_hashes, calibration_hash, oracle_hash
        )
        for case in selected
        for method in _LOCKED_METHODS
    ]
    rows.sort(key=_prediction_sort_key)
    return tuple(rows), {
        "facts": facts,
        "selected_facts": tuple(selected),
        "lookups": lookups,
        "lookup_hashes": lookup_hashes,
        "calibration_hash": calibration_hash,
        "oracle_hash": oracle_hash,
    }


def _validate_jsonl_predictions_independent(
    file_path: Path,
    run_id: str,
    required_splits: Sequence[str] = _LOCKED_SPLITS,
) -> tuple[tuple[dict[str, Any], ...], dict[str, Any]]:
    expected, context = _validator_expected_predictions(run_id, required_splits)
    parsed: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for index, raw_line in enumerate(_iter_lf_lines(file_path)):
        try:
            row = json.loads(raw_line.decode("utf-8"), parse_float=e002.JsonNumber)
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
            raise InvalidRunError("prediction JSON parse failure") from error
        if type(row) is not dict:
            raise InvalidRunError("prediction row is not an object")
        _validate_prediction_object(row, run_id)
        if index >= len(expected):
            raise InvalidRunError("prediction row count overflow")
        expected_object = _validator_prediction_object(expected[index])
        if row != expected_object or e002.canonical_json_bytes(row) != raw_line:
            raise InvalidRunError("independent prediction semantic mismatch")
        key = (row["run_id"], row["method"], row["case_id"])
        if key in seen:
            raise InvalidRunError("duplicate prediction key")
        seen.add(key)
        parsed.append(row)
    if len(parsed) != len(expected):
        raise InvalidRunError("prediction row count mismatch")
    return tuple(parsed), context


def _validator_stats(
    facts: Sequence[Mapping[str, Any]],
    predictions: Mapping[tuple[str, str], Mapping[str, Any]],
    method: str,
    predicate: Callable[[Mapping[str, Any]], bool],
    lookups: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    stats: dict[str, Any] = {
        "support": 0, "positive_count": 0, "negative_count": 0,
        "tp": 0, "tn": 0, "fp": 0, "fn": 0,
        "brier_numerator": Fraction(0),
        "bin_counts": [0] * 10,
        "bin_probability_sums": [Fraction(0)] * 10,
        "bin_truth_sums": [0] * 10,
    }
    for case in facts:
        if not predicate(case):
            continue
        row = predictions[(method, case["case_id"])]
        truth = int(case["truth"])
        decision = bool(row["decision"])
        if method == "M1-no-calibration":
            probability = Fraction(int(decision), 1)
        elif lookups is not None:
            probability = next(
                entry[3] for entry in lookups[method]["entries"]
                if entry[0] == row["raw_score"]
            ) if any(
                entry[0] == row["raw_score"]
                for entry in lookups[method]["entries"]
            ) else lookups[method]["fallback"]
            if probability is None:
                raise InvalidRunError("independent probability lookup missing")
        else:
            probability = Fraction(str(row["p_valid"]))
        stats["support"] += 1
        if truth:
            stats["positive_count"] += 1
        else:
            stats["negative_count"] += 1
        if truth and decision:
            stats["tp"] += 1
        elif truth and not decision:
            stats["fn"] += 1
        elif not truth and decision:
            stats["fp"] += 1
        else:
            stats["tn"] += 1
        stats["brier_numerator"] += (probability - truth) ** 2
        bin_index = min(9, int(probability * 10))
        stats["bin_counts"][bin_index] += 1
        stats["bin_probability_sums"][bin_index] += probability
        stats["bin_truth_sums"][bin_index] += truth
    return stats


def _validator_merge(left: dict[str, Any], right: Mapping[str, Any]) -> None:
    for key in ("support", "positive_count", "negative_count", "tp", "tn", "fp", "fn"):
        left[key] += right[key]
    left["brier_numerator"] += right["brier_numerator"]
    for index in range(10):
        left["bin_counts"][index] += right["bin_counts"][index]
        left["bin_probability_sums"][index] += right["bin_probability_sums"][index]
        left["bin_truth_sums"][index] += right["bin_truth_sums"][index]


def _validator_metric_value(stats: Mapping[str, Any], metric: str) -> Fraction | None:
    if metric == "fpr":
        denominator = stats["tn"] + stats["fp"]
        return Fraction(stats["fp"], denominator) if denominator else None
    if metric == "fnr":
        denominator = stats["tp"] + stats["fn"]
        return Fraction(stats["fn"], denominator) if denominator else None
    if metric == "precision":
        denominator = stats["tp"] + stats["fp"]
        return Fraction(stats["tp"], denominator) if denominator else None
    if metric == "recall":
        denominator = stats["tp"] + stats["fn"]
        return Fraction(stats["tp"], denominator) if denominator else None
    if metric == "specificity":
        denominator = stats["tn"] + stats["fp"]
        return Fraction(stats["tn"], denominator) if denominator else None
    if metric == "f1":
        denominator = 2 * stats["tp"] + stats["fp"] + stats["fn"]
        return Fraction(2 * stats["tp"], denominator) if denominator else None
    if metric == "balanced_accuracy":
        recall = _validator_metric_value(stats, "recall")
        specificity = _validator_metric_value(stats, "specificity")
        return (recall + specificity) / 2 if recall is not None and specificity is not None else None
    if metric == "brier":
        return stats["brier_numerator"] / stats["support"] if stats["support"] else None
    if metric == "ece":
        if not stats["support"]:
            return None
        total = Fraction(0)
        for count, probability_sum, truth_sum in zip(
            stats["bin_counts"], stats["bin_probability_sums"], stats["bin_truth_sums"]
        ):
            if count:
                total += Fraction(count, stats["support"]) * abs(
                    probability_sum / count - Fraction(truth_sum, count)
                )
        return total
    raise InvalidRunError("validator metric drift")


def _validator_denominators(stats: Mapping[str, Any]) -> dict[str, int]:
    return {
        "fpr": stats["tn"] + stats["fp"],
        "fnr": stats["tp"] + stats["fn"],
        "precision": stats["tp"] + stats["fp"],
        "recall": stats["tp"] + stats["fn"],
        "specificity": stats["tn"] + stats["fp"],
        "f1": 2 * stats["tp"] + stats["fp"] + stats["fn"],
        "balanced_accuracy": int(bool(stats["tp"] + stats["fn"] and stats["tn"] + stats["fp"])),
        "brier": stats["support"],
        "ece": stats["support"],
    }


def _validator_metric_cells(stats: Mapping[str, Any]) -> dict[str, str]:
    denominators = _validator_denominators(stats)
    return {
        "support": str(stats["support"]),
        "positive_count": str(stats["positive_count"]),
        "negative_count": str(stats["negative_count"]),
        "tp": str(stats["tp"]), "tn": str(stats["tn"]),
        "fp": str(stats["fp"]), "fn": str(stats["fn"]),
        **{f"{metric}_denominator": str(denominators[metric]) for metric in (
            "fpr", "fnr", "precision", "recall", "specificity", "f1", "ece"
        )},
        "balanced_accuracy": _validator_d9(_validator_metric_value(stats, "balanced_accuracy")),
        "fpr": _validator_d9(_validator_metric_value(stats, "fpr")),
        "fnr": _validator_d9(_validator_metric_value(stats, "fnr")),
        "precision": _validator_d9(_validator_metric_value(stats, "precision")),
        "recall": _validator_d9(_validator_metric_value(stats, "recall")),
        "specificity": _validator_d9(_validator_metric_value(stats, "specificity")),
        "f1": _validator_d9(_validator_metric_value(stats, "f1")),
        "brier": _validator_d9(_validator_metric_value(stats, "brier")),
        "ece": _validator_d9(_validator_metric_value(stats, "ece")),
    }


def _validator_diagnostic_clusters(
    facts: Sequence[Mapping[str, Any]],
) -> dict[str, tuple[str, ...]]:
    confirmatory = [case for case in facts if case["split"] == "confirmatory"]
    selected: dict[str, set[str]] = {"d1": set(), "d2": set(), "d3": set()}
    for case in confirmatory:
        if case["truth"] == 0 and case["schema_valid"] and "conservation" in case["oracle_failure_set"]:
            selected["d1"].add(case["cluster_id"])
        if case["truth"] == 1 and case["case_kind"] == "valid" and "active-active" in case["base_structure_flags"]:
            selected["d2"].add(case["cluster_id"])
        if case["truth"] == 1 and case["case_kind"] == "valid" and "pending-closed" in case["base_structure_flags"]:
            selected["d3"].add(case["cluster_id"])
    output = {
        diagnostic: tuple(sorted(values, key=lambda value: value.encode("utf-8")))
        for diagnostic, values in selected.items()
    }
    if output != dict(_VALIDATOR_DIAGNOSTIC_CLUSTER_IDS):
        raise InvalidRunError("independent diagnostic cluster-set drift")
    return output


def _validator_bootstrap_index(
    subgroup: str, metric: str, replicate: int, position: int, count: int,
    diagnostic: str | None = None,
) -> int:
    if diagnostic is None:
        material = f"E002-v1|bootstrap|{subgroup}|{metric}|{replicate}|{position}"
    else:
        material = f"E002-v1|bootstrap|diagnostic|{diagnostic}|{replicate}|{position}"
    digest = hashlib.sha256(material.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % count


def _validator_bootstrap_block(
    subgroup: str,
    metric: str,
    method_a: str,
    method_b: str,
    eligible_cluster_ids: Sequence[str],
    facts: Sequence[Mapping[str, Any]],
    predictions: Mapping[tuple[str, str], Mapping[str, Any]],
    predicate: Callable[[Mapping[str, Any]], bool],
    diagnostic: str | None = None,
    replicate_count: int = _LOCKED_REPLICATES,
    lookups: Mapping[str, Mapping[str, Any]] | None = None,
) -> tuple[list[dict[str, str]], dict[tuple[str, str, str], dict[str, str]]]:
    ordered_ids = tuple(sorted(eligible_cluster_ids, key=lambda value: value.encode("utf-8")))
    if not ordered_ids:
        raise InvalidRunError("independent bootstrap empty cluster block")
    stats_a = {
        cluster_id: _validator_stats(
            facts, predictions, method_a,
            lambda case, cluster_id=cluster_id: case["cluster_id"] == cluster_id and predicate(case),
            lookups,
        ) for cluster_id in ordered_ids
    }
    stats_b = {
        cluster_id: _validator_stats(
            facts, predictions, method_b,
            lambda case, cluster_id=cluster_id: case["cluster_id"] == cluster_id and predicate(case),
            lookups,
        ) for cluster_id in ordered_ids
    }
    deltas: list[Fraction] = []
    rows: list[dict[str, str]] = []
    subgroup_code = diagnostic or _VALIDATOR_SUBGROUP_CODE[subgroup]
    pair_key = "m1-b0" if diagnostic is None else _VALIDATOR_DIAGNOSTIC_PAIR[diagnostic][4]
    metric_code = _VALIDATOR_METRIC_CODE[metric]
    for replicate in range(replicate_count):
        aggregate_a = _validator_stats((), {}, method_a, lambda _case: False, lookups)
        aggregate_b = _validator_stats((), {}, method_b, lambda _case: False, lookups)
        for position in range(len(ordered_ids)):
            selected = ordered_ids[_validator_bootstrap_index(
                subgroup, metric, replicate, position, len(ordered_ids), diagnostic
            )]
            _validator_merge(aggregate_a, stats_a[selected])
            _validator_merge(aggregate_b, stats_b[selected])
        value_a = _validator_metric_value(aggregate_a, metric)
        value_b = _validator_metric_value(aggregate_b, metric)
        delta = value_a - value_b if value_a is not None and value_b is not None else None
        if delta is not None:
            deltas.append(delta)
        rows.append({
            "row_type": "replicate", "replicate": str(replicate),
            "subgroup_code": subgroup_code, "metric_code": metric_code,
            "method_pair_key": pair_key, "delta": _validator_d9(delta),
            "ci_lower": "NA", "ci_upper": "NA", "usable_replicates": "0",
            "status": "usable" if delta is not None else "undefined",
        })
    usable = len(deltas)
    if not deltas:
        lower = upper = "NA"
        status = "undefined"
    else:
        ordered = sorted(deltas)
        lower_index = max(0, min(usable - 1, math.ceil(0.025 * usable) - 1))
        upper_index = max(0, min(usable - 1, math.ceil(0.975 * usable) - 1))
        lower = _validator_d9(ordered[lower_index])
        upper = _validator_d9(ordered[upper_index])
        status = "valid" if usable == replicate_count == _LOCKED_REPLICATES else "partial"
    for row in rows:
        row["usable_replicates"] = str(usable)
    rows.append({
        "row_type": "interval", "replicate": "NA", "subgroup_code": subgroup_code,
        "metric_code": metric_code, "method_pair_key": pair_key, "delta": "NA",
        "ci_lower": lower, "ci_upper": upper, "usable_replicates": str(usable),
        "status": status,
    })
    interval_key = (
        f"diagnostic:{diagnostic}" if diagnostic is not None else subgroup,
        metric,
        "M1-B0" if diagnostic is None else _VALIDATOR_DIAGNOSTIC_PAIR[diagnostic][3],
    )
    return rows, {interval_key: {
        "ci_lower": lower, "ci_upper": upper,
        "usable_replicates": str(usable), "status": status,
    }}


def _validate_bootstrap_independent(
    file_path: Path,
    context: Mapping[str, Any],
    selected_splits: Sequence[str] = ("confirmatory",),
    replicate_count: int = _LOCKED_REPLICATES,
    include_diagnostics: bool = True,
) -> tuple[dict[tuple[str, str, str], dict[str, str]], str]:
    facts = tuple(context["facts"])
    predictions = {
        (row["method"], row["case_id"]): row
        for row in context["prediction_rows"]
    }
    selected_split_set = set(selected_splits)
    diagnostics = _validator_diagnostic_clusters(facts) if include_diagnostics else {}
    iterator = iter(_iter_csv_lines(file_path))
    try:
        raw_header, header = next(iterator)
    except StopIteration as error:
        raise InvalidRunError("empty bootstrap artifact") from error
    if header != list(_LOCKED_BOOTSTRAP_FIELDS) or raw_header != _csv_line(header):
        raise InvalidRunError("bootstrap header drift")
    intervals: dict[tuple[str, str, str], dict[str, str]] = {}
    manifest_rows: list[dict[str, str]] = []
    block_count = 0
    for subgroup in _LOCKED_SUBGROUPS:
        if subgroup.startswith("cluster:"):
            cluster_type = subgroup.split(":", 1)[1]
            cluster_ids = sorted({case["cluster_id"] for case in facts if case["split"] in selected_split_set and case["cluster_type"] == cluster_type}, key=lambda value: value.encode("utf-8"))
        else:
            cluster_ids = sorted({case["cluster_id"] for case in facts if case["split"] in selected_split_set}, key=lambda value: value.encode("utf-8"))
        for metric in _LOCKED_METRICS:
            predicate = lambda case, subgroup=subgroup: (
                case["split"] in selected_split_set
                and (subgroup == "overall"
                     or subgroup.startswith("cluster:") and case["cluster_type"] == subgroup.split(":", 1)[1]
                     or subgroup.startswith("case_kind:") and case["case_kind"] == subgroup.split(":", 1)[1])
            )
            rows, interval = _validator_bootstrap_block(
                subgroup, metric, "M1", "B0", cluster_ids, facts, predictions, predicate,
                replicate_count=replicate_count, lookups=context["lookups"],
            )
            for expected in rows:
                try:
                    raw, cells = next(iterator)
                except StopIteration as error:
                    raise InvalidRunError("bootstrap row count underflow") from error
                _validate_bootstrap_cells(cells)
                expected_cells = [expected[field] for field in _LOCKED_BOOTSTRAP_FIELDS]
                if cells != expected_cells or raw != _csv_line(expected_cells):
                    raise InvalidRunError("independent bootstrap mismatch")
                manifest_rows.append(dict(expected))
            intervals.update(interval)
            block_count += 1
    for diagnostic in ("d1", "d2", "d3") if include_diagnostics else ():
        method_a, method_b, metric, _pair, _pair_code = _VALIDATOR_DIAGNOSTIC_PAIR[diagnostic]
        eligible_ids = diagnostics[diagnostic]
        predicate = lambda case, diagnostic=diagnostic: (
            case["split"] == "confirmatory"
            and ((diagnostic == "d1" and case["truth"] == 0 and case["schema_valid"] and "conservation" in case["oracle_failure_set"])
                 or (diagnostic == "d2" and case["truth"] == 1 and case["case_kind"] == "valid" and "active-active" in case["base_structure_flags"])
                 or (diagnostic == "d3" and case["truth"] == 1 and case["case_kind"] == "valid" and "pending-closed" in case["base_structure_flags"]))
        )
        rows, interval = _validator_bootstrap_block(
            diagnostic, metric, method_a, method_b, eligible_ids, facts,
            predictions, predicate, diagnostic, replicate_count,
            context["lookups"],
        )
        for expected in rows:
            try:
                raw, cells = next(iterator)
            except StopIteration as error:
                raise InvalidRunError("bootstrap row count underflow") from error
            _validate_bootstrap_cells(cells)
            expected_cells = [expected[field] for field in _LOCKED_BOOTSTRAP_FIELDS]
            if cells != expected_cells or raw != _csv_line(expected_cells):
                raise InvalidRunError("independent diagnostic bootstrap mismatch")
            manifest_rows.append(dict(expected))
        intervals.update(interval)
        block_count += 1
    try:
        next(iterator)
    except StopIteration:
        pass
    else:
        raise InvalidRunError("bootstrap row count overflow")
    if block_count != (53 if include_diagnostics else 50):
        raise InvalidRunError("bootstrap block count drift")
    expected_rows = 53 * (replicate_count + 1) if include_diagnostics else 50 * (replicate_count + 1)
    if len(manifest_rows) != expected_rows:
        raise InvalidRunError("bootstrap manifest row count drift")
    return intervals, e002.canonical_sha256({
        "protocol_id": "E002-v1", "rows": manifest_rows,
    })


def _validator_subgroup_predicate(subgroup: str) -> Callable[[Mapping[str, Any]], bool]:
    return lambda case: (
        case["split"] == "confirmatory"
        and (
            subgroup == "overall"
            or subgroup.startswith("cluster:") and case["cluster_type"] == subgroup.split(":", 1)[1]
            or subgroup.startswith("case_kind:") and case["case_kind"] == subgroup.split(":", 1)[1]
        )
    )


def _validator_metric_rows(
    run_id: str,
    context: Mapping[str, Any],
    intervals: Mapping[tuple[str, str, str], Mapping[str, str]],
    selected_splits: Sequence[str] = _LOCKED_SPLITS,
) -> tuple[dict[str, str], ...]:
    facts = tuple(context["facts"])
    predictions = {
        (row["method"], row["case_id"]): row
        for row in context["prediction_rows"]
    }
    lookup_hashes = context["lookup_hashes"]
    rows: list[dict[str, str]] = []
    for split in selected_splits:
        split_facts = [case for case in facts if case["split"] == split]
        for subgroup in _LOCKED_SUBGROUPS:
            subgroup_facts = [
                case for case in split_facts
                if subgroup == "overall"
                or subgroup.startswith("cluster:") and case["cluster_type"] == subgroup.split(":", 1)[1]
                or subgroup.startswith("case_kind:") and case["case_kind"] == subgroup.split(":", 1)[1]
            ]
            for method in _LOCKED_METHODS:
                row = {field: "NA" for field in _LOCKED_METRIC_FIELDS}
                row.update({
                    "row_kind": "method", "run_id": run_id,
                    "protocol_path": "experiments/E002-heterogeneous-specification-stress/protocol.md",
                    "protocol_commit": "9e39c5defc89f2c2a896b53dda529f326e9dfcf8",
                    "split": split, "subgroup": subgroup, "method": method,
                    "method_pair": "NA", "diagnostic_id": "NA",
                    "calibration_lookup_sha256": lookup_hashes[method],
                    "interval_status": "descriptive-only",
                })
                stats = _validator_stats(
                    subgroup_facts, predictions, method, lambda _case: True,
                    context["lookups"],
                )
                row.update(_validator_metric_cells(stats))
                if split == "confirmatory" and method in {"B0", "M1"}:
                    statuses: list[str] = []
                    refs: list[str] = []
                    for metric in _LOCKED_METRICS:
                        interval = intervals[(subgroup, metric, "M1-B0")]
                        statuses.append(interval["status"])
                        refs.append(f"primary|{subgroup}|{metric}|M1-B0")
                        suffix = "ba" if metric == "balanced_accuracy" else metric
                        row[f"delta_{suffix}_ci_lower"] = interval["ci_lower"]
                        row[f"delta_{suffix}_ci_upper"] = interval["ci_upper"]
                    row["paired_interval_ref"] = ";".join(refs)
                    row["interval_status"] = (
                        "undefined" if "undefined" in statuses
                        else "partial" if "partial" in statuses else "valid"
                    )
                rows.append(row)
    diagnostics = _validator_diagnostic_clusters(facts)
    if tuple(selected_splits) == _LOCKED_SPLITS:
      for diagnostic in ("d1", "d2", "d3"):
        method_a, method_b, metric, pair, pair_code = _VALIDATOR_DIAGNOSTIC_PAIR[diagnostic]
        subset = [case for case in facts if case["cluster_id"] in diagnostics[diagnostic] and (
            (diagnostic == "d1" and case["split"] == "confirmatory" and case["truth"] == 0 and case["schema_valid"] and "conservation" in case["oracle_failure_set"])
            or (diagnostic == "d2" and case["split"] == "confirmatory" and case["truth"] == 1 and case["case_kind"] == "valid" and "active-active" in case["base_structure_flags"])
            or (diagnostic == "d3" and case["split"] == "confirmatory" and case["truth"] == 1 and case["case_kind"] == "valid" and "pending-closed" in case["base_structure_flags"])
        )]
        stats_a = _validator_stats(subset, predictions, method_a, lambda _case: True, context["lookups"])
        stats_b = _validator_stats(subset, predictions, method_b, lambda _case: True, context["lookups"])
        value_a = _validator_metric_value(stats_a, metric)
        value_b = _validator_metric_value(stats_b, metric)
        if value_a is None or value_b is None:
            raise InvalidRunError("independent diagnostic denominator undefined")
        interval = intervals[(f"diagnostic:{diagnostic}", metric, pair)]
        denominator = (
            stats_a["tn"] + stats_a["fp"] if metric == "fpr"
            else stats_a["tp"] + stats_a["fn"]
        )
        error_a = stats_a["fp"] if metric == "fpr" else stats_a["fn"]
        error_b = stats_b["fp"] if metric == "fpr" else stats_b["fn"]
        row = {field: "NA" for field in _LOCKED_METRIC_FIELDS}
        row.update({
            "row_kind": "diagnostic", "run_id": run_id,
            "protocol_path": "experiments/E002-heterogeneous-specification-stress/protocol.md",
            "protocol_commit": "9e39c5defc89f2c2a896b53dda529f326e9dfcf8",
            "split": "confirmatory", "subgroup": f"diagnostic:{diagnostic}",
            "method": "NA", "method_pair": pair, "diagnostic_id": diagnostic,
            "calibration_lookup_sha256": "NA", "interval_status": interval["status"],
            "diagnostic_metric": metric,
            "diagnostic_support": str(len(subset)),
            "diagnostic_positive_count": str(sum(case["truth"] for case in subset)),
            "diagnostic_negative_count": str(sum(1 - case["truth"] for case in subset)),
            "diagnostic_denominator": str(denominator),
            "diagnostic_method_a_error_count": str(error_a),
            "diagnostic_method_b_error_count": str(error_b),
            "diagnostic_delta": _validator_d9(value_a - value_b),
            "diagnostic_interval_ref": f"stress|{diagnostic}|{metric}|{pair}",
            "diagnostic_ci_lower": interval["ci_lower"],
            "diagnostic_ci_upper": interval["ci_upper"],
        })
        rows.append(row)
    expected_count = len(selected_splits) * len(_LOCKED_SUBGROUPS) * len(_LOCKED_METHODS) + (
        3 if tuple(selected_splits) == _LOCKED_SPLITS else 0
    )
    if len(rows) != expected_count:
        raise InvalidRunError("independent metric row count drift")
    return tuple(rows)


def _validate_metrics_independent(
    file_path: Path,
    run_id: str,
    context: Mapping[str, Any],
    intervals: Mapping[tuple[str, str, str], Mapping[str, str]],
    selected_splits: Sequence[str] = _LOCKED_SPLITS,
) -> tuple[dict[str, str], ...]:
    expected = _validator_metric_rows(run_id, context, intervals, selected_splits)
    iterator = iter(_iter_csv_lines(file_path))
    try:
        raw_header, header = next(iterator)
    except StopIteration as error:
        raise InvalidRunError("empty metric artifact") from error
    if header != list(_LOCKED_METRIC_FIELDS) or raw_header != _csv_line(header):
        raise InvalidRunError("metric header drift")
    parsed: list[dict[str, str]] = []
    for index, expected_row in enumerate(expected):
        try:
            raw, cells = next(iterator)
        except StopIteration as error:
            raise InvalidRunError("metric row count underflow") from error
        _validate_metric_cells(cells)
        expected_cells = [expected_row[field] for field in _LOCKED_METRIC_FIELDS]
        if cells != expected_cells or raw != _csv_line(expected_cells):
            raise InvalidRunError("independent metric semantic mismatch")
        parsed.append(expected_row)
    try:
        next(iterator)
    except StopIteration:
        return tuple(parsed)
    raise InvalidRunError("metric row count overflow")


def _validate_prediction_object(row: Mapping[str, object], run_id: str) -> None:
    if set(row) != set(_LOCKED_PREDICTION_FIELDS):
        raise InvalidRunError("prediction key schema drift")
    string_fields = {
        "run_id", "protocol_path", "protocol_commit", "method", "split",
        "cluster_id", "cluster_type", "cluster_signature_sha256", "case_id",
        "case_kind", "recipe_id", "input_sha256", "oracle_manifest_sha256",
        "calibration_lookup_sha256", "status",
    }
    if any(type(row[field]) is not str for field in string_fields):
        raise InvalidRunError("prediction scalar type drift")
    if row["run_id"] != run_id or row["protocol_path"] != _VALIDATOR_PROTOCOL_PATH:
        raise InvalidRunError("prediction identity drift")
    if row["protocol_commit"] != _VALIDATOR_PROTOCOL_COMMIT or row["status"] != "valid":
        raise InvalidRunError("prediction protocol/status drift")
    if row["method"] not in _LOCKED_METHODS or row["split"] not in _LOCKED_SPLITS:
        raise InvalidRunError("prediction method/split drift")
    if row["cluster_type"] not in _LOCKED_TYPES or row["case_kind"] not in _LOCKED_CASE_KINDS:
        raise InvalidRunError("prediction type drift")
    if row["recipe_id"] not in _LOCKED_RECIPES:
        raise InvalidRunError("prediction recipe drift")
    if re.fullmatch(r"H[0-5]-C(?:0[0-9]|1[0-5])", row["cluster_id"]) is None:
        raise InvalidRunError("prediction cluster ID drift")
    if row["case_id"] != f"{row['cluster_id']}::{row['recipe_id']}":
        raise InvalidRunError("prediction case ID drift")
    if row["cluster_type"] != row["cluster_id"][:2]:
        raise InvalidRunError("prediction cluster/type drift")
    if row["cluster_signature_sha256"] == "":
        raise InvalidRunError("prediction signature identity drift")
    if not _HASH.fullmatch(row["cluster_signature_sha256"]):
        raise InvalidRunError("prediction signature hash drift")
    for field in ("input_sha256", "oracle_manifest_sha256", "calibration_lookup_sha256"):
        if not _HASH.fullmatch(row[field]):
            raise InvalidRunError(f"prediction hash drift: {field}")
    if type(row["truth"]) is not int or type(row["truth"]) is bool or row["truth"] not in {0, 1}:
        raise InvalidRunError("prediction truth type drift")
    if type(row["decision"]) is not bool:
        raise InvalidRunError("prediction decision type drift")
    if type(row["raw_score"]) is not int or type(row["raw_score"]) is bool or not 0 <= row["raw_score"] <= 5:
        raise InvalidRunError("prediction raw score type drift")
    if type(row["p_valid"]) is not e002.JsonNumber or not re.fullmatch(
        r"^-?(?:0|[1-9][0-9]*)\.[0-9]{9}$", str(row["p_valid"])
    ) or str(row["p_valid"]) == "-0.000000000":
        raise InvalidRunError("prediction probability token drift")
    probability = float(str(row["p_valid"]))
    if not (probability >= 0.0 and probability <= 1.0):
        raise InvalidRunError("prediction probability range drift")
    for field in ("fault_set", "oracle_failure_set", "base_structure_flags"):
        values = row[field]
        if type(values) is not list or any(type(value) is not str for value in values):
            raise InvalidRunError(f"prediction list type drift: {field}")
        if values != sorted(values, key=lambda value: value.encode("utf-8")):
            raise InvalidRunError(f"prediction list order drift: {field}")
        if field in {"fault_set", "oracle_failure_set"} and any(
            value not in _LOCKED_FAMILIES for value in values
        ):
            raise InvalidRunError(f"prediction family token drift: {field}")
        if field == "base_structure_flags" and any(
            value not in _LOCKED_FLAGS for value in values
        ):
            raise InvalidRunError("prediction structure flag drift")


def _csv_line(cells: Sequence[str]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.writer(
        output,
        delimiter=",",
        quotechar='"',
        doublequote=True,
        lineterminator="\n",
        quoting=csv.QUOTE_MINIMAL,
    )
    writer.writerow(list(cells))
    return output.getvalue()[:-1].encode("utf-8")


def _iter_csv_lines(file_path: Path):
    for raw_line in _iter_lf_lines(file_path):
        try:
            text = raw_line.decode("utf-8")
            row = next(
                csv.reader(
                    [text],
                    delimiter=",",
                    quotechar='"',
                    doublequote=True,
                    quoting=csv.QUOTE_MINIMAL,
                )
            )
        except (UnicodeDecodeError, csv.Error, StopIteration) as error:
            raise InvalidRunError(f"CSV parse failure: {file_path.name}") from error
        yield raw_line, row


def _validate_metric_cells(cells: Sequence[str]) -> None:
    if len(cells) != len(_LOCKED_METRIC_FIELDS) or any(type(cell) is not str for cell in cells):
        raise InvalidRunError("metric cell schema drift")
    row = dict(zip(_LOCKED_METRIC_FIELDS, cells))
    if row["row_kind"] not in {"method", "diagnostic"}:
        raise InvalidRunError("metric row kind drift")
    if row["split"] not in _LOCKED_SPLITS:
        raise InvalidRunError("metric split drift")
    if row["method"] != _VALIDATOR_NA and row["method"] not in _LOCKED_METHODS:
        raise InvalidRunError("metric method drift")
    if row["method_pair"] not in {_VALIDATOR_NA, "omit-M1", "over-M1", "stale-M1"}:
        raise InvalidRunError("metric method pair drift")
    if row["diagnostic_id"] not in {_VALIDATOR_NA, *_LOCKED_DIAGNOSTICS}:
        raise InvalidRunError("metric diagnostic ID drift")
    if row["interval_status"] not in {"valid", "partial", "undefined", "descriptive-only"}:
        raise InvalidRunError("metric status drift")
    for field in (
        "balanced_accuracy", "fpr", "fnr", "precision", "recall", "specificity",
        "f1", "brier", "ece", "delta_ba_ci_lower", "delta_ba_ci_upper",
        "delta_fpr_ci_lower", "delta_fpr_ci_upper", "delta_fnr_ci_lower",
        "delta_fnr_ci_upper", "delta_brier_ci_lower", "delta_brier_ci_upper",
        "delta_ece_ci_lower", "delta_ece_ci_upper", "diagnostic_delta",
        "diagnostic_ci_lower", "diagnostic_ci_upper",
    ):
        if row[field] == "-0.000000000":
            raise InvalidRunError(f"negative-zero metric token: {field}")
        if not _is_d9_or_na(row[field]):
            raise InvalidRunError(f"metric D9/NA drift: {field}")
    for field in (
        "support", "positive_count", "negative_count", "tp", "tn", "fp", "fn",
        "fpr_denominator", "fnr_denominator", "precision_denominator",
        "recall_denominator", "specificity_denominator", "f1_denominator",
        "ece_denominator", "diagnostic_support", "diagnostic_positive_count",
        "diagnostic_negative_count", "diagnostic_denominator",
        "diagnostic_method_a_error_count", "diagnostic_method_b_error_count",
    ):
        if not _INT_OR_NA.fullmatch(row[field]):
            raise InvalidRunError(f"metric count drift: {field}")
    if row["calibration_lookup_sha256"] != _VALIDATOR_NA and not _HASH.fullmatch(row["calibration_lookup_sha256"]):
        raise InvalidRunError("metric calibration hash drift")
    diagnostic_fields = (
        "diagnostic_metric", "diagnostic_support", "diagnostic_positive_count",
        "diagnostic_negative_count", "diagnostic_denominator",
        "diagnostic_method_a_error_count", "diagnostic_method_b_error_count",
        "diagnostic_delta", "diagnostic_interval_ref", "diagnostic_ci_lower",
        "diagnostic_ci_upper",
    )
    if row["row_kind"] == "method":
        if (
            row["method"] not in _LOCKED_METHODS
            or row["method_pair"] != _VALIDATOR_NA
            or row["diagnostic_id"] != _VALIDATOR_NA
            or row["calibration_lookup_sha256"] == _VALIDATOR_NA
            or any(row[field] != _VALIDATOR_NA for field in diagnostic_fields)
        ):
            raise InvalidRunError("ordinary metric row schema drift")
        if row["split"] != "confirmatory" or row["method"] not in {"B0", "M1"}:
            if row["interval_status"] != "descriptive-only" or any(
                    row[field] != _VALIDATOR_NA
                for field in (
                    "paired_interval_ref", "delta_ba_ci_lower", "delta_ba_ci_upper",
                    "delta_fpr_ci_lower", "delta_fpr_ci_upper", "delta_fnr_ci_lower",
                    "delta_fnr_ci_upper", "delta_brier_ci_lower", "delta_brier_ci_upper",
                    "delta_ece_ci_lower", "delta_ece_ci_upper",
                )
            ):
                raise InvalidRunError("descriptive metric interval drift")
        elif row["paired_interval_ref"] == _VALIDATOR_NA or row["interval_status"] not in {
            "valid", "partial", "undefined"
        }:
            raise InvalidRunError("primary metric interval drift")
    else:
        expected_pair = _LOCKED_DIAGNOSTIC_PAIR.get(row["diagnostic_id"])
        expected_metric = _LOCKED_DIAGNOSTIC_METRIC.get(row["diagnostic_id"])
        if (
            row["split"] != "confirmatory"
            or row["method"] != _VALIDATOR_NA
            or row["method_pair"] != expected_pair
            or row["calibration_lookup_sha256"] != _VALIDATOR_NA
            or row["diagnostic_metric"] != expected_metric
            or row["paired_interval_ref"] != _VALIDATOR_NA
            or row["diagnostic_interval_ref"] == _VALIDATOR_NA
            or any(row[field] != _VALIDATOR_NA for field in _LOCKED_METHOD_METRIC_FIELDS)
        ):
            raise InvalidRunError("diagnostic metric row schema drift")
        expected_ref = (
            "stress|d1|fpr|omit-M1" if row["diagnostic_id"] == "d1" else
            "stress|d2|fnr|over-M1" if row["diagnostic_id"] == "d2" else
            "stress|d3|fnr|stale-M1"
        )
        if row["diagnostic_interval_ref"] != expected_ref or row["interval_status"] not in {
            "valid", "partial", "undefined"
        }:
            raise InvalidRunError("diagnostic interval identity drift")
    refs = row["paired_interval_ref"]
    if refs != _VALIDATOR_NA:
        allowed = {
            f"primary|{subgroup}|{metric}|M1-B0"
            for subgroup in _LOCKED_SUBGROUPS
            for metric in _LOCKED_METRICS
        }
        if any(item not in allowed for item in refs.split(";")):
            raise InvalidRunError("metric primary interval reference drift")
    diagnostic_ref = row["diagnostic_interval_ref"]
    if diagnostic_ref != _VALIDATOR_NA and diagnostic_ref not in {
        "stress|d1|fpr|omit-M1",
        "stress|d2|fnr|over-M1",
        "stress|d3|fnr|stale-M1",
    }:
        raise InvalidRunError("metric diagnostic interval reference drift")


def _validate_bootstrap_cells(cells: Sequence[str]) -> None:
    if len(cells) != len(_LOCKED_BOOTSTRAP_FIELDS) or any(type(cell) is not str for cell in cells):
        raise InvalidRunError("bootstrap cell schema drift")
    row = dict(zip(_LOCKED_BOOTSTRAP_FIELDS, cells))
    if row["row_type"] not in {"replicate", "interval"}:
        raise InvalidRunError("bootstrap row type drift")
    if row["subgroup_code"] not in _LOCKED_SUBGROUP_CODES | set(_LOCKED_DIAGNOSTICS):
        raise InvalidRunError("bootstrap subgroup code drift")
    if row["metric_code"] not in _LOCKED_METRIC_CODES:
        raise InvalidRunError("bootstrap metric code drift")
    if row["method_pair_key"] not in {"m1-b0", "omit-m1", "over-m1", "stale-m1"}:
        raise InvalidRunError("bootstrap method-pair drift")
    if row["delta"] == "-0.000000000":
        raise InvalidRunError("negative-zero bootstrap token: delta")
    if not _is_d9_or_na(row["delta"]):
        raise InvalidRunError("bootstrap delta drift")
    if row["ci_lower"] == "-0.000000000" or row["ci_upper"] == "-0.000000000":
        raise InvalidRunError("negative-zero bootstrap token: interval")
    if not _is_d9_or_na(row["ci_lower"]) or not _is_d9_or_na(row["ci_upper"]):
        raise InvalidRunError("bootstrap interval drift")
    if not re.fullmatch(r"^(?:0|[1-9][0-9]*)$", row["usable_replicates"]):
        raise InvalidRunError("bootstrap usable-count drift")
    is_diagnostic = row["subgroup_code"] in set(_LOCKED_DIAGNOSTICS)
    expected_pair = (
        _LOCKED_BOOTSTRAP_DIAGNOSTIC_PAIR[row["subgroup_code"]]
        if is_diagnostic else "m1-b0"
    )
    if row["method_pair_key"] != expected_pair:
        raise InvalidRunError("bootstrap pair/subgroup mismatch")
    if is_diagnostic and row["metric_code"] != {
        "d1": "fpr", "d2": "fnr", "d3": "fnr"
    }[row["subgroup_code"]]:
        raise InvalidRunError("bootstrap diagnostic metric drift")
    if row["row_type"] == "replicate" and row["status"] not in {"usable", "undefined"}:
        raise InvalidRunError("bootstrap replicate status drift")
    if row["row_type"] == "interval" and row["status"] not in {"valid", "partial", "undefined"}:
        raise InvalidRunError("bootstrap status drift")
    if row["row_type"] == "replicate":
        if not re.fullmatch(r"(?:0|[1-9][0-9]*)", row["replicate"]):
            raise InvalidRunError("bootstrap replicate index drift")
        if int(row["replicate"]) >= _LOCKED_REPLICATES:
            raise InvalidRunError("bootstrap replicate range drift")
        if row["ci_lower"] != _VALIDATOR_NA or row["ci_upper"] != _VALIDATOR_NA:
            raise InvalidRunError("bootstrap replicate CI drift")
        if (row["status"] == "undefined") != (row["delta"] == _VALIDATOR_NA):
            raise InvalidRunError("bootstrap replicate undefined policy drift")
    else:
        if row["replicate"] != _VALIDATOR_NA or row["delta"] != _VALIDATOR_NA:
            raise InvalidRunError("bootstrap interval-row drift")
        if (row["status"] == "undefined") != (
            row["ci_lower"] == _VALIDATOR_NA and row["ci_upper"] == _VALIDATOR_NA
        ):
            raise InvalidRunError("bootstrap interval undefined policy drift")


def _validate_jsonl_predictions(file_path: Path, artifacts: e002.PipelineArtifacts) -> None:
    expected = sorted(artifacts.prediction_rows, key=_prediction_sort_key)
    seen: set[tuple[str, str, str]] = set()
    count = 0
    for raw_line in _iter_lf_lines(file_path):
        try:
            row = json.loads(
                raw_line.decode("utf-8"), parse_float=e002.JsonNumber
            )
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
            raise InvalidRunError("prediction JSON parse failure") from error
        if type(row) is not dict:
            raise InvalidRunError("prediction row is not an object")
        _validate_prediction_object(row, artifacts.run_id)
        if count >= len(expected):
            raise InvalidRunError("prediction row count overflow")
        expected_object = e002._prediction_json_row(expected[count])
        if row != expected_object or e002.canonical_json_bytes(row) != raw_line:
            raise InvalidRunError("prediction canonical/order/content mismatch")
        key = (row["run_id"], row["method"], row["case_id"])
        if key in seen:
            raise InvalidRunError("duplicate prediction key")
        seen.add(key)
        count += 1
    if count != len(expected):
        raise InvalidRunError("prediction row count mismatch")


def _validate_csv_artifact(
    file_path: Path,
    fields: Sequence[str],
    expected_rows: Sequence[Mapping[str, object]],
    cell_validator: Callable[[Sequence[str]], None],
) -> None:
    if tuple(fields) not in {_LOCKED_METRIC_FIELDS, _LOCKED_BOOTSTRAP_FIELDS}:
        raise InvalidRunError("runner field schema identity drift")
    expected_header = list(fields)
    rows_seen = 0
    seen_keys: set[tuple[str, ...]] = set()
    for raw_line, cells in _iter_csv_lines(file_path):
        if rows_seen == 0:
            if cells != expected_header or raw_line != _csv_line(expected_header):
                raise InvalidRunError(f"CSV header/canonicality mismatch: {file_path.name}")
            rows_seen += 1
            continue
        index = rows_seen - 1
        if index >= len(expected_rows):
            raise InvalidRunError(f"CSV row count overflow: {file_path.name}")
        if len(cells) != len(fields):
            raise InvalidRunError(f"CSV column count mismatch: {file_path.name}")
        cell_validator(cells)
        if fields == _LOCKED_METRIC_FIELDS:
            key = tuple(
                cells[fields.index(name)]
                for name in ("row_kind", "split", "subgroup", "method", "diagnostic_id")
            )
        else:
            key = tuple(
                cells[fields.index(name)]
                for name in (
                    "row_type", "replicate", "subgroup_code", "metric_code",
                    "method_pair_key",
                )
            )
        if key in seen_keys:
            raise InvalidRunError(f"duplicate CSV row key: {file_path.name}")
        seen_keys.add(key)
        expected_cells = [str(expected_rows[index][field]) for field in fields]
        if cells != expected_cells or raw_line != _csv_line(expected_cells):
            raise InvalidRunError(f"CSV canonical/order/content mismatch: {file_path.name}")
        rows_seen += 1
    if rows_seen != len(expected_rows) + 1:
        raise InvalidRunError(f"CSV row count mismatch: {file_path.name}")


def _validator_raw_prediction_hash(rows: Sequence[Mapping[str, Any]]) -> str:
    ordered = sorted(rows, key=_prediction_sort_key)
    return e002.canonical_sha256({
        "protocol_id": "E002-v1",
        "rows": [
            {
                "split": row["split"], "case_id": row["case_id"],
                "method": row["method"], "raw_score": row["raw_score"],
                "decision": row["decision"], "input_sha256": row["input_sha256"],
            }
            for row in ordered
        ],
    })


def _validator_h2_outcome(
    context: Mapping[str, Any],
    metric_rows: Sequence[Mapping[str, str]],
    intervals: Mapping[tuple[str, str, str], Mapping[str, str]],
) -> tuple[str, str]:
    by_key = {
        (row["split"], row["subgroup"], row["method"]): row
        for row in metric_rows if row["row_kind"] == "method"
    }
    deltas = _validator_primary_deltas(context, split="confirmatory")
    ba_interval = intervals[("overall", "balanced_accuracy", "M1-B0")]
    fpr_interval = intervals[("overall", "fpr", "M1-B0")]
    anchor_ok = (
        ba_interval["status"] == "valid" and ba_interval["ci_lower"] != "NA"
        and Fraction(ba_interval["ci_lower"]) > 0
        and fpr_interval["status"] == "valid" and fpr_interval["ci_upper"] != "NA"
        and Fraction(fpr_interval["ci_upper"]) < 0
        and deltas["fnr"] is not None and deltas["fnr"] <= 0
    )
    cluster_deltas: list[Fraction | None] = []
    for cluster_type in _VALIDATOR_TYPE_ORDER:
        cluster_deltas.append(
            _validator_primary_deltas(
                context, cluster_type, split="confirmatory"
            )["balanced_accuracy"]
        )
    anchor_ok = anchor_ok and all(
        delta is not None and delta >= 0 for delta in cluster_deltas
    ) and sum(delta is not None and delta > 0 for delta in cluster_deltas) >= 4
    stress_ok = all(
        intervals[(f"diagnostic:{diagnostic}", _VALIDATOR_DIAGNOSTIC_PAIR[diagnostic][2], _VALIDATOR_DIAGNOSTIC_PAIR[diagnostic][3])]["status"] == "valid"
        and intervals[(f"diagnostic:{diagnostic}", _VALIDATOR_DIAGNOSTIC_PAIR[diagnostic][2], _VALIDATOR_DIAGNOSTIC_PAIR[diagnostic][3])]["ci_lower"] != "NA"
        and Fraction(intervals[(f"diagnostic:{diagnostic}", _VALIDATOR_DIAGNOSTIC_PAIR[diagnostic][2], _VALIDATOR_DIAGNOSTIC_PAIR[diagnostic][3])]["ci_lower"]) > 0
        for diagnostic in ("d1", "d2", "d3")
    )
    outcome = "supported" if anchor_ok and stress_ok else "mixed/not supported"
    fnr_delta = deltas["fnr"]
    guardrail = f"status={'pass' if fnr_delta is not None and fnr_delta <= 0 else 'fail'};delta={_validator_d9(fnr_delta)}"
    return outcome, guardrail


def _validator_token_pattern(token: str) -> str:
    if token == "RUN_ID":
        return r"e002-[0-9]{8}-[0-9]{3}"
    if token == "PROTOCOL_COMMIT" or token == "HASH":
        return r"[0-9a-f]{64}|[0-9a-f]{40}"
    if token == "PASS_OR_FAIL":
        return r"pass|fail"
    if token == "INT":
        return r"[0-9]+"
    if token == "D9_OR_NA":
        return r"(?:NA|-?(?:0|[1-9][0-9]*)\.[0-9]{9})"
    if token == "STATUS":
        return r"valid|partial|undefined|descriptive-only"
    if token == "H2_OUTCOME":
        return r"supported|mixed/not supported"
    if token == "INT_LIST":
        return r"(?:none|[0-5](?:, [0-5])*)"
    if token == "PASS_OR_FAIL_AND_DELTA":
        return r"status=(?:pass|fail);delta=(?:NA|-?(?:0|[1-9][0-9]*)\.[0-9]{9})"
    if token == "SECONDARY_METRICS":
        d9 = r"(?:NA|-?(?:0|[1-9][0-9]*)\.[0-9]{9})"
        return rf"ba={d9};fpr={d9};fnr={d9};brier={d9};ece={d9}"
    if token == "CALIBRATION_SUMMARY":
        d9 = r"(?:NA|-?(?:0|[1-9][0-9]*)\.[0-9]{9})"
        return rf"lookup=(?:[0-9a-f]{{64}});scores=(?:none|[0-5](?:, [0-5])*);p_valid=(?:none|{d9}(?:, {d9})*)"
    raise InvalidRunError(f"unknown report placeholder: {token}")


def _validator_fraction(token: str) -> Fraction | None:
    return None if token == _VALIDATOR_NA else Fraction(token)


def _validator_primary_deltas(
    context: Mapping[str, Any],
    cluster_type: str | None = None,
    *,
    split: str,
) -> dict[str, Fraction | None]:
    if split not in _LOCKED_SPLITS:
        raise InvalidRunError(f"validator delta split drift: {split}")
    facts = tuple(
        case
        for case in context["facts"]
        if case["split"] == split
        and (cluster_type is None or case["cluster_type"] == cluster_type)
    )
    predictions = {
        (row["method"], row["case_id"]): row
        for row in context["prediction_rows"]
    }
    stats = {
        method: _validator_stats(
            facts,
            predictions,
            method,
            lambda _case: True,
            context["lookups"],
        )
        for method in ("B0", "M1")
    }
    deltas: dict[str, Fraction | None] = {}
    for metric in _LOCKED_METRICS:
        left = _validator_metric_value(stats["M1"], metric)
        right = _validator_metric_value(stats["B0"], metric)
        deltas[metric] = left - right if left is not None and right is not None else None
    return deltas


def _validator_report_replacements(
    run_id: str,
    context: Mapping[str, Any],
    metric_rows: Sequence[Mapping[str, str]],
    intervals: Mapping[tuple[str, str, str], Mapping[str, str]],
    manifest_hashes: Mapping[str, str],
    artifact_hashes: Mapping[str, str],
) -> dict[str, list[str]]:
    """Recompute every dynamic report field from independently checked rows."""

    by_key = {
        (row["split"], row["subgroup"], row["method"]): row
        for row in metric_rows
        if row["row_kind"] == "method"
    }
    diagnostic_rows = {
        row["diagnostic_id"]: row
        for row in metric_rows
        if row["row_kind"] == "diagnostic"
    }
    primary_metrics = ("balanced_accuracy", "fpr", "fnr", "brier", "ece")
    primary_rows = {
        method: by_key[("confirmatory", "overall", method)]
        for method in ("B0", "M1")
    }
    d9_values: list[str] = []
    for method in ("B0", "M1"):
        d9_values.extend(primary_rows[method][metric] for metric in primary_metrics)
    primary_deltas = _validator_primary_deltas(context, split="confirmatory")
    d9_values.extend(_validator_d9(primary_deltas[metric]) for metric in primary_metrics)
    for metric in primary_metrics:
        interval = intervals[("overall", metric, "M1-B0")]
        d9_values.extend((interval["ci_lower"], interval["ci_upper"]))
    d9_values.extend(
        value
        for diagnostic in ("d1", "d2", "d3")
        for value in (
            diagnostic_rows[diagnostic]["diagnostic_delta"],
            diagnostic_rows[diagnostic]["diagnostic_ci_lower"],
            diagnostic_rows[diagnostic]["diagnostic_ci_upper"],
        )
    )

    count_values = [
        "96", "912", "228", "228", "456", "7296", "243", "530054",
        *(diagnostic_rows[diagnostic]["diagnostic_support"] for diagnostic in ("d1", "d2", "d3")),
    ]
    primary_statuses = [
        primary_rows[method]["interval_status"] for method in ("B0", "M1")
    ]
    status_values = primary_statuses + [
        "valid" if all(status == "valid" for status in primary_statuses) else "partial",
        *(diagnostic_rows[diagnostic]["interval_status"] for diagnostic in ("d1", "d2", "d3")),
    ]
    lookups = context["lookups"]
    lookup_hashes = context["lookup_hashes"]
    secondary_methods = (
        "M1-omit-conservation", "M1-overconstraint", "M1-stale-transition",
        "M1-no-semantic", "M1-no-state",
    )
    score_values = [
        ", ".join(str(entry[0]) for entry in lookups[method]["entries"]) or "none"
        for method in secondary_methods
    ]
    score_values.append(
        ", ".join(str(entry[0]) for entry in lookups["M1"]["entries"]) or "none"
    )

    secondary_values: list[str] = []
    for method in secondary_methods:
        row = by_key[("confirmatory", "overall", method)]
        secondary_values.append(";".join(
            f"{short}={row[metric]}"
            for short, metric in (
                ("ba", "balanced_accuracy"), ("fpr", "fpr"), ("fnr", "fnr"),
                ("brier", "brier"), ("ece", "ece"),
            )
        ))

    def lookup_summary(method: str) -> str:
        lookup = lookups[method]
        if lookup["fallback"] is None:
            return "lookup=none;scores=none;p_valid=none"
        scores = ", ".join(str(entry[0]) for entry in lookup["entries"]) or "none"
        probabilities = ", ".join(
            _validator_d9(entry[3]) for entry in lookup["entries"]
        ) or "none"
        return (
            f"lookup={lookup_hashes[method]};scores={scores};"
            f"p_valid={probabilities}"
        )

    h2_outcome, guardrail = _validator_h2_outcome(context, metric_rows, intervals)
    return {
        "RUN_ID": [run_id, run_id, run_id],
        "PROTOCOL_COMMIT": [_VALIDATOR_PROTOCOL_COMMIT],
        "PASS_OR_FAIL": ["pass"] * 8,
        "INT": count_values,
        "D9_OR_NA": d9_values,
        "STATUS": status_values,
        "H2_OUTCOME": [h2_outcome],
        "HASH": [
            *(lookup_hashes[method] for method in secondary_methods),
            context["calibration_hash"],
            artifact_hashes["predictions"], artifact_hashes["metrics"],
            artifact_hashes["bootstrap"],
            manifest_hashes["raw_prediction"], manifest_hashes["calibration"],
            manifest_hashes["metric"], manifest_hashes["bootstrap"],
            artifact_hashes["predictions"], artifact_hashes["metrics"],
            artifact_hashes["bootstrap"],
        ],
        "INT_LIST": score_values,
        "PASS_OR_FAIL_AND_DELTA": [guardrail],
        "SECONDARY_METRICS": secondary_values,
        "CALIBRATION_SUMMARY": [lookup_summary(method) for method in secondary_methods],
    }


def _validate_report_digest_fields(
    result_text: str,
    artifact_hashes: Mapping[str, str],
    manifest_hashes: Mapping[str, str],
    calibration_hash: str,
) -> None:
    """Validate each digest in its exact locked report namespace.

    Substring checks are intentionally not sufficient: the bootstrap artifact
    digest and the bootstrap-manifest digest are different fields and may be
    different values.  Each required line is matched by its complete field
    prefix and must occur exactly once.
    """

    required = (
        ("lookup_manifest_sha256: ", calibration_hash),
        (
            "- [predictions](../../../data/E002-v1-predictions.jsonl) sha256=",
            artifact_hashes["predictions"],
        ),
        (
            "- [metrics](../../../data/E002-v1-metrics.csv) sha256=",
            artifact_hashes["metrics"],
        ),
        (
            "- [bootstrap](../../../data/E002-v1-bootstrap.csv) sha256=",
            artifact_hashes["bootstrap"],
        ),
        ("raw_prediction_manifest: ", manifest_hashes["raw_prediction"]),
        ("calibration_manifest: ", manifest_hashes["calibration"]),
        ("metric_manifest: ", manifest_hashes["metric"]),
        ("bootstrap_manifest: ", manifest_hashes["bootstrap"]),
        ("prediction_bytes: ", artifact_hashes["predictions"]),
        ("metrics_bytes: ", artifact_hashes["metrics"]),
        ("bootstrap_bytes: ", artifact_hashes["bootstrap"]),
    )
    lines = result_text[:-1].split("\n") if result_text.endswith("\n") else result_text.split("\n")
    for prefix, digest in required:
        if _HASH.fullmatch(digest) is None:
            raise InvalidRunError(f"invalid expected report digest: {prefix}")
        expected_line = f"{prefix}{digest}"
        matching = [line for line in lines if line.startswith(prefix)]
        if matching != [expected_line]:
            raise InvalidRunError(f"result digest field mismatch: {prefix.strip()}")


def _validate_report_template_shape(
    result_text: str,
    valid_template: str,
    expected_replacements: Mapping[str, Sequence[str]] | None = None,
) -> None:
    if not result_text.endswith("\n"):
        raise InvalidRunError("result final LF drift")
    actual_lines = result_text[:-1].split("\n")
    template_lines = valid_template.split("\n")
    if len(actual_lines) != len(template_lines):
        raise InvalidRunError("result line-count/template drift")
    consumed: dict[str, int] = defaultdict(int)
    for actual, template in zip(actual_lines, template_lines):
        pattern_parts: list[str] = []
        cursor = 0
        template_matches = list(re.finditer(r"<([A-Z][A-Z0-9_]*)>", template))
        for match in template_matches:
            pattern_parts.append(re.escape(template[cursor:match.start()]))
            pattern_parts.append(f"({_validator_token_pattern(match.group(1))})")
            cursor = match.end()
        pattern_parts.append(re.escape(template[cursor:]))
        actual_match = re.fullmatch("".join(pattern_parts), actual)
        if actual_match is None:
            raise InvalidRunError("result template field grammar drift")
        if expected_replacements is not None:
            for match, actual_value in zip(template_matches, actual_match.groups()):
                token = match.group(1)
                index = consumed[token]
                expected_values = expected_replacements.get(token, ())
                if index >= len(expected_values) or actual_value != expected_values[index]:
                    raise InvalidRunError(f"result semantic field drift: {token}")
                consumed[token] += 1
    if expected_replacements is not None:
        for token, expected_values in expected_replacements.items():
            if consumed[token] != len(expected_values):
                raise InvalidRunError(f"result placeholder count drift: {token}")


def _validate_result_bytes(
    file_path: Path,
    run_id: str,
    context: Mapping[str, Any],
    metric_rows: Sequence[Mapping[str, str]],
    intervals: Mapping[tuple[str, str, str], Mapping[str, str]],
    manifest_hashes: Mapping[str, str],
    artifact_hashes: Mapping[str, str],
) -> None:
    result_bytes = file_path.read_bytes()
    forbidden = (
        b"result_draft_bytes", b"result_final_sha256", b"redacted", b"preimage"
    )
    if any(token in result_bytes.lower() for token in forbidden):
        raise InvalidRunError("forbidden result hash/preimage field")
    if b"<" in result_bytes or b"\r" in result_bytes or not result_bytes.endswith(b"\n"):
        raise InvalidRunError("result template token/newline drift")
    _reject_negative_zero_bytes(result_bytes, "report")
    if result_bytes.endswith(b"\n\n") or any(
        line.endswith((b" ", b"\t")) for line in result_bytes.splitlines()
    ):
        raise InvalidRunError("result whitespace drift")
    try:
        result_text = result_bytes.decode("utf-8")
    except UnicodeDecodeError as error:
        raise InvalidRunError("result UTF-8 drift") from error
    valid_template, invalid_template = e002._template_blocks(e002._protocol_text())
    e002._assert_template_grammar(valid_template, invalid_template)
    expected_counts = {
        "clusters": "96", "cases": "912", "development_cases": "228",
        "calibration_cases": "228", "confirmatory_cases": "456",
        "prediction_rows": "7296", "metric_rows": "243", "bootstrap_lines": "530054",
    }
    for key, value in expected_counts.items():
        if f"{key}: {value}\n" not in result_text:
            raise InvalidRunError(f"result count mismatch: {key}")
    if f"# E002-v1 result — {run_id}\n" not in result_text or f"run_id: {run_id}\n" not in result_text:
        raise InvalidRunError("result run identity drift")
    if "protocol_commit: 9e39c5defc89f2c2a896b53dda529f326e9dfcf8\n" not in result_text:
        raise InvalidRunError("result protocol identity drift")
    outcome, guardrail = _validator_h2_outcome(context, metric_rows, intervals)
    if f"outcome: {outcome}\n" not in result_text or f"fnr_guardrail: {guardrail}\n" not in result_text:
        raise InvalidRunError("result H2 field mismatch")
    actual_prediction_rows = context["prediction_rows"]
    metric_hash = e002.canonical_sha256({"protocol_id": "E002-v1", "rows": [dict(row) for row in metric_rows]})
    raw_hash = _validator_raw_prediction_hash(actual_prediction_rows)
    exact_manifest_hashes = {
        "raw_prediction": raw_hash,
        "calibration": context["calibration_hash"],
        "metric": metric_hash,
        "bootstrap": context["bootstrap_manifest_hash"],
    }
    expected_replacements = _validator_report_replacements(
        run_id, context, metric_rows, intervals, exact_manifest_hashes, artifact_hashes
    )
    _validate_report_template_shape(result_text, valid_template, expected_replacements)
    _validate_report_digest_fields(
        result_text,
        artifact_hashes,
        exact_manifest_hashes,
        context["calibration_hash"],
    )
    for method in _LOCKED_METHODS:
        if method.encode("ascii") not in result_bytes:
            raise InvalidRunError(f"result method missing: {method}")
    if result_bytes.count(_VALID_RESULT_DEVIATIONS_MARKER) != 1:
        raise InvalidRunError("result deviation marker drift")


def _validate_staged_artifacts(
    stage_paths: Mapping[str, Path],
    artifacts: e002.PipelineArtifacts,
) -> None:
    for label in ("predictions", "metrics", "bootstrap", "result"):
        if not stage_paths[label].is_file():
            raise InvalidRunError(f"missing staged artifact: {label}")
    if hasattr(artifacts, "population"):
        prediction_rows, context = _validate_jsonl_predictions_independent(
            stage_paths["predictions"], artifacts.run_id
        )
        context = dict(context)
        context["prediction_rows"] = prediction_rows
        intervals, bootstrap_manifest_hash = _validate_bootstrap_independent(
            stage_paths["bootstrap"], context
        )
        context["bootstrap_manifest_hash"] = bootstrap_manifest_hash
        metric_rows = _validate_metrics_independent(
            stage_paths["metrics"], artifacts.run_id, context, intervals
        )
    else:
        _validate_jsonl_predictions(stage_paths["predictions"], artifacts)
        _validate_csv_artifact(
            stage_paths["metrics"], _LOCKED_METRIC_FIELDS, artifacts.metric_rows, _validate_metric_cells
        )
        _validate_csv_artifact(
            stage_paths["bootstrap"], _LOCKED_BOOTSTRAP_FIELDS, artifacts.bootstrap.rows, _validate_bootstrap_cells
        )
        metric_rows = artifacts.metric_rows
        context = {}
        intervals = {}
    staged_hashes = {
        "predictions": e002.sha256_hex(stage_paths["predictions"].read_bytes()),
        "metrics": e002.sha256_hex(stage_paths["metrics"].read_bytes()),
        "bootstrap": e002.sha256_hex(stage_paths["bootstrap"].read_bytes()),
    }
    if staged_hashes != dict(artifacts.artifact_hashes):
        raise InvalidRunError("staged artifact hash mismatch")
    if hasattr(artifacts, "population"):
        manifest_hashes = {
            "raw_prediction": _validator_raw_prediction_hash(context["prediction_rows"]),
            "calibration": context["calibration_hash"],
            "metric": e002.canonical_sha256({
                "protocol_id": "E002-v1", "rows": [dict(row) for row in metric_rows]
            }),
            "bootstrap": context["bootstrap_manifest_hash"],
        }
        _validate_result_bytes(
            stage_paths["result"], artifacts.run_id, context, metric_rows,
            intervals, manifest_hashes, staged_hashes,
        )
    else:
        raise InvalidRunError("independent staged validator requires population")


def _validate_artifacts(artifacts: e002.PipelineArtifacts) -> None:
    if set(artifacts.serialized) != {"predictions", "metrics", "bootstrap", "result"}:
        raise InvalidRunError("artifact key set drift")
    if len(artifacts.prediction_rows) != 7296:
        raise InvalidRunError("prediction row count drift")
    if len(artifacts.metric_rows) != 243:
        raise InvalidRunError("metric row count drift")
    if len(artifacts.bootstrap.rows) != 530053:
        raise InvalidRunError("bootstrap replicate row count drift")
    if len(artifacts.serialized["bootstrap"].splitlines()) != 530054:
        raise InvalidRunError("bootstrap line count drift")
    expected_hashes = {
        "predictions": e002.sha256_hex(artifacts.serialized["predictions"]),
        "metrics": e002.sha256_hex(artifacts.serialized["metrics"]),
        "bootstrap": e002.sha256_hex(artifacts.serialized["bootstrap"]),
    }
    if dict(artifacts.artifact_hashes) != expected_hashes:
        raise InvalidRunError("artifact hash drift")
    expected_manifests = e002._manifest_hashes(
        artifacts.population,
        artifacts.prediction_rows,
        artifacts.lookups,
        artifacts.metric_rows,
        artifacts.bootstrap,
    )
    if dict(artifacts.manifest_hashes) != expected_manifests:
        raise InvalidRunError("manifest hash drift")
    if artifacts.calibration_hash != expected_manifests["calibration"]:
        raise InvalidRunError("calibration manifest identity drift")
    multi_rows, multi_counts, multi_bytes, multi_hash = e002.multi_fault_relation_evidence(
        artifacts.population
    )
    if (
        tuple(artifacts.multi_fault_relation_rows) != multi_rows
        or dict(artifacts.multi_fault_relation_counts) != multi_counts
        or artifacts.multi_fault_relation_bytes != multi_bytes
        or artifacts.multi_fault_relation_hash != multi_hash
        or len(multi_rows) != 432
    ):
        raise InvalidRunError("multi-fault external evidence drift")
    if (
        len(artifacts.serialized["predictions"]) >= 8_000_000
        or len(artifacts.serialized["metrics"]) >= 500_000
        or len(artifacts.serialized["bootstrap"]) >= 50_000_000
        or len(artifacts.serialized["result"]) >= 40_000
        or e002.BOOTSTRAP_ESTIMATE >= e002.PUBLIC_LIMIT
    ):
        raise InvalidRunError("planning envelope or public size gate failed")
    if b"result_draft_bytes" in artifacts.serialized["result"]:
        raise InvalidRunError("forbidden report draft hash field")
    if any(token in artifacts.serialized["result"].lower() for token in (b"result_final_sha256", b"redacted", b"preimage")):
        raise InvalidRunError("forbidden report hash/preimage field")
    _reject_negative_zero_bytes(artifacts.serialized["result"], "report")
    for name, content in artifacts.serialized.items():
        if len(content) >= e002.PUBLIC_LIMIT:
            raise InvalidRunError(f"public size gate failed: {name}")


def execute_run(
    run_id: str,
    output_root: Path | str,
    *,
    repository_root: Path | None = None,
    protocol_guard_fn: Callable[[Path, Path, Mapping[str, Path]], None] | None = None,
    pipeline_factory: Callable[[str, Path], e002.PipelineArtifacts] | None = None,
    publish_fn: Callable[[Path, Path], None] | None = None,
    post_publish_fn: Callable[[Path, Path, _PublicationReceipt], None] | None = None,
    artifact_validator_fn: Callable[[e002.PipelineArtifacts], None] | None = None,
    staged_validator_fn: Callable[[Mapping[str, Path], e002.PipelineArtifacts], None] | None = None,
) -> dict[str, object]:
    """Execute one staged run; injectable hooks are for local failure tests."""

    if not e002.validate_run_id(run_id):
        raise InvalidRunError("invalid run ID")
    repository = (repository_root or _repository_root()).resolve()
    destination_root = Path(output_root).resolve()
    final_paths = _final_paths(destination_root, run_id)
    guard = protocol_guard_fn or _protocol_guard
    # This is intentionally the first operation that can inspect or create an
    # output-root-related location.  The default guard itself never mkdirs.
    guard(repository, destination_root, final_paths)

    factory = pipeline_factory or e002.build_pipeline
    publisher = publish_fn or _publish_exclusive
    post_publisher = post_publish_fn or (lambda _source, _destination, _receipt: None)
    artifact_validator = artifact_validator_fn or _validate_artifacts
    staged_validator = staged_validator_fn or _validate_staged_artifacts

    # Factory and artifact validation are deliberately pre-staging.  Failures
    # here cannot create output_root or an invalid-run record.
    try:
        artifacts = factory(run_id, repository)
        artifact_validator(artifacts)
    except Exception as error:
        if isinstance(error, InvalidRunError):
            raise
        raise InvalidRunError(f"pre-staging pipeline failure: {error}") from error

    created_directories: list[Path] = []
    stage_root: Path | None = None
    staging_started = False
    owned_destinations: list[tuple[Path, tuple[int, int]]] = []
    try:
        _mkdir_tracked(destination_root, created_directories)
        stage_root = Path(tempfile.mkdtemp(prefix=".e002-stage-", dir=str(destination_root)))
        staging_started = True
        stage_paths = {
            "predictions": stage_root / "data" / "E002-v1-predictions.jsonl",
            "metrics": stage_root / "data" / "E002-v1-metrics.csv",
            "bootstrap": stage_root / "data" / "E002-v1-bootstrap.csv",
            "result": stage_root
            / "experiments"
            / "E002-heterogeneous-specification-stress"
            / "results"
            / f"run-{run_id}.md",
        }
        # Canonical data files are written first; the result is written last
        # even in staging.
        for label in ("predictions", "metrics", "bootstrap", "result"):
            _write_exclusive(stage_paths[label], artifacts.serialized[label])
        for label in ("predictions", "metrics", "bootstrap", "result"):
            if stage_paths[label].read_bytes() != artifacts.serialized[label]:
                raise InvalidRunError(f"staged byte verification failed: {label}")
        staged_validator(stage_paths, artifacts)
        for label in ("predictions", "metrics", "bootstrap", "result"):
            # Materialize and remember only directories created by this
            # invocation before calling the publisher.  An injected publisher
            # may create a destination and then raise; both the file and its
            # newly-created parent directories must remain cleanable.
            _mkdir_tracked(final_paths[label].parent, created_directories)
            destination = final_paths[label]
            before_identity = _file_identity(destination)
            if before_identity is not None:
                raise InvalidRunError(f"output appeared during run: {destination}")
            try:
                receipt = publisher(stage_paths[label], destination)
            except BaseException:
                # No receipt means no ownership.  In particular, byte
                # equality is deliberately not considered evidence because a
                # race-created external file may be identical.
                raise
            if publisher is not _publish_exclusive:
                # A hook is a fault-injection surface, not an ownership
                # authority.  Even a hook that happens to return an object
                # shaped like a receipt cannot authorize deletion.
                raise InvalidRunError(
                    f"untrusted publisher cannot issue ownership receipt: {destination}"
                )
            if not isinstance(receipt, _PublicationReceipt) or receipt._token is not _RECEIPT_TOKEN:
                raise InvalidRunError(f"publication produced no runner receipt: {destination}")
            if receipt.path != destination or _file_identity(destination) != receipt.identity:
                raise InvalidRunError(f"published destination ownership mismatch: {destination}")
            owned_destinations.append((receipt.path, receipt.identity))
            post_publisher(stage_paths[label], destination, receipt)
            if final_paths[label].read_bytes() != artifacts.serialized[label]:
                raise InvalidRunError(f"final byte verification failed: {label}")
            if _file_identity(destination) != receipt.identity:
                raise InvalidRunError(f"final ownership identity changed: {label}")
        _remove_tree_verified(stage_root)
        stage_root = None
    except BaseException as error:
        cleanup_errors: list[BaseException] = []
        if stage_root is not None:
            try:
                _remove_tree_verified(stage_root)
            except BaseException as cleanup_error:
                cleanup_errors.append(cleanup_error)
        if owned_destinations:
            try:
                _remove_owned_files_verified(owned_destinations)
            except BaseException as cleanup_error:
                cleanup_errors.append(cleanup_error)
        if created_directories:
            try:
                _remove_directories_verified(created_directories)
            except BaseException as cleanup_error:
                cleanup_errors.append(cleanup_error)
        if not staging_started:
            if cleanup_errors:
                raise InvalidRunError("persistent pre-staging cleanup failure") from cleanup_errors[0]
            if isinstance(error, InvalidRunError):
                raise
            if not isinstance(error, Exception):
                raise
            raise InvalidRunError(f"pre-staging failure: {error}") from error
        if cleanup_errors:
            raise InvalidRunError("persistent cleanup failure; no invalid record written") from cleanup_errors[0]
        invalid_target = final_paths["result"]
        if any(
            target.exists()
            for label, target in final_paths.items()
            if label != "result"
        ):
            raise InvalidRunError("cleanup verification found a non-result final") from error
        try:
            _write_exclusive(invalid_target, e002.render_invalid_result(run_id))
            if invalid_target.read_bytes() != e002.render_invalid_result(run_id):
                raise InvalidRunError("invalid-run record verification failed")
        except BaseException as invalid_error:
            if not isinstance(invalid_error, Exception):
                raise
            raise InvalidRunError("could not write invalid-run record") from invalid_error
        if isinstance(error, InvalidRunError):
            raise
        if not isinstance(error, Exception):
            raise
        raise InvalidRunError(str(error)) from error
    result_sha256 = e002.sha256_hex(final_paths["result"].read_bytes())
    multi_rows = tuple(getattr(artifacts, "multi_fault_relation_rows", ()))
    multi_counts = dict(getattr(artifacts, "multi_fault_relation_counts", {}))
    multi_bytes = getattr(artifacts, "multi_fault_relation_bytes", b"")
    multi_hash = getattr(artifacts, "multi_fault_relation_hash", e002.sha256_hex(multi_bytes))
    return {
        "status": "valid",
        "run_id": run_id,
        "paths": tuple(str(final_paths[label]) for label in ("predictions", "metrics", "bootstrap", "result")),
        "result_sha256": result_sha256,
        "multi_fault_relation_rows": multi_rows,
        "multi_fault_relation_counts": multi_counts,
        "multi_fault_relation_bytes": multi_bytes,
        "multi_fault_relation_sha256": multi_hash,
    }


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the locked E002-v1 harness")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output-root", required=True, type=Path)
    return parser


def main(arguments: Sequence[str] | None = None) -> int:
    parser = build_argument_parser()
    options = parser.parse_args(arguments)
    try:
        outcome = execute_run(options.run_id, options.output_root)
    except InvalidRunError as error:
        print(f"status: invalid\nrun_id: {options.run_id}\nerror: {error}", file=sys.stderr)
        return 2
    relation_object = {
        "protocol_id": e002.PROTOCOL_VERSION,
        "rows": list(outcome["multi_fault_relation_rows"]),
    }
    counts = outcome["multi_fault_relation_counts"]
    print(f"status: {outcome['status']}")
    print(f"run_id: {outcome['run_id']}")
    print(f"result_sha256: {outcome['result_sha256']}")
    print(f"multi_fault_relation_sha256: {outcome['multi_fault_relation_sha256']}")
    print(
        "multi_fault_relation_counts: "
        f"equals={counts.get('equals', 0)};"
        f"contains={counts.get('contains', 0)};"
        f"differs={counts.get('differs', 0)}"
    )
    print(
        "multi_fault_relations_json: "
        + e002.canonical_json_text(relation_object)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
