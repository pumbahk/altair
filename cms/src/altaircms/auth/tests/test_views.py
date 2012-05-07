import unittest

from pyramid import testing
from altaircms.testing import DummyRequest


def setup_module():
    import sqlahelper
    from sqlalchemy import create_engine
    engine = create_engine("sqlite:///")
    sqlahelper.add_engine(engine)
    from .. import models
    #sqlahelper.get_base().metadata.create_all()
    models.Base.metadata.create_all()

def teardown_module():
    import sqlahelper
    sqlahelper.get_base().metadata.drop_all()

class RoleViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()
        import transaction
        transaction.abort()

    def _getTarget(self):
        from .. import views
        return views.RoleView

    def _makeOne(self, request):
        return self._getTarget()(request)

    def test_it(self):
        request = testing.DummyRequest()
        target = self._makeOne(request)                
        self.assertEqual(target.request, request)

    def add_role(self, role_name, permissions):
        from .. import models
        role = models.Role(name=role_name, permissions=permissions)
        import sqlahelper
        sqlahelper.get_session().add(role)
        sqlahelper.get_session().flush()
        return role

    def test_get_role(self):
        role = self.add_role('test-role', ['page_update'])
        request = testing.DummyRequest(matchdict=dict(id=role.id))
        target = self._makeOne(request)                
        result = target.get_role()
        self.assertEqual(result, role)

    def test_list(self):
        role = self.add_role('test-role', ['page_update'])
        request = testing.DummyRequest()
        target = self._makeOne(request)                
        result = target.list()
        self.assertEqual(result['roles'], [role])

    def test_read(self):
        role = self.add_role('test-role', ['page_update'])
        request = testing.DummyRequest(matchdict=dict(id=role.id))
        target = self._makeOne(request)                
        result = target.read()
        self.assertEqual(result['role'], role)
        from ..forms import RoleForm
        self.assertTrue(isinstance(result['form'], RoleForm))

    def test_read_not_found(self):
        from pyramid.httpexceptions import HTTPNotFound
        request = testing.DummyRequest(matchdict=dict(id="99999999999999"))
        target = self._makeOne(request)                
        try:
            result = target.read()
            self.fail()
        except HTTPNotFound:
            pass

    def test_update(self):
        self.config.add_route('role', '/roles/{id}')
        role = self.add_role('test-role', ['page_update'])
        request = DummyRequest(matchdict=dict(id=role.id),
                params={"permission": "page_delete"})
        target = self._makeOne(request)                
        result = target.update()
        self.assertEqual(result.location, '/roles/' + str(role.id))
        self.assertEqual(role.permissions, ['page_update', 'page_delete'])

    def test_update_invalid(self):
        self.config.add_route('role', '/roles/{id}')
        role = self.add_role('test-role', ['page_update'])
        request = DummyRequest(matchdict=dict(id=role.id),
                params={})
        target = self._makeOne(request)                
        result = target.update()
        self.assertEqual(result['role'], role)

    def test_delete(self):
        self.config.add_route('role_list', '/roles')
        role = self.add_role('test-role', ['page_update'])
        request = DummyRequest(matchdict=dict(id=role.id),
                params={})
        target = self._makeOne(request)                
        result = target.delete()
        self.assertEqual(result.location, '/roles')

        from .. import models
        self.assertEqual(len( models.Role.query.filter_by(id=role.id).all()), 0)
