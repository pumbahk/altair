import unittest
from pyramid import testing

def setUpModule():
    from altaircms.testing import setup_db
    setup_db(["altaircms.auth.models", 
              "altaircms.event.models", 
              "altaircms.page.models"])

def tearDownModule():
    from altaircms.testing import teardown_db
    teardown_db()
    


class RootFactoryTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.include("altair.sqlahelper")
        import sqlahelper
        self.session = sqlahelper.get_session()

    def _makeRequest(self):
        class request:
            registry = self.config.registry
            environ = {"altair.sqlahelper.sessions": {"slave": self.session}}  #for altair.sqlahelper.
        return request

    def tearDown(self):
        testing.tearDown()
        import transaction
        transaction.abort()

    def _getTarget(self):
        from altaircms import security
        return security.RootFactory

    def _makeOne(self, request):
        return self._getTarget()(request)

    def test_acl_default(self):

        from pyramid.security import Allow, Authenticated
        request = self._makeRequest()

        target = self._makeOne(request)
        result = target.__acl__

        self.assertEqual(list(result), [(Allow, Authenticated, 'authenticated')])

    def _add_role(self, role_name, permissions):
        from altaircms.auth import models
        role = models.Role(name=role_name, permissions=permissions)
        self.session.add(role)
        return role

    def test_acl_one_role(self):
        from pyramid.security import Allow, Authenticated
        self._add_role('test-role', ['page_update'])
        request = self._makeRequest()

        target = self._makeOne(request)
        result = target.__acl__

        self.assertEqual(list(result), 
            [(Allow, Authenticated, 'authenticated'),
            ('Allow', 'test-role', 'page_update')])

