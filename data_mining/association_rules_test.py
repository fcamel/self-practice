#!/usr/bin/env python
# -*- encoding: utf8 -*-

import unittest

import association_rules


__author__ = 'fcamel'


class ItemsTest(unittest.TestCase):
    def testNormal(self):
        a = association_rules.Items(['a'])
        ab = association_rules.Items(['a', 'b'])
        self.assertTrue(a.issubset(ab))
        self.assertFalse(ab.issubset(a))


class ItemsetTest(unittest.TestCase):
    def testNormal(self):
        a = association_rules.Itemset(['a'], 4)
        ab = association_rules.Itemset(['a', 'b'], 2)
        self.assertTrue(a.issubset(ab))
        self.assertFalse(ab.issubset(a))


class FindFrequentItemsetsTest(unittest.TestCase):
    def testEmpty(self):
        actual = association_rules.find_frequent_itemsets([], 2, 10)
        self.assertEqual([], actual)

    def testOneFrequentItemset(self):
        rows = [
            ['a'],
            ['a'],
            ['b'],
        ]
        actual = association_rules.find_frequent_itemsets(rows, 2, 10)

        expected = [
            association_rules.Itemset(['a'], 2),
        ]
        self.assertEqual(expected, actual)

    def testTwoFrequentItemset(self):
        rows = [
            ['a', 'b'],
            ['a', 'b'],
            ['b', 'c'],
        ]
        actual = association_rules.find_frequent_itemsets(rows, 2, 10)

        expected = [
            association_rules.Itemset(['a'], 2),
            association_rules.Itemset(['b'], 3),
            association_rules.Itemset(['a', 'b'], 2),
        ]
        self.assertEqual(expected, actual)

    def testThreeFrequentItemset(self):
        rows = [
            ['a', 'b', 'c', 'd'],
            ['a', 'b', 'c', 'e'],
            ['a', 'b', 'd', 'f'],
        ]
        actual = association_rules.find_frequent_itemsets(rows, 2, 10)

        expected = [
            association_rules.Itemset(['a'], 3),
            association_rules.Itemset(['b'], 3),
            association_rules.Itemset(['c'], 2),
            association_rules.Itemset(['d'], 2),
            association_rules.Itemset(['a', 'b'], 3),
            association_rules.Itemset(['a', 'c'], 2),
            association_rules.Itemset(['a', 'd'], 2),
            association_rules.Itemset(['b', 'c'], 2),
            association_rules.Itemset(['b', 'd'], 2),
            association_rules.Itemset(['a', 'b', 'c'], 2),
            association_rules.Itemset(['a', 'b', 'd'], 2),
        ]
        self.assertEqual(len(expected), len(actual))
        for i in range(len(expected)):
            e = expected[i]
            a = actual[i]
            self.assertEqual(e, a, '%s != %s' % (str(e), str(a)))

    def testUnorderedTwoFrequentItemset(self):
        rows = [
            ['b', 'a'],
            ['c', 'b'],
            ['a', 'b'],
        ]
        actual = association_rules.find_frequent_itemsets(rows, 2, 10)

        expected = [
            association_rules.Itemset(['a'], 2),
            association_rules.Itemset(['b'], 3),
            association_rules.Itemset(['a', 'b'], 2),
        ]
        self.assertEqual(expected, actual)


class FindAssociationRules(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testEmpty(self):
        actual = association_rules.find_association_rules([], 0.1)
        self.assertEqual([], actual)

    def testOneToOne(self):
        data = [
            association_rules.Itemset(['a'], 4),
            association_rules.Itemset(['b'], 2),
            association_rules.Itemset(['a', 'b'], 2),
        ]
        actual = association_rules.find_association_rules(data, 0.1)

        expected = [
            association_rules.Rule(['b'], ['a'], 2, 1.0),
            association_rules.Rule(['a'], ['b'], 4, 0.5),
        ]
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()

