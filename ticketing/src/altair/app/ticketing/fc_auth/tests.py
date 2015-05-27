import unittest
import mock
from pyramid import testing
from altair.auth import REQUEST_KEY
from altair.auth.testing import DummySession
from altair.app.ticketing.testing import _setup_db, _teardown_db, DummyRequest
from altair.sqlahelper import register_sessionmaker_with_engine
from .testing import add_credential

class FCAuthPluginTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.session = _setup_db(modules=[
                'altair.app.ticketing.core.models',
                'altair.app.ticketing.operators.models',
                'altair.app.ticketing.users.models',
                'altair.app.ticketing.orders.models',
                ])
        register_sessionmaker_with_engine(
            self.config.registry,
            'slave',
            self.session.bind
            )

    def tearDown(self):
        _teardown_db()
        testing.tearDown()

    def _getTarget(self):
        from .plugins import FCAuthPlugin
        return FCAuthPlugin

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)


    def test_provided(self):
        from altair.auth.interfaces import ISessionKeeper, IChallenger, IAuthenticator
        from zope.interface.verify import verifyObject

        target = self._makeOne()
        verifyObject(IChallenger, target)
        verifyObject(IAuthenticator, target)

    def test_authenticate_invalid(self):
        membership = "fc"
        username = "test_user"
        password = "secret"

        target = self._makeOne()

        auth_factors = {
            target.name: {
                membership: membership,
                username: username,
                password: password,
                },
            }

        request = DummyRequest()
        dummy_session_keeper = mock.Mock()
        result = target.authenticate(request, mock.Mock(session_keepers=[dummy_session_keeper]), auth_factors)

        self.assertEqual(result, (None, None))

    def _addCredential(self, membership, membergroup, username, password):
        user_credential = add_credential(membership, membergroup, username, password)
        self.session.add(user_credential)
        self.session.flush()
        return user_credential

    def test_authenticate(self):
        membership = "fc"
        membergroup = "fc_platinum"
        username = "test_user"
        password = "secret"
        self._addCredential(membership, membergroup, username, password)

        target = self._makeOne()
        auth_factors = {
            target.name: {
                "membership": membership,
                "username": username,
                "login": True,
                }
            }
        request = DummyRequest()
        dummy_session_keeper = mock.Mock()
        result = target.authenticate(request, mock.Mock(session_keepers=[dummy_session_keeper]), auth_factors)

        self.assertTrue(result)

class TestIt(unittest.TestCase):
    def setUp(self):
        self.request = DummyRequest(matched_route=testing.DummyModel(name='dummy'), params={'event_id': 58})
        self.config = testing.setUp(request=self.request)
        self.config.include('altair.app.ticketing.cart.request')
        self.config.add_route('dummy', '/dummy')
        self.session = _setup_db(modules=[
                'altair.app.ticketing.core.models',
                #'altair.app.ticketing.tickets.models',
                'altair.app.ticketing.operators.models',
                #'altair.app.ticketing.users.models',
                ])
        register_sessionmaker_with_engine(
            self.config.registry,
            'slave',
            self.session.bind
            )
        from altair.auth.interfaces import ISessionKeeper
        from zope.interface import directlyProvides
        dummy_session_keeper = mock.Mock()
        directlyProvides(dummy_session_keeper, ISessionKeeper)
        self.dummy_session_keeper = dummy_session_keeper

    def tearDown(self):
        _teardown_db()
        testing.tearDown()

    def _makeAuthAPI(self, *args, **kwargs):
        from altair.auth.api import AuthAPI
        from altair.auth import PluginRegistry
        from .plugins import FCAuthPlugin

        pr = PluginRegistry(None)
        pr.register(self.dummy_session_keeper)
        pr.register(FCAuthPlugin())
        return AuthAPI(pr.lookup_by_interface)


    def _addCredential(self, membership, membergroup, username, password, organization_short_name="testing"):
        user_credential = add_credential(membership, membergroup, username, password, organization_short_name)
        self.session.add(user_credential)
        self.session.flush()
        return user_credential

    def test_it(self):
        api = self._makeAuthAPI()

        membership = u"fc"
        membergroup = u"fc_plutinum"
        username = "test_user"
        password = "secret"
        self._addCredential(membership, membergroup, username, password)
        creds = {
            "login": True,
            "membership": membership,
            "username": username,
            }

        request = DummyRequest()
        identifiers, auth_factors, metadata = api.login(request, request.response, creds)

        self.assertEqual(
            identifiers,
            {
                'fc_auth': {
                    'username': username,
                    'membership': membership,
                    'membergroup': membergroup,
                    "is_guest": False
                    }
                }
            )

    def test_challenge_not_required(self):
        login_url = 'http://example.com/login'
        api = self._makeAuthAPI()
        request = self.request
        request.organization = testing.DummyModel(id=None)

        result = api.challenge(request, request.response)
        self.assertFalse(result)


        
    def test_challenge_redirect(self):
        from . import SESSION_KEY
        from mock import Mock
        from datetime import datetime
        from zope.interface import directlyProvides
        from altair.app.ticketing.cart.interfaces import ICartResource

        self.config.add_route('fc_auth.login', '/membership/{membership}/login')
        self.dummy_session_keeper.get_auth_factors.return_value = None

        membership = "fc"
        membergroup = "fc_plutinum"
        username = "test_user"
        password = "secret"
        self._addCredential(membership, membergroup, username, password,
                            "fc")

        request = self.request
        membership = testing.DummyModel(name="fc")
        query = Mock()
        query.join.return_value = query
        query.with_entities.return_value = query
        query.first.return_value = membership
        request.context = testing.DummyResource(
            performance=testing.DummyModel(
                query_sales_segments=lambda *args, **kwargs: query
                ),
            memberships=[
                membership,
                ],
            now=datetime(2014, 1, 1, 0, 0, 0)
            )
        directlyProvides(request.context, ICartResource)
        request.session = DummySession()

        api = self._makeAuthAPI()
        result = api.challenge(request, request.response)
        self.assertTrue(result)
        self.assertEqual(request.response.location, 'http://example.com/membership/fc/login')
        self.assertEqual(request.session[SESSION_KEY]['return_url'], '/dummy?event_id=58')


class guest_authenticateTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.session = _setup_db(modules=[
                'altair.app.ticketing.core.models',
                'altair.app.ticketing.operators.models',
                'altair.app.ticketing.users.models',
                ])
        register_sessionmaker_with_engine(
            self.config.registry,
            'slave',
            self.session.bind
            )

    def tearDown(self):
        _teardown_db()
        testing.tearDown()

    def _callFUT(self, *args, **kwargs):
        from .plugins import guest_authenticate
        return guest_authenticate(*args, **kwargs)

    def test_empty(self):
        environ = { REQUEST_KEY: DummyRequest() }
        identity = {}
        result = self._callFUT(environ, identity)

        self.assertIsNone(result)

    def test_no_guest_membergroup(self):
        request = DummyRequest()
        identity = { "membership": 'testing' }
        result = self._callFUT(request, identity)

        self.assertIsNone(result)

    def _create_guest(self, name):
        import altair.app.ticketing.users.models as u_m

        membership = u_m.Membership(name=name)
        guest = u_m.MemberGroup(membership=membership, is_guest=True, name=name+"_guest")
        self.session.add(membership)
        self.session.flush()
        return guest

    def test_it(self):
        import pickle
        identity = { "membership": 'testing' }

        self._create_guest(identity['membership'])
        request = DummyRequest()
        result = self._callFUT(request, identity)
        self.assertEqual(result['membership'], 'testing')
        self.assertEqual(result['membergroup'], 'testing_guest')
        self.assertTrue(result['is_guest'])

class LoginViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        from pyramid.authorization import ACLAuthorizationPolicy
        from zope.interface import directlyProvides
        self.config.set_authorization_policy(ACLAuthorizationPolicy())
        self.config.include('altair.auth')
        get_auth_api_patch = mock.patch('altair.auth.api.get_auth_api')
        self.get_auth_api = get_auth_api_patch.start()
        self.get_auth_api_patch = get_auth_api_patch

    def tearDown(self):
        self.get_auth_api_patch.stop() 
        testing.tearDown()

    def _getTarget(self):
        from .views import LoginView
        return LoginView

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_guest_login_fail(self):
        from . import SESSION_KEY
        from repoze.who.interfaces import IAPIFactory

        self.get_auth_api.return_value.login.return_value = ({ 'username': 'username' }, {}, {})
        request = DummyRequest(matchdict={'membership': 'testing'}, environ={'wsgi.version':'0.0'})
        request.session[SESSION_KEY] = {'return_url': '/return/to/url'}
        context = request.context = testing.DummyResource(
            request=request,
            primary_membership=testing.DummyResource(name='XX')
            )

        target = self._makeOne(context, request)

        result = target.guest_login()
        self.assertEqual(result.location, "/return/to/url")

    def test_guest_login(self):
        from . import SESSION_KEY
        from repoze.who.interfaces import IAPIFactory
        from .resources import FCAuthResource

        self.get_auth_api.return_value.login.return_value = ({ 'username': 'username' }, {}, {})
        request = DummyRequest(matchdict={'membership': 'this will not be referred to'}, environ={'wsgi.version':'0.0'})
        request.session[SESSION_KEY] = {'return_url': '/return/to/url'}
        context = request.context = testing.DummyResource(
            request=request,
            primary_membership=testing.DummyResource(name='XX')
            )

        target = self._makeOne(context, request)

        result = target.guest_login()

        self.assertEqual(result.location, '/return/to/url')
        self.get_auth_api.return_value.login.assert_called_with(request, request.response, {'membership':'XX', 'is_guest':True}, auth_factor_provider_name='fc_auth')
