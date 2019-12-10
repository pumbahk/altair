#! /usr/bin/env python
# coding=utf-8
from random import randrange
from unittest import TestCase
from datetime import datetime, timedelta
import mock
import sqlahelper
from sqlalchemy.engine.base import Connection, Engine
from pyramid.testing import DummyRequest, setUp, tearDown

from altair.app.ticketing.skidata.scripts import send_white_list_data_to_skidata as target_batch
from altair.app.ticketing.skidata.scripts.tests.test_helper import *
from altair.app.ticketing.testing import _setup_db, _teardown_db
from altair.sqlahelper import register_sessionmaker_with_engine


class TestEngine(object):
    def __init__(self):
        self.engine = sqlahelper.get_engine()

    def connect(self, **kwargs):
        return MockConnection(engine=self.engine)


class MockConnection(Connection):
    def scalar(self, object, *multiparams, **params):
        # Return 1 because a query `select get_lock` is incompatible with sqlite
        if isinstance(object, str) and object.lower().startswith('select get_lock'):
            return 1
        return super(MockConnection, self).scalar(object, *multiparams, **params)


def _send_to_batch(params):
    target_batch.send_white_list_data_to_skidata(params)


class SkidataSendWhitelistTest(TestCase):
    def setUp(self):
        self.request = DummyRequest()
        self.config = setUp(request=self.request)
        self.session = _setup_db(
            modules=[
                'altair.app.ticketing.core.models',
                'altair.app.ticketing.orders.models',
                'altair.app.ticketing.skidata.models',
            ])

        register_sessionmaker_with_engine(
            self.config.registry,
            'slave',
            self.session.bind
        )

    def tearDown(self):
        _teardown_db()
        tearDown()

    def _make_test_data(self, code, short_name, offset, stock_count, is_sent):
        session = self.session
        # create performance info.
        organization = create_organization(session, code, short_name, True)

        event = create_event(session, organization, u'2020年 プロ野球公式戦', True)

        target_date = datetime.now() + timedelta(days=offset)
        performance = create_performance(session, event, u'楽天イーグルス vs 北海道日本ハムファイターズ', target_date, target_date)

        stock = create_stock(session, event, performance, u'指定席')

        sales_segment = create_sales_segment(session, organization, event, performance)

        product, product_item = create_product_info(session, performance, stock, sales_segment, u'大人席')

        venue = create_venue(session, organization, performance, u'仙台球場', u'宮城県')
        session.flush()

        # create order info.
        now = datetime.now()
        stock_left = stock_count
        while stock_left > 0:
            order_seats = randrange(1, 11, 1)  # get random quantity from 1~10
            if order_seats > stock_left:
                order_seats = stock_left
            key = unicode(stock_left)
            order_no = code + short_name + key
            ordered_product_item = create_order_info(session, organization.id, performance, product,
                                                     product_item, order_no, datetime.now() - timedelta(days=1))
            for i in range(order_seats):
                num = unicode(i)
                seat_name = short_name + u' 広場 ' + key + num
                data = u'TS9JIJ' + short_name + key + num
                skidata_barcode = create_barcode_recorder(session, stock, venue, ordered_product_item, seat_name, data)
                if is_sent:
                    skidata_barcode.sent_at = now
            stock_left -= order_seats
        session.flush()

    def _assert_equal(self, except_count):
        barcode_objs = self.session.query(SkidataBarcode).filter(SkidataBarcode.sent_at.isnot(None)).all()
        self.assertEqual(except_count, len(barcode_objs))

    @mock.patch.object(target_batch, 'bootstrap')
    @mock.patch.object(target_batch, 'sqlahelper')
    def test_target_1_days_ahead_performance(self, mock_sqlahelper, mock_bootstrap):
        mock_sqlahelper.get_engine.return_value = TestEngine()
        mock_bootstrap.return_value = {'registry': self.config.registry}
        # 指定した期間の公演の予約データがwhitelistとして送信され、送信時間が更新されること
        stock_count = 110
        offset = 1
        delta_days = 1
        self._make_test_data(u'RE', u'eagles', offset, stock_count, False)
        self._assert_equal(0)
        _send_to_batch(['', '-C', '/altair.ticketing.batch.ini', '--offset', str(offset), '--days', str(delta_days)])
        self._assert_equal(stock_count)

    @mock.patch.object(target_batch, 'bootstrap')
    @mock.patch.object(target_batch, 'sqlahelper')
    def test_target_3_days_ahead_performance(self, mock_sqlahelper, mock_bootstrap):
        mock_sqlahelper.get_engine.return_value = TestEngine()
        mock_bootstrap.return_value = {'registry': self.config.registry}
        # 指定した期間の公演の予約データがwhitelistとして送信され、送信時間が更新されること
        stock_count = 100
        offset = 3
        delta_days = 1
        self._make_test_data(u'RE', u'eagles', offset, stock_count, False)
        self._assert_equal(0)
        _send_to_batch(['', '-C', '/altair.ticketing.batch.ini', '--offset', str(offset), '--days', str(delta_days)])
        self._assert_equal(stock_count)

    @mock.patch.object(target_batch, 'bootstrap')
    @mock.patch.object(target_batch, 'sqlahelper')
    def test_target_3_days_ahead_and_1or5_days(self, mock_sqlahelper, mock_bootstrap):
        mock_sqlahelper.get_engine.return_value = TestEngine()
        mock_bootstrap.return_value = {'registry': self.config.registry}
        # 指定した期間外の公演の予約データがwhitelistとして送信されないこと
        stock_count = 120
        offset = 3
        delta_days = 1
        self._make_test_data(u'RE', u'eagles01', 1, 10, False)
        self._make_test_data(u'RE', u'eagles', offset, stock_count, False)
        self._make_test_data(u'RE', u'eagles01', 5, 20, False)
        self._assert_equal(0)
        _send_to_batch(['', '-C', '/altair.ticketing.batch.ini', '--offset', str(offset), '--days', str(delta_days)])
        self._assert_equal(stock_count)

    @mock.patch.object(target_batch, 'bootstrap')
    @mock.patch.object(target_batch, 'sqlahelper')
    def test_target_1_days_ahead_and_has_same_day_sent_data(self, mock_sqlahelper, mock_bootstrap):
        mock_sqlahelper.get_engine.return_value = TestEngine()
        mock_bootstrap.return_value = {'registry': self.config.registry}
        # 送信済みの予約データは再度送信されないこと
        stock_count = 130
        sent_count = 20
        offset = 1
        delta_days = 1
        self._make_test_data(u'RE', u'eagles', offset, stock_count, False)
        self._make_test_data(u'RE', u'eagles01', offset, sent_count, True)
        self._assert_equal(sent_count)
        _send_to_batch(['', '-C', '/altair.ticketing.batch.ini', '--offset', str(offset), '--days', str(delta_days)])
        self._assert_equal(stock_count + sent_count)

    @mock.patch.object(target_batch, 'bootstrap')
    @mock.patch.object(target_batch, 'sqlahelper')
    def test_target_3_days_ahead_and_has_other_day_sent_data(self, mock_sqlahelper, mock_bootstrap):
        mock_sqlahelper.get_engine.return_value = TestEngine()
        mock_bootstrap.return_value = {'registry': self.config.registry}
        # 送信済みの予約データは再度送信されないこと
        stock_count = 130
        sent_count = 20
        offset = 3
        delta_days = 1
        self._make_test_data(u'RE', u'eagles', offset, stock_count, False)
        self._make_test_data(u'RE', u'eagles01', 1, sent_count, True)
        self._assert_equal(sent_count)
        _send_to_batch(['', '-C', '/altair.ticketing.batch.ini', '--offset', str(offset), '--days', str(delta_days)])
        self._assert_equal(stock_count + sent_count)
