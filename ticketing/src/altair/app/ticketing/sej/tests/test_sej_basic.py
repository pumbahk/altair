# -*- coding:utf-8 -*-
import unittest
import datetime
from pyramid import testing
import cgi
import os
from altair.app.ticketing.testing import _setup_db, _teardown_db
import time

class SejTest(unittest.TestCase):
    def _makeServer(self, *args, **kwargs):
        from webapi import DummyServer
        self.server = DummyServer(*args, **kwargs)
        self.server.start()
        return self.server

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('altair.app.ticketing.sej.communicator')
        self.session = _setup_db([
            'altair.app.ticketing.core.models',
            'altair.app.ticketing.orders.models',
            'altair.app.ticketing.lots.models',
            'altair.app.ticketing.sej.models'
            ])
        self.server = None
        from ..models import ThinSejTenant, _session
        _session.remove()
        self.tenant = ThinSejTenant(
            shop_id=u'30520',
            shop_name=u'楽天チケット',
            contact_01=u'contact',
            contact_02=u'連絡先2',
            inticket_api_url=u"http://127.0.0.1:38001",
            api_key=u'E6PuZ7Vhe7nWraFW',   
            )

    def tearDown(self):
        if self.server is not None:
            self.server.stop()
        testing.tearDown()
        _teardown_db()

    def test_request_order_cancel(self):
        import webob.util
        import sqlahelper
        from altair.app.ticketing.sej.models import SejOrder, SejTicket
        from altair.app.ticketing.sej.payment import request_cancel_order
        webob.util.status_reasons[800] = 'OK'

        target = self._makeServer(lambda environ: '<SENBDATA>DATA=END</SENBDATA>', host='127.0.0.1', port=38001, status=800)

        sej_order = SejOrder(
            billing_number        = u'00000001',
            exchange_number       = u'00001111',
            ticket_count          = 1,
            exchange_sheet_url    = u'https://inticket.nrir1test.jp/order/hi.do',
            order_no              = u'orderid00001',
            exchange_sheet_number = u'11111111',
            order_at              = datetime.datetime.now()
            )

        request_cancel_order(
            self.config.registry,
            tenant=self.tenant,
            sej_order=sej_order
            )

        self.server.poll()

        self.assertEqual(self.server.request.body, 'X_shop_id=30520&xcode=cf0fe9fc34300dd1f946e6c9c33fc020&X_hikikae_no=00001111&X_haraikomi_no=00000001&X_shop_order_id=orderid00001')
        self.assertEqual(self.server.request.method, 'POST')
        self.assertEqual(self.server.request.url, 'http://127.0.0.1:38001/order/cancelorder.do')

        assert sej_order.cancel_at is not None

    def test_request_order_cancel_fail(self):
        import webob.util
        import sqlahelper
        from altair.app.ticketing.sej.exceptions import SejError
        from altair.app.ticketing.sej.models import SejOrder, SejTicket
        from altair.app.ticketing.sej.payment import request_cancel_order
        webob.util.status_reasons[800] = 'OK'

        target = self._makeServer(lambda environ: '<SENBDATA>Error_Type=38&Error_Msg=Already Paid&Error_Field=X_shop_id,X_shop_order_id,X_ticket_hon_cnt&</SENBDATA><SENBDATA>DATA=END</SENBDATA>', host='127.0.0.1', port=38001, status=800)

        sej_order = SejOrder(
            billing_number        = u'00000001',
            exchange_number       = u'00001111',
            ticket_count          = 1,
            exchange_sheet_url    = u'https://inticket.nrir1test.jp/order/hi.do',
            order_no              = u'orderid00001',
            exchange_sheet_number = u'11111111',
            order_at              = datetime.datetime.now()
            )

        with self.assertRaises(SejError) as e:
            request_cancel_order(
                self.config.registry,
                tenant=self.tenant,
                sej_order=sej_order
                )

        self.server.poll()

        self.assertEqual(self.server.request.body, 'X_shop_id=30520&xcode=cf0fe9fc34300dd1f946e6c9c33fc020&X_hikikae_no=00001111&X_haraikomi_no=00000001&X_shop_order_id=orderid00001')
        self.assertEqual(self.server.request.method, 'POST')
        self.assertEqual(self.server.request.url, 'http://127.0.0.1:38001/order/cancelorder.do')
        self.assertEqual(e.exception.error_type, 38)
        self.assertEqual(e.exception.error_msg, 'Already Paid')
        self.assertEqual(e.exception.error_field, 'X_shop_id,X_shop_order_id,X_ticket_hon_cnt')
        self.assertEqual(sej_order.error_type, 38)
        self.assertIsNone(sej_order.cancel_at)

    def test_request_order_cash_on_delivery(self):
        '''2-1.決済要求 代引き'''
        from altair.app.ticketing.sej.api import create_sej_order
        from altair.app.ticketing.sej.models import SejOrder, SejTicket
        from altair.app.ticketing.sej.payment import SejPaymentType, SejTicketType, request_order
        from altair.app.ticketing.sej.payload import build_sej_datetime_without_second

        import webob.util

        sej_sample_response\
            = '<SENBDATA>' + \
                'X_shop_order_id=%(order_no)s&'+ \
                'X_haraikomi_no=%(haraikomi_no)s&' + \
                'X_url_info=https://inticket.nrir1test.jp/order/hi.do&' +\
                'iraihyo_id_00=%(iraihyo_id_00)s&' + \
                'X_ticket_cnt=%(ticket_total_num)02d&' + \
                'X_ticket_hon_cnt=%(ticket_num)02d&' + \
                'X_barcode_no_01=00001&' + \
                'X_barcode_no_02=00002&' + \
                'X_barcode_no_03=00003&' + \
              '</SENBDATA>' + \
              '<SENBDATA>DATA=END</SENBDATA>'

        def sej_dummy_response(environ):
            return sej_sample_response % dict(
                order_no         = 'orderid00001',
                haraikomi_no     = '0000000001',
                iraihyo_id_00    = '11111111',
                ticket_total_num = 3,
                ticket_num       = 2,
            )

        webob.util.status_reasons[800] = 'OK'
        target = self._makeServer(sej_dummy_response, host='127.0.0.1', port=38001, status=800)

        sej_order = create_sej_order(
            self.config.registry,
            order_no=u"orderid00001",
            user_name=u"お客様氏名",
            user_name_kana=u'コイズミモリヨシ',
            tel=u'0312341234',
            zip_code=u'1070062',
            email=u'dev@ticketstar.jp',
            total_price=15000,
            ticket_price=13000,
            commission_fee=1000,
            ticketing_fee=1000,
            payment_type=SejPaymentType.CashOnDelivery,
            payment_due_at=datetime.datetime(2012,7,30,7,00), #u'201207300700',
            regrant_number_due_at=datetime.datetime(2012,7,30,7,00), # u'201207300700',
            tickets=[
                dict(
                    ticket_type         = SejTicketType.TicketWithBarcode,
                    event_name          = u'イベント名1',
                    performance_name    = u'パフォーマンス名',
                    ticket_template_id  = u'TTTS000001',
                    performance_datetime= datetime.datetime(2012,8,31,18,00),
                    xml = '''<TICKET>
                      <TEST1>test&#x20;test</TEST1>
                      <TEST2><![CDATA[TEST [] >M>J TEST@&nbsp;]]></TEST2>
                      <TEST3>&#x3000;</TEST3>
                      <FIXTAG01></FIXTAG01>
                      <FIXTAG02></FIXTAG02>
                      <FIXTAG03></FIXTAG03>
                      <FIXTAG04></FIXTAG04>
                      <FIXTAG05></FIXTAG05>
                      <FIXTAG06></FIXTAG06>
                    </TICKET>'''
                ),

                dict(
                    ticket_type         = SejTicketType.TicketWithBarcode,
                    event_name          = u'イベント名2',
                    performance_name    = u'パフォーマンス名',
                    ticket_template_id  = u'TTTS000001',
                    performance_datetime= datetime.datetime(2012,8,31,18,00),
                    xml = '''<TICKET>
                      <TEST1>test&#x20;test</TEST1>
                      <TEST2><![CDATA[TEST [] >M>J TEST@&nbsp;]]></TEST2>
                      <TEST3>&#x3000;</TEST3>
                      <FIXTAG01></FIXTAG01>
                      <FIXTAG02></FIXTAG02>
                      <FIXTAG03></FIXTAG03>
                      <FIXTAG04></FIXTAG04>
                      <FIXTAG05></FIXTAG05>
                      <FIXTAG06></FIXTAG06>
                    </TICKET>'''
                ),

                dict(
                    ticket_type         = SejTicketType.ExtraTicketWithBarcode,
                    event_name          = u'イベント名3',
                    performance_name    = u'パフォーマンス名',
                    ticket_template_id  = u'TTTS000001',
                    performance_datetime= datetime.datetime(2012,8,31,18,00),
                    xml = u'''<TICKET>
                      <TEST1>test&#x20;test</TEST1>
                      <TEST2><![CDATA[TEST [] >M>J TEST@&nbsp;]]></TEST2>
                      <TEST3>&#x3000;</TEST3>
                      <FIXTAG01></FIXTAG01>
                      <FIXTAG02></FIXTAG02>
                      <FIXTAG03></FIXTAG03>
                      <FIXTAG04></FIXTAG04>
                      <FIXTAG05></FIXTAG05>
                      <FIXTAG06></FIXTAG06>
                    </TICKET>'''
                    )
                ]
            )

        request_order(
            self.config.registry,
            tenant=self.tenant,
            sej_order=sej_order
            )

        self.server.poll()

        self.assertEqual(self.server.request.method, 'POST')
        self.assertEqual(self.server.request.url, 'http://127.0.0.1:38001/order/order.do')

        sej_tickets = sej_order.tickets

        req = cgi.parse_qs(self.server.request.body)
        self.assertEqual(req['X_shop_order_id'], [sej_order.order_no])
        self.assertEqual(req['user_namek'][0].decode('cp932'), sej_order.user_name)
        self.assertEqual(req['user_name_kana'][0].decode('cp932'), sej_order.user_name_kana)
        self.assertEqual(req['X_user_tel_no'], [sej_order.tel])
        self.assertEqual(req['X_user_post'], [sej_order.zip_code])
        self.assertEqual(req['X_user_email'], [sej_order.email])
        self.assertEqual(req['X_goukei_kingaku'], ['%06d' % sej_order.total_price])
        self.assertEqual(req['X_ticket_daikin'], ['%06d' % sej_order.ticket_price])
        self.assertEqual(req['X_ticket_kounyu_daikin'], ['%06d' % sej_order.commission_fee])
        self.assertEqual(req['X_hakken_daikin'], ['%06d' % sej_order.ticketing_fee])
        self.assertEqual(req['X_shori_kbn'], ['%02d' % SejPaymentType.CashOnDelivery.v])
        self.assertEqual(req['X_pay_lmt'], [build_sej_datetime_without_second(sej_order.payment_due_at)])
        self.assertEqual(req['X_saifuban_hakken_lmt'], [build_sej_datetime_without_second(sej_order.regrant_number_due_at)])

        assert sej_order is not None
        assert sej_order.total_price    == 15000
        assert sej_order.ticket_price   == 13000
        assert sej_order.commission_fee == 1000
        assert sej_order.ticketing_fee  == 1000
        assert sej_order.total_ticket_count == 3
        assert sej_order.ticket_count == 2
        assert sej_order.exchange_sheet_number == u'11111111'
        assert sej_order.billing_number == u'0000000001'
        assert sej_order.exchange_sheet_url == u'https://inticket.nrir1test.jp/order/hi.do'
        assert sej_tickets[0].barcode_number == '00001'

        assert sej_tickets[0].ticket_idx           == 1
        assert int(sej_tickets[0].ticket_type)     == SejTicketType.TicketWithBarcode.v # XXX: enumなので文字列として格納される
        assert sej_tickets[0].event_name           == u'イベント名1'
        assert sej_tickets[0].performance_name     == u'パフォーマンス名'
        assert sej_tickets[0].performance_datetime == datetime.datetime(2012,8,31,18,00)
        assert sej_tickets[0].ticket_template_id   == u'TTTS000001'
        assert sej_tickets[0].ticket_data_xml      is not None

        assert sej_tickets[1].barcode_number == '00002'
        assert sej_tickets[2].barcode_number == '00003'

    def test_request_order_cash_on_delivery_fail(self):
        '''2-1.決済要求 代引き'''
        from altair.app.ticketing.sej.api import create_sej_order
        from altair.app.ticketing.sej.exceptions import SejError
        from altair.app.ticketing.sej.models import SejOrder, SejTicket
        from altair.app.ticketing.sej.payment import SejPaymentType, SejTicketType, request_order
        from altair.app.ticketing.sej.payload import build_sej_datetime_without_second

        import webob.util

        sej_dummy_response = lambda environ: \
            '<SENBDATA>Error_Type=04&Error_Msg=Condition Unmatch&Error_Field=X_ticket_cnt&</SENBDATA>' \
            '<SENBDATA>DATA=END</SENBDATA>'

        webob.util.status_reasons[800] = 'OK'
        target = self._makeServer(sej_dummy_response, host='127.0.0.1', port=38001, status=800)

        sej_order = create_sej_order(
            self.config.registry,
            order_no=u"orderid00001",
            user_name=u"お客様氏名",
            user_name_kana=u'コイズミモリヨシ',
            tel=u'0312341234',
            zip_code=u'1070062',
            email=u'dev@ticketstar.jp',
            total_price=15000,
            ticket_price=13000,
            commission_fee=1000,
            ticketing_fee=1000,
            payment_type=SejPaymentType.CashOnDelivery,
            payment_due_at=datetime.datetime(2012,7,30,7,00), #u'201207300700',
            regrant_number_due_at=datetime.datetime(2012,7,30,7,00), # u'201207300700',
            tickets=[]
            )

        with self.assertRaises(SejError) as e:
            request_order(
                self.config.registry,
                tenant=self.tenant,
                sej_order=sej_order
                )

        self.server.poll()

        self.assertEqual(self.server.request.method, 'POST')
        self.assertEqual(self.server.request.url, 'http://127.0.0.1:38001/order/order.do')

        sej_tickets = sej_order.tickets

        req = cgi.parse_qs(self.server.request.body)
        self.assertEqual(req['X_shop_order_id'], [sej_order.order_no])
        self.assertEqual(req['user_namek'][0].decode('cp932'), sej_order.user_name)
        self.assertEqual(req['user_name_kana'][0].decode('cp932'), sej_order.user_name_kana)
        self.assertEqual(req['X_user_tel_no'], [sej_order.tel])
        self.assertEqual(req['X_user_post'], [sej_order.zip_code])
        self.assertEqual(req['X_user_email'], [sej_order.email])
        self.assertEqual(req['X_goukei_kingaku'], ['%06d' % sej_order.total_price])
        self.assertEqual(req['X_ticket_daikin'], ['%06d' % sej_order.ticket_price])
        self.assertEqual(req['X_ticket_kounyu_daikin'], ['%06d' % sej_order.commission_fee])
        self.assertEqual(req['X_hakken_daikin'], ['%06d' % sej_order.ticketing_fee])
        self.assertEqual(req['X_shori_kbn'], ['%02d' % SejPaymentType.CashOnDelivery.v])
        self.assertEqual(req['X_pay_lmt'], [build_sej_datetime_without_second(sej_order.payment_due_at)])
        self.assertEqual(req['X_saifuban_hakken_lmt'], [build_sej_datetime_without_second(sej_order.regrant_number_due_at)])

        self.assertEqual(e.exception.error_type, 4)
        self.assertEqual(e.exception.error_msg, 'Condition Unmatch')
        self.assertEqual(e.exception.error_field, 'X_ticket_cnt')

        self.assertIsNotNone(sej_order)
        self.assertEqual(sej_order.error_type, 4)


    def test_request_order_prepayment(self):
        '''2-1.決済要求 支払い済み'''
        from altair.app.ticketing.sej.api import create_sej_order
        from altair.app.ticketing.sej.models import SejOrder, SejTicket
        from altair.app.ticketing.sej.payment import SejPaymentType, SejTicketType, request_order

        import webob.util

        sej_sample_response\
            = '<SENBDATA>' + \
            'X_shop_order_id=%(order_no)s&'+ \
            'X_haraikomi_no=%(haraikomi_no)s&' + \
            'X_hikikae_no=%(hikikae_no)s&' + \
            'X_url_info=https://inticket.nrir1test.jp/order/hi.do&' +\
            'iraihyo_id_00=%(iraihyo_id_00)s&' + \
            'X_ticket_cnt=%(ticket_total_num)02d&' + \
            'X_ticket_hon_cnt=%(ticket_num)02d&'+ \
            'X_barcode_no_01=00001&' + \
            'X_barcode_no_02=00002&' + \
            'X_barcode_no_03=00003&' + \
             '</SENBDATA>' + \
            '<SENBDATA>DATA=END</SENBDATA>'

        def sej_dummy_response(environ):
            return sej_sample_response % dict(
                order_no         = 'orderid00001',
                haraikomi_no     = '0000000001',
                iraihyo_id_00    = '11111111',
                hikikae_no       = '22222222',
                ticket_total_num = 3,
                ticket_num       = 2,
            )

        webob.util.status_reasons[800] = 'OK'
        target = self._makeServer(sej_dummy_response, host='127.0.0.1', port=38001, status=800)
        sej_order = create_sej_order(
            self.config.registry,
            order_no        = u"orderid00001",
            user_name       = u"お客様氏名",
            user_name_kana  = u'コイズミモリヨシ',
            tel             = u'0312341234',
            zip_code        = u'1070062',
            email           = u'dev@ticketstar.jp',
            total_price     = 15000,
            ticket_price    = 13000,
            commission_fee  = 1000,
            ticketing_fee   = 1000,
            payment_type    = SejPaymentType.Paid,
            payment_due_at = datetime.datetime(2012,7,30,7,00), #u'201207300700',
            regrant_number_due_at = datetime.datetime(2012,7,30,7,00), # u'201207300700',
            tickets=[
                dict(
                    ticket_type         = SejTicketType.TicketWithBarcode,
                    event_name          = u'イベント名',
                    performance_name    = u'パフォーマンス名',
                    ticket_template_id  = u'TTTS000001',
                    performance_datetime= datetime.datetime(2012,8,31,18,00),
                    xml = u'''<?xml version="1.0" encoding="UTF-8" ?>
                    <TICKET>
                      <TEST1>test&#x20;test</TEST1>
                      <TEST2><![CDATA[TEST [] >M>J TEST@&nbsp;]]></TEST2>
                      <TEST3>&#x3000;</TEST3>
                      <FIXTAG01></FIXTAG01>
                      <FIXTAG02></FIXTAG02>
                      <FIXTAG03></FIXTAG03>
                      <FIXTAG04></FIXTAG04>
                      <FIXTAG05></FIXTAG05>
                      <FIXTAG06></FIXTAG06>
                    </TICKET>'''
                ),
                dict(
                    ticket_type         = SejTicketType.TicketWithBarcode,
                    event_name          = u'イベント名',
                    performance_name    = u'パフォーマンス名',
                    ticket_template_id  = u'TTTS000001',
                    performance_datetime= datetime.datetime(2012,8,31,18,00),
                    xml = u'''<?xml version="1.0" encoding="UTF-8" ?>
                    <TICKET>
                      <TEST1>test&#x20;test</TEST1>
                      <TEST2><![CDATA[TEST [] >M>J TEST@&nbsp;]]></TEST2>
                      <TEST3>&#x3000;</TEST3>
                      <FIXTAG01></FIXTAG01>
                      <FIXTAG02></FIXTAG02>
                      <FIXTAG03></FIXTAG03>
                      <FIXTAG04></FIXTAG04>
                      <FIXTAG05></FIXTAG05>
                      <FIXTAG06></FIXTAG06>
                    </TICKET>'''
                ),
                dict(
                    ticket_type         = SejTicketType.ExtraTicketWithBarcode,
                    event_name          = u'イベント名',
                    performance_name    = u'パフォーマンス名',
                    ticket_template_id  = u'TTTS000001',
                    performance_datetime= datetime.datetime(2012,8,31,18,00),
                    xml = u'''<TICKET>
                      <TEST1>test&#x20;test</TEST1>
                      <TEST2><![CDATA[TEST [] >M>J TEST@&nbsp;]]></TEST2>
                      <TEST3>&#x3000;</TEST3>
                      <FIXTAG01></FIXTAG01>
                      <FIXTAG02></FIXTAG02>
                      <FIXTAG03></FIXTAG03>
                      <FIXTAG04></FIXTAG04>
                      <FIXTAG05></FIXTAG05>
                      <FIXTAG06></FIXTAG06>
                    </TICKET>'''
                    )
                ]
            )


        sejTicketOrder = request_order(
            self.config.registry,
            tenant=self.tenant,
            sej_order=sej_order
            )
        self.server.poll()

        self.assertEqual(self.server.request.method, 'POST')
        self.assertEqual(self.server.request.url, 'http://127.0.0.1:38001/order/order.do')

        assert sej_order.total_ticket_count == 3
        assert sej_order.ticket_count == 2
        sej_tickets = sej_order.tickets
        assert len(sej_tickets) == 3
        idx = 1
        for ticket in sej_tickets:
            assert ticket.ticket_idx == idx
            assert ticket.event_name == u'イベント名'
            assert ticket.performance_name == u'パフォーマンス名'
            assert ticket.performance_datetime == datetime.datetime(2012,8,31,18,00)
            assert ticket.ticket_template_id == u'TTTS000001'
            idx+=1
        assert sej_order.exchange_sheet_number == u'11111111'
        assert sej_order.billing_number == u'0000000001'
        assert sej_order.exchange_sheet_url == u'https://inticket.nrir1test.jp/order/hi.do'

        sej_tickets = sej_order.tickets

        assert sej_tickets[0].barcode_number == '00001'
        assert sej_tickets[1].barcode_number == '00002'
        assert sej_tickets[2].barcode_number == '00003'

        assert sej_tickets[0].ticket_idx           == 1
        assert sej_tickets[0].ticket_type          == '%d' % SejTicketType.TicketWithBarcode.v
        assert sej_tickets[0].event_name           == u'イベント名'
        assert sej_tickets[0].performance_name     == u'パフォーマンス名'
        assert sej_tickets[0].performance_datetime == datetime.datetime(2012,8,31,18,00)
        assert sej_tickets[0].ticket_template_id   == u'TTTS000001'
        assert sej_tickets[0].ticket_data_xml      is not None

    def test_request_order_update(self):
        import webob.util
        import sqlahelper
        from altair.app.ticketing.sej.models import SejOrder, SejTicket, SejTicketType, SejOrderUpdateReason, SejPaymentType
        from altair.app.ticketing.sej.payment import request_update_order
        webob.util.status_reasons[800] = 'OK'

        target = self._makeServer(lambda environ: '<SENBDATA>X_haraikomi_no=00000001&X_hikikae_no=00001111&X_ticket_cnt=01&X_ticket_hon_cnt=01&X_url_info=https://inticket.nrir1test.jp/order/hi.do&X_shop_order_id=orderid00001&iraihyo_id_00=11111111&X_barcode_no_01=00002000</SENBDATA><SENBDATA>DATA=END</SENBDATA>', host='127.0.0.1', port=38001, status=800)

        sej_order = SejOrder(
            payment_type='%d' % SejPaymentType.CashOnDelivery.v,
            shop_id           = u'30520',
            billing_number    = u'00000001',
            exchange_number   = u'00001111',
            ticket_count      = 1,
            total_ticket_count = 1,
            total_price       = 15000,
            ticket_price      = 13000,
            commission_fee    = 1000,
            ticketing_fee     = 1000,
            exchange_sheet_url      = u'https://inticket.nrir1test.jp/order/hi.do',
            order_no      = u'orderid00001',
            exchange_sheet_number = u'11111111',
            order_at      = datetime.datetime.now(),
            regrant_number_due_at = datetime.datetime(2012,7,30,7,00) # u'201207300700'
            )

        ticket = SejTicket(
            order=sej_order,
            ticket_idx=1,
            ticket_type=('%d' % SejTicketType.TicketWithBarcode.v),
            barcode_number='00001000',
            event_name=u'イベント',
            performance_name=u'パフォーマンス',
            performance_datetime=datetime.datetime(2012,8,30,19,00),
            ticket_template_id='TTTS0001',
            ticket_data_xml=u'<TICKET><FIXTAG01>HEY</FIXTAG01></TICKET>',
            product_item_id=12345
            )

        request_update_order(
            self.config.registry,
            tenant=self.tenant,
            sej_order=sej_order, 
            update_reason=SejOrderUpdateReason.Change
            )

        self.server.poll()

        result = cgi.parse_qs(self.server.request.body)
        self.assertEqual(result['X_hakken_daikin'], ['001000'])
        self.assertEqual(result['X_ticket_cnt'], ['01'])
        self.assertEqual(result['X_ticket_hon_cnt'], ['01'])
        self.assertEqual(result['xcode'], ['37ec9c530172b72093ff15ee60880854'])
        self.assertEqual(result['X_hikikae_no'], ['00001111'])
        self.assertEqual(result['X_shop_order_id'], ['orderid00001'])
        self.assertEqual(result['X_shop_id'], ['30520'])
        self.assertEqual(result['X_goukei_kingaku'], ['015000'])
        self.assertEqual(result['X_saifuban_hakken_lmt'], ['201207300700'])
        self.assertEqual(result['X_ticket_kbn_01'], ['1'])
        self.assertEqual(result['X_upd_riyu'], ['01'])
        self.assertEqual(result['ticket_text_01'], ["<?xml version='1.0' encoding='Shift_JIS' ?>\n<TICKET><FIXTAG01>HEY</FIXTAG01></TICKET>"])
        self.assertEqual(result['X_ticket_kounyu_daikin'], ['001000'])
        self.assertEqual(result['X_haraikomi_no'], ['00000001'])
        self.assertEqual(result['X_ticket_daikin'], ['013000'])
        self.assertEqual(result['X_kouen_date_01'], ['201208301900'])
        self.assertEqual(result['kougyo_mei_01'], ['\x83C\x83x\x83\x93\x83g'])
        self.assertEqual(result['X_ticket_template_01'], ['TTTS0001'])
        self.assertEqual(result['kouen_mei_01'], ['\x83p\x83t\x83H\x81[\x83}\x83\x93\x83X'])
        self.assertEqual(self.server.request.method, 'POST')
        self.assertEqual(self.server.request.url, 'http://127.0.0.1:38001/order/updateorder.do')
        self.assertEqual(ticket.barcode_number, '00002000')

    def test_request_order_update_fail(self):
        import webob.util
        import sqlahelper
        from altair.app.ticketing.sej.exceptions import SejError
        from altair.app.ticketing.sej.models import SejOrder, SejTicket, SejTicketType, SejOrderUpdateReason, SejPaymentType
        from altair.app.ticketing.sej.payment import request_update_order
        webob.util.status_reasons[800] = 'OK'

        target = self._makeServer(lambda environ: '<SENBDATA>Error_Type=38&Error_Msg=Already Paid&Error_Field=X_shop_id,X_shop_order_id,X_ticket_hon_cnt&</SENBDATA><SENBDATA>DATA=END</SENBDATA>', host='127.0.0.1', port=38001, status=800)

        sej_order = SejOrder(
            payment_type='%d' % SejPaymentType.CashOnDelivery.v,
            shop_id           = u'30520',
            billing_number    = u'00000001',
            exchange_number   = u'00001111',
            ticket_count      = 1,
            total_ticket_count = 1,
            total_price       = 15000,
            ticket_price      = 13000,
            commission_fee    = 1000,
            ticketing_fee     = 1000,
            exchange_sheet_url      = u'https://inticket.nrir1test.jp/order/hi.do',
            order_no      = u'orderid00001',
            exchange_sheet_number = u'11111111',
            order_at      = datetime.datetime.now(),
            regrant_number_due_at = datetime.datetime(2012,7,30,7,00) # u'201207300700'
            )

        ticket = SejTicket(
            order=sej_order,
            ticket_idx=1,
            ticket_type=('%d' % SejTicketType.TicketWithBarcode.v),
            barcode_number='00001000',
            event_name=u'イベント',
            performance_name=u'パフォーマンス',
            performance_datetime=datetime.datetime(2012,8,30,19,00),
            ticket_template_id='TTTS0001',
            ticket_data_xml=u'<TICKET><FIXTAG01>HEY</FIXTAG01></TICKET>',
            product_item_id=12345
            )

        with self.assertRaises(SejError) as e:
            request_update_order(
                self.config.registry,
                tenant=self.tenant,
                sej_order=sej_order, 
                update_reason=SejOrderUpdateReason.Change
                )

        self.server.poll()

        result = cgi.parse_qs(self.server.request.body)
        self.assertEqual(result['X_hakken_daikin'], ['001000'])
        self.assertEqual(result['X_ticket_cnt'], ['01'])
        self.assertEqual(result['X_ticket_hon_cnt'], ['01'])
        self.assertEqual(result['xcode'], ['37ec9c530172b72093ff15ee60880854'])
        self.assertEqual(result['X_hikikae_no'], ['00001111'])
        self.assertEqual(result['X_shop_order_id'], ['orderid00001'])
        self.assertEqual(result['X_shop_id'], ['30520'])
        self.assertEqual(result['X_goukei_kingaku'], ['015000'])
        self.assertEqual(result['X_saifuban_hakken_lmt'], ['201207300700'])
        self.assertEqual(result['X_ticket_kbn_01'], ['1'])
        self.assertEqual(result['X_upd_riyu'], ['01'])
        self.assertEqual(result['ticket_text_01'], ["<?xml version='1.0' encoding='Shift_JIS' ?>\n<TICKET><FIXTAG01>HEY</FIXTAG01></TICKET>"])
        self.assertEqual(result['X_ticket_kounyu_daikin'], ['001000'])
        self.assertEqual(result['X_haraikomi_no'], ['00000001'])
        self.assertEqual(result['X_ticket_daikin'], ['013000'])
        self.assertEqual(result['X_kouen_date_01'], ['201208301900'])
        self.assertEqual(result['kougyo_mei_01'], ['\x83C\x83x\x83\x93\x83g'])
        self.assertEqual(result['X_ticket_template_01'], ['TTTS0001'])
        self.assertEqual(result['kouen_mei_01'], ['\x83p\x83t\x83H\x81[\x83}\x83\x93\x83X'])
        self.assertEqual(self.server.request.method, 'POST')
        self.assertEqual(self.server.request.url, 'http://127.0.0.1:38001/order/updateorder.do')
        self.assertEqual(ticket.barcode_number, '00001000')
        self.assertEqual(e.exception.error_type, 38)
        self.assertEqual(e.exception.error_msg, 'Already Paid')
        self.assertEqual(e.exception.error_field, 'X_shop_id,X_shop_order_id,X_ticket_hon_cnt')

    def test_request_order_update_11554(self):
        import webob.util
        import sqlahelper
        from altair.app.ticketing.sej.exceptions import SejError
        from altair.app.ticketing.sej.models import SejOrder, SejTicket, SejTicketType, SejOrderUpdateReason, SejPaymentType
        from altair.app.ticketing.sej.payment import request_update_order
        webob.util.status_reasons[800] = 'OK'

        target = self._makeServer(lambda environ: '<SENBDATA>X_haraikomi_no=00000001&X_hikikae_no=00001111&X_ticket_cnt=02&X_ticket_hon_cnt=01&X_url_info=https://inticket.nrir1test.jp/order/hi.do&X_shop_order_id=orderid00001&iraihyo_id_00=11111111&X_barcode_no_01=00002000</SENBDATA><SENBDATA>DATA=END</SENBDATA>', host='127.0.0.1', port=38001, status=800)

        sej_order = SejOrder(
            payment_type='%d' % SejPaymentType.CashOnDelivery.v,
            shop_id           = u'30520',
            billing_number    = u'00000001',
            exchange_number   = u'00001111',
            ticket_count      = 0,
            total_ticket_count = 2,
            total_price       = 15000,
            ticket_price      = 13000,
            commission_fee    = 1000,
            ticketing_fee     = 1000,
            exchange_sheet_url      = u'https://inticket.nrir1test.jp/order/hi.do',
            order_no      = u'orderid00001',
            exchange_sheet_number = u'11111111',
            order_at      = datetime.datetime.now(),
            regrant_number_due_at = datetime.datetime(2012,7,30,7,00), # u'201207300700'
            tickets=[
                SejTicket(
                    ticket_idx=1,
                    ticket_type=('%d' % SejTicketType.TicketWithBarcode.v),
                    barcode_number='00001000',
                    event_name=u'イベント',
                    performance_name=u'パフォーマンス',
                    performance_datetime=datetime.datetime(2012,8,30,19,00),
                    ticket_template_id='TTTS0001',
                    ticket_data_xml=u'<TICKET><FIXTAG01>HEY</FIXTAG01></TICKET>',
                    product_item_id=12345
                    ),
                SejTicket(
                    ticket_idx=2,
                    ticket_type=('%d' % SejTicketType.ExtraTicket.v),
                    barcode_number='00001001',
                    event_name=u'イベント',
                    performance_name=u'パフォーマンス',
                    performance_datetime=datetime.datetime(2012,8,30,19,00),
                    ticket_template_id='TTTS0001',
                    ticket_data_xml=u'<TICKET><FIXTAG01>HEY</FIXTAG01></TICKET>',
                    product_item_id=12345
                    ),
                ]
            )

        request_update_order(
            self.config.registry,
            tenant=self.tenant,
            sej_order=sej_order, 
            update_reason=SejOrderUpdateReason.Change
            )

        self.server.poll()

        result = cgi.parse_qs(self.server.request.body)
        self.assertEqual(result['X_hakken_daikin'], ['001000'])
        self.assertEqual(result['X_ticket_cnt'], ['02'])
        self.assertEqual(result['X_ticket_hon_cnt'], ['01'])
        self.assertEqual(result['xcode'], ['93aec2f6f4954f25b752a39fb7f92719'])
        self.assertEqual(result['X_hikikae_no'], ['00001111'])
        self.assertEqual(result['X_shop_order_id'], ['orderid00001'])
        self.assertEqual(result['X_shop_id'], ['30520'])
        self.assertEqual(result['X_goukei_kingaku'], ['015000'])
        self.assertEqual(result['X_saifuban_hakken_lmt'], ['201207300700'])
        self.assertEqual(result['X_ticket_kbn_01'], ['1'])
        self.assertEqual(result['X_upd_riyu'], ['01'])
        self.assertEqual(result['ticket_text_01'], ["<?xml version='1.0' encoding='Shift_JIS' ?>\n<TICKET><FIXTAG01>HEY</FIXTAG01></TICKET>"])
        self.assertEqual(result['X_ticket_kounyu_daikin'], ['001000'])
        self.assertEqual(result['X_haraikomi_no'], ['00000001'])
        self.assertEqual(result['X_ticket_daikin'], ['013000'])
        self.assertEqual(result['X_kouen_date_01'], ['201208301900'])
        self.assertEqual(result['kougyo_mei_01'], ['\x83C\x83x\x83\x93\x83g'])
        self.assertEqual(result['X_ticket_template_01'], ['TTTS0001'])
        self.assertEqual(result['kouen_mei_01'], ['\x83p\x83t\x83H\x81[\x83}\x83\x93\x83X'])
        self.assertEqual(self.server.request.method, 'POST')
        self.assertEqual(self.server.request.url, 'http://127.0.0.1:38001/order/updateorder.do')
        self.assertEqual(sej_order.ticket_count, 1)
        self.assertEqual(sej_order.total_ticket_count, 2)


    def test_create_ticket_template_without_css(self):
        from altair.app.ticketing.sej.models import SejTicketTemplateFile
        from altair.app.ticketing.sej.ticket import package_ticket_template_to_zip
        import sqlahelper

        st = SejTicketTemplateFile(notation_version=1)

        st.status = '1'
        st.template_id = u'TTTS000001'
        st.template_name = u'ＴＳテンプレート０１'
        st.publish_start_date      = datetime.datetime(2012,06,06)
        st.publish_end_date        = None
        st.ticket_html = u'''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd"><html></html>'''.encode('utf-8')
        st.ticket_css  = None
        self.session.add(st)
        self.session.flush()

        filename = package_ticket_template_to_zip(self.session, 'TTTS000001')
        self.assertEqual(os.path.basename(filename), 'TTTS000001.zip')
        import zipfile
        z = zipfile.ZipFile(filename)
        files = set(zi.filename for zi in z.infolist())
        self.assertTrue('archive.txt' in files)
        self.assertTrue('TTEMPLATE.CSV' in files)
        self.assertTrue('TTTS000001/TTTS000001.htm' in files)
        self.assertTrue('TTTS000001/TTTS000001.css' not in files)

    def test_create_ticket_template_with_css(self):
        from altair.app.ticketing.sej.models import SejTicketTemplateFile
        from altair.app.ticketing.sej.ticket import package_ticket_template_to_zip
        import sqlahelper

        st = SejTicketTemplateFile(notation_version=1)

        st.status = '1'
        st.template_id = u'TTTS000001'
        st.template_name = u'ＴＳテンプレート０１'
        st.publish_start_date      = datetime.datetime(2012,06,06)
        st.publish_end_date        = None
        st.ticket_html = u'''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd"><html></html>'''.encode('utf-8')
        st.ticket_css  = u'''.dummy {}'''
        self.session.add(st)
        self.session.flush()

        filename = package_ticket_template_to_zip(self.session, 'TTTS000001')
        self.assertEqual(os.path.basename(filename), 'TTTS000001.zip')
        import zipfile
        z = zipfile.ZipFile(filename)
        files = set(zi.filename for zi in z.infolist())
        self.assertTrue('archive.txt' in files)
        self.assertTrue('TTEMPLATE.CSV' in files)
        self.assertTrue('TTTS000001/TTTS000001.htm' in files)
        self.assertTrue('TTTS000001/TTTS000001.css' in files)

if __name__ == u"__main__":
    import os
    print os.getpid()
    unittest.main()
