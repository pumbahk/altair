import unittest
from pyramid import testing
from .testing import DummyHandler, setUpDB, tearDownDB


class QueryCountTweenTests(unittest.TestCase):
    def setUp(self):
        self.request = testing.DummyRequest()
        self.config = testing.setUp(request=self.request)
        self.db_session = setUpDB()

    def tearDown(self):
        testing.tearDown()
        tearDownDB()


    def _getTarget(self):
        from . import QueryCountTween
        return QueryCountTween

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)


    def test_it(self):
        marker = object()
        handler = DummyHandler(marker, 99)
        target = self._makeOne(handler, self.config.registry)
        request = self.request

        result = target(request)

        self.assertEqual(result, marker)

        self.assertEqual(len(request.environ['altair.queryprofile.testing.results']), 99)
        #self.assertEqual(request.environ['altair.queryprofile.query_count'], 99)
