# -*- coding:utf-8 -*-
from unittest import TestCase
from nose.tools import ok_, eq_
from .commands import chop_none


class AnotherTestCase(TestCase):
    @staticmethod
    def test_chop_none():
        row = {'aaa': None, 'bbb': '222', 'ccc': '333'}
        ret = chop_none(row)
        eq_(ret['aaa'], "")
        eq_(ret['bbb'], "222")
        eq_(ret['ccc'], "333")
