#!/usr/bin/env python
# -*- encoding: utf8 -*-

'''
The script calculates sum((i + 1) * 2) in a stupid way.
Just an example to show how to use ParallelTaskRunner directly.
'''

import prunner

TASK_INIT = 'task_init'
TASK_ADD_ONE = 'task_add_one'
TASK_DOUBLE = 'task_double'
TASK_SUM = 'task_sum'

class MyRunner(prunner.ParallelTaskRunner):
    def begin(self, options):
        self.dict_['sum'] = 0
        self.queue.put(prunner.Task(TASK_INIT, range(2000)))

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


runner = MyRunner(10, False, None)
runner.start()
