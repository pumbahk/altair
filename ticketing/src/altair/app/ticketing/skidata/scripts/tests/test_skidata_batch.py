#! /usr/bin/env python
# coding=utf-8
import string
import random
from unittest import TestCase
from datetime import datetime, timedelta
import mock
from pyramid.testing import DummyRequest, setUp, tearDown

from altair.app.ticketing import install_ld
from altair.app.ticketing.skidata.api import record_skidata_barcode_as_sent
from altair.app.ticketing.skidata.exceptions import SkidataSendWhitelistError
from altair.app.ticketing.skidata.scripts import send_whitelist_data_to_skidata as target_batch
from altair.app.ticketing.skidata.scripts.tests.test_helper import *
from altair.app.ticketing.testing import _setup_db, _teardown_db
from altair.sqlahelper import register_sessionmaker_with_engine
from altair.app.ticketing.skidata.models import SkidataBarcode, SkidataPropertyTypeEnum


def _send_to_batch(params):
    target_batch.send_whitelist_data_to_skidata(params)


def _random_string(string_length=5):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return "".join([random.choice(letters) for i in range(string_length)])


def _send_whitelist_to_skidata(skidata_session, whitelist, barcode_list, fail_silently=False):
    record_skidata_barcode_as_sent(barcode_list)


class SkidataSendWhitelistTest(TestCase):
    def setUp(self):
        settings = {
            'altair.skidata.webservice.timeout': '20',
            'altair.skidata.webservice.url': 'http://localhost/ImporterWebService',
            'altair.skidata.webservice.header.version': 'HSHIF25',
            'altair.skidata.webservice.header.issuer': '1',
            'altair.skidata.webservice.header.receiver': '1',
        }
        self.request = DummyRequest()
        self.config = setUp(request=self.request, settings=settings)
        self.session = _setup_db(
            modules=[
                'altair.app.ticketing.core.models',
                'altair.app.ticketing.orders.models',
                'altair.app.ticketing.skidata.models',
            ],
            hook=install_ld
        )

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

        sales_segment_group, sales_segment = create_sales_segment(session, organization, event, performance)

        product, product_item = create_product_info(session, performance, stock, sales_segment, u'大人席')

        venue = create_venue(session, organization, performance, u'仙台球場', u'宮城県')

        session.flush()
        create_skidata_property(session, organization, SkidataPropertyTypeEnum.SalesSegmentGroup.v,
                                sales_segment_group.id, u'通常購入', 0)
        name = u'大人'
        value = 0
        if random.randrange(0, 2, 1) == 1:
            name = u'子供'
            value = 1
        create_skidata_property(session, organization, SkidataPropertyTypeEnum.ProductItem.v,
                                product_item.id, name, value)
        # create order info.
        random_string = _random_string()
        now = datetime.now()
        stock_left = stock_count
        while stock_left > 0:
            order_seats = random.randrange(1, 11, 1)  # get random quantity from 1~10
            if order_seats > stock_left:
                order_seats = stock_left
            key = unicode(stock_left)
            order_no = code + random_string + key
            ordered_product_item = create_order_info(session, organization.id, performance, product,
                                                     product_item, order_no, datetime.now() - timedelta(days=1))
            for i in range(order_seats):
                num = unicode(i)
                seat_name = random_string + u' 広場 ' + key + num
                data = u'TS9JIJ' + random_string + key + num
                barcode = create_barcode_recorder(session, stock, venue, ordered_product_item, seat_name, data)
                if is_sent:
                    barcode.sent_at = now
            stock_left -= order_seats
        session.flush()

    def _assert_equal(self, except_count):
        barcode_objs = self.session.query(SkidataBarcode).filter(SkidataBarcode.sent_at.isnot(None)).all()
        self.assertEqual(except_count, len(barcode_objs))

    @mock.patch.object(target_batch, 'send_whitelist_to_skidata')
    @mock.patch.object(target_batch, 'bootstrap')
    def test_target_1_days_ahead_performance(self, mock_bootstrap, mock_send_whitelist_to_skidata):
        mock_bootstrap.return_value = {'registry': self.config.registry}
        mock_send_whitelist_to_skidata.side_effect = _send_whitelist_to_skidata
        # 指定した期間の公演の予約データがwhitelistとして送信され、送信時間が更新されること
        stock_count = 110
        offset = 1
        delta_days = 1
        self._make_test_data(u'RE', u'eagles', offset, stock_count, False)
        self._assert_equal(0)
        _send_to_batch(['', '-C', '/altair.ticketing.batch.ini', '--offset', str(offset), '--days', str(delta_days)])
        self._assert_equal(stock_count)

    @mock.patch.object(target_batch, 'send_whitelist_to_skidata')
    @mock.patch.object(target_batch, 'bootstrap')
    def test_target_3_days_ahead_performance(self, mock_bootstrap, mock_send_whitelist_to_skidata):
        mock_bootstrap.return_value = {'registry': self.config.registry}
        mock_send_whitelist_to_skidata.side_effect = _send_whitelist_to_skidata
        # 指定した期間の公演の予約データがwhitelistとして送信され、送信時間が更新されること
        stock_count = 100
        offset = 3
        delta_days = 1
        self._make_test_data(u'RE', u'eagles', offset, stock_count, False)
        self._assert_equal(0)
        _send_to_batch(['', '-C', '/altair.ticketing.batch.ini', '--offset', str(offset), '--days', str(delta_days)])
        self._assert_equal(stock_count)

    @mock.patch.object(target_batch, 'send_whitelist_to_skidata')
    @mock.patch.object(target_batch, 'bootstrap')
    def test_target_3_days_ahead_and_1or5_days(self, mock_bootstrap, mock_send_whitelist_to_skidata):
        mock_bootstrap.return_value = {'registry': self.config.registry}
        mock_send_whitelist_to_skidata.side_effect = _send_whitelist_to_skidata
        # 指定した期間外の公演の予約データがwhitelistとして送信されないこと
        stock_count = 120
        offset = 3
        delta_days = 1
        self._make_test_data(u'RE', u'eagles01', 1, 10, False)
        self._make_test_data(u'RE', u'eagles', offset, stock_count, False)
        self._make_test_data(u'RE', u'eagles02', 5, 20, False)
        self._assert_equal(0)
        _send_to_batch(['', '-C', '/altair.ticketing.batch.ini', '--offset', str(offset), '--days', str(delta_days)])
        self._assert_equal(stock_count)

    @mock.patch.object(target_batch, 'send_whitelist_to_skidata')
    @mock.patch.object(target_batch, 'bootstrap')
    def test_target_1_days_ahead_and_has_same_day_sent_data(self, mock_bootstrap, mock_send_whitelist_to_skidata):
        mock_bootstrap.return_value = {'registry': self.config.registry}
        mock_send_whitelist_to_skidata.side_effect = _send_whitelist_to_skidata
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

    @mock.patch.object(target_batch, 'send_whitelist_to_skidata')
    @mock.patch.object(target_batch, 'bootstrap')
    def test_target_3_days_ahead_and_has_other_day_sent_data(self, mock_bootstrap, mock_send_whitelist_to_skidata):
        mock_bootstrap.return_value = {'registry': self.config.registry}
        mock_send_whitelist_to_skidata.side_effect = _send_whitelist_to_skidata
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

    @mock.patch.object(target_batch, 'send_whitelist_to_skidata')
    @mock.patch.object(target_batch, 'bootstrap')
    def test_target_1_days_ahead_exception(self, mock_bootstrap, mock_send_whitelist_to_skidata):
        mock_bootstrap.return_value = {'registry': self.config.registry}

        def _send_whitelist_raise_exception(skidata_session, whitelist, barcode_list, fail_silently=False):
            if len(barcode_list) == 1000:
                raise SkidataSendWhitelistError(u'Failed to update barcode.')
            record_skidata_barcode_as_sent(barcode_list)
        mock_send_whitelist_to_skidata.side_effect = _send_whitelist_raise_exception
        # ある1000件のwhitelist送信に失敗しても残りのwhitelistは送信されて、最後まで処理されること
        stock_count = 2098
        offset = 1
        delta_days = 1
        self._make_test_data(u'RE', u'eagles', offset, stock_count, False)
        self._assert_equal(0)
        _send_to_batch(['', '-C', '/altair.ticketing.batch.ini', '--offset', str(offset), '--days', str(delta_days)])
        self._assert_equal(98)
