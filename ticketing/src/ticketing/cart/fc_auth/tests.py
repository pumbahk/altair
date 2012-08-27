import unittest
from pyramid import testing
from ticketing.testing import _setup_db, _teardown_db
from .testing import add_credential

class FCAuthPluginTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session = _setup_db(modules=[
                'ticketing.core.models',
                #'ticketing.tickets.models',
                'ticketing.operators.models',
                #'ticketing.users.models',
                ])

    @classmethod
    def tearDownClass(cls):
        _teardown_db()

    def tearDown(self):
        _teardown_db()

    def _getTarget(self):
        from .plugins import FCAuthPlugin
        return FCAuthPlugin

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)


    def _makeEnv(self, *kwargs):
        environ = {}
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
        user = add_credential(membership, membergroup, username, password)
        self.session.add(user)
        return user

    def test_authenticate(self):
        membership = "fc"
        membergroup = "fc_platinum"
        username = "test_user"
        password = "secret"
        self._addCredential(membership, membergroup, username, password)

        identity = {
            "membership": membership,
            "username": username,
            "password": password,
            }
        environ = self._makeEnv()


        target = self._makeOne('')
        result = target.authenticate(environ, identity)

        self.assertTrue(result)

class TestIt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session = _setup_db(modules=[
                'ticketing.core.models',
                #'ticketing.tickets.models',
                'ticketing.operators.models',
                #'ticketing.users.models',
                ])

    @classmethod
    def tearDownClass(cls):
        _teardown_db()

    def tearDown(self):
        _teardown_db()

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
        environ = {}
        from wsgiref.util import setup_testing_defaults
        setup_testing_defaults(environ)
        environ.update(kwargs)
        return environ

    def _addCredential(self, membership, membergroup, username, password):
        user = add_credential(membership, membergroup, username, password)
        self.session.add(user)
        return user

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
            "membership": membership,
            "username": username,
            "password": password,
            }

        authenticated, headers = api.login(creds)

        import pickle
        self.assertEqual(pickle.loads(authenticated['repoze.who.userid'].decode('base64')), 
            {'username': 'test_user', 'membership': 'fc', 'membergroup': 'fc_plutinum', "is_guest": False})

    def test_challenge_none(self):
        login_url = 'http://example.com/login'
        factory = self._makeAPIFactory(login_url=login_url)
        environ = self._makeEnv()
        api = factory(environ)
        environ['repoze.who.plugins'] = api.name_registry

        result = api.challenge()
        self.assertIsNone(result)

    def test_challenge_redirect(self):
        login_url = 'http://example.com/login'
        factory = self._makeAPIFactory()
        environ = self._makeEnv()
        environ['ticketing.cart.fc_auth.required'] = True
        api = factory(environ)
        environ['repoze.who.plugins'] = api.name_registry
        environ['ticketing.cart.fc_auth.login_url'] = login_url
        session = DummySession()
        environ['session.rakuten_openid'] = session

        result = api.challenge()

        self.assertEqual(result.location, login_url)
        self.assertEqual(session['return_url'], 'http://127.0.0.1/')


class guest_authenticateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session = _setup_db(modules=[
                'ticketing.core.models',
                #'ticketing.tickets.models',
                'ticketing.operators.models',
                #'ticketing.users.models',
                ])

    @classmethod
    def tearDownClass(cls):
        _teardown_db()

    def tearDown(self):
        _teardown_db()

    def _callFUT(self, *args, **kwargs):
        from .plugins import guest_authenticate
        return guest_authenticate(*args, **kwargs)

    def test_empty(self):
        environ = {
        }
        identity = {
        }
        result = self._callFUT(environ, identity)

        self.assertIsNone(result)

    def test_no_geust_membergroup(self):
        environ = {
        }
        identity = {
            "membership": 'testing',
        }
        result = self._callFUT(environ, identity)

        self.assertIsNone(result)

    def _create_guest(self, name):
        import ticketing.users.models as u_m

        membership = u_m.Membership(name=name)
        guest = u_m.MemberGroup(membership=membership, is_guest=True, name=name+"_guest")
        self.session.add(membership)
        self.session.flush()
        return guest

    def test_it(self):
        environ = {
        }
        identity = {
            "membership": 'testing',
        }

        self._create_guest(identity['membership'])
        result = self._callFUT(environ, identity)

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
        membership_name = 'testing'

        request = testing.DummyRequest(matchdict={'membership': 'testing'})
        request.environ['session.rakuten_openid'] = {'return_url': '/return/to/url'}
        request.environ['repoze.who.api'] = DummyWhoApi(None)

        target = self._makeOne(request)

        result = target.guest_login()

        self.assertIn('message', result)

    def test_guest_login(self):
        membership_name = 'testing'

        request = testing.DummyRequest(matchdict={'membership': 'testing'})
        request.environ['session.rakuten_openid'] = {'return_url': '/return/to/url'}
        request.environ['repoze.who.api'] = DummyWhoApi(
            {'membership': 'testing', 'is_guest': True},
            [('X-TESTING', 'TESTING')])


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

class DummySession(dict):
    def save(self):
        pass
