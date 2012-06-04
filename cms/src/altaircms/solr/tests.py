import unittest
from pyramid import testing
from .interfaces import IFulltextSearch
from zope.interface import implementer

## for testing
@implementer(IFulltextSearch)
class DummyFullTextSearch(object):
    @classmethod
    def create_from_request(cls, request):
        return cls()

    def query(self, *args, **kwargs):
        pass

    def register(self, *args, **kwargs):
        pass

class DirectiveTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def teardown(self):
        testing.tearDown()

    def _callFUT(self, request, *args, **kwargs):
        from .api import get_fulltext_search
        return get_fulltext_search(request, *args, **kwargs)
        
    def test_get_apiobject(self):
        from .directives import add_fulltext_search
        add_fulltext_search(self.config, DummyFullTextSearch)

        request = testing.DummyRequest(registry=self.config.registry)
        result = self._callFUT(request)

        self.assertTrue(isinstance(result, DummyFullTextSearch))
