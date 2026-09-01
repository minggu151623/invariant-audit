"""Development and calibration-only checks for the locked E003-v1 code.

The real-fixture integration test is deliberately restricted to the frozen
2019 development and 2020 calibration shards.  The 2021 confirmatory payload
is never opened by this suite: a byte-read guard raises if its basename is
requested.  Future confirmatory execution is tested only with synthetic
artifacts and injected runner hooks.
"""

from __future__ import annotations

import copy
import gzip
import hashlib
import inspect
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import e003
import oracle_e003
import run_e003


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = Path("/private/tmp/invariant-audit-e003-v1/source-manifest.json")
CONFIRMATORY_BASENAME = e003.SOURCE_FILES["confirmatory"]


def _raw_issue(
    *,
    event_id: int | str = 100,
    repo_id: int | str = 1000,
    owner: str = "owner",
    name: str = "repository",
    issue_id: int | str = 200,
    number: int = 7,
    action: str = "opened",
    state: str | None = None,
) -> dict[str, object]:
    state = state or ("closed" if action == "closed" else "open")
    repo_url = f"https://api.github.com/repos/{owner}/{name}"
    return {
        "id": event_id,
        "type": "IssuesEvent",
        "actor": {
            "id": 900,
            "login": "fixture-actor",
            "ignored_actor_field": {"raw": "not projected"},
        },
        "repo": {
            "id": repo_id,
            "name": name,
            "url": repo_url,
            "ignored_repo_field": True,
        },
        "payload": {
            "action": action,
            "issue": {
                "id": issue_id,
                "number": number,
                "state": state,
                "url": f"{repo_url}/issues/{number}",
                "repository_url": repo_url,
                "title": "raw title is not projected",
            },
            "ignored_payload_field": "ignored",
        },
        "public": True,
        "created_at": "2020-01-15T12:00:00Z",
        "ignored_top_level": {"body": "raw text is not projected"},
    }


def _raw_pull_request(
    *,
    event_id: int | str = 300,
    repo_id: int | str = 2000,
    owner: str = "owner",
    name: str = "repository",
    pull_id: int | str = 400,
    number: int = 8,
    action: str = "opened",
    state: str | None = None,
    merged: bool = False,
) -> dict[str, object]:
    state = state or ("closed" if action == "closed" else "open")
    repo_url = f"https://api.github.com/repos/{owner}/{name}"
    return {
        "id": event_id,
        "type": "PullRequestEvent",
        "actor": {"id": 901, "login": "fixture-pr-actor"},
        "repo": {"id": repo_id, "name": name, "url": repo_url},
        "payload": {
            "action": action,
            "number": number,
            "pull_request": {
                "id": pull_id,
                "number": number,
                "state": state,
                "merged": merged,
                "url": f"{repo_url}/pulls/{number}",
                "title": "not projected",
            },
        },
        "public": True,
        "created_at": "2020-01-15T12:01:00Z",
    }


def _project(raw: dict[str, object]) -> dict[str, object]:
    projected, reason = e003.project_event(raw)
    if projected is None:
        raise AssertionError(f"fixture did not project: {reason}")
    return projected


def _source_event(raw: dict[str, object], split: str = "development") -> e003.SourceEvent:
    projected = _project(raw)
    repo_id = str(projected["repo"]["id"])
    event_id = str(projected["id"])
    event_type = str(projected["type"])
    return e003.SourceEvent(
        split=split,
        source_file=e003.SOURCE_FILES[split],
        source_sha256="a" * 64,
        source_line=int(event_id) + 1,
        repo_id=repo_id,
        event_id=event_id,
        event_type=event_type,
        action=str(projected["payload"]["action"]),
        payload=projected,
        input_sha256=e003.input_sha256(projected),
    )


def _dummy_manifest(source_root: Path | None = None) -> e003.SourceManifest:
    root = source_root or Path(tempfile.gettempdir()) / "e003-synthetic-source"
    files = tuple(
        e003.ManifestFile(
            split=split,
            filename=e003.SOURCE_FILES[split],
            url=e003.SOURCE_URLS[split],
            bytes=0,
            jsonl_lines=0,
            sha256="0" * 64,
        )
        for split in e003.SPLITS
    )
    return e003.SourceManifest(
        protocol_id=e003.PROTOCOL_VERSION,
        files=files,
        manifest_path=root / "source-manifest.json",
        source_root=root,
        manifest_sha256="b" * 64,
    )


def _bundle_for_events(events: list[e003.SourceEvent], split: str = "development") -> e003.SourceBundle:
    scan = e003.SourceScan(
        split=split,
        line_count=len(events),
        repo_ids=frozenset(event.repo_id for event in events),
        eligible=tuple(events),
        exclusion_counts=(),
    )
    return e003.SourceBundle(_dummy_manifest(), (scan,), frozenset())


def _quota_events(split: str = "development") -> list[e003.SourceEvent]:
    events: list[e003.SourceEvent] = []
    event_id = 10_000
    # Sixteen issue repositories and sixteen disjoint pull-request
    # repositories provide 32 overall clusters while respecting the cap of 4.
    for offset in range(16):
        for _ in range(4):
            events.append(
                _source_event(
                    _raw_issue(event_id=event_id, repo_id=1000 + offset, issue_id=event_id + 100),
                    split,
                )
            )
            event_id += 1
    for offset in range(16):
        for _ in range(4):
            events.append(
                _source_event(
                    _raw_pull_request(event_id=event_id, repo_id=2000 + offset, pull_id=event_id + 100),
                    split,
                )
            )
            event_id += 1
    return events


def _write_synthetic_source(
    directory: Path,
    records_by_split: dict[str, list[dict[str, object]]],
) -> Path:
    source_root = directory / "source"
    source_root.mkdir()
    manifest_files: list[dict[str, object]] = []
    for split in e003.SPLITS:
        records = records_by_split.get(split, [])
        filename = e003.SOURCE_FILES[split]
        if split in records_by_split:
            raw = b"".join(
                json.dumps(record, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
                + b"\n"
                for record in records
            )
            compressed = gzip.compress(raw)
            (source_root / filename).write_bytes(compressed)
            byte_count = len(compressed)
            line_count = len(records)
            digest = hashlib.sha256(compressed).hexdigest()
        else:
            byte_count = 0
            line_count = 0
            digest = "0" * 64
        manifest_files.append(
            {
                "bytes": byte_count,
                "filename": filename,
                "jsonl_lines": line_count,
                "sha256": digest,
                "split": split,
                "url": e003.SOURCE_URLS[split],
            }
        )
    manifest = {"files": manifest_files, "protocol_id": e003.PROTOCOL_VERSION}
    manifest_path = directory / "source-manifest.json"
    manifest_path.write_bytes(e003.canonical_jsonl_bytes(manifest))
    return manifest_path


def _prediction_row(
    *,
    method: str,
    truth: int,
    decision: bool,
    probability: Fraction,
    repo_id: str = "1",
    event_id: str = "1",
    event_type: str = "IssuesEvent",
    split: str = "confirmatory",
    variant_id: str = "clean",
) -> dict[str, object]:
    return {
        "protocol_id": e003.PROTOCOL_VERSION,
        "run_id": "e003-20260901-001",
        "source_file": "2021-01-15-12.json.gz",
        "source_sha256": "c" * 64,
        "source_line": 1,
        "split": split,
        "repo_id": repo_id,
        "event_id": event_id,
        "event_type": event_type,
        "base_event_id": event_id,
        "variant_id": variant_id,
        "case_kind": e003.VARIANT_KIND[variant_id],
        "truth": truth,
        "oracle_failure_set": [] if truth else ["identity"],
        "schema_valid": True,
        "method": method,
        "decision": decision,
        "raw_score": 0 if decision else 1,
        "p_valid": probability,
        "input_sha256": "d" * 64,
        "source_manifest_sha256": "e" * 64,
        "calibration_lookup_sha256": "f" * 64,
        "status": "valid",
    }


class E003CoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clean_issue = _project(_raw_issue())
        cls.clean_pr = _project(_raw_pull_request())
        cls.dev_cases = e003.build_cases(
            {"development": (_source_event(_raw_issue()), _source_event(_raw_pull_request(), "development"))},
            oracle_e003.reference_oracle,
        )["development"]

    def test_protocol_constants_and_future_paths_are_locked(self) -> None:
        self.assertEqual(e003.PROTOCOL_VERSION, "E003-v1")
        self.assertEqual(e003.PROTOCOL_COMMIT, "163e44dcabc698f101dee70dd7f3aa1bb7c8d5fb")
        self.assertEqual(len(e003.PROTOCOL_BLOB_SHA256), 64)
        self.assertEqual(e003.CASES_PER_SPLIT, 512)
        self.assertEqual(e003.EXPECTED_BOOTSTRAP_ROWS, 150_000)
        self.assertEqual(
            run_e003._final_paths(Path("/repo"), "e003-20260901-001"),
            {
                "predictions": Path("/repo/data/E003-v1-predictions.jsonl"),
                "metrics": Path("/repo/data/E003-v1-metrics.csv"),
                "bootstrap": Path("/repo/data/E003-v1-bootstrap.csv"),
                "result": Path(
                    "/repo/experiments/E003-external-transfer-validation/results/run-e003-20260901-001.md"
                ),
            },
        )

    def test_projection_normalizes_decimal_ids_and_drops_unknown_raw_fields(self) -> None:
        raw = _raw_issue(event_id="100", repo_id="1000", issue_id="200")
        projected = _project(raw)
        self.assertEqual(projected["id"], "100")
        self.assertEqual(projected["repo"]["id"], "1000")
        self.assertNotIn("ignored_top_level", projected)
        self.assertNotIn("ignored_actor_field", projected["actor"])
        self.assertNotIn("title", projected["payload"]["issue"])
        self.assertEqual(e003.input_sha256(projected), hashlib.sha256(
            e003.canonical_json_bytes(projected) + b"\n"
        ).hexdigest())

    def test_decimal_id_timestamp_and_url_boundaries_fail_closed(self) -> None:
        raw = _raw_issue()
        for bad_id in (True, -1, "", "+1", "01", 1.0, "1.0"):
            candidate = copy.deepcopy(raw)
            candidate["id"] = bad_id
            projected, reason = e003.project_event(candidate)
            self.assertIsNone(projected, bad_id)
            self.assertEqual(reason, "common_schema", bad_id)
        for bad_url in (
            "http://api.github.com/repos/owner/repository",
            "https://api.github.com/repos/owner/repository?x=1",
            "https://api.github.com/repos/owner/repository/issues/0",
            "https://api.github.com/repos/owner/repository/issues/7/extra",
        ):
            candidate = copy.deepcopy(raw)
            candidate["payload"]["issue"]["url"] = bad_url
            projected, reason = e003.project_event(candidate)
            self.assertIsNone(projected)
            self.assertEqual(reason, "event_specific_schema")
        for timestamp in ("2020-02-30T12:00:00Z", "2020-01-15T12:00:00+00:00", "2020-01-15Z"):
            candidate = copy.deepcopy(raw)
            candidate["created_at"] = timestamp
            self.assertEqual(e003.project_event(candidate)[1], "common_schema")

    def test_action_state_and_merged_pull_request_rules(self) -> None:
        closed_merged = _project(_raw_pull_request(action="closed", state="closed", merged=True))
        self.assertEqual(oracle_e003.reference_oracle(closed_merged).oracle_failure_set, ())
        opened_merged = copy.deepcopy(self.clean_pr)
        opened_merged["payload"]["pull_request"]["merged"] = True
        oracle = oracle_e003.reference_oracle(opened_merged)
        self.assertTrue(oracle.schema_valid)
        self.assertEqual(oracle.oracle_failure_set, ("state",))
        self.assertTrue(e003.validate_b0(opened_merged).decision)
        self.assertFalse(e003.validate_m1(opened_merged).decision)
        invalid_action = copy.deepcopy(self.clean_issue)
        invalid_action["payload"]["action"] = "edited"
        self.assertEqual(e003.project_event(invalid_action)[1], "event_specific_schema")
        self.assertEqual(oracle_e003.reference_oracle(invalid_action).oracle_failure_set, ("schema",))

    def test_oracle_is_separate_and_perturbations_are_one_sided(self) -> None:
        source = inspect.getsource(oracle_e003)
        self.assertNotIn("import e003", source)
        self.assertNotIn("validate_method", source)
        self.assertNotIn("M1_CHECKS", source)
        clean = self.clean_issue
        original_method = e003.M1_CHECKS["identity"]
        original_oracle = oracle_e003._identity_relation
        try:
            e003.M1_CHECKS["identity"] = lambda _payload: False
            self.assertEqual(oracle_e003.reference_oracle(clean).oracle_failure_set, ())
            self.assertFalse(e003.validate_m1(clean).decision)
            e003.M1_CHECKS["identity"] = original_method
            oracle_e003._identity_relation = lambda _payload: False
            self.assertEqual(e003.validate_m1(clean).oracle_failure_set if False else (), ())
            self.assertTrue(e003.validate_m1(clean).decision)
            self.assertEqual(oracle_e003.reference_oracle(clean).oracle_failure_set, ("identity",))
        finally:
            e003.M1_CHECKS["identity"] = original_method
            oracle_e003._identity_relation = original_oracle

    def test_fail_closed_oracle_and_methods_on_malformed_shapes(self) -> None:
        malformed = [None, [], {}, {"id": "1", "type": "IssuesEvent"}]
        for field in ("actor", "repo", "payload", "created_at", "public"):
            candidate = copy.deepcopy(self.clean_issue)
            candidate[field] = None
            malformed.append(candidate)
        for candidate in malformed:
            oracle = oracle_e003.reference_oracle(candidate)
            self.assertFalse(oracle.schema_valid, repr(candidate))
            self.assertEqual(oracle.truth, 0)
            self.assertEqual(oracle.oracle_failure_set, ("schema",))
            for method in e003.METHODS:
                try:
                    result = e003.validate_method(candidate, method)
                except Exception as error:  # pragma: no cover - diagnostic failure
                    self.fail(f"{method} raised: {error!r}")
                self.assertFalse(result.decision)

    def test_mutations_are_independent_exact_and_have_known_oracle_answers(self) -> None:
        for base in (
            _source_event(_raw_issue()),
            _source_event(_raw_pull_request()),
        ):
            cases = e003.build_cases({"development": (base,)}, oracle_e003.reference_oracle)["development"]
            clean = next(case for case in cases if case.variant_id == "clean")
            expected = {
                "clean": (),
                "S1-missing-resource": ("schema",),
                "I1-wrong-repository": ("identity",),
                "T1-status-contradiction": ("state",),
            }
            for case in cases:
                self.assertEqual(case.oracle_failure_set, expected[case.variant_id])
                self.assertEqual(case.truth, int(not case.oracle_failure_set))
                if case.variant_id == "clean":
                    wanted = set()
                elif case.variant_id == "S1-missing-resource":
                    resource = "issue" if base.event_type == "IssuesEvent" else "pull_request"
                    wanted = {("payload", resource)}
                elif case.variant_id == "I1-wrong-repository":
                    path = "issue" if base.event_type == "IssuesEvent" else "pull_request"
                    leaf = "repository_url" if base.event_type == "IssuesEvent" else "url"
                    wanted = {("payload", path, leaf)}
                else:
                    path = "issue" if base.event_type == "IssuesEvent" else "pull_request"
                    wanted = {("payload", path, "state")}
                self.assertEqual(e003.mutation_diff_paths(clean.payload, case.payload), wanted)
            self.assertEqual(len(cases), 4)

    def test_case_construction_does_not_pass_labels_to_methods(self) -> None:
        cases = self.dev_cases
        captured: list[object] = []
        original = e003.validate_method

        def capture(payload: object, method: str) -> e003.ValidationResult:
            captured.append(payload)
            return original(payload, method)

        try:
            e003.validate_method = capture  # type: ignore[assignment]
            rows = e003.evaluate_cases(cases, "M1")
        finally:
            e003.validate_method = original  # type: ignore[assignment]
        self.assertEqual(len(rows), len(cases))
        self.assertTrue(captured)
        self.assertTrue(all(set(payload) == {
            "id", "type", "actor", "repo", "payload", "public", "created_at"
        } for payload in captured))
        self.assertTrue(all(
            "truth" not in payload and "variant_id" not in payload and "split" not in payload
            for payload in captured
        ))

    def test_b0_m1_and_ablation_family_semantics(self) -> None:
        cases = e003.build_cases(
            {"development": (_source_event(_raw_issue()), _source_event(_raw_pull_request()))},
            oracle_e003.reference_oracle,
        )["development"]
        for case in cases:
            b0 = e003.validate_method(case.payload, "B0")
            m1 = e003.validate_method(case.payload, "M1")
            no_identity = e003.validate_method(case.payload, "M1-no-identity")
            no_state = e003.validate_method(case.payload, "M1-no-state")
            no_cal = e003.validate_method(case.payload, "M1-no-calibration")
            self.assertEqual(b0.decision, case.variant_id != "S1-missing-resource")
            self.assertEqual(m1.decision, case.variant_id == "clean")
            self.assertEqual(no_cal, m1)
            self.assertEqual(no_identity.decision, case.variant_id not in {
                "S1-missing-resource", "T1-status-contradiction"
            })
            self.assertEqual(no_state.decision, case.variant_id not in {
                "S1-missing-resource", "I1-wrong-repository"
            })
            self.assertIn(b0.raw_score, (0, 1))
            self.assertGreaterEqual(m1.raw_score, 0)

    def test_selection_is_deterministic_quota_capped_and_isolated(self) -> None:
        events = _quota_events()
        first = e003.select_bases(_bundle_for_events(events))
        second = e003.select_bases(_bundle_for_events(list(reversed(events))))
        self.assertEqual(
            [(event.event_type, event.repo_id, event.event_id) for event in first["development"]],
            [(event.event_type, event.repo_id, event.event_id) for event in second["development"]],
        )
        self.assertEqual(len(first["development"]), 128)
        self.assertEqual(len({event.repo_id for event in first["development"]}), 32)
        per_group = {}
        for event in first["development"]:
            per_group[(event.repo_id, event.event_type)] = per_group.get((event.repo_id, event.event_type), 0) + 1
        self.assertTrue(all(value <= 4 for value in per_group.values()))
        self.assertEqual(len({event.input_sha256 for event in first["development"]}), 128)

    def test_source_group_isolation_removes_shared_repository_ids(self) -> None:
        with tempfile.TemporaryDirectory(prefix="e003-isolation-") as name:
            root = Path(name)
            records = {
                "development": [_raw_issue(event_id=1, repo_id=10)],
                "calibration": [_raw_issue(event_id=2, repo_id=10), _raw_pull_request(event_id=3, repo_id=20)],
            }
            manifest_path = _write_synthetic_source(root, records)
            manifest = e003.load_manifest(manifest_path)
            e003.verify_source_hashes(manifest, ("development", "calibration"))
            bundle = e003.scan_sources(manifest, oracle_e003.reference_oracle, ("development", "calibration"))
            self.assertEqual(bundle.shared_repo_ids, frozenset({"10"}))
            self.assertEqual(bundle.eligible("development"), ())
            self.assertEqual(len(bundle.eligible("calibration")), 1)
            self.assertEqual(bundle.scan_for("development").exclusions()["cross_split_repository"], 1)

    def test_source_parser_rejects_duplicate_ids_and_trailing_gzip_bytes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="e003-source-") as name:
            root = Path(name)
            duplicate = [_raw_issue(event_id=1), _raw_issue(event_id=1, number=9)]
            manifest_path = _write_synthetic_source(root, {"development": duplicate})
            manifest = e003.load_manifest(manifest_path)
            e003.verify_source_hashes(manifest, ("development",))
            with self.assertRaises(e003.ProtocolError):
                e003.scan_sources(manifest, oracle_e003.reference_oracle, ("development",))
        with tempfile.TemporaryDirectory(prefix="e003-gzip-") as name:
            root = Path(name)
            manifest_path = _write_synthetic_source(root, {"development": [_raw_issue()]})
            path = root / "source" / e003.SOURCE_FILES["development"]
            path.write_bytes(path.read_bytes() + b"trailing-binary")
            manifest = e003.load_manifest(manifest_path)
            with self.assertRaises(e003.ProtocolError):
                e003.verify_source_hashes(manifest, ("development",))
            # Rebuild the manifest for the malformed compressed bytes so the
            # decompression gate itself, rather than the hash gate, is tested.
            compressed = path.read_bytes()
            digest = hashlib.sha256(compressed).hexdigest()
            manifest_obj = {
                "files": [
                    {
                        "bytes": len(compressed) if split == "development" else 0,
                        "filename": e003.SOURCE_FILES[split],
                        "jsonl_lines": 1 if split == "development" else 0,
                        "sha256": digest if split == "development" else "0" * 64,
                        "split": split,
                        "url": e003.SOURCE_URLS[split],
                    }
                    for split in e003.SPLITS
                ],
                "protocol_id": e003.PROTOCOL_VERSION,
            }
            manifest_path.write_bytes(e003.canonical_jsonl_bytes(manifest_obj))
            manifest = e003.load_manifest(manifest_path)
            e003.verify_source_hashes(manifest, ("development",))
            with self.assertRaises(e003.ProtocolError):
                list(e003._iter_source_records(manifest, "development"))

    def test_calibration_formula_isolated_and_marker_hash_is_exact(self) -> None:
        cases = e003.build_cases(
            {
                "calibration": (
                    _source_event(_raw_issue(event_id=11), "calibration"),
                    _source_event(_raw_pull_request(event_id=12), "calibration"),
                )
            },
            oracle_e003.reference_oracle,
        )
        rows = e003.evaluate_all_methods(cases)
        lookup = e003.fit_calibration_lookup("M1", rows)
        self.assertEqual(lookup.lookup(0), Fraction(3, 4))
        self.assertEqual(lookup.lookup(1), Fraction(1, 8))
        self.assertEqual(
            e003.NO_CALIBRATION_MARKER_SHA256,
            hashlib.sha256(e003.NO_CALIBRATION_MARKER.encode("utf-8")).hexdigest(),
        )
        with self.assertRaises(e003.ProtocolError):
            e003.fit_calibration_lookup(
                "M1",
                list(rows) + [{"method": "M1", "split": "confirmatory", "case_key": ("x",), "truth": 1, "raw_score": 0}],
            )
        self.assertEqual(tuple(lookup.record()), ("method", "entries", "global_p_valid"))
        self.assertEqual(lookup.serialized(), e003.canonical_jsonl_bytes(lookup.record()))
        self.assertEqual(lookup.sha256(), hashlib.sha256(lookup.serialized()).hexdigest())

    def test_metrics_exact_arithmetic_bins_and_na_policy(self) -> None:
        rows = [
            _prediction_row(method="B0", truth=1, decision=True, probability=Fraction(1)),
            _prediction_row(method="B0", truth=0, decision=False, probability=Fraction(0), repo_id="2", event_id="2"),
            _prediction_row(method="B0", truth=1, decision=False, probability=Fraction(1, 2), repo_id="3", event_id="3"),
            _prediction_row(method="B0", truth=0, decision=True, probability=Fraction(1, 2), repo_id="4", event_id="4"),
        ]
        metrics = e003.compute_metrics(rows, method="B0", split="confirmatory", subgroup="overall")
        self.assertEqual(
            {field: metrics[field] for field in ("support", "positive_count", "negative_count", "tp", "tn", "fp", "fn")},
            {"support": 4, "positive_count": 2, "negative_count": 2, "tp": 1, "tn": 1, "fp": 1, "fn": 1},
        )
        self.assertEqual(metrics["balanced_accuracy"], Fraction(1, 2))
        self.assertEqual(metrics["fpr"], Fraction(1, 2))
        self.assertEqual(metrics["fnr"], Fraction(1, 2))
        self.assertEqual(metrics["brier"], Fraction(1, 8))
        empty = e003.compute_metrics(rows, method="B0", split="confirmatory", subgroup="type:PullRequestEvent")
        self.assertTrue(all(empty[field] is None for field in e003.METRICS))
        self.assertEqual(e003.csv_value(None), "NA")
        csv_bytes = e003.serialize_csv(
            [{"row_kind": "pair", **{field: None for field in e003.METRIC_FIELDS if field != "row_kind"}}],
            e003.METRIC_FIELDS,
        )
        self.assertTrue(csv_bytes.startswith((",".join(e003.METRIC_FIELDS) + "\n").encode()))
        self.assertIn(b",NA,", csv_bytes)

    def test_bootstrap_hash_index_percentile_and_determinism(self) -> None:
        expected_index = int(hashlib.sha256(
            b"E003-v1|bootstrap|overall|balanced_accuracy|0|0"
        ).hexdigest(), 16) % 24
        self.assertEqual(e003.bootstrap_index("overall", "balanced_accuracy", 0, 0, 24), expected_index)
        self.assertEqual(e003.percentile([Fraction(0), Fraction(2)], Fraction(1, 4)), Fraction(1, 2))
        rows: list[dict[str, object]] = []
        for repo in range(24):
            repo_id = str(100 + repo)
            for event_type in ("IssuesEvent", "PullRequestEvent"):
                for method in e003.PRIMARY_METHODS:
                    rows.append(_prediction_row(
                        method=method,
                        truth=repo % 2,
                        decision=(method == "M1" and repo % 2 == 1),
                        probability=Fraction(1, 2),
                        repo_id=repo_id,
                        event_id=f"{repo}-{event_type}",
                        event_type=event_type,
                    ))
        first = e003.bootstrap_confirmatory(rows, replicates=31)
        second = e003.bootstrap_confirmatory(rows, replicates=31)
        self.assertEqual(first, second)
        self.assertEqual(first.replicate_count, 31)
        self.assertEqual(len(first.cluster_ids), 24)
        self.assertEqual(len(e003.build_bootstrap_rows(first, "e003-20260901-001")), 31 * 15)
        self.assertEqual(e003.expected_bootstrap_row_count(first), 31 * 15)
        self.assertTrue(all(item["usable_replicates"] == 31 for item in first.intervals))

    def test_bootstrap_undefined_denominators_are_literal_na(self) -> None:
        rows = [
            _prediction_row(method="B0", truth=1, decision=True, probability=Fraction(1), repo_id="1"),
            _prediction_row(method="M1", truth=1, decision=True, probability=Fraction(1), repo_id="1"),
        ]
        result = e003.bootstrap_confirmatory(rows, replicates=5, enforce_minimum=False)
        fpr = result.interval("overall", "fpr")
        self.assertEqual(fpr["status"], "undefined")
        self.assertEqual(fpr["usable_replicates"], 0)
        fpr_rows = [row for row in e003.build_bootstrap_rows(result, "e003-20260901-001") if row["metric"] == "fpr"]
        self.assertTrue(all(row["delta"] is None and row["status"] == "undefined" for row in fpr_rows))

    def test_prediction_metric_bootstrap_schemas_and_canonical_lf(self) -> None:
        cases = e003.build_cases(
            {"development": (_source_event(_raw_issue()),)}, oracle_e003.reference_oracle
        )
        raw = e003.evaluate_all_methods(cases)
        # Give the small synthetic set a calibration split solely to exercise
        # the canonical prediction schema without building a holdout result.
        calibration_cases = e003.build_cases(
            {"calibration": (_source_event(_raw_issue(event_id=2), "calibration"),)},
            oracle_e003.reference_oracle,
        )
        all_cases = {**cases, **calibration_cases}
        all_raw = e003.evaluate_all_methods(all_cases)
        calibration_raw = tuple(
            row for row in all_raw if row.get("split") == "calibration"
        )
        lookups = e003.fit_all_calibrations(calibration_raw)
        predictions = e003.build_prediction_rows(
            "e003-20260901-001", all_cases, all_raw, lookups, "1" * 64
        )
        self.assertTrue(all(tuple(row) == e003.PREDICTION_FIELDS for row in predictions))
        encoded = e003.serialize_jsonl(predictions)
        self.assertTrue(encoded.endswith(b"\n"))
        decoded = json.loads(encoded.splitlines()[0])
        self.assertEqual(set(decoded), set(e003.PREDICTION_FIELDS))
        self.assertIsInstance(decoded["decision"], bool)
        self.assertIsInstance(decoded["oracle_failure_set"], list)
        self.assertTrue(all(not line.endswith(b"\r") for line in encoded.splitlines()))
        metrics = e003.build_metric_rows(
            predictions,
            run_id="e003-20260901-001",
            source_manifest_sha256="1" * 64,
        )
        self.assertEqual(len(metrics), 54)
        self.assertEqual(e003.serialize_csv(metrics, e003.METRIC_FIELDS).splitlines()[0].decode(), ",".join(e003.METRIC_FIELDS))

    def test_development_calibration_integration_is_exact_and_confirmatory_guarded(self) -> None:
        if not MANIFEST_PATH.is_file():
            self.fail(f"frozen development/calibration manifest missing: {MANIFEST_PATH}")
        opened: list[str] = []
        original = e003._read_source_bytes

        def guarded(path: Path) -> bytes:
            opened.append(path.name)
            if path.name == CONFIRMATORY_BASENAME:
                raise AssertionError("development/calibration preflight opened confirmatory gzip")
            return original(path)

        started = time.perf_counter()
        with mock.patch.object(e003, "_read_source_bytes", side_effect=guarded):
            evidence = e003.build_development_calibration_preflight(MANIFEST_PATH)
        elapsed = time.perf_counter() - started
        self.assertEqual(evidence.split_base_counts, (("development", 64), ("calibration", 64)))
        self.assertEqual(evidence.split_case_counts, (("development", 512), ("calibration", 512)))
        self.assertGreaterEqual(dict(evidence.split_repository_counts)["development"], 24)
        self.assertGreaterEqual(dict(evidence.split_repository_counts)["calibration"], 24)
        self.assertEqual(evidence.raw_row_count, 512 * 2 * len(e003.METHODS))
        self.assertFalse(evidence.confirmatory_scored)
        self.assertFalse(evidence.confirmatory_metrics_constructed)
        self.assertEqual(set(opened), {
            e003.SOURCE_FILES["development"], e003.SOURCE_FILES["calibration"]
        })
        self.assertEqual(len(evidence.calibration_lookup_hashes), len(e003.CALIBRATED_METHODS))
        self.assertTrue(all(len(digest) == 64 for _, digest in evidence.calibration_lookup_hashes))
        self.assertLess(elapsed, 90.0)


class E003RunnerTests(unittest.TestCase):
    @staticmethod
    def _fake_manifest(tmp: Path) -> e003.SourceManifest:
        return _dummy_manifest(tmp)

    @staticmethod
    def _fake_artifact(run_id: str, suffix: str = "") -> SimpleNamespace:
        contents = {
            "predictions": f"predictions{suffix}\n".encode(),
            "metrics": f"metrics{suffix}\n".encode(),
            "bootstrap": f"bootstrap{suffix}\n".encode(),
            "result": f"result{suffix}\n".encode(),
        }
        artifact = SimpleNamespace(run_id=run_id, serialized_outputs=tuple(contents.items()))
        artifact.serialized = lambda name: contents[name]
        artifact.hashes = lambda: {name: hashlib.sha256(data).hexdigest() for name, data in contents.items()}
        return artifact

    def test_cli_requires_explicit_run_id_output_root_and_manifest(self) -> None:
        parser = run_e003.build_argument_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args([])
        options = parser.parse_args([
            "--run-id", "e003-20260901-001",
            "--output-root", "/tmp/repo",
            "--source-manifest", "/tmp/source-manifest.json",
        ])
        self.assertEqual(options.run_id, "e003-20260901-001")
        with self.assertRaises(run_e003.InvalidRunError):
            run_e003._validate_run_id("e003-20260230-001")
        with self.assertRaises(run_e003.InvalidRunError):
            run_e003._validate_run_id("e003-20260901-1")

    def test_runner_import_has_no_side_effects(self) -> None:
        env = dict(os.environ)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run(
            [sys.executable, "-c", "import e003, oracle_e003, run_e003"],
            cwd=Path(__file__).parent,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout, "")
        self.assertEqual(completed.stderr, "")

    def test_runner_guard_precedes_output_root_creation_and_success_is_atomic(self) -> None:
        with tempfile.TemporaryDirectory(prefix="e003-runner-") as name:
            output_root = Path(name) / "future-output"
            repository = Path(name) / "repository"
            repository.mkdir()
            manifest_path = Path(name) / "manifest.json"
            manifest_path.write_bytes(b"synthetic manifest placeholder")
            observed: list[bool] = []
            artifact = self._fake_artifact("e003-20260901-001")

            def guard(_repo: Path, destination: Path, _paths: Mapping[str, Path], _manifest: Path) -> None:
                observed.append(destination.exists())
                self.assertFalse(destination.exists())

            calls: list[int] = []

            def factory(*_args: object) -> SimpleNamespace:
                calls.append(1)
                return artifact

            outcome = run_e003.execute_run(
                "e003-20260901-001",
                output_root,
                manifest_path,
                repository_root=repository,
                protocol_guard_fn=guard,
                source_preflight_fn=lambda _path, _root: self._fake_manifest(Path(name)),
                pipeline_factory=factory,
                artifact_validator_fn=lambda _artifact: None,
            )
            self.assertEqual(observed, [False])
            self.assertEqual(len(calls), 2)
            self.assertEqual(outcome["status"], "valid")
            final_paths = run_e003._final_paths(output_root, "e003-20260901-001")
            self.assertEqual(
                {label: path.read_bytes() for label, path in final_paths.items()},
                dict(artifact.serialized_outputs),
            )
            self.assertFalse(any(path.name.startswith(".e003-stage-") for path in output_root.iterdir()))

    def test_runner_output_absence_and_two_build_mismatch_fail_before_staging(self) -> None:
        with tempfile.TemporaryDirectory(prefix="e003-runner-guard-") as name:
            root = Path(name)
            output_root = root / "output"
            repository = root / "repo"
            repository.mkdir()
            manifest_path = root / "manifest.json"
            manifest_path.write_bytes(b"placeholder")
            run_id = "e003-20260901-002"
            target = run_e003._final_paths(output_root, run_id)["predictions"]
            target.parent.mkdir(parents=True)
            target.write_bytes(b"preexisting")
            calls: list[int] = []

            def guard(_repo: Path, _destination: Path, paths: Mapping[str, Path], _manifest: Path) -> None:
                if any(path.exists() for path in paths.values()):
                    raise run_e003.InvalidRunError("output already exists")

            with self.assertRaises(run_e003.InvalidRunError):
                run_e003.execute_run(
                    run_id,
                    output_root,
                    manifest_path,
                    repository_root=repository,
                    protocol_guard_fn=guard,
                    pipeline_factory=lambda *_args: calls.append(1) or self._fake_artifact(run_id),
                )
            self.assertEqual(calls, [])
            target.write_bytes(b"removed-for-next-test")
            target.unlink()
            calls.clear()

            def changing_factory(*_args: object) -> SimpleNamespace:
                index = len(calls)
                calls.append(1)
                return self._fake_artifact(run_id, suffix=str(index))

            with self.assertRaises(run_e003.InvalidRunError):
                run_e003.execute_run(
                    run_id,
                    output_root,
                    manifest_path,
                    repository_root=repository,
                    protocol_guard_fn=guard,
                    source_preflight_fn=lambda _path, _root: self._fake_manifest(root),
                    pipeline_factory=changing_factory,
                    artifact_validator_fn=lambda _artifact: None,
                )
            self.assertEqual(len(calls), 2)
            target.parent.rmdir()
            output_root.rmdir()
            self.assertFalse(output_root.exists())

    def test_runner_staging_failure_cleans_all_finals_and_writes_only_concise_invalid_record(self) -> None:
        with tempfile.TemporaryDirectory(prefix="e003-runner-invalid-") as name:
            root = Path(name)
            output_root = root / "output"
            repository = root / "repo"
            repository.mkdir()
            manifest_path = root / "manifest.json"
            manifest_path.write_bytes(b"placeholder")
            run_id = "e003-20260901-003"
            artifact = self._fake_artifact(run_id)

            def guard(_repo: Path, _destination: Path, _paths: Mapping[str, Path], _manifest: Path) -> None:
                return None

            def fail_staged(_paths: Mapping[str, Path], _contents: Mapping[str, bytes]) -> None:
                raise run_e003.InvalidRunError("synthetic staged validation failure")

            with self.assertRaises(run_e003.InvalidRunError):
                run_e003.execute_run(
                    run_id,
                    output_root,
                    manifest_path,
                    repository_root=repository,
                    protocol_guard_fn=guard,
                    source_preflight_fn=lambda _path, _root: self._fake_manifest(root),
                    pipeline_factory=lambda *_args: artifact,
                    artifact_validator_fn=lambda _artifact: None,
                    staged_validator_fn=fail_staged,
                )
            paths = run_e003._final_paths(output_root, run_id)
            self.assertTrue(paths["result"].is_file())
            self.assertEqual(paths["result"].read_bytes(), run_e003._invalid_result_bytes(run_id))
            self.assertTrue(all(not paths[name].exists() for name in ("predictions", "metrics", "bootstrap")))
            self.assertEqual(paths["result"].read_text(encoding="utf-8").count("metrics"), 1)
            self.assertNotIn("synthetic", paths["result"].read_text(encoding="utf-8"))
            self.assertFalse(any(path.name.startswith(".e003-stage-") for path in output_root.iterdir()))

    def test_runner_factory_failure_is_pre_staging_and_has_no_retry_or_invalid_record(self) -> None:
        with tempfile.TemporaryDirectory(prefix="e003-runner-pre-") as name:
            root = Path(name)
            output_root = root / "output"
            repository = root / "repo"
            repository.mkdir()
            manifest_path = root / "manifest.json"
            manifest_path.write_bytes(b"placeholder")
            calls: list[int] = []

            def factory(*_args: object) -> object:
                calls.append(1)
                raise RuntimeError("factory failure")

            with self.assertRaises(run_e003.InvalidRunError):
                run_e003.execute_run(
                    "e003-20260901-004",
                    output_root,
                    manifest_path,
                    repository_root=repository,
                    protocol_guard_fn=lambda *_args: None,
                    source_preflight_fn=lambda _path, _root: self._fake_manifest(root),
                    pipeline_factory=factory,
                )
            self.assertEqual(len(calls), 1)
            self.assertFalse(output_root.exists())

    def test_invalid_record_is_exact_protocol_shape(self) -> None:
        value = run_e003._invalid_result_bytes("e003-20260901-005").decode("utf-8")
        self.assertEqual(value.splitlines(), [
            "# E003-v1 invalid run — e003-20260901-005",
            "status: invalid",
            "protocol_id: E003-v1",
            f"protocol_commit: {e003.PROTOCOL_COMMIT}",
            "run_id: e003-20260901-005",
            "failure_class: invalid-run",
            "No metrics or evidence exist.",
            "corrected_run_requires_new_id: true",
        ])
        self.assertTrue(value.endswith("\n"))


if __name__ == "__main__":
    unittest.main()
