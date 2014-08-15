import os
import unittest
import mock
from pyramid import testing

here = os.path.dirname(__file__)

class TestIt(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def assertHasAttr(self, obj, attr_name):
        assert hasattr(obj, attr_name), u"{0} does not have {1}".format(obj, attr_name)

    def test_it(self):
        from altair.auth import (
            who_api,
            who_api_factory,
            decide,
            list_who_api_factory,
        )
        from altair.auth.testing import make_augmented_who_api_factory_with_dummy
        self.config.registry.settings.update({'altair.auth.decider': 'altair.auth.testing:DummyDecider'})
        self.config.testing_securitypolicy()
        self.config.include('altair.auth')
        self.assertHasAttr(self.config, 'add_who_api_factory')
        who1_factory = make_augmented_who_api_factory_with_dummy()
        who2_factory = make_augmented_who_api_factory_with_dummy()
        self.config.add_who_api_factory('who1', who1_factory)
        self.config.add_who_api_factory('who2', who2_factory)
        request = testing.DummyRequest(environ={'wsgi.version': '1.0'})
        factory = who_api_factory(request, 'who1')
        self.assertEqual(factory, who1_factory)
        factory = who_api_factory(request, 'who2')
        self.assertEqual(factory, who2_factory)
        request.testing_who_api_name = 'who1'
        api_name = decide(request)
        self.assertEqual(api_name, 'who1')
        api, api_name = who_api(request)
        self.assertEqual(api_name, 'who1')
        self.assertEqual(api.factory, who1_factory)

        factories = list_who_api_factory(request)

        self.assertEqual(factories, 
                         [(u'who1', who1_factory),
                          (u'who2', who2_factory)])

class TestMultiWhoAuthenticationPolicy(unittest.TestCase):
    def setUp(self):
        from altair.auth.testing import make_augmented_who_api_factory_with_dummy
        self.config = testing.setUp()
        self.config.registry.settings.update({
            'altair.auth.decider': 'altair.auth.testing:DummyDecider',
            'altair.auth.identifier': 'altair.auth.testing:DummyPlugin',
            })
        self.config.testing_securitypolicy()
        self.config.include('altair.auth')
        who1_factory = make_augmented_who_api_factory_with_dummy()
        who2_factory = make_augmented_who_api_factory_with_dummy()
        self.config.add_who_api_factory('who1', who1_factory)
        self.config.add_who_api_factory('who2', who2_factory)

    def tearDown(self):
        testing.tearDown()

    def _getTarget(self):
        from . import MultiWhoAuthenticationPolicy
        return MultiWhoAuthenticationPolicy

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _makeRequest(self, *args, **kwargs):
        from . import REQUEST_KEY
        request = testing.DummyRequest(*args, **kwargs)
        request.environ[REQUEST_KEY] = request
        return request

    def test_authenticated_userid_with_callback_returning_empty_list(self):
        callback = mock.Mock()
        callback.return_value = []
        target = self._makeOne(self.config.registry, callback)
        request = self._makeRequest(environ={'wsgi.version': '1.0'})
        request.testing_who_api_name = 'nonexistent'
        result = target.authenticated_userid(request)
        self.assertEqual(result, None)

        callback = mock.Mock()
        callback.return_value = []
        target = self._makeOne(self.config.registry, callback)
        request = self._makeRequest(environ={'wsgi.version': '1.0'})
        request.testing_who_api_name = 'who2'
        identity = {'a':'b'}
        request.environ['return_value_for_identify'] = identity
        request.environ['return_value_for_authenticate'] = '***'
        result = target.authenticated_userid(request)
        self.assertEqual(callback.call_args[0][0]['a'], 'b')
        self.assertEqual(callback.call_args[0][0]['repoze.who.userid'], '***')
        self.assertEqual(callback.call_args[0][1], request)
        self.assertEqual(result, '***')

    def test_authenticated_userid_with_callback_returning_nonempty_list(self):
        callback = mock.Mock()
        callback.return_value = ['group']
        target = self._makeOne(self.config.registry, callback)
        request = self._makeRequest(environ={'wsgi.version': '1.0'})
        request.testing_who_api_name = 'nonexistent'
        result = target.authenticated_userid(request)
        self.assertEqual(result, None)

        callback = mock.Mock()
        callback.return_value = ['group']
        target = self._makeOne(self.config.registry, callback)
        request = self._makeRequest(environ={'wsgi.version': '1.0'})
        request.testing_who_api_name = 'who2'
        identity = {'a':'b'}
        request.environ['return_value_for_identify'] = identity
        request.environ['return_value_for_authenticate'] = '***'
        result = target.authenticated_userid(request)
        self.assertEqual(result, '***')

    def test_unauthenticated_userid(self):
        callback = mock.Mock()
        target = self._makeOne(self.config.registry, callback)
        request = self._makeRequest(environ={'wsgi.version': '1.0'})
        request.testing_who_api_name = 'nonexistent'
        result = target.unauthenticated_userid(request)
        self.assertEqual(result, None)

        request = self._makeRequest(environ={'wsgi.version': '1.0'})
        request.testing_who_api_name = 'who2'
        identity = {'a':'b'}
        request.environ['return_value_for_identify'] = identity
        request.environ['return_value_for_authenticate'] = '***'
        result = target.unauthenticated_userid(request)
        self.assertEqual(result, '***')

    def test_effective_principals_with_callback_returning_empty_list(self):
        from pyramid.security import Everyone, Authenticated
        callback = mock.Mock()
        callback.return_value = []
        target = self._makeOne(self.config.registry, callback)
        request = self._makeRequest(environ={'wsgi.version': '1.0'})
        request.testing_who_api_name = 'nonexistent'
        result = target.effective_principals(request)
        self.assertEqual(result, [Everyone])

        callback = mock.Mock()
        callback.return_value = []
        target = self._makeOne(self.config.registry, callback)
        request = self._makeRequest(environ={'wsgi.version': '1.0'})
        request.testing_who_api_name = 'who2'
        identity = {'a':'b'}
        request.environ['return_value_for_identify'] = identity
        request.environ['return_value_for_authenticate'] = '***'
        result = target.effective_principals(request)
        self.assertEqual(callback.call_args[0][0]['a'], 'b')
        self.assertEqual(callback.call_args[0][0]['repoze.who.userid'], '***')
        self.assertEqual(callback.call_args[0][1], request)
        self.assertEqual(set(result), {'***', Authenticated, Everyone})

    def test_effective_principals_with_callback_returning_nonempty_list(self):
        from pyramid.security import Everyone, Authenticated
        callback = mock.Mock()
        callback.return_value = ['group']
        target = self._makeOne(self.config.registry, callback)
        request = self._makeRequest(environ={'wsgi.version': '1.0'})
        request.testing_who_api_name = 'nonexistent'
        result = target.effective_principals(request)
        self.assertEqual(result, [Everyone])

        callback = mock.Mock()
        callback.return_value = ['group']
        target = self._makeOne(self.config.registry, callback)
        request = self._makeRequest(environ={'wsgi.version': '1.0'})
        request.testing_who_api_name = 'who2'
        identity = {'a':'b'}
        request.environ['return_value_for_identify'] = identity
        request.environ['return_value_for_authenticate'] = '***'
        result = target.effective_principals(request)
        self.assertEqual(set(result), {'***', 'group', Authenticated, Everyone})

    def test_remember_with_callback_returning_empty_list(self):
        from pyramid.security import Everyone, Authenticated
        callback = mock.Mock()
        callback.return_value = []
        target = self._makeOne(self.config.registry, callback)
        request = self._makeRequest(environ={'wsgi.version': '1.0'})
        request.testing_who_api_name = 'nonexistent'
        result = target.remember(request, None)
        self.assertEqual(result, [])

        callback = mock.Mock()
        callback.return_value = []
        target = self._makeOne(self.config.registry, callback)
        request = self._makeRequest(environ={'wsgi.version': '1.0'})
        request.testing_who_api_name = 'who2'
        request.environ['return_value_for_remember'] = ['***']
        result = target.remember(request, None)
        self.assertEqual(result, ['***'])

    def test_remember_with_callback_returning_nonempty_list(self):
        from pyramid.security import Everyone, Authenticated
        callback = mock.Mock()
        callback.return_value = ['group']
        target = self._makeOne(self.config.registry, callback)
        request = self._makeRequest(environ={'wsgi.version': '1.0'})
        request.testing_who_api_name = 'nonexistent'
        result = target.remember(request, None)
        self.assertEqual(result, [])

        callback = mock.Mock()
        callback.return_value = ['group']
        target = self._makeOne(self.config.registry, callback)
        request = self._makeRequest(environ={'wsgi.version': '1.0'})
        request.testing_who_api_name = 'who2'
        request.environ['return_value_for_remember'] = ['***']
        result = target.remember(request, None)
        self.assertEqual(result, ['***'])

    def test_forget_with_callback_returning_empty_list(self):
        from pyramid.security import Everyone, Authenticated
        callback = mock.Mock()
        callback.return_value = []
        target = self._makeOne(self.config.registry, callback)
        request = self._makeRequest(environ={'wsgi.version': '1.0'})
        request.testing_who_api_name = 'nonexistent'
        result = target.forget(request)
        self.assertEqual(result, [])

        callback = mock.Mock()
        callback.return_value = []
        target = self._makeOne(self.config.registry, callback)
        request = self._makeRequest(environ={'wsgi.version': '1.0'})
        request.testing_who_api_name = 'who2'
        identity = {'a':'b'}
        request.environ['return_value_for_identify'] = identity
        request.environ['return_value_for_authenticate'] = '***'
        request.environ['return_value_for_forget'] = ['***']
        result = target.forget(request)
        self.assertEqual(result, ['***'])

    def test_forget_with_callback_returning_nonempty_list(self):
        from pyramid.security import Everyone, Authenticated
        callback = mock.Mock()
        callback.return_value = ['group']
        target = self._makeOne(self.config.registry, callback)
        request = self._makeRequest(environ={'wsgi.version': '1.0'})
        request.testing_who_api_name = 'nonexistent'
        result = target.forget(request)
        self.assertEqual(result, [])

        callback = mock.Mock()
        callback.return_value = ['group']
        target = self._makeOne(self.config.registry, callback)
        request = self._makeRequest(environ={'wsgi.version': '1.0'})
        request.testing_who_api_name = 'who2'
        identity = {'a':'b'}
        request.environ['return_value_for_identify'] = identity
        request.environ['return_value_for_authenticate'] = '***'
        request.environ['return_value_for_forget'] = ['***']
        result = target.forget(request)
        self.assertEqual(result, ['***'])



