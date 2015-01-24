#!/usr/bin/env python
# -*- encoding: utf8 -*-

import sys
import optparse

import cluster


def main():
    '''\
    %prog [options] <rating_file> <k>

    Run K-Means on <rating_file> with K = <k>
    '''
    parser = optparse.OptionParser(usage=main.__doc__)
    options, args = parser.parse_args()

    if len(args) != 2:
        parser.print_help()
        return 1

    filename, k = args
    k = int(k)
    data = []
    for line in open(filename):
        ts = line.split('\t')
        if len(ts) != 7:
            continue
        app_name = ts[0]
        # the number of 5 stars, 4 stars, .., 1 star
        rating_numbers = map(int, ts[2:])
        sum_ = float(sum(rating_numbers))
        if not sum_:
            continue
        rating_numbers = tuple(n / sum_ for n in rating_numbers)
        d = cluster.Data(app_name, rating_numbers)
        data.append(d)

    cl = cluster.KMeansClustering(data)
    clusters = cl.getclusters(k)
    for i, c in enumerate(clusters):
        print 'Cluster %d' % (i + 1)
        print '-' * 40
        for d in sorted(c):
            print str(d)
        print

    return 0


if __name__ == '__main__':
    sys.exit(main())
