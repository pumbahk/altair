# coding: utf-8
import transaction

from pyramid import testing
from webob.multidict import MultiDict

from altaircms.base.tests import BaseTest
from altaircms.topic.views import TopicRESTAPIView

class TestTopicView(BaseTest):
    def setUp(self):
        self.request = testing.DummyRequest()
        self.request.method = "PUT"
        super(TestTopicView, self).setUp()

    def tearDown(self):
        transaction.commit()

    def test_create_invalid(self):
        # null post
        self.request.POST = MultiDict([])

        resp = TopicRESTAPIView(self.request).create()
        self.assertEqual(resp.status_int, 400)

    def test_create_valid(self):
        self._fill_request_post()
        resp = TopicRESTAPIView(self.request).create()
        self.assertEqual(resp.status_int, 201)
        self.assertEqual(resp.message, None)

    def test_read(self):
        self._insert_topic()

        # list object
        resp = TopicRESTAPIView(self.request).read()
        self.assertTrue("topics" in dict(resp.items()))

        # # read object: slack-off
        resp = TopicRESTAPIView(self.request, '1').read()
        D = dict(resp.items())
        self.assertTrue("title" in D)
        self.assertTrue("kind" in D)
        self.assertTrue("text" in D)

    def test_delete(self):
        self._insert_topic()

        resp = TopicRESTAPIView(self.request, '1').delete()
        self.assertEqual(resp.status_int, 200)

        resp = TopicRESTAPIView(self.request, '999').delete()
        self.assertEqual(resp.status_int, 400)

    def _insert_topic(self):
        self._fill_request_post()
        TopicRESTAPIView(self.request).create()

    def _fill_request_post(self):
        self.request.POST = MultiDict([
                (u'event', u'__None'),
                (u'is_global', u'y'),
                (u'kind', u"公演中止情報"),
                (u'orderno', u'50'),
                (u'page', u'__None'),
                (u'publish_open_on', u'2011-01-1 18:00:00'),
                (u'publish_close_on', u'2012-1-1 19:00:00'), 
                (u'text', u'topic content'),
                (u'title', u'topictitle')
                ])
# import warnings
# warnings.warn("this test is failed")

if __name__ == "__main__":
    import unittest
    unittest.main()
