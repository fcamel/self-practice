#!/usr/bin/env python
# -*- encoding: utf8 -*-

'''
The script calculates sum((i + 1) * 2) in a stupid way.
Just an example to show how to use prunner's high level API.

This is easier to use and as fast as prunner_example.py.
'''
import prunner

def begin():
    prunner.get_dict()['sum'] = 0
    prunner.post_task(init, range(2000))

def init(numbers):
    for i in numbers:
        prunner.post_task(add_one, i)

def add_one(n):
    prunner.post_task(double, n + 1)

def double(n):
    prunner.post_task(sum_up, n)
    prunner.post_task(sum_up, n)

def sum_up(n):
    with prunner.global_lock():
        prunner.get_dict()['sum'] += n

def end():
    print prunner.get_dict()['sum']

prunner.init(10, False, begin, end)
prunner.start()
