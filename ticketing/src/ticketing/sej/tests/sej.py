# -*- coding:utf-8 -*-
import unittest
import datetime

from ticketing.sej.payment import SejTicketDataXml

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

    def test_file_payment(self):
        ''' 入金速報:SEITIS91_30516_20110912
        '''
        import os
        from ticketing.sej.file import SejInstantPaymentFileParser
        body = open(os.path.dirname(__file__)+ '/data/SEITIS91_30516_20110912', 'r').read()
        parser = SejInstantPaymentFileParser()
        data = parser.parse(body)
        for row in data:
            assert row['notification_type'] == 91
            assert row['payment_type'] == 1 or row['payment_type'] == 2 or \
                    row['payment_type'] == 3 or row['payment_type'] == 4
        assert len(data) == 27

    def test_file_payemnt_expire(self):
        '''支払期限切れ:SEITIS51_30516_20110912'''
        import os
        from ticketing.sej.file import SejExpiredFileParser
        body = open(os.path.dirname(__file__)+ '/data/SEITIS51_30516_20110912', 'r').read()
        parser = SejExpiredFileParser()
        data = parser.parse(body)
        for row in data:
            assert row['notification_type'] == 51
        assert len(data) == 2

    def test_file_ticketing_expire(self):
        '''発券期限切れ:SEITIS61_30516_201109122'''
        import os
        from ticketing.sej.file import SejExpiredFileParser
        body = open(os.path.dirname(__file__)+ '/data/SEITIS61_30516_20110912', 'r').read()
        parser = SejExpiredFileParser()
        data = parser.parse(body)
        for row in data:
            assert row['notification_type'] == 61
        assert len(data) == 1

    def test_file_refund(self):
        '''払戻速報:SEITIS92_30516_20110914'''
        import os
        from ticketing.sej.file import SejRefundFileParser
        body = open(os.path.dirname(__file__)+ '/data/SEITIS92_30516_20110914', 'r').read()
        parser = SejRefundFileParser()
        data = parser.parse(body)
        for row in data:
            assert row['notification_type'] == 92
        assert len(data) == 4

    def test_file_payment_info(self):
        '''支払い案内:SEITIS94_30516_20111008'''
        import os
        from ticketing.sej.file import SejPaymentInfoFileParser
        body = open(os.path.dirname(__file__)+ '/data/SEITIS94_30516_20111008', 'r').read()
        parser = SejPaymentInfoFileParser()
        data = parser.parse(body)
        for row in data:
            assert row['notification_type'] == 94
        assert len(data) == 30

    def test_file_check_cancel_pay(self):
        '''□会計取消（入金）:SEITIS95_30516_20110915'''
        import os
        from ticketing.sej.file import SejCheckFileParser
        body = open(os.path.dirname(__file__)+ '/data/SEITIS95_30516_20110915', 'r').read()
        parser = SejCheckFileParser()
        data = parser.parse(body)
        for row in data:
            assert row['notification_type'] == 95

        assert len(data) == 3

    def test_file_check_cancel_ticketing(self):
        '''□会計取消（発券）:SEITIS96_30516_20110915'''
        import os
        from ticketing.sej.file import SejCheckFileParser
        body = open(os.path.dirname(__file__)+ '/data/SEITIS96_30516_20110915', 'r').read()
        parser = SejCheckFileParser()
        data = parser.parse(body)
        for row in data:
            assert row['notification_type'] == 96

        assert len(data) == 2

    def test_file_refund_commit(self):
        '''□払戻確定:SEITIS97_30516_20110916'''
        import os
        from ticketing.sej.file import SejRefundFileParser
        body = open(os.path.dirname(__file__)+ '/data/SEITIS97_30516_20110916', 'r').read()
        parser = SejRefundFileParser()
        data = parser.parse(body)
        for row in data:
            assert row['notification_type'] == 97
        assert len(data) == 3

    def test_file_refund_cancel(self):
        '''□払戻取消:SEITIS98_30516_20110916'''
        import os
        from ticketing.sej.file import SejRefundFileParser
        body = open(os.path.dirname(__file__)+ '/data/SEITIS98_30516_20110916', 'r').read()
        parser = SejRefundFileParser()
        data = parser.parse(body)
        for row in data:
            assert row['notification_type'] == 98

        assert len(data) == 1

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
        sejOrder.exchange_sheet_url    = u'https://www.r1test.com/order/hi.do&iraihyo_id_00=11111111'
        sejOrder.order_id              = u'orderid00001'
        sejOrder.exchange_sheet_number = u'11111111'
        sejOrder.exchange_number       = u'22222222'
        sejOrder.order_at              = datetime.datetime.now()

        DBSession = sqlahelper.get_session()
        DBSession.add(sejOrder)
        DBSession.flush()

        m_dict = MultiDict()
        m_dict.add(u'X_shori_id', u'123456789012')
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

        assert int(n.payment_type )         == SejPaymentType.CashOnDelivery.v

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
        m_dict.add(u'X_shori_id', u'123456789012')
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

        assert n.process_number == u'123456789012'
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
        assert n.processed_at          == datetime.datetime(2012,7,1,8,11,00)

    def test_request_order_cancel(self):
        '''2-3.注文キャンセル'''
        from ticketing.sej.models import SejOrder
        from ticketing.sej.payment import SejOrderUpdateReason, request_cancel_order

        import webob.util
        webob.util.status_reasons[800] = 'OK'

        target = self._makeOne(lambda environ: '<SENBDATA>DATA=END</SENBDATA>', host='127.0.0.1', port=18002, status=800)
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
            hostname=u"http://127.0.0.1:18002"
        )

        target.assert_method('POST')
        target.assert_url('http://127.0.0.1:18002/order/cancelorder.do')

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
                'X_ticket_hon_cnt=%(ticket_num)02d&</SENBDATA>' + \
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
        target = self._makeOne(sej_dummy_response, host='127.0.0.1', port=18001, status=800)
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

            hostname=u"http://127.0.0.1:18001",

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
        target.assert_url('http://127.0.0.1:18001/order/order.do')

        order = SejOrder.query.filter_by(order_id = u'orderid00001', billing_number=u'0000000001').one()

        assert order is not None
        assert order.total_ticket_count == 3
        assert order.ticket_count == 2
        assert order.exchange_sheet_number == u'11111111'
        assert order.billing_number == u'0000000001'
        assert order.exchange_sheet_url == u'https://www.r1test.com/order/hi.do'

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
            'X_ticket_hon_cnt=%(ticket_num)02d&</SENBDATA>' + \
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
        target = self._makeOne(sej_dummy_response, host='127.0.0.1', port=18001, status=800)
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

             hostname=u"http://127.0.0.1:18001",

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
        target.assert_url('http://127.0.0.1:18001/order/order.do')

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

    def test_request_order_cancel(self):

        import webob.util
        import sqlahelper
        from ticketing.sej.models import SejOrder
        from ticketing.sej.payment import SejOrderUpdateReason, request_cancel_order
        webob.util.status_reasons[800] = 'OK'

        target = self._makeOne(lambda environ: '<SENBDATA>DATA=END</SENBDATA>', host='127.0.0.1', port=18002, status=800)
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
            hostname=u"http://127.0.0.1:18002"
        )

        target.assert_body('X_shop_id=30520&xcode=cf0fe9fc34300dd1f946e6c9c33fc020&X_hikikae_no=00001111&X_haraikomi_no=00000001&X_shop_order_id=orderid00001')
        target.assert_method('POST')
        target.assert_url('http://127.0.0.1:18002/order/cancelorder.do')

        sej_order = SejOrder.query.filter_by(order_id = u'orderid00001', billing_number=u'00000001').one()
        assert sej_order.cancel_at is not None

if __name__ == u"__main__":
    import os
    print os.getpid()
    unittest.main()