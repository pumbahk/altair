import unittest

from pyramid import testing
from pyramid.events import BeforeRender

from altaircms.subscribers import add_renderer_globals


def _initTestingDB():
    from sqlalchemy import create_engine
    from altaircms.models import initialize_sql
    session = initialize_sql(create_engine('sqlite:///:memory:'))
    return session


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.session = _initTestingDB()


class TestBaseView(BaseTest):
    def tearDown(self):
        testing.tearDown()

    def test_it(self):
        from altaircms.base.views import dashboard

        request = testing.DummyRequest()
        resp = dashboard(request)
        self.assertEqual(resp, {})
