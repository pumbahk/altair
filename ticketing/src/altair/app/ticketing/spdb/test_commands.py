# -*- coding:utf-8 -*-
from mock import MagicMock
from unittest import TestCase
from nose.tools import ok_, eq_
from .commands import chop_none, SQLCreater


class SQLCreaterTestCase(TestCase):
    @staticmethod
    def test_sql(self):
        args = MagicMock(org=15, term_from="2016/01/01", term_to="2030/01/01")
        sql = "select * from test"
        creater = SQLCreater(args, sql)
        creater.sql
        print "test"


class AnotherTestCase(TestCase):
    @staticmethod
    def test_chop_none():
        row = {'aaa': None, 'bbb': '222', 'ccc': '333'}
        ret = chop_none(row)
        eq_(ret['aaa'], "")
        eq_(ret['bbb'], "222")
        eq_(ret['ccc'], "333")
