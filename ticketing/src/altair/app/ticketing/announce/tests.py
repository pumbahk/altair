# -*- coding:utf-8 -*-

import unittest
from pyramid import testing

from altair.app.ticketing.announce.utils import MacroEngine

class TestIt(unittest.TestCase):
    def setUp(self):
        testing.setUp()

        self.engine = MacroEngine()

    def tearDown(self):
        testing.tearDown()

    def test_build(self):
        template = u"Hello {{world}}"
        data = { "world": "altair" }
        built = self.engine.build(template, data)
        self.assertEqual(built, "Hello altair")

    def test_build_html(self):
        """filtersが未指定であれば、HTMLタグは素通しする"""
        template = u"<b>Hello</b> {{world}}"
        data = {"world": "<i>altair</i>"}
        built = self.engine.build(template, data)
        self.assertEqual(built, "<b>Hello</b> <i>altair</i>")

    def test_build_with_html_filter(self):
        """html filterによりHTMLタグはエスケープされるが、マクロの箇所のみ"""
        template = u"<b>Hello</b> {{world}}"
        data = {"world": "<i>altair</i>"}
        built = self.engine.build(template, data, filters=["html"])
        self.assertEqual(built, "<b>Hello</b> &lt;i&gt;altair&lt;/i&gt;")

    def test_build_with_link_filter(self):
        """filterが適用されるのはマクロの箇所のみ"""
        template = u"http://altair.xx/ {{url}}"
        data = {"url": "https://www.google.com/?q=a&b=c#xxx"}
        built = self.engine.build(template, data, filters=["link"])
        self.assertEqual(built, u'http://altair.xx/ <a href="https://www.google.com/?q=a&amp;b=c#xxx">https://www.google.com/?q=a&amp;b=c#xxx</a>')

    # 以下、dataを使用しないテスト

    def test_fields(self):
        template = u"a {{b}} {{c.d.e}} {{f.unique()}} {{g.as(h)}}"
        fields = self.engine.fields(template)
        self.assertEqual(fields, [ u"b", u"c.d.e", u"f.unique()", u"g.as(h)" ])

    def test_label(self):
        label = self.engine.label(u"b")
        self.assertEqual(label, u"b")

    def test_label_nest(self):
        """要素参照がある場合、最後の要素を採用する"""
        label = self.engine.label(u"b.c")
        self.assertEqual(label, u"c")

    def test_label_func(self):
        """関数呼び出しは無視する"""
        label = self.engine.label(u"b.unique()")
        self.assertEqual(label, u"b")

    def test_label_nest_func(self):
        """関数呼び出しは無視する"""
        label = self.engine.label(u"b.c.unique()")
        self.assertEqual(label, u"c")

    def test_label_func_nest(self):
        """要素参照は関数呼び出しの後でもよい"""
        label = self.engine.label(u"b.element(0).c")
        self.assertEqual(label, u"c")

