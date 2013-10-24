# -*- coding:utf-8 -*-
from pyramid import testing
import unittest

class DescriptionTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.include("altair.app.ticketing.description")

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *args, **kwargs):
        from .api import get_description
        return get_description(*args, **kwargs)

    def test_event(self):
        from altair.app.ticketing.core.models import Event

        request = testing.DummyRequest()
        event = Event(title=":Event:title")

        result = self._callFUT(request, event)
        print result

    
        
if __name__ == '__main__':
    unittest.main()
