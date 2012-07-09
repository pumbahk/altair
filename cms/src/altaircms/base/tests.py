import unittest
from pyramid import testing
from altaircms.testing import DummyRequest
from altaircms.lib.testutils import BaseTest
from altaircms.auth.models import Operator
class TestBaseView(BaseTest):
    def tearDown(self):
        testing.tearDown()

    def test_it(self):
        from .views import dashboard
        request = DummyRequest(user=Operator())
        resp = dashboard(request)

        self.assertEquals(resp.keys(), ["events"])
        self.assertEquals(list(resp["events"]), [])

