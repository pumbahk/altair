# encoding:utf-8
import unittest
from .testing import _setup_db, _teardown_db
from datetime import datetime
from decimal import Decimal
from pyramid.testing import setUp, tearDown, DummyRequest

class GetFamiPortOrderTest(unittest.TestCase):
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
        self.order = FamiPortOrder(
            client_code=u'00000000000000000000001',
            famiport_sales_segment=self.sales_segment,
            famiport_performance=self.performance,
            order_no=u'XX000012345',
            famiport_order_identifier=u'012301230123',
            type=FamiPortOrderType.CashOnDelivery.value,
            total_amount=Decimal(10400),
            ticket_payment=Decimal(10000),
            system_fee=Decimal(200),
            ticketing_fee=Decimal(200),
            customer_name=u'テスト　太郎',
            customer_address_1=u'東京都品川区西五反田7-1-9',
            customer_address_2=u'五反田HSビル9F',
            customer_phone_number=u'0123456789'
            )
        self.session.add(self.order)
        self.session.flush()

    def tearDown(self):
        _teardown_db(self.config.registry)
        tearDown()

    def test_get_famiport_order(self):
        from .api import get_famiport_order
        famiport_order = get_famiport_order(self.request, u'00000000000000000000001', u'XX000012345')


class FamiPortCreateOrUpdateFamiPortVenueTest(unittest.TestCase):
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
        from .models import FamiPortClient, FamiPortPlayguide
        self.client = FamiPortClient(
            code=u'00000000000000000000001',
            name=u'チケットスター',
            prefix=u'000',
            playguide=FamiPortPlayguide(discrimination_code=5, discrimination_code_2=4)
            )
        self.session.add(self.client)
        self.session.flush()

    def tearDown(self):
        _teardown_db(self.config.registry)
        tearDown()

    def test_it(self):
        from .api import create_or_update_famiport_venue
        from .models import FamiPortPrefecture
    
        result = create_or_update_famiport_venue(
            self.request,
            client_code=u'00000000000000000000001',
            id=None,
            userside_id=None,
            name=u'テスト会場',
            name_kana=u'テストカイジョウ',
            prefecture=FamiPortPrefecture.Tokyo.id, 
            update_existing=False
            )
        self.assertEqual(result, dict(new=True, venue_id=1))

    def test_try_update_existing(self):
        from .api import create_or_update_famiport_venue
        from .models import FamiPortPrefecture
    
        result = create_or_update_famiport_venue(
            self.request,
            client_code=u'00000000000000000000001',
            id=None,
            userside_id=None,
            name=u'テスト会場',
            name_kana=u'テストカイジョウ',
            prefecture=FamiPortPrefecture.Tokyo.id, 
            update_existing=True
            )
        self.assertEqual(result, dict(new=True, venue_id=1))

    def test_update_existing_without_id(self):
        from .api import create_or_update_famiport_venue
        from .models import FamiPortPrefecture, FamiPortVenue

        existing = FamiPortVenue( 
            client_code=u'00000000000000000000001',
            userside_id=None,
            name=u'テスト会場',
            name_kana=u'テストカイジョウ',
            prefecture=FamiPortPrefecture.Tokyo.id
            )
        self.session.add(existing)
        self.session.flush()
    
        result = create_or_update_famiport_venue(
            self.request,
            client_code=u'00000000000000000000001',
            id=None,
            userside_id=None,
            name=u'テスト会場',
            name_kana=u'テストカイジョウ',
            prefecture=FamiPortPrefecture.Aomori.id, 
            update_existing=True
            )
        self.assertEqual(result, dict(new=False, venue_id=1))
        venue = self.session.query(FamiPortVenue).filter_by(id=1).one()
        self.assertEqual(venue.prefecture, FamiPortPrefecture.Aomori.id)

    def test_update_existing_with_id(self):
        from .api import create_or_update_famiport_venue
        from .models import FamiPortPrefecture, FamiPortVenue

        existing = FamiPortVenue( 
            client_code=u'00000000000000000000001',
            userside_id=None,
            name=u'テスト会場',
            name_kana=u'テストカイジョウ',
            prefecture=FamiPortPrefecture.Tokyo.id
            )
        self.session.add(existing)
        self.session.flush()
    
        result = create_or_update_famiport_venue(
            self.request,
            client_code=u'00000000000000000000001',
            id=1,
            userside_id=None,
            name=u'テストー会場',
            name_kana=u'テストカイジョウ',
            prefecture=FamiPortPrefecture.Aomori.id, 
            update_existing=True
            )
        self.assertEqual(result, dict(new=False, venue_id=1))
        venue = self.session.query(FamiPortVenue).filter_by(id=1).one()
        self.assertEqual(venue.prefecture, FamiPortPrefecture.Aomori.id)


class FamiPortCreateOrUpdateFamiPortEventTest(unittest.TestCase):
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
            FamiPortClient,
            FamiPortPlayguide,
            FamiPortPrefecture,
            FamiPortVenue,
            FamiPortGenre1,
            FamiPortGenre2,
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

    def tearDown(self):
        _teardown_db(self.config.registry)
        tearDown()

    def test_it(self):
        from .models import FamiPortSalesChannel, FamiPortPrefecture
        from .api import create_or_update_famiport_event
        result = create_or_update_famiport_event(
            self.request,
            client_code=u'00000000000000000000001',
            userside_id=None,
            code_1=u'000000',
            code_2=u'0000',
            name_1=u'テストイベント',
            name_2=u'テスト',
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            venue_id=self.venue.id,
            purchasable_prefectures=[FamiPortPrefecture.Aichi.id],
            start_at=datetime(2015, 10, 1, 0, 0, 0),
            end_at=datetime(2015, 12, 31, 23, 59, 59),
            genre_1_code=u'00000',
            genre_2_code=u'00000',
            keywords=[u'キーワード1', u'キーワード2'],
            search_code=u'00000001',
            update_existing=False
            )
        self.assertEqual(result, dict(new=True))

    def test_try_update_existing(self):
        from .models import FamiPortSalesChannel, FamiPortPrefecture, FamiPortEvent
        from .api import create_or_update_famiport_event

        event = FamiPortEvent(
            client_code=u'00000000000000000000001',
            name_1=u'テストイベント',
            name_2=u'テスト',
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
        self.session.add(event)

        result = create_or_update_famiport_event(
            self.request,
            client_code=u'00000000000000000000001',
            userside_id=None,
            code_1=u'000000',
            code_2=u'0000',
            name_1=u'テストイベント',
            name_2=u'テスト',
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            venue_id=self.venue.id,
            purchasable_prefectures=[FamiPortPrefecture.Aichi.id],
            start_at=datetime(2015, 10, 1, 0, 0, 0),
            end_at=datetime(2015, 12, 31, 23, 59, 59),
            genre_1_code=u'00000',
            genre_2_code=u'00000',
            keywords=[u'キーワード1', u'キーワード2'],
            search_code=u'00000001',
            update_existing=True
            )
        self.assertEqual(result, dict(new=True))
        self.assertEqual(self.session.query(FamiPortEvent).count(), 2)
        self.assertEqual(self.session.query(FamiPortEvent).filter(FamiPortEvent.invalidated_at != None).count(), 0)

    def test_update_existing(self):
        from .models import FamiPortSalesChannel, FamiPortPrefecture, FamiPortEvent
        from .api import create_or_update_famiport_event

        event = FamiPortEvent(
            client_code=u'00000000000000000000001',
            name_1=u'テストイベント',
            name_2=u'テスト',
            code_1=u'000000',
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
        self.session.add(event)

        result = create_or_update_famiport_event(
            self.request,
            client_code=u'00000000000000000000001',
            userside_id=None,
            code_1=u'000000',
            code_2=u'0000',
            name_1=u'テストイベント',
            name_2=u'テスト',
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            venue_id=self.venue.id,
            purchasable_prefectures=[FamiPortPrefecture.Aichi.id],
            start_at=datetime(2015, 10, 1, 0, 0, 0),
            end_at=datetime(2015, 12, 31, 23, 59, 59),
            genre_1_code=u'00000',
            genre_2_code=u'00000',
            keywords=[u'キーワード1', u'キーワード2'],
            search_code=u'00000001',
            update_existing=True
            )
        self.assertEqual(result, dict(new=False))
        self.assertEqual(self.session.query(FamiPortEvent).count(), 2)
        self.assertEqual(self.session.query(FamiPortEvent).filter(FamiPortEvent.invalidated_at != None).count(), 1)


class FamiPortCreateOrUpdateFamiPortPerformanceTest(unittest.TestCase):
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
            FamiPortClient,
            FamiPortPlayguide,
            FamiPortPrefecture,
            FamiPortSalesChannel,
            FamiPortVenue,
            FamiPortEvent,
            FamiPortGenre1,
            FamiPortGenre2,
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
            name_1=u'テストイベント',
            name_2=u'テスト',
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

    def tearDown(self):
        _teardown_db(self.config.registry)
        tearDown()

    def test_normal(self):
        from .models import FamiPortSalesChannel, FamiPortPerformanceType
        from .api import create_or_update_famiport_performance
        result = create_or_update_famiport_performance(
            self.request,
            client_code='00000000000000000000001',
            userside_id=None,
            event_code_1=self.event.code_1,
            event_code_2=self.event.code_2,
            code=u'000',
            name=u'公演',
            type_=FamiPortPerformanceType.Normal.value,
            searchable=True,
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            start_at=datetime(2015, 10, 1, 0, 0, 0),
            ticket_name=None,
            update_existing=False
            )
        self.assertEqual(result, dict(new=True))

    def test_normal_fail(self):
        from .models import FamiPortSalesChannel, FamiPortPerformanceType
        from .api import create_or_update_famiport_performance
        from .exc import FamiPortAPIError
        with self.assertRaises(FamiPortAPIError):
            create_or_update_famiport_performance(
                self.request,
                client_code='00000000000000000000001',
                userside_id=None,
                event_code_1=self.event.code_1,
                event_code_2=self.event.code_2,
                code=u'000',
                name=u'公演',
                type_=FamiPortPerformanceType.Normal.value,
                searchable=True,
                sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
                start_at=datetime(2015, 10, 1, 0, 0, 0),
                ticket_name=u'ticket_name',
                update_existing=False
                )

    def test_spanned(self):
        from .models import FamiPortSalesChannel, FamiPortPerformanceType
        from .api import create_or_update_famiport_performance
        result = create_or_update_famiport_performance(
            self.request,
            client_code='00000000000000000000001',
            userside_id=None,
            event_code_1=self.event.code_1,
            event_code_2=self.event.code_2,
            code=u'000',
            name=u'公演',
            type_=FamiPortPerformanceType.Spanned.value,
            searchable=True,
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            start_at=datetime(2015, 10, 1, 0, 0, 0),
            ticket_name=u'ticket_name',
            update_existing=False
            )
        self.assertEqual(result, dict(new=True))

    def test_spanned_fail(self):
        from .models import FamiPortSalesChannel, FamiPortPerformanceType
        from .api import create_or_update_famiport_performance
        from .exc import FamiPortAPIError
        with self.assertRaises(FamiPortAPIError):
            create_or_update_famiport_performance(
                self.request,
                client_code='00000000000000000000001',
                userside_id=None,
                event_code_1=self.event.code_1,
                event_code_2=self.event.code_2,
                code=u'000',
                name=u'公演',
                type_=FamiPortPerformanceType.Spanned.value,
                searchable=True,
                sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
                start_at=datetime(2015, 10, 1, 0, 0, 0),
                ticket_name=None,
                update_existing=False
                )

    def test_update_existing(self):
        from .models import FamiPortSalesChannel, FamiPortPerformance, FamiPortPerformanceType
        from .api import create_or_update_famiport_performance

        performance = FamiPortPerformance(
            userside_id=None,
            famiport_event_id=self.event.id,
            code=u'000',
            name=u'公演',
            type=FamiPortPerformanceType.Normal.value,
            searchable=False,
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            start_at=datetime(2015, 10, 1, 0, 0, 0),
            ticket_name=None
            )
        self.session.add(performance)
        self.session.flush()

        result = create_or_update_famiport_performance(
            self.request,
            client_code='00000000000000000000001',
            userside_id=None,
            event_code_1=self.event.code_1,
            event_code_2=self.event.code_2,
            code=u'000',
            name=u'公演',
            type_=FamiPortPerformanceType.Normal.value,
            searchable=True,
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            start_at=datetime(2015, 10, 1, 0, 0, 0),
            ticket_name=None,
            update_existing=True
            )
        self.assertEqual(result, dict(new=False))

class FamiPortCreateOrUpdateFamiPortSalesSegmentTest(unittest.TestCase):
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
            FamiPortClient,
            FamiPortPlayguide,
            FamiPortPrefecture,
            FamiPortSalesChannel,
            FamiPortVenue,
            FamiPortEvent,
            FamiPortPerformance,
            FamiPortPerformanceType,
            FamiPortGenre1,
            FamiPortGenre2,
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

    def tearDown(self):
        _teardown_db(self.config.registry)
        tearDown()

    def test_it(self):
        from .api import create_or_update_famiport_sales_segment
        from .models import FamiPortSalesChannel
        result = create_or_update_famiport_sales_segment(
            self.request,
            client_code=u'00000000000000000000001',
            userside_id=None,
            event_code_1=u'000001',
            event_code_2=u'0000',
            performance_code=u'000',
            code=u'000',
            name=u'受付区分1',
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            published_at=datetime(2015, 5, 1, 0, 0, 0),
            start_at=datetime(2015, 6, 1, 0, 0, 0),
            end_at=datetime(2015, 9, 30, 0, 0, 0),
            auth_required=False,
            auth_message=None,
            seat_selection_start_at=datetime(2015, 7, 1, 0, 0, 0),
            update_existing=False
            )
        self.assertEqual(result, dict(new=True))

class CreateFamiPortOrderTest(unittest.TestCase):
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
            FamiPortClient,
            FamiPortPlayguide,
            FamiPortPrefecture,
            FamiPortSalesChannel,
            FamiPortVenue,
            FamiPortEvent,
            FamiPortPerformance,
            FamiPortPerformanceType,
            FamiPortGenre1,
            FamiPortGenre2,
            FamiPortSalesSegment,
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
            famiport_performance_id=self.performance.id,
            code=u'000',
            name=u'テスト',
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            published_at=datetime(2015, 5, 1),
            start_at=datetime(2015, 7, 1),
            end_at=datetime(2015, 9, 30),
            auth_required=False,
            seat_selection_start_at=datetime(2015, 8, 1)
            )
        self.session.add(self.sales_segment)
        self.session.flush()

    def tearDown(self):
        _teardown_db(self.config.registry)
        tearDown()

    def test_it(self):
        from .models import FamiPortOrderType, FamiPortTicketType
        from decimal import Decimal
        from datetime import datetime
        from .api import create_famiport_order
        create_famiport_order(
            self.request,
            client_code=self.client.code,
            type_=FamiPortOrderType.CashOnDelivery.value,
            event_code_1=self.event.code_1,
            event_code_2=self.event.code_2,
            performance_code=self.performance.code,
            sales_segment_code=self.sales_segment.code,
            order_no=u'XX0000000000',
            customer_name=u'購入者　氏名',
            customer_phone_number=u'0123456789',
            customer_address_1=u'住所1',
            customer_address_2=u'住所2',
            total_amount=Decimal(1432),
            ticketing_fee=Decimal(216),
            system_fee=Decimal(216),
            ticket_payment=Decimal(1000),
            tickets=[
                dict(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_no=u'0000000000001',
                    template=u'TTEV000001',
                    data=u'<ticket>test</ticket>',
                    price=500,
                    userside_id=1,
                    userside_token_id=1,
                    logically_subticket=False
                    ),
                dict(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_no=u'0000000000001',
                    template=u'TTEV000001',
                    data=u'<ticket>test</ticket>',
                    price=500,
                    userside_id=2,
                    userside_token_id=2,
                    logically_subticket=False
                    )
                ],
            payment_start_at=datetime(2015, 6, 1, 0, 0, 0),
            payment_due_at=datetime(2015, 6, 4, 0, 0, 0)
            )

    def test_without_sales_segment(self):
        from .models import FamiPortOrderType, FamiPortTicketType
        from decimal import Decimal
        from datetime import datetime
        from .api import create_famiport_order
        create_famiport_order(
            self.request,
            client_code=self.client.code,
            type_=FamiPortOrderType.CashOnDelivery.value,
            event_code_1=self.event.code_1,
            event_code_2=self.event.code_2,
            performance_code=self.performance.code,
            sales_segment_code=None,
            order_no=u'XX0000000000',
            customer_name=u'購入者　氏名',
            customer_phone_number=u'0123456789',
            customer_address_1=u'住所1',
            customer_address_2=u'住所2',
            total_amount=Decimal(1432),
            ticketing_fee=Decimal(216),
            system_fee=Decimal(216),
            ticket_payment=Decimal(1000),
            tickets=[
                dict(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_no=u'0000000000001',
                    template=u'TTEV000001',
                    data=u'<ticket>test</ticket>',
                    price=500,
                    userside_id=1,
                    userside_token_id=1,
                    logically_subticket=False
                    ),
                dict(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_no=u'0000000000001',
                    template=u'TTEV000001',
                    data=u'<ticket>test</ticket>',
                    price=500,
                    userside_id=2,
                    userside_token_id=2,
                    logically_subticket=False
                    )
                ],
            payment_start_at=datetime(2015, 6, 1, 0, 0, 0),
            payment_due_at=datetime(2015, 6, 4, 0, 0, 0)
            )


class MoveOrdersToNewPerformanceTest(unittest.TestCase):
    def setUp(self):
        from altair.sqlahelper import get_db_session
        self._request = DummyRequest()
        self._config = setUp(request=self._request)
        self._engine = _setup_db(self._config.registry,['altair.app.ticketing.famiport.models'])
        self._session = get_db_session(self._request, 'famiport')

    def tearDown(self):
        _teardown_db(self._config.registry)
        tearDown()

    @staticmethod
    def _call_test_target(*args, **kwargs):
        from altair.app.ticketing.famiport.api import move_orders_to_new_performance
        return move_orders_to_new_performance(*args, **kwargs)

    def _make_base_test_data(self):
        from altair.app.ticketing.famiport.models import (
            FamiPortVenue,
            FamiPortEvent,
            FamiPortPerformance,
            FamiPortOrder,
            FamiPortSalesChannel,
            FamiPortPrefecture,
            FamiPortPerformanceType,
            FamiPortOrderType,
            FamiPortSalesSegment
        )
        self._venue = FamiPortVenue(
            client_code=u'00000000000000000000001',
            userside_id=None,
            name=u'テスト会場',
            name_kana=u'テストカイジョウ',
            prefecture=FamiPortPrefecture.Tokyo.id,
        )
        self._session.add(self._venue)
        self._session.flush()

        self._old_event = FamiPortEvent(
            client_code=u'00000000000000000000001',
            name_1=u'テストイベント1',
            name_2=u'テスト1',
            code_1=u'000001',
            code_2=u'0000',
            sales_channel=FamiPortSalesChannel.FamiPortOnly.value,
            venue_id=self._venue.id,
            purchasable_prefectures=[FamiPortPrefecture.Nationwide.id],
            start_at=datetime(2015, 10, 1, 0, 0, 0),
            end_at=datetime(2015, 12, 31, 23, 59, 59),
            keywords=[],
            search_code=u'00000000',
            invalidated_at=datetime(2016, 10, 1, 0, 0, 0)
        )
        self._session.add(self._old_event)
        self._session.flush()

        self._old_performance = FamiPortPerformance(
            userside_id=1,
            famiport_event_id=self._old_event.id,
            code=u'000',
            name=u'公演1',
            type=FamiPortPerformanceType.Normal.value,
            searchable=False,
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            start_at=datetime(2015, 10, 1, 0, 0, 0),
            ticket_name=None
        )
        self._session.add(self._old_performance)
        self._session.flush()

        self._old_sales_segment = FamiPortSalesSegment(
            famiport_performance_id=self._old_performance.id,
            code=u'000',
            name=u'テスト',
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            published_at=datetime(2015, 5, 1),
            start_at=datetime(2015, 7, 1),
            end_at=datetime(2015, 9, 30),
            auth_required=False,
            seat_selection_start_at=datetime(2015, 8, 1)
        )
        self._session.add(self._old_sales_segment)
        self._session.flush()

        self._order = FamiPortOrder(
            client_code=u'00000000000000000000001',
            famiport_sales_segment=self._old_sales_segment,
            famiport_performance=self._old_performance,
            order_no=u'XX000012345',
            famiport_order_identifier=u'012301230123',
            type=FamiPortOrderType.CashOnDelivery.value,
            total_amount=Decimal(10400),
            ticket_payment=Decimal(10000),
            system_fee=Decimal(200),
            ticketing_fee=Decimal(200),
            customer_name=u'テスト　太郎',
            customer_address_1=u'東京都品川区西五反田7-1-9',
            customer_address_2=u'五反田HSビル9F',
            customer_phone_number=u'0123456789'
        )
        self._session.add(self._order)
        self._session.flush()

        self._new_event = FamiPortEvent(
            client_code=u'00000000000000000000001',
            name_1=u'テストイベント1',
            name_2=u'テスト1',
            code_1=u'000001',
            code_2=u'0002',
            sales_channel=FamiPortSalesChannel.FamiPortOnly.value,
            venue_id=self._venue.id,
            purchasable_prefectures=[FamiPortPrefecture.Nationwide.id],
            start_at=datetime(2015, 10, 1, 0, 0, 0),
            end_at=datetime(2015, 12, 31, 23, 59, 59),
            keywords=[],
            search_code=u'00000000'
        )
        self._session.add(self._new_event)
        self._session.flush()

        self._new_performance = FamiPortPerformance(
            userside_id=self._old_performance.userside_id,
            famiport_event_id=self._new_event.id,
            code=u'001',
            name=u'公演1',
            type=FamiPortPerformanceType.Normal.value,
            searchable=False,
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            start_at=datetime(2015, 10, 1, 0, 0, 0),
            ticket_name=None
        )
        self._session.add(self._new_performance)
        self._session.flush()

    def test_move_orders(self):
        """ move_orders_to_new_performance正常系テスト FamiPortOrderの移動 """
        self._make_base_test_data()
        result = self._call_test_target(
            self._request,
            self._old_event.client_code,
            self._new_performance.userside_id,
            self._new_event.code_1,
            self._new_event.code_2,
            self._new_performance.code
        )
        self.assertEqual(result[u'number_of_moved_order'], 1)
        self.assertEqual(self._order.famiport_performance.id, self._new_performance.id)

    def test_no_orders_to_move(self):
        """ move_orders_to_new_performance正常系テスト 移動するFamiPortOrderなし """
        self._make_base_test_data()
        userside_id_no_existence = -1
        result = self._call_test_target(
            self._request,
            self._old_event.client_code,
            userside_id_no_existence,
            self._new_event.code_1,
            self._new_event.code_2,
            self._new_performance.code
        )
        self.assertEqual(result[u'number_of_moved_order'], 0)
        self.assertEqual(self._order.famiport_performance.id, self._old_performance.id)

    def test_no_event(self):
        """ move_orders_to_new_performance異常系テスト 対象イベントなし """
        from altair.app.ticketing.famiport.exc import FamiPortAPINotFoundError
        self._make_base_test_data()
        client_code_no_existence = -1
        with self.assertRaises(FamiPortAPINotFoundError):
            self._call_test_target(
                self._request,
                client_code_no_existence,
                self._new_performance.userside_id,
                self._new_event.code_1,
                self._new_event.code_2,
                self._new_performance.code
            )

    def test_no_performance(self):
        """ move_orders_to_new_performance異常系テスト 対象公演なし """
        from altair.app.ticketing.famiport.exc import FamiPortAPINotFoundError
        self._make_base_test_data()
        performance_code_no_existence = -1

        with self.assertRaises(FamiPortAPINotFoundError):
            self._call_test_target(
                self._request,
                self._old_event.client_code,
                self._new_performance.userside_id,
                self._new_event.code_1,
                self._new_event.code_2,
                performance_code_no_existence
            )


class MoveOrdersToNewSalesSegmentTest(unittest.TestCase):
    def setUp(self):
        from altair.sqlahelper import get_db_session
        self._request = DummyRequest()
        self._config = setUp(request=self._request)
        self._engine = _setup_db(self._config.registry,['altair.app.ticketing.famiport.models'])
        self._session = get_db_session(self._request, 'famiport')

    def tearDown(self):
        _teardown_db(self._config.registry)
        tearDown()

    @staticmethod
    def _call_test_target(*args, **kwargs):
        from altair.app.ticketing.famiport.api import move_orders_to_new_sales_segment
        return move_orders_to_new_sales_segment(*args, **kwargs)

    def _make_base_test_data(self):
        from altair.app.ticketing.famiport.models import (
            FamiPortVenue,
            FamiPortEvent,
            FamiPortPerformance,
            FamiPortOrder,
            FamiPortSalesChannel,
            FamiPortPrefecture,
            FamiPortPerformanceType,
            FamiPortOrderType,
            FamiPortSalesSegment
        )
        self._venue = FamiPortVenue(
            client_code=u'00000000000000000000001',
            userside_id=None,
            name=u'テスト会場',
            name_kana=u'テストカイジョウ',
            prefecture=FamiPortPrefecture.Tokyo.id,
        )
        self._session.add(self._venue)
        self._session.flush()

        self._old_event = FamiPortEvent(
            client_code=u'00000000000000000000001',
            name_1=u'テストイベント1',
            name_2=u'テスト1',
            code_1=u'000001',
            code_2=u'0000',
            sales_channel=FamiPortSalesChannel.FamiPortOnly.value,
            venue_id=self._venue.id,
            purchasable_prefectures=[FamiPortPrefecture.Nationwide.id],
            start_at=datetime(2015, 10, 1, 0, 0, 0),
            end_at=datetime(2015, 12, 31, 23, 59, 59),
            keywords=[],
            search_code=u'00000000',
            invalidated_at=datetime(2016, 10, 1, 0, 0, 0)
        )
        self._session.add(self._old_event)
        self._session.flush()

        self._old_performance = FamiPortPerformance(
            userside_id=1,
            famiport_event_id=self._old_event.id,
            code=u'000',
            name=u'公演1',
            type=FamiPortPerformanceType.Normal.value,
            searchable=False,
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            start_at=datetime(2015, 10, 1, 0, 0, 0),
            ticket_name=None
        )
        self._session.add(self._old_performance)
        self._session.flush()

        self._old_sales_segment = FamiPortSalesSegment(
            userside_id=1,
            famiport_performance_id=self._old_performance.id,
            code=u'000',
            name=u'テスト',
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            published_at=datetime(2015, 5, 1),
            start_at=datetime(2015, 7, 1),
            end_at=datetime(2015, 9, 30),
            auth_required=False,
            seat_selection_start_at=datetime(2015, 8, 1)
        )
        self._session.add(self._old_sales_segment)
        self._session.flush()

        self._order = FamiPortOrder(
            client_code=u'00000000000000000000001',
            famiport_sales_segment=self._old_sales_segment,
            famiport_performance=self._old_performance,
            order_no=u'XX000012345',
            famiport_order_identifier=u'012301230123',
            type=FamiPortOrderType.CashOnDelivery.value,
            total_amount=Decimal(10400),
            ticket_payment=Decimal(10000),
            system_fee=Decimal(200),
            ticketing_fee=Decimal(200),
            customer_name=u'テスト　太郎',
            customer_address_1=u'東京都品川区西五反田7-1-9',
            customer_address_2=u'五反田HSビル9F',
            customer_phone_number=u'0123456789'
        )
        self._session.add(self._order)
        self._session.flush()

        self._new_event = FamiPortEvent(
            client_code=u'00000000000000000000001',
            name_1=u'テストイベント1',
            name_2=u'テスト1',
            code_1=u'000001',
            code_2=u'0002',
            sales_channel=FamiPortSalesChannel.FamiPortOnly.value,
            venue_id=self._venue.id,
            purchasable_prefectures=[FamiPortPrefecture.Nationwide.id],
            start_at=datetime(2015, 10, 1, 0, 0, 0),
            end_at=datetime(2015, 12, 31, 23, 59, 59),
            keywords=[],
            search_code=u'00000000'
        )
        self._session.add(self._new_event)
        self._session.flush()

        self._new_performance = FamiPortPerformance(
            userside_id=self._old_performance.userside_id,
            famiport_event_id=self._new_event.id,
            code=u'001',
            name=u'公演1',
            type=FamiPortPerformanceType.Normal.value,
            searchable=False,
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            start_at=datetime(2015, 10, 1, 0, 0, 0),
            ticket_name=None
        )
        self._session.add(self._new_performance)
        self._session.flush()

        self._new_sales_segment = FamiPortSalesSegment(
            userside_id=self._old_sales_segment.userside_id,
            famiport_performance_id=self._new_performance.id,
            code=u'001',
            name=u'テスト',
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            published_at=datetime(2015, 5, 1),
            start_at=datetime(2015, 7, 1),
            end_at=datetime(2015, 9, 30),
            auth_required=False,
            seat_selection_start_at=datetime(2015, 8, 1)
        )
        self._session.add(self._new_sales_segment)
        self._session.flush()

    def test_move_orders(self):
        """ move_orders_to_new_sales_segment正常系テスト FamiPortOrderの移動 """
        self._make_base_test_data()
        result = self._call_test_target(
            self._request,
            self._old_event.client_code,
            self._new_sales_segment.userside_id,
            self._new_event.code_1,
            self._new_event.code_2,
            self._new_performance.code,
            self._new_sales_segment.code,
            self._new_sales_segment.name,
            self._new_sales_segment.start_at,
            self._new_sales_segment.end_at
        )
        self.assertEqual(result[u'number_of_moved_order'], 1)
        self.assertEqual(self._order.famiport_sales_segment.id, self._new_sales_segment.id)

    def test_no_orders_to_move(self):
        """ move_orders_to_new_sales_segment正常系テスト 移動するFamiPortOrderなし """
        self._make_base_test_data()
        userside_id_no_existence = -1
        result = self._call_test_target(
            self._request,
            self._old_event.client_code,
            userside_id_no_existence,
            self._new_event.code_1,
            self._new_event.code_2,
            self._new_performance.code,
            self._new_sales_segment.code,
            self._new_sales_segment.name,
            self._new_sales_segment.start_at,
            self._new_sales_segment.end_at
        )
        self.assertEqual(result[u'number_of_moved_order'], 0)
        self.assertEqual(self._order.famiport_sales_segment.id, self._old_sales_segment.id)

    def test_no_performance(self):
        """ move_orders_to_new_sales_segment正常系テスト 対象公演なし """
        from altair.app.ticketing.famiport.exc import FamiPortAPINotFoundError
        self._make_base_test_data()
        performance_code_no_existence = -1
        with self.assertRaises(FamiPortAPINotFoundError):
            self._call_test_target(
                self._request,
                self._old_event.client_code,
                self._new_sales_segment.userside_id,
                self._new_event.code_1,
                self._new_event.code_2,
                performance_code_no_existence,
                self._new_sales_segment.code,
                self._new_sales_segment.name,
                self._new_sales_segment.start_at,
                self._new_sales_segment.end_at
            )

    def test_no_sales_segment(self):
        """ move_orders_to_new_sales_segment正常系テスト 対象販売区分なし """
        from altair.app.ticketing.famiport.exc import FamiPortAPINotFoundError
        self._make_base_test_data()
        sales_segment_code_no_existence = -1
        with self.assertRaises(FamiPortAPINotFoundError):
            self._call_test_target(
                self._request,
                self._old_event.client_code,
                self._new_sales_segment.userside_id,
                self._new_event.code_1,
                self._new_event.code_2,
                self._new_performance.code,
                sales_segment_code_no_existence,
                self._new_sales_segment.name,
                self._new_sales_segment.start_at,
                self._new_sales_segment.end_at
            )
