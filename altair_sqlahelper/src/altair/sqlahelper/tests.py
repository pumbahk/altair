import unittest
from pyramid import testing
from .testing import DummyMaker

class from_settingsTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from . import from_settings
        return from_settings(*args, **kwargs)

    def test_empty(self):
        settings = {}
        result = self._callFUT(settings)

        self.assertEqual(result, {})

    def test_url_only(self):
        settings = {
            'altair.sqlahelper.sessions.testing.url': 'sqlite:///'
        }
        result = self._callFUT(settings)

        self.assertEqual(result, {'testing': {'url': 'sqlite:///'}})

    def test_with_echo(self):
        settings = {
            'altair.sqlahelper.sessions.testing.url': 'sqlite:///',
            'altair.sqlahelper.sessions.testing.echo': 'true',
        }
        result = self._callFUT(settings)

        self.assertEqual(result, {'testing': {'url': 'sqlite:///', 'echo': True}})


    def test_with_many(self):
        settings = {
            'altair.sqlahelper.sessions.testing.url': 'sqlite:///',
            'altair.sqlahelper.sessions.testing.echo': 'true',
            'altair.sqlahelper.sessions.testing2.url': 'sqlite:///:memory:',
        }
        result = self._callFUT(settings)

        self.assertEqual(result, {'testing': {'url': 'sqlite:///', 'echo': True},
                                  'testing2': {'url': 'sqlite:///:memory:'}})

class register_sessionmakersTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from . import register_sessionmakers
        return register_sessionmakers(*args, **kwargs)

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()


    def test_empty(self):
        from .interfaces import ISessionMaker
        urls = {}
        self._callFUT(self.config, urls)
        registered = self.config.registry.getAllUtilitiesRegisteredFor(ISessionMaker)

        self.assertEqual(registered, [])

    def test_one(self):
        from .interfaces import ISessionMaker
        urls = {'testing': {'url': 'sqlite:///'}}
        self._callFUT(self.config, urls)
        sessionmaker = self.config.registry.queryUtility(ISessionMaker, name='testing')
        self.assertEqual(str(sessionmaker().bind.url), 'sqlite:///')


class get_db_sessionTests(unittest.TestCase):
    
    def _callFUT(self, *args, **kwargs):
        from . import get_db_session
        return get_db_session(*args, **kwargs)

    def test_cached(self):
        request = testing.DummyRequest()
        marker = testing.DummyResource()
        request.environ['altair.sqlahelper.sessions'] = {'testing': marker}
        result = self._callFUT(request, 'testing')

        self.assertEqual(result, marker)


    def test_new_session(self):
        from .interfaces import ISessionMaker
        request = testing.DummyRequest()
        marker = testing.DummyResource()
        sessionmaker = DummyMaker(marker)
        request.registry.registerUtility(sessionmaker, ISessionMaker, name='testing')
        result = self._callFUT(request, 'testing')

        self.assertEqual(result, marker)
        self.assertEqual(request.environ['altair.sqlahelper.sessions'], {'testing': marker})
