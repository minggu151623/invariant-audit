import unittest

import certificate as c
import exhaustive_reference as r


class MutableKeyTests(unittest.TestCase):
    def check(self, table, expected, family=1, keys=2, rhs=2):
        rules = c.FAMILIES[family][1]
        cost, witness, _states = c.radius(table, rules, rhs)
        self.assertEqual(cost, expected)
        self.assertEqual(cost, r.radius(table, rules, keys, rhs)[0])
        self.assertEqual(c.accepts(table, rules, rhs), r.accepts(table, rules))
        if cost is not None:
            self.assertEqual(witness[0], table[0])
            self.assertEqual(sum(a != b for row, changed in zip(table, witness)
                                 for a, b in zip(row, changed)), cost)
            self.assertNotEqual(r.accepts(table, rules), r.accepts(witness, rules))

    def test_no_context_infinite(self):
        self.check(((0, 0, 0, 0),), None)

    def test_shared_key_repairs_two_groups(self):
        self.check(((0, 0, 0, 0), (0, 0, 1, 1), (0, 1, 0, 1), (1, 0, 0, 0)), 1)

    def test_key_import_breaks_singletons(self):
        self.check(((0, 0, 0, 0), (1, 0, 0, 1)), 1)

    def test_triple_key_plus_rhs_cost(self):
        self.check(((0, 0, 0, 0), (1, 1, 1, 0)), 4, family=3)

    def test_alternate_nonmatching_values(self):
        self.check(((0, 0, 0, 0), (2, 2, 2, 0)), 4, family=3, keys=3)
        row = (2, 1, 2, 0)
        self.assertEqual(c.reconstruct(row, 0, 0), row)

    def test_rejected_tie(self):
        self.check(((0, 0, 0, 0), (0, 0, 0, 1)), 1)

    def test_ternary_rivals(self):
        self.check(((0, 0, 0, 0), (0, 0, 0, 1), (0, 0, 0, 2)), 1, rhs=3)

    def test_domain_equality_membership(self):
        table = ((0, 0, 0, 0), (2, 0, 2, 1))
        self.check(table, 1, family=0, keys=3)

    def test_canonical_row_actions_respect_domain(self):
        for _cost, row, _contribution in c.canonical_actions((2, 0, 2, 1), ((0, 1), (1, 2)), 3):
            self.assertTrue(all(0 <= value < 3 for value in row))


if __name__ == '__main__':
    unittest.main()
