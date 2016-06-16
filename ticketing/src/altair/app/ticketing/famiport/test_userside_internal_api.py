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
    lookup_altair_famiport_venue,
    update_altair_famiport_performance_if_needed,
    update_altair_famiport_sales_segment_pair_if_needed
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


class FamiPortReflectDataUpdateTest(unittest.TestCase):
    """FM連携用中間データの更新テスト"""

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
    def test_update_altair_famiport_performance_when_changing_performance_date(self, mock_sync_altair_famiport_venue):
        """公演日を変更した時にAltairFamiPortPerformanceの更新されることを確認"""
        # setup
        from altair.viewhelpers.datetime_ import create_date_time_formatter
        from altair.app.ticketing.famiport.userside_models import AltairFamiPortReflectionStatus
        from altair.app.ticketing.famiport.models import FamiPortPerformanceType
        mock_sync_altair_famiport_venue.return_value = {'venue_id':'1234'}
        now = datetime.now()
        altair_famiport_venue = create_altair_famiport_venue(self.request, self.session, self.performance, name_kana=u'')
        altair_famiport_performance_group = create_altair_famiport_performance_group(self.request, self.session, self.performance, altair_famiport_venue)
        datetime_formatter = create_date_time_formatter(self.request)
        altair_famiport_performance = create_altair_famiport_performance(self.request, self.session, self.performance, altair_famiport_performance_group, datetime_formatter)

        # 公演日更新
        self.performance.start_on = datetime(2016,06,20,10,0)

        # テスト対象
        update_altair_famiport_performance_if_needed(self.request, self.session, altair_famiport_performance, self.performance, altair_famiport_performance_group, datetime_formatter, now)
        result = lookup_altair_famiport_performance(self.session, self.performance)

        self.assertEqual(result.start_at, datetime(2016,06,20,10,0))

        self.assertEqual(result.updated_at, now)
        self.assertEqual(result.status, AltairFamiPortReflectionStatus.AwaitingReflection.value)

    @mock.patch('altair.app.ticketing.famiport.userside_internal_api.sync_altair_famiport_venue')
    def test_update_altair_famiport_performance_when_changing_venue(self, mock_sync_altair_famiport_venue):
        """会場を変更した時にAltairFamiPortPerformanceの更新されることを確認"""
        # setup
        from altair.viewhelpers.datetime_ import create_date_time_formatter
        from altair.app.ticketing.famiport.userside_models import AltairFamiPortReflectionStatus
        from altair.app.ticketing.famiport.models import FamiPortPerformanceType
        now = datetime.now()
        # 会場更新前のsetup
        mock_sync_altair_famiport_venue.return_value = {'venue_id':'1234'}
        altair_famiport_venue1 = create_altair_famiport_venue(self.request, self.session, self.performance, name_kana=u'')
        altair_famiport_performance_group1 = create_altair_famiport_performance_group(self.request, self.session, self.performance, altair_famiport_venue1)
        datetime_formatter = create_date_time_formatter(self.request)
        altair_famiport_performance = create_altair_famiport_performance(self.request, self.session, self.performance, altair_famiport_performance_group1, datetime_formatter)

        # 会場更新
        self.performance.venue = Venue(
                site=Site(
                    siteprofile_id=2,
                    siteprofile=SiteProfile(name=u'どこか別の会場')
                ),
                name=u'別会場？？F',
                organization_id=111
            )

        # 会場更新後のsetup
        mock_sync_altair_famiport_venue.return_value = {'venue_id':'1235'}
        altair_famiport_venue2 = create_altair_famiport_venue(self.request, self.session, self.performance, name_kana=u'')
        altair_famiport_performance_group2 = create_altair_famiport_performance_group(self.request, self.session, self.performance, altair_famiport_venue2)

        # テスト対象
        update_altair_famiport_performance_if_needed(self.request, self.session, altair_famiport_performance, self.performance, altair_famiport_performance_group2, datetime_formatter, now)
        result = lookup_altair_famiport_performance(self.session, self.performance)

        self.assertEqual(result.altair_famiport_performance_group_id, altair_famiport_performance_group2.id)
        self.assertEqual(result.altair_famiport_performance_group.altair_famiport_venue.venue_name, u'別会場？？F')

        self.assertEqual(result.updated_at, now)
        self.assertEqual(result.status, AltairFamiPortReflectionStatus.AwaitingReflection.value)

    @mock.patch('altair.app.ticketing.famiport.userside_internal_api.sync_altair_famiport_venue')
    def test_update_altair_famiport_performance_when_changing_performance_end_on(self, mock_sync_altair_famiport_venue):
        """公演終了日を追加(変更)した時にAltairFamiPortPerformanceの更新されることを確認"""
        # setup
        from altair.viewhelpers.datetime_ import create_date_time_formatter
        from altair.app.ticketing.famiport.userside_models import AltairFamiPortReflectionStatus
        from altair.app.ticketing.famiport.models import FamiPortPerformanceType
        mock_sync_altair_famiport_venue.return_value = {'venue_id':'1234'}
        now = datetime.now()
        altair_famiport_venue = create_altair_famiport_venue(self.request, self.session, self.performance, name_kana=u'')
        altair_famiport_performance_group = create_altair_famiport_performance_group(self.request, self.session, self.performance, altair_famiport_venue)
        datetime_formatter = create_date_time_formatter(self.request)
        altair_famiport_performance = create_altair_famiport_performance(self.request, self.session, self.performance, altair_famiport_performance_group, datetime_formatter)
        # 更新前は1日券
        self.assertEqual(altair_famiport_performance.type, FamiPortPerformanceType.Normal.value)

        # 公演日更新
        self.performance.end_on = datetime(2016,06,25,10,0)

        # テスト対象
        update_altair_famiport_performance_if_needed(self.request, self.session, altair_famiport_performance, self.performance, altair_famiport_performance_group, datetime_formatter, now)
        result = lookup_altair_famiport_performance(self.session, self.performance)

        self.assertEqual(result.type, FamiPortPerformanceType.Spanned.value)
        self.assertIn(u'まで有効', result.ticket_name)

        self.assertEqual(result.updated_at, now)
        self.assertEqual(result.status, AltairFamiPortReflectionStatus.AwaitingReflection.value)

    @mock.patch('altair.app.ticketing.famiport.userside_internal_api.sync_altair_famiport_venue')
    def test_update_altair_famiport_ss_pair_when_changing_name(self, mock_sync_altair_famiport_venue):
        """販売区分名を変更した時にAltairFamiPortSalesSegmentPairの更新されることを確認"""
        # setup
        from altair.viewhelpers.datetime_ import create_date_time_formatter
        from altair.app.ticketing.famiport.userside_models import AltairFamiPortReflectionStatus
        from altair.app.ticketing.famiport.models import FamiPortPerformanceType
        from altair.app.ticketing.famiport.userside_api import find_sales_segment_pairs,filter_famiport_pdmp_sales_segments
        mock_sync_altair_famiport_venue.return_value = {'venue_id':'1234'}
        now = datetime.now()
        altair_famiport_venue = create_altair_famiport_venue(self.request, self.session, self.performance, name_kana=u'')
        altair_famiport_performance_group = create_altair_famiport_performance_group(self.request, self.session, self.performance, altair_famiport_venue)
        datetime_formatter = create_date_time_formatter(self.request)
        altair_famiport_performance = create_altair_famiport_performance(self.request, self.session, self.performance, altair_famiport_performance_group, datetime_formatter)
        fm_sales_segments = filter_famiport_pdmp_sales_segments(self.performance.sales_segments)
        sales_segment_pairs = list(find_sales_segment_pairs(self.session, fm_sales_segments))
        altair_sales_segments = []
        for seat_unselectable_ss, seat_selectable_ss in sales_segment_pairs:
            altair_sales_segments.append(create_altair_famiport_sales_segment_pair(self.request, self.session, seat_unselectable_ss, seat_selectable_ss, altair_famiport_performance))

        # 販売区分名を更新
        self.fm_sales_segment.sales_segment_group.name = u'ファミマ先行（更新後）'

        # テスト対象
        fm_sales_segments = filter_famiport_pdmp_sales_segments(self.performance.sales_segments)
        sales_segment_pairs = list(find_sales_segment_pairs(self.session, fm_sales_segments))
        result = []
        for ss in altair_sales_segments:
            for unsele_ss, sele_ss in sales_segment_pairs:
                result.append(update_altair_famiport_sales_segment_pair_if_needed(self.request, self.session, ss, unsele_ss, sele_ss, now))

        self.assertEqual(result[0].name, u'ファミマ先行（更新後）')

        self.assertEqual(result[0].updated_at, now)
        self.assertEqual(result[0].status, AltairFamiPortReflectionStatus.AwaitingReflection.value)

    @mock.patch('altair.app.ticketing.famiport.userside_internal_api.sync_altair_famiport_venue')
    def test_update_altair_famiport_ss_pair_when_changing_start_at(self, mock_sync_altair_famiport_venue):
        """販売開始日を変更した時にAltairFamiPortSalesSegmentPairの更新されることを確認"""
        # setup
        from altair.viewhelpers.datetime_ import create_date_time_formatter
        from altair.app.ticketing.famiport.userside_models import AltairFamiPortReflectionStatus
        from altair.app.ticketing.famiport.models import FamiPortPerformanceType
        from altair.app.ticketing.famiport.userside_api import find_sales_segment_pairs,filter_famiport_pdmp_sales_segments
        mock_sync_altair_famiport_venue.return_value = {'venue_id':'1234'}
        now = datetime.now()
        altair_famiport_venue = create_altair_famiport_venue(self.request, self.session, self.performance, name_kana=u'')
        altair_famiport_performance_group = create_altair_famiport_performance_group(self.request, self.session, self.performance, altair_famiport_venue)
        datetime_formatter = create_date_time_formatter(self.request)
        altair_famiport_performance = create_altair_famiport_performance(self.request, self.session, self.performance, altair_famiport_performance_group, datetime_formatter)
        fm_sales_segments = filter_famiport_pdmp_sales_segments(self.performance.sales_segments)
        sales_segment_pairs = list(find_sales_segment_pairs(self.session, fm_sales_segments))
        altair_sales_segments = []
        for seat_unselectable_ss, seat_selectable_ss in sales_segment_pairs:
            altair_sales_segments.append(create_altair_famiport_sales_segment_pair(self.request, self.session, seat_unselectable_ss, seat_selectable_ss, altair_famiport_performance))

        # 販売区分名を更新
        self.fm_sales_segment.start_at = datetime(2016,06,11,10,0)

        # テスト対象
        fm_sales_segments = filter_famiport_pdmp_sales_segments(self.performance.sales_segments)
        sales_segment_pairs = list(find_sales_segment_pairs(self.session, fm_sales_segments))
        result = []
        for ss in altair_sales_segments:
            for unsele_ss, sele_ss in sales_segment_pairs:
                result.append(update_altair_famiport_sales_segment_pair_if_needed(self.request, self.session, ss, unsele_ss, sele_ss, now))

        self.assertEqual(result[0].published_at, datetime(2016,06,11,10,0))

        self.assertEqual(result[0].updated_at, now)
        self.assertEqual(result[0].status, AltairFamiPortReflectionStatus.AwaitingReflection.value)
