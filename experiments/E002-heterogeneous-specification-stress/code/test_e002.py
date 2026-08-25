"""Development-only tests for the locked E002-v1 implementation.

Scoring, calibration, metric, and reduced-bootstrap fixtures use only the
development and calibration splits. Confirmatory arithmetic is checked
structurally; no confirmatory score or metric is computed here.
"""

from __future__ import annotations

import copy
import importlib.util
import inspect
import json
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import e002
import run_e002


RUN_ID = "e002-20260825-001"


def _adversarial_checker_calls_reference(payload: object, method: str = "M1") -> object:
    return e002.reference_oracle(payload)


def _adversarial_checker_uses_oracle_table(payload: object) -> object:
    return e002.ORACLE_ALLOWED_EDGES


class E002HarnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.population = e002.generate_population()
        cls.cases = cls.population.cases
        cls.scored_cases = tuple(
            case for case in cls.cases if case.split in {"development", "calibration"}
        )
        cls.calibration_cases = tuple(
            case for case in cls.scored_cases if case.split == "calibration"
        )
        (
            cls.lookups,
            cls.calibration_manifest_object,
            cls.calibration_hash,
            cls.prediction_rows,
            cls.prediction_map,
        ) = e002.build_predictions(
            RUN_ID,
            cls.population,
            cls.calibration_cases,
            scoring_cases=cls.scored_cases,
        )
        cls.lookup_hashes = {
            lookup.method: e002._lookup_hash(lookup) for lookup in cls.lookups
        }
        cls.bootstrap = e002.run_bootstrap(
            cls.population,
            cls.prediction_map,
            replicate_count=16,
            bootstrap_splits=("development", "calibration"),
            include_diagnostics=False,
        )
        cls.metric_rows = e002.build_metric_rows(
            RUN_ID,
            cls.population,
            cls.prediction_map,
            cls.lookup_hashes,
            cls.bootstrap,
            splits=("development", "calibration"),
            include_diagnostics=False,
        )

    def test_run_id_protocol_and_locked_identity(self) -> None:
        self.assertTrue(e002.validate_run_id(RUN_ID))
        self.assertFalse(e002.validate_run_id("e002-20260230-001"))
        self.assertEqual(e002.PROTOCOL_VERSION, "E002-v1")
        self.assertEqual(
            e002.PROTOCOL_PATH,
            "experiments/E002-heterogeneous-specification-stress/protocol.md",
        )
        self.assertEqual(len(e002.PROTOCOL_COMMIT), 40)
        self.assertEqual(len(e002.PROTOCOL_BLOB), 40)

    def test_exact_population_split_and_future_artifact_arithmetic(self) -> None:
        self.assertEqual(len(self.population.clusters), 96)
        self.assertEqual(len(self.cases), 912)
        self.assertEqual(
            {split: len(cases) for split, cases in self.population.by_split().items()},
            {"development": 228, "calibration": 228, "confirmatory": 456},
        )
        self.assertEqual(
            {
                split: len(clusters)
                for split, clusters in self.population.clusters_by_split().items()
            },
            {"development": 24, "calibration": 24, "confirmatory": 48},
        )
        self.assertEqual(len(self.scored_cases), 456)
        self.assertEqual(len(self.prediction_rows), 456 * len(e002.METHODS))
        self.assertEqual(912 * len(e002.METHODS), 7296)
        self.assertEqual(
            len(e002.SPLITS) * len(e002.SUBGROUPS) * len(e002.METHODS)
            + len(e002.DIAGNOSTICS),
            243,
        )
        self.assertEqual(53 * (10_000 + 1), 530_053)
        self.assertEqual(530_053 + 1, 530_054)

    def test_pairwise_split_leakage_gate(self) -> None:
        split_clusters = self.population.clusters_by_split()
        split_cases = self.population.by_split()
        for split in e002.SPLITS:
            for field in ("base_hash", "cluster_id"):
                values = {getattr(item, field) for item in split_clusters[split]}
                self.assertEqual(len(values), len(split_clusters[split]))
            case_ids = {case.case_id for case in split_cases[split]}
            self.assertEqual(len(case_ids), len(split_cases[split]))
        for index, left in enumerate(e002.SPLITS):
            for right in e002.SPLITS[index + 1 :]:
                self.assertTrue(
                    {
                        cluster.base_hash for cluster in split_clusters[left]
                    }.isdisjoint(
                        {cluster.base_hash for cluster in split_clusters[right]}
                    )
                )
                self.assertTrue(
                    {
                        cluster.cluster_id for cluster in split_clusters[left]
                    }.isdisjoint(
                        {cluster.cluster_id for cluster in split_clusters[right]}
                    )
                )
                self.assertTrue(
                    {case.case_id for case in split_cases[left]}.isdisjoint(
                        {case.case_id for case in split_cases[right]}
                    )
                )

    def test_independent_type_recipe_footprint_and_signature_manifests(self) -> None:
        self.assertEqual(tuple(e002.INDEPENDENT_TYPE_ORDER), e002.TYPE_ORDER)
        for cluster in self.population.clusters:
            expected_tuple, expected_signature = e002.INDEPENDENT_SIGNATURE_MANIFEST[
                cluster.cluster_type
            ]
            self.assertEqual(cluster.structural_signature, expected_tuple)
            self.assertEqual(cluster.signature_sha256, expected_signature)
            self.assertEqual(
                tuple(case.recipe_id for case in cluster.cases),
                e002.INDEPENDENT_RECIPE_MANIFEST[cluster.cluster_type],
            )
            for case in cluster.cases:
                self.assertEqual(
                    case.case_kind, e002.INDEPENDENT_CASE_KIND_MANIFEST[case.recipe_id]
                )
                self.assertEqual(
                    case.fault_set, e002.INDEPENDENT_FAULT_MANIFEST[case.recipe_id]
                )
                self.assertEqual(
                    case.footprint,
                    e002.INDEPENDENT_FOOTPRINT_MANIFEST[cluster.cluster_type][
                        case.recipe_id
                    ],
                )
        self.assertEqual(
            {len(cluster.cases) for cluster in self.population.clusters},
            {7, 8, 9, 10, 11, 12},
        )

    def test_all_six_signature_vectors_and_known_answers(self) -> None:
        expected_signatures = {
            "H0": "2e80ccf18dad2a97d8d3e975b0f726f6cf15687fa6e4f50ddf55a940e6d29e9b",
            "H1": "0195af9dd2a1ef0f4348c6fc6f082b626d7c9ab1c310c9487d5760bf74afa574",
            "H2": "0863b001f0a85dc2582be68a41d33afc2c7d8b28bb52e224e66c4124b8a42d45",
            "H3": "278251e55ee1daf215d42e1f534bf811529ab9da39069e488c448f88014d3272",
            "H4": "d96362a72a4bd443d8e750ced1cebca4521ff28a9e5116bfe6e65c57d2cfbaf3",
            "H5": "9a0568400739c46729f811419f84a144a0dfd5de1031f30bd9a47834f101bdcd",
        }
        for cluster_type, expected in expected_signatures.items():
            self.assertEqual(e002.sha256_hex(e002._signature_input(cluster_type)), expected)
            self.assertEqual(
                e002.INDEPENDENT_SIGNATURE_MANIFEST[cluster_type][1], expected
            )
        self.assertEqual(
            e002.sha256_hex("E002-v1|amount|0|0"),
            "6211e62d437c6210a1c02e41c02c49f5dcce723a6ee0d69a6af036803cf629f4",
        )
        self.assertEqual(e002._amount_cents(0, 0), 920)
        self.assertEqual(
            e002.sha256_hex("H0-C00::valid-base"),
            "bc4c1aa9ecb37f29ec8f1acebb4040d61cca0bf3c3d2de061af53dd1d4876911",
        )
        bootstrap_digest = e002.sha256_hex(
            "E002-v1|bootstrap|overall|balanced_accuracy|0|0"
        )
        self.assertEqual(
            bootstrap_digest,
            "ec4fb50879c8319c8000ee52e5d68a1d4617e570c3874457ce9dbb1b727ee050",
        )
        self.assertEqual(
            int.from_bytes(bytes.fromhex(bootstrap_digest)[:8], "big") % 48, 28
        )

    def test_runtime_sanity_accepts_population_and_rejects_every_mutable_table_drift(self) -> None:
        result = e002.runtime_sanity_check(self.population)
        self.assertEqual(result["clusters"], 96)
        self.assertEqual(result["cases"], 912)
        mutators = {
            "TRACE_TABLE": lambda: e002.TRACE_TABLE.__setitem__(
                "H0", (("pending", "active", "closed"),) * 3
            ),
            "TYPE_MANIFEST": lambda: e002.TYPE_MANIFEST["H0"].__setitem__(
                "multi", 3
            ),
            "TYPE_ORDER": lambda: setattr(e002, "TYPE_ORDER", tuple(reversed(e002.TYPE_ORDER))),
            "RECIPE_ORDER": lambda: setattr(
                e002,
                "RECIPE_ORDER",
                ("valid-base", "C1", "R1", *e002.RECIPE_ORDER[3:]),
            ),
            "M01_OPERATION_REORDER": lambda: e002.MULTI_RECIPE.__setitem__(
                "M01", ("C1", "R1")
            ),
            "RECIPE_FAMILIES": lambda: e002.RECIPE_FAMILIES.__setitem__(
                "R1", ("conservation",)
            ),
            "SINGLE_RECIPE": lambda: e002.SINGLE_RECIPE.remove("R1"),
            "MULTI_RECIPE": lambda: e002.MULTI_RECIPE.__setitem__("M01", ("R1",)),
        }
        for name, mutate in mutators.items():
            with self.subTest(table=name):
                snapshots = {
                    "TRACE_TABLE": copy.deepcopy(e002.TRACE_TABLE),
                    "TYPE_MANIFEST": copy.deepcopy(e002.TYPE_MANIFEST),
                    "TYPE_ORDER": e002.TYPE_ORDER,
                    "RECIPE_ORDER": e002.RECIPE_ORDER,
                    "RECIPE_FAMILIES": copy.deepcopy(e002.RECIPE_FAMILIES),
                    "SINGLE_RECIPE": set(e002.SINGLE_RECIPE),
                    "MULTI_RECIPE": copy.deepcopy(e002.MULTI_RECIPE),
                }
                try:
                    mutate()
                    with self.assertRaises(e002.ProtocolError):
                        e002.runtime_sanity_check(self.population)
                finally:
                    e002.TRACE_TABLE.clear()
                    e002.TRACE_TABLE.update(snapshots["TRACE_TABLE"])
                    e002.TYPE_MANIFEST.clear()
                    e002.TYPE_MANIFEST.update(snapshots["TYPE_MANIFEST"])
                    e002.TYPE_ORDER = snapshots["TYPE_ORDER"]
                    e002.RECIPE_ORDER = snapshots["RECIPE_ORDER"]
                    e002.RECIPE_FAMILIES.clear()
                    e002.RECIPE_FAMILIES.update(snapshots["RECIPE_FAMILIES"])
                    e002.SINGLE_RECIPE.clear()
                    e002.SINGLE_RECIPE.update(snapshots["SINGLE_RECIPE"])
                    e002.MULTI_RECIPE.clear()
                    e002.MULTI_RECIPE.update(snapshots["MULTI_RECIPE"])

    def test_runtime_sanity_rejects_full_generation_and_operation_mutations(self) -> None:
        original_base = e002.generate_base_payload
        original_apply = e002._apply_recipe

        def bad_event_id(cluster_index: int, cluster_type: str) -> object:
            payload = copy.deepcopy(original_base(cluster_index, cluster_type))
            payload["events"][0]["event_id"] = payload["events"][1]["event_id"]
            return payload

        def bad_c1(base: object, recipe_id: str) -> object:
            payload, footprint = original_apply(base, recipe_id)
            if recipe_id == "C1":
                payload["ledger"][-1]["amount_cents"] += 1
            return payload, footprint

        with mock.patch.object(e002, "generate_base_payload", bad_event_id):
            with self.assertRaises(e002.ProtocolError):
                e002.runtime_sanity_check(self.population)
        with mock.patch.object(e002, "_apply_recipe", bad_c1):
            with self.assertRaises(e002.ProtocolError):
                e002.runtime_sanity_check(self.population)

    def test_independent_recipe_constructor_is_not_a_projection(self) -> None:
        for cluster in self.population.clusters:
            independent_base = e002.independently_rebuild_base_payload(
                cluster.cluster_index, cluster.cluster_type
            )
            self.assertEqual(independent_base, e002.generate_base_payload(
                cluster.cluster_index, cluster.cluster_type
            ))
            for case in cluster.cases:
                self.assertEqual(
                    e002.independently_apply_recipe(independent_base, case.recipe_id),
                    case.payload,
                )
        self.assertEqual(
            e002.INDEPENDENT_RECIPE_OPERATION_MANIFEST["M01"],
            (
                ("copy", "/ledger/1/entry_id", "/ledger/0/entry_id"),
                ("increment", "/ledger/last/amount_cents", 1),
            ),
        )

    def test_recipe_truth_oracle_isolation_and_positive_family_passes(self) -> None:
        for case in self.cases:
            with self.subTest(case_id=case.case_id):
                oracle = e002.reference_oracle(case.payload)
                self.assertEqual(case.truth, oracle.truth)
                self.assertEqual(case.oracle_failure_set, oracle.failed_families)
                if case.case_kind == "valid":
                    self.assertEqual(oracle.truth, 1)
                    self.assertEqual(oracle.failed_families, ())
                    self.assertTrue(all(passed for _name, passed in oracle.family_passes))
                elif case.case_kind == "single":
                    self.assertEqual(oracle.truth, 0)
                    self.assertEqual(
                        oracle.failed_families,
                        e002.INDEPENDENT_FAULT_MANIFEST[case.recipe_id],
                    )
                else:
                    self.assertEqual(oracle.truth, 0)

    def test_h0_h5_separation_and_ordered_transition_probes(self) -> None:
        first = next(case for case in self.cases if case.case_id == "H0-C00::valid-base")
        fifth = next(case for case in self.cases if case.case_id == "H5-C00::valid-base")
        self.assertEqual(
            e002.canonical_sha256(first.payload),
            "8ddb5fbd84a64ef811a261ad72359f647d0757e8c83c864bd206bbb03b8dd07b",
        )
        self.assertEqual(
            e002.canonical_sha256(fifth.payload),
            "97935beb48f281d1d1fe8317d8ee7f300089bd2e6ad523fc06aaaaf47d4c6db3",
        )
        self.assertTrue(e002.validate_m1(first.payload).decision)
        self.assertFalse(e002.validate_m1_overconstraint(first.payload).decision)
        self.assertTrue(e002.validate_m1_stale_transition(first.payload).decision)
        self.assertTrue(e002.validate_m1(fifth.payload).decision)
        self.assertTrue(e002.validate_m1_overconstraint(fifth.payload).decision)
        self.assertFalse(e002.validate_m1_stale_transition(fifth.payload).decision)
        base = copy.deepcopy(first.payload)
        disconnected = copy.deepcopy(base)
        disconnected["events"][1]["from_state"] = "pending"
        disconnected["events"][1]["to_state"] = "active"
        self.assertTrue(e002.validate_b0(disconnected).decision)
        self.assertFalse(e002.reference_oracle(disconnected).truth)
        self.assertFalse(e002.validate_m1(disconnected).decision)
        terminal = copy.deepcopy(base)
        terminal["events"][-1]["to_state"] = "active"
        self.assertTrue(e002.validate_b0(terminal).decision)
        self.assertFalse(e002.reference_oracle(terminal).truth)
        self.assertFalse(e002.validate_m1(terminal).decision)

    def test_fail_closed_nested_schema_and_b0_type_only_contract(self) -> None:
        valid = copy.deepcopy(
            next(case for case in self.cases if case.case_id == "H0-C00::valid-base").payload
        )
        malformed = [
            {},
            None,
            [],
            {"meta": {}, "entities": [], "ledger": [], "events": []},
        ]
        nested_extra = copy.deepcopy(valid)
        nested_extra["meta"]["debug"] = "unexpected"
        malformed.append(nested_extra)
        bool_integer = copy.deepcopy(valid)
        bool_integer["meta"]["declared_total_cents"] = True
        malformed.append(bool_integer)
        wrong_cardinality = copy.deepcopy(valid)
        wrong_cardinality["events"] = wrong_cardinality["events"][:7]
        malformed.append(wrong_cardinality)
        list_substitution = copy.deepcopy(valid)
        list_substitution["entities"][0] = []
        malformed.append(list_substitution)
        none_substitution = copy.deepcopy(valid)
        none_substitution["ledger"] = None
        malformed.append(none_substitution)
        extra_event_field = copy.deepcopy(valid)
        extra_event_field["events"][0]["metadata"] = "unexpected"
        malformed.append(extra_event_field)
        for payload in malformed:
            with self.subTest(payload=repr(payload)[:50]):
                self.assertFalse(e002.reference_oracle(payload).schema_valid)
                for method in e002.METHODS:
                    self.assertFalse(e002.validate_method(payload, method).decision)
        duplicate = copy.deepcopy(valid)
        duplicate["entities"][1]["entity_id"] = duplicate["entities"][0]["entity_id"]
        self.assertTrue(e002.validate_b0(duplicate).decision)
        self.assertFalse(e002.validate_m1(duplicate).decision)

    def test_oracle_checker_transitive_independence_and_no_metadata_leakage(self) -> None:
        e002.assert_oracle_checker_independence()
        graph = e002.oracle_checker_call_graph()
        self.assertNotIn("reference_oracle", graph["checker_functions"])
        self.assertNotIn("ORACLE_ALLOWED_EDGES", graph["checker_globals"])
        checker_source = inspect.getsource(e002.checker_validation)
        for forbidden in ("target_family", "fault_set", "oracle_failure_set", "truth"):
            self.assertNotIn(forbidden, checker_source)
        with mock.patch.object(
            e002, "checker_validation", _adversarial_checker_calls_reference
        ):
            with self.assertRaises(e002.ProtocolError):
                e002.assert_oracle_checker_independence()
        with mock.patch.object(
            e002, "_checker_identity", _adversarial_checker_uses_oracle_table
        ):
            with self.assertRaises(e002.ProtocolError):
                e002.assert_oracle_checker_independence()

        def make_alias_checker():
            oracle_alias = e002.reference_oracle

            def checker(payload: object) -> object:
                return oracle_alias(payload)

            return checker

        with mock.patch.object(e002, "checker_validation", make_alias_checker()):
            with self.assertRaises(e002.ProtocolError):
                e002.assert_oracle_checker_independence()

        def make_table_alias_checker():
            table_alias = e002.ORACLE_ALLOWED_EDGES

            def checker(_payload: object) -> object:
                return table_alias

            return checker

        with mock.patch.object(e002, "checker_validation", make_table_alias_checker()):
            with self.assertRaises(e002.ProtocolError):
                e002.assert_oracle_checker_independence()

    def test_oracle_checker_independence_rejects_external_module_helper(self) -> None:
        """An imported helper outside this implementation cannot hide a bypass."""

        module_name = "e002_external_bridge_probe"
        with tempfile.TemporaryDirectory() as temporary:
            module_file = Path(temporary) / "external_bridge.py"
            module_file.write_text(
                "import e002\n\n"
                "def bridge(payload, method='M1'):\n"
                "    return e002.reference_oracle(payload)\n",
                encoding="utf-8",
            )
            spec = importlib.util.spec_from_file_location(module_name, module_file)
            self.assertIsNotNone(spec)
            self.assertIsNotNone(spec.loader)
            external = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = external
            try:
                assert spec.loader is not None
                spec.loader.exec_module(external)
                with mock.patch.object(e002, "checker_validation", external.bridge):
                    with self.assertRaisesRegex(
                        e002.ProtocolError, "external callable"
                    ):
                        e002.assert_oracle_checker_independence()
            finally:
                sys.modules.pop(module_name, None)

    def test_protocol_section8_perturbations_execute_independently(self) -> None:
        """Changing either implementation leaves the other path unchanged."""

        bounded_cases = self.scored_cases

        def oracle_projection(payload: object) -> object:
            result = e002.reference_oracle(payload)
            return (
                result.schema_valid,
                result.truth,
                result.failed_families,
                result.base_structure_flags,
                result.family_passes,
            )

        def checker_projection(payload: object) -> object:
            result = e002.validate_m1(payload)
            return result.decision, result.raw_score, result.failed_families

        oracle_before = tuple(
            (case.case_id, oracle_projection(case.payload)) for case in bounded_cases
        )
        checker_before = tuple(
            (case.case_id, checker_projection(case.payload)) for case in bounded_cases
        )
        with mock.patch.object(e002, "_checker_identity", lambda _payload: True):
            checker_after_checker_perturbation = tuple(
                (case.case_id, checker_projection(case.payload))
                for case in bounded_cases
            )
            oracle_after_checker_perturbation = tuple(
                (case.case_id, oracle_projection(case.payload)) for case in bounded_cases
            )
        self.assertEqual(oracle_after_checker_perturbation, oracle_before)
        self.assertNotEqual(checker_after_checker_perturbation, checker_before)

        original_oracle = e002.reference_oracle

        def perturbed_oracle(payload: object) -> e002.OracleResult:
            result = original_oracle(payload)
            return replace(result, truth=1 - result.truth)

        with mock.patch.object(e002, "reference_oracle", perturbed_oracle):
            oracle_after_oracle_perturbation = tuple(
                (case.case_id, oracle_projection(case.payload)) for case in bounded_cases
            )
            checker_after_oracle_perturbation = tuple(
                (case.case_id, checker_projection(case.payload))
                for case in bounded_cases
            )
        self.assertNotEqual(oracle_after_oracle_perturbation, oracle_before)
        self.assertEqual(checker_after_oracle_perturbation, checker_before)

    def test_ablation_methods_and_calibration_isolation(self) -> None:
        valid = next(case for case in self.cases if case.case_kind == "valid").payload
        r1 = next(case for case in self.cases if case.recipe_id == "R1").payload
        t1 = next(case for case in self.cases if case.recipe_id == "T1").payload
        for payload in (valid, r1, t1):
            self.assertEqual(
                e002.validate_method(payload, "M1-no-calibration").decision,
                e002.validate_m1(payload).decision,
            )
        self.assertTrue(e002.validate_method(valid, "M1-no-semantic").decision)
        self.assertTrue(e002.validate_method(valid, "M1-no-state").decision)
        self.assertTrue(e002.validate_method(r1, "M1-no-semantic").decision)
        self.assertFalse(e002.validate_method(r1, "M1-no-state").decision)
        self.assertFalse(e002.validate_method(t1, "M1-no-semantic").decision)
        self.assertTrue(e002.validate_method(t1, "M1-no-state").decision)
        self.assertEqual({lookup.method for lookup in self.lookups}, set(e002.METHODS))
        self.assertEqual(len({e002._lookup_hash(lookup) for lookup in self.lookups}), 8)

    def test_calibration_formula_fallback_and_lookup_ownership(self) -> None:
        for lookup in self.lookups[:-1]:
            for score, positive, count, probability in lookup.entries:
                self.assertEqual(probability, e002.Fraction(positive + 1, count + 2))
            total = sum(entry[2] for entry in lookup.entries)
            positives = sum(entry[1] for entry in lookup.entries)
            self.assertEqual(lookup.fallback, e002.Fraction(positives + 1, total + 2))
            self.assertEqual(lookup.lookup(99), lookup.fallback)
        no_calibration = self.lookups[-1]
        self.assertIsNone(no_calibration.fallback)
        self.assertEqual(no_calibration.entries, ())
        for row in self.metric_rows:
            self.assertEqual(
                row["calibration_lookup_sha256"], self.lookup_hashes[row["method"]]
            )

    def test_calibration_inventory_rejects_duplicates_and_confirmatory_substitution(self) -> None:
        duplicate = self.calibration_cases[:-1] + (self.calibration_cases[-2],)
        with self.assertRaises(e002.ProtocolError):
            e002.build_predictions(
                RUN_ID, self.population, duplicate, scoring_cases=self.scored_cases
            )
        confirmatory = next(
            case for case in self.cases if case.split == "confirmatory"
        )
        substituted = self.calibration_cases[:-1] + (confirmatory,)
        with self.assertRaises(e002.ProtocolError):
            e002.build_predictions(
                RUN_ID, self.population, substituted, scoring_cases=self.scored_cases
            )

    def test_diagnostic_eligibility_rejects_flag_or_set_drift(self) -> None:
        original_predicate = e002._diagnostic_cases

        def no_d2(_case: object, diagnostic: str) -> bool:
            if diagnostic == "d2":
                return False
            return original_predicate(_case, diagnostic)

        with mock.patch.object(e002, "_diagnostic_cases", no_d2):
            with self.assertRaises(e002.ProtocolError):
                e002.diagnostic_eligibility(self.population)

    def test_metric_calibration_lookup_diagnostic_na_contract(self) -> None:
        intervals = {
            (
                f"diagnostic:{diagnostic}",
                e002.DIAGNOSTIC_METRIC[diagnostic],
                e002.DIAGNOSTIC_PAIR_CODE[diagnostic],
            ): {
                "ci_lower": "0.100000000",
                "ci_upper": "0.200000000",
                "status": "partial",
            }
            for diagnostic in e002.DIAGNOSTICS
        }
        bootstrap = e002.BootstrapResult((), intervals, 3, 16)
        rows = tuple(
            e002._diagnostic_row(
                RUN_ID,
                diagnostic,
                self.scored_cases,
                self.prediction_map,
                self.calibration_hash,
                bootstrap,
            )
            for diagnostic in e002.DIAGNOSTICS
        )
        expected_pairs = {"d1": "omit-M1", "d2": "over-M1", "d3": "stale-M1"}
        for row in rows:
            self.assertEqual(row["method"], e002.NA)
            self.assertEqual(row["calibration_lookup_sha256"], e002.NA)
            self.assertEqual(row["method_pair"], expected_pairs[row["diagnostic_id"]])
            self.assertEqual(row["paired_interval_ref"], e002.NA)
            for field in ("support", "positive_count", "negative_count", "tp", "tn", "fp", "fn"):
                self.assertEqual(row[field], e002.NA)

    def test_metric_validator_uses_literal_diagnostic_mapping(self) -> None:
        intervals = {
            (f"diagnostic:{diagnostic}", e002.DIAGNOSTIC_METRIC[diagnostic], e002.DIAGNOSTIC_PAIR_CODE[diagnostic]): {
                "ci_lower": "0.100000000", "ci_upper": "0.200000000", "status": "partial"
            }
            for diagnostic in e002.DIAGNOSTICS
        }
        row = e002._diagnostic_row(
            RUN_ID,
            "d2",
            self.scored_cases,
            self.prediction_map,
            self.calibration_hash,
            e002.BootstrapResult((), intervals, 3, 16),
        )
        cells = [row[field] for field in e002.METRIC_FIELDS]
        run_e002._validate_metric_cells(cells)
        malformed = dict(row)
        malformed["diagnostic_metric"] = "fpr"
        with mock.patch.dict(e002.DIAGNOSTIC_METRIC, {"d2": "fpr"}):
            with self.assertRaises(run_e002.InvalidRunError):
                run_e002._validate_metric_cells(
                    [malformed[field] for field in e002.METRIC_FIELDS]
                )

    def test_metric_formulas_and_literal_na_undefined_policy(self) -> None:
        stats = e002._Stats()
        stats.add(1, True, e002.Fraction(1, 1))
        stats.add(0, False, e002.Fraction(0, 1))
        self.assertEqual(e002._metric_from_stats(stats, "balanced_accuracy"), e002.Fraction(1, 1))
        self.assertEqual(e002._metric_from_stats(stats, "fpr"), e002.Fraction(0, 1))
        self.assertEqual(e002._metric_from_stats(stats, "fnr"), e002.Fraction(0, 1))
        self.assertEqual(e002._metric_from_stats(stats, "brier"), e002.Fraction(0, 1))
        empty = e002._Stats()
        for metric in e002.REPORT_METRICS:
            self.assertIsNone(e002._metric_from_stats(empty, metric))
        self.assertEqual(e002.d9(None), e002.NA)
        self.assertEqual(e002._metric_row_values(empty)["fpr"], e002.NA)
        self.assertEqual(e002._metric_row_values(empty)["fpr_denominator"], "0")

    def test_reduced_bootstrap_determinism_count_and_partial_interval_policy(self) -> None:
        second = e002.run_bootstrap(
            self.population,
            self.prediction_map,
            replicate_count=16,
            bootstrap_splits=("development", "calibration"),
            include_diagnostics=False,
        )
        self.assertEqual(self.bootstrap.rows, second.rows)
        self.assertEqual(self.bootstrap.intervals, second.intervals)
        self.assertEqual(self.bootstrap.block_count, 50)
        self.assertEqual(self.bootstrap.replicate_count, 16)
        self.assertEqual(len(self.bootstrap.rows), 50 * 17)
        valid_fpr = self.bootstrap.intervals[("case_kind:valid", "fpr", "M1-B0")]
        self.assertEqual(valid_fpr["status"], "undefined")
        self.assertEqual(valid_fpr["ci_lower"], e002.NA)
        self.assertEqual(valid_fpr["ci_upper"], e002.NA)
        lower, upper, status, usable = e002._nearest_rank_interval(
            [e002.Fraction(1, 10), e002.Fraction(2, 10), e002.Fraction(3, 10)], 16
        )
        self.assertEqual((lower, upper, status, usable), ("0.100000000", "0.300000000", "partial", 3))

    def test_metric_rows_schema_uniqueness_and_development_only_scope(self) -> None:
        self.assertTrue(all(set(row) == set(e002.METRIC_FIELDS) for row in self.metric_rows))
        keys = [
            (row["row_kind"], row["split"], row["subgroup"], row["method"], row["diagnostic_id"])
            for row in self.metric_rows
        ]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual({row["split"] for row in self.metric_rows}, {"development", "calibration"})
        self.assertTrue(all(row["row_kind"] == "method" for row in self.metric_rows))
        self.assertTrue(all(row["interval_status"] == "descriptive-only" for row in self.metric_rows))

    def test_prediction_rows_schema_and_no_confirmatory_scoring(self) -> None:
        self.assertEqual(len(self.prediction_rows), 456 * 8)
        self.assertTrue(
            all(set(e002._prediction_json_row(row)) == set(e002.PREDICTION_FIELDS) for row in self.prediction_rows)
        )
        keys = [(row["run_id"], row["method"], row["case_id"]) for row in self.prediction_rows]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertNotIn("confirmatory", {row["split"] for row in self.prediction_rows})
        self.assertNotIn("truth", inspect.getsource(e002.checker_validation))
        self.assertNotIn("fault_set", inspect.getsource(e002.checker_validation))

    def test_independent_bootstrap_serializer_size_arithmetic(self) -> None:
        self.assertEqual(e002.INDEPENDENT_BOOTSTRAP_BLOCKS, 53)
        self.assertEqual(e002.INDEPENDENT_BOOTSTRAP_REPLICATE_LINES, 530_000)
        self.assertEqual(
            e002.INDEPENDENT_BOOTSTRAP_REPLICATE_LINES
            * e002.INDEPENDENT_BOOTSTRAP_REPLICATE_BYTES
            + e002.INDEPENDENT_BOOTSTRAP_BLOCKS
            * e002.INDEPENDENT_BOOTSTRAP_INTERVAL_BYTES
            + e002.INDEPENDENT_BOOTSTRAP_FIXED_BYTES,
            47_710_564,
        )
        self.assertEqual(e002.BOOTSTRAP_ESTIMATE, 47_710_564)
        with mock.patch.object(e002, "BOOTSTRAP_ESTIMATE", 1):
            with self.assertRaises(e002.ProtocolError):
                e002.runtime_sanity_check(self.population)

    def test_diagnostic_eligibility_and_primary_count_arithmetic_without_scoring(self) -> None:
        eligibility = e002.diagnostic_eligibility(self.population)
        self.assertEqual(
            {key: len(value) for key, value in eligibility.items()},
            {"d1": 48, "d2": 40, "d3": 40},
        )
        self.assertEqual(48 + 40 + 40, 128)
        self.assertEqual(48 + 40 + 40, 3 * 40 + 8)
        self.assertEqual(
            len(e002.SUBGROUPS) * len(e002.METRICS) + len(e002.DIAGNOSTICS), 53
        )

    def test_canonical_manifests_and_template_vocabulary_are_modular(self) -> None:
        population_manifest = e002.population_manifest(self.population)
        self.assertEqual(list(population_manifest), ["protocol_id", "clusters"])
        self.assertEqual(
            [cluster["cluster_id"] for cluster in population_manifest["clusters"][:3]],
            ["H0-C00", "H0-C01", "H0-C02"],
        )
        raw_manifest = e002.raw_prediction_manifest(self.prediction_rows)
        self.assertEqual(raw_manifest["rows"][0]["case_id"], "H0-C00::valid-base")
        valid_template, invalid_template = e002._template_blocks(e002._protocol_text())
        e002._assert_template_grammar(valid_template, invalid_template)
        self.assertNotIn("result_draft_bytes", valid_template)
        self.assertNotIn("result_final_sha256", valid_template)
        self.assertNotIn("mixed/not supported", e002.render_invalid_result(RUN_ID).decode())
        self.assertIn("mixed/not supported", inspect.getsource(e002._h2_summary))

    def test_no_report_hash_participates_before_finalization(self) -> None:
        fingerprint_source = inspect.getsource(e002.PipelineArtifacts.fingerprint)
        build_source = inspect.getsource(e002._build_pipeline_once)
        self.assertNotIn("result_markdown", fingerprint_source + build_source)
        self.assertNotIn("serialized_artifacts", fingerprint_source + build_source)
        self.assertNotIn("sha256_hex(result_bytes)", fingerprint_source + build_source)
        self.assertIn('if key != "result"', fingerprint_source)
        self.assertIn("first.serialized[key] != second.serialized[key]", inspect.getsource(e002.build_pipeline))

    def test_report_negative_zero_is_rejected_before_any_semantic_hash_check(self) -> None:
        run_e002._reject_negative_zero_bytes(
            f"run_id: {RUN_ID}\n".encode("ascii"), "report"
        )
        with self.assertRaisesRegex(run_e002.InvalidRunError, "negative-zero"):
            run_e002._reject_negative_zero_bytes(
                b"delta=-0.000000000\n", "report"
            )
        with tempfile.TemporaryDirectory() as temporary:
            result_file = Path(temporary) / "result.md"
            result_file.write_bytes(b"-0.000000000\n")
            with self.assertRaisesRegex(run_e002.InvalidRunError, "negative-zero"):
                run_e002._validate_result_bytes(
                    result_file, RUN_ID, {}, (), {}, {}, {}
                )

        metric = dict(self.metric_rows[0])
        metric["fpr"] = "-0.000000000"
        with self.assertRaisesRegex(run_e002.InvalidRunError, "negative-zero"):
            run_e002._validate_metric_cells(
                [metric[field] for field in e002.METRIC_FIELDS]
            )
        bootstrap = dict(self.bootstrap.rows[0])
        bootstrap["delta"] = "-0.000000000"
        with self.assertRaisesRegex(run_e002.InvalidRunError, "negative-zero"):
            run_e002._validate_bootstrap_cells(
                [bootstrap[field] for field in e002.BOOTSTRAP_FIELDS]
            )

    def test_report_digest_namespaces_are_exact_and_swaps_fail(self) -> None:
        artifact_hashes = {
            "predictions": "1" * 64,
            "metrics": "2" * 64,
            "bootstrap": "3" * 64,
        }
        manifest_hashes = {
            "raw_prediction": "4" * 64,
            "calibration": "5" * 64,
            "metric": "6" * 64,
            "bootstrap": "7" * 64,
        }
        calibration_hash = "8" * 64
        valid = "\n".join(
            (
                f"lookup_manifest_sha256: {calibration_hash}",
                "- [predictions](../../../data/E002-v1-predictions.jsonl) "
                f"sha256={artifact_hashes['predictions']}",
                "- [metrics](../../../data/E002-v1-metrics.csv) "
                f"sha256={artifact_hashes['metrics']}",
                "- [bootstrap](../../../data/E002-v1-bootstrap.csv) "
                f"sha256={artifact_hashes['bootstrap']}",
                f"raw_prediction_manifest: {manifest_hashes['raw_prediction']}",
                f"calibration_manifest: {manifest_hashes['calibration']}",
                f"metric_manifest: {manifest_hashes['metric']}",
                f"bootstrap_manifest: {manifest_hashes['bootstrap']}",
                f"prediction_bytes: {artifact_hashes['predictions']}",
                f"metrics_bytes: {artifact_hashes['metrics']}",
                f"bootstrap_bytes: {artifact_hashes['bootstrap']}",
            )
        ) + "\n"
        run_e002._validate_report_digest_fields(
            valid, artifact_hashes, manifest_hashes, calibration_hash
        )
        swapped_artifact = valid.replace(
            f"sha256={artifact_hashes['bootstrap']}",
            f"sha256={manifest_hashes['bootstrap']}",
            1,
        )
        with self.assertRaisesRegex(run_e002.InvalidRunError, "digest field"):
            run_e002._validate_report_digest_fields(
                swapped_artifact, artifact_hashes, manifest_hashes, calibration_hash
            )
        swapped_manifest = valid.replace(
            f"bootstrap_manifest: {manifest_hashes['bootstrap']}",
            f"bootstrap_manifest: {artifact_hashes['bootstrap']}",
            1,
        )
        with self.assertRaisesRegex(run_e002.InvalidRunError, "digest field"):
            run_e002._validate_report_digest_fields(
                swapped_manifest, artifact_hashes, manifest_hashes, calibration_hash
            )

    def test_report_placeholder_values_are_checked_against_independent_expectations(self) -> None:
        template = "value=<INT>;state=<STATUS>"
        expected = {"INT": ["7"], "STATUS": ["valid"]}
        run_e002._validate_report_template_shape("value=7;state=valid\n", template, expected)
        with self.assertRaises(run_e002.InvalidRunError):
            run_e002._validate_report_template_shape("value=8;state=valid\n", template, expected)

    def test_multi_fault_external_relation_evidence_is_complete_and_deterministic(self) -> None:
        rows, counts, evidence_bytes, evidence_hash = e002.multi_fault_relation_evidence(
            self.population
        )
        self.assertEqual(len(rows), 432)
        self.assertEqual(sum(counts.values()), 432)
        self.assertEqual([row["case_id"] for row in rows], sorted(row["case_id"] for row in rows))
        self.assertTrue(set(row["relation"] for row in rows).issubset({"equals", "contains", "differs"}))
        for row in rows:
            recipe_id = row["case_id"].rsplit("::", 1)[1]
            self.assertEqual(
                tuple(row["observed_oracle_failure_set"]),
                e002.INDEPENDENT_MULTI_OBSERVED_FAILURES[recipe_id],
            )
            self.assertEqual(
                row["relation"], e002.INDEPENDENT_MULTI_RELATION[recipe_id]
            )
        self.assertEqual((rows, counts, evidence_bytes, evidence_hash), e002.multi_fault_relation_evidence(self.population))

    def test_staged_schema_validators_reject_malformed_canonical_bytes(self) -> None:
        prediction = e002._prediction_json_row(self.prediction_rows[0])
        bad_prediction = dict(prediction)
        bad_prediction["truth"] = True
        with self.assertRaises(run_e002.InvalidRunError):
            run_e002._validate_prediction_object(bad_prediction, RUN_ID)
        metric = dict(self.metric_rows[0])
        metric["method_pair"] = "m1-b0"
        with self.assertRaises(run_e002.InvalidRunError):
            run_e002._validate_metric_cells([metric[field] for field in e002.METRIC_FIELDS])
        bootstrap = dict(self.bootstrap.rows[0])
        bootstrap["method_pair_key"] = "omit-m1"
        with self.assertRaises(run_e002.InvalidRunError):
            run_e002._validate_bootstrap_cells([bootstrap[field] for field in e002.BOOTSTRAP_FIELDS])
        with tempfile.TemporaryDirectory() as temporary:
            file_path = Path(temporary) / "prediction.jsonl"
            file_path.write_bytes(e002.canonical_json_bytes(bad_prediction) + b"\n")
            fake = SimpleNamespace(prediction_rows=(self.prediction_rows[0],), run_id=RUN_ID)
            with self.assertRaises(run_e002.InvalidRunError):
                run_e002._validate_jsonl_predictions(file_path, fake)

    def test_independent_staged_recomputation_rejects_consistent_object_corruption(self) -> None:
        prediction_bytes = e002.serialize_predictions(self.prediction_rows)
        metric_bytes = e002.serialize_metrics(self.metric_rows)
        bootstrap_bytes = e002.serialize_bootstrap(self.bootstrap.rows)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            prediction_file = root / "predictions.jsonl"
            metric_file = root / "metrics.csv"
            bootstrap_file = root / "bootstrap.csv"

            prediction_file.write_bytes(prediction_bytes)
            parsed, context = run_e002._validate_jsonl_predictions_independent(
                prediction_file,
                RUN_ID,
                required_splits=("development", "calibration"),
            )
            context = dict(context)
            context["prediction_rows"] = parsed
            bootstrap_file.write_bytes(bootstrap_bytes)
            intervals, bootstrap_hash = run_e002._validate_bootstrap_independent(
                bootstrap_file,
                context,
                selected_splits=("development", "calibration"),
                replicate_count=16,
                include_diagnostics=False,
            )
            context["bootstrap_manifest_hash"] = bootstrap_hash
            metric_file.write_bytes(metric_bytes)
            validated_metrics = run_e002._validate_metrics_independent(
                metric_file,
                RUN_ID,
                context,
                intervals,
                selected_splits=("development", "calibration"),
            )
            self.assertEqual(len(validated_metrics), 160)

            corrupted_prediction = json.loads(
                prediction_file.read_text(encoding="utf-8").splitlines()[0],
                parse_float=e002.JsonNumber,
            )
            corrupted_prediction["cluster_signature_sha256"] = "0" * 64
            prediction_file.write_bytes(
                e002.canonical_json_bytes(corrupted_prediction) + b"\n"
                + b"\n".join(prediction_bytes.splitlines()[1:]) + b"\n"
            )
            with self.assertRaises(run_e002.InvalidRunError):
                run_e002._validate_jsonl_predictions_independent(
                    prediction_file,
                    RUN_ID,
                    required_splits=("development", "calibration"),
                )

            metric_lines = metric_bytes.splitlines()
            metric_cells = metric_lines[1].decode("utf-8").split(",")
            metric_cells[metric_cells.index(metric_cells[0])] = metric_cells[0]
            support_index = e002.METRIC_FIELDS.index("support")
            metric_cells[support_index] = "999"
            metric_lines[1] = ",".join(metric_cells).encode("utf-8")
            metric_file.write_bytes(b"\n".join(metric_lines) + b"\n")
            with self.assertRaises(run_e002.InvalidRunError):
                run_e002._validate_metrics_independent(
                    metric_file,
                    RUN_ID,
                    context,
                    intervals,
                    selected_splits=("development", "calibration"),
                )

            bootstrap_lines = bootstrap_bytes.splitlines()
            bootstrap_cells = bootstrap_lines[1].decode("utf-8").split(",")
            delta_index = e002.BOOTSTRAP_FIELDS.index("delta")
            bootstrap_cells[delta_index] = "0.123456789"
            bootstrap_lines[1] = ",".join(bootstrap_cells).encode("utf-8")
            bootstrap_file.write_bytes(b"\n".join(bootstrap_lines) + b"\n")
            with self.assertRaises(run_e002.InvalidRunError):
                run_e002._validate_bootstrap_independent(
                    bootstrap_file,
                    context,
                    selected_splits=("development", "calibration"),
                    replicate_count=16,
                    include_diagnostics=False,
                )

    def test_runner_schema_literals_survive_core_field_tuple_mutations(self) -> None:
        prediction = e002._prediction_json_row(self.prediction_rows[0])
        metric = self.metric_rows[0]
        bootstrap = self.bootstrap.rows[0]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            prediction_file = root / "predictions.jsonl"
            # json.dumps intentionally changes the canonical numeric token and
            # preserves the serializer's insertion order rather than the
            # locked UTF-8 key order.
            prediction_file.write_text(
                json.dumps(prediction, ensure_ascii=True, separators=(",", ":")) + "\n",
                encoding="utf-8",
            )
            metric_bytes = bytearray(e002.serialize_metrics((metric,)))
            metric_header = metric_bytes.splitlines()[0].split(b",")
            metric_header[0], metric_header[1] = metric_header[1], metric_header[0]
            metric_file = root / "metrics.csv"
            metric_file.write_bytes(b",".join(metric_header) + b"\n" + metric_bytes.split(b"\n", 1)[1])
            bootstrap_bytes = bytearray(e002.serialize_bootstrap((bootstrap,)))
            bootstrap_header = bootstrap_bytes.splitlines()[0].split(b",")
            bootstrap_header[0], bootstrap_header[1] = bootstrap_header[1], bootstrap_header[0]
            bootstrap_file = root / "bootstrap.csv"
            bootstrap_file.write_bytes(
                b",".join(bootstrap_header) + b"\n" + bootstrap_bytes.split(b"\n", 1)[1]
            )
            fake = SimpleNamespace(prediction_rows=(self.prediction_rows[0],), run_id=RUN_ID)
            mutations = (
                ("PREDICTION_FIELDS", lambda: run_e002._validate_jsonl_predictions(prediction_file, fake)),
                (
                    "METRIC_FIELDS",
                    lambda: run_e002._validate_csv_artifact(
                        metric_file,
                        run_e002._LOCKED_METRIC_FIELDS,
                        (metric,),
                        run_e002._validate_metric_cells,
                    ),
                ),
                (
                    "BOOTSTRAP_FIELDS",
                    lambda: run_e002._validate_csv_artifact(
                        bootstrap_file,
                        run_e002._LOCKED_BOOTSTRAP_FIELDS,
                        (bootstrap,),
                        run_e002._validate_bootstrap_cells,
                    ),
                ),
            )
            for field_name, probe in mutations:
                with self.subTest(field_name=field_name):
                    original = getattr(e002, field_name)
                    with mock.patch.object(e002, field_name, original + ("unexpected",)):
                        with self.assertRaises(run_e002.InvalidRunError):
                            probe()

    def test_runner_validator_identity_and_na_literals_survive_core_mutations(self) -> None:
        prediction = e002._prediction_json_row(self.prediction_rows[0])
        prediction["protocol_commit"] = "0" * 40
        with mock.patch.object(e002, "PROTOCOL_COMMIT", "0" * 40):
            with self.assertRaises(run_e002.InvalidRunError):
                run_e002._validate_prediction_object(prediction, RUN_ID)
        metric = dict(self.metric_rows[0])
        metric["method_pair"] = "BROKEN"
        with mock.patch.object(e002, "NA", "BROKEN"):
            with self.assertRaises(run_e002.InvalidRunError):
                run_e002._validate_metric_cells(
                    [metric[field] for field in e002.METRIC_FIELDS]
                )

    def _fake_artifacts(self) -> SimpleNamespace:
        serialized = {
            "predictions": b"prediction\n",
            "metrics": b"metric\n",
            "bootstrap": b"bootstrap\n",
            "result": b"result\n",
        }
        return SimpleNamespace(
            run_id=RUN_ID,
            prediction_rows=(),
            metric_rows=(),
            bootstrap=SimpleNamespace(rows=()),
            serialized=serialized,
            artifact_hashes={
                name: e002.sha256_hex(content)
                for name, content in serialized.items()
                if name != "result"
            },
        )

    def _no_validation(self, _artifacts: object) -> None:
        return None

    def test_runner_guard_observes_nonexistent_output_root_before_mkdir(self) -> None:
        observations: list[bool] = []

        def guard(_repository: Path, output_root: Path, final_paths: object) -> None:
            observations.append(output_root.exists())
            self.assertFalse(output_root.exists())
            self.assertTrue(all(not target.exists() for target in final_paths.values()))
            raise run_e002.InvalidRunError("guard probe")

        with tempfile.TemporaryDirectory() as temporary:
            output_root = Path(temporary) / "not-created"
            with self.assertRaises(run_e002.InvalidRunError):
                run_e002.execute_run(RUN_ID, output_root, protocol_guard_fn=guard)
            self.assertEqual(observations, [False])
            self.assertFalse(output_root.exists())

    def test_runner_factory_failure_has_no_root_or_invalid_record(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output_root = Path(temporary) / "never-created"

            def guard(_repository: Path, root: Path, finals: object) -> None:
                self.assertFalse(root.exists())
                self.assertTrue(all(not target.exists() for target in finals.values()))

            def factory(_run_id: str, _repository: Path) -> object:
                raise run_e002.InvalidRunError("factory fault")

            with self.assertRaises(run_e002.InvalidRunError):
                run_e002.execute_run(
                    RUN_ID,
                    output_root,
                    protocol_guard_fn=guard,
                    pipeline_factory=factory,
                )
            self.assertFalse(output_root.exists())

    def test_runner_temp_writer_success_external_hash_and_overwrite_refusal(self) -> None:
        fake = self._fake_artifacts()

        def guard(_repository: Path, output_root: Path, final_paths: object) -> None:
            if output_root.exists():
                self.assertTrue(any(target.exists() for target in final_paths.values()))
                raise run_e002.InvalidRunError("overwrite")

        with tempfile.TemporaryDirectory() as temporary:
            output_root = Path(temporary) / "results-root"
            outcome = run_e002.execute_run(
                RUN_ID,
                output_root,
                protocol_guard_fn=guard,
                pipeline_factory=lambda _run_id, _repository: fake,
                artifact_validator_fn=self._no_validation,
                staged_validator_fn=lambda _paths, _artifacts: None,
            )
            final_paths = run_e002._final_paths(output_root, RUN_ID)
            self.assertEqual(outcome["status"], "valid")
            self.assertEqual(outcome["result_sha256"], e002.sha256_hex(final_paths["result"].read_bytes()))
            self.assertNotIn(outcome["result_sha256"].encode(), final_paths["result"].read_bytes())
            self.assertTrue(all(target.is_file() for target in final_paths.values()))
            with self.assertRaises(run_e002.InvalidRunError):
                run_e002.execute_run(
                    RUN_ID,
                    output_root,
                    protocol_guard_fn=guard,
                    pipeline_factory=lambda _run_id, _repository: fake,
                    artifact_validator_fn=self._no_validation,
                    staged_validator_fn=lambda _paths, _artifacts: None,
                )

    def test_runner_post_destination_failure_cleans_valid_finals_and_stage(self) -> None:
        fake = self._fake_artifacts()

        def guard(_repository: Path, output_root: Path, final_paths: object) -> None:
            self.assertFalse(output_root.exists())
            self.assertTrue(all(not target.exists() for target in final_paths.values()))

        def create_byte_identical_then_raise(source: Path, destination: Path) -> None:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(source.read_bytes())
            raise run_e002.InvalidRunError("unreceipted post-destination fault")

        with tempfile.TemporaryDirectory() as temporary:
            output_root = Path(temporary) / "post-destination"
            with self.assertRaises(run_e002.InvalidRunError):
                run_e002.execute_run(
                    RUN_ID,
                    output_root,
                    protocol_guard_fn=guard,
                    pipeline_factory=lambda _run_id, _repository: fake,
                    publish_fn=create_byte_identical_then_raise,
                    artifact_validator_fn=self._no_validation,
                    staged_validator_fn=lambda _paths, _artifacts: None,
                )
            finals = run_e002._final_paths(output_root, RUN_ID)
            # Identical bytes do not establish ownership.  The arbitrary
            # publisher created this race target and raised before issuing a
            # runner receipt, so cleanup must preserve it and fail closed.
            self.assertTrue(finals["predictions"].is_file())
            self.assertEqual(finals["predictions"].read_bytes(), b"prediction\n")
            self.assertFalse(finals["metrics"].exists())
            self.assertFalse(finals["bootstrap"].exists())
            self.assertFalse(finals["result"].exists())
            self.assertFalse(any(".e002-stage-" in str(item) for item in output_root.rglob("*")))

    def test_runner_owned_receipt_allows_post_publish_cleanup(self) -> None:
        fake = self._fake_artifacts()

        def post_fault(
            _source: Path, _destination: Path, _receipt: run_e002._PublicationReceipt
        ) -> None:
            raise run_e002.InvalidRunError("post-receipt fault")

        with tempfile.TemporaryDirectory() as temporary:
            output_root = Path(temporary) / "receipt-cleanup"
            with self.assertRaises(run_e002.InvalidRunError):
                run_e002.execute_run(
                    RUN_ID,
                    output_root,
                    protocol_guard_fn=lambda *_args: None,
                    pipeline_factory=lambda _run_id, _repository: fake,
                    publish_fn=run_e002._publish_exclusive,
                    post_publish_fn=post_fault,
                    artifact_validator_fn=self._no_validation,
                    staged_validator_fn=lambda _paths, _artifacts: None,
                )
            finals = run_e002._final_paths(output_root, RUN_ID)
            self.assertFalse(finals["predictions"].exists())
            self.assertFalse(finals["metrics"].exists())
            self.assertFalse(finals["bootstrap"].exists())
            self.assertTrue(finals["result"].is_file())
            self.assertIn(b"status: invalid", finals["result"].read_bytes())
            self.assertFalse(any(".e002-stage-" in str(item) for item in output_root.rglob("*")))

    def test_runner_receipt_identity_preserves_race_replacement(self) -> None:
        fake = self._fake_artifacts()

        def replace_after_receipt(
            _source: Path, destination: Path, _receipt: run_e002._PublicationReceipt
        ) -> None:
            destination.unlink()
            destination.write_bytes(b"external replacement\n")
            raise run_e002.InvalidRunError("post-receipt race")

        with tempfile.TemporaryDirectory() as temporary:
            output_root = Path(temporary) / "receipt-race"
            with self.assertRaisesRegex(run_e002.InvalidRunError, "persistent cleanup"):
                run_e002.execute_run(
                    RUN_ID,
                    output_root,
                    protocol_guard_fn=lambda *_args: None,
                    pipeline_factory=lambda _run_id, _repository: fake,
                    publish_fn=run_e002._publish_exclusive,
                    post_publish_fn=replace_after_receipt,
                    artifact_validator_fn=self._no_validation,
                    staged_validator_fn=lambda _paths, _artifacts: None,
                )
            finals = run_e002._final_paths(output_root, RUN_ID)
            self.assertEqual(finals["predictions"].read_bytes(), b"external replacement\n")
            self.assertFalse(finals["result"].exists())

    def test_partial_mkdir_failure_tracks_only_created_directories(self) -> None:
        real_mkdir = Path.mkdir
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "a" / "b" / "c"
            created: list[Path] = []
            calls = {"count": 0}

            def mkdir_with_fault(*args: object, **kwargs: object) -> None:
                calls["count"] += 1
                directory = root / "a" if calls["count"] == 1 else root / "a" / "b"
                if calls["count"] == 2:
                    raise OSError("injected partial mkdir failure")
                real_mkdir(directory, *args, **kwargs)

            with mock.patch.object(Path, "mkdir", side_effect=mkdir_with_fault):
                with self.assertRaises(OSError):
                    run_e002._mkdir_tracked(target, created)
            self.assertEqual(created, [root / "a"])
            run_e002._remove_directories_verified(created)
            self.assertFalse((root / "a").exists())

    def test_runner_transient_cleanup_failure_retries_and_leaves_no_valid_finals(self) -> None:
        fake = self._fake_artifacts()
        real_remove = run_e002._remove_tree_verified
        calls = {"count": 0}

        def flaky_remove(directory: Path) -> None:
            calls["count"] += 1
            if calls["count"] == 1:
                raise run_e002.InvalidRunError("transient cleanup fault")
            real_remove(directory)

        with tempfile.TemporaryDirectory() as temporary, mock.patch.object(
            run_e002, "_remove_tree_verified", side_effect=flaky_remove
        ):
            output_root = Path(temporary) / "transient-cleanup"
            with self.assertRaises(run_e002.InvalidRunError):
                run_e002.execute_run(
                    RUN_ID,
                    output_root,
                    protocol_guard_fn=lambda *_args: None,
                    pipeline_factory=lambda _run_id, _repository: fake,
                    artifact_validator_fn=self._no_validation,
                    staged_validator_fn=lambda _paths, _artifacts: None,
                )
            finals = run_e002._final_paths(output_root, RUN_ID)
            self.assertFalse(finals["predictions"].exists())
            self.assertFalse(finals["metrics"].exists())
            self.assertFalse(finals["bootstrap"].exists())
            self.assertTrue(finals["result"].is_file())
            self.assertGreaterEqual(calls["count"], 2)
            self.assertFalse(any(".e002-stage-" in str(item) for item in output_root.rglob("*")))

    def test_runner_persistent_cleanup_failure_is_reported_without_partial_outputs(self) -> None:
        fake = self._fake_artifacts()
        real_remove = run_e002._remove_tree_verified

        def remove_then_report(directory: Path) -> None:
            real_remove(directory)
            raise run_e002.InvalidRunError("persistent cleanup injection")

        with tempfile.TemporaryDirectory() as temporary, mock.patch.object(
            run_e002, "_remove_tree_verified", side_effect=remove_then_report
        ):
            output_root = Path(temporary) / "persistent-cleanup"
            with self.assertRaisesRegex(run_e002.InvalidRunError, "persistent cleanup"):
                run_e002.execute_run(
                    RUN_ID,
                    output_root,
                    protocol_guard_fn=lambda *_args: None,
                    pipeline_factory=lambda _run_id, _repository: fake,
                    artifact_validator_fn=self._no_validation,
                    staged_validator_fn=lambda _paths, _artifacts: None,
                )
            self.assertFalse(output_root.exists())

    def test_protocol_guard_mock_clean_identity_and_ancestor(self) -> None:
        repository = Path(__file__).resolve().parents[3]
        output_root = repository

        def fake_git(_repository: Path, *arguments: str) -> str:
            if arguments[:1] == ("status",):
                return ""
            if arguments[:1] == ("rev-parse",):
                return e002.PROTOCOL_BLOB + "\n"
            return ""

        show_result = SimpleNamespace(stdout=(repository / e002.PROTOCOL_PATH).read_bytes())
        with mock.patch.object(run_e002, "_git", side_effect=fake_git), mock.patch.object(
            run_e002.subprocess, "run", return_value=show_result
        ):
            run_e002._protocol_guard(
                repository,
                output_root,
                run_e002._final_paths(output_root, RUN_ID),
            )
        self.assertTrue(output_root.exists())

    def test_default_protocol_guard_rejects_alternate_root_before_mkdir(self) -> None:
        repository = Path(__file__).resolve().parents[3]
        with tempfile.TemporaryDirectory() as temporary:
            output_root = Path(temporary) / "alternate-root"
            self.assertFalse(output_root.exists())

            def fake_git(_repository: Path, *arguments: str) -> str:
                if arguments[:1] == ("status",):
                    return ""
                if arguments[:1] == ("rev-parse",):
                    return e002.PROTOCOL_BLOB + "\n"
                return ""

            show_result = SimpleNamespace(stdout=(repository / e002.PROTOCOL_PATH).read_bytes())
            with mock.patch.object(run_e002, "_git", side_effect=fake_git), mock.patch.object(
                run_e002.subprocess, "run", return_value=show_result
            ):
                with self.assertRaisesRegex(
                    run_e002.InvalidRunError, "output root must be repository root"
                ):
                    run_e002._protocol_guard(
                        repository,
                        output_root,
                        run_e002._final_paths(output_root, RUN_ID),
                    )
            self.assertFalse(output_root.exists())

    def test_output_paths_and_repository_outputs_remain_absent(self) -> None:
        repository = Path(__file__).resolve().parents[3]
        reserved = (
            repository / "data" / "E002-v1-predictions.jsonl",
            repository / "data" / "E002-v1-metrics.csv",
            repository / "data" / "E002-v1-bootstrap.csv",
            repository
            / "experiments"
            / "E002-heterogeneous-specification-stress"
            / "results"
            / f"run-{RUN_ID}.md",
            repository
            / "experiments"
            / "E002-heterogeneous-specification-stress"
            / "code"
            / "__pycache__",
        )
        self.assertTrue(all(not target.exists() for target in reserved))


if __name__ == "__main__":
    unittest.main()
