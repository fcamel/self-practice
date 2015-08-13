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


class ScopeCount(object):
    def __init__(self, lock, count):
        self._lock = lock
        self._count = count

    def __enter__(self):
        with ScopeLock(self._lock):
            self._count.value += 1

    def __exit__(self, type_, value, traceback):
        with ScopeLock(self._lock):
            self._count.value -= 1


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
        n_active_worker = manager.Value('i', 0)

        # Set member fields first.
        self.manager = manager
        self.lock = lock
        self.queue = queue
        self.dict_ = dict_
        self.n_active_worker = n_active_worker

        # Put initial value to queue.
        self.begin(self._options)

        # Start workers (they are both consumers and producers).
        processes = []
        for _ in xrange(self._n_process):
            args = (
                manager,
                lock,
                queue,
                dict_,
                n_active_worker,
            )
            p = multiprocessing.Process(target=self.main, args=args)
            try:
                p.start()
            except Exception, _:
                logging.exception('?')
                continue
            processes.append(p)

        # Wait all workers to stop.
        while processes:
            for p in list(processes):
                if not p.is_alive():
                    processes.remove(p)
                    continue

                with ScopeLock(lock):
                    naw = n_active_worker.value
                msg = (
                    '> pid=%d: # of process=%d, # of active worker=%d, '
                    'queue.qsize=%d\n'
                    '' % (os.getpid(), len(processes),
                          naw, queue.qsize())
                )
                sys.stderr.write(msg)
                p.join(0.1)

                with ScopeLock(lock):
                    if (n_active_worker.value <= 0 and queue.empty()):
                        # When there is only one task in the queue,
                        # there is a very short period that there is also
                        # no worker. Wait a while to ensure all tasks
                        # are really done.
                        time.sleep(0.1)
                        if (n_active_worker.value <= 0 and queue.empty()):
                            # There is neither active worker nor data in queue.
                            # Notify all workers to stop.
                            for i in xrange(len(processes)):
                                queue.put(None)

        self.end()

    def main(self, manager, lock, queue, dict_, n_active_worker):
        self.manager = manager
        self.lock = lock
        self.queue = queue
        self.dict_ = dict_

        while True:
            task = queue.get()
            if not task:
                break
            with ScopeCount(lock, n_active_worker):
                try:
                    self.run(task)
                except Exception, _:
                    logging.exception('?')
