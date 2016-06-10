# encoding:utf-8
from datetime import datetime
import unittest
import logging
import sqlalchemy as sa
from altair.app.ticketing.payments.plugins import FAMIPORT_PAYMENT_PLUGIN_ID, FAMIPORT_DELIVERY_PLUGIN_ID
from pyramid.testing import setUp, tearDown
from altair.app.ticketing.testing import _setup_db, _teardown_db, DummyRequest
from altair.app.ticketing.famiport.testing import _setup_db as fm_setup_db, _teardown_db as fm__teardown_db
from userside_api import (
    find_sales_segment_pairs,
    create_famiport_reflection_data,
    submit_to_downstream_sync
)
from userside_internal_api import create_altair_famiport_venue
from api import resolve_famiport_prefecture_by_name



from altair.viewhelpers.datetime_ import create_date_time_formatter

from altair.app.ticketing.core.models import (
            Organization,
            FamiPortTenant,
            SiteProfile,
            Site,
            Venue,
            Event,
            Performance,
            SalesSegmentGroup,
            SalesSegment,
            PaymentMethod,
            DeliveryMethod,
            PaymentDeliveryMethodPair
)

from altair.app.ticketing.famiport.userside_models import (
    AltairFamiPortReflectionStatus,
    AltairFamiPortVenue,
    AltairFamiPortPerformanceGroup,
    AltairFamiPortPerformance,
    AltairFamiPortSalesSegmentPair
)

from altair.app.ticketing.famiport.models import (
    FamiPortPlayguide,
    FamiPortClient,
    FamiPortVenue,
    FamiPortGenre1,
    FamiPortEvent,
    FamiPortPerformance,
    FamiPortSalesSegment
)

logger = logging.getLogger(__name__)

# TODO Test duplicate AltairFamiPortVenue case

class FamiPortSyncTest(unittest.TestCase):
    def setUp(self):
        self.request = DummyRequest()


        self.session = _setup_db(
            modules=[
                'altair.app.ticketing.core.models',
                'altair.app.ticketing.famiport.userside_models',
                ]
            )

        # Set up data on Altair side
        self.rt_org = Organization(id = 15, name = u'楽天チケット', code = 'RT', short_name = 'RT')
        self.rt_fmtenant = FamiPortTenant(organization_id = 15, name = u'楽天チケット', code = '00001')

        self.session.add(self.rt_org)
        self.session.add(self.rt_fmtenant)

        self.fm_paymentmethod = PaymentMethod(id = 1, name = u'ファミポート決済', organization_id = 15, payment_plugin_id = FAMIPORT_PAYMENT_PLUGIN_ID, fee = 0.0)
        self.fm_deliverymethod = DeliveryMethod(id = 1, name = u'ファミポート引取', organization_id = 15, delivery_plugin_id = FAMIPORT_DELIVERY_PLUGIN_ID)
        self.fm_pdmp = PaymentDeliveryMethodPair(id = 1, sales_segment_group_id = 1, payment_method_id = 1, delivery_method_id = 1, \
                                                 system_fee = 0.0, transaction_fee = 0.0, discount = 0)

        self.session.add(self.fm_paymentmethod)
        self.session.add(self.fm_deliverymethod)
        self.session.add(self.fm_pdmp)

        self.fm_request = DummyRequest()
        self.fm_config = setUp()
        self.engine = fm_setup_db(self.fm_config.registry, ['altair.app.ticketing.famiport.models'])
        from altair.sqlahelper import get_global_db_session
        self.fm_session = get_global_db_session(self.fm_config.registry, 'famiport')
        self.fm_request.session = self.fm_session

        # Set up data on FamiPort side
        self.fmplayguide = FamiPortPlayguide(id = 1, name = u'楽天チケット', discrimination_code = 5, discrimination_code_2 = 4)
        self.rt_fmclient = FamiPortClient(famiport_playguide_id = 1, code = '00001', name = u'楽天チケット', prefix = '001')
        self.fm_session.add(self.fmplayguide)
        self.fm_session.add(self.rt_fmclient)
        self.fm_session.flush()

    def tearDown(self):
        _teardown_db()
        fm__teardown_db(self.fm_config.registry)
        tearDown()

    def test_find_sales_segment_pairs(self):
        """ Test seat uneslectable SalesSegment and seat selectable SalesSegment pairing
        """
        siteprofile1 = SiteProfile(id = 1, name = u'Zepp DiverCity TOKYO', prefecture = u'東京都')
        site1 = Site(id = 1, siteprofile_id = siteprofile1.id, name = u'Zepp DiverCity TOKYO', visible = True)
        event1 = Event(id = 1, code = 'RT00001', title = u'テストイベント1', organization_id = 15)
        performance1 = Performance(id = 1, event_id = 1, name = u'テスト公演1', code = 'RT0000000001', \
                                   start_on = datetime(2016, 3, 1, 10, 0, 0), end_on = None)
        venue1 = Venue(id = 1, site_id = site1.id, organization_id = 15, name = u'Zepp DiverCity TOKYO', performance_id = performance1.id)
        salessegmentgroup1 = SalesSegmentGroup(id = 1, organization_id = 15, event_id = event1.id, kind = 'normal', name = u'一般発売', \
                            seat_choice = False, start_at = datetime(2016, 2, 1, 10, 0, 0), end_at = datetime(2016, 2, 26, 23, 59, 59))
        unselectable_salessegment1 = SalesSegment(id = 1, sales_segment_group_id = salessegmentgroup1.id, performance_id = performance1.id, event_id = event1.id, \
                                     payment_delivery_method_pairs = [self.fm_pdmp], public = True, seat_choice = False, \
                                     start_at = datetime(2016, 2, 1, 10, 0, 0), end_at = datetime(2016, 2, 14, 23, 59, 59))
        selectable_salessegment1 = SalesSegment(id = 2, sales_segment_group_id = salessegmentgroup1.id, performance_id = performance1.id, event_id = event1.id, \
                                     payment_delivery_method_pairs = [self.fm_pdmp], public = True, seat_choice = True, \
                                     start_at = datetime(2016, 2, 15, 0, 0, 0), end_at = datetime(2016, 2, 29, 23, 59, 59))
        sales_segments1 = [unselectable_salessegment1]
        sales_segment_pairs1 = list(find_sales_segment_pairs(self.session, sales_segments1))
        for seat_unselectable_sales_segment, seat_selectable_sales_segment in sales_segment_pairs1:
            self.assertEqual(seat_unselectable_sales_segment.id, unselectable_salessegment1.id)
            self.assertEqual(seat_selectable_sales_segment, None)

        sales_segments2 = [selectable_salessegment1]
        sales_segment_pairs2 = list(find_sales_segment_pairs(self.session, sales_segments2))
        for seat_unselectable_sales_segment, seat_selectable_sales_segment in sales_segment_pairs2:
            self.assertEqual(seat_unselectable_sales_segment, None)
            self.assertEqual(seat_selectable_sales_segment.id, selectable_salessegment1.id)

        sales_segments3 = [unselectable_salessegment1, selectable_salessegment1]
        sales_segment_pairs3 = list(find_sales_segment_pairs(self.session, sales_segments3))
        for seat_unselectable_sales_segment, seat_selectable_sales_segment in sales_segment_pairs3:
            self.assertEqual(seat_unselectable_sales_segment.id, unselectable_salessegment1.id)
            self.assertEqual(seat_selectable_sales_segment.id, selectable_salessegment1.id)


    @staticmethod
    def __changeStatus(entity, status):
        entity.status = status


    def test_fmsync_without_altairfmvenue_and_fmvenue(self):
        """1st FM sync without existing AltairFamiPortVenue and FamiPortVenue
        """

        siteprofile1 = SiteProfile(id = 1, name = u'Zepp DiverCity TOKYO', prefecture = u'東京都')
        site1 = Site(id = 1, siteprofile_id = 1, name = u'Zepp DiverCity TOKYO', visible = True)
        event1 = Event(id = 1, code = 'RT00001', title = u'テストイベント1', organization_id = 15)
        performance1 = Performance(id = 1, event_id = 1, name = u'テスト公演1', code = 'RT0000000001', \
                                   start_on = datetime(2016, 3, 1, 10, 0, 0), end_on = None)
        venue1 = Venue(id = 1, site_id = 1, organization_id = 15, name = u'Zepp DiverCity TOKYO', performance_id = 1)
        salessegmentgroup1 = SalesSegmentGroup(id = 1, organization_id = 15, event_id = 1, kind = 'normal', name = u'一般発売', \
                            seat_choice = False, start_at = datetime(2016, 2, 1, 10, 0, 0), end_at = datetime(2016, 2, 26, 23, 59, 59))
        salessegment1 = SalesSegment(id = 1, sales_segment_group_id = 1, performance_id = 1, event_id = 1, \
                                     payment_delivery_method_pairs = [self.fm_pdmp], public = True, seat_choice = False, \
                                     start_at = datetime(2016, 2, 1, 10, 0, 0), end_at = datetime(2016, 2, 26, 23, 59, 59))

        self.session.add(siteprofile1)
        self.session.add(site1)
        self.session.add(event1)
        self.session.add(performance1)
        self.session.add(venue1)
        self.session.add(salessegmentgroup1)
        self.session.add(salessegment1)
        self.session.flush()

        famiport_genre1 = FamiPortGenre1(code = 1, name = u'音楽')
        self.fm_session.add(famiport_genre1)
        self.fm_session.flush()

        datetime_formatter = create_date_time_formatter(self.request)
        create_famiport_reflection_data(self.request, self.session, event1, datetime_formatter)

        # Retrieve created intermidiate objects: AltairFamiPortVenue, AltairFamiPortPerformanceGroup, AltairFamiPortPerformance, AltairFamiPortSalesSegmentPair
        altair_famiport_venue = self.session.query(AltairFamiPortVenue)\
                                            .filter(AltairFamiPortVenue.siteprofile_id == siteprofile1.id)\
                                            .filter(AltairFamiPortVenue.venue_name == venue1.name).one()
        altair_famiport_performance_group = self.session.query(AltairFamiPortPerformanceGroup)\
                                                        .filter_by(event_id = event1.id).one()
        altair_famiport_performance = self.session.query(AltairFamiPortPerformance)\
                                                  .filter_by(performance_id = performance1.id).one()
        altair_famiport_salessegment_pair = self.session.query(AltairFamiPortSalesSegmentPair)\
                                                .filter(sa.or_(AltairFamiPortSalesSegmentPair.seat_unselectable_sales_segment_id == salessegment1.id, \
                                                               AltairFamiPortSalesSegmentPair.seat_selectable_sales_segment_id == salessegment1.id)).one()

        famiport_venue = self.fm_session.query(FamiPortVenue).filter(FamiPortVenue.userside_id == altair_famiport_venue.id).one()

        self.assertEqual(venue1.name, altair_famiport_venue.name)
        self.assertEqual(venue1.site.siteprofile.id, altair_famiport_venue.siteprofile_id)

        self.assertEqual(event1.id, altair_famiport_performance_group.event_id)
        self.assertEqual(altair_famiport_venue.id, altair_famiport_performance_group.altair_famiport_venue_id)

        self.assertEqual(performance1.id, altair_famiport_performance.performance_id)
        self.assertEqual(altair_famiport_performance_group.id, altair_famiport_performance.altair_famiport_performance_group_id)

        self.assertEqual(salessegment1.id, altair_famiport_salessegment_pair.seat_unselectable_sales_segment_id)

        self.assertEqual(venue1.name, famiport_venue.name)
        self.assertEqual(resolve_famiport_prefecture_by_name(self.request, venue1.site.siteprofile.prefecture), famiport_venue.prefecture)

        # Change status from Editing to AwaitingReflection
        for entity in [altair_famiport_venue, altair_famiport_performance_group, altair_famiport_performance, altair_famiport_salessegment_pair]:
            self.__changeStatus(entity, AltairFamiPortReflectionStatus.AwaitingReflection.value)

        # Create FamiPort objects
        submit_to_downstream_sync(self.fm_request, self.session, self.rt_fmtenant, event1)

        # Retrieve created famiport objects
        famiport_event = self.fm_session.query(FamiPortEvent).filter_by(userside_id = altair_famiport_performance_group.id).one()
        famiport_performance = self.fm_session.query(FamiPortPerformance).filter_by(userside_id = altair_famiport_performance.id).one()
        famiport_salessegment = self.fm_session.query(FamiPortSalesSegment).filter_by(userside_id = altair_famiport_salessegment_pair.id).one()

        # Make sure expected FamiPort objects are created
        self.assertEqual(famiport_venue.id, famiport_event.venue_id)
        self.assertEqual(famiport_event.id, famiport_performance.famiport_event_id)
        self.assertEqual(performance1.start_on, famiport_performance.start_at)

        self.assertEqual(famiport_performance.id, famiport_salessegment.famiport_performance_id)
        self.assertEqual(salessegment1.start_at, famiport_salessegment.start_at)
        self.assertEqual(salessegment1.end_at, famiport_salessegment.end_at)
        self.assertEqual(salessegmentgroup1.name, famiport_salessegment.name)

    def test_fmsync_with_altairfmvenue_and_fmvenue(self):
        """ 1st FM sync with existing AltairFamiPortVenue and FamiPortVenue
        """

        siteprofile1 = SiteProfile(id = 1, name = u'Zepp DiverCity TOKYO', prefecture = u'東京都')
        site1 = Site(id = 1, siteprofile_id = 1, name = u'Zepp DiverCity TOKYO', visible = True)
        event1 = Event(id = 1, code = 'RT00001', title = u'テストイベント1', organization_id = 15)
        performance1 = Performance(id = 1, event_id = 1, name = u'テスト公演1', code = 'RT0000000001', \
                                   start_on = datetime(2016, 3, 1, 10, 0, 0), end_on = None)
        venue1 = Venue(id = 1, site_id = 1, organization_id = 15, name = u'Zepp DiverCity TOKYO', performance_id = 1)
        salessegmentgroup1 = SalesSegmentGroup(id = 1, organization_id = 15, event_id = 1, kind = 'normal', name = u'一般発売', \
                                               seat_choice = False, start_at = datetime(2016, 2, 1, 10, 0, 0), \
                                               end_at = datetime(2016, 2, 26, 23, 59, 59))
        salessegment1 = SalesSegment(id = 1, sales_segment_group_id = 1, performance_id = 1, event_id = 1, \
                                     payment_delivery_method_pairs = [self.fm_pdmp], public = True, seat_choice = False, \
                                     start_at = datetime(2016, 2, 1, 10, 0, 0), end_at = datetime(2016, 2, 26, 23, 59, 59))

        self.session.add(siteprofile1)
        self.session.add(site1)
        self.session.add(event1)
        self.session.add(performance1)
        self.session.add(venue1)
        self.session.add(salessegmentgroup1)
        self.session.add(salessegment1)
        self.session.flush()

        famiport_genre1 = FamiPortGenre1(code = 1, name = u'音楽')
        self.fm_session.add(famiport_genre1)
        self.fm_session.flush()

        # Create dummy AltairFamiPortVenue and FamiPortVenue for existing ones check test
        altair_famiport_venue1 = create_altair_famiport_venue(self.request, self.session, performance1, name_kana=u'')

        datetime_formatter = create_date_time_formatter(self.request)
        create_famiport_reflection_data(self.request, self.session, event1, datetime_formatter)

        # Retrieve created intermidiate objects: AltairFamiPortVenue, AltairFamiPortPerformanceGroup, AltairFamiPortPerformance, AltairFamiPortSalesSegmentPair
        altair_famiport_venue = self.session.query(AltairFamiPortVenue)\
                                            .filter(AltairFamiPortVenue.siteprofile_id == siteprofile1.id)\
                                            .filter(AltairFamiPortVenue.venue_name == venue1.name).one()
        altair_famiport_performance_group = self.session.query(AltairFamiPortPerformanceGroup)\
                                                        .filter_by(event_id = event1.id).one()
        altair_famiport_performance = self.session.query(AltairFamiPortPerformance)\
                                                  .filter_by(performance_id = performance1.id).one()
        altair_famiport_salessegment_pair = self.session.query(AltairFamiPortSalesSegmentPair)\
                                                .filter(sa.or_(AltairFamiPortSalesSegmentPair.seat_unselectable_sales_segment_id == salessegment1.id, \
                                                               AltairFamiPortSalesSegmentPair.seat_selectable_sales_segment_id == salessegment1.id)).one()

        famiport_venue = self.fm_session.query(FamiPortVenue).filter(FamiPortVenue.userside_id == altair_famiport_venue.id).one()

        self.assertEqual(venue1.name, altair_famiport_venue.name)
        self.assertEqual(venue1.site.siteprofile.id, altair_famiport_venue.siteprofile_id)

        self.assertEqual(event1.id, altair_famiport_performance_group.event_id)
        self.assertEqual(altair_famiport_venue.id, altair_famiport_performance_group.altair_famiport_venue_id)

        self.assertEqual(performance1.id, altair_famiport_performance.performance_id)
        self.assertEqual(altair_famiport_performance_group.id, altair_famiport_performance.altair_famiport_performance_group_id)

        self.assertEqual(salessegment1.id, altair_famiport_salessegment_pair.seat_unselectable_sales_segment_id)

        self.assertEqual(venue1.name, famiport_venue.name)
        self.assertEqual(resolve_famiport_prefecture_by_name(self.request, venue1.site.siteprofile.prefecture), famiport_venue.prefecture)

        # Change status from Editing to AwaitingReflection
        for entity in [altair_famiport_venue, altair_famiport_performance_group, altair_famiport_performance, altair_famiport_salessegment_pair]:
            self.__changeStatus(entity, AltairFamiPortReflectionStatus.AwaitingReflection.value)

        # Create FamiPort objects
        submit_to_downstream_sync(self.fm_request, self.session, self.rt_fmtenant, event1)

        # Retrieve created famiport objects
        famiport_event = self.fm_session.query(FamiPortEvent).filter_by(userside_id = altair_famiport_performance_group.id).one()
        famiport_performance = self.fm_session.query(FamiPortPerformance).filter_by(userside_id = altair_famiport_performance.id).one()
        famiport_salessegment = self.fm_session.query(FamiPortSalesSegment).filter_by(userside_id = altair_famiport_salessegment_pair.id).one()

        # Make sure expected FamiPort objects are created
        self.assertEqual(famiport_venue.id, famiport_event.venue_id)
        self.assertEqual(famiport_event.id, famiport_performance.famiport_event_id)
        self.assertEqual(performance1.start_on, famiport_performance.start_at)

        self.assertEqual(famiport_performance.id, famiport_salessegment.famiport_performance_id)
        self.assertEqual(salessegment1.start_at, famiport_salessegment.start_at)
        self.assertEqual(salessegment1.end_at, famiport_salessegment.end_at)
        self.assertEqual(salessegmentgroup1.name, famiport_salessegment.name)

    def test_venue_name_change_without_altairfmvenue_and_fmvenue(self):
        """2nd FM sync after venue name was changed without existing AltairFamiPortVenue and FamiPortVenue
        """

        siteprofile1 = SiteProfile(id = 1, name = u'Zepp DiverCity TOKYO', prefecture = u'東京都')
        site1 = Site(id = 1, siteprofile_id = 1, name = u'Zepp DiverCity TOKYO', visible = True)
        event1 = Event(id = 1, code = 'RT00001', title = u'テストイベント1', organization_id = 15)
        performance1 = Performance(id = 1, event_id = 1, name = u'テスト公演1', code = 'RT0000000001', \
                                   start_on = datetime(2016, 3, 1, 10, 0, 0), end_on = None)
        venue1 = Venue(id = 1, site_id = 1, organization_id = 15, name = u'Zepp DiverCity TOKYO', performance_id = 1)
        salessegmentgroup1 = SalesSegmentGroup(id = 1, organization_id = 15, event_id = 1, kind = 'normal', name = u'一般発売', \
                                               seat_choice = False, start_at = datetime(2016, 2, 1, 10, 0, 0), \
                                               end_at = datetime(2016, 2, 26, 23, 59, 59))
        salessegment1 = SalesSegment(id = 1, sales_segment_group_id = 1, performance_id = 1, event_id = 1, \
                                     payment_delivery_method_pairs = [self.fm_pdmp], public = True, seat_choice = False, \
                                     start_at = datetime(2016, 2, 1, 10, 0, 0), end_at = datetime(2016, 2, 26, 23, 59, 59))

        self.session.add(siteprofile1)
        self.session.add(site1)
        self.session.add(event1)
        self.session.add(performance1)
        self.session.add(venue1)
        self.session.add(salessegmentgroup1)
        self.session.add(salessegment1)
        self.session.flush()

        famiport_genre1 = FamiPortGenre1(code = 1, name = u'音楽')
        self.fm_session.add(famiport_genre1)
        self.fm_session.flush()

        datetime_formatter = create_date_time_formatter(self.request)
        create_famiport_reflection_data(self.request, self.session, event1, datetime_formatter)

        # Retrieve created intermidiate objects: AltairFamiPortVenue, AltairFamiPortPerformanceGroup, AltairFamiPortPerformance, AltairFamiPortSalesSegmentPair
        altair_famiport_venue = self.session.query(AltairFamiPortVenue)\
                                            .filter(AltairFamiPortVenue.siteprofile_id == siteprofile1.id)\
                                            .filter(AltairFamiPortVenue.venue_name == venue1.name).one()
        altair_famiport_performance_group = self.session.query(AltairFamiPortPerformanceGroup)\
                                                        .filter_by(event_id = event1.id).one()
        altair_famiport_performance = self.session.query(AltairFamiPortPerformance)\
                                                  .filter_by(performance_id = performance1.id).one()
        altair_famiport_salessegment_pair = self.session.query(AltairFamiPortSalesSegmentPair) \
                                                .filter(sa.or_(AltairFamiPortSalesSegmentPair.seat_unselectable_sales_segment_id == salessegment1.id, \
                                                               AltairFamiPortSalesSegmentPair.seat_selectable_sales_segment_id == salessegment1.id)).one()

        venue1.name = u'Zepp DiverCity TOKYO Next'
        self.session.add(venue1)
        self.session.flush()

        # Change status from Editing
        for entity in [altair_famiport_venue, altair_famiport_performance_group, altair_famiport_performance, altair_famiport_salessegment_pair]:
            self.__changeStatus(entity, AltairFamiPortReflectionStatus.Editing.value)

        create_famiport_reflection_data(self.request, self.session, event1, datetime_formatter)

        altair_famiport_performance = self.session.query(AltairFamiPortPerformance)\
                                                  .filter(AltairFamiPortPerformance.performance_id == performance1.id).one()
        altair_famiport_performance_group = altair_famiport_performance.altair_famiport_performance_group
        altair_famiport_venue = altair_famiport_performance_group.altair_famiport_venue

        famiport_venue = self.fm_session.query(FamiPortVenue).filter(FamiPortVenue.userside_id == altair_famiport_venue.id).one()

        self.assertEqual(venue1.name, altair_famiport_venue.venue_name)
        self.assertEqual(venue1.site.siteprofile.id, altair_famiport_venue.siteprofile_id)

        self.assertEqual(event1.id, altair_famiport_performance_group.event_id)
        self.assertEqual(altair_famiport_venue.id, altair_famiport_performance_group.altair_famiport_venue_id)

        self.assertEqual(performance1.id, altair_famiport_performance.performance_id)
        self.assertEqual(altair_famiport_performance_group.id, altair_famiport_performance.altair_famiport_performance_group_id)

        self.assertEqual(salessegment1.id, altair_famiport_salessegment_pair.seat_unselectable_sales_segment_id)

        self.assertEqual(venue1.name, famiport_venue.name)
        self.assertEqual(resolve_famiport_prefecture_by_name(self.request, venue1.site.siteprofile.prefecture), famiport_venue.prefecture)

        # Change status from Editing to AwaitingReflection
        for entity in [altair_famiport_venue, altair_famiport_performance_group, altair_famiport_performance, altair_famiport_salessegment_pair]:
            self.__changeStatus(entity, AltairFamiPortReflectionStatus.AwaitingReflection.value)

        # Create FamiPort objects
        submit_to_downstream_sync(self.fm_request, self.session, self.rt_fmtenant, event1)

        # Retrieve created famiport objects
        famiport_event = self.fm_session.query(FamiPortEvent).filter_by(userside_id = altair_famiport_performance_group.id) \
                                                             .filter_by(invalidated_at = None).one()
        famiport_performance = self.fm_session.query(FamiPortPerformance).filter_by(userside_id = altair_famiport_performance.id) \
                                                                         .filter_by(invalidated_at = None).one()
        famiport_salessegment = self.fm_session.query(FamiPortSalesSegment).filter_by(userside_id = altair_famiport_salessegment_pair.id) \
                                                                           .filter_by(invalidated_at = None).one()

        # Make sure expected FamiPort objects are created
        self.assertEqual(famiport_venue.id, famiport_event.venue_id)
        self.assertEqual(famiport_event.id, famiport_performance.famiport_event_id)
        self.assertEqual(performance1.start_on, famiport_performance.start_at)

        self.assertEqual(famiport_performance.id, famiport_salessegment.famiport_performance_id)
        self.assertEqual(salessegment1.start_at, famiport_salessegment.start_at)
        self.assertEqual(salessegment1.end_at, famiport_salessegment.end_at)
        self.assertEqual(salessegmentgroup1.name, famiport_salessegment.name)

    def test_venue_name_change_with_altairfmvenue_and_fmvenue(self):
        """2nd FM sync after venue name was changed with existing AltairFamiPortVenue and FamiPortVenue
        """

        siteprofile1 = SiteProfile(id = 1, name = u'Zepp DiverCity TOKYO', prefecture = u'東京都')
        site1 = Site(id = 1, siteprofile_id = 1, name = u'Zepp DiverCity TOKYO', visible = True)
        event1 = Event(id = 1, code = 'RT00001', title = u'テストイベント1', organization_id = 15)
        performance1 = Performance(id = 1, event_id = 1, name = u'テスト公演1', code = 'RT0000000001', \
                                   start_on = datetime(2016, 3, 1, 10, 0, 0), end_on = None)
        venue1 = Venue(id = 1, site_id = 1, organization_id = 15, name = u'Zepp DiverCity TOKYO', performance_id = 1)
        salessegmentgroup1 = SalesSegmentGroup(id = 1, organization_id = 15, event_id = 1, kind = 'normal', \
                                               name = u'一般発売', seat_choice = False, \
                                               start_at = datetime(2016, 2, 1, 10, 0, 0), end_at = datetime(2016, 2, 26, 23, 59, 59))
        salessegment1 = SalesSegment(id = 1, sales_segment_group_id = 1, performance_id = 1, event_id = 1, \
                                     payment_delivery_method_pairs = [self.fm_pdmp], public = True, seat_choice = False, \
                                     start_at = datetime(2016, 2, 1, 10, 0, 0), end_at = datetime(2016, 2, 26, 23, 59, 59))

        self.session.add(siteprofile1)
        self.session.add(site1)
        self.session.add(event1)
        self.session.add(performance1)
        self.session.add(venue1)
        self.session.add(salessegmentgroup1)
        self.session.add(salessegment1)
        self.session.flush()

        famiport_genre1 = FamiPortGenre1(code = 1, name = u'音楽')
        self.fm_session.add(famiport_genre1)
        self.fm_session.flush()

        # Create dummy AltairFamiPortVenue and FamiPortVenue for existing ones check test
        dummy_venue = Venue(id = 2, site_id = 1, organization_id = 15, name = u'Zepp DiverCity TOKYO Next', performance_id = None)
        self.session.add(dummy_venue)
        self.session.flush()
        dummy_altair_famiport_venue = create_altair_famiport_venue(self.request, self.session, performance1, name_kana=u'')

        datetime_formatter = create_date_time_formatter(self.request)
        create_famiport_reflection_data(self.request, self.session, event1, datetime_formatter)

        # Retrieve created intermidiate objects: AltairFamiPortVenue, AltairFamiPortPerformanceGroup, AltairFamiPortPerformance, AltairFamiPortSalesSegmentPair
        altair_famiport_venue = self.session.query(AltairFamiPortVenue)\
                                            .filter(AltairFamiPortVenue.siteprofile_id == siteprofile1.id)\
                                            .filter(AltairFamiPortVenue.venue_name == venue1.name).one()
        altair_famiport_performance_group = self.session.query(AltairFamiPortPerformanceGroup)\
                                                        .filter_by(event_id = event1.id).one()
        altair_famiport_performance = self.session.query(AltairFamiPortPerformance)\
                                                  .filter_by(performance_id = performance1.id).one()
        altair_famiport_salessegment_pair = self.session.query(AltairFamiPortSalesSegmentPair)\
                                                .filter(sa.or_(AltairFamiPortSalesSegmentPair.seat_unselectable_sales_segment_id == salessegment1.id, \
                                                               AltairFamiPortSalesSegmentPair.seat_selectable_sales_segment_id == salessegment1.id)).one()

        # Change status from Editing to AwaitingReflection
        for entity in [altair_famiport_venue, altair_famiport_performance_group, altair_famiport_performance, altair_famiport_salessegment_pair]:
            self.__changeStatus(entity, AltairFamiPortReflectionStatus.AwaitingReflection.value)

        # Create FamiPort objects
        submit_to_downstream_sync(self.fm_request, self.session, self.rt_fmtenant, event1)

        venue1.name = u'Zepp DiverCity TOKYO Next'
        self.session.add(venue1)
        self.session.flush()

        # Change status from Editing
        for entity in [altair_famiport_venue, altair_famiport_performance_group, altair_famiport_performance, altair_famiport_salessegment_pair]:
            self.__changeStatus(entity, AltairFamiPortReflectionStatus.Editing.value)

        create_famiport_reflection_data(self.request, self.session, event1, datetime_formatter)

        altair_famiport_venue = self.session.query(AltairFamiPortVenue)\
                                            .filter(AltairFamiPortVenue.siteprofile_id == venue1.site.siteprofile_id)\
                                            .filter(AltairFamiPortVenue.venue_name == venue1.name).one()
        altair_famiport_performance_group = self.session.query(AltairFamiPortPerformanceGroup)\
                                                        .filter(AltairFamiPortPerformanceGroup.event_id == event1.id)\
                                                        .filter(AltairFamiPortPerformanceGroup.altair_famiport_venue_id == altair_famiport_venue.id).one()
        altair_famiport_performance = self.session.query(AltairFamiPortPerformance)\
                                                  .filter(AltairFamiPortPerformance.performance_id == performance1.id).one()

        famiport_venue = self.fm_session.query(FamiPortVenue).filter(FamiPortVenue.userside_id == altair_famiport_venue.id).one()

        # Change status from Editing to AwaitingReflection
        for entity in [altair_famiport_venue, altair_famiport_performance_group, altair_famiport_performance, altair_famiport_salessegment_pair]:
            self.__changeStatus(entity, AltairFamiPortReflectionStatus.AwaitingReflection.value)

        # Create FamiPort objects
        submit_to_downstream_sync(self.fm_request, self.session, self.rt_fmtenant, event1)

        self.assertEqual(venue1.name, altair_famiport_venue.venue_name)
        self.assertEqual(venue1.site.siteprofile.id, altair_famiport_venue.siteprofile_id)

        self.assertEqual(event1.id, altair_famiport_performance_group.event_id)
        self.assertEqual(altair_famiport_venue.id, altair_famiport_performance_group.altair_famiport_venue_id)

        self.assertEqual(performance1.id, altair_famiport_performance.performance_id)
        self.assertEqual(altair_famiport_performance_group.id, altair_famiport_performance.altair_famiport_performance_group_id)

        self.assertEqual(salessegment1.id, altair_famiport_salessegment_pair.seat_unselectable_sales_segment_id)

        self.assertEqual(venue1.name, famiport_venue.name)
        self.assertEqual(resolve_famiport_prefecture_by_name(self.request, venue1.site.siteprofile.prefecture), famiport_venue.prefecture)

        # Retrieve created famiport objects
        famiport_venue = self.fm_session.query(FamiPortVenue).filter(FamiPortVenue.userside_id == altair_famiport_venue.id).one()
        famiport_event = self.fm_session.query(FamiPortEvent).filter_by(userside_id = altair_famiport_performance_group.id) \
                                                             .filter_by(invalidated_at = None).one()
        famiport_performance = self.fm_session.query(FamiPortPerformance).filter(FamiPortPerformance.famiport_event_id == famiport_event.id) \
                                                                         .filter_by(userside_id = altair_famiport_performance.id) \
                                                                         .filter_by(invalidated_at = None).one()
        famiport_salessegment = self.fm_session.query(FamiPortSalesSegment).filter(FamiPortSalesSegment.famiport_performance_id == famiport_performance.id) \
                                                                           .filter_by(userside_id = altair_famiport_salessegment_pair.id) \
                                                                           .filter_by(invalidated_at = None).one()

        # Make sure expected FamiPort objects are created
        self.assertEqual(famiport_venue.id, famiport_event.venue_id)
        self.assertEqual(famiport_event.id, famiport_performance.famiport_event_id)
        self.assertEqual(performance1.start_on, famiport_performance.start_at)

        self.assertEqual(famiport_performance.id, famiport_salessegment.famiport_performance_id)
        self.assertEqual(salessegment1.start_at, famiport_salessegment.start_at)
        self.assertEqual(salessegment1.end_at, famiport_salessegment.end_at)
        self.assertEqual(salessegmentgroup1.name, famiport_salessegment.name)

    def test_venue_id_name_change_without_altairfmvenue_and_fmvenue(self):
        """2nd FM sync after venue id and name were changed without existing AltairFamiPortVenue and FamiPortVenue
        """

        siteprofile1 = SiteProfile(id = 1, name = u'Zepp DiverCity TOKYO', prefecture = u'東京都')
        site1 = Site(id = 1, siteprofile_id = 1, name = u'Zepp DiverCity TOKYO', visible = True)
        event1 = Event(id = 1, code = 'RT00001', title = u'テストイベント1', organization_id = 15)
        performance1 = Performance(id = 1, event_id = 1, name = u'テスト公演1', code = 'RT0000000001', \
                                   start_on = datetime(2016, 3, 1, 10, 0, 0), end_on = None)
        venue1 = Venue(id = 1, site_id = 1, organization_id = 15, name = u'Zepp DiverCity TOKYO', performance_id = 1)
        salessegmentgroup1 = SalesSegmentGroup(id = 1, organization_id = 15, event_id = 1, kind = 'normal', \
                                               name = u'一般発売', seat_choice = False, \
                                               start_at = datetime(2016, 2, 1, 10, 0, 0), end_at = datetime(2016, 2, 26, 23, 59, 59))
        salessegment1 = SalesSegment(id = 1, sales_segment_group_id = 1, performance_id = 1, event_id = 1, \
                                     payment_delivery_method_pairs = [self.fm_pdmp], public = True, seat_choice = False, \
                                     start_at = datetime(2016, 2, 1, 10, 0, 0), end_at = datetime(2016, 2, 26, 23, 59, 59))

        self.session.add(siteprofile1)
        self.session.add(site1)
        self.session.add(event1)
        self.session.add(performance1)
        self.session.add(venue1)
        self.session.add(salessegmentgroup1)
        self.session.add(salessegment1)
        self.session.flush()

        famiport_genre1 = FamiPortGenre1(code = 1, name = u'音楽')
        self.fm_session.add(famiport_genre1)
        self.fm_session.flush()

        datetime_formatter = create_date_time_formatter(self.request)
        create_famiport_reflection_data(self.request, self.session, event1, datetime_formatter)

        # Retrieve created intermidiate objects: AltairFamiPortVenue, AltairFamiPortPerformanceGroup, AltairFamiPortPerformance, AltairFamiPortSalesSegmentPair
        altair_famiport_venue = self.session.query(AltairFamiPortVenue)\
                                            .filter(AltairFamiPortVenue.siteprofile_id == siteprofile1.id)\
                                            .filter(AltairFamiPortVenue.venue_name == venue1.name).one()
        altair_famiport_performance_group = self.session.query(AltairFamiPortPerformanceGroup)\
                                                        .filter_by(event_id = event1.id).one()
        altair_famiport_performance = self.session.query(AltairFamiPortPerformance)\
                                                  .filter_by(performance_id = performance1.id).one()
        altair_famiport_salessegment_pair = self.session.query(AltairFamiPortSalesSegmentPair)\
                                                .filter(sa.or_(AltairFamiPortSalesSegmentPair.seat_unselectable_sales_segment_id == salessegment1.id, \
                                                               AltairFamiPortSalesSegmentPair.seat_selectable_sales_segment_id == salessegment1.id)).one()

        # Change status from Editing to AwaitingReflection
        for entity in [altair_famiport_venue, altair_famiport_performance_group, altair_famiport_performance, altair_famiport_salessegment_pair]:
            self.__changeStatus(entity, AltairFamiPortReflectionStatus.AwaitingReflection.value)

        # Create FamiPort objects
        submit_to_downstream_sync(self.fm_request, self.session, self.rt_fmtenant, event1)

        siteprofile2 = SiteProfile(id = 2, name = u'Zepp DiverCity KYOTO', prefecture = u'京都府')
        site2 = Site(id = 2, siteprofile_id = 2, name = u'Zepp DiverCity KYOTO', visible = True)
        venue2 = Venue(id = 2, site_id = 2, organization_id = 15, name = u'Zepp DiverCity KYOTO', performance_id = performance1.id)
        performance1.venue = venue2
        venue1.delete()

        self.session.add(siteprofile2)
        self.session.add(site2)
        self.session.add(venue2)
        self.session.add(performance1)
        self.session.flush()

        # Change status from Editing
        for entity in [altair_famiport_venue, altair_famiport_performance_group, altair_famiport_performance, altair_famiport_salessegment_pair]:
            self.__changeStatus(entity, AltairFamiPortReflectionStatus.Editing.value)

        create_famiport_reflection_data(self.request, self.session, event1, datetime_formatter)

        altair_famiport_performance = self.session.query(AltairFamiPortPerformance)\
                                                  .filter(AltairFamiPortPerformance.performance_id == performance1.id).one()
        altair_famiport_performance_group = altair_famiport_performance.altair_famiport_performance_group
        altair_famiport_venue = altair_famiport_performance_group.altair_famiport_venue

        famiport_venue = self.fm_session.query(FamiPortVenue).filter(FamiPortVenue.userside_id == altair_famiport_venue.id).one()

        self.assertEqual(venue2.name, altair_famiport_venue.venue_name)
        self.assertEqual(venue2.site.siteprofile.id, altair_famiport_venue.siteprofile_id)

        self.assertEqual(event1.id, altair_famiport_performance_group.event_id)
        self.assertEqual(altair_famiport_venue.id, altair_famiport_performance_group.altair_famiport_venue_id)

        self.assertEqual(performance1.id, altair_famiport_performance.performance_id)
        self.assertEqual(altair_famiport_performance_group.id, altair_famiport_performance.altair_famiport_performance_group_id)

        self.assertEqual(salessegment1.id, altair_famiport_salessegment_pair.seat_unselectable_sales_segment_id)

        self.assertEqual(venue2.name, famiport_venue.name)
        self.assertEqual(resolve_famiport_prefecture_by_name(self.request, venue2.site.siteprofile.prefecture), famiport_venue.prefecture)

        # Change status from Editing to AwaitingReflection
        for entity in [altair_famiport_venue, altair_famiport_performance_group, altair_famiport_performance, altair_famiport_salessegment_pair]:
            self.__changeStatus(entity, AltairFamiPortReflectionStatus.AwaitingReflection.value)

        # Create FamiPort objects
        submit_to_downstream_sync(self.fm_request, self.session, self.rt_fmtenant, event1)

        # Retrieve created famiport objects
        famiport_venue = self.fm_session.query(FamiPortVenue).filter(FamiPortVenue.userside_id == altair_famiport_venue.id).one()
        famiport_event = self.fm_session.query(FamiPortEvent).filter_by(userside_id = altair_famiport_performance_group.id) \
                                                             .filter_by(invalidated_at = None).one()
        famiport_performance = self.fm_session.query(FamiPortPerformance).filter(FamiPortPerformance.famiport_event_id == famiport_event.id) \
                                                                         .filter_by(userside_id = altair_famiport_performance.id) \
                                                                         .filter_by(invalidated_at = None).one()
        famiport_salessegment = self.fm_session.query(FamiPortSalesSegment).filter(FamiPortSalesSegment.famiport_performance_id == famiport_performance.id) \
                                                                           .filter_by(userside_id = altair_famiport_salessegment_pair.id) \
                                                                           .filter_by(invalidated_at = None).one()

        # Make sure expected FamiPort objects are created
        self.assertEqual(famiport_venue.id, famiport_event.venue_id)
        self.assertEqual(famiport_event.id, famiport_performance.famiport_event_id)
        self.assertEqual(performance1.start_on, famiport_performance.start_at)

        self.assertEqual(famiport_performance.id, famiport_salessegment.famiport_performance_id)
        self.assertEqual(salessegment1.start_at, famiport_salessegment.start_at)
        self.assertEqual(salessegment1.end_at, famiport_salessegment.end_at)
        self.assertEqual(salessegmentgroup1.name, famiport_salessegment.name)

    def test_no_change(self):
        """2nd FM sync with no change
        """

        siteprofile1 = SiteProfile(id = 1, name = u'Zepp DiverCity TOKYO', prefecture = u'東京都')
        site1 = Site(id = 1, siteprofile_id = 1, name = u'Zepp DiverCity TOKYO', visible = True)
        event1 = Event(id = 1, code = 'RT00001', title = u'テストイベント1', organization_id = 15)
        performance1 = Performance(id = 1, event_id = 1, name = u'テスト公演1', code = 'RT0000000001', \
                                   start_on = datetime(2016, 3, 1, 10, 0, 0), end_on = None)
        venue1 = Venue(id = 1, site_id = 1, organization_id = 15, name = u'Zepp DiverCity TOKYO', performance_id = 1)
        salessegmentgroup1 = SalesSegmentGroup(id = 1, organization_id = 15, event_id = 1, kind = 'normal', \
                                               name = u'一般発売', seat_choice = False, start_at = datetime(2016, 2, 1, 10, 0, 0), \
                                               end_at = datetime(2016, 2, 26, 23, 59, 59))
        salessegment1 = SalesSegment(id = 1, sales_segment_group_id = 1, performance_id = 1, event_id = 1, \
                                     payment_delivery_method_pairs = [self.fm_pdmp], public = True, seat_choice = False, \
                                     start_at = datetime(2016, 2, 1, 10, 0, 0), end_at = datetime(2016, 2, 26, 23, 59, 59))

        self.session.add(siteprofile1)
        self.session.add(site1)
        self.session.add(event1)
        self.session.add(performance1)
        self.session.add(venue1)
        self.session.add(salessegmentgroup1)
        self.session.add(salessegment1)
        self.session.flush()

        famiport_genre1 = FamiPortGenre1(code = 1, name = u'音楽')
        self.fm_session.add(famiport_genre1)
        self.fm_session.flush()

        datetime_formatter = create_date_time_formatter(self.request)
        create_famiport_reflection_data(self.request, self.session, event1, datetime_formatter)

        # Retrieve created intermidiate objects: AltairFamiPortVenue, AltairFamiPortPerformanceGroup, AltairFamiPortPerformance, AltairFamiPortSalesSegmentPair
        altair_famiport_venue = self.session.query(AltairFamiPortVenue)\
                                            .filter(AltairFamiPortVenue.siteprofile_id == siteprofile1.id)\
                                            .filter(AltairFamiPortVenue.venue_name == venue1.name).one()
        altair_famiport_performance_group = self.session.query(AltairFamiPortPerformanceGroup)\
                                                        .filter_by(event_id = event1.id).one()
        altair_famiport_performance = self.session.query(AltairFamiPortPerformance)\
                                                  .filter_by(performance_id = performance1.id).one()
        altair_famiport_salessegment_pair = self.session.query(AltairFamiPortSalesSegmentPair)\
                                                .filter(sa.or_(AltairFamiPortSalesSegmentPair.seat_unselectable_sales_segment_id == salessegment1.id, \
                                                               AltairFamiPortSalesSegmentPair.seat_selectable_sales_segment_id == salessegment1.id)).one()

        famiport_venue = self.fm_session.query(FamiPortVenue).filter(FamiPortVenue.userside_id == altair_famiport_venue.id).one()

        # Change status from Editing to AwaitingReflection
        for entity in [altair_famiport_venue, altair_famiport_performance_group, altair_famiport_performance, altair_famiport_salessegment_pair]:
            self.__changeStatus(entity, AltairFamiPortReflectionStatus.AwaitingReflection.value)

        # Create FamiPort objects
        submit_to_downstream_sync(self.fm_request, self.session, self.rt_fmtenant, event1)

        # Retrieve created famiport objects
        famiport_event = self.fm_session.query(FamiPortEvent).filter_by(userside_id = altair_famiport_performance_group.id).one()
        famiport_performance = self.fm_session.query(FamiPortPerformance).filter_by(userside_id = altair_famiport_performance.id).one()
        famiport_salessegment = self.fm_session.query(FamiPortSalesSegment).filter_by(userside_id = altair_famiport_salessegment_pair.id).one()

        # Make sure expected FamiPort objects are created
        self.assertEqual(famiport_venue.id, famiport_event.venue_id)
        self.assertEqual(famiport_event.id, famiport_performance.famiport_event_id)
        self.assertEqual(performance1.start_on, famiport_performance.start_at)

        self.assertEqual(famiport_performance.id, famiport_salessegment.famiport_performance_id)
        self.assertEqual(salessegment1.start_at, famiport_salessegment.start_at)
        self.assertEqual(salessegment1.end_at, famiport_salessegment.end_at)
        self.assertEqual(salessegmentgroup1.name, famiport_salessegment.name)


        # Change status from Editing
        for entity in [altair_famiport_venue, altair_famiport_performance_group, altair_famiport_performance, altair_famiport_salessegment_pair]:
           self.__changeStatus(entity, AltairFamiPortReflectionStatus.Editing.value)

        # Auto add again
        create_famiport_reflection_data(self.request, self.session, event1, datetime_formatter)

        # Retrieve created intermidiate objects: AltairFamiPortVenue, AltairFamiPortPerformanceGroup, AltairFamiPortPerformance, AltairFamiPortSalesSegmentPair
        altair_famiport_venue = self.session.query(AltairFamiPortVenue)\
                                            .filter(AltairFamiPortVenue.siteprofile_id == siteprofile1.id)\
                                            .filter(AltairFamiPortVenue.venue_name == venue1.name).one()
        altair_famiport_performance_group = self.session.query(AltairFamiPortPerformanceGroup)\
                                                        .filter_by(event_id = event1.id).one()
        altair_famiport_performance = self.session.query(AltairFamiPortPerformance)\
                                                  .filter_by(performance_id = performance1.id).one()
        altair_famiport_salessegment_pair = self.session.query(AltairFamiPortSalesSegmentPair)\
                                                .filter(sa.or_(AltairFamiPortSalesSegmentPair.seat_unselectable_sales_segment_id == salessegment1.id, \
                                                               AltairFamiPortSalesSegmentPair.seat_selectable_sales_segment_id == salessegment1.id)).one()

        famiport_venue = self.fm_session.query(FamiPortVenue).filter(FamiPortVenue.userside_id == altair_famiport_venue.id).one()

        self.assertEqual(venue1.name, altair_famiport_venue.name)
        self.assertEqual(venue1.site.siteprofile.id, altair_famiport_venue.siteprofile_id)

        self.assertEqual(event1.id, altair_famiport_performance_group.event_id)
        self.assertEqual(altair_famiport_venue.id, altair_famiport_performance_group.altair_famiport_venue_id)

        self.assertEqual(performance1.id, altair_famiport_performance.performance_id)
        self.assertEqual(altair_famiport_performance_group.id, altair_famiport_performance.altair_famiport_performance_group_id)

        self.assertEqual(salessegment1.id, altair_famiport_salessegment_pair.seat_unselectable_sales_segment_id)

        self.assertEqual(venue1.name, famiport_venue.name)

        # Change status from Editing to AwaitingReflection
        for entity in [altair_famiport_venue, altair_famiport_performance_group, altair_famiport_performance, altair_famiport_salessegment_pair]:
            self.__changeStatus(entity, AltairFamiPortReflectionStatus.AwaitingReflection.value)

        # Create FamiPort objects
        submit_to_downstream_sync(self.fm_request, self.session, self.rt_fmtenant, event1)

        # Retrieve created famiport objects
        famiport_venue = self.fm_session.query(FamiPortVenue).filter(FamiPortVenue.userside_id == altair_famiport_venue.id).one()
        famiport_event = self.fm_session.query(FamiPortEvent).filter_by(userside_id = altair_famiport_performance_group.id) \
                                                             .filter_by(invalidated_at = None).one()
        famiport_performance = self.fm_session.query(FamiPortPerformance).filter(FamiPortPerformance.famiport_event_id == famiport_event.id) \
                                                                         .filter_by(userside_id = altair_famiport_performance.id) \
                                                                         .filter_by(invalidated_at = None).one()
        famiport_salessegment = self.fm_session.query(FamiPortSalesSegment).filter(FamiPortSalesSegment.famiport_performance_id == famiport_performance.id) \
                                                                           .filter_by(userside_id = altair_famiport_salessegment_pair.id) \
                                                                           .filter_by(invalidated_at = None).one()

        # Make sure expected FamiPort objects are created
        self.assertEqual(famiport_venue.id, famiport_event.venue_id)
        self.assertEqual(famiport_event.id, famiport_performance.famiport_event_id)
        self.assertEqual(performance1.start_on, famiport_performance.start_at)

        self.assertEqual(famiport_performance.id, famiport_salessegment.famiport_performance_id)
        self.assertEqual(salessegment1.start_at, famiport_salessegment.start_at)
        self.assertEqual(salessegment1.end_at, famiport_salessegment.end_at)
        self.assertEqual(salessegmentgroup1.name, famiport_salessegment.name)

    def test_venue_and_performance_starton_change_without_altairfmvenue_and_fmvenue(self):
        """2nd FM sync with performance.start.on change without existing AltairFamiPortVenue and FamiPortVenue
        """

        siteprofile1 = SiteProfile(id = 1, name = u'Zepp DiverCity TOKYO', prefecture = u'東京都')
        site1 = Site(id = 1, siteprofile_id = 1, name = u'Zepp DiverCity TOKYO', visible = True)
        event1 = Event(id = 1, code = 'RT00001', title = u'テストイベント1', organization_id = 15)
        performance1 = Performance(id = 1, event_id = 1, name = u'テスト公演1', code = 'RT0000000001', \
                                   start_on = datetime(2016, 3, 1, 10, 0, 0), end_on = None)
        venue1 = Venue(id = 1, site_id = 1, organization_id = 15, name = u'Zepp DiverCity TOKYO', performance_id = 1)
        salessegmentgroup1 = SalesSegmentGroup(id = 1, organization_id = 15, event_id = 1, kind = 'normal', \
                                               name = u'一般発売', seat_choice = False, start_at = datetime(2016, 2, 1, 10, 0, 0), \
                                               end_at = datetime(2016, 2, 26, 23, 59, 59))
        salessegment1 = SalesSegment(id = 1, sales_segment_group_id = 1, performance_id = 1, event_id = 1, \
                                     payment_delivery_method_pairs = [self.fm_pdmp], public = True, seat_choice = False, \
                                     start_at = datetime(2016, 2, 1, 10, 0, 0), end_at = datetime(2016, 2, 26, 23, 59, 59))

        self.session.add(siteprofile1)
        self.session.add(site1)
        self.session.add(event1)
        self.session.add(performance1)
        self.session.add(venue1)
        self.session.add(salessegmentgroup1)
        self.session.add(salessegment1)
        self.session.flush()

        famiport_genre1 = FamiPortGenre1(code = 1, name = u'音楽')
        self.fm_session.add(famiport_genre1)
        self.fm_session.flush()

        datetime_formatter = create_date_time_formatter(self.request)
        create_famiport_reflection_data(self.request, self.session, event1, datetime_formatter)

        # Retrieve created intermidiate objects: AltairFamiPortVenue, AltairFamiPortPerformanceGroup, AltairFamiPortPerformance, AltairFamiPortSalesSegmentPair
        altair_famiport_venue = self.session.query(AltairFamiPortVenue)\
                                            .filter(AltairFamiPortVenue.siteprofile_id == siteprofile1.id)\
                                            .filter(AltairFamiPortVenue.venue_name == venue1.name).one()
        altair_famiport_performance_group = self.session.query(AltairFamiPortPerformanceGroup).filter_by(event_id = event1.id).one()
        altair_famiport_performance = self.session.query(AltairFamiPortPerformance).filter_by(performance_id = performance1.id).one()
        altair_famiport_salessegment_pair = self.session.query(AltairFamiPortSalesSegmentPair)\
                                                        .filter(sa.or_(AltairFamiPortSalesSegmentPair.seat_unselectable_sales_segment_id == salessegment1.id, \
                                                                       AltairFamiPortSalesSegmentPair.seat_selectable_sales_segment_id == salessegment1.id)).one()

        self.assertEqual(performance1.start_on, altair_famiport_performance.start_at)

        # Change status from Editing to AwaitingReflection
        for entity in [altair_famiport_venue, altair_famiport_performance_group, altair_famiport_performance, altair_famiport_salessegment_pair]:
            self.__changeStatus(entity, AltairFamiPortReflectionStatus.AwaitingReflection.value)

        # Create FamiPort objects
        submit_to_downstream_sync(self.fm_request, self.session, self.rt_fmtenant, event1)

        siteprofile2 = SiteProfile(id = 2, name = u'Zepp DiverCity KYOTO', prefecture = u'京都府')
        site2 = Site(id = 2, siteprofile_id = 2, name = u'Zepp DiverCity KYOTO', visible = True)
        venue2 = Venue(id = 2, site_id = 2, organization_id = 15, name = u'Zepp DiverCity KYOTO', performance_id = performance1.id)
        performance1.venue = venue2
        venue1.delete()
        performance1.start_on = datetime(2016, 3, 1, 11, 0, 0)

        self.session.add(siteprofile2)
        self.session.add(site2)
        self.session.add(venue2)
        self.session.add(performance1)
        self.session.flush()

        # Change status from Editing
        for entity in [altair_famiport_venue, altair_famiport_performance_group, altair_famiport_performance, altair_famiport_salessegment_pair]:
            self.__changeStatus(entity, AltairFamiPortReflectionStatus.Editing.value)

        create_famiport_reflection_data(self.request, self.session, event1, datetime_formatter)

        altair_famiport_performance = self.session.query(AltairFamiPortPerformance)\
                                                  .filter(AltairFamiPortPerformance.performance_id == performance1.id).one()
        altair_famiport_performance_group = altair_famiport_performance.altair_famiport_performance_group
        altair_famiport_venue = altair_famiport_performance_group.altair_famiport_venue

        self.assertEqual(performance1.start_on, altair_famiport_performance.start_at)


        # Change status from Editing to AwaitingReflection
        for entity in [altair_famiport_venue, altair_famiport_performance_group, altair_famiport_performance, altair_famiport_salessegment_pair]:
            self.__changeStatus(entity, AltairFamiPortReflectionStatus.AwaitingReflection.value)

        # Create FamiPort objects
        submit_to_downstream_sync(self.fm_request, self.session, self.rt_fmtenant, event1)

        # Retrieve created famiport objects
        famiport_venue = self.fm_session.query(FamiPortVenue).filter(FamiPortVenue.userside_id == altair_famiport_venue.id).one()
        famiport_event = self.fm_session.query(FamiPortEvent).filter_by(userside_id = altair_famiport_performance_group.id) \
                                                             .filter_by(invalidated_at = None).one()
        famiport_performance = self.fm_session.query(FamiPortPerformance).filter(FamiPortPerformance.famiport_event_id == famiport_event.id) \
                                                                         .filter_by(userside_id = altair_famiport_performance.id) \
                                                                         .filter_by(invalidated_at = None).one()
        famiport_salessegment = self.fm_session.query(FamiPortSalesSegment).filter(FamiPortSalesSegment.famiport_performance_id == famiport_performance.id) \
                                                                           .filter_by(userside_id = altair_famiport_salessegment_pair.id) \
                                                                           .filter_by(invalidated_at = None).one()

        # Make sure expected FamiPort objects are created
        self.assertEqual(famiport_venue.id, famiport_event.venue_id)
        self.assertEqual(famiport_event.id, famiport_performance.famiport_event_id)
        self.assertEqual(performance1.start_on, famiport_performance.start_at)

        self.assertEqual(altair_famiport_venue.id, famiport_performance.famiport_event.venue.userside_id)
        self.assertEqual(famiport_performance.id, famiport_salessegment.famiport_performance_id)
        self.assertEqual(salessegment1.start_at, famiport_salessegment.start_at)
        self.assertEqual(salessegment1.end_at, famiport_salessegment.end_at)
        self.assertEqual(salessegmentgroup1.name, famiport_salessegment.name)

    def test_add_sales_segment(self):
        """
        2nd FM sync with new SalesSegment added
        """

        siteprofile1 = SiteProfile(id = 1, name = u'Zepp DiverCity TOKYO', prefecture = u'東京都')
        site1 = Site(id = 1, siteprofile_id = 1, name = u'Zepp DiverCity TOKYO', visible = True)
        event1 = Event(id = 1, code = 'RT00001', title = u'テストイベント1', organization_id = 15)
        performance1 = Performance(id = 1, event_id = 1, name = u'テスト公演1', code = 'RT0000000001', \
                                   start_on = datetime(2016, 3, 1, 10, 0, 0), end_on = None)
        venue1 = Venue(id = 1, site_id = 1, organization_id = 15, name = u'Zepp DiverCity TOKYO', performance_id = 1)
        salessegmentgroup1 = SalesSegmentGroup(id = 1, organization_id = 15, event_id = 1, kind = 'normal', \
                                               name = u'一般発売', seat_choice = False, start_at = datetime(2016, 2, 1, 10, 0, 0), \
                                               end_at = datetime(2016, 2, 26, 23, 59, 59))
        salessegment1 = SalesSegment(id = 1, sales_segment_group_id = 1, performance_id = 1, event_id = 1, \
                                     payment_delivery_method_pairs = [self.fm_pdmp], public = True, seat_choice = False, \
                                     start_at = datetime(2016, 2, 1, 10, 0, 0), end_at = datetime(2016, 2, 29, 23, 59, 59))

        self.session.add(siteprofile1)
        self.session.add(site1)
        self.session.add(event1)
        self.session.add(performance1)
        self.session.add(venue1)
        self.session.add(salessegmentgroup1)
        self.session.add(salessegment1)
        self.session.flush()

        famiport_genre1 = FamiPortGenre1(code = 1, name = u'音楽')
        self.fm_session.add(famiport_genre1)
        self.fm_session.flush()

        datetime_formatter = create_date_time_formatter(self.request)
        create_famiport_reflection_data(self.request, self.session, event1, datetime_formatter)

        # Retrieve created intermidiate objects: AltairFamiPortVenue, AltairFamiPortPerformanceGroup, AltairFamiPortPerformance, AltairFamiPortSalesSegmentPair
        altair_famiport_venue = self.session.query(AltairFamiPortVenue)\
                                            .filter(AltairFamiPortVenue.siteprofile_id == siteprofile1.id)\
                                            .filter(AltairFamiPortVenue.venue_name == venue1.name).one()
        altair_famiport_performance_group = self.session.query(AltairFamiPortPerformanceGroup).filter_by(event_id = event1.id).one()
        altair_famiport_performance = self.session.query(AltairFamiPortPerformance).filter_by(performance_id = performance1.id).one()
        altair_famiport_salessegment_pair = self.session.query(AltairFamiPortSalesSegmentPair)\
                                                .filter(sa.or_(AltairFamiPortSalesSegmentPair.seat_unselectable_sales_segment_id == salessegment1.id, \
                                                               AltairFamiPortSalesSegmentPair.seat_selectable_sales_segment_id == salessegment1.id)).one()

        # Change status from Editing to AwaitingReflection
        for entity in [altair_famiport_venue, altair_famiport_performance_group, altair_famiport_performance, altair_famiport_salessegment_pair]:
            self.__changeStatus(entity, AltairFamiPortReflectionStatus.AwaitingReflection.value)

        # Create FamiPort objects
        submit_to_downstream_sync(self.fm_request, self.session, self.rt_fmtenant, event1)

        salessegment2 = SalesSegment(id = 2, sales_segment_group_id = 1, performance_id = 1, event_id = 1, \
                                     payment_delivery_method_pairs = [self.fm_pdmp], public = True, seat_choice = True, \
                                     start_at = datetime(2016, 3, 1, 0, 0, 0), end_at = datetime(2016, 3, 31, 23, 59, 59))
        self.session.add(salessegment2)
        self.session.flush()

        # Change status to Editing
        for entity in [altair_famiport_venue, altair_famiport_performance_group, altair_famiport_performance, altair_famiport_salessegment_pair]:
            self.__changeStatus(entity, AltairFamiPortReflectionStatus.Editing.value)

        create_famiport_reflection_data(self.request, self.session, event1, datetime_formatter)

        altair_famiport_salessegment_pair = self.session.query(AltairFamiPortSalesSegmentPair)\
                                                .filter(AltairFamiPortSalesSegmentPair.altair_famiport_performance_id == altair_famiport_performance.id).one()

        self.assertEqual(altair_famiport_salessegment_pair.seat_unselectable_sales_segment_id, salessegment1.id)
        self.assertEqual(altair_famiport_salessegment_pair.seat_selectable_sales_segment_id, salessegment2.id)

        # Change status from Editing to AwaitingReflection
        for entity in [altair_famiport_venue, altair_famiport_performance_group, altair_famiport_performance, altair_famiport_salessegment_pair]:
            self.__changeStatus(entity, AltairFamiPortReflectionStatus.AwaitingReflection.value)

        # Create FamiPort objects
        submit_to_downstream_sync(self.fm_request, self.session, self.rt_fmtenant, event1)

        # Retrieve created famiport objects
        famiport_venue = self.fm_session.query(FamiPortVenue).filter(FamiPortVenue.userside_id == altair_famiport_venue.id).one()
        famiport_event = self.fm_session.query(FamiPortEvent).filter_by(userside_id = altair_famiport_performance_group.id) \
                                                             .filter_by(invalidated_at = None).one()
        famiport_performance = self.fm_session.query(FamiPortPerformance).filter(FamiPortPerformance.famiport_event_id == famiport_event.id) \
                                                                         .filter_by(userside_id = altair_famiport_performance.id) \
                                                                         .filter_by(invalidated_at = None).one()
        famiport_salessegment = self.fm_session.query(FamiPortSalesSegment).filter(FamiPortSalesSegment.famiport_performance_id == famiport_performance.id) \
                                                                           .filter_by(userside_id = altair_famiport_salessegment_pair.id) \
                                                                           .filter_by(invalidated_at = None).one()

        # Make sure expected FamiPort objects are created
        self.assertEqual(famiport_venue.id, famiport_event.venue_id)
        self.assertEqual(famiport_event.id, famiport_performance.famiport_event_id)
        self.assertEqual(performance1.start_on, famiport_performance.start_at)

        self.assertEqual(famiport_performance.id, famiport_salessegment.famiport_performance_id)
        self.assertEqual(salessegment1.start_at, famiport_salessegment.start_at)
        self.assertEqual(salessegment2.end_at, famiport_salessegment.end_at)
        self.assertEqual(salessegmentgroup1.name, famiport_salessegment.name)
