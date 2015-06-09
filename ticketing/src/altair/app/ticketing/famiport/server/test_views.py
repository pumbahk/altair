# -*- coding: utf-8 -*-
from unittest import TestCase
import re
import itertools
import mock
import lxml.etree
from pyramid.testing import (
    DummyModel,
    )
from altair.app.ticketing.testing import (
    _setup_db,
    _teardown_db,
    )


class FamiPortAPIViewTest(TestCase):
    def setUp(self):

        from webtest import TestApp
        from pyramid.config import Configurator
        self.session = _setup_db([
            'altair.app.ticketing.famiport.models'
            ])
        config = Configurator()
        config.include('altair.app.ticketing.famiport.server', '/famiport/')

        extra_environ = {'HTTP_HOST': 'localhost:8063'}
        self.app = TestApp(config.make_wsgi_app(), extra_environ=extra_environ)

    def tearDown(self):
        self.session.remove()
        _teardown_db()

    def _callFUT(self, *args, **kwds):
        return self.app.post(self.url, *args, **kwds)

    def _check_payload(self, res, exp, famiport_response_class=None):
        res_payload = lxml.etree.tostring(res, pretty_print=True)
        exp_payload = lxml.etree.tostring(exp, pretty_print=True)
        res_payload_list = map(lambda x: x.strip(), res_payload.split('\n'))
        exp_payload_list = map(lambda x: x.strip(), exp_payload.split('\n'))

        regx = re.compile(r'<(?P<tag>[^>]+)>')

        for res_elm, exp_elm in itertools.izip_longest(res_payload_list, exp_payload_list, fillvalue=None):
            matching = regx.search(res_elm)
            if not matching:
                continue

            tag_name = matching.group('tag')
            if tag_name in ['ticketData']:  # ignore orz
                continue

            if famiport_response_class and tag_name in famiport_response_class._encryptedFields:
                self.assertEqual(bool(res_elm), bool(exp_elm))
            else:
                self.assertEqual(res_elm, exp_elm)
            #     tag_name = lxml.etree.fromstring(res_elm).tag
            # except:
            #     import ipdb; ipdb.set_trace()
            #     raise
            # if famiport_response_class and tag_name in famiport_response_class.encrypted_fields:
            #     # 暗号化処理のところ
            #     # とりあえずskipする
            #     pass
            # else:
            #     import ipdb; ipdb.set_trace()


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

    @mock.patch('altair.app.ticketing.famiport.models.FamiPortOrder.get_by_reserveNumber')
    def test_it(self, get_by_reserveNumber):
        from ..testing import FamiPortReservationInquiryResponseFakeFactory as FakeFactory
        import datetime
        from ..testing import generate_ticket_data
        from ..models import FamiPortTicket
        from ..communication import FamiPortReservationInquiryResponse as FamiPortResponse
        famiport_tickets = [
            FamiPortTicket(
                barcode_number=ticket['barCodeNo'],
                type=ticket['ticketClass'],
                template_code=ticket['templateCode'],
                data=ticket['ticketData'],
            ) for ticket in list(generate_ticket_data())[:1]]

        payment_due_at = datetime.datetime(2015, 3, 31, 17, 25, 55)
        ticketing_start_at = datetime.datetime(2015, 3, 31, 17, 25, 53)
        ticketing_end_at = datetime.datetime(2015, 3, 31, 17, 25, 55)

        get_by_reserveNumber.return_value = DummyModel(
            customer_name=u'楽天太郎',
            famiport_order_identifier='430000000002',
            type='1',
            payment_due_at=payment_due_at,
            paid_at=None,
            issued_at=None,
            ticketing_start_at=ticketing_start_at,
            ticketing_end_at=ticketing_end_at,
            playguide_id=1,
            playguide_name=u'クライアント１',
            exchange_number='4310000000002',
            barcode_number=u'4110000000006',
            total_amount=670,
            ticket_payment=0,
            system_fee=500,
            ticketing_fee=170,
            ticket_total_count=len(famiport_tickets),
            ticket_count=len(famiport_tickets),
            koen_date=None,
            famiport_tickets=famiport_tickets,
            kogyo_name=u'サンプル興行',
            customer_name_input=0,
            customer_phone_input=0,
            famiport_sales_segment=DummyModel(
                famiport_performance=DummyModel(
                    start_at=None,
                    ),
                )
            )

        res = self._callFUT({
            'authNumber': '',
            'reserveNumber': '5300000000001',
            'ticketingDate': '20150325151159',
            'storeCode': '000009',
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
<storeCode>099999</storeCode>
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

    @mock.patch('altair.app.ticketing.famiport.models.FamiPortOrder.get_by_barCodeNo')
    def test_it(self, get_by_barCodeNo):
        import datetime
        from ..testing import generate_ticket_data
        from ..testing import FamiPortPaymentTicketingResponseFakeFactory as FakeFactory
        from ..models import FamiPortTicket
        from ..communication import FamiPortPaymentTicketingResponse as FamiPortResponse

        famiport_tickets = [
            FamiPortTicket(
                barcode_number=ticket['barCodeNo'],
                type=ticket['ticketClass'],
                template_code=ticket['templateCode'],
                data=ticket['ticketData'],
            ) for ticket in generate_ticket_data()]

        payment_due_at = datetime.datetime(2015, 3, 31, 17, 25, 55)
        ticketing_start_at = datetime.datetime(2015, 3, 31, 17, 25, 53)
        ticketing_end_at = datetime.datetime(2015, 3, 31, 17, 25, 55)

        get_by_barCodeNo.return_value = DummyModel(
            famiport_order_identifier='430000000002',
            type='3',
            payment_due_at=payment_due_at,
            paid_at=None,
            issued_at=None,
            ticketing_start_at=ticketing_start_at,
            ticketing_end_at=ticketing_end_at,
            playguide_id=1,
            playguide_name=u'クライアント１',
            exchange_number='4310000000002',
            barcode_number=u'1000000000000',
            total_amount=200,
            ticket_payment=0,
            system_fee=0,
            ticketing_fee=200,
            ticket_total_count=len(famiport_tickets),
            ticket_count=len(famiport_tickets),
            koen_date=None,
            famiport_tickets=famiport_tickets,
            kogyo_name=u'ａｂｃｄｅｆｇｈｉｊ１２３４５６７８９０',
            famiport_sales_segment=DummyModel(
                famiport_performance=DummyModel(
                    start_at=None,
                    ),
                )
            )

        res = self._callFUT({
            'ticketingDate': '20150331172554',
            'playGuideId': '',
            'phoneNumber': 'rfanmRgUZFRRephCwOsgbg%3d%3d',
            'customerName': 'pT6fj7ULQklIfOWBKGyQ6g%3d%3d',
            'mmkNo': '01',
            'barCodeNo': '1000000000000',
            'sequenceNo': '12345678901',
            'storeCode': '099999',
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
<storeCode>099999</storeCode>
<sequenceNo>12345678901</sequenceNo>
<barCodeNo>6010000000000</barCodeNo>
<orderId>123456789012</orderId>
<replyCode>00</replyCode>
</FMIF>
    """

    url = '/famiport/reservation/completion'

    @mock.patch('altair.app.ticketing.famiport.models.FamiPortOrder.get_by_barCodeNo')
    def test_it(self, get_by_barCodeNo):
        from ..testing import FamiPortPaymentTicketingCompletionResponseFakeFactory as FakeFactory
        get_by_barCodeNo.return_value = DummyModel()
        res = self._callFUT({
            'ticketingDate': '20150331184114',
            'orderId': '123456789012',
            'totalAmount': '1000',
            'playGuideId': '',
            'mmkNo': '01',
            'barCodeNo': '6010000000000',
            'sequenceNo': '12345678901',
            'storeCode': '099999',
            })
        self.assertEqual(200, res.status_code)

        self._check_payload(
            FakeFactory.parse(res.unicode_body),
            FakeFactory.create(),
            )

    @mock.patch('altair.app.ticketing.famiport.models.FamiPortOrder.get_by_barCodeNo')
    def test_fail(self, get_by_barCodeNo):
        from ..testing import FamiPortPaymentTicketingCompletionResponseFailFakeFactory as FakeFactory
        get_by_barCodeNo.return_value = None
        res = self._callFUT({
            'ticketingDate': '20150331184114',
            'orderId': '123456789012',
            'totalAmount': '1000',
            'playGuideId': '',
            'mmkNo': '01',
            'barCodeNo': '6010000000000',
            'sequenceNo': '12345678901',
            'storeCode': '099999',
            })
        self.assertEqual(200, res.status_code)

        self._check_payload(
            FakeFactory.parse(res.unicode_body),
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
<storeCode>099999</storeCode>
<sequenceNo>12345678901</sequenceNo>
<barCodeNo>3300000000000</barCodeNo>
<orderId>123456789012</orderId>
<replyCode>00</replyCode>
</FMIF>
    """

    url = '/famiport/reservation/cancel'

    def test_it(self):
        from ..testing import FamiPortPaymentTicketingCancelResponseFakeFactory as FakeFactory
        res = self._callFUT({
            'playGuideId': '',
            'storeCode': '000009',
            'ticketingDate': '20150401101950',
            'barCodeNo': '1000000000000',
            'sequenceNo': '15040100009',
            'mmkNo': '1',
            'orderId': '123456789012',
            'cancelCode': '10',
            })
        self.assertEqual(200, res.status_code)

        self._check_payload(
            FakeFactory.parse(res.unicode_body),
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

    @mock.patch('altair.app.ticketing.famiport.models.FamiPortInformationMessage.get_message')
    def test_it(self, get_message):
        from ..testing import FamiPortInformationResponseFakeFactory as FakeFactory
        get_message.return_value = DummyModel()
        res = self._callFUT({
            'uketsukeCode': '',
            'kogyoSubCode': '',
            'reserveNumber': '4000000000001',
            'infoKubun': 'Reserve',
            'kogyoCode': '',
            'koenCode': '',
            'authCode': '',
            'storeCode': '000009',
            })
        self.assertEqual(200, res.status_code)

        self._check_payload(
            FakeFactory.parse(res.unicode_body),
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

    @mock.patch('altair.app.ticketing.famiport.models.FamiPortOrder.get_by_barCodeNo')
    def test_it(self, get_by_barCodeNo):
        from ..testing import FamiPortCustomerResponseFakeFactory as FakeFactory
        get_by_barCodeNo.return_value = DummyModel(
            customer_name=u'発券　し太郎',
            customer_member_id=u'REIOHREOIHOIERHOIERHGOIERGHOI',
            customer_address_1=u'東京都品川区',
            customer_address_2=u'西五反田',
            customer_identify_no=u'1234567890123456',
            )
        res = self._callFUT({
            'storeCode': '000009',
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
            FakeFactory.parse(res.unicode_body),
            FakeFactory.create(),
            )
