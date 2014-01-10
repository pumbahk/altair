# -*- coding:utf-8 -*-
import os
import re
import unittest
from datetime import datetime
from pyramid import testing
from altair.app.ticketing.testing import _setup_db, _teardown_db

class SejApiTest(unittest.TestCase):
    api_key = 'XXX'

    def setUp(self):
        self.session = _setup_db([
            'altair.app.ticketing.core.models',
            'altair.app.ticketing.sej.models'
            ])

    def tearDown(self):
        testing.tearDown()
        _teardown_db()

    def last_notification(self):
        from ..models import SejNotification
        return self.session.query(SejNotification).order_by('created_at DESC').first()

    def _getTarget(self):
        from ..views import SejCallback 
        return SejCallback

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _parseResponse(self, resp):
        from altair.app.ticketing.utils import uniurldecode
        assert resp is not None
        m = re.match(ur'<SENBDATA>(.*?)</SENBDATA>', resp.body)
        assert m is not None
        return dict(uniurldecode(m.group(1), 'raw', 'CP932'))

    def _append_signature(self, params):
        from hashlib import md5
        params['xcode'] = md5(','.join([v for _, v in sorted(((k.lower(), v) for k, v in params.items() if k.startswith('X_')), lambda a, b: cmp(a[0], b[0]))] + [self.api_key])).hexdigest()

    def test_api_payment_complete(self):
        from ..models import SejPaymentType, SejNotificationType
        params = {
            'X_tuchi_type': str(SejNotificationType.PaymentComplete.v),
            'X_shori_id': '12345',
            'X_shop_id': '000000',
            'X_shori_kbn': str(SejPaymentType.Paid.v),
            'X_shop_order_id': '000000000000',
            'X_haraikomi_no': '000000000000',
            'X_hikikae_no': '000000000000',
            'X_goukei_kingaku': '1234',
            'X_ticket_cnt': '1',
            'X_ticket_hon_cnt': '1',
            'X_kaishu_cnt': '0',
            'X_pay_mise_no': '000000',
            'X_hakken_mise_no': '000000',
            'X_torikeshi_riyu': '',
            'X_shori_time': '20130101',
            'pay_mise_name': u'テスト店舗',
            'hakken_mise_name': u'テスト店舗'
            }
        self._append_signature(params)
        request = testing.DummyRequest(post=params)
        testing.setUp(request=request, settings={'altair.sej.api_key': self.api_key})
        target = self._makeOne(request)
        resp = self._parseResponse(target.callback())
        assert resp['status'] == '800'
        target = self.last_notification() 
        assert target.notification_type == str(SejNotificationType.PaymentComplete.v)
        assert target.process_number      == params['X_shori_id']
        assert target.payment_type        == params['X_shori_kbn']
        assert target.shop_id             == params['X_shop_id']
        assert target.order_no            == params['X_shop_order_id']
        assert target.billing_number      == params['X_haraikomi_no']
        assert target.exchange_number     == params['X_hikikae_no']
        assert float(target.total_price)  == float(params['X_goukei_kingaku'])
        assert target.total_ticket_count  == int(params['X_ticket_cnt'])
        assert target.ticket_count        == int(params['X_ticket_hon_cnt'])
        assert target.return_ticket_count == int(params['X_kaishu_cnt'])
        assert target.pay_store_number    == params['X_pay_mise_no']
        assert target.ticketing_store_number == params['X_hakken_mise_no']
        assert target.processed_at        == datetime(2013, 01, 01, 0, 0, 0)
        assert target.pay_store_name       == u'テスト店舗'
        assert target.ticketing_store_name == u'テスト店舗'

        testing.tearDown()
        request = testing.DummyRequest(post=params)
        testing.setUp(request=request, settings={'altair.sej.api_key': self.api_key})
        target = self._makeOne(request)
        resp = self._parseResponse(target.callback())

        assert resp['status'] == '810'
        target = self.last_notification() 
        assert target.notification_type == str(SejNotificationType.PaymentComplete.v)
        assert target.process_number      == params['X_shori_id']
        assert target.payment_type        == params['X_shori_kbn']
        assert target.shop_id             == params['X_shop_id']
        assert target.order_no            == params['X_shop_order_id']
        assert target.billing_number      == params['X_haraikomi_no']
        assert target.exchange_number     == params['X_hikikae_no']
        assert float(target.total_price)  == float(params['X_goukei_kingaku'])
        assert int(target.total_ticket_count) == int(params['X_ticket_cnt'])
        assert int(target.ticket_count)       == int(params['X_ticket_hon_cnt'])
        assert int(target.return_ticket_count) == int(params['X_kaishu_cnt'])
        assert target.pay_store_number    == params['X_pay_mise_no']
        assert target.ticketing_store_number == params['X_hakken_mise_no']
        assert target.processed_at        == datetime(2013, 01, 01, 0, 0, 0)
        assert target.pay_store_name       == u'テスト店舗'
        assert target.ticketing_store_name == u'テスト店舗'

    def test_api_payment_complete_2(self):
        '''入金発券完了通知'''
        from altair.app.ticketing.sej.models import SejOrder, SejTicket
        from altair.app.ticketing.sej.payment import SejOrderUpdateReason, SejPaymentType

        sejOrder = SejOrder()

        sejOrder.process_type          = SejOrderUpdateReason.Change.v
        sejOrder.billing_number        = u'00000001'
        sejOrder.ticket_count          = 1
        sejOrder.exchange_sheet_url    = u'https://www.r1test.com/order/hi.do'
        sejOrder.order_no              = u'orderid00001'
        sejOrder.exchange_sheet_number = u'11111111'
        sejOrder.exchange_number       = u'22222222'
        sejOrder.order_at              = datetime.now()

        self.session.add(sejOrder)

        params = {
            u'X_shori_id': u'000000036380',
            u'X_shop_id': u'30520',
            u'X_shop_order_id': u'120607191915',
            u'X_tuchi_type': u'01', # '01':入金発券完了通知 '31':SVC強制取消通知
            u'X_shori_kbn': u'%02d' % SejPaymentType.CashOnDelivery,
            u'X_haraikomi_no': u'2329873576572',
            u'X_hikikae_no': u'',
            u'X_goukei_kingaku': u'015000',
            u'X_ticket_cnt': u'01',
            u'X_ticket_hon_cnt': u'01',
            u'X_kaishu_cnt': u'00',
            u'X_pay_mise_no': u'000017',
            u'pay_mise_name': u'豊洲',
            u'X_hakken_mise_no':u'000017',
            u'hakken_mise_name': u'豊洲',
            u'X_torikeshi_riyu': u'',
            u'X_shori_time': u'20120607194231',
            }
        self._append_signature(params)

        request = testing.DummyRequest(post=params)
        testing.setUp(request=request, settings={'altair.sej.api_key': self.api_key})
        target = self._makeOne(request)
        response = target.callback().body

        assert response == '<SENBDATA>status=800&</SENBDATA><SENBDATA>DATA=END</SENBDATA>'
        from altair.app.ticketing.sej.models import SejNotification
        n = SejNotification.query.filter_by(order_no=u'120607191915', billing_number=u'2329873576572').one()

        assert n.process_number        == '000000036380'
        assert int(n.payment_type)     == SejPaymentType.CashOnDelivery.v

        assert n.notification_type     == u'1'
        assert n.billing_number        == u'2329873576572'
        assert n.exchange_number       == u''
        assert n.total_price           == 15000
        assert n.total_ticket_count    == 1
        assert n.ticket_count          == 1
        assert n.return_ticket_count   == 0
        assert n.pay_store_number      == u'000017'
        assert n.pay_store_name        == u'豊洲'
        assert n.ticketing_store_number== u'000017'
        assert n.ticketing_store_name  == u'豊洲'
        assert n.cancel_reason         == ''


        assert n.signature             == params['xcode']


    def test_api_ticketing_expire(self):
        from ..models import SejPaymentType, SejNotificationType
        params = {
            'X_tuchi_type': str(SejNotificationType.TicketingExpire.v),
            'X_shori_id': '12346',
            'X_shop_id': '000000',
            'X_shori_kbn': str(SejPaymentType.Paid.v),
            'X_lmt_time': '20120523',
            'X_shop_order_id': '000000000000',
            'X_haraikomi_no': '000000000000',
            'X_hikikae_no': '000000000000',
            'X_shori_time': '20130101',
            }
        self._append_signature(params)

        request = testing.DummyRequest(post=params)
        testing.setUp(request=request, settings={'altair.sej.api_key': self.api_key})
        target = self._makeOne(request)
        resp = self._parseResponse(target.callback())

        assert resp['status'] == '800'
        target = self.last_notification() 
        assert target.notification_type == str(SejNotificationType.TicketingExpire.v)
        assert target.process_number      == params['X_shori_id']
        assert target.payment_type        == params['X_shori_kbn']
        assert target.shop_id             == params['X_shop_id']
        assert target.order_no            == params['X_shop_order_id']
        assert target.ticketing_due_at    == datetime(2012, 5, 23, 0, 0, 0)
        assert target.billing_number      == params['X_haraikomi_no']
        assert target.exchange_number     == params['X_hikikae_no']
        assert target.processed_at        == datetime(2013, 1, 1, 0, 0, 0)


    def test_callback_svc_cancel_notification(self):
        '''SVCキャンセル'''
        from altair.app.ticketing.sej.models import SejOrder
        from altair.app.ticketing.sej.payment import SejOrderUpdateReason, SejPaymentType
        params = {
            'X_shori_id': u'000000036605',
            'X_shop_id': u'30520',
            'X_shop_order_id': u'000000000600',
            'X_tuchi_type': u'31', # '01':入金発券完了通知 '31':SVC強制取消通知
            'X_shori_kbn': u'%02d' % SejPaymentType.CashOnDelivery,
            'X_haraikomi_no': u'2343068205221',
            'X_hikikae_no': u'',
            'X_goukei_kingaku': u'005315',
            'X_ticket_cnt': u'01',
            'X_ticket_hon_cnt': u'01',
            'X_kaishu_cnt': u'00',
            'X_torikeshi_riyu': u'',
            'X_shori_time': u'20120612154447',
            }
        self._append_signature(params)

        request = testing.DummyRequest(post=params)
        testing.setUp(request=request, settings={'altair.sej.api_key': self.api_key})
        target = self._makeOne(request)
        response = target.callback().body

        assert response == '<SENBDATA>status=800&</SENBDATA><SENBDATA>DATA=END</SENBDATA>'
        from altair.app.ticketing.sej.models import SejNotification
        n = SejNotification.query.filter_by(order_no=u'000000000600', billing_number=u'2343068205221').one()

        assert n.process_number == u'000000036605'
        assert int(n.payment_type )         == SejPaymentType.CashOnDelivery.v
        assert n.notification_type     == u'31'
        assert n.billing_number        == u'2343068205221'
        assert n.exchange_number       == u''
        assert n.total_price           == 5315
        assert n.total_ticket_count    == 1
        assert n.ticket_count          == 1
        assert n.return_ticket_count   == 0
        assert n.cancel_reason         == ''
        assert n.signature             == params['xcode']

    def test_callback_expire_notification(self):
        from altair.app.ticketing.sej.models import SejOrder
        from altair.app.ticketing.sej.payment import SejOrderUpdateReason, SejPaymentType

        params = {
            u'X_shori_id':  u'000000036665',
            u'X_shop_id': u'30520',
            u'X_shop_order_id': u'000000000605',
            u'X_tuchi_type': u'72', # '01':入金発券完了通知 '31':SVC強制取消通知
            u'X_shori_kbn':  u'01',
            u'X_haraikomi_no': u'2374045665660',
            u'X_hikikae_no': u'',
            u'X_shori_kbn_new': u'01',
            u'X_haraikomi_no_new': u'2306374720345',
            u'X_hikikae_no_new': u'',
            u'X_lmt_time_new': u'201207092359',
            u'X_barcode_no_new_01': u'6200004532147',
            u'X_shori_time': u'20120613111810',
            }
        self._append_signature(params)

        request = testing.DummyRequest(post=params)
        testing.setUp(request=request, settings={'altair.sej.api_key': self.api_key})
        target = self._makeOne(request)
        response = target.callback().body

        assert response == '<SENBDATA>status=800&</SENBDATA><SENBDATA>DATA=END</SENBDATA>'
        from altair.app.ticketing.sej.models import SejNotification
        n = SejNotification.query.filter_by(order_no=u'000000000605', billing_number=u'2374045665660').one()

        assert n.process_number         == u'000000036665'
        assert n.shop_id                == u'30520'
        assert n.order_no               == u'000000000605'
        assert n.notification_type      == u'72'
        assert int(n.payment_type )     == SejPaymentType.CashOnDelivery.v
        assert n.billing_number         == u'2374045665660'
        assert n.exchange_number        == u''
        assert n.signature              == params['xcode']

