import unittest
from pyramid import testing

def setup_module():
    import sqlahelper
    from sqlalchemy import create_engine
    engine = create_engine("sqlite:///")
    engine.echo = True
    sqlahelper.add_engine(engine)
    
    from ..auth import models
    sqlahelper.get_base().metadata.create_all()

def teardown_module():
    import sqlahelper
    sqlahelper.get_base().metadata.drop_all()

class RootFactoryTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()
        import transaction
        transaction.abort()

    def _getTarget(self):
        from .. import security
        return security.RootFactory

    def _makeOne(self, request):
        return self._getTarget()(request)

    def test_acl_default(self):

        from pyramid.security import Allow, Authenticated
        request = testing.DummyRequest()

        target = self._makeOne(request)
        result = target.__acl__

        self.assertEqual(result, [(Allow, Authenticated, 'authenticated')])

    def _add_role(self, role_name, permissions):
        from ..auth import models
        role = models.Role(name=role_name, permissions=permissions)
        import sqlahelper
        sqlahelper.get_session().add(role)
        return role

    def test_acl_one_role(self):

        from pyramid.security import Allow, Authenticated
        self._add_role('test-role', ['page_update'])
        request = testing.DummyRequest()

        target = self._makeOne(request)
        result = target.__acl__

        self.assertEqual(result, 
            [(Allow, Authenticated, 'authenticated'),
            ('Allow', 'test-role', 'page_update')])
