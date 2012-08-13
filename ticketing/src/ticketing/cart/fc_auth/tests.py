import unittest
from ticketing.testing import _setup_db, _teardown_db
from .testing import add_credential

class FCAuthPluginTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session = _setup_db(modules=[
                'ticketing.core.models',
                'ticketing.tickets.models',
                'ticketing.operators.models',
                'ticketing.users.models',
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

    def _addCredential(self, membership, username, password):
        user = add_credential(membership, username, password)
        self.session.add(user)
        return user

    def test_authenticate(self):
        membership = "fc"
        username = "test_user"
        password = "secret"
        self._addCredential(membership, username, password)

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
                'ticketing.tickets.models',
                'ticketing.operators.models',
                'ticketing.users.models',
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

        fc_auth = FCAuthPlugin(rememberer_name='auth_tkt',
            login_url=kwargs.get('login_url'))
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

    def _addCredential(self, membership, username, password):
        user = add_credential(membership, username, password)
        self.session.add(user)
        return user

    def test_it(self):
        factory = self._makeAPIFactory()
        environ = self._makeEnv()
        api = factory(environ)
        environ['repoze.who.plugins'] = api.name_registry

        membership = "fc"
        username = "test_user"
        password = "secret"
        self._addCredential(membership, username, password)
        creds = {
            "membership": membership,
            "username": username,
            "password": password,
            }

        authenticated, headers = api.login(creds)

        import pickle
        self.assertEqual(pickle.loads(authenticated['repoze.who.userid'].decode('base64')), {'username': 'test_user', 'membership': 'fc'})

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
        factory = self._makeAPIFactory(login_url=login_url)
        environ = self._makeEnv()
        environ['ticketing.cart.fc_auth.required'] = True
        api = factory(environ)
        environ['repoze.who.plugins'] = api.name_registry

        result = api.challenge()

        self.assertEqual(result.location, login_url)
