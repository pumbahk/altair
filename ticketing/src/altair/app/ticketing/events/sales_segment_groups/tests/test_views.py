# -*- coding:utf-8 -*-

import unittest
from pyramid import testing
from altair.app.ticketing.testing import _setup_db, _teardown_db, DummyRequest


class SalesSegmentGroupsTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.include('altair.app.ticketing.renderers')
        self.session = _setup_db(
            [
                'altair.app.ticketing.core.models',
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
        )
        request = DummyRequest(
            context=context,
            POST=dict(
                event_id=str(event.id),
                account_id=str(account.id),
                name='testing sales segment group',
                kind='normal',
            )
        )

        target = self._makeOne(context, request)

        result = target.new_post()
        if isinstance(result, dict):
            for f, msgs in result['form'].errors.items():
                print f,
                for m in msgs:
                    print m


        ssg = self.session.query(SalesSegmentGroup).filter_by(
            name="testing sales segment group").one()
        self.assertEqual(ssg.organization, organization)
        self.assertEqual(ssg.event, event)

    def test_edit_post(self):
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

        context = testing.DummyResource(user=user)
        request = DummyRequest(
            context=context,
            matchdict=dict(
                sales_segment_group_id=str(sales_segment_group.id),
            ),
            matched_route=testing.DummyResource(name=''),
            POST=dict(
                id=str(sales_segment_group.id),
                event_id=str(event.id),
                account_id=str(account.id),
                name='testing sales segment group',
                kind='normal',
                start_at='2013-01-01 00:00',
                end_at='2013-12-31 00:00',
            )
        )

        target = self._makeOne(context, request)

        result = target._edit_post()

        if result:
            for f, msgs in result.errors.items():
                print f,
                for m in msgs:
                    print m

        self.assertIsNone(result)

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
