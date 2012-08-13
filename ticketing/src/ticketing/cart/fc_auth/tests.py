import unittest
from ticketing.testing import _setup_db, _teardown_db

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

        target = self._makeOne()
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
        
        target = self._makeOne()
        result = target.authenticate(environ, identity)

        self.assertFalse(result)

    def _addCredential(self, membership, username, password):
        import ticketing.core.models
        from ticketing.users.models import Membership, User, UserCredential

        m = Membership(name=membership)
        u = User()
        uc = UserCredential(membership=m,
                            user=u,
                            auth_identifier=username,
                            auth_secret=password)

        self.session.add(u)
        return u

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


        target = self._makeOne()
        result = target.authenticate(environ, identity)

        self.assertTrue(result)
