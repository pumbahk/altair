# -*- coding:utf-8 -*-
import unittest

import mock
from altair.app.ticketing.testing import _setup_db, _teardown_db
from pyramid import testing


class TestCanceller(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db(modules=[
            "altair.app.ticketing.pgw.models",
            "altair.app.ticketing.core.models",
            "altair.app.ticketing.orders.models",
            "altair.app.ticketing.users.models",
        ])
        from altair.multicheckout.models import _session
        _session.remove()
        _session.configure(bind=self.session.bind)
        self.config = testing.setUp()

    def tearDown(self):
        from altair.multicheckout.api import remove_default_session
        remove_default_session()
        _teardown_db()
        testing.tearDown()

    def _getTarget(self):
        from .cancelauth import Canceller
        return Canceller

    def _makeOne(self, now=None):
        return self._getTarget()(testing.DummyRequest(), now=now)

    def test_run_cancel_auth(self):
        target = self._makeOne()
        result = target.get_cancel_auth_pgw_order_statuses()
        self.assertEqual(result, [])

    @mock.patch('altair.app.ticketing.pgw.scripts.cancelauth.Canceller.get_cancel_auth_pgw_order_statuses')
    @mock.patch('altair.app.ticketing.pgw.api.cancel_or_refund')
    def test_run_cancel_auth(self, mock_cancel_or_refund, mock_pgw_order_statuses):
        from altair.app.ticketing.pgw import models as m
        mock_pgw_order_statuses.return_value = [
            m.PGWOrderStatus(payment_id="RTXXXXXXXX")
        ]
        mock_cancel_or_refund.return_value = True
        target = self._makeOne()
        result = target.run()
        self.assertEqual(result, True)
