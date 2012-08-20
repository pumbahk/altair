import unittest

from pyramid import testing

class auth_model_callbackTests(unittest.TestCase):

    def _callFUT(self, *args, **kwargs):
        from .security import auth_model_callback
        return auth_model_callback(*args, **kwargs)


    def test_non_dict(self):
        user = ""
        request = testing.DummyRequest()

        result = self._callFUT(user, request)

        self.assertEqual(result, [])

    def test_membership(self):
        user = {'membership': 'test-membership'}
        request = testing.DummyRequest()

        result = self._callFUT(user, request)

        self.assertEqual(result, ['membership:test-membership'])

    def test_membergroup(self):
        user = {'membergroup': 'test-membergroup'}
        request = testing.DummyRequest()

        result = self._callFUT(user, request)

        self.assertEqual(result, ['membergroup:test-membergroup'])
        
    def test_clamed_id(self):
        user = {'clamed_id': 'http://example.com'}
        request = testing.DummyRequest()

        result = self._callFUT(user, request)

        self.assertEqual(result, ['rakuten_auth'])
