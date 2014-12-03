# -*- coding:utf-8 -*-

""" TBA
"""

import unittest
from pyramid import testing
from altair.app.ticketing.testing import DummyRequest

def _setup_db():
    from sqlalchemy import create_engine
    import sqlahelper
    engine = create_engine('sqlite:///')
    sqlahelper.add_engine(engine)
    session = sqlahelper.get_session()
    import altair.app.ticketing.models
    import altair.app.ticketing.core.models
    import altair.app.ticketing.cart.models
    sqlahelper.get_base().metadata.create_all(bind=session.bind)
    return session

def _teardown_db():
    import sqlahelper
    session = sqlahelper.get_session()
    session.remove()
    sqlahelper.get_base().metadata.drop_all(bind=session.bind)

class OrderReviewResourceTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.include('altair.app.ticketing.cart.request')
        self.session = _setup_db()
        from altair.sqlahelper import register_sessionmaker_with_engine
        register_sessionmaker_with_engine(
            self.config.registry,
            'slave',
            self.session.bind,
            self.session.session_factory
            )

    def tearDown(self):
        _teardown_db()
        testing.tearDown()

    def _getTarget(self):
        from ..resources import OrderReviewResource
        return OrderReviewResource

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_order_no(self):
        from altair.app.ticketing.core.models import Host, Organization
        from altair.app.ticketing.users.models import Membership
        request = DummyRequest(params=dict(order_no='000000000001'))
        host = Host(host_name=request.host,
                    organization=Organization(short_name="testing"))
        organization = host.organization
        membership = Membership(organization=organization, name="89ers")
        self.session.add(host)
        self.session.add(membership)
        self.session.flush()

        target = self._makeOne(request)
        self.assertEqual(target.order_no, '000000000001')
        self.assertEqual(target.primary_membership.id, membership.id)
