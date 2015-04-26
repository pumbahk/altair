from __future__ import absolute_import

import os
import unittest
import mock
from pyramid.security import Everyone
from zope.interface import directlyProvides
from pyramid import testing

here = os.path.dirname(__file__)

def make_mock(_interfaces=(), *args, **kwargs):
    m = mock.Mock(*args, **kwargs)
    directlyProvides(m, *_interfaces)
    return m

class TestIt(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.testing_securitypolicy()
        self.config.include('altair.auth')
        decider = mock.Mock(return_value=True)
        self.config.set_who_api_decider(decider)
        from .interfaces import ISessionKeeper, ILoginHandler, IAuthenticator, IChallenger, IMetadataProvider
        self.session_keeper = make_mock(_interfaces=(ISessionKeeper,))
        self.session_keeper.name = 'dummy_session_keeper'
        self.others = make_mock(_interfaces=(ILoginHandler, IAuthenticator, IChallenger, IMetadataProvider))
        self.others.name = 'dummy_auth_plugin'
        self.config.add_auth_plugin(self.session_keeper)
        self.config.add_auth_plugin(self.others)
        self.config.commit()

    def tearDown(self):
        testing.tearDown()

    def test_get_plugin_registry(self):
        from .api import get_plugin_registry
        registry = get_plugin_registry(self.config.registry)
        self.assertIsNotNone(registry)
        self.assertEqual(registry.lookup('dummy_session_keeper'), self.session_keeper)
        self.assertEqual(registry.lookup('dummy_auth_plugin'), self.others)

    def test_auth_api(self):
        from .api import get_auth_api
        from .interfaces import IAuthAPI
        request = testing.DummyRequest()
        api = get_auth_api(request)
        self.assertTrue(IAuthAPI.providedBy(api))


class TestAuthAPI(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.testing_securitypolicy()
        self.config.include('altair.auth')
        decider = mock.Mock(return_value=True)
        self.config.set_who_api_decider(decider)
        from .interfaces import ISessionKeeper, ILoginHandler, IAuthenticator, IChallenger, IMetadataProvider
        self.session_keeper = make_mock(_interfaces=(ISessionKeeper,))
        self.session_keeper.name = 'dummy_session_keeper'
        self.others = make_mock(_interfaces=(ILoginHandler, IAuthenticator, IChallenger, IMetadataProvider))
        self.others.name = 'dummy_auth_plugin'
        self.config.add_auth_plugin(self.session_keeper)
        self.config.add_auth_plugin(self.others)
        self.config.commit()

    def tearDown(self):
        testing.tearDown()

    def test_login(self):
        from .api import get_auth_api
        request = testing.DummyRequest()
        api = get_auth_api(request)
        self.others.get_auth_factors.return_value = { 'username': 'AAA', 'authenticated': True }
        self.others.get_metadata.return_value = { 'META': 'META' }
        self.others.authenticate.return_value = ({ 'user_id': 0 }, { 'dummy_session_keeper': { 'username': 'AAA' } })
        identities, auth_factors, metadata = api.login(request, request.response, { 'username': 'AAA', 'password': 'BBB' })
        self.assertEqual(identities, { 'dummy_auth_plugin': { 'user_id': 0 } })
        self.assertEqual(auth_factors, { 'dummy_session_keeper': { 'username': 'AAA' } })
        self.assertEqual(metadata, { 'META': 'META' })
        self.others.authenticate.assert_called_with(request, api, { 'dummy_auth_plugin': { 'username': 'AAA', 'authenticated': True } } )
        self.session_keeper.remember.assert_called_with(request, api, request.response, { 'username': 'AAA' })

    def test_logout(self):
        from .api import get_auth_api
        request = testing.DummyRequest()
        api = get_auth_api(request)
        request.environ['altair.auth.auth_factors'] = { 'dummy_session_keeper': { 'username': 'AAA' } }
        api.logout(request, request.response)
        self.session_keeper.forget.assert_called_with(request, api, request.response, None)
        self.assertTrue('altair.auth.auth_factors' not in request.environ)

    def test_classifier(self):
        from .api import get_auth_api, get_request_classifier
        from .interfaces import IAuthenticator
        self.others.classifications = {
            IAuthenticator: ['B']
            }
        request = testing.DummyRequest()
        api = get_auth_api(request)
        self.others.get_auth_factors.return_value = { 'username': 'AAA', 'authenticated': True }
        self.others.get_metadata.return_value = { 'META': 'META' }
        self.others.authenticate.return_value = ({ 'user_id': 0 }, { 'dummy_session_keeper': { 'username': 'AAA' } })
        identities, auth_factors, metadata = api.login(request, request.response, { 'username': 'AAA', 'password': 'BBB' }, classification='A')
        self.assertEqual(identities, {})


class TestAuthenticationPolicy(unittest.TestCase):
    maxDiff = 100000
    def setUp(self):
        self.config = testing.setUp()
        self.config.include('altair.auth')

    def tearDown(self):
        testing.tearDown()

    def _getTarget(self):
        from .pyramid import AuthenticationPolicy
        return AuthenticationPolicy

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _makeRequest(self, *args, **kwargs):
        request = testing.DummyRequest(*args, **kwargs)
        return request

    def test_effective_principals(self):
        from .interfaces import ISessionKeeper, ILoginHandler, IAuthenticator, IChallenger, IMetadataProvider
        session_keeper = make_mock(_interfaces=(ISessionKeeper,))
        self.config.add_auth_plugin(session_keeper)
        for i in range(0, 3):
            plugin = make_mock(_interfaces=(IAuthenticator, IChallenger))
            plugin.name = 'dummy-%d' % i
            plugin.authenticate.return_value = ({}, {})
            self.config.add_auth_plugin(plugin)
        target = self._makeOne(self.config.registry)
        request = self._makeRequest()
        principals = target.effective_principals(request)
        self.assertEqual(sorted(principals), [
            'altair.auth.authenticator:dummy-0',
            'altair.auth.authenticator:dummy-0+dummy-1',
            'altair.auth.authenticator:dummy-0+dummy-1+dummy-2',
            'altair.auth.authenticator:dummy-0+dummy-2',
            'altair.auth.authenticator:dummy-1',
            'altair.auth.authenticator:dummy-1+dummy-2',
            'altair.auth.authenticator:dummy-2',
            Everyone,
            ])
