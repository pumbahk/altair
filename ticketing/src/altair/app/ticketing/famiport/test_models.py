# encoding:utf-8
from unittest import TestCase
import mock
from .testing import _setup_db, _teardown_db
from datetime import datetime, date
from decimal import Decimal
from pyramid.testing import setUp, tearDown, DummyRequest


class TestFamiPortEvent(TestCase):
    def setUp(self):
        self.config = setUp()
        self.engine = _setup_db(
            self.config.registry,
            [
                'altair.app.ticketing.famiport.models',
                ])
        from altair.sqlahelper import get_global_db_session
        self.session = get_global_db_session(self.config.registry, 'famiport')

    def tearDown(self):
        _teardown_db(self.config.registry)
        tearDown()

    def testSpaceDelimited(self):
        from .models import FamiPortEvent, FamiPortClient, FamiPortPlayguide, FamiPortVenue, FamiPortGenre1, FamiPortGenre2
        event = FamiPortEvent(
            code_1=u'000000',
            code_2=u'0000',
            name_1=u'name_1',
            name_2=u'name_2',
            client=FamiPortClient(
                name=u'チケットスター',
                code=u'000',
                playguide=FamiPortPlayguide(discrimination_code=1, discrimination_code_2=1),
                prefix=u'XXX'
                ),
            venue=FamiPortVenue(name=u'venue', client_code=u'000000', name_kana=u'ヴェニュー'),
            genre_1=FamiPortGenre1(code=1, name=u'genre1'),
            genre_2=FamiPortGenre2(genre_1_code=1, code=2, name=u'genre2'),
            keywords=[u'a', u'b', u'c'],
            search_code=u'search'
            )
        self.session.add(event)
        self.session.flush()
        _event = self.session.query(FamiPortEvent).filter_by(code_1=u'000000').one()
        self.assertEqual(_event.keywords, [u'a', u'b', u'c'])
        stored_value = list(self.session.bind.execute('SELECT keywords FROM FamiPortEvent WHERE code_1=?', (u'000000', )))[0][0]
        self.assertEqual(stored_value, u'a b c')


class TestScrew(TestCase):
    def test_screw36(self):
        from .models import screw36
        v = screw36(0x0, 0x123456789)
        self.assertEqual(v, 0x123456789)
        v = screw36(0x555555555, 0x123456789)
        self.assertEqual(v, 0xa96156b56 ^ 0x123456789)
        v = screw36(0xaaaaaaaaa, 0x123456789)
        self.assertEqual(v, 0x569ea94a9 ^ 0x123456789)

    def test_screw36_1e10(self):
        import math
        from .models import screw36
        for i in range(0, 100000):
            assert math.log10(screw36(i, 0x123456789)) < 11

    def test_screw47(self):
        from .models import screw47
        v = screw47(0x555555555555, 0x12345678901)
        self.assertEqual(v, 0x4d54b5a4ad71 ^ 0x12345678901)
        v = screw47(0x2aaaaaaaaaaa, 0x12345678901)
        self.assertEqual(v, 0x32ab4a5b528e ^ 0x12345678901)


class TestCalculateGtinCd(TestCase):
    def test_it(self):
        from .models import calculate_gtin_cd
        self.assertEqual(calculate_gtin_cd(u'629104150021'), u'3')


class FamiPortInformationMessageTest(TestCase):
    def setUp(self):
        self.config = setUp()
        self.engine = _setup_db(
            self.config.registry,
            [
                'altair.app.ticketing.famiport.models',
                ])
        from altair.sqlahelper import get_global_db_session
        self.session = get_global_db_session(self.config.registry, 'famiport')

    def tearDown(self):
        _teardown_db(self.config.registry)
        tearDown()

    def _target(self):
        from .models import FamiPortInformationMessage as klass
        return klass

    def _makeOne(self, *args, **kwargs):
        return self._target()(*args, **kwargs)

    def test_it(self):
        target = self._target()
        kwds = {
            'result_code': 'WithInformation',
            'message': u'日本語のメッセージ',
            }

        old_obj = self._makeOne(**kwds)
        self.session.add(old_obj)
        self.session.flush()
        filter_sql = (target.id == old_obj.id)
        new_obj = self.session \
            .query(target) \
            .filter(filter_sql) \
            .one()

        for key, value in kwds.items():
            self.assertEqual(getattr(new_obj, key), value)

    def test_create(self):
        target = self._target()
        kwds = {
            'result_code': 'WithInformation',
            'message': u'日本語のメッセージ',
            }

        old_obj = target(**kwds)

        self.session.add(old_obj)
        self.session.flush()
        filter_sql = (target.id == old_obj.id)
        new_obj = self.session \
            .query(target) \
            .filter(filter_sql) \
            .one()

        for key, value in kwds.items():
            self.assertEqual(getattr(new_obj, key), value)

    def test_get_message(self):
        from .communication import InformationResultCodeEnum
        target = self._target()
        kwds = {
            'information_result_code': InformationResultCodeEnum.WithInformation,
            'default_message': '',
            'session': self.session,
            }

        msg = target.get_message(**kwds)
        self.assertEqual(msg, '')


class CreateRandomSequenceNumberTest(TestCase):
    def _get_target(self):
        from .models import create_random_sequence_number as target
        return target

    def _get_valid_chars(self):
        import string
        valid_cahrs = string.digits + string.ascii_uppercase
        return valid_cahrs

    def test_it_length_13(self):
        length = 13
        func = self._get_target()
        valid_chars = self._get_valid_chars()
        value = func(length)
        self.assertEqual(length, len(value))
        for ch in value:
            self.assertIn(ch, valid_chars)

    def test_it_length_14(self):
        length = 14
        func = self._get_target()
        valid_chars = self._get_valid_chars()
        value = func(length)
        self.assertEqual(length, len(value))
        for ch in value:
            self.assertIn(ch, valid_chars)


class TestFamiPortReceipt(TestCase):
    def _target(self):
        from .models import FamiPortReceipt as klass
        return klass

    def _makeOne(self, *args, **kwargs):
        return self._target()(*args, **kwargs)

    def test_mark_completed(self):
        from pyramid.testing import DummyRequest
        from datetime import datetime
        now_ = datetime.now()
        request = DummyRequest()
        request.registry = mock.Mock()
        receipt = self._makeOne(
            id=1,
            reserve_number=u'111111111',
            completed_at=None,
            )
        receipt.mark_completed(now_, request)
        self.assertEqual(receipt.completed_at, now_)
        self.assertTrue(request.registry.notify.called)

    def test_mark_completed_error(self):
        from .exc import FamiPortUnsatisfiedPreconditionError
        from pyramid.testing import DummyRequest
        from datetime import datetime
        now_ = datetime.now()
        request = DummyRequest()
        request.registry = mock.Mock()
        receipt = self._makeOne(
            id=1,
            reserve_number=u'111111111',
            completed_at=now_,
            )
        with self.assertRaises(FamiPortUnsatisfiedPreconditionError):
            receipt.mark_completed(now_, request)


class FamiPortOrderTest(TestCase):
    def setUp(self):
        from altair.sqlahelper import get_global_db_session
        self.request = DummyRequest()
        self.config = setUp(request=self.request)
        self.config.include('.')
        self.engine = _setup_db(
            self.config.registry,
            [
                'altair.app.ticketing.famiport.models',
                'altair.app.ticketing.famiport.communication.models',
                ]
            )
        self.session = get_global_db_session(self.config.registry, 'famiport')
        from .models import (
            FamiPortPrefecture,
            FamiPortPlayguide,
            FamiPortClient,
            FamiPortVenue,
            FamiPortGenre1,
            FamiPortGenre2,
            FamiPortSalesChannel,
            FamiPortPerformanceType,
            FamiPortEvent,
            FamiPortPerformance,
            FamiPortSalesSegment,
            FamiPortInformationMessage,
            FamiPortPrefecture,
            FamiPortOrder,
            FamiPortReceipt,
            FamiPortOrderType,
            FamiPortReceiptType,
            FamiPortTicketType,
            FamiPortTicket,
            FamiPortShop,
            )
        self.famiport_shop = FamiPortShop(
            code=u'000009',
            company_code=u'TEST',
            company_name=u'TEST',
            district_code=u'TEST',
            district_name=u'TEST',
            district_valid_from=date(2015, 6, 1),
            branch_code=u'TEST',
            branch_name=u'TEST',
            branch_valid_from=date(2015, 6, 1),
            name=u'TEST',
            name_kana=u'TEST',
            tel=u'070111122222',
            prefecture=1,
            prefecture_name=u'東京都',
            address=u'東京都品川区西五反田',
            open_from=date(2015, 6, 1),
            zip=u'1410000',
            business_run_from=date(2015, 6, 1),
            )
        self.session.add(self.famiport_shop)
        self.famiport_playguide = FamiPortPlayguide(
            discrimination_code=5,
            discrimination_code_2=4
            )
        self.famiport_client = FamiPortClient(
            playguide=self.famiport_playguide,
            code=u'012340123401234012340123',
            name=u'チケットスター',
            prefix=u'TTT'
            )
        self.famiport_genre_1 = FamiPortGenre1(
            code=1,
            name=u'大ジャンル'
            )
        self.famiport_genre_2 = FamiPortGenre2(
            genre_1=self.famiport_genre_1,
            code=2,
            name=u'小ジャンル'
            )
        self.famiport_venue = FamiPortVenue(
            client_code=u'012340123401234012340123',
            name=u'博品館劇場',
            name_kana=u'ハクヒンカンゲキジョウ',
            prefecture=FamiPortPrefecture.Tokyo.id
            )
        self.famiport_event = FamiPortEvent(
            client=self.famiport_client,
            venue=self.famiport_venue,
            genre_1=self.famiport_genre_1,
            genre_2=self.famiport_genre_2,
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            code_1=u'000000',
            code_2=u'1111',
            name_1=u'テスト公演',
            name_2=u'テスト公演副題',
            start_at=datetime(2015, 7, 1, 19, 0, 0),
            end_at=datetime(2015, 7, 10, 23, 59, 59),
            keywords=[u'チケットスター', u'博品館', u'イベント'],
            purchasable_prefectures=[u'%02d' % FamiPortPrefecture.Nationwide.id],
            )
        self.famiport_performance = FamiPortPerformance(
            famiport_event=self.famiport_event,
            code=u'001',
            name=u'7/1公演',
            type=FamiPortPerformanceType.Normal.value,
            searchable=False,
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            start_at=datetime(2015, 7, 1, 19, 0, 0),
            ticket_name=u''
            )
        self.famiport_sales_segment = FamiPortSalesSegment(
            famiport_performance=self.famiport_performance,
            code=u'001',
            name=u'一般販売',
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            published_at=datetime(2015, 4, 15, 0, 0, 0),
            start_at=datetime(2015, 5, 1, 10, 0, 0),
            end_at=datetime(2015, 5, 31, 23, 59, 59),
            auth_required=False,
            auth_message=u'',
            seat_selection_start_at=datetime(2015, 5, 10, 10, 0, 0)
            )
        self.famiport_order_cash_on_delivery = FamiPortOrder(
            type=FamiPortOrderType.CashOnDelivery.value,
            order_no=u'RT0000000000',
            famiport_order_identifier=u'000011112222',
            famiport_sales_segment=self.famiport_sales_segment,
            famiport_performance=self.famiport_performance,
            famiport_client=self.famiport_client,
            generation=0,
            invalidated_at=None,
            total_amount=Decimal(10540),
            ticket_payment=Decimal(10000),
            ticketing_fee=Decimal(216),
            system_fee=Decimal(324),
            paid_at=None,
            issued_at=None,
            canceled_at=None,
            ticketing_start_at=datetime(2015, 5, 20, 12, 34, 56),
            ticketing_end_at=datetime(2015, 5, 23, 23, 59, 59),
            payment_start_at=datetime(2015, 5, 20, 12, 34, 56),
            payment_due_at=datetime(2015, 5, 23, 23, 59, 59),
            customer_name=u'チケット　太郎',
            customer_address_1=u'東京都品川区西五反田7-1-9',
            customer_address_2=u'五反田HSビル9F',
            customer_phone_number=u'0123456789',
            famiport_receipts=[
                FamiPortReceipt(
                    type=FamiPortReceiptType.CashOnDelivery.value,
                    barcode_no=u'01234012340123',
                    famiport_order_identifier=u'000011112223',
                    shop_code=u'00009',
                    reserve_number=u'4321043210432'
                    ),
                ],
            famiport_tickets=[
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=u'0000000000001',
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    ),
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=u'0000000000002',
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    )
                ],
            customer_name_input=False,
            customer_phone_input=False,
            created_at=datetime(2015, 5, 20, 12, 34, 56)
            )
        self.session.add(self.famiport_order_cash_on_delivery)
        self.famiport_order_payment = FamiPortOrder(
            type=FamiPortOrderType.Payment.value,
            order_no=u'RT0000000001',
            famiport_order_identifier=u'000011112225',
            famiport_sales_segment=self.famiport_sales_segment,
            famiport_performance=self.famiport_performance,
            famiport_client=self.famiport_client,
            generation=0,
            invalidated_at=None,
            total_amount=Decimal(10540),
            ticket_payment=Decimal(10000),
            ticketing_fee=Decimal(216),
            system_fee=Decimal(324),
            paid_at=None,
            issued_at=None,
            canceled_at=None,
            ticketing_start_at=datetime(2015, 5, 22, 00, 00, 00),
            ticketing_end_at=datetime(2015, 5, 23, 23, 59, 59),
            payment_start_at=datetime(2015, 5, 20, 12, 34, 56),
            payment_due_at=datetime(2015, 5, 21, 23, 59, 59),
            customer_name=u'チケット　太郎',
            customer_address_1=u'東京都品川区西五反田7-1-9',
            customer_address_2=u'五反田HSビル9F',
            customer_phone_number=u'0123456789',
            famiport_receipts=[
                FamiPortReceipt(
                    type=FamiPortReceiptType.Payment.value,
                    barcode_no=u'01234012340124',
                    famiport_order_identifier=u'000011112224',
                    shop_code=u'00009',
                    reserve_number=u'4321043210433',
                    ),
                FamiPortReceipt(
                    type=FamiPortReceiptType.Ticketing.value,
                    barcode_no=u'01234012340125',
                    famiport_order_identifier=u'000011112225',
                    shop_code=u'00009',
                    reserve_number=u'4321043210434',
                    )
                ],
            famiport_tickets=[
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=u'0000000000003',
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    ),
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=u'0000000000004',
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    )
                ],
            customer_name_input=False,
            customer_phone_input=False,
            created_at=datetime(2015, 5, 20, 12, 34, 56)
            )
        self.session.add(self.famiport_order_payment)
        self.famiport_order_payment_only = FamiPortOrder(
            type=FamiPortOrderType.PaymentOnly.value,
            order_no=u'RT0000000001',
            famiport_order_identifier=u'000011112226',
            famiport_sales_segment=self.famiport_sales_segment,
            famiport_performance=self.famiport_performance,
            famiport_client=self.famiport_client,
            generation=0,
            invalidated_at=None,
            total_amount=Decimal(10540),
            ticket_payment=Decimal(10000),
            ticketing_fee=Decimal(216),
            system_fee=Decimal(324),
            paid_at=None,
            issued_at=None,
            canceled_at=None,
            ticketing_start_at=None,
            ticketing_end_at=None,
            payment_start_at=datetime(2015, 5, 22, 12, 34, 56),
            payment_due_at=datetime(2015, 5, 23, 23, 59, 59),
            customer_name=u'チケット　太郎',
            customer_address_1=u'東京都品川区西五反田7-1-9',
            customer_address_2=u'五反田HSビル9F',
            customer_phone_number=u'0123456789',
            famiport_receipts=[
                FamiPortReceipt(
                    type=FamiPortReceiptType.Payment.value,
                    famiport_order_identifier=u'000011112227',
                    barcode_no=u'01234012340126',
                    shop_code=u'00009',
                    reserve_number=u'4321043210435'
                    ),
                ],
            famiport_tickets=[
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=u'0000000000005',
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    ),
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=u'0000000000006',
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    )
                ],
            customer_name_input=True,
            customer_phone_input=False,
            created_at=datetime(2015, 5, 22, 12, 34, 56)
            )
        self.session.add(self.famiport_order_payment_only)

        self.famiport_order_ticketing_only = FamiPortOrder(
            type=FamiPortOrderType.Ticketing.value,
            order_no=u'RT0000000001',
            famiport_order_identifier=u'000011112228',
            famiport_sales_segment=self.famiport_sales_segment,
            famiport_performance=self.famiport_performance,
            famiport_client=self.famiport_client,
            generation=0,
            invalidated_at=None,
            total_amount=Decimal(10540),
            ticket_payment=Decimal(10000),
            ticketing_fee=Decimal(216),
            system_fee=Decimal(324),
            paid_at=None,
            issued_at=None,
            canceled_at=None,
            ticketing_start_at=datetime(2015, 5, 20, 12, 34, 56),
            ticketing_end_at=datetime(2015, 5, 23, 23, 59, 59),
            payment_start_at=None,
            payment_due_at=None,
            customer_name=u'チケット　太郎',
            customer_address_1=u'東京都品川区西五反田7-1-9',
            customer_address_2=u'五反田HSビル9F',
            customer_phone_number=u'0123456789',
            famiport_receipts=[
                FamiPortReceipt(
                    type=FamiPortReceiptType.Ticketing.value,
                    famiport_order_identifier=u'000011112229',
                    barcode_no=u'01234012340127',
                    shop_code=u'00009',
                    reserve_number=u'4321043210436'
                    ),
                ],
            famiport_tickets=[
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=u'0000000000007',
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    ),
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=u'0000000000008',
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    )
                ],
            customer_name_input=False,
            customer_phone_input=False,
            created_at=datetime(2015, 5, 22, 12, 34, 56)
            )
        self.session.add(self.famiport_order_ticketing_only)
        self.session.commit()
        self.now = datetime(2015, 5, 21, 10, 0, 0)

    def tearDown(self):
        _teardown_db(self.config.registry)
        tearDown()

    def test_mark_reissueable_basic(self):
        from .exc import FamiPortUnsatisfiedPreconditionError
        from .models import FamiPortVoidReason
        self.famiport_order_cash_on_delivery.famiport_receipts[0].inquired_at = datetime(2015, 5, 21, 0, 0, 0)
        self.famiport_order_cash_on_delivery.famiport_receipts[0].payment_request_received_at = datetime(2015, 5, 21, 0, 0, 30)
        self.famiport_order_cash_on_delivery.famiport_receipts[0].completed_at = datetime(2015, 5, 21, 0, 1, 0)
        self.famiport_order_cash_on_delivery.make_reissueable(
            datetime(2015, 5, 21, 0, 10, 0),
            self.request,
            cancel_reason_code=u'00',
            cancel_reason_text=u'canceled'
            )
        self.assertIsNotNone(self.famiport_order_cash_on_delivery.famiport_receipts[0].completed_at)
        self.assertIsNotNone(self.famiport_order_cash_on_delivery.famiport_receipts[0].made_reissueable_at)
        self.assertIsNone(self.famiport_order_cash_on_delivery.famiport_receipts[0].payment_request_received_at)

    def test_mark_reissueable_on_payment_only(self):
        from .exc import FamiPortUnsatisfiedPreconditionError
        from .models import FamiPortVoidReason
        with self.assertRaises(FamiPortUnsatisfiedPreconditionError):
            self.famiport_order_payment_only.make_reissueable(
                datetime(2015, 5, 21, 0, 10, 0),
                self.request,
                cancel_reason_code=u'00',
                cancel_reason_text=u'canceled'
                )

    def test_expired_cash_on_delivery(self):
        target = self.famiport_order_cash_on_delivery
        self.assertEqual(target.expired(datetime(2015, 5, 19, 0, 0, 0)), None)
        self.assertEqual(target.expired(datetime(2015, 5, 20, 12, 34, 56)), None)
        self.assertEqual(target.expired(datetime(2015, 5, 21, 0, 0, 0)), None)
        self.assertEqual(target.expired(datetime(2015, 5, 23, 23, 59, 59)), None)
        self.assertEqual(target.expired(datetime(2015, 5, 24, 0, 0, 0)), datetime(2015, 5, 23, 23, 59, 59))

    def test_expired_paid_cash_on_delivery(self):
        target = self.famiport_order_cash_on_delivery
        target.payment_famiport_receipt.completed_at = datetime(2015, 5, 21, 0, 0, 0)
        self.assertEqual(target.expired(datetime(2015, 5, 19, 0, 0, 0)), None)
        self.assertEqual(target.expired(datetime(2015, 5, 20, 12, 34, 56)), None)
        self.assertEqual(target.expired(datetime(2015, 5, 21, 0, 0, 0)), None)
        self.assertEqual(target.expired(datetime(2015, 5, 23, 23, 59, 59)), None)
        self.assertEqual(target.expired(datetime(2015, 5, 24, 0, 0, 0)), None)

    def test_expired_payment(self):
        target = self.famiport_order_payment
        self.assertEqual(target.expired(datetime(2015, 5, 19, 0, 0, 0)), None)
        self.assertEqual(target.expired(datetime(2015, 5, 20, 12, 34, 56)), None)
        self.assertEqual(target.expired(datetime(2015, 5, 21, 23, 59, 59)), None)
        self.assertEqual(target.expired(datetime(2015, 5, 22, 0, 0, 0)), datetime(2015, 5, 21, 23, 59, 59))
        self.assertEqual(target.expired(datetime(2015, 5, 23, 23, 59, 59)), datetime(2015, 5, 21, 23, 59, 59))
        self.assertEqual(target.expired(datetime(2015, 5, 24, 0, 0, 0)), datetime(2015, 5, 21, 23, 59, 59))

    def test_expired_payment_paid(self):
        target = self.famiport_order_payment
        target.payment_famiport_receipt.completed_at = datetime(2015, 5, 21, 0, 0, 0)
        self.assertEqual(target.expired(datetime(2015, 5, 22, 0, 0, 0)), None)
        self.assertEqual(target.expired(datetime(2015, 5, 23, 23, 59, 59)), None)
        self.assertEqual(target.expired(datetime(2015, 5, 24, 0, 0, 0)), datetime(2015, 5, 23, 23, 59, 59))

    def test_expired_payment_paid_and_issued(self):
        target = self.famiport_order_payment
        target.payment_famiport_receipt.completed_at = datetime(2015, 5, 21, 0, 0, 0)
        target.ticketing_famiport_receipt.completed_at = datetime(2015, 5, 23, 0, 0, 0)
        self.assertEqual(target.expired(datetime(2015, 5, 22, 0, 0, 0)), None)
        self.assertEqual(target.expired(datetime(2015, 5, 23, 23, 59, 59)), None)
        self.assertEqual(target.expired(datetime(2015, 5, 24, 0, 0, 0)), None)

    def test_expired_ticketing_only(self):
        target = self.famiport_order_ticketing_only
        self.assertEqual(target.expired(datetime(2015, 5, 19, 0, 0, 0)), None)
        self.assertEqual(target.expired(datetime(2015, 5, 20, 12, 34, 56)), None)
        self.assertEqual(target.expired(datetime(2015, 5, 21, 0, 0, 0)), None)
        self.assertEqual(target.expired(datetime(2015, 5, 23, 23, 59, 59)), None)
        self.assertEqual(target.expired(datetime(2015, 5, 24, 0, 0, 0)), datetime(2015, 5, 23, 23, 59, 59))

    def test_expired_issued_ticketing_only(self):
        target = self.famiport_order_ticketing_only
        target.ticketing_famiport_receipt.completed_at = datetime(2015, 5, 23, 0, 0, 0)
        self.assertEqual(target.expired(datetime(2015, 5, 19, 0, 0, 0)), None)
        self.assertEqual(target.expired(datetime(2015, 5, 20, 12, 34, 56)), None)
        self.assertEqual(target.expired(datetime(2015, 5, 21, 0, 0, 0)), None)
        self.assertEqual(target.expired(datetime(2015, 5, 23, 23, 59, 59)), None)
        self.assertEqual(target.expired(datetime(2015, 5, 24, 0, 0, 0)), None)

    def test_expired_payment_only(self):
        target = self.famiport_order_payment_only
        self.assertEqual(target.expired(datetime(2015, 5, 19, 0, 0, 0)), None)
        self.assertEqual(target.expired(datetime(2015, 5, 20, 12, 34, 56)), None)
        self.assertEqual(target.expired(datetime(2015, 5, 21, 0, 0, 0)), None)
        self.assertEqual(target.expired(datetime(2015, 5, 23, 23, 59, 59)), None)
        self.assertEqual(target.expired(datetime(2015, 5, 24, 0, 0, 0)), datetime(2015, 5, 23, 23, 59, 59))


    def test_expired_paid_payment_only(self):
        target = self.famiport_order_payment_only
        target.payment_famiport_receipt.completed_at = datetime(2015, 5, 21, 0, 0, 0)
        self.assertEqual(target.expired(datetime(2015, 5, 19, 0, 0, 0)), None)
        self.assertEqual(target.expired(datetime(2015, 5, 20, 12, 34, 56)), None)
        self.assertEqual(target.expired(datetime(2015, 5, 21, 0, 0, 0)), None)
        self.assertEqual(target.expired(datetime(2015, 5, 23, 23, 59, 59)), None)
        self.assertEqual(target.expired(datetime(2015, 5, 24, 0, 0, 0)), None)

