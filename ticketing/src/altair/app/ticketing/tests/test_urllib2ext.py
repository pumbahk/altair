import unittest
import mock
from pyramid import testing

class SensibleRequestTest(unittest.TestCase):
    def _getTarget(self):
        from ..urllib2ext import SensibleRequest
        return SensibleRequest

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_without_userinfo(self):
        target = self._makeOne('http://localhost/')
        self.assertEqual(target.get_host(), 'localhost')
        self.assertEqual(target.get_userinfo(), None)

        target = self._makeOne('http://127.0.0.1/')
        self.assertEqual(target.get_host(), '127.0.0.1')
        self.assertEqual(target.get_userinfo(), None)

        target = self._makeOne('http://[::1]/')
        self.assertEqual(target.get_host(), '[::1]')
        self.assertEqual(target.get_userinfo(), None)

        target = self._makeOne('http://localhost:12345/')
        self.assertEqual(target.get_host(), 'localhost:12345')
        self.assertEqual(target.get_userinfo(), None)

        target = self._makeOne('http://127.0.0.1:12345/')
        self.assertEqual(target.get_host(), '127.0.0.1:12345')
        self.assertEqual(target.get_userinfo(), None)

        target = self._makeOne('http://[::1]:12345/')
        self.assertEqual(target.get_host(), '[::1]:12345')
        self.assertEqual(target.get_userinfo(), None)

    def test_without_userinfo(self):
        target = self._makeOne('http://user@localhost/')
        self.assertEqual(target.get_host(), 'localhost')
        self.assertEqual(target.get_userinfo(), ('user', None))

        target = self._makeOne('http://user@127.0.0.1/')
        self.assertEqual(target.get_host(), '127.0.0.1')
        self.assertEqual(target.get_userinfo(), ('user', None))

        target = self._makeOne('http://user@[::1]/')
        self.assertEqual(target.get_host(), '[::1]')
        self.assertEqual(target.get_userinfo(), ('user', None))

        target = self._makeOne('http://user@localhost:12345/')
        self.assertEqual(target.get_host(), 'localhost:12345')
        self.assertEqual(target.get_userinfo(), ('user', None))

        target = self._makeOne('http://user@127.0.0.1:12345/')
        self.assertEqual(target.get_host(), '127.0.0.1:12345')
        self.assertEqual(target.get_userinfo(), ('user', None))

        target = self._makeOne('http://user@[::1]:12345/')
        self.assertEqual(target.get_host(), '[::1]:12345')
        self.assertEqual(target.get_userinfo(), ('user', None))

        target = self._makeOne('http://user:pwd@localhost/')
        self.assertEqual(target.get_host(), 'localhost')
        self.assertEqual(target.get_userinfo(), ('user', 'pwd'))

        target = self._makeOne('http://user:pwd@127.0.0.1/')
        self.assertEqual(target.get_host(), '127.0.0.1')
        self.assertEqual(target.get_userinfo(), ('user', 'pwd'))

        target = self._makeOne('http://user:pwd@[::1]/')
        self.assertEqual(target.get_host(), '[::1]')
        self.assertEqual(target.get_userinfo(), ('user', 'pwd'))

        target = self._makeOne('http://user:pwd@localhost:12345/')
        self.assertEqual(target.get_host(), 'localhost:12345')
        self.assertEqual(target.get_userinfo(), ('user', 'pwd'))

        target = self._makeOne('http://user:pwd@127.0.0.1:12345/')
        self.assertEqual(target.get_host(), '127.0.0.1:12345')
        self.assertEqual(target.get_userinfo(), ('user', 'pwd'))

        target = self._makeOne('http://user:pwd@[::1]:12345/')
        self.assertEqual(target.get_host(), '[::1]:12345')
        self.assertEqual(target.get_userinfo(), ('user', 'pwd'))

class OpenerFactoryFromConfigTest(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from ..urllib2ext import opener_factory_from_config 
        return opener_factory_from_config(*args, **kwargs)

    def test_default(self):
        config = testing.setUp(settings={
            'a.b.c': ''
            })
        default_opener_factory = mock.Mock()
        factory = self._callFUT(config, 'a.b.c', default_opener_factory)
        factory()
        default_opener_factory.assert_called_once_with()
        config = testing.setUp(settings={
            })
        default_opener_factory = mock.Mock()
        factory = self._callFUT(config, 'a.b.c', default_opener_factory)
        factory()
        default_opener_factory.assert_called_once_with()

    @staticmethod
    def dummy_factory(*args, **kwargs):
        return (args, kwargs)

    def test_with_args(self):
        config = testing.setUp(settings={
            'a.b.c': '%s.%s.dummy_factory' % (__name__, self.__class__.__name__),
            'a.b.c.x': '1',
            'a.b.c.y': '2',
            'a.b.c.z': '3',
            })
        default_opener_factory = mock.Mock()
        factory = self._callFUT(config, 'a.b.c', default_opener_factory)
        self.assertEqual(factory(), ((), { 'x': '1', 'y': '2', 'z': '3' }))
        self.assertFalse(default_opener_factory.called)

