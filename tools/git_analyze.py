#!/usr/bin/env python
# -*- encoding: utf8 -*-

import sys
import subprocess
import operator
import optparse
import os

def main():
    '''\
    %prog [options] <path>
    '''
    parser = optparse.OptionParser(usage=main.__doc__)
    options, args = parser.parse_args()

    if len(args) != 1:
        parser.print_help()
        return 1
    path = args[0]

    # Get commits per author.
    cmd = "git shortlog -c -s -n -e %s" % path
    proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    out, err = proc.communicate()

    count = {}
    for line in out.split('\n'):
        ts = line.split()
        if not ts:
            continue
        n = int(ts[0])
        author = ts[-1]
        if author not in count:
            count[author] = [0, 0]
        count[author][0] += n

    results = [[k, nc, nf] for k, (nc, nf) in count.items()]
    results.sort(key=operator.itemgetter(1), reverse=True)

    # Get updated files per author.
    for r in results:
        cmd = 'git whatchanged --author="%s" --no-commit-id --name-only %s' % (r[0], path)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        out, err = proc.communicate()
        aset = set()
        for f in out.split('\n'):
            if not f:
                continue
            aset.add(f)
        r[2] = len(aset)

    print("%-50s %12s %10s" % ("Author", "# of commits", "# of files"))
    for k, nc, nf in results:
        print("%-50s %12d %10d" % (k, nc, nf))

    return 0


if __name__ == '__main__':
    sys.exit(main())
