# coding: utf-8
import transaction

from pyramid import testing
from webob.multidict import MultiDict

from altaircms.lib.testutils import BaseTest
from altaircms.topcontent.views import TopcontentRESTAPIView

class TestTopcontentView(BaseTest):
    def setUp(self):
        self.request = testing.DummyRequest()
        self.request.method = "PUT"
        super(TestTopcontentView, self).setUp()

    def tearDown(self):
        transaction.commit()

    def test_create_invalid(self):
        # null post
        self.request.POST = MultiDict([])

        resp = TopcontentRESTAPIView(self.request).create()
        self.assertEqual(resp.status_int, 400)

    def test_create_valid(self):
        self._fill_request_post()
        resp = TopcontentRESTAPIView(self.request).create()
        self.assertEqual(resp.status_int, 201)
        self.assertEqual(resp.message, None)

    def test_read(self):
        self._insert_topcontent()

        # list object
        resp = TopcontentRESTAPIView(self.request).read()
        self.assertTrue("topcontents" in dict(resp.items()))

        # # read object: slack-off
        resp = TopcontentRESTAPIView(self.request, '1').read()
        D = dict(resp.items())
        self.assertTrue("title" in D)
        self.assertTrue("kind" in D)
        self.assertTrue("text" in D)

    def test_delete(self):
        self._insert_topcontent()

        resp = TopcontentRESTAPIView(self.request, '1').delete()
        self.assertEqual(resp.status_int, 200)

        resp = TopcontentRESTAPIView(self.request, '999').delete()
        self.assertEqual(resp.status_int, 400)

    def _insert_topcontent(self):
        self._fill_request_post()
        TopcontentRESTAPIView(self.request).create()

    def _fill_request_post(self):
        self.request.POST = MultiDict([
                (u'page', u'__None'),
                (u'kind', u"注目のページ"),
                (u'countdown_type', u"page_open"),
                (u'orderno', u'50'),
                (u'page', u'__None'),
                (u'publish_open_on', u'2011-01-1 18:00:00'),
                (u'publish_close_on', u'2012-1-1 19:00:00'), 
                (u'text', u'topcontent content'),
                (u'title', u'topcontenttitle')
                ])

if __name__ == "__main__":
    import unittest
    unittest.main()
