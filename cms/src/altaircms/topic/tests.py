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
        self.assertTrue(str(resp).startswith("{'topics': ["))

        # read object
        resp = TopicRESTAPIView(self.request, '1').read()
        self.assertEquals(dict(resp.items()), 
                          {'publish_at': u'2012-01-01T10:10:10',
                           'title': u'たいとる',
                           "id": 1, 
                           "kind": u"その他", 
                           'text': u'内容'})


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
            (u'title', u'たいとる'),
            (u"kind", u"その他"), 
            (u'publish_at', u'2012-1-1 10:10:10'),
            (u'text', u'内容'),
        ])


if __name__ == "__main__":
    import unittest
    unittest.main()
