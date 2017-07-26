# -*- coding: utf-8 -*-

import unittest
import mock
from pyramid import testing
from altair.app.ticketing.testing import DummyRequest
from datetime import datetime, timedelta
from altair.app.ticketing.testing import _setup_db, _teardown_db
from altair.app.ticketing.core.models import TicketPrintHistory
from altair.app.ticketing.core.testing import CoreTestMixin
from altair.app.ticketing.qr.utils import QRTicketObject
from altair.app.ticketing.qr import get_qrdata_aes_builder
from . import (HT_QR_DATA_FREE,
               HT_QR_DATA_HEADER,
               HT_TYPE_CODE,
               HT_ID_CODE,
               HT_COUNT_FLAG,
               HT_SEASON_FLAG,
               HT_SPECIAL_FLAG,
               item_list as ht_item_list,
               encrypting_items as ht_encrypting_items)
from .qr_utilits import (build_ht_qr_by_order_no,
                         build_ht_qr_by_token_id,
                         build_ht_qr_by_order,
                         build_ht_qr_by_token,
                         build_ht_qr_by_ticket_id,
                         build_ht_qr_by_history,
                         make_data_for_qr)
from altair.app.ticketing.orders.models import Order, OrderedProduct, OrderedProductItem

class QRUtilsTest(unittest.TestCase, CoreTestMixin):

    def setUp(self):
        '''
        item_list = OrderedDict([
            ('id_code', 10),
            ('type_code', 1),
            ('ticket_code', 6),
            ('serial_no', 17),
            ('issued_at', 8),
            ('count_flag', 1),
            ('season_flag', 1),
            ('valid_date_from', 8),
            ('valid_date_to', 8),
            ('enterable_days', 3),
            ('enterable_from', 4),
            ('usable_date_to', 8),
            ('special_flag', 1)
        ])
        '''
        p_start_on = datetime(2017, 2, 1, 15, 0, 0)
        now = datetime.now()

        issued_at = p_start_on.strftime('%Y%m%d')
        usable_date_to = (now + timedelta(days=30)).strftime('%Y%m%d')
        self.origin_data = {
            'id_code': HT_ID_CODE,
            'type_code': HT_TYPE_CODE,
            'ticket_code': u'123456',
            'serial_no': u'A1234560000000001',
            'issued_at': issued_at,
            'count_flag': HT_COUNT_FLAG,
            'season_flag': HT_SEASON_FLAG,
            'valid_date_from': u'20170101',
            'valid_date_to': u'20201231',
            'enterable_from': u'1500',
            'enterable_days': u'000',
            'usable_date_to': usable_date_to,
            'special_flag': HT_SPECIAL_FLAG
        }
        self.content = HT_ID_CODE + HT_TYPE_CODE + '123456A1234560000000001{issued_at}1020170101202012310001500{usable_date_to}0'.format(issued_at=issued_at, usable_date_to=usable_date_to)
        self.header = HT_QR_DATA_FREE + HT_QR_DATA_HEADER

        self.session = _setup_db([
            'altair.app.ticketing.core.models',
            'altair.app.ticketing.orders.models',
        ])

        self.config = testing.setUp()
        self.config.include('altair.app.ticketing.qr')
        self.request = testing.DummyRequest()
        CoreTestMixin.setUp(self)
        self.performance.start_on=p_start_on
        self.performance.open_on=datetime.strptime(self.origin_data['valid_date_from'] + '0000', '%Y%m%d%H%M')
        self.performance.end_on = datetime.strptime(self.origin_data['valid_date_to'] + '2359', '%Y%m%d%H%M')
        self.stock_types = self._create_stock_types(1)
        self.stocks = self._create_stocks(self.stock_types)
        self.product = self._create_products(self.stocks)
        self.product[0].items[0].name = "XXX_{0}_{1}_{2}".format(self.origin_data['ticket_code'], self.origin_data['enterable_days'], str(30))

        self.order = self._create_order([(self.product[0], 1)], order_no='HT0000000000')
        self.order.created_at = now
        self.session.add(self.order)
        self.session.flush()
        item_token = self.order.items[0].elements[0].tokens[0]
        self.history = TicketPrintHistory(
            id=1,
            seat_id=None,
            item_token_id=item_token.id,
            ordered_product_item_id=None,
            order_id=self.order.id
        )
        self.session.add(self.history)
        self.session.flush()

    def tearDown(self):
        _teardown_db()

    def _extract_qr_data_for_test(self, ticket):
        builder = get_qrdata_aes_builder(self.request)
        qr = ticket.qr
        data = builder.extract(qr, self.header, ht_item_list)
        return data

    def test_make_data_for_qr(self):
        data, _ = make_data_for_qr(self.history)
        self.assertEquals(len(data['content']), 76)
        self.assertEquals(data['header'], HT_QR_DATA_FREE + HT_QR_DATA_HEADER)
        self.assertEquals(data['content'], self.content)

    def test_build_ht_qr_by_history(self):
        ticket = build_ht_qr_by_history(self.request, self.history)
        data = self._extract_qr_data_for_test(ticket)
        self.assertDictEqual(data, self.origin_data)

    def test_build_ht_qr_by_ticket_id(self):
        ticket = build_ht_qr_by_ticket_id(self.request, 1)
        data = self._extract_qr_data_for_test(ticket)
        self.assertDictEqual(data, self.origin_data)

    def test_build_ht_qr_by_token(self):
        item_token = self.order.items[0].elements[0].tokens[0]
        ticket = build_ht_qr_by_token(self.request, self.order.order_no, item_token)
        data = self._extract_qr_data_for_test(ticket)
        self.assertDictEqual(data, self.origin_data)