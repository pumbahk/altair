# -*- coding:utf-8 -*-
import unittest
import mock
from pyramid import testing
from datetime import datetime
from altair.app.ticketing.testing import _setup_db, _teardown_db
from altair.app.ticketing.core.models import DBSession as session
from altair.app.ticketing.core.models import (
    Event,
    Performance,
    SalesSegmentGroup,
    SalesSegment,
    PaymentDeliveryMethodPair,
    PaymentMethod,
    DeliveryMethod,
    Venue,
    Site,
    FamiPortTenant
)
from altair.app.ticketing.famiport.userside_models import (
    AltairFamiPortVenue,
    AltairFamiPortPerformanceGroup,
    AltairFamiPortPerformance,
    AltairFamiPortSalesSegmentPair
)
from altair.app.ticketing.payments import plugins

from ..famiport_helpers import get_famiport_reflection_warnings, get_famiport_reflect_button_status

class FamiPortReflectionStatusLogicTest(unittest.TestCase):
    """FM連携の連携要否判定ロジック
    """

    def setUp(self):
        self.session = _setup_db(modules=[
            "altair.app.ticketing.core.models",
            "altair.app.ticketing.famiport.userside_models"
            ])

    def tearDown(self):
        _teardown_db()

    def _create_non_fm_pdmp_event(self):
        not_fm_pdmp1 = PaymentDeliveryMethodPair(
            payment_method=PaymentMethod(
                payment_plugin_id=plugins.SEJ_PAYMENT_PLUGIN_ID,
                fee=0
            ),
            delivery_method=DeliveryMethod(
                delivery_plugin_id=plugins.SEJ_DELIVERY_PLUGIN_ID
            ),
            system_fee=0,
            transaction_fee=0,
            discount=0
        )
        not_fm_pdmp2 = PaymentDeliveryMethodPair(
            payment_method=PaymentMethod(
                payment_plugin_id=plugins.MULTICHECKOUT_PAYMENT_PLUGIN_ID,
                fee=0
            ),
            delivery_method=DeliveryMethod(
                delivery_plugin_id=plugins.SEJ_DELIVERY_PLUGIN_ID
            ),
            system_fee=0,
            transaction_fee=0,
            discount=0
        )
        not_fm_pdmp3 = PaymentDeliveryMethodPair(
            payment_method=PaymentMethod(
                payment_plugin_id=plugins.MULTICHECKOUT_PAYMENT_PLUGIN_ID,
                fee=0
            ),
            delivery_method=DeliveryMethod(
                delivery_plugin_id=plugins.SEJ_DELIVERY_PLUGIN_ID
            ),
            system_fee=0,
            transaction_fee=0,
            discount=0
        )
        sales_segment1 = SalesSegment(
            start_at=datetime(2016,6,1,10,0),
            end_at=datetime(2016,6,10,10,0),
            public=True,
            payment_delivery_method_pairs=[not_fm_pdmp1]
        )
        sales_segment2 = SalesSegment(
            start_at=datetime(2016,6,15,10,0),
            end_at=datetime(2016,6,25,10,0),
            public=False,
            payment_delivery_method_pairs=[not_fm_pdmp2]
        )
        performance1 = Performance(
            name=u'公演１',
            start_on=datetime(2016,6,30,10,0),
            sales_segments=[sales_segment1,sales_segment2]
        )
        sales_segment_group1 = SalesSegmentGroup(
            start_at=datetime(2016,6,1,10,0),
            end_at=datetime(2016,6,10,10,0),
            public=True,
            payment_delivery_method_pairs=[not_fm_pdmp3]
        )
        event = Event(
            sales_segment_groups=[sales_segment_group1],
            performances=[performance1]
        )
        session.add(event)
        session.flush()
        return event

    def _create_fm_pdmp_event(self):
        fm_pdmp1 = PaymentDeliveryMethodPair(
            payment_method=PaymentMethod(
                payment_plugin_id=plugins.FAMIPORT_PAYMENT_PLUGIN_ID,
                fee=0
            ),
            delivery_method=DeliveryMethod(
                delivery_plugin_id=plugins.FAMIPORT_DELIVERY_PLUGIN_ID
            ),
            system_fee=0,
            transaction_fee=0,
            discount=0
        )
        fm_pdmp2 = PaymentDeliveryMethodPair(
            payment_method=PaymentMethod(
                payment_plugin_id=plugins.MULTICHECKOUT_PAYMENT_PLUGIN_ID,
                fee=0
            ),
            delivery_method=DeliveryMethod(
                delivery_plugin_id=plugins.FAMIPORT_DELIVERY_PLUGIN_ID
            ),
            system_fee=0,
            transaction_fee=0,
            discount=0
        )
        fm_pdmp3 = PaymentDeliveryMethodPair(
            payment_method=PaymentMethod(
                payment_plugin_id=plugins.FAMIPORT_PAYMENT_PLUGIN_ID,
                fee=0
            ),
            delivery_method=DeliveryMethod(
                delivery_plugin_id=plugins.FAMIPORT_DELIVERY_PLUGIN_ID
            ),
            system_fee=0,
            transaction_fee=0,
            discount=0
        )
        sales_segment_group1 = SalesSegmentGroup(
            name=u'一般販売',
            start_at=datetime(2016,6,1,10,0),
            end_at=datetime(2016,6,10,10,0),
            public=True,
            payment_delivery_method_pairs=[fm_pdmp3]
        )
        sales_segment1 = SalesSegment(
            start_at=datetime(2016,6,1,10,0),
            end_at=datetime(2016,6,10,10,0),
            public=True,
            payment_delivery_method_pairs=[fm_pdmp1],
            sales_segment_group=sales_segment_group1
        )
        sales_segment2 = SalesSegment(
            start_at=datetime(2016,6,15,10,0),
            end_at=datetime(2016,6,25,10,0),
            public=False,
            payment_delivery_method_pairs=[fm_pdmp2]
        )
        performance1 = Performance(
            name=u'公演１',
            start_on=datetime(2016,6,30,10,0),
            sales_segments=[sales_segment1],
            venue=Venue(
                site=Site(siteprofile_id=999),
                organization_id=15,
                name=u'どこどこ会場'
            )
        )
        event = Event(
            sales_segment_groups=[sales_segment_group1],
            performances=[performance1],
            organization_id=15
        )
        session.add(event)
        session.flush()
        altair_venue = AltairFamiPortVenue(
            organization_id=15,
            siteprofile_id=999,
            famiport_venue_id=1,
            venue_name=u'どこどこ会場',
            name=u'どこどこ会場',
            name_kana=u'ドコドコカイジョウ'
        )
        session.add(altair_venue)
        altair_fmpg = AltairFamiPortPerformanceGroup(
            event=event,
            organization_id=15,
            code_1=1,
            code_2=1,
            altair_famiport_venue=altair_venue
        )
        session.add(altair_fmpg)
        altair_fmp = AltairFamiPortPerformance(
            performance=performance1,
            start_at=datetime(2016,6,30,10,0),
            altair_famiport_performance_group=altair_fmpg
        )
        session.add(altair_fmp)
        altair_ssp = AltairFamiPortSalesSegmentPair(
            seat_unselectable_sales_segment=sales_segment1,
            altair_famiport_performance=altair_fmp,
            code=1,
            name=u'一般販売'
        )
        session.add(altair_ssp)
        tenant = FamiPortTenant(
            organization_id=15,
            name=u'楽チケ',
            code=1
        )
        session.add(tenant)
        session.flush()
        return event

    def test_reflection_not_need_event(self):
        """ファミマ決済引取がない場合は、連携不要"""
        event = self._create_non_fm_pdmp_event()

        warnings = get_famiport_reflection_warnings(testing.DummyRequest, session, event.performances[0])
        status = get_famiport_reflect_button_status(testing.DummyRequest, session, event)
        self.assertEqual(warnings, {})
        self.assertEqual(status, u"NO_NEED_REFLECTION")

    @mock.patch('altair.app.ticketing.famiport.api.get_famiport_sales_segment_by_userside_id')
    def test_reflection_completed_event(self, get_famiport_sales_segment_by_userside_id):
        """ファミマ決済引取があり、連携も完了している場合は連携注意文言なし"""
        event = self._create_fm_pdmp_event()
        performance = event.performances[0]
        get_famiport_sales_segment_by_userside_id.return_value = dict(
            start_at=datetime(2016,6,1,10,0),
            end_at=datetime(2016,6,10,10,0),
            name=u'一般販売'
        )

        warnings = get_famiport_reflection_warnings(testing.DummyRequest, session, performance)
        status = get_famiport_reflect_button_status(testing.DummyRequest, session, event)
        self.assertEqual(warnings.get(performance.id), [])
        self.assertEqual(warnings.keys(), [performance.id])
        self.assertEqual(status, u"ALL_REFLECTED")
