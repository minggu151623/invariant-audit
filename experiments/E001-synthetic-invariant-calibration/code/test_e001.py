"""Development-only tests for the locked E001-v1 implementation.

These tests exercise the generator, validators, calibration, metrics, and
writer machinery with local synthetic/development fixtures.  They never call
the future confirmatory CLI or print confirmatory metrics.
"""

from __future__ import annotations

import copy
import hashlib
import inspect
import os
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

import e001
import run_e001


class E001HarnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.datasets = e001.generate_all_splits()
        cls.dev_cases = cls.datasets["development"]

    @staticmethod
    def _cases_for_base(cases: list[e001.Case], base_case_id: str) -> dict[tuple[str, bool], e001.Case]:
        return {
            (case.target_family, case.valid): case
            for case in cases
            if case.base_case_id == base_case_id
        }

    @staticmethod
    def _diff_paths(left: object, right: object, path: tuple[object, ...] = ()) -> set[tuple[object, ...]]:
        if type(left) is not type(right):
            return {path}
        if isinstance(left, dict):
            keys = set(left) | set(right)
            return {
                child
                for key in keys
                for child in E001HarnessTests._diff_paths(
                    left.get(key), right.get(key), path + (key,)
                )
            }
        if isinstance(left, list):
            differences: set[tuple[object, ...]] = set()
            if len(left) != len(right):
                differences.add(path + ("length",))
            for index in range(min(len(left), len(right))):
                differences.update(
                    E001HarnessTests._diff_paths(left[index], right[index], path + (index,))
                )
            return differences
        return set() if left == right else {path}

    def test_exact_split_counts_clusters_quotas_and_disjointness(self) -> None:
        expected_counts = {"development": 256, "calibration": 256, "confirmatory": 512}
        self.assertEqual({name: len(rows) for name, rows in self.datasets.items()}, expected_counts)
        base_ids = {
            split: {case.base_case_id for case in cases}
            for split, cases in self.datasets.items()
        }
        self.assertEqual({split: len(ids) for split, ids in base_ids.items()}, {
            "development": 32,
            "calibration": 32,
            "confirmatory": 64,
        })
        self.assertEqual(base_ids["development"] & base_ids["calibration"], set())
        self.assertEqual(base_ids["development"] & base_ids["confirmatory"], set())
        self.assertEqual(base_ids["calibration"] & base_ids["confirmatory"], set())
        for split, cases in self.datasets.items():
            self.assertEqual(sum(case.truth for case in cases), len(cases) // 2)
            for base_id in base_ids[split]:
                cluster = [case for case in cases if case.base_case_id == base_id]
                self.assertEqual(len(cluster), e001.CASES_PER_BASE)
                self.assertEqual(
                    {(case.target_family, case.valid) for case in cluster},
                    {(family, valid) for family in e001.FAMILIES for valid in (True, False)},
                )
            for family in e001.FAMILIES:
                self.assertEqual(
                    sum(case.target_family == family for case in cases), len(cases) // 4
                )
        self.assertEqual(e001.sanity_check_dataset(self.datasets)["total_cases"], 1024)

    def test_exact_amount_hashes_and_base_shapes_across_every_base(self) -> None:
        for split, seeds in e001.SPLIT_SEEDS.items():
            for seed in seeds:
                for base_index in range(e001.BASE_BUNDLES_PER_SEED):
                    payload = e001.generate_base_payload(split, seed, base_index)
                    self.assertEqual(len(payload["entities"]), 4)
                    self.assertEqual(len(payload["ledger"]), 4)
                    self.assertEqual(len(payload["events"]), 7)
                    expected_amounts = []
                    for draw_index in range(4):
                        material = (
                            f"{e001.PROTOCOL_VERSION}|value|{split}|{seed}|"
                            f"{base_index}|{draw_index}"
                        ).encode("utf-8")
                        digest = hashlib.sha256(material).digest()
                        expected_amounts.append(200 + int.from_bytes(digest[:8], "big") % 300)
                    self.assertEqual(
                        [row["amount_cents"] for row in payload["ledger"]], expected_amounts
                    )
                    self.assertEqual(
                        payload["meta"]["declared_total_cents"], sum(expected_amounts)
                    )
                    self.assertEqual(e001.reference_oracle(payload).truth, 1)

    def test_byte_determinism_and_dataset_hash(self) -> None:
        regenerated = e001.generate_all_splits()
        self.assertEqual(
            e001.dataset_canonical_bytes(self.datasets),
            e001.dataset_canonical_bytes(regenerated),
        )
        self.assertEqual(e001.dataset_sha256(self.datasets), e001.dataset_sha256(regenerated))
        for split in e001.SPLIT_SEEDS:
            self.assertEqual(
                [case.input_sha256 for case in self.datasets[split]],
                [case.input_sha256 for case in regenerated[split]],
            )

    def test_runtime_sanity_gate_rejects_faulty_b0_and_recipe_footprint(self) -> None:
        sanity = e001.runtime_sanity_check(self.datasets)
        self.assertEqual(sanity["runtime_b0_cases"], 1024)
        self.assertEqual(sanity["recipe_footprints_checked"], 1024)
        self.assertIn(
            "runtime_sanity_check(cases_by_split)",
            inspect.getsource(e001.build_pipeline),
        )

        original_b0 = e001.validate_b0
        try:
            e001.validate_b0 = lambda _: e001.ValidationResult(False, 1)  # type: ignore[assignment]
            with self.assertRaises(e001.ProtocolError):
                e001.runtime_sanity_check(self.datasets)
        finally:
            e001.validate_b0 = original_b0  # type: ignore[assignment]

        target_index = next(
            index
            for index, case in enumerate(self.dev_cases)
            if case.target_family == "S1" and case.valid
        )
        target = self.dev_cases[target_index]
        faulty_payload = copy.deepcopy(target.payload)
        faulty_payload["entities"][0], faulty_payload["entities"][1] = (
            faulty_payload["entities"][1],
            faulty_payload["entities"][0],
        )
        faulty_cases = {split: list(cases) for split, cases in self.datasets.items()}
        faulty_cases["development"][target_index] = replace(
            target, payload=faulty_payload
        )
        with self.assertRaises(e001.ProtocolError):
            e001.runtime_sanity_check(faulty_cases)

    def test_all_recipes_and_oracle_isolation_across_every_base(self) -> None:
        for split, cases in self.datasets.items():
            for base_id in {case.base_case_id for case in cases}:
                bundle = self._cases_for_base(cases, base_id)
                self.assertEqual(set(bundle), {
                    (family, valid) for family in e001.FAMILIES for valid in (True, False)
                })
                for (family, valid), case in bundle.items():
                    oracle = e001.reference_oracle(case.payload)
                    self.assertEqual(oracle, e001.OracleResult(
                        case.family_passes, case.truth, case.oracle_reason
                    ))
                    self.assertEqual(case.truth, int(valid))
                    failed = tuple(name for name, passed in oracle.family_passes if not passed)
                    self.assertEqual(failed, () if valid else (family,))
                    self.assertEqual(e001.validate_m1(case.payload).decision, valid)
                    self.assertTrue(e001.validate_b0(case.payload).decision)

    def test_recipe_footprints_and_fixed_order_vectors(self) -> None:
        for split, cases in self.datasets.items():
            for base_id in {case.base_case_id for case in cases}:
                bundle = self._cases_for_base(cases, base_id)
                base = e001.generate_base_payload(
                    split, next(case.seed for case in cases if case.base_case_id == base_id),
                    next(case.base_index for case in cases if case.base_case_id == base_id),
                )
                s1_positive = bundle[("S1", True)].payload
                self.assertEqual(
                    {e001.canonical_json_text(row) for row in s1_positive["entities"]},
                    {e001.canonical_json_text(row) for row in base["entities"]},
                )
                self.assertEqual(
                    [row["entity_id"] for row in s1_positive["entities"]],
                    ["entity-2", "entity-0", "entity-3", "entity-1"],
                )
                self.assertEqual(
                    [row["entry_id"] for row in s1_positive["ledger"]],
                    ["ledger-3", "ledger-1", "ledger-0", "ledger-2"],
                )
                self.assertEqual(
                    [row["event_id"] for row in s1_positive["events"]],
                    ["event-2-0", "event-0-0", "event-3-0", "event-1-0",
                     "event-2-1", "event-0-1", "event-1-1"],
                )
                s1_negative = bundle[("S1", False)].payload
                diffs = self._diff_paths(base, s1_negative)
                self.assertEqual(diffs, {("ledger", 1, "entry_id")})

                s2_positive = bundle[("S2", True)].payload
                self.assertEqual([row["entry_id"] for row in s2_positive["ledger"][:2]],
                                 ["ledger-0a", "ledger-0b"])
                self.assertEqual(
                    sum(row["amount_cents"] for row in s2_positive["ledger"]),
                    base["meta"]["declared_total_cents"],
                )
                self.assertEqual(
                    [row for row in s2_positive["ledger"][2:]], base["ledger"][1:]
                )
                s2_negative = bundle[("S2", False)].payload
                diffs = self._diff_paths(base, s2_negative)
                self.assertEqual(diffs, {("ledger", 1, "amount_cents")})

                t1_positive = bundle[("T1", True)].payload
                self.assertEqual(
                    [row["event_id"] for row in t1_positive["events"]],
                    ["event-1-0", "event-0-0", "event-2-0", "event-0-1",
                     "event-1-1", "event-2-1", "event-3-0"],
                )
                t1_negative = bundle[("T1", False)].payload
                self.assertEqual(self._diff_paths(base, t1_negative), {
                    ("entities", 0, "current_state"), ("events", 1, "to_state")
                })

                t2_positive = bundle[("T2", True)].payload
                self.assertEqual(t2_positive["events"][-1], {
                    "event_id": "event-3-1", "entity_id": "entity-3",
                    "from_state": "active", "to_state": "active", "revision": 2,
                })
                self.assertEqual(
                    next(row for row in t2_positive["entities"] if row["entity_id"] == "entity-3")["revision"],
                    2,
                )
                t2_negative = bundle[("T2", False)].payload
                self.assertEqual(self._diff_paths(base, t2_negative), {
                    ("events", 1, "revision")
                })

    def test_independent_oracle_and_m1_perturbation_vectors(self) -> None:
        payload = e001.generate_base_payload("development", 101, 0)
        original_m1 = e001.M1_CHECKS["T1"]
        original_reference = e001.REFERENCE_CHECKS["T1"]
        try:
            e001.M1_CHECKS["T1"] = lambda _: False
            self.assertEqual(e001.reference_oracle(payload).truth, 1)
            self.assertFalse(e001.validate_m1(payload).decision)
            e001.M1_CHECKS["T1"] = original_m1
            e001.REFERENCE_CHECKS["T1"] = lambda _: False
            self.assertEqual(e001.reference_oracle(payload).truth, 0)
            self.assertTrue(e001.validate_m1(payload).decision)
        finally:
            e001.M1_CHECKS["T1"] = original_m1
            e001.REFERENCE_CHECKS["T1"] = original_reference

    def test_t1_ordered_path_continuity_allowed_edges_and_closed_terminal(self) -> None:
        base = e001.generate_base_payload("development", 101, 0)
        reordered = copy.deepcopy(base)
        reordered["events"][0], reordered["events"][1] = (
            reordered["events"][1], reordered["events"][0]
        )
        self.assertFalse(e001.reference_t1(reordered))
        self.assertFalse(e001.validate_m1(reordered).decision)

        illegal_edge = copy.deepcopy(base)
        illegal_edge["events"][0]["from_state"] = "active"
        self.assertFalse(e001.reference_t1(illegal_edge))
        self.assertFalse(e001.validate_m1(illegal_edge).decision)

        after_closed = copy.deepcopy(base)
        after_closed["events"].append({
            "event_id": "event-0-2", "entity_id": "entity-0",
            "from_state": "closed", "to_state": "active", "revision": 3,
        })
        self.assertFalse(e001.reference_t1(after_closed))
        self.assertFalse(e001.validate_m1(after_closed).decision)

    def test_fail_closed_exact_nested_schema_and_sanitizer(self) -> None:
        base = e001.generate_base_payload("development", 101, 0)
        malformed = [None, [], {}, {"meta": None, "entities": [], "ledger": [], "events": []}]
        for field in ("meta", "entities", "ledger", "events"):
            value = copy.deepcopy(base)
            value[field] = None
            malformed.append(value)
            value = copy.deepcopy(base)
            value[field] = []
            malformed.append(value)
        for field, index, nested_key in (
            ("entities", 0, "metadata"), ("ledger", 0, "metadata"),
            ("events", 0, "metadata"),
        ):
            value = copy.deepcopy(base)
            value[field][index][nested_key] = {"unexpected": True}
            malformed.append(value)
        for field, nested_key in (
            ("meta", "metadata"),
        ):
            value = copy.deepcopy(base)
            value[field][nested_key] = "extra"
            malformed.append(value)

        for field, nested_key in (
            ("meta", "declared_total_cents"),
        ):
            value = copy.deepcopy(base)
            value[field][nested_key] = True
            malformed.append(value)
        for field, nested_key in (
            ("entities", "revision"), ("ledger", "amount_cents"),
            ("events", "revision"),
        ):
            value = copy.deepcopy(base)
            value[field][0][nested_key] = True
            malformed.append(value)
        for field, lengths in (("entities", (0, 1, 3, 5)), ("ledger", (0, 1, 3, 6)),
                               ("events", (0, 1, 6, 9))):
            for length in lengths:
                value = copy.deepcopy(base)
                if length <= len(value[field]):
                    value[field] = value[field][:length]
                else:
                    value[field].extend(
                        copy.deepcopy(value[field][-1])
                        for _ in range(length - len(value[field]))
                    )
                malformed.append(value)

        for value in malformed:
            self.assertIsNone(e001.sanitize_payload(value), repr(value))
            for method in e001.METHODS:
                try:
                    result = e001.validate_method(value, method)
                except Exception as exc:  # pragma: no cover - diagnostic guard
                    self.fail(f"{method} raised on malformed payload: {exc!r}")
                self.assertFalse(result.decision, method)

    def test_validators_receive_only_payload_and_reject_oracle_fields(self) -> None:
        captured: list[object] = []
        original = e001.validate_method

        def wrapper(payload: object, method: str) -> e001.ValidationResult:
            captured.append(payload)
            return original(payload, method)

        try:
            e001.validate_method = wrapper  # type: ignore[assignment]
            e001.evaluate_raw(self.dev_cases[:8], "M1")
        finally:
            e001.validate_method = original  # type: ignore[assignment]
        self.assertTrue(captured)
        self.assertTrue(all(set(payload) == set(e001.PAYLOAD_FIELDS) for payload in captured))
        leaked = copy.deepcopy(self.dev_cases[0].payload)
        leaked["target_family"] = "S1"
        leaked["truth"] = 1
        leaked["oracle_reason"] = "all families pass"
        self.assertFalse(e001.validate_m1(leaked).decision)
        self.assertFalse(e001.validate_b0(leaked).decision)
        self.assertEqual(len(inspect.signature(e001.validate_m1).parameters), 1)

    def test_b0_m1_and_all_ablation_decision_score_behavior(self) -> None:
        for case in self.dev_cases:
            b0 = e001.validate_b0(case.payload)
            m1 = e001.validate_m1(case.payload)
            self.assertTrue(b0.decision)
            self.assertEqual(b0.raw_score, 1)
            self.assertEqual(m1.decision, case.valid, case.case_id)
            self.assertEqual(m1.raw_score, 0 if case.valid else 1)
            self.assertEqual(m1.failed_families, () if case.valid else (case.target_family,))
            no_semantic = e001.validate_method(case.payload, "M1-no-semantic")
            no_state = e001.validate_method(case.payload, "M1-no-state")
            no_calibration = e001.validate_method(case.payload, "M1-no-calibration")
            self.assertEqual(no_calibration, m1)
            expected_semantic = case.valid or case.target_family in ("S1", "S2")
            expected_state = case.valid or case.target_family in ("T1", "T2")
            self.assertEqual(no_semantic.decision, expected_semantic)
            self.assertEqual(no_state.decision, expected_state)
            self.assertEqual(no_semantic.raw_score, 0 if expected_semantic else 1)
            self.assertEqual(no_state.raw_score, 0 if expected_state else 1)

    def test_calibration_lookup_frozen_and_ablation_specific(self) -> None:
        raw_rows = [
            row
            for method in e001.METHODS
            for row in e001.evaluate_raw(self.datasets["calibration"], method)
        ]
        lookups = e001.fit_all_calibrations(raw_rows)
        self.assertEqual(tuple(lookup.method for lookup in lookups), e001.CALIBRATED_METHODS)
        self.assertNotIn("M1-no-calibration", {lookup.method for lookup in lookups})
        rows = [
            {"method": "M1", "split": "calibration", "case_id": "a", "raw_score": 0, "truth": 1},
            {"method": "M1", "split": "calibration", "case_id": "b", "raw_score": 0, "truth": 0},
            {"method": "M1", "split": "calibration", "case_id": "c", "raw_score": 1, "truth": 0},
            {"method": "M1", "split": "calibration", "case_id": "d", "raw_score": 1, "truth": 0},
        ]
        lookup = e001.fit_calibration_lookup("M1", rows)
        self.assertAlmostEqual(lookup.lookup(0), 2 / 4)
        self.assertAlmostEqual(lookup.lookup(1), 1 / 4)
        self.assertAlmostEqual(lookup.lookup(4), 2 / 6)
        with self.assertRaises(e001.ProtocolError):
            e001.fit_calibration_lookup("M1", rows + [
                {"method": "M1", "split": "confirmatory", "case_id": "x", "raw_score": 0, "truth": 1}
            ])

    def test_development_prediction_schema_unique_rows_and_no_oracle_fields(self) -> None:
        raw_rows = [
            row
            for method in e001.METHODS
            for row in e001.evaluate_raw(self.dev_cases, method)
        ]
        calibration_raw = [
            row
            for method in e001.METHODS
            for row in e001.evaluate_raw(self.datasets["calibration"], method)
        ]
        lookups = e001.fit_all_calibrations(calibration_raw)
        rows = e001.build_prediction_rows(
            "development-only", self.dev_cases, raw_rows, lookups, "a" * 64
        )
        self.assertEqual(len(rows), len(self.dev_cases) * len(e001.METHODS))
        self.assertEqual(
            len({(row["method"], row["case_id"]) for row in rows}), len(rows)
        )
        self.assertTrue(all(set(row) == set(e001.PREDICTION_FIELDS) for row in rows))
        self.assertTrue(all(type(row["decision"]) is bool for row in rows))
        self.assertTrue(all(0 <= row["p_valid"] <= 1 for row in rows))
        no_cal = [row for row in rows if row["method"] == "M1-no-calibration"]
        m1 = {(row["case_id"]): row for row in rows if row["method"] == "M1"}
        self.assertTrue(all(row["p_valid"] in (0.0, 1.0) for row in no_cal))
        self.assertTrue(all(row["decision"] == m1[row["case_id"]]["decision"] for row in no_cal))
        self.assertNotIn("oracle_reason", rows[0])
        metric_rows = e001.build_metric_rows(rows, splits=("development",))
        self.assertEqual(len(metric_rows), len(e001.METHODS) * len(e001.SUBGROUPS))
        self.assertEqual(
            len({(row["method"], row["split"], row["subgroup"]) for row in metric_rows}),
            len(metric_rows),
        )
        self.assertTrue(all("intervals" in row and "paired_intervals" in row for row in metric_rows))

    def test_metric_formulas_undefined_policy_and_na_serialization(self) -> None:
        rows = [
            {"truth": 1, "decision": True, "p_valid": 0.9},
            {"truth": 1, "decision": False, "p_valid": 0.4},
            {"truth": 0, "decision": False, "p_valid": 0.1},
            {"truth": 0, "decision": True, "p_valid": 0.8},
        ]
        metrics = e001.compute_metrics(rows)
        for name in ("fpr", "fnr", "precision", "recall", "specificity", "f1", "balanced_accuracy"):
            self.assertAlmostEqual(metrics[name], 0.5)
        self.assertAlmostEqual(metrics["brier"], (0.1**2 + 0.6**2 + 0.1**2 + 0.8**2) / 4)
        self.assertEqual(sum(bin_row["count"] for bin_row in metrics["ece_bins"]), 4)
        self.assertAlmostEqual(
            metrics["ece"],
            (abs(0.1 - 0) + abs(0.4 - 1) + abs(0.8 - 0) + abs(0.9 - 1)) / 4,
        )
        positive_only = e001.compute_metrics([
            {"truth": 1, "decision": True, "p_valid": 1.0}
        ])
        self.assertIsNone(positive_only["fpr"])
        self.assertEqual(positive_only["denominators"]["fpr"], 0)
        undefined = e001.compute_metrics([])
        for name in e001.METRIC_NAMES:
            self.assertIsNone(undefined[name])
        row = {field: None for field in e001.METRIC_FIELDS}
        row.update({"method": "M1", "split": "development", "subgroup": "overall"})
        encoded = e001.serialize_csv([row], e001.METRIC_FIELDS).decode("utf-8")
        self.assertIn("NA", encoded)
        self.assertNotIn(",,", encoded)
        undefined_interval = e001._interval(None, "S1", "fpr", [None] * 10_000, 10_000)
        self.assertEqual(undefined_interval["status"], "undefined")
        self.assertIsNone(undefined_interval["lower"])
        self.assertEqual(undefined_interval["usable_replicates"], 0)

    def test_reporting_contains_method_pairs_h1_guardrail_ablations_and_limits(self) -> None:
        intervals = tuple(
            {
                "method": method,
                "method_pair": None,
                "subgroup": subgroup,
                "metric": metric,
                "lower": 0.0,
                "upper": 0.0,
                "usable_replicates": 10_000,
                "status": "available",
            }
            for method in e001.METHODS
            for subgroup in e001.SUBGROUPS
            for metric in e001.METRIC_NAMES
        ) + tuple(
            {
                "method": None,
                "method_pair": "M1-minus-B0",
                "subgroup": subgroup,
                "metric": metric,
                "lower": 0.0,
                "upper": 0.0,
                "usable_replicates": 10_000,
                "status": "available",
            }
            for subgroup in e001.SUBGROUPS
            for metric in e001.METRIC_NAMES
        )
        bootstrap = e001.BootstrapResult(
            10_000, tuple(f"cluster-{i:02d}" for i in range(64)), e001.METHODS,
            tuple(), tuple(), intervals
        )
        metric_rows = []
        for method in e001.METHODS:
            for subgroup in e001.SUBGROUPS:
                metric_rows.append({
                    "method": method, "split": "confirmatory", "subgroup": subgroup,
                    "balanced_accuracy": None, "FPR": None, "FNR": None,
                    "Brier": None, "ECE": None, "ci_lower": None, "ci_upper": None,
                    "paired_delta": None,
                })
        report = e001.build_results_markdown(
            "report-development-only",
            {"split_counts": {"development": 256, "calibration": 256, "confirmatory": 512},
             "confirmatory_clusters": 64},
            metric_rows,
            bootstrap,
        )
        for expected in (
            "Primary paired deltas (M1 minus B0)", "H1 is supported within this synthetic design",
            "FNR condition is a co-primary guardrail", "mixed/not supported",
            "M1-no-semantic", "M1-no-state", "M1-no-calibration", "Deviations: none",
            "Run validity", "Environment", "../../../data/E001-v1-bootstrap.csv",
            "Limitations", e001.PROTOCOL_COMMIT,
        ):
            self.assertIn(expected, report)

    @staticmethod
    def _bootstrap_fixture() -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for cluster in range(e001.BOOTSTRAP_CLUSTER_COUNT):
            base_case_id = f"development-bootstrap-{cluster:02d}"
            for family in e001.FAMILIES:
                for truth in (1, 0):
                    for method in e001.METHODS:
                        if method == "B0":
                            decision = True
                        else:
                            decision = bool(truth)
                        rows.append({
                            "method": method,
                            "split": "development",
                            "base_case_id": base_case_id,
                            "case_id": f"{base_case_id}-{family}-{truth}-{method}",
                            "target_family": family,
                            "truth": truth,
                            "decision": decision,
                            "p_valid": 0.75 if decision else 0.25,
                        })
        return rows

    @staticmethod
    def _row_stream_hash(rows: object) -> str:
        digest = hashlib.sha256()
        for row in rows:  # type: ignore[union-attr]
            digest.update(e001.canonical_json_bytes(row))
            digest.update(b"\n")
        return digest.hexdigest()

    def test_bootstrap_exact_count_determinism_pairs_intervals_and_size(self) -> None:
        fixture = self._bootstrap_fixture()
        expected_indices = tuple(
            int.from_bytes(
                hashlib.sha256(f"E001-v1|bootstrap|0|{index}".encode("utf-8")).digest()[:8],
                "big",
            ) % 64
            for index in range(64)
        )
        self.assertEqual(e001.bootstrap_cluster_indices(0, 64), expected_indices)
        first = e001.bootstrap_confirmatory(fixture, split="development")
        second = e001.bootstrap_confirmatory(fixture, split="development")
        self.assertEqual(first.replicate_count, 10_000)
        self.assertEqual(first.cluster_ids, tuple(f"development-bootstrap-{i:02d}" for i in range(64)))
        self.assertEqual(set(first.available_methods), set(e001.METHODS))
        self.assertEqual(
            {(subgroup, metric) for subgroup, metric, _ in first.delta_values},
            {(subgroup, metric) for subgroup in e001.SUBGROUPS for metric in e001.METRIC_NAMES},
        )
        self.assertTrue(all(len(values) == 10_000 for _, _, values in first.delta_values))
        self.assertEqual(first.intervals, second.intervals)
        self.assertEqual(
            self._row_stream_hash(e001.iter_bootstrap_rows(first)),
            self._row_stream_hash(e001.iter_bootstrap_rows(second)),
        )
        self.assertEqual(e001.expected_bootstrap_row_count(first), 450_270)
        self.assertEqual(
            sum(1 for _ in e001.iter_bootstrap_rows(first, row_type="replicate")), 450_000
        )
        self.assertEqual(
            sum(1 for _ in e001.iter_bootstrap_rows(first, row_type="interval")), 270
        )
        delta = first.delta_series("overall", "balanced_accuracy")
        self.assertTrue(all(value == 0.5 for value in delta))
        self.assertEqual(first.interval(None, "overall", "balanced_accuracy")["lower"], 0.5)
        replicate_rows = list(e001.iter_bootstrap_rows(first, row_type="replicate"))
        self.assertTrue(all(row["method"] is None for row in replicate_rows[:4]))
        self.assertTrue(all(row["method_pair"] == "M1-minus-B0" for row in replicate_rows[:4]))
        estimated = e001.bootstrap_size_estimate(first)
        self.assertGreater(estimated, 0)
        self.assertLess(estimated, e001.PUBLIC_LARGE_FILE_LIMIT)

    def test_runner_protocol_clean_ancestor_gates_with_mocks(self) -> None:
        self.assertEqual(e001.PROTOCOL_COMMIT, "d8b26d21e9692ace19436d78461460940043f5c7")
        self.assertEqual(
            e001.PROTOCOL_PATH,
            "experiments/E001-synthetic-invariant-calibration/protocol.md",
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol = root / e001.PROTOCOL_PATH
            protocol.parent.mkdir(parents=True)
            locked = b"locked protocol bytes"
            protocol.write_bytes(locked)

            def git_fn(_: Path, *args: str, binary: bool = False) -> bytes | str:
                if args[0] == "status":
                    return ""
                if args[0] == "show":
                    return locked if binary else locked.decode()
                if args[0] == "rev-parse":
                    return "HEAD\n"
                raise AssertionError(args)

            run_e001._protocol_guard(
                root,
                git_fn=git_fn,
                ancestor_fn=lambda *_: True,
            )
            with self.assertRaises(RuntimeError):
                run_e001._protocol_guard(
                    root,
                    git_fn=lambda *_args, **_kwargs: " M dirty",
                    ancestor_fn=lambda *_: True,
                )
            with self.assertRaises(RuntimeError):
                run_e001._protocol_guard(root, git_fn=git_fn, ancestor_fn=lambda *_: False)

    def test_cli_requires_explicit_run_id_and_output_root(self) -> None:
        with self.assertRaises(SystemExit):
            run_e001.build_parser().parse_args([])

    def test_guard_observes_nonexistent_output_root_before_any_directory_write(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo_root = Path(directory) / "repo"
            output_root = repo_root / "future-output"
            repo_root.mkdir()
            observed: list[bool] = []

            def failing_guard(_: Path) -> None:
                observed.append(output_root.exists())
                raise RuntimeError("preflight failure")

            with self.assertRaises(run_e001.InvalidRunError):
                run_e001.execute_run(
                    "guard-order-001",
                    output_root,
                    repo_root=repo_root,
                    protocol_guard_fn=failing_guard,
                    pipeline_factory=lambda _: None,
                )
            self.assertEqual(observed, [False])
            invalid = (
                output_root
                / run_e001.EXPERIMENT_ROOT
                / "results"
                / "run-guard-order-001.md"
            )
            self.assertTrue(invalid.is_file())
            self.assertIn("Run validity:", invalid.read_text())

    def test_runner_stages_writes_result_last_and_refuses_overwrite(self) -> None:
        class FakeArtifact:
            def __init__(self, run_id: str) -> None:
                self.run_id = run_id
                self.serialized_outputs = (
                    ("predictions", b"predictions\n"),
                    ("metrics", b"metrics\n"),
                    ("bootstrap", b"bootstrap\n"),
                    ("result", b"# valid result\n"),
                )

            def serialized(self, name: str) -> bytes:
                return dict(self.serialized_outputs)[name]

            def hashes(self) -> dict[str, str]:
                return {name: hashlib.sha256(content).hexdigest()
                        for name, content in self.serialized_outputs}

        calls: list[str] = []
        finalization_order: list[str] = []

        def factory(run_id: str) -> FakeArtifact:
            calls.append(run_id)
            return FakeArtifact(run_id)

        def recording_replace(source: object, target: object) -> None:
            finalization_order.append(Path(target).name)
            os.replace(source, target)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            summary = run_e001.execute_run(
                "dev-writer-001",
                root,
                repo_root=root,
                protocol_guard_fn=lambda _: None,
                pipeline_factory=factory,
                replace_fn=recording_replace,
            )
            self.assertEqual(summary["status"], "valid")
            self.assertEqual(calls, ["dev-writer-001", "dev-writer-001"])
            self.assertEqual(finalization_order, [
                "E001-v1-predictions.jsonl", "E001-v1-metrics.csv",
                "E001-v1-bootstrap.csv", "run-dev-writer-001.md",
            ])
            targets = {
                "results": root / run_e001.EXPERIMENT_ROOT / "results" / "run-dev-writer-001.md",
                "predictions": root / "data" / "E001-v1-predictions.jsonl",
                "metrics": root / "data" / "E001-v1-metrics.csv",
                "bootstrap": root / "data" / "E001-v1-bootstrap.csv",
            }
            self.assertEqual(targets["results"].read_bytes(), b"# valid result\n")
            self.assertEqual(targets["predictions"].read_bytes(), b"predictions\n")
            self.assertFalse(any(path.name.startswith(".e001-stage-") for path in root.iterdir()))
            with self.assertRaises(FileExistsError):
                run_e001.execute_run(
                    "dev-writer-002",
                    root,
                    repo_root=root,
                    protocol_guard_fn=lambda _: None,
                    pipeline_factory=factory,
                )

    def test_runner_fault_injection_leaves_only_invalid_record(self) -> None:
        class FakeArtifact:
            run_id = "fault-001"
            serialized_outputs = (
                ("predictions", b"p"), ("metrics", b"m"),
                ("bootstrap", b"b"), ("result", b"valid-looking"),
            )

            def serialized(self, name: str) -> bytes:
                return dict(self.serialized_outputs)[name]

            def hashes(self) -> dict[str, str]:
                return {name: hashlib.sha256(content).hexdigest()
                        for name, content in self.serialized_outputs}

        count = 0

        def fail_on_result(source: object, target: object) -> None:
            nonlocal count
            count += 1
            if count == 4:
                raise OSError("injected finalize failure")
            import os
            os.replace(source, target)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(run_e001.InvalidRunError):
                run_e001.execute_run(
                    "fault-001", root, repo_root=root,
                    protocol_guard_fn=lambda _: None,
                    pipeline_factory=lambda _: FakeArtifact(),
                    replace_fn=fail_on_result,
                )
            invalid = root / run_e001.EXPERIMENT_ROOT / "results" / "run-fault-001.md"
            self.assertTrue(invalid.is_file())
            text = invalid.read_text(encoding="utf-8")
            self.assertIn("Run validity: `invalid`", text)
            self.assertIn("Metrics are not evidence", text)
            self.assertNotIn("valid-looking", text)
            self.assertFalse((root / "data" / "E001-v1-predictions.jsonl").exists())
            self.assertFalse((root / "data" / "E001-v1-metrics.csv").exists())
            self.assertFalse((root / "data" / "E001-v1-bootstrap.csv").exists())


if __name__ == "__main__":
    unittest.main()
