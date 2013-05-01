import unittest
from datetime import datetime
import time

class RefreshCacheFireTests(unittest.TestCase):
    def _getTarget(self):
        from altairsite.front.api import FrontPageRenderer
        class DummyContext(FrontPageRenderer):
            result = []
            called = False
            def refresh_template_cache(self, *args, **kwargs):
                self.result.append((self, args, kwargs))
                self.called = True
        return DummyContext

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_template_is_none__not_fire(self):
        target = self._makeOne(None)
        target.refresh_template_if_need(None, None)
        self.assertFalse(target.called)

    def test_template_is_not_uploaded__not_fire(self):
        target = self._makeOne(None)
        class layout:
            uploaded_at = None
        target.refresh_template_if_need(None, layout)
        self.assertFalse(target.called)

    def test_fresh_template__not_fire(self):        
        target = self._makeOne(None)
        class layout:
            uploaded_at = datetime(2000, 1, 1)
        class template:
            cache = {}
            last_modified = time.mktime(datetime(2000, 1, 2).timetuple())
        target.refresh_template_if_need(template, layout)
        self.assertFalse(target.called)

    def test_it(self):        
        target = self._makeOne(None)
        class layout:
            uploaded_at = datetime(2000, 1, 3)
        class template:
            cache = {}
            last_modified = time.mktime(datetime(2000, 1, 2).timetuple())
        target.refresh_template_if_need(template, layout)
        self.assertTrue(target.called)

if __name__  == "__main__":
    unittest.main()
