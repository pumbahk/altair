# -*- coding:utf-8 -*-
import unittest
from datetime import datetime
import os
from pyramid import testing
from altair.app.ticketing.testing import _setup_db, _teardown_db

class SejApiTest(unittest.TestCase):
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

    def test_callback_notification(self):
        from altair.app.ticketing.utils import uniurldecode
        from ..api import callback_notification
        from ..resources import SejPaymentType, SejNotificationType
        from hashlib import md5
        import re
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
        digest = md5(','.join([v for _, v in sorted(((k.lower(), v) for k, v in params.items() if k.startswith('X_')), lambda a, b: cmp(a[0], b[0]))] + ['XXX'])).hexdigest()
        params['xcode'] = digest

        _resp = re.match(ur'<SENBDATA>(.*?)</SENBDATA>', callback_notification(params, 'XXX'))
        assert _resp is not None
        resp = dict(uniurldecode(_resp.group(1), 'raw', 'CP932'))
        assert resp['status'] == '800'
        target = self.last_notification() 
        assert target.notification_type == str(SejNotificationType.PaymentComplete.v)
        assert target.process_number      == params['X_shori_id']
        assert target.payment_type        == params['X_shori_kbn']
        assert target.shop_id             == params['X_shop_id']
        assert target.order_id            == params['X_shop_order_id']
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

        _resp = re.match(ur'<SENBDATA>(.*?)</SENBDATA>', callback_notification(params, 'XXX'))
        assert _resp is not None
        resp = dict(uniurldecode(_resp.group(1), 'raw', 'CP932'))
        assert resp['status'] == '810'
        target = self.last_notification() 
        assert target.notification_type == str(SejNotificationType.PaymentComplete.v)
        assert target.process_number      == params['X_shori_id']
        assert target.payment_type        == params['X_shori_kbn']
        assert target.shop_id             == params['X_shop_id']
        assert target.order_id            == params['X_shop_order_id']
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
        digest = md5(','.join([v for _, v in sorted(((k.lower(), v) for k, v in params.items() if k.startswith('X_')), lambda a, b: cmp(a[0], b[0]))] + ['XXX'])).hexdigest()
        params['xcode'] = digest

        _resp = re.match(ur'<SENBDATA>(.*?)</SENBDATA>', callback_notification(params, 'XXX'))
        assert _resp is not None
        resp = dict(uniurldecode(_resp.group(1), 'raw', 'CP932'))
        assert resp['status'] == '800'
        target = self.last_notification() 
        assert target.notification_type == str(SejNotificationType.TicketingExpire.v)
        assert target.process_number      == params['X_shori_id']
        assert target.payment_type        == params['X_shori_kbn']
        assert target.shop_id             == params['X_shop_id']
        assert target.order_id            == params['X_shop_order_id']
        assert target.ticketing_due_at    == datetime(2012, 5, 23, 0, 0, 0)
        assert target.billing_number      == params['X_haraikomi_no']
        assert target.exchange_number     == params['X_hikikae_no']
        assert target.processed_at        == datetime(2013, 1, 1, 0, 0, 0)

