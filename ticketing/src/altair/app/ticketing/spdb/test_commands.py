# -*- coding:utf-8 -*-
from unittest import TestCase
from nose.tools import ok_, eq_
from .commands import chop_none, SQLCreater, SpdbInfo, FileOperator
from pyramid.testing import DummyModel
import argparse
from datetime import datetime, timedelta

class SQLCreaterTestCase(TestCase):
    """
        期間指定
        何も指定されなかったら、昨日1日分を取得する。
        fromだけ指定されたら、その日1日分を取得する。
        toが指定されたら、toで指定された日、1日分も取得する。
        ex) -f 2016/12/1 -t 2016/12/5の場合、2016/12/1 00:00:00 - 2016/12/6 00:00:00
    """
    # 何も指定されなかったら昨日１日分
    @staticmethod
    def test_sql1():
        args = DummyModel(org=15, all=False, delete=False, term_from="", term_to="")
        sql = "select * from test"
        creater = SQLCreater(args, sql)
        term_from = datetime.strptime(datetime.now().date().strftime('%Y/%m/%d'), '%Y/%m/%d') - timedelta(days=1)
        term_to = datetime.strptime(datetime.now().date().strftime('%Y/%m/%d'), '%Y/%m/%d')
        eq_(creater.sql, "select * from test WHERE `Order`.organization_id = 15 AND `Order`.updated_at BETWEEN '{0}' and '{1}' AND `Order`.canceled_at IS NULL".format(term_from, term_to))

    # fromだけ指定されたら、その日1日分を取得する。
    @staticmethod
    def test_sql2():
        args = DummyModel(org=15, all="", delete=False, term_from="2017/3/29", term_to="")
        sql = "select * from test"
        creater = SQLCreater(args, sql)
        term_from = datetime.strptime(datetime.now().date().strftime('%Y/%m/%d'), '%Y/%m/%d') - timedelta(days=1)
        term_to = datetime.strptime(datetime.now().date().strftime('%Y/%m/%d'), '%Y/%m/%d')
        eq_(creater.sql, "select * from test WHERE `Order`.organization_id = 15 AND `Order`.updated_at BETWEEN '2017-03-29 00:00:00' and '2017-03-30 00:00:00' AND `Order`.canceled_at IS NULL".format(term_from, term_to))

    @staticmethod
    def test_sql3():
        args = DummyModel(org=15, term_from="2016/01/01", term_to="2020/01/01", all=False, delete=False)
        sql = "select * from test"
        creater = SQLCreater(args, sql)
        eq_(creater.sql, "select * from test WHERE `Order`.organization_id = 15 AND `Order`.updated_at BETWEEN '2016-01-01 00:00:00' and '2020-01-02 00:00:00' AND `Order`.canceled_at IS NULL")

    @staticmethod
    def test_sql4():
        args = DummyModel(org="15", term_from="", term_to="", all=True, delete=True)
        sql = "select * from test"
        creater = SQLCreater(args, sql)
        eq_(creater.sql, "select * from test WHERE `Order`.organization_id = 15 AND `Order`.canceled_at IS NOT NULL")

    @staticmethod
    def test_sql5():
        args = DummyModel(org="")
        sql = "select * from test"
        creater = SQLCreater(args, sql)
        eq_(creater.sql, "")


class AnotherTestCase(TestCase):
    @staticmethod
    def test_chop_none():
        row = {'aaa': None, 'bbb': '222', 'ccc': '333'}
        ret = chop_none(row)
        eq_(ret['aaa'], "")
        eq_(ret['bbb'], "222")
        eq_(ret['ccc'], "333")
