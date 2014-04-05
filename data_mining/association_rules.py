#!/usr/bin/env python
# -*- encoding: utf8 -*-

import sys
import optparse
import itertools
import datetime
import time

__author__ = 'fcamel'


VERBOSE = False

class Items(object):
    def __init__(self, raw_items):
        '''
        |items| is a list of unicode.
        '''
        self.data = sorted(raw_items)
        self._key = u'\t'.join(self.data)
        self._hash = hash(self._key)

    def __eq__(self, other):
        if not isinstance(other, Items):
            return False
        return self._key == other._key

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return self._hash

    def __cmp__(self, other):
        return cmp(self.data, other.data)

    def __len__(self):
        return len(self.data)

    def issubset(self, other):
        if len(self) > len(other):
            return False
        for item in self.data:
            if item not in other.data:
                return False
        return True

    def diff(self, other):
        '''
        Must be called when self.issubset(other) is True
        '''
        items = []
        for item in self.data:
            if item not in other.data:
                items.append(item)
        return items


class Itemset(object):
    def __init__(self, raw_items, support):
        self.items = Items(raw_items)
        self.support = support

    def __eq__(self, other):
        if not isinstance(other, Itemset):
            return False
        return (self.support == other.support
                and self.items == other.items)

    def __ne__(self, other):
        return not self == other

    def __cmp__(self, other):
        c = cmp(self.items, other.items)
        if c:
            return c
        return cmp(self.support, other.support)

    def __str__(self):
        return '<%s> %d' % (', '.join(self.items.data), self.support)

    def __unicode__(self):
        return u'<%s> %d' % (u', '.join(self.items.data), self.support)

    def __len__(self):
        return len(self.items)

    def issubset(self, other):
        return self.items.issubset(other.items)


class Rule(object):
    def __init__(self, from_, to, from_support, confidence):
        self.from_ = from_
        self.to = to
        self.from_support = from_support
        self.confidence = confidence

    def __eq__(self, other):
        if not isinstance(other, Rule):
            return False
        return (self.from_ == other.from_
                and self.to == other.to
                and self.from_support == other.from_support
                and self.confidence == other.confidence)

    def __ne__(self, other):
        return not self == other

    def __cmp__(self, other):
        c = cmp(self.confidence, other.confidence)
        if c:
            return -1 * c
        c = cmp(self.from_support, other.from_support)
        if c:
            return c
        c = cmp(self.from_, other.from_)
        if c:
            return c
        return cmp(self.to, other.to)

    def __str__(self):
        return ('%s (%d) -> %s (%.3f)'
                '' % (', '.join(self.from_), self.from_support,
                      ', '.join(self.to), self.confidence))

    def __unicode__(self):
        return (u'%s (%d) -> %s (%.3f)'
                u'' % (u', '.join(self.from_), self.from_support,
                       u', '.join(self.to), self.confidence))


def to_console(string):
    if not VERBOSE:
        return
    t = time.time()
    t = datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')
    sys.stderr.write('%s\t%s\n' % (t, string))

def load_data(filename):
    rows = []
    with open(filename) as fr:
        for line in fr:
            _, items_string = line.decode('utf8').rstrip().split('\t')
            rows.append(items_string.split(' '))
    return rows

def find_frequent_itemsets(rows, support, max_k):
    to_console('** find_frequent_itemsets() begins')
    result = []
    # Ensure all items are in order
    for r in rows:
        r.sort()

    # Find 1-frequent itemset
    counts = {}
    for r in rows:
        for item in r:
            if item not in counts:
                counts[item] = 0
            counts[item] += 1

    freq_itemsets = []
    for k, v in counts.iteritems():
        if v >= support:
            freq_itemsets.append(Itemset([k], v))
    freq_itemsets.sort()
    result.extend(freq_itemsets)

    to_console('** find_frequent_itemsets() # of 1-freq: %d' % len(freq_itemsets))

    # Find k-frequent itemset, k >= 2
    k = 1
    while freq_itemsets and k < max_k:
        k += 1
        candidates = set()
        for itemset in freq_itemsets:
            candidates.update(itemset.items.data)

        counts = {}
        for r in rows:
            subset = []
            for item in r:
                if item in candidates:
                    subset.append(item)
            if len(subset) < k:
                continue

            for raw_items in itertools.combinations(subset, k):
                items = Items(raw_items)
                if items not in counts:
                    counts[items] = 0
                counts[items] += 1

        freq_itemsets = []
        for items, v in counts.iteritems():
            if v >= support:
                freq_itemsets.append(Itemset(items.data, v))
        freq_itemsets.sort()
        result.extend(freq_itemsets)
        to_console('** find_frequent_itemsets() # of %d-freq: %d'
                   '' % (k, len(freq_itemsets)))

    to_console('** find_frequent_itemsets() end')
    return result

def find_association_rules(freq_itemsets, min_confidence):
    to_console('** find_association_rules() begin # of itemsets: %d'
               '' % len(freq_itemsets))
    rules = []
    for a in freq_itemsets:
        for b in freq_itemsets:
            if a == b:
                continue
            if not a.issubset(b):
                continue
            from_ = a.items.data
            to = b.items.diff(a.items)
            confidence = float(b.support) / a.support
            if confidence >= min_confidence:
                rules.append(Rule(from_, to, a.support, confidence))
    to_console('** find_association_rules() end')
    return sorted(rules)

def main():
    '''\
    %prog [options] <filename>

    Format in <filename>

    tid<TAB>item1 item2 ... itemk
    tid<TAB>item1 item2 ... itemk
    ...
    tid<TAB>item1 item2 ... itemk
    '''
    global VERBOSE

    parser = optparse.OptionParser(usage=main.__doc__)
    parser.add_option('-v', '--verbose', dest='verbose',
                      action='store_true', default=False)
    parser.add_option('-s', '--support', dest='support', type=int,
                      help='minimum support for frequent item set (default: 10).',
                      default=10)
    parser.add_option('-c', '--confidence', dest='confidence', type=float,
                      help='minimum confidence (default: 0.1).', default=0.1)
    parser.add_option('-k', '--k-frequent-itemset', dest='kfreq', type=int,
                      help='find at most k-frequent itemset (default: 10).',
                      default=10)
    options, args = parser.parse_args()

    if len(args) != 1:
        parser.print_help()
        return 1

    VERBOSE = options.verbose
    filename = args[0]

    rows = load_data(filename)
    freq_itemsets = find_frequent_itemsets(rows, options.support, options.kfreq)
    rules = find_association_rules(freq_itemsets, options.confidence)
    for r in rules:
        print unicode(r).encode('utf8')

    return 0


if __name__ == '__main__':
    sys.exit(main())
