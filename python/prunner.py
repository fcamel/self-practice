# -*- encoding: utf8 -*-
'''
Parallel Runner: run your tasks in parallel.

See prunner_example.py to know how to use it.
'''

import logging
import multiprocessing
import os
import sys
import time


__author__ = 'fcamel'


class ScopeActive(object):
    def __init__(self, is_active):
        self._is_active = is_active

    def __enter__(self):
        self._is_active.value = 1

    def __exit__(self, type_, value, traceback):
        self._is_active.value = 0


class ScopeLock(object):
    def __init__(self, lock):
        self._lock = lock

    def __enter__(self):
        self._lock.acquire()

    def __exit__(self, type_, value, traceback):
        self._lock.release()


class Task(object):
    def __init__(self, label, data):
        self.label = label
        self.data = data


class ParallelTaskRunner(object):
    '''
    Override begin(), run(), end() to fit your need.

    You may need some helper objects:
    * self.queue: the task queue.
    * self.dict_: shared dict.
    * self.lock: when accessing self.dict_,
                 use self.lock to avoid race condition.
    * self.manager: create shared variables via self.manager when need.
      Ref. https://docs.python.org/2/library/multiprocessing.html#sharing-state-between-processes
    '''
    def __init__(self, n_process, debug, options):
        self._options = options
        self._debug = debug
        self._n_process = n_process
        if self._debug:
            multiprocessing.log_to_stderr(logging.INFO)

    def begin(self, options):
        pass

    def run(self, task):
        pass

    def end(self):
        pass

    def start(self):
        manager = multiprocessing.Manager()
        lock = manager.Lock()
        queue = manager.Queue()
        dict_ = manager.dict()

        # Set member fields first.
        self.manager = manager
        self.lock = lock
        self.queue = queue
        self.dict_ = dict_

        # Put initial value to queue.
        self.begin(self._options)

        # Start workers (they are both consumers and producers).
        processes = []
        active_flags = []
        for _ in xrange(self._n_process):
            is_active = manager.Value('i', 0)
            p = multiprocessing.Process(target=self.main, args=[is_active])
            try:
                p.start()
            except Exception, _:
                logging.exception('?')
                continue
            active_flags.append(is_active)
            processes.append(p)

        # Wait all workers to stop.
        while processes:
            for p in list(processes):
                if not p.is_alive():
                    processes.remove(p)
                    continue

                p.join(0.1)

                done, naw = self.is_done(active_flags, self.queue)
                msg = (
                    '> pid=%d: # of process=%d, # of active worker=%d, '
                    'queue.qsize=%d\n'
                    '' % (os.getpid(), len(processes), naw, queue.qsize())
                )
                sys.stderr.write(msg)

                if done:
                    # There is neither active worker nor data in queue.
                    # Notify all workers to stop.
                    for i in xrange(len(processes)):
                        queue.put(None)

        self.end()

    def main(self, is_active):
        while True:
            task = self.queue.get()
            if not task:
                break
            with ScopeActive(is_active):
                try:
                    self.run(task)
                except Exception, _:
                    logging.exception('?')

    @staticmethod
    def is_done(active_flags, queue):
        retry = 2
        while True:
            # Reading is_active is not async safe, but it's okay.
            naw = sum(is_active.value for is_active in active_flags)
            if naw > 0 or not queue.empty():
                return False, naw
            # When there is only one task in the queue, there may be a very
            # short period that there is also no worker. Wait a while
            # to ensure all tasks are really done.
            if retry > 0:
                retry -= 1
                time.sleep(0.1)
            else:
                break
        return True, 0
