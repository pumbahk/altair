# -*- coding:utf-8 -*-

import unittest
from pyramid import testing
from altair.app.ticketing.testing import _setup_db, _teardown_db, DummyRequest


class SalesSegmentGroupsTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.include('pyramid_mako')
        self.config.add_mako_renderer('.html')
        self.session = _setup_db(
            [
                'altair.app.ticketing.core.models',
                'altair.app.ticketing.orders.models',
                'altair.app.ticketing.lots.models',
            ])
        import sqlalchemy.orm
        sqlalchemy.orm.configure_mappers()

    def tearDown(self):
        _teardown_db()
        testing.tearDown()

    def _getTarget(self):
        from ..views import SalesSegmentGroups
        return SalesSegmentGroups

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_new_post(self):
        from altair.app.ticketing.core.models import (
            Organization,
            Operator,
            Event,
            OrganizationSetting,
            Account,
            SalesSegmentKindEnum,
            SalesSegmentGroup,
        )
        organization = Organization(short_name='testing')
        account = Account(organization=organization)
        organization_setting = OrganizationSetting(organization=organization,
                                                   name=u"default")
        user = Operator(organization=organization)
        event = Event(organization=organization)

        self.session.add(organization)
        self.session.flush()

        context = testing.DummyResource(
            user=user,
            organization=organization,
            event=event,
            sales_segment_group=None
        )
        request = DummyRequest(
            context=context,
            POST=dict(
                event_id=str(event.id),
                account_id=str(account.id),
                name='testing sales segment group',
                kind='normal',
                start_at="2013-10-10 00:00",
                end_at="2013-10-10 00:00",
            )
        )

        target = self._makeOne(context, request)

        result = target.new_post()
        self.assertFalse(isinstance(result, dict))
        ssg = self.session.query(SalesSegmentGroup).filter_by(
            name="testing sales segment group").one()
        self.assertEqual(ssg.organization, organization)
        self.assertEqual(ssg.event, event)

    def test_edit_post(self):
        from datetime import time, datetime
        from altair.app.ticketing.core.models import (
            Organization,
            Operator,
            Event,
            OrganizationSetting,
            Account,
            SalesSegmentGroup,
            SalesSegment,
        )
        organization = Organization(short_name='testing')
        organization_setting = OrganizationSetting(organization=organization,
                                                   name=u"default")
        account = Account(organization=organization)
        user = Operator(organization=organization)
        event = Event(organization=organization)
        sales_segment_group = SalesSegmentGroup(
            event=event,
            organization=organization,
            sales_segments=[
                SalesSegment(),
            ],
        )
        self.session.add(organization)
        self.session.flush()

        context = testing.DummyResource(
            user=user,
            organization=organization,
            event=event,
            sales_segment_group=sales_segment_group
            )
        request = DummyRequest(
            context=context,
            matchdict=dict(
                sales_segment_group_id=str(sales_segment_group.id),
            ),
            matched_route=testing.DummyResource(name=''),
            POST={
                "id": str(sales_segment_group.id),
                "event_id": str(event.id),
                "account_id": str(account.id),
                "name": 'testing sales segment group',
                "kind": 'normal',
                "start_at": '2013-01-01 00:00',
                "end_day_prior_to_performance": "1",
                "end_time": '23:59:00',
            }
        )

        target = self._makeOne(context, request)

        result = target._edit_post()

        if result:
            for f, msgs in result.errors.items():
                print f,
                for m in msgs:
                    print m

        self.assertIsNone(result)

        self.assertEqual(sales_segment_group.start_at, datetime(2013, 1, 1))
        self.assertEqual(sales_segment_group.end_day_prior_to_performance, 1)
        self.assertEqual(sales_segment_group.end_time, time(23, 59, 0))
        ss = sales_segment_group.sales_segments[0]

        self.assertEqual(ss.organization, organization)
        self.assertEqual(ss.event, event)

    def test_bind_membergroup_post(self):
        from altair.app.ticketing.core.models import (
            Organization,
            Operator,
            Event,
            OrganizationSetting,
            Account,
            SalesSegmentGroup,
            SalesSegment,
        )
        from altair.app.ticketing.users.models import (
            MemberGroup,
            Membership,
        )
        organization = Organization(short_name='testing')
        membership = Membership(organization=organization)
        membergroups = [MemberGroup(membership=membership)
                        for i in range(10)]
            

        organization_setting = OrganizationSetting(organization=organization,
                                                   name=u"default")
        account = Account(organization=organization)
        user = Operator(organization=organization)
        event = Event(organization=organization)
        sales_segment_group = SalesSegmentGroup(
            event=event,
            organization=organization,
            sales_segments=[
                SalesSegment(),
            ],
        )
        self.session.add(organization)
        self.session.flush()

        context = testing.DummyResource(
            user=user,
            organization=organization,
            event=event,
            sales_segment_group=sales_segment_group
        )
        redirect_to = "/redirect/to"
        request = DummyRequest(
            context=context,
            POST=([('redirect_to', redirect_to)]
                  + [('membergroups', str(m.id))
                     for m in membergroups]),
            matchdict=dict(
                sales_segment_group_id=str(sales_segment_group.id),
            ),
        )

        target = self._makeOne(context, request)

        result = target.bind_membergroup_post()

        self.assertEqual(result.location,
                         redirect_to)

        self.assertEqual(sales_segment_group.membergroups,
                         membergroups)
        self.assertEqual(sales_segment_group.sales_segments[0].membergroups,
                         membergroups)
