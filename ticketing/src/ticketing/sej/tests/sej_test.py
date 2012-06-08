# -*- coding:utf-8 -*-
import unittest
import datetime

from ticketing.sej.payment import SejTicketDataXml
from ticketing.sej.utils import JavaHashMap

class SejTest(unittest.TestCase):

    def _getTarget(self):
        import webapi
        return webapi.DummyServer

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def setUp(self):
        import sqlahelper
        from sqlalchemy import create_engine
        from ticketing.sej.models import SejOrder
        engine = create_engine("sqlite:///")
        sqlahelper.get_session().remove()
        sqlahelper.add_engine(engine)
        Base = sqlahelper.get_base()
        Base.metadata.create_all()

    def tearDown(self):
        pass


    def test_callback_pay_notification(self):
        '''入金発券完了通知'''
        import sqlahelper
        from webob.multidict import MultiDict
        from ticketing.sej.models import SejOrder
        from ticketing.sej.payment import SejOrderUpdateReason, SejPaymentType, callback_notification

        sejOrder = SejOrder()

        sejOrder.process_type          = SejOrderUpdateReason.Change.v
        sejOrder.billing_number        = u'00000001'
        sejOrder.ticket_count          = 1
        sejOrder.exchange_sheet_url    = u'https://www.r1test.com/order/hi.do'
        sejOrder.order_id              = u'orderid00001'
        sejOrder.exchange_sheet_number = u'11111111'
        sejOrder.exchange_number       = u'22222222'
        sejOrder.order_at              = datetime.datetime.now()

        DBSession = sqlahelper.get_session()
        DBSession.add(sejOrder)
        DBSession.flush()

        m_dict = MultiDict()
        m_dict.add(u'X_shori_id', u'000000000001')
        m_dict.add(u'X_shop_id',u'30520')
        m_dict.add(u'X_shop_order_id',u'orderid00001')
        m_dict.add(u'X_tuchi_type',u'01') # '01':入金発券完了通知 '31':SVC強制取消通知
        m_dict.add(u'X_shori_kbn', u'%02d' % SejPaymentType.CashOnDelivery)
        m_dict.add(u'X_haraikomi_no',u'00000001')
        m_dict.add(u'X_hikikae_no',u'22222222')
        m_dict.add(u'X_goukei_kingaku',u'015000')
        m_dict.add(u'X_ticket_cnt',u'04')
        m_dict.add(u'X_ticket_hon_cnt',u'03')
        m_dict.add(u'X_kaishu_cnt',u'00')
        m_dict.add(u'X_pay_mise_no',u'000001')
        m_dict.add(u'pay_mise_name',u'五反田店')
        m_dict.add(u'X_hakken_mise_no',u'000002')
        m_dict.add(u'hakken_mise_name',u'西五反田店')
        m_dict.add(u'X_torikeshi_riyu', u'')
        m_dict.add(u'X_shori_time',u'201207010811')
        m_dict.add(u'xcode',u'c607ffcafbda1a13f629acce2dea24d5')

        response = callback_notification(m_dict)

        assert response == '<SENBDATA>status=800&</SENBDATA><SENBDATA>DATA=END</SENBDATA>'
        from ticketing.sej.models import SejNotification
        n = SejNotification.query.filter_by(order_id = u'orderid00001', billing_number=u'00000001').one()

        assert n.process_number        == '000000000001'
        assert int(n.payment_type)         == SejPaymentType.CashOnDelivery.v

        assert n.notification_type     == u'1'
        assert n.billing_number        == u'00000001'
        assert n.exchange_number       == u'22222222'
        assert n.total_price           == 15000
        assert n.total_ticket_count    == 4
        assert n.ticket_count          == 3
        assert n.return_ticket_count   == 0
        assert n.pay_store_number      == u'000001'
        assert n.pay_store_name        == u'五反田店'
        assert n.ticketing_store_number== u'000002'
        assert n.ticketing_store_name  == u'西五反田店'
        assert n.cancel_reason         == ''


        assert n.signature             == u'c607ffcafbda1a13f629acce2dea24d5'
        assert n.processed_at          == datetime.datetime(2012,7,1,8,11,00)

    def test_callback_svc_cancel_notification(self):
        '''CSV'''
        import sqlahelper
        from webob.multidict import MultiDict
        from ticketing.sej.models import SejOrder
        from ticketing.sej.payment import SejOrderUpdateReason, SejPaymentType, callback_notification

        sej_order = SejOrder()

        sej_order.process_type          = SejOrderUpdateReason.Change.v
        sej_order.billing_number        = u'00000001'
        sej_order.ticket_count          = 1
        sej_order.exchange_sheet_url    = u'https://www.r1test.com/order/hi.do&iraihyo_id_00=11111111'
        sej_order.order_id              = u'orderid00001'
        sej_order.exchange_sheet_number = u'11111111'
        sej_order.exchange_number       = u'22222222'
        sej_order.order_at              = datetime.datetime.now()

        DBSession = sqlahelper.get_session()
        DBSession.add(sej_order)
        DBSession.flush()

        m_dict = MultiDict()
        m_dict.add(u'X_shori_id', u'000000000002')
        m_dict.add(u'X_shop_id',u'30520')
        m_dict.add(u'X_shop_order_id',u'orderid00001')
        m_dict.add(u'X_tuchi_type',u'31') # '01':入金発券完了通知 '31':SVC強制取消通知
        m_dict.add(u'X_shori_kbn', u'%02d' % SejPaymentType.CashOnDelivery)
        m_dict.add(u'X_haraikomi_no',u'00000001')
        m_dict.add(u'X_hikikae_no',u'22222222')
        m_dict.add(u'X_goukei_kingaku',u'015000')
        m_dict.add(u'X_ticket_cnt',u'04')
        m_dict.add(u'X_ticket_hon_cnt',u'03')
        m_dict.add(u'X_kaishu_cnt',u'00')
        m_dict.add(u'X_pay_mise_no',u'000001')
        m_dict.add(u'pay_mise_name',u'五反田店')
        m_dict.add(u'X_hakken_mise_no',u'000002')
        m_dict.add(u'hakken_mise_name',u'西五反田店')
        m_dict.add(u'X_torikeshi_riyu', u'')
        m_dict.add(u'X_shori_time',u'201207010811')
        m_dict.add(u'xcode',u'c607ffcafbda1a13f629acce2dea24d5')

        response = callback_notification(m_dict)

        assert response == '<SENBDATA>status=800&</SENBDATA><SENBDATA>DATA=END</SENBDATA>'
        from ticketing.sej.models import SejNotification
        n = SejNotification.query.filter_by(order_id = u'orderid00001', billing_number=u'00000001').one()

        assert n.process_number == u'000000000002'
        assert int(n.payment_type )         == SejPaymentType.CashOnDelivery.v
        assert n.notification_type     == u'31'
        assert n.billing_number        == u'00000001'
        assert n.exchange_number       == u'22222222'
        assert n.total_price           == 15000
        assert n.total_ticket_count    == 4
        assert n.ticket_count          == 3
        assert n.return_ticket_count   == 0
        assert n.pay_store_number      == u'000001'
        assert n.pay_store_name        == u'五反田店'
        assert n.ticketing_store_number== u'000002'
        assert n.ticketing_store_name  == u'西五反田店'
        assert n.cancel_reason         == ''
        assert n.signature             == u'c607ffcafbda1a13f629acce2dea24d5'
        assert n.processed_at          == datetime.datetime(2012,7,1,8,11,00)

    def test_callback_expire_notification(self):
        '''CSV'''
        import sqlahelper
        from webob.multidict import MultiDict
        from ticketing.sej.models import SejOrder
        from ticketing.sej.payment import SejOrderUpdateReason, SejPaymentType, callback_notification

        sej_order = SejOrder()

        sej_order.process_type          = SejOrderUpdateReason.Change.v
        sej_order.billing_number        = u'00000001'
        sej_order.ticket_count          = 1
        sej_order.exchange_sheet_url    = u'https://www.r1test.com/order/hi.do&iraihyo_id_00=11111111'
        sej_order.order_id              = u'orderid00001'
        sej_order.exchange_sheet_number = u'11111111'
        sej_order.exchange_number       = u'22222222'
        sej_order.order_at              = datetime.datetime.now()

        DBSession = sqlahelper.get_session()
        DBSession.add(sej_order)
        DBSession.flush()

        m_dict = MultiDict()
        m_dict.add(u'X_shori_id', u'000000000003')
        m_dict.add(u'X_shop_id',u'30520')
        m_dict.add(u'X_shop_order_id',u'orderid00001')
        m_dict.add(u'X_tuchi_type',u'72') # '01':入金発券完了通知 '31':SVC強制取消通知
        m_dict.add(u'X_shori_kbn', u'%02d' % SejPaymentType.CashOnDelivery)
        m_dict.add(u'X_lmt_time_new',u'201207010811')
        m_dict.add(u'X_haraikomi_no',u'00000001')
        m_dict.add(u'X_hikikae_no',u'22222222')
        m_dict.add(u'X_shori_time',u'201207010811')
        m_dict.add(u'xcode',u'c607ffcafbda1a13f629acce2dea24d5')

        response = callback_notification(m_dict)

        assert response == '<SENBDATA>status=800&</SENBDATA><SENBDATA>DATA=END</SENBDATA>'
        from ticketing.sej.models import SejNotification
        n = SejNotification.query.filter_by(order_id = u'orderid00001', billing_number=u'00000001').one()

        assert n.process_number == u'000000000003'
        assert int(n.payment_type )         == SejPaymentType.CashOnDelivery.v
        assert n.notification_type     == u'72'
        assert n.billing_number        == u'00000001'
        assert n.exchange_number       == u'22222222'
        assert n.signature             == u'c607ffcafbda1a13f629acce2dea24d5'
        assert n.processed_at          == datetime.datetime(2012,7,1,8,11,00)

    def test_request_order_cancel(self):
        '''2-3.注文キャンセル'''
        from ticketing.sej.models import SejOrder
        from ticketing.sej.payment import SejOrderUpdateReason, request_cancel_order

        import webob.util
        webob.util.status_reasons[800] = 'OK'

        target = self._makeOne(lambda environ: '<SENBDATA>DATA=END</SENBDATA>', host='127.0.0.1', port=38002, status=800)
        target.start()

        sej_order = SejOrder()

        sej_order.process_type     = SejOrderUpdateReason.Change.v
        sej_order.billing_number  = u'00000001'
        sej_order.exchange_number = u'12345678'
        sej_order.ticket_count  = 1
        sej_order.url_info      = u'https://www.r1test.com/order/hi.do&iraihyo_id_00=11111111'
        sej_order.order_id      = u'orderid00001'
        sej_order.exchange_sheet_number = u'11111111'
        sej_order.order_at      = datetime.datetime.now()

        import sqlahelper

        DBSession = sqlahelper.get_session()
        DBSession.add(sej_order)
        DBSession.flush()

        request_cancel_order(
            order_id=u'orderid00001',
            billing_number=u'00000001',
            exchange_number ='12345678',
            hostname=u"http://127.0.0.1:38002"
        )

        target.assert_method('POST')
        target.assert_url('http://127.0.0.1:38002/order/cancelorder.do')

        sej_order = SejOrder.query.filter_by(order_id = u'orderid00001', billing_number=u'00000001').one()

        assert sej_order.cancel_at is not None

    def test_request_order_cash_on_delivery(self):
        '''2-1.決済要求 代引き'''

        from ticketing.sej.models import SejOrder
        from ticketing.sej.payment import SejPaymentType, SejTicketType, request_order

        import webob.util

        sej_sample_response\
            = '<SENBDATA>' + \
                'X_shop_order_id=%(order_id)s&'+ \
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
                order_id         = 'orderid00001',
                haraikomi_no     = '0000000001',
                iraihyo_id_00    = '11111111',
                ticket_total_num = 3,
                ticket_num       = 2,
            )

        webob.util.status_reasons[800] = 'OK'
        target = self._makeOne(sej_dummy_response, host='127.0.0.1', port=38001, status=800)
        target.start()

        request_order(
            shop_name       = u'楽天チケット',
            contact_01      = u'contactあ',
            contact_02      = u'連絡先2',
            order_id        = u"orderid00001",
            username        = u"お客様氏名",
            username_kana   = u'コイズミモリヨシ',
            tel             = u'0312341234',
            zip             = u'1070062',
            email           = u'dev@ticketstar.jp',
            total           = 15000,
            ticket_total    = 13000,
            commission_fee  = 1000,
            ticketing_fee   = 1000,
            payment_type    = SejPaymentType.CashOnDelivery,
            payment_due_datetime = datetime.datetime(2012,7,30,7,00), #u'201207300700',
            regrant_number_datetime = datetime.datetime(2012,7,30,7,00), # u'201207300700',

            hostname=u"http://127.0.0.1:38001",

            tickets = [
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

        target.assert_method('POST')
        target.assert_url('http://127.0.0.1:38001/order/order.do')

        order = SejOrder.query.filter_by(order_id = u'orderid00001', billing_number=u'0000000001').one()

        assert order is not None
        assert order.total_price    == 15000
        assert order.ticket_price   == 13000
        assert order.commission_fee == 1000
        assert order.ticketing_fee  == 1000
        assert order.total_ticket_count == 3
        assert order.ticket_count == 2
        assert order.exchange_sheet_number == u'11111111'
        assert order.billing_number == u'0000000001'
        assert order.exchange_sheet_url == u'https://www.r1test.com/order/hi.do'
        assert order.tickets[0].barcode_number == '00001'

        assert order.tickets[0].ticket_idx           == 1
        assert order.tickets[0].ticket_type          == SejTicketType.TicketWithBarcode.v
        assert order.tickets[0].event_name           == u'イベント名1'
        assert order.tickets[0].performance_name     == u'パフォーマンス名'
        assert order.tickets[0].performance_datetime == datetime.datetime(2012,8,31,18,00)
        assert order.tickets[0].ticket_template_id   == u'TTTS000001'
        assert order.tickets[0].ticket_data_xml      is not None

        assert order.tickets[1].barcode_number == '00002'
        assert order.tickets[2].barcode_number == '00003'


    def test_request_order_prepayment(self):
        '''2-1.決済要求 支払い済み'''
        import sqlahelper
        from ticketing.sej.models import SejOrder
        from ticketing.sej.payment import SejPaymentType, SejTicketType, request_order

        import webob.util

        sej_sample_response\
            = '<SENBDATA>' + \
            'X_shop_order_id=%(order_id)s&'+ \
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
                order_id         = 'orderid00001',
                haraikomi_no     = '0000000001',
                iraihyo_id_00    = '11111111',
                hikikae_no       = '22222222',
                ticket_total_num = 3,
                ticket_num       = 2,
            )

        webob.util.status_reasons[800] = 'OK'
        target = self._makeOne(sej_dummy_response, host='127.0.0.1', port=38001, status=800)
        target.start()

        sejTicketOrder = request_order(
             shop_name       = u'楽天チケット',
             contact_01      = u'contactあ',
             contact_02      = u'連絡先2',
             order_id        = u"orderid00001",
             username        = u"お客様氏名",
             username_kana   = u'コイズミモリヨシ',
             tel             = u'0312341234',
             zip             = u'1070062',
             email           = u'dev@ticketstar.jp',
             total           = 15000,
             ticket_total    = 13000,
             commission_fee  = 1000,
             ticketing_fee   = 1000,
             payment_type    = SejPaymentType.Paid,
             payment_due_datetime = datetime.datetime(2012,7,30,7,00), #u'201207300700',
            regrant_number_datetime = datetime.datetime(2012,7,30,7,00), # u'201207300700',

             hostname=u"http://127.0.0.1:38001",

             tickets = [
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

        target.assert_method('POST')
        target.assert_url('http://127.0.0.1:38001/order/order.do')

        sej_order = SejOrder.query.filter_by(order_id = u'orderid00001', billing_number=u'0000000001').one()

        assert sej_order is not None
        assert sej_order.total_ticket_count == 3
        assert sej_order.ticket_count == 2
        assert len(sej_order.tickets) == 3
        idx = 1
        for ticket in sej_order.tickets:
            assert ticket.ticket_idx == idx
            assert ticket.event_name == u'イベント名'
            assert ticket.performance_name == u'パフォーマンス名'
            assert ticket.performance_datetime == datetime.datetime(2012,8,31,18,00)
            assert ticket.ticket_template_id == u'TTTS000001'
            idx+=1
        assert sej_order.exchange_sheet_number == u'11111111'
        assert sej_order.billing_number == u'0000000001'
        assert sej_order.exchange_sheet_url == u'https://www.r1test.com/order/hi.do'

        assert sej_order.tickets[0].barcode_number == '00001'
        assert sej_order.tickets[1].barcode_number == '00002'
        assert sej_order.tickets[2].barcode_number == '00003'

        assert sej_order.tickets[0].ticket_idx           == 1
        assert sej_order.tickets[0].ticket_type          == SejTicketType.TicketWithBarcode.v
        assert sej_order.tickets[0].event_name           == u'イベント名'
        assert sej_order.tickets[0].performance_name     == u'パフォーマンス名'
        assert sej_order.tickets[0].performance_datetime == datetime.datetime(2012,8,31,18,00)
        assert sej_order.tickets[0].ticket_template_id   == u'TTTS000001'
        assert sej_order.tickets[0].ticket_data_xml      is not None

    def test_request_order_cancel(self):

        import webob.util
        import sqlahelper
        from ticketing.sej.models import SejOrder
        from ticketing.sej.payment import SejOrderUpdateReason, request_cancel_order
        webob.util.status_reasons[800] = 'OK'

        target = self._makeOne(lambda environ: '<SENBDATA>DATA=END</SENBDATA>', host='127.0.0.1', port=38002, status=800)
        target.start()

        sej_order = SejOrder()

        sej_order.process_type     = SejOrderUpdateReason.Change.v
        sej_order.billing_number    = u'00000001'
        sej_order.exchange_number   = u'00001111'
        sej_order.ticket_count      = 1
        sej_order.exchange_sheet_url      = u'https://www.r1test.com/order/hi.do&iraihyo_id_00=11111111'
        sej_order.order_id      = u'orderid00001'
        sej_order.exchange_sheet_number = u'11111111'
        sej_order.order_at      = datetime.datetime.now()


        DBSession = sqlahelper.get_session()
        DBSession.add(sej_order)
        DBSession.flush()

        request_cancel_order(
            order_id=u'orderid00001',
            billing_number=u'00000001',
            exchange_number=u'00001111',
            hostname=u"http://127.0.0.1:38002"
        )

        target.assert_body('X_shop_id=30520&xcode=cf0fe9fc34300dd1f946e6c9c33fc020&X_hikikae_no=00001111&X_haraikomi_no=00000001&X_shop_order_id=orderid00001')
        target.assert_method('POST')
        target.assert_url('http://127.0.0.1:38002/order/cancelorder.do')

        sej_order = SejOrder.query.filter_by(order_id = u'orderid00001', billing_number=u'00000001').one()
        assert sej_order.cancel_at is not None

    def test_refund_file(self):

        from ticketing.sej.models import SejOrder, SejCancelTicket, SejCancelEvent
        from ticketing.sej.payment import SejOrderUpdateReason, SejPaymentType, request_cancel_event

        import sqlahelper
        DBSession = sqlahelper.get_session()

        event = SejCancelEvent()
        event.available = 1
        event.shop_id = u'30520'
        event.event_code_01  = u'EPZED'
        event.event_code_02  = u'0709A'
        event.title = u'入金、払戻用興行'
        event.sub_title = u'入金、払戻用公演'
        event.event_at = datetime.datetime(2012,8,31,18,00)
        event.start_at = datetime.datetime(2012,6,7,18,30)
        event.end_at = datetime.datetime(2012,6,10,18,30)
        event.expire_at = datetime.datetime(2012,6,10,18,30)
        event.event_expire_at = datetime.datetime(2012,6,10,18,30)
        event.ticket_expire_at = datetime.datetime(2012,7,10,18,30)
        event.disapproval_reason = u''
        event.need_stub = 1
        event.remarks = u'備考'
        event.un_use_01 = u''
        event.un_use_02 = u''
        event.un_use_03 = u''
        event.un_use_04 = u''
        event.un_use_05 = u''

        event.tickets = list()

        DBSession.add(event)

        ticket = SejCancelTicket()
        ticket.available = 1
        ticket.shop_id = u'30520'
        ticket.event_code_01  = u'EPZED'
        ticket.event_code_02  = u'0709A'
        ticket.order_id  = u'120605112150'
        ticket.ticket_barcode_number = u'2222222222222'
        ticket.refund_ticket_amount = 13000
        ticket.refund_amount = 2000
        DBSession.add(ticket)
        event.tickets.append(ticket)


        DBSession.flush()


        request_cancel_event(event)

    def test_refund_file(self):

        from ticketing.sej.models import SejOrder, SejCancelTicket, SejCancelEvent
        from ticketing.sej.payment import SejOrderUpdateReason, SejPaymentType, request_cancel_event

        import sqlahelper
        DBSession = sqlahelper.get_session()

        event1 = SejCancelEvent()
        event1.available = 1
        event1.shop_id = u'30520'
        event1.event_code_01  = u'EPZED'
        event1.event_code_02  = u'0709A'
        event1.title = u'入金、払戻用興行'
        event1.sub_title = u'入金、払戻用公演'
        event1.event_at = datetime.datetime(2012,8,31,18,00)
        event1.start_at = datetime.datetime(2012,6,7,18,30)
        event1.end_at = datetime.datetime(2012,6,10,18,30)
        event1.event_expire_at = datetime.datetime(2012,6,10,18,30)
        event1.ticket_expire_at = datetime.datetime(2012,7,10,18,30)
        event1.refund_enabled = 1
        event1.disapproval_reason = None
        event1.need_stub = 1
        event1.remarks = u'備考'
        event1.un_use_01 = u''
        event1.un_use_02 = u''
        event1.un_use_03 = u''
        event1.un_use_04 = u''
        event1.un_use_05 = u''

        event1.tickets = list()

        DBSession.add(event1)

        event2 = SejCancelEvent()
        event2.available = 1
        event2.shop_id = u'30520'
        event2.event_code_01  = u'EPZED'
        event2.event_code_02  = u'0709B'
        event2.title = u'入金、払戻用興行'
        event2.sub_title = u'入金、払戻用公演'
        event2.event_at = datetime.datetime(2012,8,31,18,00)
        event2.start_at = datetime.datetime(2012,6,7,18,30)
        event2.end_at = datetime.datetime(2012,6,10,18,30)
        event2.event_expire_at = datetime.datetime(2012,6,10,18,30)
        event2.ticket_expire_at = datetime.datetime(2012,7,10,18,30)
        event2.refund_enabled = 1
        event2.disapproval_reason = None
        event2.need_stub = 1
        event2.remarks = u'備考'
        event2.un_use_01 = u''
        event2.un_use_02 = u''
        event2.un_use_03 = u''
        event2.un_use_04 = u''
        event2.un_use_05 = u''

        event2.tickets = list()

        DBSession.add(event2)

        event3 = SejCancelEvent()
        event3.available = 1
        event3.shop_id = u'30520'
        event3.event_code_01  = u'EPZED'
        event3.event_code_02  = u'0709C'
        event3.title = u'入金、払戻用興行'
        event3.sub_title = u'入金、払戻用公演'
        event3.event_at = datetime.datetime(2012,8,31,18,00)
        event3.start_at = datetime.datetime(2012,6,7,18,30)
        event3.end_at = datetime.datetime(2012,6,10,18,30)
        event3.event_expire_at = datetime.datetime(2012,6,10,18,30)
        event3.ticket_expire_at = datetime.datetime(2012,7,10,18,30)
        event3.refund_enabled = 1
        event3.disapproval_reason = None
        event3.need_stub = 1
        event3.remarks = u'備考'
        event3.un_use_01 = u''
        event3.un_use_02 = u''
        event3.un_use_03 = u''
        event3.un_use_04 = u''
        event3.un_use_05 = u''

        event3.tickets = list()

        DBSession.add(event2)

        ticket = SejCancelTicket()
        ticket.available = 1
        ticket.shop_id = u'30520'
        ticket.event_code_01  = u'EPZED'
        ticket.event_code_02  = u'0709A'
        ticket.order_id  = u'120607195249'
        ticket.ticket_barcode_number = u'6200004507473'
        ticket.refund_ticket_amount = 13000
        ticket.refund_amount = 1000
        DBSession.add(ticket)
        event1.tickets.append(ticket)

        ticket = SejCancelTicket()
        ticket.available = 1
        ticket.shop_id = u'30520'
        ticket.event_code_01  = u'EPZED'
        ticket.event_code_02  = u'0709B'
        ticket.order_id  = u'120607195250'
        ticket.ticket_barcode_number = u'6200004507480'
        ticket.refund_ticket_amount = 13000
        ticket.refund_amount = 1000
        DBSession.add(ticket)
        event2.tickets.append(ticket)

        ticket = SejCancelTicket()
        ticket.available = 1
        ticket.shop_id = u'30520'
        ticket.event_code_01  = u'EPZED'
        ticket.event_code_02  = u'0709A'
        ticket.order_id  = u'120607200334'
        ticket.ticket_barcode_number = u'6200004507497'
        ticket.refund_ticket_amount = 13000
        ticket.refund_amount = 1000
        DBSession.add(ticket)
        event3.tickets.append(ticket)

        DBSession.flush()


        request_cancel_event([event1, event2, event3])
if __name__ == u"__main__":
    import os
    print os.getpid()
    unittest.main()