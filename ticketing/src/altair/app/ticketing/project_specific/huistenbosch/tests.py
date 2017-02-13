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
from . import (HT_QR_DATA_HEADER,
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
        issued_at = datetime.now().strftime('%Y%m%d')
        usable_date_to = (datetime.now() + timedelta(days=90)).strftime('%Y%m%d')
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
            'enterable_from': u'1000',
            'enterable_days': u'000',
            'usable_date_to': usable_date_to,
            'special_flag': HT_SPECIAL_FLAG
        }
        self.content = 'HTB00000011123456A1234560000000001{issued_at}1120170101202012310001000{usable_date_to}0'.format(issued_at=issued_at, usable_date_to=usable_date_to)
        self.header = 'http://www.shop-huistenbosch.jp/1'

        self.session = _setup_db([
            'altair.app.ticketing.core.models',
            'altair.app.ticketing.orders.models',
        ])

        self.config = testing.setUp()
        self.config.include('altair.app.ticketing.qr')
        CoreTestMixin.setUp(self)
        self.performance.start_on=datetime(2017, 2, 1, 15, 0, 0)
        self.performance.open_on=datetime.strptime(self.origin_data['valid_date_from'] + self.origin_data['enterable_from'], '%Y%m%d%H%M')
        self.performance.end_on = datetime.strptime(self.origin_data['valid_date_to'] + '2359', '%Y%m%d%H%M')
        self.stock_types = self._create_stock_types(1)
        self.stocks = self._create_stocks(self.stock_types)
        self.product = self._create_products(self.stocks)
        self.product[0].items[0].name = "XXX_{0}_{1}".format(self.origin_data['ticket_code'], self.origin_data['enterable_days'])

        self.order = self._create_order([(self.product[0], 1)], order_no='HT0000000000')

        self.session.add(self.order)
        self.session.flush()
        item_token = self.order.items[0].elements[0].tokens[0]
        self.history = TicketPrintHistory(
            id=1,
            seat_id=None,
            item_token_id=item_token.id,
            ordered_product_item_id=999,
            order_id=self.order.id
        )
        self.session.add(self.history)
        self.session.flush()

    def tearDown(self):
        _teardown_db()

    def test_make_data_for_qr(self):
        data, _ = make_data_for_qr(self.history)
        self.assertEquals(len(data['content']), 76)
        self.assertEquals(data['header'], HT_QR_DATA_HEADER)
        self.assertEquals(data['content'], self.content)

    def test_build_ht_qr_by_history(self):
        request = testing.DummyRequest()
        ticket = build_ht_qr_by_ticket_id(request, 1)
        builder = get_qrdata_aes_builder(request)
        qr = ticket.qr
        data = builder.extract(qr, HT_QR_DATA_HEADER, ht_item_list)

        self.assertDictEqual(data, self.origin_data)

'HTB00000011123456A1234560000000001201702131120170101202012310001000201705140'
'HTB00000011123456A1234560000000001201702131120170101202012310001000201705100'