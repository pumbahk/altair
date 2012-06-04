# -*- coding:utf-8 -*-

import unittest
from pyramid import testing
from .. import testing as page_testing


class PageCloneTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from .. import clone
        return clone.page_clone(*args, **kwargs)

    def test_it(self):
        from .. import models as m
        request = testing.DummyRequest()

        page = m.Page(title=u'元ページ', url='http://example.com/original')

        result = self._callFUT(request, page)


        self.assertEqual(result.title, u'元ページ(コピー)')
        self.assertIsNone(result.url)