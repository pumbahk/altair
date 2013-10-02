# -*- coding:utf-8 -*-

import unittest
from testfixtures import compare, ShouldRaise

class TestKeyBreak(unittest.TestCase):
    def test_it(self):
        from . import KeyBreak
        data = [
            dict(v1=1, v2=1, v3=1, v4=1),
            dict(v1=1, v2=1, v3=1, v4=1),
            dict(v1=1, v2=2, v3=1, v4=1),
            dict(v1=2, v2=2, v3=1, v4=1),
            dict(v1=3, v2=1, v3=1, v4=1),
        ]

        breaker = KeyBreak(keys=['v1', 'v2'])
        it = breaker(data)
        compare(it.next(), ({'v1': False, 'v2': False}, {'v1': 1, 'v2': 1, 'v3': 1, 'v4': 1}))
        compare(it.next(), ({'v1': False, 'v2': False}, {'v1': 1, 'v2': 1, 'v3': 1, 'v4': 1}))
        compare(it.next(), ({'v1': False, 'v2': True}, {'v1': 1, 'v2': 2, 'v3': 1, 'v4': 1}))
        compare(it.next(), ({'v1': True, 'v2': False}, {'v1': 2, 'v2': 2, 'v3': 1, 'v4': 1}))
        compare(it.next(), ({'v1': True, 'v2': True}, {'v1': 3, 'v2': 1, 'v3': 1, 'v4': 1}))

    def test_empty(self):
        from . import KeyBreak
        data = []

        breaker = KeyBreak(keys=['v1', 'v2'])
        it = breaker(data)
        with ShouldRaise(StopIteration):
            next(it)

class TestPredicatedYielder(unittest.TestCase):

    def test_it(self):
        from . import PredicatedYielder
        predicate = lambda d: d[0]

        data = [
            (False, 1),
            (False, 2),
            (True, 3),
            (False, 4),
            (True, 5),
        ]
        target = PredicatedYielder(predicate)

        result = list(target(data))

        compare(result, [(True, 3), (True, 5)])

class TestKeyBreakCounter(unittest.TestCase):

    def test_it(self):
        from . import KeyBreakCounter
        data = [
            dict(v1=1, v2=1, v3=1, v4=1),
            dict(v1=1, v2=1, v3=1, v4=1),
            dict(v1=1, v2=2, v3=1, v4=1),
            dict(v1=2, v2=2, v3=1, v4=1),
            dict(v1=3, v2=1, v3=1, v4=1),
        ]

        target = KeyBreakCounter(keys=['v1', 'v2'])

        result = list(target(data))

        compare(result, [({'v1': 0, 'v2': 0},
                          {'v1': False, 'v2': False},
                          {'v1': 1, 'v2': 1, 'v3': 1, 'v4': 1}),
                         ({'v1': 0, 'v2': 0},
                          {'v1': False, 'v2': False},
                          {'v1': 1, 'v2': 1, 'v3': 1, 'v4': 1}),
                         ({'v1': 0, 'v2': 1},
                          {'v1': False, 'v2': True},
                          {'v1': 1, 'v2': 2, 'v3': 1, 'v4': 1}),
                         ({'v1': 1, 'v2': 0},
                          {'v1': True, 'v2': False},
                          {'v1': 2, 'v2': 2, 'v3': 1, 'v4': 1}),
                         ({'v1': 2, 'v2': 0},
                          {'v1': True, 'v2': True},
                          {'v1': 3, 'v2': 1, 'v3': 1, 'v4': 1})]
            )
