# -*- coding:utf-8 -*-
import unittest
import datetime
from pyramid import testing
import cgi
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
            'altair.app.ticketing.sej.models'
            ])
        self.server = None
        from altair.app.ticketing.sej.models import ThinSejTenant
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
        '''2-3.注文キャンセル'''
        from altair.app.ticketing.sej.models import SejOrder
        from altair.app.ticketing.sej.payment import SejOrderUpdateReason, request_cancel_order

        import webob.util
        webob.util.status_reasons[800] = 'OK'

        target = self._makeServer(lambda environ: '<SENBDATA>DATA=END</SENBDATA>', host='127.0.0.1', port=38001, status=800)
        sej_order = SejOrder(
            billing_number        = u'00000001',
            exchange_number       = u'12345678',
            ticket_count          = 1,
            url_info              = u'https://www.r1test.com/order/hi.do&iraihyo_id_00=11111111',
            order_no              = u'orderid00001',
            exchange_sheet_number = u'11111111',
            order_at              = datetime.datetime.now()
            )

        import sqlahelper

        DBSession = sqlahelper.get_session()
        DBSession.add(sej_order)
        DBSession.flush()

        request_cancel_order(
            self.config.registry,
            tenant=self.tenant,
            sej_order=sej_order
            )
        self.server.poll()

        self.assertEqual(self.server.request.method, 'POST')
        self.assertEqual(self.server.request.url, 'http://127.0.0.1:38001/order/cancelorder.do')

        sej_order = SejOrder.query.filter_by(order_no=u'orderid00001', billing_number=u'00000001').one()

        assert sej_order.cancel_at is not None

    def test_request_order_cash_on_delivery(self):
        '''2-1.決済要求 代引き'''
        from altair.app.ticketing.sej.api import create_sej_order
        from altair.app.ticketing.sej.ticket import SejTicketDataXml
        from altair.app.ticketing.sej.models import SejOrder, SejTicket
        from altair.app.ticketing.sej.payment import SejPaymentType, SejTicketType, request_order
        from altair.app.ticketing.sej.payload import build_sej_datetime_without_second

        import webob.util

        sej_sample_response\
            = '<SENBDATA>' + \
                'X_shop_order_id=%(order_no)s&'+ \
                'X_haraikomi_no=%(haraikomi_no)s&' + \
                'X_url_info=https://www.r1test.com/order/hi.do&' +\
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
                    xml = SejTicketDataXml(u'''<?xml version="1.0" encoding="UTF-8" ?>
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
                    </TICKET>''')
                ),

                dict(
                    ticket_type         = SejTicketType.TicketWithBarcode,
                    event_name          = u'イベント名2',
                    performance_name    = u'パフォーマンス名',
                    ticket_template_id  = u'TTTS000001',
                    performance_datetime= datetime.datetime(2012,8,31,18,00),
                    xml = SejTicketDataXml(u'''<?xml version="1.0" encoding="UTF-8" ?>
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
                    </TICKET>''')
                ),

                dict(
                    ticket_type         = SejTicketType.ExtraTicketWithBarcode,
                    event_name          = u'イベント名3',
                    performance_name    = u'パフォーマンス名',
                    ticket_template_id  = u'TTTS000001',
                    performance_datetime= datetime.datetime(2012,8,31,18,00),
                    xml = SejTicketDataXml(u'''<?xml version="1.0" encoding="Shift_JIS" ?>
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
                    </TICKET>''')
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

        sej_order = SejOrder.query.filter_by(order_no=u'orderid00001', billing_number=u'0000000001').one()
        sej_tickets = SejTicket.query.filter_by(order_no=sej_order.order_no).order_by(SejTicket.ticket_idx).all()

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
        assert sej_order.exchange_sheet_url == u'https://www.r1test.com/order/hi.do'
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

    def test_request_order_prepayment(self):
        '''2-1.決済要求 支払い済み'''
        from altair.app.ticketing.sej.api import create_sej_order
        from altair.app.ticketing.sej.ticket import SejTicketDataXml
        from altair.app.ticketing.sej.models import SejOrder, SejTicket
        from altair.app.ticketing.sej.payment import SejPaymentType, SejTicketType, request_order

        import webob.util

        sej_sample_response\
            = '<SENBDATA>' + \
            'X_shop_order_id=%(order_no)s&'+ \
            'X_haraikomi_no=%(haraikomi_no)s&' + \
            'X_hikikae_no=%(hikikae_no)s&' + \
            'X_url_info=https://www.r1test.com/order/hi.do&' +\
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
                    xml = SejTicketDataXml(u'''<?xml version="1.0" encoding="UTF-8" ?>
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
                    </TICKET>''')
                ),
                dict(
                    ticket_type         = SejTicketType.TicketWithBarcode,
                    event_name          = u'イベント名',
                    performance_name    = u'パフォーマンス名',
                    ticket_template_id  = u'TTTS000001',
                    performance_datetime= datetime.datetime(2012,8,31,18,00),
                    xml = SejTicketDataXml(u'''<?xml version="1.0" encoding="UTF-8" ?>
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
                    </TICKET>''')
                ),
                dict(
                    ticket_type         = SejTicketType.ExtraTicketWithBarcode,
                    event_name          = u'イベント名',
                    performance_name    = u'パフォーマンス名',
                    ticket_template_id  = u'TTTS000001',
                    performance_datetime= datetime.datetime(2012,8,31,18,00),
                    xml = SejTicketDataXml(u'''<?xml version="1.0" encoding="Shift_JIS" ?>
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
                    </TICKET>''')
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

        sej_order = SejOrder.query.filter_by(order_no=u'orderid00001', billing_number=u'0000000001').one()

        assert sej_order is not None
        assert sej_order.total_ticket_count == 3
        assert sej_order.ticket_count == 2
        sej_tickets = SejTicket.query.filter_by(order_no=sej_order.order_no).order_by(SejTicket.ticket_idx).all()
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
        assert sej_order.exchange_sheet_url == u'https://www.r1test.com/order/hi.do'

        sej_tickets = SejTicket.query.filter_by(order_no=sej_order.order_no).order_by(SejTicket.ticket_idx).all()
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
            exchange_sheet_url    = u'https://www.r1test.com/order/hi.do',
            order_no              = u'orderid00001',
            exchange_sheet_number = u'11111111',
            order_at              = datetime.datetime.now()
            )
        DBSession = sqlahelper.get_session()
        DBSession.add(sej_order)
        DBSession.flush()

        request_cancel_order(
            self.config.registry,
            tenant=self.tenant,
            sej_order=sej_order
            )

        self.server.poll()

        self.assertEqual(self.server.request.body, 'X_shop_id=30520&xcode=cf0fe9fc34300dd1f946e6c9c33fc020&X_hikikae_no=00001111&X_haraikomi_no=00000001&X_shop_order_id=orderid00001')
        self.assertEqual(self.server.request.method, 'POST')
        self.assertEqual(self.server.request.url, 'http://127.0.0.1:38001/order/cancelorder.do')

        sej_order = SejOrder.query.filter_by(order_no=u'orderid00001', billing_number=u'00000001').one()
        assert sej_order.cancel_at is not None

    def test_request_order_update(self):
        import webob.util
        import sqlahelper
        from altair.app.ticketing.sej.models import SejOrder, SejTicket, SejTicketType, SejOrderUpdateReason, SejPaymentType
        from altair.app.ticketing.sej.payment import request_update_order
        webob.util.status_reasons[800] = 'OK'

        target = self._makeServer(lambda environ: '<SENBDATA>X_haraikomi_no=00000001&X_hikikae_no=00001111&X_ticket_cnt=01&X_ticket_hon_cnt=01&X_url_info=https://www.r1test.com/order/hi.do&X_shop_order_id=orderid00001&iraihyo_id_00=11111111&X_barcode_no_01=00002000</SENBDATA><SENBDATA>DATA=END</SENBDATA>', host='127.0.0.1', port=38001, status=800)

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
            exchange_sheet_url      = u'https://www.r1test.com/order/hi.do',
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
            ticket_data_xml=u'<?xml version="1.0" encoding="Shift_JIS" ?><TICKET></TICKET>',
            product_item_id=12345
            )

        DBSession = sqlahelper.get_session()
        DBSession.add(sej_order)
        DBSession.add(ticket)
        DBSession.flush()

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
        self.assertEqual(result['ticket_text_01'], ['<?xml version="1.0" encoding="Shift_JIS" ?><TICKET></TICKET>'])
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

    def test_create_ticket_template(self):
        from altair.app.ticketing.sej.models import SejTicketTemplateFile
        from altair.app.ticketing.sej.ticket import package_ticket_template_to_zip
        import sqlahelper
        DBSession = sqlahelper.get_session()

        st = SejTicketTemplateFile()

        st.status = '1'
        st.template_id = u'TTTS000001'
        st.template_name = u'ＴＳテンプレート０１'
        st.publish_start_date      = datetime.datetime(2012,06,06)
        st.publish_end_date        = None
        st.ticket_html = u'''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html lang="en" xmlns:v="urn:schemas-microsoft-com:vml">
<head>
  <meta http-equiv="Content-Type" content="text/html;charset=UTF-8" />
  <title></title>
<!--[if (lt IE 9)]>
  <style type="text/css">
v\:* { behavior: url(#default#VML); }
</style>
<![endif]-->
  <style type="text/css">
body {
  margin: 0 0;
}

.pre { white-space: pre; }
.b { font-weight: 900; }
.f0 { font-family: "Arial"; }
.f1 { font-family: "Arial Black"; }
.f2 { font-family: "Verdana"; }
.f3 { font-family: "Impact"; }
.f4 { font-family: "Comic Sans MS"; }
.f5 { font-family: "Times New Roman"; }
.f6 { font-family: "Courier New"; }
.f7 { font-family: "Lucida Console"; }
.f8 { font-family: "Lucida Sans Unicode"; }
.f9 { font-family: "Modern"; }
.f10 { font-family: "Microsoft Sans Serif"; }
.f11 { font-family: "Roman"; }
.f12 { font-family: "Script"; }
.f13 { font-family: "Symbol"; }
.f14 { font-family: "Wingdings"; }
.f15 { font-family: "ＭＳ ゴシック"; }
.f16 { font-family: "ＭＳ Ｐゴシック"; }
.f17 { font-family: "ＭＳ 明朝"; }
.f18 { font-family: "ＭＳ Ｐ明朝"; }
.f19 { font-family: "MS UI Gothic"; }

</style>
  <script type="text/javascript">
var fonts = [
];

function XHR() {
  return typeof ActiveXObject != 'undefined' ?
      new ActiveXObject("Msxml2.XMLHTTP"):
      new XMLHttpRequest();
}

function loadXml(url, success, error) {
  var xhr = XHR();
  if (typeof xhr.overrideMimeType != 'undefined')
    xhr.overrideMimeType('text/xml');
  xhr.onreadystatechange = function() {
    if (xhr.readyState == 4) {
      if (xhr.status == 200 || xhr.status == 0) {
        var xml = xhr.responseXML;
        try {
          if ((!xml || !xml.documentElement) && xhr.responseText) {
            if (window.DOMParser) {
              var parser = new window.DOMParser();
              xml = parser.parseFromString(xhr.responseText, "text/xml");
            } else {
              var xml = new ActiveXObject("Microsoft.XMLDOM");
              xml.async = false;
              xml.load(url);
            }
          } else if (!xhr.responseText) {
            error('General failure');
            return;
          }
        } catch (e) {
          error(e.message);
          return;
        }
        success(xml);
      } else {
        error(xhr.status);
      }
    }
  };
  try {
    xhr.open("GET", url, true);
    xhr.send();
  } catch (e) {
    error(e.message);
  }
}

function parse(text, handlers) {
  var regexp = /"((?:[^"]|\\.)*)"|:([^\s"]*)|(-?(?:[0-9]+(?:\.[0-9]+)?|\.[0-9]+)(?:[eE][-+]?[0-9]+)?)|([*+/A-Za-z_-]+)|([ \t]+)|(\r\n|\r|\n)|(.)/g;
  var stack = [];
  var column = 0, line = 0;
  handlers.$stack = stack;
  for (var g; g = regexp.exec(text);) {
    if (g[1]) {
      stack.push(g[1].replace(/\\(.)/, '$1'));
    } else if (g[2]) {
      stack.push(g[2]);
    } else if (g[3]) {
      stack.push(parseFloat(g[3]));
    } else if (g[4]) {
      switch (g[4]) {
      case 'd':
        stack.push(stack[stack.length - 1]);
        break;
      default:
        var handler = handlers[g[4]];
        if (handler === void(0))
          throw new Error("TSE00002: Unknown command: " + g[4]);
        var arity = handler.length;
        handler.apply(handlers, stack.splice(stack.length - arity, arity));
        break;
      }
    } else if (g[6]) {
      column = 0;
      line++;
      continue;
    } else if (g[7]) {
      throw new Error("TSE00001: Syntax error at column " + (column + 1) + " line " + (line + 1));
    }
    column += g[0].length;
  }
}

function findXmlNode(xmldoc, n, path) {
  var retval = null;
  if (typeof ActiveXObject == 'undefined') {
    var xpathResult = xmldoc.evaluate(path, n, null, XPathResult.ANY_TYPE, null);
    switch (xpathResult.resultType) {
    case XPathResult.UNORDERED_NODE_ITERATOR_TYPE:
    case XPathResult.ORDERED_NODE_ITERATOR_TYPE:
      retval = [];
      for (var n = null; (n = xpathResult.iterateNext());)
        retval.push(n);
      break;
    case XPathResult.UNORDERED_NODE_SNAPSHOT_TYPE:
    case XPathResult.ORDERED_NODE_SNAPSHOT_TYPE:
      retval = [];
      for (var i = 0, l = xpathResult.snapshotLength; i < l; i++)
        retval.push(xpathResult.snapshotItem(i));
      break;
    case XPathResult.NUMBER_TYPE:
      retval = xpathResult.numberValue;
      break;
    case XPathResult.STRING_TYPE:
      retval = xpathResult.stringValue;
      break;
    case XPathResult.BOOLEAN_TYPE:
      retval = xpathResult.booleanValue;
      break;
    }
  } else {
    retval = n.selectNodes(path);
  }
  return retval;
}

function stringizeXmlNodes(nodes) {
  var retval = [];
  for (var i = 0, l = nodes.length; i < l; i++) {
    retval.push(stringizeXmlNode(nodes[i]));
  }
  return retval.join('');
}

function stringizeXmlNode(n) {
  switch (n.nodeType) {
  case 1:
    return stringizeXmlNodes(n.childNodes);
  default:
    return n.nodeValue;
  }
}

function Drawable() {
  this.initialize.apply(this, arguments);
}

if (window.ActiveXObject) {
  function newVmlElement(name) {
    return document.createElement("v:" + name);
  }

  Drawable.prototype.initialize = function Drawable_initialize(n, width, height) {
    this.n = n;
    this.width = width;
    this.height = height;
  };

  Drawable.prototype.path = function Drawable_path(pathData) {
    var path = newVmlElement('shape');
    var buf = [];
    var currentPoint = { x: 0., y: 0. };
    for (var i in pathData) {
      var datum = pathData[i];
      switch (datum[0]) {
      case 'Z':
        buf.push('x');
        break;
      case 'M':
        buf.push('m',
          (datum[1] * 1000).toFixed(0),
          (datum[2] * 1000).toFixed(0));
        currentPoint = { x: datum[1], y: datum[2] };
        break;
      case 'L':
        buf.push('l',
          (datum[1] * 1000).toFixed(0),
          (datum[2] * 1000).toFixed(0));
        currentPoint = { x: datum[1], y: datum[2] };
        break;
      case 'C':
        buf.push('c',
          (datum[1] * 1000).toFixed(0),
          (datum[2] * 1000).toFixed(0),
          (datum[3] * 1000).toFixed(0),
          (datum[4] * 1000).toFixed(0),
          (datum[5] * 1000).toFixed(0),
          (datum[6] * 1000).toFixed(0));
        currentPoint = { x: datum[5], y: datum[6] };
        break;
      case 'Q':
        buf.push('q',
          (datum[1] * 1000).toFixed(0),
          (datum[2] * 1000).toFixed(0),
          (datum[3] * 1000).toFixed(0),
          (datum[4] * 1000).toFixed(0));
        currentPoint = { x: datum[3], y: datum[4] };
        break;
      case 'A':
        var rx = Math.abs(datum[1]), ry = Math.abs(datum[2]),
            phi = Math.abs(datum[3]), largeArc = datum[4], sweep = datum[5],
            x  = datum[6], y = datum[7];
        var s = Math.sin(Math.PI * phi / 180),
            c = Math.cos(Math.PI * phi / 180);
        var cx = (currentPoint.x - x) / 2, cy = (currentPoint.y - y) / 2;
        var x1_ = c * cx + s * cy, y1_ = -s * cx + c * cy;
        var lambda = Math.sqrt((x1_ * x1_) / (rx * rx) + (y1_ * y1_) / (ry * ry));
        if (lambda > 1)
          rx *= lambda, ry *= lambda;
        var c_ = (largeArc == sweep ? -1: 1) * Math.sqrt((rx * rx * ry * ry - rx * rx * y1_ * y1_ - ry * ry * x1_ * x1_) / (rx * rx * y1_ * y1_ + ry * ry * x1_ * x1_));
        var cx_ = c_ * (rx * y1_) / ry,
            cy_ = -c_ * (ry * x1_) / rx;
        var ecx = c * cx_ - s * cy_ + (x + currentPoint.x) / 2,
            ecy = s * cx_ + c * cy_ + (y + currentPoint.y) / 2;
        var vx1 = (x1_ - cx_) / rx, vy1 = (y1_ - cy_) / ry;
        var vx2 = (-x1_ - cx_) / rx, vy2 = (-y1_ - cy_) / ry;
        var theta1 = (vy1 > 0 ? 1: -1) * Math.acos(vx1 / Math.sqrt(vx1 * vx1 + vy1 * vy1));
        var thetad = (vx1 * vy2 - vy1 * vx2 > 0 ? 1: -1) * Math.acos((vx1 * vx2 + vy1 * vy2) / Math.sqrt(vx1 * vx1 + vy1 * vy1) / Math.sqrt(vx2 * vx2 + vy2 * vy2));
        if (sweep && thetad > 0)
          thetad -= Math.PI * 2;
        else if (!sweep && thetad < 0)
          thetad += Math.PI * 2;
        var rsx = ecx + Math.cos(theta1) * rx,
            rsy = ecy + Math.sin(theta1) * ry;
        var rex = ecx + Math.cos(theta1 + thetad) * rx,
            rey = ecy + Math.sin(theta1 + thetad) * ry;
        if (thetad < 0) {
          var tmp;
          tmp = rsx, rsx = rex, rex = tmp;
          tmp = rsy, rsy = rey, rey = tmp;
        }
        if (phi == 0) {
          var rsxs = (rsx * 1000).toFixed(0),
              rsys = (rsy * 1000).toFixed(0);
          var rexs = (rex * 1000).toFixed(0),
              reys = (rey * 1000).toFixed(0);
          buf.push('m', rsxs, rsys);
          buf.push('at',
            ((ecx - rx) * 1000).toFixed(0),
            ((ecy - ry) * 1000).toFixed(0),
            ((ecx + rx) * 1000).toFixed(0),
            ((ecy + ry) * 1000).toFixed(0),
            rsxs, rsys, rexs, reys);
          buf.push('m', rexs, reys);
        }
        break;
      }
    }
    path.style.display = 'block';
    path.style.position = 'absolute';
    path.style.left = '0';
    path.style.top = '0';
    path.style.width = this.width;
    path.style.height = this.height;
    path.coordSize = parseFloat(this.width) * 1000 + "," + parseFloat(this.height) * 1000;
    path.setAttribute('path', buf.join(' '));
    this.n.appendChild(path);
    return {
      n: path,
      style: function (value) {
        if (value.strokeWidth)
          path.setAttribute('strokeWeight', value.strokeWidth * 2.5);
        if (value.strokeColor) {
          path.setAttribute('strokeColor', value.strokeColor || 'none');
          path.setAttribute('stroked', 't');
        } else {
          path.setAttribute('stroked', 'f');
        }
        if (value.fillColor) {
          path.setAttribute('fillColor', value.fillColor);
          path.setAttribute('filled', 't');
        } else {
          path.setAttribute('filled', 'f');
        }
      }
    };
  };
} else {
  var SVG_NAMESPACE = 'http://www.w3.org/2000/svg';
  function newSvgElement(name) {
    return document.createElementNS(SVG_NAMESPACE, name);
  }
  Drawable.prototype.initialize = function Drawable_initialize(n, width, height) {
    this.n = n;
    var svg = newSvgElement('svg');
    svg.setAttribute('style', 'display:block;position:absolute;left:0;top:0');
    svg.setAttribute('version', '1.0');
    svg.setAttribute('width', width);
    svg.setAttribute('height', height);
    svg.setAttribute('viewBox', '0 0 ' + parseFloat(width) + ' ' + parseFloat(height));
    this.n.appendChild(svg);
    this.svg = svg;
  };

  Drawable.prototype.path = function Drawable_path(pathData) {
    var path = newSvgElement('path');
    var buf = [];
    for (var i in pathData) {
      buf.push.apply(buf, pathData[i]);
    }
    path.setAttribute('d', buf.join(' '));
    this.svg.appendChild(path);
    return {
      n: path,
      style: function (value) {
        if (value.strokeWidth)
          path.setAttribute('stroke-width', value.strokeWidth);
        path.setAttribute('stroke', value.strokeColor || 'none');
        path.setAttribute('fill', value.fillColor || 'none');
      }
    };
  };
}

function newHandler(n, xmldoc) {
  var pathData = [];
  var drawable = null;
  var unit = 'mm';
  var fontSize = 10;
  var classes = [];
  var currentPoint = { x: 0., y: 0. };
  var scale = 1.;
  var style = {
    fillColor: null,
    strokeColor: null,
    strokeWidth: null
  };
  function initPathData() {
    if (pathData == null)
      pathData = [['M', currentPoint.x, currentPoint.y]];
  }
  function initDrawable() {
    if (drawable == null)
      drawable = new Drawable(n, '1000' + unit, '1000' + unit);
  }
  return {
    xn: function xmlNode(path) {
      var nodes = findXmlNode(xmldoc, xmldoc.documentElement, path);
      for (var i = 0; i < nodes.length; i++)
        this.$stack.push(nodes[i]);
      this.$stack.push(nodes.length);
    },
    sxn: function _stringizeXmlNodes() {
      var l = this.$stack.pop();
      var nodes = this.$stack.splice(this.$stack.length - l, l);
      this.$stack.push(stringizeXmlNodes(nodes));
    },
    S: function _scale(value) {
      scale = value;
    },
    fs: function fontSize(value) {
      fontSize = value;
    },
    hc: function pushClass(klass) {
      classes.push(klass);
    },
    pc: function popClass() {
      classes.pop();
    },
    sc: function setClass(klass) {
      classes = [klass];
    },
    rg: function setFillColor(value) {
      style.fillColor = value;
    },
    RG: function setStrokeColor(value) {
      style.strokeColor = value;
    },
    Sw: function setStrokeWidth(value) {
      style.strokeWidth = value * scale;
    },
    U: function setUnit(_unit) {
      unit = _unit;
    },
    X: function showText(width, height, text) {
      n.insertAdjacentHTML('beforeEnd', [
        '<div style="position:absolute;',
        'font-size:', fontSize, 'pt', ';',
        'left:', currentPoint.x, unit, ';',
        'top:', currentPoint.y, unit, ';',
        'width:', width, unit, ';',
        'height:', height, unit, '"',
        ' class="', classes.join(' '), '"',
        '>', text, '</div>'].join(''));
    },
    N: function newPath() {
    },
    m: function moveTo(x, y) {
      x *= scale;
      y *= scale;
      if (pathData != null)
        pathData.push(['M', x, y]);
      currentPoint = { x: x, y: y };
    },
    l: function lineTo(x, y) {
      x *= scale;
      y *= scale;
      initPathData();
      pathData.push(['L', x, y]);
      currentPoint = { x: x, y: y };
    },
    c: function curveTo(x1, y1, x2, y2, x3, y3) {
      x1 *= scale;
      y1 *= scale;
      x2 *= scale;
      y2 *= scale;
      x3 *= scale;
      y3 *= scale;
      initPathData();
      pathData.push(['C', x1, y1, x2, y2, x3, y3]);
      currentPoint = { x: x3, y: y3 };
    },
    v: function curveToS1(x2, y2, x3, y3) {
      x2 *= scale;
      y2 *= scale;
      x3 *= scale;
      y3 *= scale;
      initPathData();
      pathData.push(['C', currentPoint.x, currentPoint.y, x2, y2, x3, y3]);
      currentPoint = { x: x3, y: y3 };
    },
    y: function curveToS2(x1, y1, x3, y3) {
      x1 *= scale;
      y1 *= scale;
      x3 *= scale;
      y3 *= scale;
      if (pathData == null)
        pathData = [['M', currentPoint.x, currentPoint.y]];
      pathData.push(['C', x1, y1, x3, y3, x3, y3]);
      currentPoint = { x: x3, y: y3 };
    },
    q: function quadraticCurveTo(x1, y1, x2, y2) {
      x1 *= scale;
      y1 *= scale;
      x2 *= scale;
      y2 *= scale;
      if (pathData == null)
        pathData = [['M', currentPoint.x, currentPoint.y]];
      pathData.push(['Q', x1, y1, x2, y2]);
      currentPoint = { x: x2, y: y2 };
    },
    a: function arc(rx, ry, phi, largeArc, sweep, x, y) {
      rx *= scale;
      ry *= scale;
      x *= scale;
      y *= scale;
      if (pathData == null)
        pathData = [['M', currentPoint.x, currentPoint.y]];
      pathData.push(['A', rx, ry, phi, largeArc, sweep, x, y]);
      currentPoint = { x: x, y: y };
    },
    h: function closePath() {
      if (pathData == null)
        pathData = [['M', currentPoint.x, currentPoint.y]];
      pathData.push(['Z']);
    },
    f: function fill() {
      if (pathData == null)
        return;
      initDrawable();
      drawable.path(pathData).style({
        strokeWidth: null,
        strokeColor: null,
        fillColor: style.fillColor
      });
      pathData = null;
    },
    s: function stroke() {
      if (pathData == null)
        return;
      pathData.push(['Z']);
      initDrawable();
      drawable.path(pathData).style({
        strokeWidth: style.strokeWidth,
        strokeColor: style.strokeColor,
        fillColor: null
      });
      pathData = null;
    },
    B: function strokeAndFill() {
      if (pathData == null)
        return;
      if (drawable == null)
        drawable = new Drawable(n, '1000' + unit, '1000' + unit);
      drawable.path(pathData).style(style);
      pathData = null;
    }
  };
}

function reportError(msg) {
  var page = document.getElementById('page');
  page.innerHTML = '';
  page.insertAdjacentHTML('beforeEnd', '<b>エラーが発生しました。</b><br/>');
  var n = document.createElement('pre');
  n.appendChild(document.createTextNode(msg));
  page.appendChild(n);
}

function tryWith(args, f, failure) {
  var i = 0;
  function _() {
    if (i >= args.length)
      return failure(args);
    f(args[i++], _);
  }
  _();
}

window.onload = function() {
  tryWith(
    ['file:///c:/sejpos/posapl/mmdata/mm60/xml/ptct.xml', 'ptct.xml'],
    function (dataUrl, next) {
      loadXml(dataUrl, function (xmldoc) {
        var page = document.getElementById('page');
        try {
          var handler = newHandler(page, xmldoc);
          parse(stringizeXmlNodes(findXmlNode(xmldoc, xmldoc.documentElement, 'b')), handler);
        } catch (e) {
          reportError(e.message);
        }
      }, next);
    },
    function () {
      reportError("TS00003: Load failure");
    }
  );
};
</script>
</head>
<body>
  <div id="page"></div>
</body>
</html>'''.encode('utf8')
        st.ticket_css  = None
        DBSession.add(st)
        DBSession.flush()

        filename = package_ticket_template_to_zip('TTTS000001')
        print filename

if __name__ == u"__main__":
    import os
    print os.getpid()
    unittest.main()
