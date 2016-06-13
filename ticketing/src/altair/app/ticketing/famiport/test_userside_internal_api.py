# encoding:utf-8
import unittest
import mock
from datetime import datetime
from altair.app.ticketing.testing import _setup_db, _teardown_db, DummyRequest
from pyramid.testing import setUp, tearDown
from altair.app.ticketing.core.models import (
    Performance,
    Venue,
    Event,
    Site,
    SiteProfile,
    FamiPortTenant,
    Organization,
    SalesSegment,
    SalesSegmentGroup,
    PaymentDeliveryMethodPair,
    PaymentMethod,
    DeliveryMethod
)
from altair.app.ticketing.famiport.userside_internal_api import (
    create_altair_famiport_sales_segment_pair,
    create_altair_famiport_performance,
    create_altair_famiport_performance_group,
    create_altair_famiport_venue,
    lookup_altair_famiport_sales_segment_pair,
    lookup_altair_famiport_performance,
    lookup_altair_famiport_performance_group,
    lookup_altair_famiport_venue
)
from altair.app.ticketing.payments import plugins

class FamiPortReflectDataCreationTest(unittest.TestCase):
    """FM連携用中間データの作成テスト"""
    def setUp(self):
        self.request = DummyRequest()
        self.session = _setup_db(
            [
                'altair.app.ticketing.core.models',
                'altair.app.ticketing.famiport.userside_models'
            ]
        )
        self.fm_sales_segment = SalesSegment(
            payment_delivery_method_pairs=[
                PaymentDeliveryMethodPair(
                    payment_method=PaymentMethod(
                        payment_plugin_id=plugins.FAMIPORT_PAYMENT_PLUGIN_ID,
                        fee=100
                    ),
                    delivery_method=DeliveryMethod(delivery_plugin_id=plugins.FAMIPORT_DELIVERY_PLUGIN_ID),
                    system_fee=300,
                    transaction_fee=0,
                    discount=0
                )
            ],
            sales_segment_group=SalesSegmentGroup(name=u'ファミマ先行'),
            start_at=datetime(2016,06,01,10,0),
            seat_choice=True
        )
        self.non_fm_sales_segment = SalesSegment(
            payment_delivery_method_pairs=[
                PaymentDeliveryMethodPair(
                    payment_method=PaymentMethod(
                        payment_plugin_id=plugins.MULTICHECKOUT_PAYMENT_PLUGIN_ID,
                        fee=200
                    ),
                    delivery_method=DeliveryMethod(delivery_plugin_id=plugins.SEJ_DELIVERY_PLUGIN_ID),
                    system_fee=300,
                    transaction_fee=0,
                    discount=0
                )
            ],
            sales_segment_group=SalesSegmentGroup(name=u'セブン先行'),
            start_at=datetime(2016,07,01,10,0),
            seat_choice=False
        )
        self.performance = Performance(
            name=u'公演１',
            start_on=datetime(2016,06,13,10,0),
            event_id=1,
            event=Event(organization_id=111),
            venue=Venue(
                site=Site(
                    siteprofile_id=1,
                    siteprofile=SiteProfile(name=u'クリムゾンハウス')
                ),
                name=u'クリムゾンハウス４F',
                organization_id=111
            ),
            sales_segments=[
                self.fm_sales_segment,
                self.non_fm_sales_segment
            ]
        )
        tenant = FamiPortTenant(
            organization_id=111,
            name=u'楽天チケット',
            code='00111'
        )
        self.session.add(tenant)
        self.session.flush()

    def tearDown(self):
        _teardown_db()
        tearDown()

    @mock.patch('altair.app.ticketing.famiport.userside_internal_api.sync_altair_famiport_venue')
    def test_creating_altair_famiport_venue(self, mock_sync_altair_famiport_venue):
        """AltairFamiPortVenueが作成されることを確認"""
        # setup
        from altair.app.ticketing.famiport.userside_models import AltairFamiPortReflectionStatus
        mock_sync_altair_famiport_venue.return_value = {'venue_id':'1234'}

        # テスト対象
        create_altair_famiport_venue(self.request, self.session, self.performance, name_kana=u'')
        altair_famiport_venue = lookup_altair_famiport_venue(self.session, self.performance)
        # 存在チェック
        self.assertTrue(altair_famiport_venue)
        # 属性チェック
        self.assertEqual(altair_famiport_venue.famiport_venue_id, 1234)
        self.assertEqual(altair_famiport_venue.venue_name, u'クリムゾンハウス４F')
        self.assertEqual(altair_famiport_venue.name, u'クリムゾンハウス')
        self.assertEqual(altair_famiport_venue.organization_id, 111)
        self.assertEqual(altair_famiport_venue.siteprofile_id, 1)
        self.assertEqual(altair_famiport_venue.status, AltairFamiPortReflectionStatus.AwaitingReflection.value)

    @mock.patch('altair.app.ticketing.famiport.userside_internal_api.sync_altair_famiport_venue')
    def test_creating_altair_famiport_performance_group(self, mock_sync_altair_famiport_venue):
        """AltairFamiPortVenueが作成されることを確認"""
        # setup
        from altair.app.ticketing.famiport.models import FamiPortSalesChannel
        from altair.app.ticketing.famiport.userside_models import AltairFamiPortReflectionStatus
        mock_sync_altair_famiport_venue.return_value = {'venue_id':'1234'}
        altair_famiport_venue = create_altair_famiport_venue(self.request, self.session, self.performance, name_kana=u'')

        # テスト対象
        create_altair_famiport_performance_group(self.request, self.session, self.performance, altair_famiport_venue)
        altair_famiport_performance_group = lookup_altair_famiport_performance_group(self.session, self.performance, altair_famiport_venue)
        # 存在チェック
        self.assertTrue(altair_famiport_performance_group)
        # 属性チェック
        self.assertEqual(altair_famiport_performance_group.altair_famiport_venue, altair_famiport_venue)
        self.assertEqual(altair_famiport_performance_group.organization_id, 111)
        self.assertEqual(altair_famiport_performance_group.event_id, 1)
        self.assertEqual(altair_famiport_performance_group.code_1, u'000001')
        self.assertEqual(altair_famiport_performance_group.code_2, u'0001')
        self.assertEqual(altair_famiport_performance_group.name_1, u'公演１')
        self.assertEqual(altair_famiport_performance_group.sales_channel, FamiPortSalesChannel.FamiPortAndWeb.value)
        self.assertEqual(altair_famiport_performance_group.status, AltairFamiPortReflectionStatus.AwaitingReflection.value)

    @mock.patch('altair.app.ticketing.famiport.userside_internal_api.sync_altair_famiport_venue')
    def test_creating_altair_famiport_performance(self, mock_sync_altair_famiport_venue):
        """AltairFamiPortPerformanceが作成されることを確認"""
        # setup
        from altair.viewhelpers.datetime_ import create_date_time_formatter
        from altair.app.ticketing.famiport.userside_models import AltairFamiPortReflectionStatus
        from altair.app.ticketing.famiport.models import FamiPortPerformanceType
        mock_sync_altair_famiport_venue.return_value = {'venue_id':'1234'}
        altair_famiport_venue = create_altair_famiport_venue(self.request, self.session, self.performance, name_kana=u'')
        altair_famiport_performance_group = create_altair_famiport_performance_group(self.request, self.session, self.performance, altair_famiport_venue)
        datetime_formatter = create_date_time_formatter(self.request)

        # テスト対象
        create_altair_famiport_performance(self.request, self.session, self.performance, altair_famiport_performance_group, datetime_formatter)
        altair_famiport_performance = lookup_altair_famiport_performance(self.session, self.performance)

        # 存在チェック
        self.assertTrue(altair_famiport_performance)
        # 属性チェック
        self.assertEqual(altair_famiport_performance.altair_famiport_performance_group, altair_famiport_performance_group)
        self.assertEqual(altair_famiport_performance.code, u'001')
        self.assertEqual(altair_famiport_performance.name, u'公演１')
        self.assertEqual(altair_famiport_performance.type, FamiPortPerformanceType.Normal.value)
        self.assertEqual(altair_famiport_performance.ticket_name, None)
        self.assertEqual(altair_famiport_performance.performance, self.performance)
        self.assertEqual(altair_famiport_performance.start_at, datetime(2016,06,13,10,0))
        self.assertEqual(altair_famiport_performance.status, AltairFamiPortReflectionStatus.AwaitingReflection.value)

    @mock.patch('altair.app.ticketing.famiport.userside_internal_api.sync_altair_famiport_venue')
    def test_creating_altair_famiport_sales_segment_pair(self, mock_sync_altair_famiport_venue):
        """AltairFamiPortSalesSegmentPairが作成されることを確認"""
        # setup
        from altair.viewhelpers.datetime_ import create_date_time_formatter
        from altair.app.ticketing.famiport.userside_models import AltairFamiPortReflectionStatus
        from altair.app.ticketing.famiport.models import FamiPortPerformanceType
        from altair.app.ticketing.famiport.userside_api import find_sales_segment_pairs,filter_famiport_pdmp_sales_segments
        mock_sync_altair_famiport_venue.return_value = {'venue_id':'1234'}
        altair_famiport_venue = create_altair_famiport_venue(self.request, self.session, self.performance, name_kana=u'')
        altair_famiport_performance_group = create_altair_famiport_performance_group(self.request, self.session, self.performance, altair_famiport_venue)
        datetime_formatter = create_date_time_formatter(self.request)
        altair_famiport_performance = create_altair_famiport_performance(self.request, self.session, self.performance, altair_famiport_performance_group, datetime_formatter)

        # テスト対象
        fm_sales_segments = filter_famiport_pdmp_sales_segments(self.performance.sales_segments)
        sales_segment_pairs = list(find_sales_segment_pairs(self.session, fm_sales_segments))
        for seat_unselectable_ss, seat_selectable_ss in sales_segment_pairs:
            create_altair_famiport_sales_segment_pair(self.request, self.session, seat_unselectable_ss, seat_selectable_ss, altair_famiport_performance)

        altair_famiport_sales_segment_pairs = []
        for ss in fm_sales_segments:
            altair_famiport_sales_segment_pairs.append(lookup_altair_famiport_sales_segment_pair(self.session, ss))

        # 存在チェック
        self.assertEqual(len(altair_famiport_sales_segment_pairs), 1)
        self.assertTrue(altair_famiport_sales_segment_pairs[0])
        # 属性チェック
        self.assertEqual(altair_famiport_sales_segment_pairs[0].altair_famiport_performance, altair_famiport_performance)
        self.assertEqual(altair_famiport_sales_segment_pairs[0].code, u'001')
        self.assertEqual(altair_famiport_sales_segment_pairs[0].name, u'ファミマ先行')
        self.assertEqual(altair_famiport_sales_segment_pairs[0].published_at, datetime(2016,06,01,10,0))
        self.assertEqual(altair_famiport_sales_segment_pairs[0].seat_unselectable_sales_segment, None)
        self.assertEqual(altair_famiport_sales_segment_pairs[0].seat_selectable_sales_segment, self.fm_sales_segment)
        self.assertEqual(altair_famiport_sales_segment_pairs[0].status, AltairFamiPortReflectionStatus.AwaitingReflection.value)
