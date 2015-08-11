# encoding:utf-8
import unittest
from .testing import _setup_db, _teardown_db
from datetime import datetime
from decimal import Decimal
from pyramid.testing import setUp, tearDown, DummyRequest

class CancelFamiPortOrderTest(unittest.TestCase):
    def setUp(self):
        self.request = DummyRequest()
        self.config = setUp(request=self.request)
        self.engine = _setup_db(
            self.config.registry,
            [
                'altair.app.ticketing.famiport.models',
                ])
        from altair.sqlahelper import get_db_session
        self.session = get_db_session(self.request, 'famiport')
        from .models import (
            FamiPortOrder,
            FamiPortOrderType,
            FamiPortClient,
            FamiPortPlayguide,
            FamiPortPrefecture,
            FamiPortSalesChannel,
            FamiPortVenue,
            FamiPortEvent,
            FamiPortPerformance,
            FamiPortPerformanceType,
            FamiPortSalesSegment,
            FamiPortGenre1,
            FamiPortGenre2,
            FamiPortTicket,
            FamiPortTicketType,
            FamiPortReceipt,
            FamiPortReceiptType,
            )
        self.client = FamiPortClient(
            code=u'00000000000000000000001',
            name=u'チケットスター',
            prefix=u'000',
            playguide=FamiPortPlayguide(discrimination_code=5, discrimination_code_2=4)
            )
        self.session.add(self.client)
        self.venue = FamiPortVenue(
            client_code=u'00000000000000000000001',
            userside_id=None,
            name=u'テスト会場',
            name_kana=u'テストカイジョウ',
            prefecture=FamiPortPrefecture.Tokyo.id,
            )
        self.session.add(self.venue)
        self.genre_1 = FamiPortGenre1(code=u'00000', name=u'大ジャンル')
        self.session.add(self.genre_1)
        self.genre_2 = FamiPortGenre2(genre_1=self.genre_1, code=u'00000', name=u'小ジャンル')
        self.session.add(self.genre_2)
        self.session.flush()
        self.event = FamiPortEvent(
            client_code=u'00000000000000000000001',
            name_1=u'テストイベント1',
            name_2=u'テスト1',
            code_1=u'000001',
            code_2=u'0000',
            sales_channel=FamiPortSalesChannel.FamiPortOnly.value,
            venue_id=self.venue.id,
            purchasable_prefectures=[FamiPortPrefecture.Nationwide.id],
            start_at=datetime(2015, 10, 1, 0, 0, 0),
            end_at=datetime(2015, 12, 31, 23, 59, 59),
            genre_1=self.genre_1,
            genre_2=self.genre_2,
            keywords=[],
            search_code=u'00000000'
            )
        self.session.add(self.event)
        self.session.flush()
        self.another_event = FamiPortEvent(
            client_code=u'00000000000000000000001',
            name_1=u'テストイベント2',
            name_2=u'テスト2',
            code_1=u'000002',
            code_2=u'0000',
            sales_channel=FamiPortSalesChannel.FamiPortOnly.value,
            venue_id=self.venue.id,
            purchasable_prefectures=[FamiPortPrefecture.Nationwide.id],
            start_at=datetime(2015, 10, 1, 0, 0, 0),
            end_at=datetime(2015, 12, 31, 23, 59, 59),
            genre_1=self.genre_1,
            genre_2=self.genre_2,
            keywords=[],
            search_code=u'00000000'
            )
        self.session.add(self.another_event)
        self.session.flush()
        self.performance = FamiPortPerformance(
            userside_id=None,
            famiport_event_id=self.event.id,
            code=u'000',
            name=u'公演1',
            type=FamiPortPerformanceType.Normal.value,
            searchable=False,
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            start_at=datetime(2015, 10, 1, 0, 0, 0),
            ticket_name=None
            )
        self.session.add(self.performance)
        self.another_performance = FamiPortPerformance(
            userside_id=None,
            famiport_event_id=self.another_event.id,
            code=u'000',
            name=u'公演2',
            type=FamiPortPerformanceType.Normal.value,
            searchable=False,
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            start_at=datetime(2015, 10, 1, 0, 0, 0),
            ticket_name=None
            )
        self.session.add(self.performance)
        self.session.flush()
        self.sales_segment = FamiPortSalesSegment(
            famiport_performance=self.performance,
            userside_id=None,
            code=u'000',
            name=u'受付区分1',
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            published_at=datetime(2015, 5, 1, 0, 0, 0),
            start_at=datetime(2015, 6, 1, 0, 0, 0),
            end_at=datetime(2015, 9, 30, 0, 0, 0),
            auth_required=False,
            auth_message=None,
            seat_selection_start_at=datetime(2015, 7, 1, 0, 0, 0)
            )
        self.order_cash_on_delivery = FamiPortOrder(
            client_code=u'00000000000000000000001',
            famiport_sales_segment=self.sales_segment,
            order_no=u'XX000012345',
            famiport_order_identifier=u'012301230123',
            type=FamiPortOrderType.CashOnDelivery.value,
            total_amount=Decimal(10400),
            ticket_payment=Decimal(10000),
            system_fee=Decimal(200),
            ticketing_fee=Decimal(200),
            payment_start_at=datetime(2015, 6, 3, 0, 0, 0),
            payment_due_at=datetime(2015, 6, 5, 0, 0, 0),
            ticketing_start_at=datetime(2015, 6, 3, 0, 0, 0),
            ticketing_end_at=datetime(2015, 6, 5, 0, 0, 0),
            customer_name=u'テスト　太郎',
            customer_address_1=u'東京都品川区西五反田7-1-9',
            customer_address_2=u'五反田HSビル9F',
            customer_phone_number=u'0123456789',
            famiport_receipts=[
                FamiPortReceipt(
                    type=FamiPortReceiptType.CashOnDelivery.value,
                    barcode_no=u'0000000000001',
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
            )
        self.session.add(self.order_cash_on_delivery)
        self.order_payment = FamiPortOrder(
            client_code=u'00000000000000000000001',
            famiport_sales_segment=self.sales_segment,
            order_no=u'XX000012346',
            famiport_order_identifier=u'012301230124',
            type=FamiPortOrderType.Payment.value,
            total_amount=Decimal(10400),
            ticket_payment=Decimal(10000),
            system_fee=Decimal(200),
            ticketing_fee=Decimal(200),
            payment_start_at=datetime(2015, 6, 3, 0, 0, 0),
            payment_due_at=datetime(2015, 6, 5, 0, 0, 0),
            ticketing_start_at=datetime(2015, 6, 3, 0, 0, 0),
            ticketing_end_at=datetime(2015, 6, 5, 0, 0, 0),
            customer_name=u'テスト　太郎',
            customer_address_1=u'東京都品川区西五反田7-1-9',
            customer_address_2=u'五反田HSビル9F',
            customer_phone_number=u'0123456789',
            famiport_receipts=[
                FamiPortReceipt(
                    type=FamiPortReceiptType.Payment.value,
                    barcode_no=u'0000000000002',
                    famiport_order_identifier=u'000011112224',
                    shop_code=u'00009',
                    reserve_number=u'4321043210433'
                    ),
                FamiPortReceipt(
                    type=FamiPortReceiptType.Ticketing.value,
                    barcode_no=u'0000000000003',
                    famiport_order_identifier=u'000011112225',
                    shop_code=u'00009',
                    reserve_number=u'4321043210434'
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
            )
        self.session.add(self.order_payment)
        self.session.flush()

    def tearDown(self):
        _teardown_db(self.config.registry)
        tearDown()

    def test_it(self):
        from .internal_api import cancel_famiport_order_by_order_no
        cancel_famiport_order_by_order_no(
            self.request,
            self.session,
            client_code=u'00000000000000000000001',
            order_no=self.order_cash_on_delivery.order_no,
            now=datetime(2015, 6, 4, 12, 34, 56)
            )
        self.assertEqual(self.order_cash_on_delivery.canceled_at, datetime(2015, 6, 4, 12, 34, 56))
        self.assertEqual(self.order_cash_on_delivery.famiport_receipts[0].canceled_at, datetime(2015, 6, 4, 12, 34, 56))

    def test_cancel_pending(self):
        from .exc import FamiPortError
        from .internal_api import cancel_famiport_order_by_order_no
        self.order_cash_on_delivery.famiport_receipts[0].payment_request_received_at = datetime(2015, 6, 4, 1, 2, 3)
        with self.assertRaises(FamiPortError):
            cancel_famiport_order_by_order_no(
                self.request,
                self.session,
                client_code=u'00000000000000000000001',
                order_no=self.order_cash_on_delivery.order_no,
                now=datetime(2015, 6, 4, 12, 34, 56)
                )


class UpdateFamiPortOrderTest(unittest.TestCase):
    def setUp(self):
        self.request = DummyRequest()
        self.config = setUp(request=self.request)
        self.engine = _setup_db(
            self.config.registry,
            [
                'altair.app.ticketing.famiport.models',
                ])
        from altair.sqlahelper import get_db_session
        self.session = get_db_session(self.request, 'famiport')
        from .models import (
            FamiPortOrder,
            FamiPortOrderType,
            FamiPortClient,
            FamiPortPlayguide,
            FamiPortPrefecture,
            FamiPortSalesChannel,
            FamiPortVenue,
            FamiPortEvent,
            FamiPortPerformance,
            FamiPortPerformanceType,
            FamiPortSalesSegment,
            FamiPortGenre1,
            FamiPortGenre2,
            FamiPortTicket,
            FamiPortTicketType,
            )
        self.client = FamiPortClient(
            code=u'00000000000000000000001',
            name=u'チケットスター',
            prefix=u'000',
            playguide=FamiPortPlayguide(discrimination_code=5, discrimination_code_2=4)
            )
        self.session.add(self.client)
        self.venue = FamiPortVenue(
            client_code=u'00000000000000000000001',
            userside_id=None,
            name=u'テスト会場',
            name_kana=u'テストカイジョウ',
            prefecture=FamiPortPrefecture.Tokyo.id,
            )
        self.session.add(self.venue)
        self.genre_1 = FamiPortGenre1(code=u'00000', name=u'大ジャンル')
        self.session.add(self.genre_1)
        self.genre_2 = FamiPortGenre2(genre_1=self.genre_1, code=u'00000', name=u'小ジャンル')
        self.session.add(self.genre_2)
        self.session.flush()
        self.event = FamiPortEvent(
            client_code=u'00000000000000000000001',
            name_1=u'テストイベント1',
            name_2=u'テスト1',
            code_1=u'000001',
            code_2=u'0000',
            sales_channel=FamiPortSalesChannel.FamiPortOnly.value,
            venue_id=self.venue.id,
            purchasable_prefectures=[FamiPortPrefecture.Nationwide.id],
            start_at=datetime(2015, 10, 1, 0, 0, 0),
            end_at=datetime(2015, 12, 31, 23, 59, 59),
            genre_1=self.genre_1,
            genre_2=self.genre_2,
            keywords=[],
            search_code=u'00000000'
            )
        self.session.add(self.event)
        self.session.flush()
        self.another_event = FamiPortEvent(
            client_code=u'00000000000000000000001',
            name_1=u'テストイベント2',
            name_2=u'テスト2',
            code_1=u'000002',
            code_2=u'0000',
            sales_channel=FamiPortSalesChannel.FamiPortOnly.value,
            venue_id=self.venue.id,
            purchasable_prefectures=[FamiPortPrefecture.Nationwide.id],
            start_at=datetime(2015, 10, 1, 0, 0, 0),
            end_at=datetime(2015, 12, 31, 23, 59, 59),
            genre_1=self.genre_1,
            genre_2=self.genre_2,
            keywords=[],
            search_code=u'00000000'
            )
        self.session.add(self.another_event)
        self.session.flush()
        self.performance = FamiPortPerformance(
            userside_id=None,
            famiport_event_id=self.event.id,
            code=u'000',
            name=u'公演1',
            type=FamiPortPerformanceType.Normal.value,
            searchable=False,
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            start_at=datetime(2015, 10, 1, 0, 0, 0),
            ticket_name=None
            )
        self.session.add(self.performance)
        self.another_performance = FamiPortPerformance(
            userside_id=None,
            famiport_event_id=self.another_event.id,
            code=u'000',
            name=u'公演2',
            type=FamiPortPerformanceType.Normal.value,
            searchable=False,
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            start_at=datetime(2015, 10, 1, 0, 0, 0),
            ticket_name=None
            )
        self.session.add(self.performance)
        self.session.flush()
        self.sales_segment = FamiPortSalesSegment(
            famiport_performance=self.performance,
            userside_id=None,
            code=u'000',
            name=u'受付区分1',
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            published_at=datetime(2015, 5, 1, 0, 0, 0),
            start_at=datetime(2015, 6, 1, 0, 0, 0),
            end_at=datetime(2015, 9, 30, 0, 0, 0),
            auth_required=False,
            auth_message=None,
            seat_selection_start_at=datetime(2015, 7, 1, 0, 0, 0)
            )
        self.order_cash_on_delivery = FamiPortOrder(
            client_code=u'00000000000000000000001',
            famiport_sales_segment=self.sales_segment,
            order_no=u'XX000012345',
            famiport_order_identifier=u'012301230123',
            type=FamiPortOrderType.CashOnDelivery.value,
            total_amount=Decimal(10400),
            ticket_payment=Decimal(10000),
            system_fee=Decimal(200),
            ticketing_fee=Decimal(200),
            payment_start_at=datetime(2015, 6, 3, 0, 0, 0),
            payment_due_at=datetime(2015, 6, 5, 0, 0, 0),
            ticketing_start_at=datetime(2015, 6, 3, 0, 0, 0),
            ticketing_end_at=datetime(2015, 6, 5, 0, 0, 0),
            customer_name=u'テスト　太郎',
            customer_address_1=u'東京都品川区西五反田7-1-9',
            customer_address_2=u'五反田HSビル9F',
            customer_phone_number=u'0123456789',
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
            )
        self.session.add(self.order_cash_on_delivery)
        self.order_payment = FamiPortOrder(
            client_code=u'00000000000000000000001',
            famiport_sales_segment=self.sales_segment,
            order_no=u'XX000012346',
            famiport_order_identifier=u'012301230124',
            type=FamiPortOrderType.Payment.value,
            total_amount=Decimal(10400),
            ticket_payment=Decimal(10000),
            system_fee=Decimal(200),
            ticketing_fee=Decimal(200),
            payment_start_at=datetime(2015, 6, 3, 0, 0, 0),
            payment_due_at=datetime(2015, 6, 5, 0, 0, 0),
            ticketing_start_at=datetime(2015, 6, 3, 0, 0, 0),
            ticketing_end_at=datetime(2015, 6, 5, 0, 0, 0),
            customer_name=u'テスト　太郎',
            customer_address_1=u'東京都品川区西五反田7-1-9',
            customer_address_2=u'五反田HSビル9F',
            customer_phone_number=u'0123456789',
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
            )
        self.session.add(self.order_payment)
        self.session.flush()

    def tearDown(self):
        _teardown_db(self.config.registry)
        tearDown()

    def test_none_updated(self):
        from .internal_api import update_famiport_order_by_order_no
        update_famiport_order_by_order_no(
            self.session,
            order_no=u'XX000012345',
            client_code=u'00000000000000000000001',
            famiport_order_identifier=None,
            type_=1,
            event_code_1='000001',
            event_code_2='0000',
            performance_code='000',
            sales_segment_code='000',
            customer_name=None,
            customer_phone_number=None,
            customer_address_1=None,
            customer_address_2=None,
            total_amount=None,
            system_fee=None,
            ticketing_fee=None,
            ticket_payment=None,
            tickets=None,
            payment_start_at=None,
            payment_due_at=None,
            ticketing_start_at=None,
            ticketing_end_at=None,
            payment_sheet_text=None,
            require_ticketing_fee_on_ticketing=False
            )

    def test_cash_on_delivery_unupdatable(self):
        from .internal_api import update_famiport_order_by_order_no
        from .exc import FamiPortAlreadyPaidError
        self.order_cash_on_delivery.paid_at = datetime(2015, 6, 4)
        with self.assertRaises(FamiPortAlreadyPaidError):
            update_famiport_order_by_order_no(
                self.session,
                order_no=u'XX000012345',
                client_code=u'00000000000000000000001',
                famiport_order_identifier=None,
                type_=1,
                event_code_1='000001',
                event_code_2='0000',
                performance_code='000',
                sales_segment_code='000',
                customer_name=None,
                customer_phone_number=None,
                customer_address_1=None,
                customer_address_2=None,
                total_amount=None,
                system_fee=None,
                ticketing_fee=None,
                ticket_payment=None,
                tickets=None,
                payment_start_at=datetime(2015, 6, 5),
                payment_due_at=None,
                ticketing_start_at=None,
                ticketing_end_at=None,
                payment_sheet_text=None,
                require_ticketing_fee_on_ticketing=False
                )

    def test_payment_unupdatable(self):
        from .internal_api import update_famiport_order_by_order_no
        from .exc import FamiPortAlreadyPaidError
        self.order_payment.paid_at = datetime(2015, 6, 4)
        with self.assertRaises(FamiPortAlreadyPaidError):
            update_famiport_order_by_order_no(
                self.session,
                order_no=u'XX000012346',
                client_code=u'00000000000000000000001',
                famiport_order_identifier=None,
                type_=2,
                event_code_1='000001',
                event_code_2='0000',
                performance_code='000',
                sales_segment_code='000',
                customer_name=None,
                customer_phone_number=None,
                customer_address_1=None,
                customer_address_2=None,
                total_amount=None,
                system_fee=None,
                ticketing_fee=None,
                ticket_payment=None,
                tickets=None,
                payment_start_at=datetime(2015, 6, 5),
                payment_due_at=None,
                ticketing_start_at=None,
                ticketing_end_at=None,
                payment_sheet_text=None,
                require_ticketing_fee_on_ticketing=False
                )

    def test_payment_updatable(self):
        from .internal_api import update_famiport_order_by_order_no
        from .exc import FamiPortAlreadyPaidError
        self.order_payment.paid_at = datetime(2015, 6, 4)
        update_famiport_order_by_order_no(
            self.session,
            order_no=u'XX000012346',
            client_code=u'00000000000000000000001',
            famiport_order_identifier=None,
            type_=2,
            event_code_1='000001',
            event_code_2='0000',
            performance_code='000',
            sales_segment_code='000',
            customer_name=None,
            customer_phone_number=None,
            customer_address_1=None,
            customer_address_2=None,
            total_amount=None,
            system_fee=None,
            ticketing_fee=None,
            ticket_payment=None,
            tickets=None,
            payment_start_at=None,
            payment_due_at=None,
            ticketing_start_at=datetime(2015, 6, 6),
            ticketing_end_at=datetime(2015, 6, 7),
            payment_sheet_text=None,
            require_ticketing_fee_on_ticketing=False
            )
