# encoding: utf-8
import unittest
from pyramid.testing import DummyResource, DummyModel, setUp
from altair.app.ticketing.testing import DummyRequest, _setup_db, _teardown_db

class PerformanceViewTests(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db([
            'altair.app.ticketing.core.models',
            'altair.app.ticketing.cart.models',
            'altair.app.ticketing.orders.models',
            ])
        self.config = setUp()
        self.config.include('altair.app.ticketing.events.performances')

    def tearDown(self):
        _teardown_db()

    def _getTarget(self):
        from ..views import Performances
        return Performances

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_9662(self):
        from datetime import datetime
        from pyramid.httpexceptions import HTTPFound
        from altair.app.ticketing.core.models import (
            Organization,
            Event,
            Performance,
            Venue,
            Site,
            SalesSegmentGroup,
            SalesSegmentGroupSetting,
            SalesSegment,
            )
        from altair.app.ticketing.users.models import (
            Membership,
            MemberGroup,
            )
        organization = Organization(name=u'xxx', short_name=u'xxx', code=u'xX', id=15)
        event = Event(organization=organization, title=u'event')
        membership = Membership(organization=organization, name='membership')
        membergroup = MemberGroup(membership=membership, name='membergroup')
        site = Site()
        venue = Venue(organization=organization, site=site)
        self.session.add(venue)
        sales_segment_group = SalesSegmentGroup(
            organization=organization,
            event=event,
            name='sales_segment_group',
            membergroups=[membergroup],
            start_at=datetime(2015, 1, 1, 0, 0, 0),
            end_at=datetime(2015,1, 2, 0, 0, 0),
            public=True,
            setting=SalesSegmentGroupSetting()
            )
        self.session.add(sales_segment_group)
        self.session.flush()
        request = DummyRequest(params={
            'id': '',
            'name': u'公演名',
            'code': u'XXXXXX000000',
            'start_on.year': '2015',
            'start_on.month': '5',
            'start_on.day': '1',
            'venue_id': 1,
            'account_id': 15,
        })
        context = DummyResource(
            request=request,
            event=event,
            user=DummyModel(organization_id=organization.id),
            organization=organization,
            )
        target = self._makeOne(context, request)
        retval = target.new_post()
        performance = self.session.query(Performance).one()
        self.assertEqual(len(performance.sales_segments), 1)
        self.assertEqual(performance.sales_segments[0].sales_segment_group_id, sales_segment_group.id)
        self.assertEqual(performance.sales_segments[0].membergroups, sales_segment_group.membergroups)
        self.assertIsInstance(retval, HTTPFound)

