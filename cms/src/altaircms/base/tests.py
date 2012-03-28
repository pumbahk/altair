import unittest

from pyramid import testing

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
        from .views import dashboard
        request = testing.DummyRequest()
        resp = dashboard(request)
        self.assertEqual(resp, {'events':[]})
