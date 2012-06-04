import unittest
from pyramid import testing
from altaircms.lib.testutils import BaseTest

class TestBaseView(BaseTest):
    def tearDown(self):
        testing.tearDown()

    def test_it(self):
        from .views import dashboard
        request = testing.DummyRequest()
        resp = dashboard(request)

        self.assertEquals(resp.keys(), ["events"])
        self.assertEquals(list(resp["events"]), [])

