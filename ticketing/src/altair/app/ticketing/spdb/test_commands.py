# -*- coding:utf-8 -*-
from mock import MagicMock
from unittest import TestCase
from nose.tools import ok_, eq_
from .commands import chop_none, SQLCreater


class Args():
    def __init__(self):
        self.org = 15
        self.term_from = "2016/01/01"
        self.term_to = "2020/01/01"
        self.all = False
        self.delete = False


class SQLCreaterTestCase(TestCase):
    @staticmethod
    def test_sql():
        args = Args()
        sql = "select * from test"
        creater = SQLCreater(args, sql)
        eq_(creater.sql, "select * from test WHERE `Order`.organization_id = 15 AND `Order`.updated_at BETWEEN '2016-01-01 00:00:00' and '2020-01-02 00:00:00' AND `Order`.canceled_at IS NULL")


class AnotherTestCase(TestCase):
    @staticmethod
    def test_chop_none():
        row = {'aaa': None, 'bbb': '222', 'ccc': '333'}
        ret = chop_none(row)
        eq_(ret['aaa'], "")
        eq_(ret['bbb'], "222")
        eq_(ret['ccc'], "333")
