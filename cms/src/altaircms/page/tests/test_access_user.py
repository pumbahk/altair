# -*- encoding:utf-8 -*-
import unittest
from datetime import datetime
import mock

"""
page.can_access(user=None, access_key=None)

* user is valid -> ok.
* access_key is valid -> ok.
"""

class PagePublishStatusTests(unittest.TestCase):
    def _createPage(self, *args, **kwargs):
        from altaircms.page.models import Page
        return Page(*args, **kwargs)

    def test_on_birth(self):
        page = self._createPage()

        self.assertFalse(page.published)
        self.assertFalse(page.can_access())

    def test_on_publish(self):
        page = self._createPage()

        page.publish()

        self.assertTrue(page.published)
        self.assertTrue(page.can_access())

    def test_on_unpublish(self):
        page = self._createPage()

        page.unpublish()

        self.assertFalse(page.published)
        self.assertTrue(page.can_access())


class PagePrivateAccessTests(unittest.TestCase):
    def _createPage(self, *args, **kwargs):
        from altaircms.page.models import Page
        return Page(*args, **kwargs)

    def test_on_birth(self):
        page = self._createPage()

        self.assertFalse(page.has_access_keys())
        self.assertEquals(len(page.access_keys), 0)


    def test_create_access_key(self):
        page = self._createPage()
        page.create_access_key(key="this-is-access-key")
        
        self.assertTrue(page.has_access_keys())
        self.assertEquals(len(page.access_keys), 1)


    def test_delete_access_key(self):
        page = self._createPage()
        key = page.create_access_key(key="this-is-access-key")
        
        page.delete_access_key(key) 

        self.assertFalse(page.has_access_keys())
        self.assertEquals(len(page.access_keys), 0)


    def test_on_publish(self):
        page = self._createPage()
        page.publish()
        key = page.create_access_key(key="this-is-access-key")

        self.assertTrue(page.can_access())
        self.assertTrue(page.can_access(key))
        

    def test_on_unpublish(self):
        page = self._createPage()
        page.unpublish()
        key = page.create_access_key(key="this-is-access-key")
        
        self.assertFalse(page.can_access())
        self.assertTrue(page.can_access(key))


    def test_on_unpublish_with_another_access_key(self):
        page = self._createPage()
        page.unpublish()
        key = page.create_access_key(key="this-is-access-key")

        another_page = self._createPage()
        another_key = another_page.create_access_key(key="this-is-another-access-key")

        self.assertFalse(page.can_access())
        self.assertFalse(page.can_access(another_key))

    def test_on_unpublish_access_key_before_expiredate(self):
        page = self._createPage()
        page.unpulish()
        key = page.create_access_key(key="this-is-access-key", expire=datetime(2012, 12, 1))

        with mock.patch("datetime.datetime") as m:
            m.now.return_value = datetime(2012, 8, 9)

            self.assertTrue(page.has_access_keys())
            self.assertTrue(page.has_valid_access_keys())
            self.assertTrue(page.can_access(key=key))

    def test_on_unpublish_access_key_after_expiredate(self):
        page = self._createPage()
        page.unpulish()
        key = page.create_access_key(key="this-is-access-key", expire=datetime(2012, 12, 1))

        with mock.patch("datetime.datetime") as m:
            m.now.return_value = datetime(2012, 12, 12)

            self.assertTrue(page.has_access_keys())
            self.assertFalse(page.has_valid_access_keys())
            self.assertFalse(page.can_access(key=key))
        

if __name__ == "__main__":
    unittest.main()
