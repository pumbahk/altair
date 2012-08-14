import unittest
from pyramid import testing

class SelectAuthTweenTests(unittest.TestCase):


    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _getTarget(self):
        from .tweens import SelectAuthTween
        return SelectAuthTween

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_it_not_required(self):
        registry = self.config.registry
        handler = DummyHandler('Hello')
        target = self._makeOne(handler, registry)

        request = testing.DummyRequest()

        result = target(request)

        self.assertTrue(request.environ['ticketing.cart.rakuten_auth.required'])

    def test_it(self):
        registry = self.config.registry
        handler = DummyHandler('Hello')
        target = self._makeOne(handler, registry)

        request = testing.DummyRequest()

        request.context = testing.DummyResource(membership='fc')

        result = target(request)

        self.assertNotIn('ticketing.cart.rakuten_auth.required', request.environ)


class DummyHandler(object):
    def __init__(self, text):
        self.text = text
        self.called = []

    def __call__(self, request):
        self.called.append(request)
        return self.text
