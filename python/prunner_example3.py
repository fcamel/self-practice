#!/usr/bin/env python
# -*- encoding: utf8 -*-

'''
The script calculates sum((i + 1) * 2) in a stupid way.
Just an example to show how to use prunner's high level API.

This is easier to use but run a little slower because it serializes MyRunner
many times implicitly.
'''

import optparse
import sys

import prunner


__author__ = 'fcamel'


class MyRunner(object):
    def __init__(self, options):
        self._options = options

    def begin(self):
        prunner.get_dict()['sum'] = 0
        prunner.post_task(self.init, range(2000))

    def init(self, numbers):
        for i in numbers:
            prunner.post_task(self.add_one, i)

    def add_one(self, n):
        prunner.post_task(self.double, n + 1)

    def double(self, n):
        prunner.post_task(self.sum_up, n)
        prunner.post_task(self.sum_up, n)

    def sum_up(self, n):
        with prunner.global_lock():
            prunner.get_dict()['sum'] += n

    def end(self):
        print prunner.get_dict()['sum']


def main():
    '''\
    %prog [options]
    '''
    parser = optparse.OptionParser(usage=main.__doc__)
    parser.add_option('-n', '--nprocess', dest='n_process', type=int,
                      help='# of process (default: 10).', default=10)
    parser.add_option('-d', '--debug', dest='debug',
                      action='store_true', default=False,
                      help='Enable debug mode (default: False).')
    options, args = parser.parse_args()

    if len(args) != 0:
        parser.print_help()
        return 1

    runner = MyRunner(options)
    prunner.init(options.n_process, options.debug, runner.begin, runner.end)
    prunner.start()

    return 0


if __name__ == '__main__':
    sys.exit(main())
