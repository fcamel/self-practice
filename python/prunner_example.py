#!/usr/bin/env python
# -*- encoding: utf8 -*-

import optparse
import sys

import prunner


__author__ = 'fcamel'


TASK_INIT = 'task_init'
TASK_ADD_ONE = 'task_add_one'
TASK_DOUBLE = 'task_double'
TASK_SUM = 'task_sum'

class MyRunner(prunner.ParallelTaskRunner):
    def begin(self, options):
        self.dict_['sum'] = 0
        self.queue.put(prunner.Task(TASK_INIT, range(100)))

    def run(self, task):
        if task.label == TASK_INIT:
            for i in task.data:
                self.queue.put(prunner.Task(TASK_ADD_ONE, i))
            return

        if task.label == TASK_ADD_ONE:
            self.queue.put(prunner.Task(TASK_DOUBLE, task.data + 1))
            return

        if task.label == TASK_DOUBLE:
            self.queue.put(prunner.Task(TASK_SUM, task.data))
            self.queue.put(prunner.Task(TASK_SUM, task.data))
            return

        if task.label == TASK_SUM:
            with prunner.ScopeLock(self.lock):
                self.dict_['sum'] += task.data

    def end(self):
        print self.dict_['sum']


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

    runner = MyRunner(options.n_process, options.debug, options)
    runner.start()

    return 0


if __name__ == '__main__':
    sys.exit(main())
