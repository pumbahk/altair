# -*- coding:utf-8 -*-
import unittest

from pyramid import testing
from altaircms.testing import DummyRequest
from altaircms.testing import setup_db, teardown_db

def setUpModule():
    setup_db(["altaircms.page.models", 
              "altaircms.event.models", 
              "altaircms.layout.models", 
              "altaircms.widget.models", 
              "altaircms.auth.models"])

def tearDownModule():
    teardown_db()

def dummy_request(*args, **kwargs):
    request = testing.DummyRequest(*args, **kwargs)
    from types import MethodType
    def allowable(self, model, qs=None):
        return model.query
    request.allowable = MethodType(allowable, request, request.__class__)
    return request

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
        request = dummy_request()
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
        request = dummy_request(matchdict=dict(id=role.id))
        target = self._makeOne(request)                
        result = target.get_role()
        self.assertEqual(result, role)

    def test_list(self):
        role = self.add_role('test-role', ['page_update'])
        request = dummy_request()
        target = self._makeOne(request)                
        result = target.list()
        self.assertEqual(result['roles'], [role])

    def test_read(self):
        role = self.add_role('test-role', ['page_update'])
        request = dummy_request(matchdict=dict(id=role.id))
        target = self._makeOne(request)                
        result = target.read()
        self.assertEqual(result['role'], role)
        from ..forms import RoleForm
        self.assertTrue(isinstance(result['form'], RoleForm))

    def test_read_not_found(self):
        from pyramid.httpexceptions import HTTPNotFound
        request = dummy_request(matchdict=dict(id="99999999999999"))
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

class RolePermissionViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()
        import transaction
        transaction.abort()

    def _getTarget(self):
        from .. import views
        return views.RolePermissionView

    def _makeOne(self, request):
        return self._getTarget()(request)

    def test_it(self):
        request = dummy_request()
        target = self._makeOne(request)

        self.assertEqual(target.request, request)

    def _add_role(self, name, permissions):
        from .. import models
        role = models.Role(name=name, permissions=permissions)
        import sqlahelper
        sqlahelper.get_session().add(role)
        sqlahelper.get_session().flush()
        return role

    def test_delete(self):
        self.config.add_route('role', '/roles/{id}')
        role = self._add_role('test-role', permissions=['page_update'])
        matchdict = {'id': 'page_update', 'role_id': str(role.id)}
        request = dummy_request(matchdict=matchdict)

        target = self._makeOne(request)
        result = target.delete()

        self.assertEqual(result.location, '/roles/' + str(role.id))
        self.assertNotIn('page_update', role.permissions)


class OperatorViewTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()
        import transaction
        transaction.abort()

    def _getTarget(self):
        from .. import views
        return views.OperatorView

    def _makeOne(self, request):
        return self._getTarget()(request)


    def test_it(self):
        request = dummy_request()
        target = self._makeOne(request)

        self.assertEqual(target.request, request)

    def _add_operator(self, name, auth_source='test', user_id=1):
        from .. import models
        operator = models.Operator(auth_source=auth_source, user_id=user_id, screen_name=name) 
        import sqlahelper
        sqlahelper.get_session().add(operator)
        sqlahelper.get_session().flush()
        
        return operator

    def test_list(self):
        operator = self._add_operator(u'test-operator')
        request = dummy_request()
        target = self._makeOne(request)

        result = target.list()

        self.assertEqual(result['operators'], [operator])
        
    def test_read(self):
        operator = self._add_operator(u'test-operator')
        request = dummy_request(matchdict=dict(id=str(operator.id)))
        target = self._makeOne(request)

        result = target.read()

        self.assertEqual(result['operator'], operator)

    def test_delete(self):
        self.config.add_route('operator_list', '/operators')
        operator = self._add_operator(u'test-operator')
        request = dummy_request(matchdict=dict(id=str(operator.id)))
        target = self._makeOne(request)

        result = target.delete()
        print result
        self.assertEqual(result.location, '/operators')

class OAuthLoginTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.add_subscriber("altaircms.auth.subscribers.touch_operator_after_login",
                                   "altaircms.auth.subscribers.AfterLogin")

    def tearDown(self):
        import transaction
        transaction.abort()
        testing.tearDown()

    def _getTarget(self):
        from .. import views
        return views.OAuthLogin

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _add_role(self, name):
        import sqlahelper
        from .. import models as m
        role = m.Role(name=name)
        sqlahelper.get_session().add(role)
        return role

    def _get_opeartor(self, user_id):
        from .. import models as m
        import sqlahelper
        session = sqlahelper.get_session()
        return session.query(m.Operator).filter(m.Operator.user_id==user_id).first()

    def _add_operator(self, user_id):
        from .. import models as m
        import sqlahelper
        session = sqlahelper.get_session()
        operator = m.Operator(user_id=user_id, auth_source='oauth')
        session.add(operator)
        return operator

    def test_oauth_callback_without_operator(self):
        import json
        from ..api import OAuthComponent
        from ..interfaces import IOAuthComponent

        self.config.add_route('dashboard', '/')
        self._add_role(u'administrator')
        self._add_role(u'staff')

        request = dummy_request(GET={'code': 'code'})
        oauth_compnent = OAuthComponent(
            'client-id',
            'secret-key',
            'authorized-url',
            'http://example.com/access-token')
        request.registry.registerUtility(oauth_compnent, IOAuthComponent)

        res_data = json.dumps({
            'user_id': '99999999',
            'organization_id': '10101010', 
            'organization_name': 'this-is-organization', 
            "organization_short_name": "org", 
            'roles': [
                'administrator',
                'staff',
            ],
            'screen_name': u'管理者',
            'access_token': 'this-is-token',
        })
        target = self._makeOne(request)
        target._urllib2 = DummyURLLib2(res_data)

        result = target.oauth_callback()

        self.assertTrue(target._urllib2.called)
        self.assertEqual(
            target._urllib2.called[0],
            'http://example.com/access-token?client_secret=secret-key&code=code&client_id=client-id&grant_type=authorization_code')
        self.assertEqual(result.location, 'http://example.com/')

        # operator data
        operator = self._get_opeartor('99999999')
        self.assertIsNotNone(operator)
        self.assertEqual(operator.auth_source, 'oauth')
        self.assertEqual(operator.screen_name, u'管理者')
        self.assertEqual(operator.oauth_token, 'this-is-token')
        self.assertEqual(len(operator.roles), 2)
        self.assertEqual(operator.roles[0].name, 'administrator')
        self.assertEqual(operator.roles[1].name, 'staff')

        self.assertEqual(operator.organization.name, "this-is-organization")


    def test_oauth_callback_with_operator(self):
        import json
        from ..api import OAuthComponent
        from ..interfaces import IOAuthComponent

        self.config.add_route('dashboard', '/')
        self._add_role(u'administrator')
        self._add_role(u'staff')

        request = dummy_request(GET={'code': 'code'})
        oauth_compnent = OAuthComponent(
            'client-id',
            'secret-key',
            'authorized-url',
            'http://example.com/access-token')
        request.registry.registerUtility(oauth_compnent, IOAuthComponent)

        res_data = json.dumps({
            'user_id': '888888888',
            'organization_id': '10101010', 
            "organization_short_name": "org", 
            'organization_name': 'this-is-organization', 
            'roles': [
                'administrator',
                'staff'
            ],
            'screen_name': u'管理者',
            'access_token': 'this-is-token',
            })

        operator = self._add_operator('888888888')
        target = self._makeOne(request)
        target._urllib2 = DummyURLLib2(res_data)

        result = target.oauth_callback()

        self.assertTrue(target._urllib2.called)
        self.assertEqual(target._urllib2.called[0], 'http://example.com/access-token?client_secret=secret-key&code=code&client_id=client-id&grant_type=authorization_code')
        self.assertEqual(result.location, 'http://example.com/')

        # operator data
        self.assertIsNotNone(operator)
        self.assertEqual(operator.auth_source, 'oauth')
        self.assertEqual(operator.screen_name, u'管理者')
        self.assertEqual(operator.organization.short_name, 'org')
        self.assertEqual(operator.oauth_token, 'this-is-token')
        self.assertEqual(len(operator.roles), 2)
        self.assertEqual(operator.roles[0].name, 'administrator')
        self.assertEqual(operator.roles[1].name, 'staff')

        self.assertEqual(operator.organization.name, "this-is-organization")
        self.assertIsNotNone(operator.last_login)


class DummyURLLib2(object):
    def __init__(self, response_data):
        self.response_data = response_data
        self.called = []

    def urlopen(self, url):
        self.called.append(url)
        from io import BytesIO
        return BytesIO(self.response_data)


