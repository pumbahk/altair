import unittest
from pyramid import testing
from altair.auth import REQUEST_KEY
from altair.auth.testing import DummySession
from altair.app.ticketing.testing import _setup_db, _teardown_db
from altair.sqlahelper import register_sessionmaker_with_engine
from .testing import add_credential

class FCAuthPluginTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
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

    def tearDown(self):
        _teardown_db()
        testing.tearDown()

    def _getTarget(self):
        from .plugins import FCAuthPlugin
        return FCAuthPlugin

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)


    def _makeEnv(self, *kwargs):
        environ = { REQUEST_KEY: testing.DummyRequest() }
        from wsgiref.util import setup_testing_defaults
        setup_testing_defaults(environ)
        environ.update(kwargs)
        return environ

    def test_provided(self):
        from repoze.who.interfaces import IIdentifier, IChallenger, IAuthenticator
        from zope.interface.verify import verifyObject

        target = self._makeOne('')
        verifyObject(IIdentifier, target)
        verifyObject(IChallenger, target)
        verifyObject(IAuthenticator, target)

    def test_authenticate_invalid(self):
        membership = "fc"
        username = "test_user"
        password = "secret"

        identity = {
            membership: membership,
            username: username,
            password: password,
            }
        environ = self._makeEnv()
        
        target = self._makeOne('')
        result = target.authenticate(environ, identity)

        self.assertFalse(result)

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

        identity = {
            "membership": membership,
            "username": username,
            "login": True,
            }
        environ = self._makeEnv()


        target = self._makeOne('')
        result = target.authenticate(environ, identity)

        self.assertTrue(result)

class TestIt(unittest.TestCase):
    def setUp(self):
        self.request = testing.DummyRequest()
        self.config = testing.setUp(request=self.request)
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

    def tearDown(self):
        _teardown_db()
        testing.tearDown()

    def _makeAPIFactory(self, *args, **kwargs):
        
        from repoze.who.api import APIFactory
        from repoze.who.plugins.auth_tkt import AuthTktCookiePlugin
        from .plugins import FCAuthPlugin, logger

        fc_auth = FCAuthPlugin(rememberer_name='auth_tkt')
        auth_tkt = AuthTktCookiePlugin('secret', 'auth_tkt')
        identifiers = [('fc_auth', fc_auth), 
                       ('auth_tkt', auth_tkt),]
        authenticators = [('fc_auth', fc_auth), 
                          ('auth_tkt', auth_tkt),
                          ]
        challengers = [('fc_auth', fc_auth), 
                       ]
        mdproviders = [('fc_auth', fc_auth), ]

        factory = APIFactory(
            identifiers=identifiers,
            authenticators=authenticators,
            challengers=challengers,
            mdproviders=mdproviders,
            request_classifier=None,
            challenge_decider=None,
            remote_user_key = 'REMOTE_USER',
            logger=logger,
            )
        return factory

    def _makeEnv(self, *kwargs):
        environ = { REQUEST_KEY: self.request }
        from wsgiref.util import setup_testing_defaults
        setup_testing_defaults(environ)
        environ.update(kwargs)
        return environ

    def _addCredential(self, membership, membergroup, username, password, organization_short_name="testing"):
        user_credential = add_credential(membership, membergroup, username, password, organization_short_name)
        self.session.add(user_credential)
        self.session.flush()
        return user_credential

    def test_it(self):
        factory = self._makeAPIFactory()
        environ = self._makeEnv()
        api = factory(environ)
        environ['repoze.who.plugins'] = api.name_registry

        membership = "fc"
        membergroup = "fc_plutinum"
        username = "test_user"
        password = "secret"
        self._addCredential(membership, membergroup, username, password)
        creds = {
            "login": True,
            "membership": membership,
            "username": username,
            }

        authenticated, headers = api.login(creds)

        import pickle
        self.assertEqual(
            pickle.loads(authenticated['repoze.who.userid'].decode('base64')), 
            {'username': 'test_user', 'membership': 'fc', 'membergroup': 'fc_plutinum', "is_guest": False})

    def test_challenge_not_required(self):
        login_url = 'http://example.com/login'
        factory = self._makeAPIFactory(login_url=login_url)
        environ = self._makeEnv()
        api = factory(environ)
        environ['repoze.who.plugins'] = api.name_registry
        from pyramid.threadlocal import get_current_request
        request = get_current_request()
        request.organization = testing.DummyModel(id=None)
        environ[REQUEST_KEY] = request

        result = api.challenge()
        self.assertIsNone(result)


        
    def test_challenge_redirect(self):
        from . import SESSION_KEY

        self.config.add_route('fc_auth.login', '/membership/{membership}/login')

        membership = "fc"
        membergroup = "fc_plutinum"
        username = "test_user"
        password = "secret"
        self._addCredential(membership, membergroup, username, password,
                            "fc")

        from pyramid.threadlocal import get_current_request
        request = get_current_request()
        request.context = testing.DummyResource()
        request.context.memberships = [testing.DummyModel()]
        request.session = DummySession()

        factory = self._makeAPIFactory()
        environ = self._makeEnv()
        environ[REQUEST_KEY] = request
        api = factory(environ)
        environ['repoze.who.plugins'] = api.name_registry
        session = request.session
        environ['session.rakuten_openid'] = session

        result = api.challenge()

        self.assertEqual(result.location, 'http://example.com/membership/fc/login')
        self.assertEqual(session[SESSION_KEY]['return_url'], 'http://127.0.0.1/')


class guest_authenticateTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
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

    def tearDown(self):
        _teardown_db()
        testing.tearDown()

    def _callFUT(self, *args, **kwargs):
        from .plugins import guest_authenticate
        return guest_authenticate(*args, **kwargs)

    def test_empty(self):
        environ = { REQUEST_KEY: testing.DummyRequest() }
        identity = {}
        userdata = {}
        result = self._callFUT(environ, identity, userdata)

        self.assertIsNone(result)

    def test_no_geust_membergroup(self):
        environ = { REQUEST_KEY: testing.DummyRequest() }
        identity = {}
        userdata = { "membership": 'testing' }
        result = self._callFUT(environ, identity, userdata)

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
        environ = { REQUEST_KEY: testing.DummyRequest() }
        identity = {}
        userdata = { "membership": 'testing' }

        self._create_guest(userdata['membership'])
        result = self._callFUT(environ, identity, userdata)
        self.assertEqual(result['membership'], 'testing')
        self.assertEqual(result['membergroup'], 'testing_guest')
        self.assertTrue(result['is_guest'])

class LoginViewTests(unittest.TestCase):
    
    def _getTarget(self):
        from .views import LoginView
        return LoginView

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_guest_login_fail(self):
        from . import SESSION_KEY
        from repoze.who.interfaces import IAPIFactory

        request = testing.DummyRequest(matchdict={'membership': 'testing'})
        request.session[SESSION_KEY] = {'return_url': '/return/to/url'}
        request.registry.registerUtility(DummyWhoApi, IAPIFactory, name="fc_auth")

        target = self._makeOne(request)

        result = target.guest_login()
        self.assertEqual(result.location, "/return/to/url")

    def test_guest_login(self):
        from . import SESSION_KEY
        from repoze.who.interfaces import IAPIFactory

        request = testing.DummyRequest(matchdict={'membership': 'testing'})
        request.session[SESSION_KEY] = {'return_url': '/return/to/url'}
        request.registry.registerUtility(lambda env: DummyWhoApi(
            {'membership': 'testing', 'is_guest': True},
            [('X-TESTING', 'TESTING')]),
                                         IAPIFactory, name="fc_auth")

        target = self._makeOne(request)

        result = target.guest_login()

        self.assertEqual(result.location, '/return/to/url')
        self.assertEqual(result.headers['X-TESTING'], 'TESTING')

class DummyWhoApi(object):
    def __init__(self, authenticated, headers=[]):
        self.authenticated = authenticated
        self.headers = headers


    def login(self, identity):
        return self.authenticated, self.headers
