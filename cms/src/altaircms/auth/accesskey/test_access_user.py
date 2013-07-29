# -*- encoding:utf-8 -*-
import unittest
from datetime import datetime
from altaircms.testing import setup_db
from altaircms.testing import teardown_db

"""
page.can_access(user=None, access_key=None)

* access_key is valid -> ok.
"""

def setUpModule():
    setup_db(["altaircms.event.models", 
              "altaircms.page.models"])

def tearDownModule():
    teardown_db()

class PagePublishStatusTests(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    def _makeOne(self, *args, **kwargs):
        from altaircms.page.models import Page
        from altaircms.auth.accesskey.control import AccessKeyControl
        return AccessKeyControl(Page(*args, **kwargs))

    def test_on_birth(self):
        target = self._makeOne()

        self.assertFalse(target.published)

    def test_on_publish(self):
        target = self._makeOne()

        target.publish()

        self.assertTrue(target.published)

    def test_on_unpublish(self):
        target = self._makeOne()

        target.unpublish()

        self.assertFalse(target.published)


class PagePrivateAccessTests(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    def _makeOne(self, *args, **kwargs):
        from altaircms.page.models import Page
        from altaircms.auth.accesskey.control import AccessKeyControl
        return AccessKeyControl(Page(*args, **kwargs))

    def test_on_birth(self):
        target = self._makeOne()

        self.assertFalse(target.has_access_keys())
        self.assertEquals(len(target.access_keys), 0)


    def test_create_access_key(self):
        target = self._makeOne()
        target.create_access_key(key="this-is-access-key")
        
        self.assertTrue(target.has_access_keys())
        self.assertEquals(len(target.access_keys), 1)


    def test_delete_access_key(self):
        target = self._makeOne()
        key = target.create_access_key(key="this-is-access-key")
        
        target.delete_access_key(key) 

        self.assertFalse(target.has_access_keys())
        self.assertEquals(len(target.access_keys), 0)


    def test_access_with_key(self):
        target = self._makeOne()
        key = target.create_access_key(key="this-is-access-key")

        self.assertFalse(target.can_private_access())
        self.assertTrue(target.can_private_access(key))

    def test_with_another_access_key(self):
        target = self._makeOne()
        key = target.create_access_key(key="this-is-access-key")

        another_target = self._makeOne()
        another_key = another_target.create_access_key(key="this-is-another-access-key")

        self.assertFalse(target.can_private_access())
        self.assertFalse(target.can_private_access(another_key))

    def test_access_key_before_expiredate(self):
        target = self._makeOne()
        key = target.create_access_key(key="this-is-access-key", expire=datetime(2012, 12, 1))

        now = datetime(2012, 8, 9)

        self.assertTrue(target.has_access_keys())
        self.assertEquals(target.valid_access_keys(now), [key])
        self.assertTrue(target.can_private_access(key=key, now=now))

    def test_on_unpublish_access_key_after_expiredate(self):
        target = self._makeOne()
        key = target.create_access_key(key="this-is-access-key", expire=datetime(2012, 12, 1))

        now = datetime(2012, 12, 12)

        self.assertTrue(target.has_access_keys())
        self.assertEquals(target.valid_access_keys(now), [])
        self.assertFalse(target.can_private_access(key=key, now=now))


    ## 
    def test_can_private_access_via_string(self):
        target = self._makeOne()
        key = target.create_access_key(key="this-is-access-key")

        import sqlahelper
        session = sqlahelper.get_session()
        session.add(key)

        self.assertTrue(target.can_private_access(key=key.hashkey))
        self.assertFalse(target.can_private_access(key="this-is-not-access-key-so-this-is-invalid"))

if __name__ == "__main__":
    unittest.main()
