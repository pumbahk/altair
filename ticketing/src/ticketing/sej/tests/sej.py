# -*- coding:utf-8 -*-
import unittest
import datetime

from ticketing.sej.payment import SejPayment, SejPaymentType, SejTicketType, SejOrderUpdateReason, request_order, request_cancel
from ticketing.sej.models import SejTicket

class SejTest(unittest.TestCase):

    def _getTarget(self):
        import webapi
        return webapi.DummyServer

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def setUp(self):

        import sqlahelper
        from sqlalchemy import create_engine
        engine = create_engine("sqlite:///")
        sqlahelper.get_session().remove()
        sqlahelper.add_engine(engine)
        Base = sqlahelper.get_base()
        Base.metadata.create_all()

    def tearDown(self):
        pass

    def test_request_order_cancel(self):

        import webob.util
        webob.util.status_reasons[800] = 'OK'

        target = self._makeOne(lambda environ: '<SENBDATA>DATA=END</SENBDATA>', host='127.0.0.1', port=18002, status=800)
        target.start()

        sejTicket = SejTicket()

        sejTicket.shori_kbn     = SejOrderUpdateReason.Change.v
        sejTicket.haraikomi_no  = u'00000001'
        sejTicket.ticket_count  = 1
        sejTicket.url_info      = u'https://www.r1test.com/order/hi.do&iraihyo_id_00=11111111'
        sejTicket.order_id      = u'orderid00001'
        sejTicket.iraihyo_id_00 = u'11111111'
        sejTicket.order_at      = datetime.datetime.now()

        import sqlahelper

        DBSession = sqlahelper.get_session()
        DBSession.add(sejTicket)
        DBSession.flush()

        request_cancel(
            order_id=u'orderid00001',
            haraikomi_no=u'00000001',
            hostname=u"http://127.0.0.1:18002"
        )

        target.assert_body('X_shop_id=30520&xcode=1e1aae52c33a8f53ae3e00f76a25301f&X_haraikomi_no=00000001&X_shop_order_id=orderid00001')
        target.assert_method('POST')
        target.assert_url('http://127.0.0.1:18002/order/cancelorder.do')

        sejTicket = SejTicket.query.filter_by(order_id = u'orderid00001', haraikomi_no=u'00000001').one()

        assert sejTicket.cancel_at is not None

    def test_request_order(self):

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

        import webob.util
        webob.util.status_reasons[800] = 'OK'
        target = self._makeOne(sej_dummy_response, host='127.0.0.1', port=18001, status=800)
        target.start()

        sejTicketOrder = request_order(
            shop_name       = u'楽天チケット',
            contact_01      = u'contact',
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
            ticketing_sub_due_datetime = datetime.datetime(2012,7,30,7,00), # u'201207300700',

            hostname=u"http://127.0.0.1:18001",

            tickets = [
                dict(
                    ticket_type         = SejTicketType.TicketWithBarcode,
                    event_name          = u'イベント名',
                    performance_name    = u'パフォーマンス名',
                    ticket_template_id  = u'TTTS000001',
                    performance_datetime= datetime.datetime(2012,8,31,18,00),
                    xml = u'''<?xml version="1.0" encoding="Shift_JIS" ?>
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
                    xml = u'''<?xml version="1.0" encoding="Shift_JIS" ?>
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
                    xml = u'''<?xml version="1.0" encoding="Shift_JIS" ?>
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
                )
            ]
        )

        target.assert_method('POST')
        target.assert_url('http://127.0.0.1:18001/order/order.do')

        sejTicket = SejTicket.query.filter_by(order_id = u'orderid00001', haraikomi_no=u'0000000001').one()

        assert sejTicket is not None
        assert sejTicket.ticket_count == 3
        assert sejTicket.ticket_hon_count == 2
        assert sejTicket.iraihyo_id_00 == u'11111111'
        assert sejTicket.url_info == u'https://www.r1test.com/order/hi.do'

if __name__ == u"__main__":
    unittest.main()