from unittest import TestCase

class SensibleRequestTest(TestCase):
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

