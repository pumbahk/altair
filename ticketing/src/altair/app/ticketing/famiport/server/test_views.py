# -*- coding: utf-8 -*-
from unittest import TestCase, skip
import mock
from lxml import etree
from decimal import Decimal
from pyramid.testing import (
    DummyModel,
    )
from ..testing import (
    _setup_db,
    _teardown_db,
    )
from altair.sqlahelper import get_global_db_session


class FamiPortAPIViewTest(TestCase):
    settings = {
        'altair.famiport.send_file.ftp.host': 'localhost',
        'altair.famiport.send_file.ftp.port': '',
        'altair.famiport.send_file.ftp.username': '',
        'altair.famiport.send_file.ftp.password': '',
        'altair.famiport.refund.stage.dir': '',
        'altair.famiport.refund.pending.dir': '',
        'altair.famiport.refund.sent.dir': '',
        'altair.famiport.sales.stage.dir': '',
        'altair.famiport.sales.pending.dir': '',
        'altair.famiport.sales.sent.dir': '',
        'altair.famiport.order_status_reflector.endpoint.completed': '',
        'altair.famiport.order_status_reflector.endpoint.canceled': '',
        'altair.famiport.order_status_reflector.endpoint.refunded': '',
        'altair.famiport.order_status_reflector.endpoint.expired': '',
        }

    def setUp(self):
        from webtest import TestApp
        from pyramid.config import Configurator
        self.config = Configurator(settings=self.settings)
        self.engine = _setup_db(
            self.config.registry,
            [
                'altair.app.ticketing.famiport.models',
                'altair.app.ticketing.famiport.communication.models',
                ]
            )
        self.session = get_global_db_session(self.config.registry, 'famiport')
        self.config.include('.', '/famiport/')
        self.config.include('..communication')

        extra_environ = {'HTTP_HOST': 'localhost:8063'}
        self.app = TestApp(self.config.make_wsgi_app(), extra_environ=extra_environ)

    def tearDown(self):
        _teardown_db(self.config)

    def _callFUT(self, *args, **kwds):
        return self.app.post(self.url, *args, **kwds)

    def _check_payload(self, res, exp, famiport_response_class=None):
        res_elms = dict((elm.tag, elm) for elm in res.xpath('*'))
        exp_elms = dict((elm.tag, elm) for elm in exp.xpath('*'))

        def _strip(value):
            return (value.strip() or None) if hasattr(value, 'strip') else value

        for tag, exp_elm in exp_elms.items():
            self.assertIn(tag, res_elms)
            res_elm = res_elms[tag]

            if tag in ['ticketData']:  # orz skip
                continue

            if famiport_response_class \
               and tag in famiport_response_class._encryptedFields:
                self.assertEqual(bool(res_elm.text), bool(exp_elm.text))
            else:
                self.assertEqual(
                    _strip(res_elm.text), _strip(exp_elm.text),
                    u'tag={}, res={}, exp={}\nXML:\n{}'.format(
                        tag, res_elm.text, exp_elm.text, etree.tostring(res)))


class InquiryTest(FamiPortAPIViewTest):
    """
    request
    authNumber=&reserveNumber=5300000000001&ticketingDate=20150325151159&storeCode=000009&

    response
<?xml version="1.0" encoding="Shift_JIS"?>
<FMIF>
<resultCode>00</resultCode>
<replyClass>1</replyClass>
<replyCode>00</replyCode>
<barCodeNo>4110000000006</barCodeNo>
<totalAmount>00000670</totalAmount>
<ticketPayment>00000000</ticketPayment>
<systemFee>00000500</systemFee>
<ticketingFee>00000170</ticketingFee>
<ticketCountTotal>1</ticketCountTotal>
<ticketCount>1</ticketCount>
<kogyoName>サンプル興行</kogyoName>
<koenDate>201505011000</koenDate>
<nameInput>0</nameInput>
<phoneInput>0</phoneInput>
</FMIF>
    """
    url = '/famiport/reservation/inquiry'

    @mock.patch('altair.app.ticketing.famiport.models.FamiPortOrderTicketNoSequence.get_next_value')
    @mock.patch('altair.app.ticketing.famiport.models.FamiPortReceipt.get_by_reserve_number')
    def test_it(self, get_by_reserve_number, get_next_value):
        from ..testing import FamiPortReservationInquiryResponseFakeFactory as FakeFactory
        from datetime import datetime
        from ..testing import generate_ticket_data
        from ..models import FamiPortTicket, FamiPortReceiptType, FamiPortReceipt, FamiPortOrder, FamiPortPerformance, FamiPortSalesSegment, FamiPortClient, FamiPortPlayguide, FamiPortEvent, FamiPortVenue
        from ..communication import FamiPortReservationInquiryResponse as FamiPortResponse
        famiport_tickets = [
            FamiPortTicket(
                barcode_number=ticket['barCodeNo'],
                type=ticket['ticketClass'],
                template_code=ticket['templateCode'],
                data=ticket['ticketData'],
            ) for ticket in list(generate_ticket_data())[:1]]

        get_next_value.return_value = u'4110000000006'
        payment_start_at = datetime(2015, 3, 24, 0, 0, 0)
        payment_due_at = datetime(2015, 3, 31, 17, 25, 55)
        ticketing_start_at = datetime(2015, 3, 31, 17, 25, 53)
        ticketing_end_at = datetime(2015, 3, 31, 17, 25, 55)
        performance_start_at = datetime(2015, 5, 1, 10, 0)

        famiport_client = FamiPortClient(
            code=u'00001',
            name=u'クライアント１',
            prefix=u'000',
            playguide=FamiPortPlayguide(discrimination_code=5, discrimination_code_2=4)
            )
        famiport_performance = FamiPortPerformance(
            name=u'サンプル興行',
            start_at=performance_start_at,
            code=u'000',
            famiport_event=FamiPortEvent(
                venue=FamiPortVenue(name=u'', name_kana=u'', client_code=famiport_client.code),
                client=famiport_client,
                code_1=u'00000',
                code_2=u'000',
                )
            )
        get_by_reserve_number.return_value = FamiPortReceipt(
            type=FamiPortReceiptType.CashOnDelivery.value,
            shop_code='99999',
            completed_at=None,
            void_at=None,
            barcode_no=u'4110000000006',
            famiport_order_identifier=u'430000000002',
            mark_inquired=lambda *args: None,
            made_reissueable_at=None,
            famiport_order=FamiPortOrder(
                order_no=u'XX0000000000',
                famiport_order_identifier=u'000000000000',
                customer_name=u'楽天太郎',
                customer_phone_number=u'',
                type=1,
                payment_start_at=payment_start_at,
                payment_due_at=payment_due_at,
                paid_at=None,
                issued_at=None,
                ticketing_start_at=ticketing_start_at,
                ticketing_end_at=ticketing_end_at,
                total_amount=670,
                ticket_payment=0,
                system_fee=500,
                ticketing_fee=170,
                famiport_tickets=famiport_tickets,
                customer_name_input=0,
                customer_phone_input=0,
                auth_number=u'',
                famiport_performance=famiport_performance,
                famiport_sales_segment=FamiPortSalesSegment(
                    code=u'000',
                    start_at=datetime(2015, 1, 1),
                    end_at=datetime(2015, 1, 1),
                    famiport_performance=famiport_performance
                    ),
                famiport_client=famiport_client,
                )
            )

        res = self._callFUT({
            'authNumber': u'',
            'reserveNumber': u'5300000000001',
            'ticketingDate': u'20150325151159',
            'storeCode': u'099999',
            })
        self.assertEqual(200, res.status_code)
        self._check_payload(
            FakeFactory.parse(res.body.decode('cp932')),
            FakeFactory.create(),
            FamiPortResponse,
            )


class PaymentTest(FamiPortAPIViewTest):
    """
    request
    ticketingDate=20150331172554&playGuideId=&phoneNumber=rfanmRgUZFRRephCwOsgbg%3d%3d&customerName=pT6fj7ULQklIfOWBKGyQ6g%3d%3d&mmkNo=01&barCodeNo=1000000000000&sequenceNo=15033100002&storeCode=000009&

    response
<?xml version="1.0" encoding="Shift_JIS"?>
<FMIF>
<resultCode>00</resultCode>
<storeCode>99999</storeCode>
<sequenceNo>12345678901</sequenceNo>
<barCodeNo>4310000000002</barCodeNo>
<orderId>430000000002</orderId>
<replyClass>3</replyClass>
<replyCode>00</replyCode>
<playGuideId>00001</playGuideId>
<playGuideName>クライアント１</playGuideName>
<exchangeTicketNo>4310000000002</exchangeTicketNo>
<totalAmount>00000200</totalAmount>
<ticketPayment>00000000</ticketPayment>
<systemFee>00000000</systemFee>
<ticketingFee>00000200</ticketingFee>
<ticketCountTotal>5</ticketCountTotal>
<ticketCount>5</ticketCount>
<kogyoName>ａｂｃｄｅｆｇｈｉｊ１２３４５６７８９０</kogyoName>
<koenDate>999999999999</koenDate>
<ticket>
<barCodeNo>1234567890019</barCodeNo>
<ticketClass>1</ticketClass>
<templateCode>TTEVEN0001</templateCode>
<ticketData>&lt;?xml version=&apos;1.0&apos; encoding=&apos;Shift_JIS&apos; ?&gt;&lt;ticket&gt;&lt;TitleOver&gt;まるばつさんかくこうえん　いん　せいぶどーむ　２０１２&lt;/TitleOver&gt;&lt;TitleMain&gt;○×△公演　〜in 西武ドーム〜　２０１２&lt;/TitleMain&gt;&lt;TitleSub&gt;※※※※※　サブタイトル　※※※※※&lt;/TitleSub&gt;&lt;FreeSpace1&gt;あいうえおかきくけこ１２３４５６７８９０一二三四五六七八九十あいうえおかきくけこ１２３４５６７８９０&lt;/FreeSpace1&gt;&lt;FreeSpace2&gt;あいうえおかきくけこ１２３４５６７８９０一二三四五六七八九十あいうえおかきくけこ１２３４５６７８９０&lt;/FreeSpace2&gt;&lt;Date&gt;2012年8月10日&lt;/Date&gt;&lt;OpenTime&gt;14:30開場&lt;/OpenTime&gt;&lt;StartTime&gt;15:00開演&lt;/StartTime&gt;&lt;Price&gt;\30,000&lt;/Price&gt;&lt;Hall&gt;西武ドーム（埼玉県所沢市）&lt;/Hall&gt;&lt;Note1&gt;※主催：　ファミマ・ドット・コム&lt;/Note1&gt;&lt;Note2&gt;※協賛：　ファミマ・ドット・コム&lt;/Note2&gt;&lt;Note3&gt;※協力：　ファミマ・ドット・コム&lt;/Note3&gt;&lt;Note4&gt;※お問合せ：　ファミマ・ドット・コム窓口&lt;/Note4&gt;&lt;Note5&gt;　平日：　9:00〜20:00&lt;/Note5&gt;&lt;Note6&gt;　祝日：　10:00〜17:00&lt;/Note6&gt;&lt;Note7&gt;&lt;/Note7&gt;&lt;Seat1&gt;１塁側&lt;/Seat1&gt;&lt;Seat2&gt;内野席A&lt;/Seat2&gt;&lt;Seat3&gt;２２段&lt;/Seat3&gt;&lt;Seat4&gt;２２８&lt;/Seat4&gt;&lt;Seat5&gt;※招待席&lt;/Seat5&gt;&lt;Sub-Title1&gt;○×△公演&lt;/Sub-Title1&gt;&lt;Sub-Title2&gt;〜in 西武ドーム〜&lt;/Sub-Title2&gt;&lt;Sub-Title3&gt;２０１２&lt;/Sub-Title3&gt;&lt;Sub-Title4&gt;&lt;/Sub-Title4&gt;&lt;Sub-Title5&gt;&lt;/Sub-Title5&gt;&lt;Sub-Date&gt;2012年8月10日&lt;/Sub-Date&gt;&lt;Sub-OpenTime&gt;14:30開場&lt;/Sub-OpenTime&gt;&lt;Sub-StartTime&gt;15:00開演&lt;/Sub-StartTime&gt;&lt;Sub-Price&gt;\30,000&lt;/Sub-Price&gt;&lt;Sub-Seat1&gt;１塁側&lt;/Sub-Seat1&gt;&lt;Sub-Seat2&gt;内野席A&lt;/Sub-Seat2&gt;&lt;Sub-Seat3&gt;２２段&lt;/Sub-Seat3&gt;&lt;Sub-Seat4&gt;２２８&lt;/Sub-Seat4&gt;&lt;Sub-Seat5&gt;※招待席&lt;/Sub-Seat5&gt;&lt;/ticket&gt;</ticketData>
</ticket>
<ticket>
<barCodeNo>1234567890026</barCodeNo>
<ticketClass>1</ticketClass>
<templateCode>TTEVEN0001</templateCode>
<ticketData>&lt;?xml version=&apos;1.0&apos; encoding=&apos;Shift_JIS&apos; ?&gt;&lt;ticket&gt;&lt;TitleOver&gt;まるばつさんかくこうえん　いん　せいぶどーむ　２０１２&lt;/TitleOver&gt;&lt;TitleMain&gt;○×△公演　〜in 西武ドーム〜　２０１２&lt;/TitleMain&gt;&lt;TitleSub&gt;※※※※※　サブタイトル　※※※※※&lt;/TitleSub&gt;&lt;FreeSpace1&gt;あいうえおかきくけこ１２３４５６７８９０一二三四五六七八九十あいうえおかきくけこ１２３４５６７８９０&lt;/FreeSpace1&gt;&lt;FreeSpace2&gt;あいうえおかきくけこ１２３４５６７８９０一二三四五六七八九十あいうえおかきくけこ１２３４５６７８９０&lt;/FreeSpace2&gt;&lt;Date&gt;2012年8月10日&lt;/Date&gt;&lt;OpenTime&gt;14:30開場&lt;/OpenTime&gt;&lt;StartTime&gt;15:00開演&lt;/StartTime&gt;&lt;Price&gt;\30,000&lt;/Price&gt;&lt;Hall&gt;西武ドーム（埼玉県所沢市）&lt;/Hall&gt;&lt;Note1&gt;※主催：　ファミマ・ドット・コム&lt;/Note1&gt;&lt;Note2&gt;※協賛：　ファミマ・ドット・コム&lt;/Note2&gt;&lt;Note3&gt;※協力：　ファミマ・ドット・コム&lt;/Note3&gt;&lt;Note4&gt;※お問合せ：　ファミマ・ドット・コム窓口&lt;/Note4&gt;&lt;Note5&gt;　平日：　9:00〜20:00&lt;/Note5&gt;&lt;Note6&gt;　祝日：　10:00〜17:00&lt;/Note6&gt;&lt;Note7&gt;&lt;/Note7&gt;&lt;Seat1&gt;１塁側&lt;/Seat1&gt;&lt;Seat2&gt;内野席A&lt;/Seat2&gt;&lt;Seat3&gt;２２段&lt;/Seat3&gt;&lt;Seat4&gt;２２８&lt;/Seat4&gt;&lt;Seat5&gt;※招待席&lt;/Seat5&gt;&lt;Sub-Title1&gt;○×△公演&lt;/Sub-Title1&gt;&lt;Sub-Title2&gt;〜in 西武ドーム〜&lt;/Sub-Title2&gt;&lt;Sub-Title3&gt;２０１２&lt;/Sub-Title3&gt;&lt;Sub-Title4&gt;&lt;/Sub-Title4&gt;&lt;Sub-Title5&gt;&lt;/Sub-Title5&gt;&lt;Sub-Date&gt;2012年8月10日&lt;/Sub-Date&gt;&lt;Sub-OpenTime&gt;14:30開場&lt;/Sub-OpenTime&gt;&lt;Sub-StartTime&gt;15:00開演&lt;/Sub-StartTime&gt;&lt;Sub-Price&gt;\30,000&lt;/Sub-Price&gt;&lt;Sub-Seat1&gt;１塁側&lt;/Sub-Seat1&gt;&lt;Sub-Seat2&gt;内野席A&lt;/Sub-Seat2&gt;&lt;Sub-Seat3&gt;２２段&lt;/Sub-Seat3&gt;&lt;Sub-Seat4&gt;２２８&lt;/Sub-Seat4&gt;&lt;Sub-Seat5&gt;※招待席&lt;/Sub-Seat5&gt;&lt;/ticket&gt;</ticketData>
</ticket>
<ticket>
<barCodeNo>1234567890033</barCodeNo>
<ticketClass>1</ticketClass>
<templateCode>TTEVEN0001</templateCode>
<ticketData>&lt;?xml version=&apos;1.0&apos; encoding=&apos;Shift_JIS&apos; ?&gt;&lt;ticket&gt;&lt;TitleOver&gt;まるばつさんかくこうえん　いん　せいぶどーむ　２０１２&lt;/TitleOver&gt;&lt;TitleMain&gt;○×△公演　〜in 西武ドーム〜　２０１２&lt;/TitleMain&gt;&lt;TitleSub&gt;※※※※※　サブタイトル　※※※※※&lt;/TitleSub&gt;&lt;FreeSpace1&gt;あいうえおかきくけこ１２３４５６７８９０一二三四五六七八九十あいうえおかきくけこ１２３４５６７８９０&lt;/FreeSpace1&gt;&lt;FreeSpace2&gt;あいうえおかきくけこ１２３４５６７８９０一二三四五六七八九十あいうえおかきくけこ１２３４５６７８９０&lt;/FreeSpace2&gt;&lt;Date&gt;2012年8月10日&lt;/Date&gt;&lt;OpenTime&gt;14:30開場&lt;/OpenTime&gt;&lt;StartTime&gt;15:00開演&lt;/StartTime&gt;&lt;Price&gt;\30,000&lt;/Price&gt;&lt;Hall&gt;西武ドーム（埼玉県所沢市）&lt;/Hall&gt;&lt;Note1&gt;※主催：　ファミマ・ドット・コム&lt;/Note1&gt;&lt;Note2&gt;※協賛：　ファミマ・ドット・コム&lt;/Note2&gt;&lt;Note3&gt;※協力：　ファミマ・ドット・コム&lt;/Note3&gt;&lt;Note4&gt;※お問合せ：　ファミマ・ドット・コム窓口&lt;/Note4&gt;&lt;Note5&gt;　平日：　9:00〜20:00&lt;/Note5&gt;&lt;Note6&gt;　祝日：　10:00〜17:00&lt;/Note6&gt;&lt;Note7&gt;&lt;/Note7&gt;&lt;Seat1&gt;１塁側&lt;/Seat1&gt;&lt;Seat2&gt;内野席A&lt;/Seat2&gt;&lt;Seat3&gt;２２段&lt;/Seat3&gt;&lt;Seat4&gt;２２８&lt;/Seat4&gt;&lt;Seat5&gt;※招待席&lt;/Seat5&gt;&lt;Sub-Title1&gt;○×△公演&lt;/Sub-Title1&gt;&lt;Sub-Title2&gt;〜in 西武ドーム〜&lt;/Sub-Title2&gt;&lt;Sub-Title3&gt;２０１２&lt;/Sub-Title3&gt;&lt;Sub-Title4&gt;&lt;/Sub-Title4&gt;&lt;Sub-Title5&gt;&lt;/Sub-Title5&gt;&lt;Sub-Date&gt;2012年8月10日&lt;/Sub-Date&gt;&lt;Sub-OpenTime&gt;14:30開場&lt;/Sub-OpenTime&gt;&lt;Sub-StartTime&gt;15:00開演&lt;/Sub-StartTime&gt;&lt;Sub-Price&gt;\30,000&lt;/Sub-Price&gt;&lt;Sub-Seat1&gt;１塁側&lt;/Sub-Seat1&gt;&lt;Sub-Seat2&gt;内野席A&lt;/Sub-Seat2&gt;&lt;Sub-Seat3&gt;２２段&lt;/Sub-Seat3&gt;&lt;Sub-Seat4&gt;２２８&lt;/Sub-Seat4&gt;&lt;Sub-Seat5&gt;※招待席&lt;/Sub-Seat5&gt;&lt;/ticket&gt;</ticketData>
</ticket>
<ticket>
<barCodeNo>1234567890040</barCodeNo>
<ticketClass>1</ticketClass>
<templateCode>TTEVEN0001</templateCode>
<ticketData>&lt;?xml version=&apos;1.0&apos; encoding=&apos;Shift_JIS&apos; ?&gt;&lt;ticket&gt;&lt;TitleOver&gt;まるばつさんかくこうえん　いん　せいぶどーむ　２０１２&lt;/TitleOver&gt;&lt;TitleMain&gt;○×△公演　〜in 西武ドーム〜　２０１２&lt;/TitleMain&gt;&lt;TitleSub&gt;※※※※※　サブタイトル　※※※※※&lt;/TitleSub&gt;&lt;FreeSpace1&gt;あいうえおかきくけこ１２３４５６７８９０一二三四五六七八九十あいうえおかきくけこ１２３４５６７８９０&lt;/FreeSpace1&gt;&lt;FreeSpace2&gt;あいうえおかきくけこ１２３４５６７８９０一二三四五六七八九十あいうえおかきくけこ１２３４５６７８９０&lt;/FreeSpace2&gt;&lt;Date&gt;2012年8月10日&lt;/Date&gt;&lt;OpenTime&gt;14:30開場&lt;/OpenTime&gt;&lt;StartTime&gt;15:00開演&lt;/StartTime&gt;&lt;Price&gt;\30,000&lt;/Price&gt;&lt;Hall&gt;西武ドーム（埼玉県所沢市）&lt;/Hall&gt;&lt;Note1&gt;※主催：　ファミマ・ドット・コム&lt;/Note1&gt;&lt;Note2&gt;※協賛：　ファミマ・ドット・コム&lt;/Note2&gt;&lt;Note3&gt;※協力：　ファミマ・ドット・コム&lt;/Note3&gt;&lt;Note4&gt;※お問合せ：　ファミマ・ドット・コム窓口&lt;/Note4&gt;&lt;Note5&gt;　平日：　9:00〜20:00&lt;/Note5&gt;&lt;Note6&gt;　祝日：　10:00〜17:00&lt;/Note6&gt;&lt;Note7&gt;&lt;/Note7&gt;&lt;Seat1&gt;１塁側&lt;/Seat1&gt;&lt;Seat2&gt;内野席A&lt;/Seat2&gt;&lt;Seat3&gt;２２段&lt;/Seat3&gt;&lt;Seat4&gt;２２８&lt;/Seat4&gt;&lt;Seat5&gt;※招待席&lt;/Seat5&gt;&lt;Sub-Title1&gt;○×△公演&lt;/Sub-Title1&gt;&lt;Sub-Title2&gt;〜in 西武ドーム〜&lt;/Sub-Title2&gt;&lt;Sub-Title3&gt;２０１２&lt;/Sub-Title3&gt;&lt;Sub-Title4&gt;&lt;/Sub-Title4&gt;&lt;Sub-Title5&gt;&lt;/Sub-Title5&gt;&lt;Sub-Date&gt;2012年8月10日&lt;/Sub-Date&gt;&lt;Sub-OpenTime&gt;14:30開場&lt;/Sub-OpenTime&gt;&lt;Sub-StartTime&gt;15:00開演&lt;/Sub-StartTime&gt;&lt;Sub-Price&gt;\30,000&lt;/Sub-Price&gt;&lt;Sub-Seat1&gt;１塁側&lt;/Sub-Seat1&gt;&lt;Sub-Seat2&gt;内野席A&lt;/Sub-Seat2&gt;&lt;Sub-Seat3&gt;２２段&lt;/Sub-Seat3&gt;&lt;Sub-Seat4&gt;２２８&lt;/Sub-Seat4&gt;&lt;Sub-Seat5&gt;※招待席&lt;/Sub-Seat5&gt;&lt;/ticket&gt;</ticketData>
</ticket>
<ticket>
<barCodeNo>1234567890057</barCodeNo>
<ticketClass>1</ticketClass>
<templateCode>TTEVEN0001</templateCode>
<ticketData>&lt;?xml version=&apos;1.0&apos; encoding=&apos;Shift_JIS&apos; ?&gt;&lt;ticket&gt;&lt;TitleOver&gt;まるばつさんかくこうえん　いん　せいぶどーむ　２０１２&lt;/TitleOver&gt;&lt;TitleMain&gt;○×△公演　〜in 西武ドーム〜　２０１２&lt;/TitleMain&gt;&lt;TitleSub&gt;※※※※※　サブタイトル　※※※※※&lt;/TitleSub&gt;&lt;FreeSpace1&gt;あいうえおかきくけこ１２３４５６７８９０一二三四五六七八九十あいうえおかきくけこ１２３４５６７８９０&lt;/FreeSpace1&gt;&lt;FreeSpace2&gt;あいうえおかきくけこ１２３４５６７８９０一二三四五六七八九十あいうえおかきくけこ１２３４５６７８９０&lt;/FreeSpace2&gt;&lt;Date&gt;2012年8月10日&lt;/Date&gt;&lt;OpenTime&gt;14:30開場&lt;/OpenTime&gt;&lt;StartTime&gt;15:00開演&lt;/StartTime&gt;&lt;Price&gt;\30,000&lt;/Price&gt;&lt;Hall&gt;西武ドーム（埼玉県所沢市）&lt;/Hall&gt;&lt;Note1&gt;※主催：　ファミマ・ドット・コム&lt;/Note1&gt;&lt;Note2&gt;※協賛：　ファミマ・ドット・コム&lt;/Note2&gt;&lt;Note3&gt;※協力：　ファミマ・ドット・コム&lt;/Note3&gt;&lt;Note4&gt;※お問合せ：　ファミマ・ドット・コム窓口&lt;/Note4&gt;&lt;Note5&gt;　平日：　9:00〜20:00&lt;/Note5&gt;&lt;Note6&gt;　祝日：　10:00〜17:00&lt;/Note6&gt;&lt;Note7&gt;&lt;/Note7&gt;&lt;Seat1&gt;１塁側&lt;/Seat1&gt;&lt;Seat2&gt;内野席A&lt;/Seat2&gt;&lt;Seat3&gt;２２段&lt;/Seat3&gt;&lt;Seat4&gt;２２８&lt;/Seat4&gt;&lt;Seat5&gt;※招待席&lt;/Seat5&gt;&lt;Sub-Title1&gt;○×△公演&lt;/Sub-Title1&gt;&lt;Sub-Title2&gt;〜in 西武ドーム〜&lt;/Sub-Title2&gt;&lt;Sub-Title3&gt;２０１２&lt;/Sub-Title3&gt;&lt;Sub-Title4&gt;&lt;/Sub-Title4&gt;&lt;Sub-Title5&gt;&lt;/Sub-Title5&gt;&lt;Sub-Date&gt;2012年8月10日&lt;/Sub-Date&gt;&lt;Sub-OpenTime&gt;14:30開場&lt;/Sub-OpenTime&gt;&lt;Sub-StartTime&gt;15:00開演&lt;/Sub-StartTime&gt;&lt;Sub-Price&gt;\30,000&lt;/Sub-Price&gt;&lt;Sub-Seat1&gt;１塁側&lt;/Sub-Seat1&gt;&lt;Sub-Seat2&gt;内野席A&lt;/Sub-Seat2&gt;&lt;Sub-Seat3&gt;２２段&lt;/Sub-Seat3&gt;&lt;Sub-Seat4&gt;２２８&lt;/Sub-Seat4&gt;&lt;Sub-Seat5&gt;※招待席&lt;/Sub-Seat5&gt;&lt;/ticket&gt;</ticketData>
</ticket>
</FMIF>
    """  # noqa
    url = '/famiport/reservation/payment'

    @mock.patch('altair.app.ticketing.famiport.models.FamiPortReceipt.get_by_barcode_no')
    def test_it(self, get_by_barcode_no):
        from datetime import datetime
        from ..testing import generate_ticket_data
        from ..testing import FamiPortPaymentTicketingResponseFakeFactory as FakeFactory
        from ..models import FamiPortTicket, FamiPortReceiptType
        from ..communication import FamiPortPaymentTicketingResponse as FamiPortResponse

        famiport_tickets = [
            FamiPortTicket(
                barcode_number=ticket['barCodeNo'],
                type=ticket['ticketClass'],
                template_code=ticket['templateCode'],
                data=ticket['ticketData'],
            ) for ticket in generate_ticket_data()]

        payment_due_at = datetime(2015, 3, 31, 17, 25, 55)
        ticketing_start_at = datetime(2015, 3, 31, 17, 25, 53)
        ticketing_end_at = datetime(2015, 3, 31, 17, 25, 55)

        famiport_performance = DummyModel(
            name=u'ａｂｃｄｅｆｇｈｉｊ１２３４５６７８９０',
            start_at=None,
            )

        famiport_receipt = DummyModel(
            type=FamiPortReceiptType.Ticketing.value,
            shop_code=u'99999',
            can_payment=lambda now: True,
            completed_at=None,
            canceled_at=None,
            reserve_number=u'4310000000002',
            barcode_no=u'1000000000000',
            famiport_order_identifier=u'430000000002',
            mark_payment_request_received=lambda *args: None,
            payment_request_received_at=None,
            made_reissueable_at=None,
            calculate_total_and_fees=lambda: (Decimal(200), Decimal(0), Decimal(0), Decimal(200)),
            famiport_order=DummyModel(
                famiport_order_identifier=u'430000000001',
                type=3,
                payment_due_at=payment_due_at,
                paid_at=None,
                issued_at=None,
                ticketing_start_at=ticketing_start_at,
                ticketing_end_at=ticketing_end_at,
                barcode_number=u'1000000000000',
                total_amount=Decimal(200),
                ticket_payment=Decimal(0),
                system_fee=Decimal(0),
                ticketing_fee=Decimal(200),
                ticket_total_count=len(famiport_tickets),
                ticket_count=len(famiport_tickets),
                payment_start_at=ticketing_start_at,
                payment_end_at=ticketing_end_at,
                famiport_tickets=famiport_tickets,
                made_reissueable_at=None,
                require_ticketing_fee_on_ticketing=True,
                famiport_performance=famiport_performance,
                famiport_sales_segment=DummyModel(
                    famiport_performance=famiport_performance
                    ),
                ticketing_famiport_receipt=DummyModel(
                    reserve_number=u'4310000000002',
                    made_reissueable_at=None
                    ),
                famiport_client=DummyModel(
                    name=u'クライアント１',
                    code=u'00001',
                    )
                )
            )
        get_by_barcode_no.return_value = famiport_receipt

        res = self._callFUT({
            'ticketingDate': u'20150331172554',
            'playGuideId': u'00001',
            'phoneNumber': u'rfanmRgUZFRRephCwOsgbg%3d%3d',
            'customerName': u'pT6fj7ULQklIfOWBKGyQ6g%3d%3d',
            'mmkNo': u'01',
            'barCodeNo': u'1000000000000',
            'sequenceNo': u'12345678901',
            'storeCode': famiport_receipt.shop_code,
            })
        self.assertEqual(200, res.status_code)
        self._check_payload(
            FakeFactory.parse(res.body.decode('cp932')),
            FakeFactory.create(),
            FamiPortResponse,
            )


class CompletionTest(FamiPortAPIViewTest):
    """
    request
ticketingDate=20150331184114&orderId=123456789012&totalAmount=1000&playGuideId=&mmkNo=01&barCodeNo=1000000000000&sequenceNo=15033100010&storeCode=000009&

    response
<?xml version="1.0" encoding="Shift_JIS"?>
<FMIF>
<resultCode>00</resultCode>
<storeCode>99999</storeCode>
<sequenceNo>12345678901</sequenceNo>
<barCodeNo>6010000000000</barCodeNo>
<orderId>123456789012</orderId>
<replyCode>00</replyCode>
</FMIF>
    """

    url = '/famiport/reservation/completion'

    @mock.patch('altair.app.ticketing.famiport.models.FamiPortReceipt.get_by_barcode_no')
    def test_it(self, get_by_barcode_no):
        from ..testing import FamiPortPaymentTicketingCompletionResponseFakeFactory as FakeFactory
        from ..models import FamiPortReceiptType
        get_by_barcode_no.return_value = DummyModel(
            id=1,
            type=FamiPortReceiptType.CashOnDelivery.value,
            completed_at=None,
            shop_code=u'99999',
            reserve_number=u'0000000000000',
            can_completion=lambda now: True,
            mark_completed=lambda *args: None,
            famiport_order_identifier=u'000000000000',
            famiport_order=DummyModel(
                mark_issued=lambda *args: None,
                mark_paid=lambda *args: None
                ),
            made_reissueable_at=None
            )
        res = self._callFUT({
            'ticketingDate': '20150331184114',
            'orderId': '123456789012',
            'totalAmount': '1000',
            'playGuideId': '',
            'mmkNo': '01',
            'barCodeNo': '6010000000000',
            'sequenceNo': '12345678901',
            'storeCode': u'99999',
            })
        self.assertEqual(200, res.status_code)

        self._check_payload(
            FakeFactory.parse(res.body.decode('cp932')),
            FakeFactory.create(),
            )

    @mock.patch('altair.app.ticketing.famiport.models.FamiPortReceipt.get_by_barcode_no')
    def test_fail(self, get_by_barcode_no):
        from ..testing import FamiPortPaymentTicketingCompletionResponseFailFakeFactory as FakeFactory
        get_by_barcode_no.return_value = None
        res = self._callFUT({
            'ticketingDate': '20150331184114',
            'orderId': '123456789012',
            'totalAmount': '1000',
            'playGuideId': '',
            'mmkNo': '01',
            'barCodeNo': '6010000000000',
            'sequenceNo': '12345678901',
            'storeCode': '99999',
            })
        self.assertEqual(200, res.status_code)

        self._check_payload(
            FakeFactory.parse(res.body.decode('cp932')),
            FakeFactory.create(),
            )


class CancelTest(FamiPortAPIViewTest):
    """
    request
playGuideId=&storeCode=000009&ticketingDate=20150401101950&barCodeNo=1000000000000&sequenceNo=15040100009&mmkNo=1&orderId=123456789012&cancelCode=10&
    response
<?xml version="1.0" encoding="Shift_JIS"?>
<FMIF>
<resultCode>00</resultCode>
<storeCode>99999</storeCode>
<sequenceNo>12345678901</sequenceNo>
<barCodeNo>3300000000000</barCodeNo>
<orderId>123456789012</orderId>
<replyCode>00</replyCode>
</FMIF>
    """

    url = '/famiport/reservation/cancel'

    @mock.patch('altair.app.ticketing.famiport.models.FamiPortReceipt.get_by_barcode_no')
    def test_it(self, get_by_barcode_no):
        from ..testing import FamiPortPaymentTicketingCancelResponseFakeFactory as FakeFactory
        from ..models import FamiPortReceiptType
        from datetime import datetime
        get_by_barcode_no.return_value = DummyModel(
            type=FamiPortReceiptType.CashOnDelivery,
            famiport_order_identifier='123456789012',
            inquired_at=datetime(2015, 1, 1, 0, 0, 0),
            shop_code='99999',
            completed_at=None,
            canceled_at=None,
            void_at=None,
            barcode_no=u'1000000000000',
            mark_voided=lambda *args: None,
            famiport_order=DummyModel(
                paid_at=None,
                canceled_at=None,
                issued_at=None
                )
            )
        res = self._callFUT({
            'playGuideId': '',
            'storeCode': u'99999',
            'ticketingDate': '20150401101950',
            'barCodeNo': '1000000000000',
            'sequenceNo': '12345678901',
            'mmkNo': '1',
            'orderId': '123456789012',
            'cancelCode': '10',
            })
        self.assertEqual(200, res.status_code)

        self._check_payload(
            FakeFactory.parse(res.body.decode('cp932')),
            FakeFactory.create(),
            )


class InformationViewTest(FamiPortAPIViewTest):
    """
    request
    uketsukeCode=&kogyoSubCode=&reserveNumber=4000000000001&infoKubun=Reserve&kogyoCode=&koenCode=&authCode=&storeCode=000009&

    response
<?xml version="1.0" encoding="Shift_JIS"?>
<FMIF>
    <resultCode>00</resultCode>
    <infoKubun>0</infoKubun>
    <infoMessage>テスト1
テスト2
テスト3
テスト4
テスト5
テスト6
テスト7
テスト8
テスト9
テスト10
テスト11
テスト12
テスト13
テスト14
テスト15
テスト16
テスト17
テスト18
テスト19
テスト20
テスト21
テスト22
テスト23</infoMessage>
</FMIF>
    """
    url = '/famiport/reservation/information'

    @skip('''AssertionError: 'infoMessage' not found in {'resultCode': <Element resultCode at 0x10a155e60>, 'infoKubun': <Element infoKubun at 0x10a155a00>}''')
    def test_it(self):
        from ..testing import FamiPortInformationResponseFakeFactory as FakeFactory
        from ..models import FamiPortInformationMessage
        msg = FamiPortInformationMessage(result_code=0)
        self.session.add(msg)
        self.session.commit()

        res = self._callFUT({
            'uketsukeCode': '',
            'kogyoSubCode': '',
            'reserveNumber': '4000000000001',
            'infoKubun': '1',
            'kogyoCode': '',
            'koenCode': '',
            'authCode': '',
            'storeCode': '000009',
            })
        self.assertEqual(200, res.status_code)

        self._check_payload(
            FakeFactory.parse(res.body.decode('cp932')),
            FakeFactory.create(),
            )


class CustomerTest(FamiPortAPIViewTest):
    """
    request
ticketingDate=20150331182222&orderId=410900000005&totalAmount=2200&playGuideId=&mmkNo=01&barCodeNo=4119000000005&sequenceNo=15033100004&storeCode=000009&
    response
<?xml version="1.0" encoding="Shift_JIS"?>
<FMIF>
<resultCode>00</resultCode>
<replyCode>00</replyCode>
<name>k9DUstJ8MjSxS5vCrHoXsDwUnlz6oUt9oBAD7aAVIJBXWFvLkbehVbFSejR8dFDpmfpeg0/+OvSEC6JWNhukadAwwt8Fd26uyZzykiTMwVQ=</name>
<memberId>lVdX1ezHs1NTaoTSLXR6SAYojrjWLzvgwgADleHELvQ=</memberId>
<address1>k9DUstJ8MjSxS5vCrHoXsEJE3WJ6M2Js7/U/bn0xdnnjQPJsT/lpdofLF2fyld8IKNskWqmQBaT538Z54GDc+A/gXkwY91eDwJ43i8VZ4jQKX2+cx9bRTu0IKgF3eCcGgAWUZ6LBOAQu17LMb/Y5auHbDcznH1yfNTfuRTWAFDcv+JFtJKAjbKXS3/vu9ISUCt7u4JzpBln9oYXHRYoAGIVZTDVmgdco9v51kDHugnM=</address1>
<address2>k9DUstJ8MjSxS5vCrHoXsEJE3WJ6M2Js7/U/bn0xdnnjQPJsT/lpdofLF2fyld8IKNskWqmQBaT538Z54GDc+A/gXkwY91eDwJ43i8VZ4jQKX2+cx9bRTu0IKgF3eCcGgAWUZ6LBOAQu17LMb/Y5auHbDcznH1yfNTfuRTWAFDcv+JFtJKAjbKXS3/vu9ISUCt7u4JzpBln9oYXHRYoAGIVZTDVmgdco9v51kDHugnM=</address2>
<identifyNo>1234567890123456</identifyNo>
</FMIF>
    """

    url = '/famiport/reservation/customer'

    @mock.patch('altair.app.ticketing.famiport.models.FamiPortReceipt.get_by_barcode_no')
    def test_it(self, get_by_barcode_no):
        from ..testing import FamiPortCustomerResponseFakeFactory as FakeFactory
        from ..communication import FamiPortCustomerInformationResponse as FamiportResponse
        from ..models import FamiPortReceiptType

        get_by_barcode_no.return_value = DummyModel(
            type=FamiPortReceiptType.CashOnDelivery,
            shop_code=u'000009',
            barcode_no=u'1000000000000',
            can_completion=lambda now: True,
            completed_at=None,
            void_at=None,
            famiport_order=DummyModel(
                customer_name=u'発券　し太郎',
                customer_member_id=u'REIOHREOIHOIERHOIERHGOIERGHOI',
                customer_address_1=u'東京都品川区',
                customer_address_2=u'西五反田',
                customer_identify_no=u'1234567890123456',
                )
            )
        res = self._callFUT({
            'storeCode': u'99999',
            'mmkNo': '01',
            'ticketingDate': '20150331182222',
            'sequenceNo': '15033100004',
            'barCodeNo': '4119000000005',
            'playGuideId': '11345',
            'orderId': '410900000005',
            'totalAmount': '2200',
            })
        self.assertEqual(200, res.status_code)
        self._check_payload(
            FakeFactory.parse(res.body.decode('cp932')),
            FakeFactory.create(),
            FamiportResponse,
            )


class RefundTest(FamiPortAPIViewTest):
    u"""払戻

    BusinessFlg=3&TextTyp=0&EntryTyp=1&ShopNo=0012345&RegisterNo=02&TimeStamp=20141201&BarCode1=2123456789012&BarCode2=&BarCode3=&BarCode4=
    """
    url = '/famiport/refund'

    @mock.patch('altair.app.ticketing.famiport.server.views.get_xmlResponse_generator')
    @mock.patch('altair.app.ticketing.famiport.server.views.get_response_builder')
    @mock.patch('altair.app.ticketing.famiport.server.views.FamiPortRequestFactory')
    @mock.patch('altair.app.ticketing.famiport.server.views.get_db_session')
    def test_it(self, get_db_session, FamiPortRequestFactory,
                get_response_builder, get_xmlResponse_generator):
        payload_builder = mock.Mock(
            encoding='cp932',
            generate_xmlResponse=mock.Mock(return_value='<xml></xml>')
            )
        get_xmlResponse_generator.return_value = payload_builder
        get_response_builder.return_value.build_response.return_value.encrypt_key = None
        self._callFUT({
            'BusinessFlg': '3',
            'TextTyp': '0',
            'EntryTyp': '1',
            'ShopNo': '0012345',
            'RegisterNo': '02',
            'TimeStamp': '20141201',
            'BarCode1': '2123456789012',
            'BarCode2': '',
            'BarCode3': '',
            'BarCode4': '',
            })

    def test_bad_request(self):
        from webtest.app import AppError
        with self.assertRaises(AppError):
            self._callFUT({})
