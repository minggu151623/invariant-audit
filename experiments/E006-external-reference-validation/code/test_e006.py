from fractions import Fraction as F
from hashlib import sha256
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

import evaluate as e
import point_reference
import run_e006 as runner


def fixture():
    headers = ['index', 'brewery_id', 'brewery_name', 'city', 'state', 'other']
    dirty, reference = [], []
    for group in range(150):
        for member in range(3):
            key = str(group*3+member)
            dirty.append((key, str(group), 'brewery' if member < 2 else 'mistyped', 'town', 'CA', 'same'))
            reference.append((key, str(group), 'brewery', 'town', 'CA', 'same'))
    return headers, tuple(dirty), tuple(reference)


class SourceTests(unittest.TestCase):
    def test_normalization_retains_unrequested_characters(self):
        self.assertEqual(e.normalize('\t A &amp;\nB \u00a0C\r '), 'A & B \u00a0C\r')
        self.assertEqual(e.normalize('NaN'), 'NaN')
        self.assertEqual(e.normalize('a\t\n b'), 'a b')

    def test_csv_quotes_empty_records_and_embedded_newline(self):
        data = b'a,b\n\n1,"x\ny"\n2,""\n'
        self.assertEqual(e.parse_table(data, ['a', 'b']), (('1', 'x y'), ('2', '')))
        with self.assertRaises(e.EvaluationError):
            e.parse_table(b'a,b\n1,2,3\n', ['a', 'b'])
        with self.assertRaises(e.EvaluationError):
            e.parse_table(data, ['changed', 'b'])

    def test_alignment_key_mismatch_is_rejected_after_dirty_scoring(self):
        headers, dirty, reference = fixture()
        broken = list(reference)
        broken[0] = ('wrong', *broken[0][1:])
        with self.assertRaises(e.EvaluationError):
            e.evaluate_dataset('beers', headers, dirty, lambda: tuple(broken), replicates=2)

    def test_manifest_drift_stops_before_source_cache_reads(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / 'data').mkdir()
            (root / runner.MANIFEST).write_bytes(b'{}')
            with self.assertRaises(e.EvaluationError):
                runner.source_bytes(root)

    def test_protocol_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            protocol = root / runner.PROTOCOL
            protocol.parent.mkdir(parents=True)
            protocol.write_bytes(b'changed')
            with patch.object(runner, 'git', side_effect=[b'a'*40+b'\n', b'locked']), self.assertRaises(e.EvaluationError):
                runner.guard(root)

    def test_one_byte_source_change_is_rejected_before_table_parsing(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            source = root / 'cache/source'
            source.mkdir(parents=True)
            (root / 'data').mkdir()
            paths = [f'datasets/{d}/{k}.csv' for d in e.DATASETS for k in ('dirty', 'clean')]
            paths += ['README.md', 'LICENSE.md', 'raha/dataset.py']
            records = []
            for path in paths:
                p = source / path
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(b'original')
                records.append({'path': path, 'bytes': 8, 'sha256': sha256(b'original').hexdigest()})
            manifest = e.canonical({'source_commit': '7be1334b8c7bbdac3f47ef514fb3e1e8c5fc181c', 'files': records})
            (root / runner.MANIFEST).write_bytes(manifest)
            (source.parent / 'source-manifest.json').write_bytes(manifest)
            (source / paths[-1]).write_bytes(b'originaL')
            with (patch.object(runner, 'SOURCE', source),
                  patch.object(runner, 'MANIFEST_SHA256', sha256(manifest).hexdigest()),
                  patch.object(e, 'parse_table') as parser, self.assertRaises(e.EvaluationError)):
                runner.source_bytes(root)
            parser.assert_not_called()


class RuleTests(unittest.TestCase):
    def test_three_policies_attribute_same_conflict_differently(self):
        headers = ['index', 'brewery_id', 'brewery_name', 'city', 'state']
        dirty = (('0', '1', 'A', 'x', 'CA'), ('1', '1', 'A', 'x', 'CA'), ('2', '1', 'B', 'x', 'CA'))
        scores = e.score_dirty('beers', headers, dirty, ('development',)*3, e.SPECS['beers'])
        self.assertEqual(scores[:, 1, :].tolist(), [[0, 1, 0, 0]]*3)
        self.assertEqual(scores[:, 2, :].tolist(), [[0, 1, 1, 0], [0, 1, 1, 0], [0, 1, 1, 1]])
        self.assertFalse(scores.flags.writeable)
        self.assertTrue(np.all(scores[:, 3:, :] == 0))

    def test_modal_tie_flags_every_dependent(self):
        headers = ['index', 'brewery_id', 'brewery_name', 'city', 'state']
        dirty = (('0', '1', 'A', 'x', 'CA'), ('1', '1', 'B', 'x', 'CA'))
        scores = e.score_dirty('beers', headers, dirty, ('development',)*2, e.SPECS['beers'])
        self.assertEqual(scores[:, 2, 3].tolist(), [1, 1])

    def test_empty_determinant_excluded_empty_dependent_included(self):
        headers = ['index', 'brewery_id', 'brewery_name', 'city', 'state']
        dirty = (('0', '', 'A', 'x', 'CA'), ('1', '', 'B', 'x', 'CA'),
                 ('2', '1', '', 'x', 'CA'), ('3', '1', 'A', 'x', 'CA'))
        scores = e.score_dirty('beers', headers, dirty, ('development',)*4, e.SPECS['beers'])
        self.assertEqual(scores[:2, 1, :].tolist(), [[2, 2, 2, 2]]*2)
        self.assertTrue(np.all(scores[:2, 2, :] == 0))
        self.assertEqual(scores[2, 2, :].tolist(), [1, 2, 2, 2])

    def test_rules_use_only_current_split_context(self):
        headers = ['index', 'brewery_id', 'brewery_name', 'city', 'state']
        dirty = (('0', '1', 'A', 'x', 'CA'), ('1', '1', 'B', 'x', 'CA'))
        scores = e.score_dirty('beers', headers, dirty, ('development', 'evaluation'), e.SPECS['beers'])
        self.assertTrue(np.all(scores == 0))


class SplitTests(unittest.TestCase):
    def test_transitive_components_and_determinant_isolation(self):
        headers = ['id', 'left', 'second', 'right']
        rows = [(str(i), 'L'+str(i), 'S'+str(i), 'R'+str(i)) for i in range(200)]
        rows[0] = ('0', 'shared-left', 'S0', 'R0')
        rows[1] = ('1', 'shared-left', 'shared-second', 'R1')
        rows[2] = ('2', 'L2', 'shared-second', 'R2')
        spec = {'key': 'id', 'fds': (('left', 'right'), ('second', 'right'))}
        identities, splits = e.components('rayyan', headers, tuple(rows), spec)
        self.assertEqual(identities[0], identities[1])
        self.assertEqual(identities[1], identities[2])
        self.assertEqual(len(set(splits[:3])), 1)
        self.assertEqual(e.components('rayyan', headers, tuple(rows), spec), (identities, splits))

    def test_duplicate_or_empty_keys_and_component_deficit(self):
        headers, dirty, _reference = fixture()
        for replacement in ('', dirty[1][0]):
            changed = list(dirty)
            changed[0] = (replacement, *changed[0][1:])
            with self.assertRaises(e.EvaluationError):
                e.components('beers', headers, tuple(changed), e.SPECS['beers'])
        same_group = tuple((row[0], 'one', *row[2:]) for row in dirty)
        with self.assertRaises(e.EvaluationError):
            e.components('beers', headers, same_group, e.SPECS['beers'])


class MetricTests(unittest.TestCase):
    def test_rational_known_answers_and_independent_agreement(self):
        truth, decision = [1, 1, 0, 0], [True, False, True, False]
        p = (F(4, 5), F(1, 5), F(4, 5), F(1, 5))
        result, difference = e.point_metrics(truth, decision, p)
        self.assertEqual([result[k] for k in ('tp', 'tn', 'fp', 'fn')], [1, 1, 1, 1])
        self.assertAlmostEqual(result['brier'], .34)
        self.assertAlmostEqual(result['ece'], .3)
        self.assertAlmostEqual(result['reliability'], .09)
        self.assertEqual(result['resolution'], 0)
        self.assertLessEqual(difference, 2e-12)
        self.assertEqual(point_reference.compute(truth, decision, p)['brier'], F(17, 50))

    def test_exact_bin_boundaries_and_undefined_denominators(self):
        result, difference = e.point_metrics([1, 0, 1, 0], [True, False, True, False],
                                            (F(1, 10), F(0), F(1), F(9, 10)))
        self.assertAlmostEqual(result['ece'], .45)
        self.assertLessEqual(difference, 2e-12)
        only_positive, _ = e.point_metrics([1, 1], [True, False], (F(1), F(0)))
        self.assertIsNone(only_positive['fpr'])
        self.assertIsNone(only_positive['balanced_accuracy'])

    def test_lookup_smoothing_fallback_and_no_boolean_labels(self):
        lookup, fallback, _record = e.fit_lookup([0, 1], [1, 0])
        self.assertEqual((lookup[0], lookup[1], fallback), (F(2, 3), F(1, 3), F(1, 2)))
        self.assertEqual(lookup.get(9, fallback), F(1, 2))
        with self.assertRaises(e.EvaluationError):
            e.fit_lookup([0], [True])


class BootstrapTests(unittest.TestCase):
    def test_draw_known_answers(self):
        for dataset, replicate, position, size, expected in (
                ('beers', 0, 0, 7, 0), ('flights', 3, 2, 11, 2), ('rayyan', 1, 5, 13, 6)):
            self.assertEqual(e.bootstrap_index(dataset, replicate, position, size), expected)

    def test_identical_paired_methods_give_zero_in_all_28_blocks(self):
        components = tuple(str(i) for i in range(8) for _ in range(2))
        labels = np.array([1, 0]*8)
        decisions = np.repeat(np.array([True, False]*8)[:, None], len(e.METHODS), axis=1)
        probabilities = tuple(tuple([F(9, 10), F(1, 10)]*8) for _ in e.METHODS)
        blocks, intervals, check = e.bootstrap('beers', components, labels, decisions, probabilities, replicates=9)
        self.assertEqual((len(blocks), len(intervals), check['components']), (28, 28, 8))
        for _pair, _metric, values in blocks:
            self.assertTrue(np.all(values == 0))
        self.assertTrue(all(row['lower'] == row['upper'] == 0 and row['status'] == 'degenerate' for row in intervals))

    def test_weighted_sufficient_statistics_match_direct_expansion(self):
        labels = np.array([1, 0, 1, 0])
        decisions = np.repeat(np.array([True, True, False, False])[:, None], 8, axis=1)
        p = tuple((F(4, 5), F(4, 5), F(1, 5), F(1, 5)) for _ in e.METHODS)
        stats = e.sufficient_statistics(np.array([0, 0, 1, 1]), labels, decisions, p, 2)
        totals = (np.array([[2, 1]]) @ stats.reshape(2, -1)).reshape(1, 8, 35)
        computed = e.metrics_from_totals(totals)
        indices = [0, 1, 0, 1, 2, 3]
        reference = point_reference.compute([int(labels[i]) for i in indices], [bool(decisions[i, 0]) for i in indices],
                                            tuple(p[0][i] for i in indices))
        for metric in e.METRICS:
            self.assertAlmostEqual(computed[metric][0, 0], float(reference[metric]))


class PipelineTests(unittest.TestCase):
    def test_full_synthetic_pipeline_and_evaluation_label_perturbation(self):
        headers, dirty, reference = fixture()
        component_ids, splits = e.components('beers', headers, dirty, e.SPECS['beers'])
        events = []
        original_score = e.score_dirty

        def score(*args):
            events.append('score')
            return original_score(*args)

        def load_reference():
            events.append('reference')
            return reference

        with patch.object(e, 'score_dirty', side_effect=score):
            first = e.evaluate_dataset('beers', headers, dirty, load_reference, replicates=3)
        self.assertEqual(events[:2], ['score', 'reference'])
        self.assertEqual(len(first['metrics']), 48)
        self.assertEqual(len(first['intervals']), 28)
        changed = tuple((*row[:-1], 'changed-reference') if split == 'evaluation' else row
                        for row, split in zip(reference, splits))
        second = e.evaluate_dataset('beers', headers, dirty, lambda: changed, replicates=3)
        self.assertEqual(first['checks']['raw_scores_sha256_before_reference_read'],
                         second['checks']['raw_scores_sha256_before_reference_read'])
        self.assertEqual(first['checks']['calibration_lookups_sha256'], second['checks']['calibration_lookups_sha256'])
        self.assertTrue(np.array_equal(first['raw'], second['raw']))
        self.assertTrue(np.array_equal(first['decisions'], second['decisions']))
        self.assertEqual(first['probabilities'], second['probabilities'])
        self.assertNotEqual(first['checks']['split_counts']['evaluation']['invalid_cells'],
                            second['checks']['split_counts']['evaluation']['invalid_cells'])

    def test_existing_output_refused_before_git(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / 'data').mkdir()
            (root / runner.OUTPUTS[0]).write_bytes(b'existing')
            with patch.object(runner, 'git') as command, self.assertRaises(e.EvaluationError):
                runner.guard(root)
            command.assert_not_called()

    def test_late_publication_failure_rolls_back_only_owned_files(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / 'keep').write_bytes(b'original')
            real_link = os.link

            def link(source, destination):
                if destination.name == 'report':
                    raise OSError('late failure')
                return real_link(source, destination)

            with patch.object(runner.os, 'link', side_effect=link), self.assertRaises(OSError):
                runner.publish(root, {'first': b'one', 'second': b'two', 'report': b'valid'})
            self.assertEqual(list(root.iterdir()), [root / 'keep'])

    def test_two_build_mismatch_preserves_only_invalid_report(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / runner.REPORT).parent.mkdir(parents=True)
            with (patch.object(runner, 'guard', return_value=('lock', 'sha', 'impl')),
                  patch.object(runner, 'build', side_effect=[{'x': b'a'}, {'x': b'b'}]),
                  self.assertRaises(e.EvaluationError)):
                runner.execute(root)
            self.assertIn('status: invalid', (root / runner.REPORT).read_text())
            self.assertFalse((root / 'x').exists())


if __name__ == '__main__':
    unittest.main()
