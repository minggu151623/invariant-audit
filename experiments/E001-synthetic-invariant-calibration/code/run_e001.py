"""Explicit, staged future-run CLI for the locked E001-v1 harness.

Importing this module is side-effect free.  A future run is possible only when
the caller supplies both an explicit run ID and output root.  The worker builds
all artifacts in memory, writes them to a private temporary directory, and
publishes the result document last.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable, Mapping

import e001


RUN_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}\Z")
EXPERIMENT_ROOT = "experiments/E001-synthetic-invariant-calibration"
FINALIZE_ORDER = ("predictions", "metrics", "bootstrap", "results")


class InvalidRunError(RuntimeError):
    """Raised when a future run fails before it can be finalized as valid."""


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _git(repo_root: Path, *arguments: str, binary: bool = False) -> bytes | str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=repo_root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=not binary,
    )
    return completed.stdout


def _git_ancestor(repo_root: Path, commit: str, head: str) -> bool:
    completed = subprocess.run(
        ["git", "merge-base", "--is-ancestor", commit, head],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        text=True,
    )
    return completed.returncode == 0


def _protocol_guard(
    repo_root: Path,
    *,
    git_fn: Callable[..., bytes | str] = _git,
    ancestor_fn: Callable[[Path, str, str], bool] = _git_ancestor,
) -> None:
    """Refuse dirty, changed, or historically unanchored protocol inputs."""

    dirty = str(git_fn(repo_root, "status", "--porcelain", "--untracked-files=all"))
    if dirty:
        raise RuntimeError("refusing run: repository worktree or index is dirty")
    protocol_path = repo_root / e001.PROTOCOL_PATH
    if not protocol_path.is_file():
        raise RuntimeError(f"refusing run: missing protocol file {e001.PROTOCOL_PATH}")
    locked_bytes = git_fn(
        repo_root,
        "show",
        f"{e001.PROTOCOL_COMMIT}:{e001.PROTOCOL_PATH}",
        binary=True,
    )
    head_bytes = git_fn(repo_root, "show", f"HEAD:{e001.PROTOCOL_PATH}", binary=True)
    if protocol_path.read_bytes() != locked_bytes or head_bytes != locked_bytes:
        raise RuntimeError("refusing run: protocol identity is not the locked commit")
    head = str(git_fn(repo_root, "rev-parse", "--verify", "HEAD")).strip()
    if not ancestor_fn(repo_root, e001.PROTOCOL_COMMIT, head):
        raise RuntimeError(
            f"refusing run: protocol commit {e001.PROTOCOL_COMMIT} is not an ancestor of {head}"
        )


def _validate_run_id(run_id: str) -> None:
    if not RUN_ID_RE.fullmatch(run_id):
        raise ValueError(
            "run_id must be 1-64 ASCII letters, digits, '.', '_' or '-' and cannot be a path"
        )


def _target_paths(output_root: Path, run_id: str) -> dict[str, Path]:
    _validate_run_id(run_id)
    targets = {
        "results": output_root
        / EXPERIMENT_ROOT
        / "results"
        / f"run-{run_id}.md",
        "predictions": output_root / "data" / "E001-v1-predictions.jsonl",
        "metrics": output_root / "data" / "E001-v1-metrics.csv",
        "bootstrap": output_root / "data" / "E001-v1-bootstrap.csv",
    }
    existing = [str(path) for path in targets.values() if path.exists()]
    if existing:
        raise FileExistsError(
            "refusing run: expected output already exists: " + ", ".join(existing)
        )
    return targets


def _invalid_markdown(run_id: str, reason: str) -> str:
    concise = " ".join(str(reason).split())[:1000]
    return "\n".join(
        (
            f"# E001 run {run_id}",
            "",
            f"- Protocol: `{e001.PROTOCOL_PATH}`",
            f"- Protocol version: `{e001.PROTOCOL_VERSION}`",
            f"- Protocol commit: `{e001.PROTOCOL_COMMIT}`",
            f"- Run ID: `{run_id}`",
            "- Run validity: `invalid`.",
            "- Metrics are not evidence and must not be interpreted as a result.",
            f"- Failure: `{concise}`",
            "- Corrected reruns require a new run ID.",
            "",
        )
    )


def _write_invalid_record(path: Path, run_id: str, reason: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(_invalid_markdown(run_id, reason))
    except FileExistsError:
        # Never overwrite an existing result, including an existing invalid record.
        pass


def _stage_bytes(stage_root: Path, targets: Mapping[str, Path], name: str, content: bytes) -> Path:
    if name not in targets:
        raise KeyError(name)
    stage_path = stage_root / f"{name}.partial"
    stage_path.parent.mkdir(parents=True, exist_ok=True)
    with stage_path.open("xb") as handle:
        handle.write(content)
    return stage_path


def _default_guard(repo_root: Path) -> None:
    _protocol_guard(repo_root)


def execute_run(
    run_id: str,
    output_root: Path,
    *,
    repo_root: Path | None = None,
    protocol_guard_fn: Callable[[Path], None] | None = None,
    pipeline_factory: Callable[[str], e001.PipelineArtifacts] | None = None,
    replace_fn: Callable[[str | os.PathLike[str], str | os.PathLike[str]], None] = os.replace,
) -> dict[str, Any]:
    """Execute a future run with staged, refusal-safe output finalization.

    The injectable guard/factory/replacer are for local unit tests only; the
    command-line path uses the locked protocol guard, deterministic pipeline,
    and ordinary ``os.replace``.
    """

    _validate_run_id(run_id)
    output_root = Path(output_root).expanduser().resolve()
    repo_root = _repo_root() if repo_root is None else Path(repo_root).resolve()
    guard = _default_guard if protocol_guard_fn is None else protocol_guard_fn
    factory = e001.build_pipeline if pipeline_factory is None else pipeline_factory
    # Target discovery is read-only. The protocol/clean-tree/ancestor guard
    # must observe the repository before output_root or any staging directory
    # is created.
    targets = _target_paths(output_root, run_id)

    moved: list[str] = []
    try:
        guard(repo_root)
        output_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".e001-stage-", dir=str(output_root)) as stage_name:
            stage_root = Path(stage_name)
            artifact = factory(run_id)
            repeat = factory(run_id)
            if artifact.run_id != run_id or repeat.run_id != run_id:
                raise RuntimeError("pipeline returned a mismatched run ID")
            if artifact.hashes() != repeat.hashes():
                raise RuntimeError("full in-memory determinism gate failed")
            for name, content in artifact.serialized_outputs:
                if content != repeat.serialized(name):
                    raise RuntimeError(f"serialized determinism gate failed for {name}")
            contents = {
                "predictions": artifact.serialized("predictions"),
                "metrics": artifact.serialized("metrics"),
                "bootstrap": artifact.serialized("bootstrap"),
                "results": artifact.serialized("result"),
            }
            if any(
                len(content) >= e001.PUBLIC_LARGE_FILE_LIMIT
                for content in contents.values()
            ):
                raise RuntimeError("an intended output exceeds the public large-file limit")
            stage_paths = {
                name: _stage_bytes(stage_root, targets, name, content)
                for name, content in contents.items()
            }
            for name in FINALIZE_ORDER:
                targets[name].parent.mkdir(parents=True, exist_ok=True)
                replace_fn(stage_paths[name], targets[name])
                moved.append(name)
            return {
                "run_id": run_id,
                "protocol_version": e001.PROTOCOL_VERSION,
                "protocol_commit": e001.PROTOCOL_COMMIT,
                "status": "valid",
                "hashes": artifact.hashes(),
                "outputs": {name: str(path) for name, path in targets.items()},
            }
    except Exception as exc:
        # Put any already-finalized file back into the staging namespace using
        # the real primitive; this path is deliberately not a second injected
        # failure point in tests.
        for name in reversed(moved):
            target = targets[name]
            if target.exists():
                try:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with tempfile.TemporaryDirectory(prefix=".e001-rollback-", dir=str(output_root)) as rollback_name:
                        rollback_path = Path(rollback_name) / target.name
                        os.replace(target, rollback_path)
                except OSError:
                    pass
        _write_invalid_record(targets["results"], run_id, str(exc))
        raise InvalidRunError(str(exc)) from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run locked E001-v1 explicitly.")
    parser.add_argument("--run-id", required=True, help="new immutable run identifier")
    parser.add_argument(
        "--output-root",
        required=True,
        type=Path,
        help="root under which the protocol data/ and results/ paths are created",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        summary = execute_run(args.run_id, args.output_root)
    except (InvalidRunError, FileExistsError, RuntimeError, ValueError) as exc:
        print(f"E001 run invalid: {exc}", file=sys.stderr)
        return 2
    print(
        f"E001 run {summary['run_id']} finalized with status {summary['status']} "
        f"(protocol {summary['protocol_commit']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
