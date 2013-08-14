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

