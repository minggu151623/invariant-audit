import unittest

import closed_form
import generic_milp


class ModelTests(unittest.TestCase):
    def compare(self, table, rules, expected, keys=2, rhs=2):
        result = generic_milp.solve(table, rules, keys, rhs)
        self.assertEqual(result['status'], 2 if expected is None else 0)
        self.assertEqual(result['cost'], expected)
        self.assertEqual(result['verification_errors'], [])
        if generic_milp.accepts(table, rules):
            self.assertEqual(closed_form.radius(table, rules, rhs)[0], expected)

    def test_empty_edit_space(self):
        self.compare(((0, 0, 0, 0),), ((0,), (1,)), None)

    def test_singleton_import_cost_four(self):
        self.compare(((0, 0, 0, 0), (1, 1, 1, 0)), ((0, 1, 2),), 4)

    def test_alternate_raw_keys(self):
        self.compare(((0, 0, 0, 0), (2, 2, 2, 0)), ((0, 1, 2),), 4, keys=3)

    def test_key_import_cost_one(self):
        self.compare(((0, 0, 0, 0), (1, 0, 0, 1)), ((0, 1), (0, 2)), 1)

    def test_nonsingleton_margin_cost_two(self):
        self.compare(((0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)), ((0,),), 2)

    def test_ternary_accepted(self):
        self.compare(((0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 1)), ((0,),), 1, rhs=3)

    def test_rejected_shared_key_synergy(self):
        self.compare(((0, 0, 0, 0), (0, 0, 1, 1), (0, 1, 0, 1), (1, 0, 0, 0)),
                     ((0, 1), (0, 2)), 1)

    def test_rejected_tie(self):
        self.compare(((0, 0, 0, 0), (0, 0, 0, 1)), ((0,),), 1)

    def test_closed_form_rejects_inapplicable_direction(self):
        with self.assertRaises(ValueError):
            closed_form.radius(((0, 0, 0, 0), (0, 0, 0, 1)), ((0,),), 2)


if __name__ == '__main__':
    unittest.main()
