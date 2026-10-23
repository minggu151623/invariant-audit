import unittest

import certificate as c
import exhaustive_reference as r


class CertificateTests(unittest.TestCase):
    def check(self, table, expected, rules=(0, 1), alphabet=2):
        cost, edits = c.radius(table, rules, alphabet)
        self.assertEqual(cost, expected)
        self.assertEqual(cost, r.all_radii(table, alphabet)[rules][0])
        if cost is not None:
            values = [value for _mask, value in table]
            before = r.decisions(table, values)[r.RULE_SETS.index(rules)]
            for index, value in edits:
                self.assertNotEqual(index, 0)
                values[index] = value
            self.assertEqual(sum(a[1] != b for a, b in zip(table, values)), cost)
            self.assertNotEqual(before, r.decisions(table, values)[r.RULE_SETS.index(rules)])

    def test_singleton(self):
        self.check(((3, 0),), None)

    def test_outside_row_does_not_break_protected_group(self):
        self.check(((3, 0), (0, 1)), None)

    def test_tie_rejects_and_one_edit_repairs(self):
        self.check(((3, 0), (3, 1)), 1)

    def test_complete_overlap(self):
        self.check(((3, 0), (3, 1), (3, 1)), 1)

    def test_disjoint_edit_support(self):
        table = ((3, 0), (1, 1), (1, 1), (2, 1), (2, 1))
        self.check(table, 2)
        self.assertEqual(c.repair_to_accept(table, (0,), 2)[0], 1)
        self.assertEqual(c.repair_to_accept(table, (1,), 2)[0], 1)

    def test_zero_only_group_fresh_rival(self):
        self.check(((3, 0), (3, 0), (3, 0)), 2)

    def test_ternary_competitors(self):
        self.check(((3, 0), (3, 1), (3, 2)), 1, alphabet=3)

    def test_single_rule_ignores_other_rule(self):
        self.check(((3, 0), (2, 1)), None, rules=(0,))

    def test_determinant_edit_scope(self):
        table = ((3, 0), (0, 1))
        self.assertTrue(c.accepts(table, (0, 1)))
        self.assertFalse(c.accepts(((3, 0), (1, 1)), (0, 1)))


if __name__ == '__main__':
    unittest.main()
