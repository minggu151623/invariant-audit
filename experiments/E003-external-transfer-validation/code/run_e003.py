"""Explicit, staged future-run CLI for locked E003-v1.

Importing this module performs no source, repository, or output I/O.  The
future execution path requires an explicit run ID, output root, and external
manifest path; it verifies the frozen cache before the core pipeline is
allowed to parse any source records.  Development tests use injected fake
artifacts and never call the default pipeline.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import e003


RUN_ID_RE = re.compile(r"e003-[0-9]{8}-[0-9]{3}\Z")
EXPERIMENT_ROOT = "experiments/E003-external-transfer-validation"
FINALIZE_ORDER = ("predictions", "metrics", "bootstrap", "result")
TWO_BUILD_CALLS = 2
AUDITED_SOURCE_MANIFEST_SHA256 = (
    "683eef39cd26d2a7f6622689adc2cd9e357e78a770f77bf91e98513b859e4633"
)


class InvalidRunError(RuntimeError):
    """The invocation failed closed before a valid artifact set existed."""


_RECEIPT_TOKEN = object()


class _PublicationReceipt:
    __slots__ = ("path", "identity", "_token")

    def __init__(self, path: Path, identity: tuple[int, int]) -> None:
        self.path = path
        self.identity = identity
        self._token = _RECEIPT_TOKEN


def _repository_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _git(
    repository_root: Path,
    *arguments: str,
    binary: bool = False,
) -> bytes | str:
    try:
        completed = subprocess.run(
            ["git", *arguments],
            cwd=str(repository_root),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=not binary,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        detail = getattr(error, "stderr", "") or str(error)
        if isinstance(detail, bytes):
            detail = detail.decode("utf-8", "replace")
        raise InvalidRunError(
            f"git gate failed: {' '.join(arguments)}: {str(detail).strip()}"
        ) from error
    return completed.stdout


def _git_ancestor(repository_root: Path, ancestor: str, descendant: str) -> bool:
    completed = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=str(repository_root),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        text=True,
    )
    return completed.returncode == 0


def _validate_run_id(run_id: str) -> None:
    if type(run_id) is not str or RUN_ID_RE.fullmatch(run_id) is None:
        raise InvalidRunError(
            "run_id must match e003-YYYYMMDD-NNN and cannot be a path"
        )
    try:
        year = int(run_id[5:9])
        month = int(run_id[9:11])
        day = int(run_id[11:13])
        import datetime

        datetime.date(year, month, day)
    except (TypeError, ValueError):
        raise InvalidRunError("run_id contains an invalid calendar date")
    if not e003.re.fullmatch(r"e003-[0-9]{8}-[0-9]{3}\Z", run_id):
        raise InvalidRunError("run_id grammar drift")


def _final_paths(output_root: Path, run_id: str) -> dict[str, Path]:
    _validate_run_id(run_id)
    return {
        "predictions": output_root / "data" / "E003-v1-predictions.jsonl",
        "metrics": output_root / "data" / "E003-v1-metrics.csv",
        "bootstrap": output_root / "data" / "E003-v1-bootstrap.csv",
        "result": output_root
        / EXPERIMENT_ROOT
        / "results"
        / f"run-{run_id}.md",
    }


def _path_is_inside(path: Path, directory: Path) -> bool:
    try:
        path.resolve().relative_to(directory.resolve())
    except ValueError:
        return False
    return True


def _verify_audited_manifest(manifest_path: Path) -> None:
    """Pin the source manifest before any source payload can be opened."""

    try:
        manifest_bytes = manifest_path.read_bytes()
    except OSError as error:
        raise InvalidRunError("audited source manifest cannot be read") from error
    if e003.sha256_hex(manifest_bytes) != AUDITED_SOURCE_MANIFEST_SHA256:
        raise InvalidRunError("audited source manifest SHA-256 mismatch")


def _protocol_guard(
    repository_root: Path,
    output_root: Path,
    final_paths: Mapping[str, Path],
    manifest_path: Path,
    *,
    ancestor_fn: Callable[[Path, str, str], bool] = _git_ancestor,
) -> None:
    """Perform all non-source guards before any output-root mutation."""

    run_id = final_paths["result"].stem.removeprefix("run-")
    _validate_run_id(run_id)
    status = str(
        _git(
            repository_root,
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
        )
    )
    if status:
        raise InvalidRunError("working tree or index is not clean")
    protocol_file = repository_root / e003.PROTOCOL_PATH
    if not protocol_file.is_file():
        raise InvalidRunError("locked protocol file is missing")
    try:
        committed_protocol = _git(
            repository_root,
            "show",
            f"{e003.PROTOCOL_COMMIT}:{e003.PROTOCOL_PATH}",
            binary=True,
        )
    except InvalidRunError as error:
        raise InvalidRunError("locked protocol commit/path is unavailable") from error
    if not isinstance(committed_protocol, bytes):
        raise InvalidRunError("locked protocol gate did not return bytes")
    if protocol_file.read_bytes() != committed_protocol:
        raise InvalidRunError("working protocol bytes differ from locked commit")
    if e003.sha256_hex(committed_protocol) != e003.PROTOCOL_BLOB_SHA256:
        raise InvalidRunError("locked protocol raw-byte hash mismatch")
    head = str(_git(repository_root, "rev-parse", "--verify", "HEAD")).strip()
    if not ancestor_fn(repository_root, e003.PROTOCOL_COMMIT, head):
        raise InvalidRunError("locked protocol commit is not an ancestor of HEAD")
    if output_root.resolve() != repository_root.resolve():
        raise InvalidRunError("confirmatory output root must be repository root")
    if output_root.exists() and not output_root.is_dir():
        raise InvalidRunError("output root is not a directory")
    manifest_path = manifest_path.resolve()
    if _path_is_inside(manifest_path, repository_root):
        raise InvalidRunError("source manifest must remain outside the repository")
    if not manifest_path.is_file():
        raise InvalidRunError("external source manifest is missing")
    _verify_audited_manifest(manifest_path)
    for label, target in final_paths.items():
        if target.exists():
            raise InvalidRunError(f"output already exists: {label}")
    if output_root.is_dir():
        stale_stages = [
            child for child in output_root.iterdir()
            if child.name.startswith(".e003-stage-")
        ]
        if stale_stages:
            raise InvalidRunError("stale E003 staging directory exists")


def _source_preflight(
    manifest_path: Path,
    source_root: Path | None,
) -> e003.SourceManifest:
    """Verify the frozen manifest and all raw gzip bytes before parsing."""

    _verify_audited_manifest(manifest_path)
    manifest = e003.load_manifest(manifest_path, source_root)
    if manifest.manifest_sha256 != AUDITED_SOURCE_MANIFEST_SHA256:
        raise InvalidRunError("audited source manifest changed during preflight")
    if _path_is_inside(manifest.source_root, _repository_root()):
        raise InvalidRunError("source cache must remain outside the repository")
    try:
        e003.verify_source_hashes(manifest, e003.SPLITS)
    except e003.ProtocolError as error:
        raise InvalidRunError(f"source manifest/cache preflight failed: {error}") from error
    return manifest


def _mkdir_tracked(directory: Path, created: list[Path]) -> None:
    if directory.exists():
        if not directory.is_dir() or directory.is_symlink():
            raise InvalidRunError(f"expected directory is unavailable: {directory}")
        return
    missing: list[Path] = []
    cursor = directory
    while not cursor.exists():
        missing.append(cursor)
        parent = cursor.parent
        if parent == cursor:
            raise InvalidRunError(f"cannot create directory: {directory}")
        cursor = parent
    if not cursor.is_dir() or cursor.is_symlink():
        raise InvalidRunError(f"directory ancestor is unavailable: {cursor}")
    for item in reversed(missing):
        item.mkdir()
        created.append(item)


def _write_exclusive(file_path: Path, content: bytes) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(
            file_path,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o644,
        )
    except OSError as error:
        raise InvalidRunError(f"exclusive write failed: {file_path}") from error
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
    if not file_path.is_file() or file_path.is_symlink():
        raise InvalidRunError(f"published destination is not a regular file: {file_path}")
    return stat_result.st_dev, stat_result.st_ino


def _publish_exclusive(source: Path, destination: Path) -> _PublicationReceipt:
    if not destination.parent.is_dir():
        raise InvalidRunError(f"destination parent is unavailable: {destination.parent}")
    if destination.exists():
        raise InvalidRunError(f"output appeared during run: {destination}")
    try:
        os.link(source, destination)
    except OSError as error:
        raise InvalidRunError(f"exclusive finalization failed: {destination}") from error
    identity = _file_identity(destination)
    if identity is None:
        raise InvalidRunError(f"published destination disappeared: {destination}")
    return _PublicationReceipt(destination, identity)


def _remove_tree_verified(directory: Path) -> None:
    if not directory.exists():
        return
    if not directory.is_dir() or directory.is_symlink():
        raise InvalidRunError(f"staging path is not a directory: {directory}")
    shutil.rmtree(directory)
    if directory.exists():
        raise InvalidRunError(f"staging cleanup could not be verified: {directory}")


def _remove_owned_files_verified(
    owned: Sequence[tuple[Path, tuple[int, int]]],
) -> None:
    for path, identity in reversed(tuple(owned)):
        current = _file_identity(path)
        if current is None:
            continue
        if current != identity:
            raise InvalidRunError(f"refusing to remove a replaced destination: {path}")
        path.unlink()
        if path.exists():
            raise InvalidRunError(f"published-file cleanup could not be verified: {path}")


def _remove_directories_verified(directories: Sequence[Path]) -> None:
    for directory in reversed(tuple(directories)):
        if not directory.exists():
            continue
        if not directory.is_dir() or directory.is_symlink():
            raise InvalidRunError(f"owned directory changed: {directory}")
        try:
            directory.rmdir()
        except OSError as error:
            raise InvalidRunError(f"owned directory is not empty: {directory}") from error


def _artifact_bytes(artifact: Any, name: str) -> bytes:
    try:
        value = artifact.serialized(name)
    except AttributeError:
        serialized = getattr(artifact, "serialized_outputs", None)
        if isinstance(serialized, Mapping):
            value = serialized[name]
        else:
            value = dict(serialized)[name]
    if type(value) is not bytes:
        raise InvalidRunError(f"artifact is not bytes: {name}")
    return value


def _validate_staged_artifacts(
    stage_paths: Mapping[str, Path],
    contents: Mapping[str, bytes],
) -> None:
    for name in FINALIZE_ORDER:
        path = stage_paths[name]
        if not path.is_file() or path.read_bytes() != contents[name]:
            raise InvalidRunError(f"staged byte verification failed: {name}")


def _invalid_result_bytes(run_id: str) -> bytes:
    return (
        f"# E003-v1 invalid run — {run_id}\n"
        "status: invalid\n"
        "protocol_id: E003-v1\n"
        f"protocol_commit: {e003.PROTOCOL_COMMIT}\n"
        f"run_id: {run_id}\n"
        "failure_class: invalid-run\n"
        "No metrics or evidence exist.\n"
        "corrected_run_requires_new_id: true\n"
    ).encode("utf-8")


def _write_invalid_record(path: Path, run_id: str) -> None:
    if path.exists():
        raise InvalidRunError("invalid-run result path appeared during cleanup")
    path.parent.mkdir(parents=True, exist_ok=True)
    _write_exclusive(path, _invalid_result_bytes(run_id))
    if path.read_bytes() != _invalid_result_bytes(run_id):
        raise InvalidRunError("invalid-run record verification failed")


def _validate_deterministic_build(
    first: Any,
    second: Any,
    run_id: str,
) -> dict[str, bytes]:
    if getattr(first, "run_id", None) != run_id or getattr(second, "run_id", None) != run_id:
        raise InvalidRunError("pipeline returned a mismatched run ID")
    contents = {name: _artifact_bytes(first, name) for name in FINALIZE_ORDER}
    repeat_contents = {name: _artifact_bytes(second, name) for name in FINALIZE_ORDER}
    if contents != repeat_contents:
        raise InvalidRunError("two-build serialized determinism gate failed")
    first_hashes = getattr(first, "hashes", None)
    second_hashes = getattr(second, "hashes", None)
    if callable(first_hashes) and callable(second_hashes) and first_hashes() != second_hashes():
        raise InvalidRunError("two-build internal determinism gate failed")
    return contents


def _production_pipeline_factory(
    run_id: str,
    repository_root: Path,
    manifest_path: Path,
    source_root: Path | None,
) -> e003.PipelineArtifacts:
    """Build through the production path with the locked independence gates."""

    return e003.build_pipeline(
        run_id,
        repository_root,
        manifest_path,
        source_root,
        independence_gate_fn=e003.run_independence_gates,
    )


def execute_run(
    run_id: str,
    output_root: Path | str,
    source_manifest: Path | str,
    *,
    source_root: Path | str | None = None,
    repository_root: Path | None = None,
    protocol_guard_fn: Callable[[Path, Path, Mapping[str, Path], Path], None] | None = None,
    source_preflight_fn: Callable[[Path, Path | None], e003.SourceManifest] | None = None,
    pipeline_factory: Callable[[str, Path, Path, Path | None], Any] | None = None,
    artifact_validator_fn: Callable[[Any], None] | None = None,
    staged_validator_fn: Callable[[Mapping[str, Path], Mapping[str, bytes]], None] | None = None,
    publish_fn: Callable[[Path, Path], _PublicationReceipt] | None = None,
) -> dict[str, Any]:
    """Execute one explicit future run with staged, fail-closed publication.

    The default source preflight and pipeline are called only from this
    explicit execution function.  There is no retry loop; the second factory
    call is the required one-time two-build determinism comparison.
    """

    _validate_run_id(run_id)
    repository = (repository_root or _repository_root()).resolve()
    destination = Path(output_root).expanduser().resolve()
    manifest_path = Path(source_manifest).expanduser().resolve()
    final_paths = _final_paths(destination, run_id)
    guard = protocol_guard_fn or _protocol_guard
    guard(repository, destination, final_paths, manifest_path)

    source_preflight = source_preflight_fn or _source_preflight
    try:
        manifest = source_preflight(
            manifest_path,
            Path(source_root).expanduser().resolve() if source_root is not None else None,
        )
    except InvalidRunError:
        raise
    except Exception as error:
        raise InvalidRunError(f"source manifest/cache preflight failed: {error}") from error

    factory = pipeline_factory or _production_pipeline_factory
    artifact_validator = artifact_validator_fn or e003.validate_pipeline_artifacts
    try:
        first = factory(run_id, repository, manifest_path, manifest.source_root)
        second = factory(run_id, repository, manifest_path, manifest.source_root)
        artifact_validator(first)
        artifact_validator(second)
        contents = _validate_deterministic_build(first, second, run_id)
    except InvalidRunError:
        raise
    except Exception as error:
        raise InvalidRunError(f"pre-staging pipeline failure: {error}") from error
    for name, data in contents.items():
        if len(data) >= e003.PUBLIC_SIZE_LIMITS[name]:
            raise InvalidRunError(f"size gate failed: {name}")

    created_directories: list[Path] = []
    stage_root: Path | None = None
    staging_started = False
    owned_destinations: list[tuple[Path, tuple[int, int]]] = []
    publisher = publish_fn or _publish_exclusive
    staged_validator = staged_validator_fn or _validate_staged_artifacts
    try:
        _mkdir_tracked(destination, created_directories)
        stage_root = Path(tempfile.mkdtemp(prefix=".e003-stage-", dir=str(destination)))
        staging_started = True
        stage_paths = {
            "predictions": stage_root / "data" / "E003-v1-predictions.jsonl",
            "metrics": stage_root / "data" / "E003-v1-metrics.csv",
            "bootstrap": stage_root / "data" / "E003-v1-bootstrap.csv",
            "result": stage_root
            / EXPERIMENT_ROOT
            / "results"
            / f"run-{run_id}.md",
        }
        for name in FINALIZE_ORDER:
            _write_exclusive(stage_paths[name], contents[name])
        staged_validator(stage_paths, contents)
        for name in FINALIZE_ORDER:
            _mkdir_tracked(final_paths[name].parent, created_directories)
            destination_path = final_paths[name]
            if destination_path.exists():
                raise InvalidRunError(f"output appeared during run: {destination_path}")
            receipt = publisher(stage_paths[name], destination_path)
            if publisher is not _publish_exclusive:
                raise InvalidRunError(
                    "injected publisher cannot authorize ownership in the default path"
                )
            if not isinstance(receipt, _PublicationReceipt) or receipt._token is not _RECEIPT_TOKEN:
                raise InvalidRunError(f"publication produced no ownership receipt: {name}")
            if receipt.path != destination_path or _file_identity(destination_path) != receipt.identity:
                raise InvalidRunError(f"publication ownership mismatch: {name}")
            owned_destinations.append((destination_path, receipt.identity))
            if destination_path.read_bytes() != contents[name]:
                raise InvalidRunError(f"final byte verification failed: {name}")
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
        try:
            _remove_directories_verified(created_directories)
        except BaseException as cleanup_error:
            cleanup_errors.append(cleanup_error)
        if not staging_started:
            if cleanup_errors:
                raise InvalidRunError("pre-staging cleanup failed") from cleanup_errors[0]
            if isinstance(error, InvalidRunError):
                raise
            if isinstance(error, Exception):
                raise InvalidRunError(f"pre-staging failure: {error}") from error
            raise InvalidRunError("pre-staging run interruption") from error
        if cleanup_errors:
            raise InvalidRunError("persistent cleanup failure; no invalid record written") from cleanup_errors[0]
        non_result_finals = [
            path for name, path in final_paths.items()
            if name != "result" and path.exists()
        ]
        if non_result_finals:
            raise InvalidRunError("cleanup found a non-result final output") from error
        invalid_target = final_paths["result"]
        try:
            _write_invalid_record(invalid_target, run_id)
        except BaseException as invalid_error:
            raise InvalidRunError("could not write the concise invalid-run record") from invalid_error
        if isinstance(error, InvalidRunError):
            raise
        if isinstance(error, Exception):
            raise InvalidRunError(str(error)) from error
        raise InvalidRunError("run interrupted after staging") from error

    result_path = final_paths["result"]
    return {
        "status": "valid",
        "run_id": run_id,
        "paths": tuple(str(final_paths[name]) for name in FINALIZE_ORDER),
        "result_sha256": e003.sha256_hex(result_path.read_bytes()),
        "source_manifest_sha256": manifest.manifest_sha256,
    }


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the locked E003-v1 harness")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--source-manifest", required=True, type=Path)
    parser.add_argument("--source-root", required=False, type=Path)
    return parser


def main(arguments: Sequence[str] | None = None) -> int:
    parser = build_argument_parser()
    options = parser.parse_args(arguments)
    try:
        outcome = execute_run(
            options.run_id,
            options.output_root,
            options.source_manifest,
            source_root=options.source_root,
        )
    except InvalidRunError as error:
        print(
            f"status: invalid\nrun_id: {options.run_id}\nerror: {error}",
            file=sys.stderr,
        )
        return 2
    print(f"status: {outcome['status']}")
    print(f"run_id: {outcome['run_id']}")
    print(f"source_manifest_sha256: {outcome['source_manifest_sha256']}")
    print(f"result_sha256: {outcome['result_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
