# coding: utf-8
from pyramid import testing
from webob.multidict import MultiDict

from altaircms.base.tests import BaseTest
from altaircms.event.views import EventRESTAPIView

class TestEventView(BaseTest):
    def setUp(self):
        self.request = testing.DummyRequest()
        self.request.method = "PUT"
        super(TestEventView, self).setUp()

    def test_create_invalid(self):
        # null post
        self.request.POST = MultiDict([])

        resp = EventRESTAPIView(self.request).create()
        self.assertEqual(resp.status_int, 400)

    def test_create_valid(self):
        self._fill_request_post()

        resp = EventRESTAPIView(self.request).create()
        self.assertEqual(resp.status_int, 201)
        self.assertEqual(resp.message, None)

    def test_read(self):
        self._insert_event()

        # list object
        resp = EventRESTAPIView(self.request).read()
        self.assertTrue(str(resp).startswith("{'events': ["))

        # read object
        resp = EventRESTAPIView(self.request, '1').read()
        self.assertTrue(str(resp).startswith("{'inquiry_for':"))

    def test_delete(self):
        self._insert_event()

        resp = EventRESTAPIView(self.request, '1').delete()
        self.assertEqual(resp.status_int, 200)

        resp = EventRESTAPIView(self.request, '999').delete()
        self.assertEqual(resp.status_int, 400)

    def _insert_event(self):
        self._fill_request_post()
        resp = EventRESTAPIView(self.request).create()

    def _fill_request_post(self):
        self.request.POST = MultiDict([
            (u'title', u'たいとる'),
            (u'subtitle', u'サブタイトル'),
            (u'description', u'説明'),
            (u'event_open', u'2011-1-1 00:00:00'),
            (u'event_close', u'2011-12-31 23:59:59'),
            (u'deal_open', u'2011-12-31 23:59:59'),
            (u'deal_close', u'2011-12-31 23:59:59'),
            (u'is_searchable', u'y'),
        ])
