# -*- coding:utf-8 -*-

import unittest
from pyramid import testing



class PageCloneTests(unittest.TestCase):
    def setUp(self):
        from altaircms.testing import setup_db
        from pyramid.testing import setUp
        setup_db(["altaircms.page.models", "altaircms.event.models", "altaircms.plugins.widget.summary.models"])
        settings = {"altaircms.plugin_static_directory": "/tmp"}
        self.config = setUp(settings=settings)

    def tearDown(self):
        import transaction
        from altaircms.testing import teardown_db
        from pyramid.testing import tearDown
        tearDown()
        transaction.abort()
        teardown_db()

    def _callFUT(self, *args, **kwargs):
        from altaircms.page.clone import page_clone
        return page_clone(*args, **kwargs)

    def _makeRequest(self):
        return testing.DummyRequest()

    def _makePage(self, title, url):
        from altaircms.page.models import Page
        return Page(title=title, url=url)

    def test_clone_with_simple_version(self):
        request = self._makeRequest()
        page = self._makePage(title=u'元ページ', url='http://example.com/original')
        result = self._callFUT(request, page)

        self.assertEqual(result.title, u'元ページ(コピー)')
        self.assertEqual(result.url, "http://example.com/original")

    def test_clone_with_widget(self):
        import json
        from altaircms.models import DBSession
        from altaircms.plugins.widget.summary.models import SummaryWidget
        import transaction

        self.config.add_directive("add_widgetname", self.config.maybe_dotted("altaircms.plugins.helpers.add_widgetname"))
        self.config.include("altaircms.plugins.widget.summary")

        request = self._makeRequest()

        page = self._makePage(title=u'元ページ', url='http://example.com/original')
        page.id = 2
        widget0 = SummaryWidget(id=1, page=page)
        page.structure = json.dumps({"top": [{"name": "summary", "pk": 1}]})

        DBSession.add(page)
        transaction.commit()
        page = DBSession.merge(page)
        widget0 = DBSession.merge(widget0)

        result = self._callFUT(request, page, session=DBSession)

        DBSession.add(result)
        transaction.commit()
        result = DBSession.merge(result)
        page = DBSession.merge(page)

        ## 新しいpageはidを持って生成され２つは別物
        self.assertIsNotNone(result.id)
        self.assertNotEqual(page.id, result.id)

        ## widget の合計は2
        widgets = SummaryWidget.query.all()
        self.assertEqual(len(widgets), 2)

        ## そのうちwidget(id=0)は実際に作ったもの
        widget00 = SummaryWidget.query.filter_by(id=1).one()
        self.assertEqual(widget00.page_id, page.id)

        ## もう一方はコピーによってできたもの
        widget11 = SummaryWidget.query.filter(SummaryWidget.id != 1).one()
        self.assertEqual(widget11.page_id, result.id)
