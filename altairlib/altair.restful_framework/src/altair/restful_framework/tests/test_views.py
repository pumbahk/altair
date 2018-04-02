# -*- coding: utf-8 -*-

from pyramid import testing
from pyramid.response import Response
from unittest import TestCase

from altair.restful_framework.views import APIView

class TestAPIView(APIView):

    def get(self, request, *args, **kwargs):
        return Response({'method': 'GET'})

    def post(self, request, *args, **kwargs):
        return Response({'method': 'POST'})

class TestInitKwargsAPIView(APIView):

    def get(self, request, *args, **kwargs):
        return Response({'name': self.name})

class TestExceptionAPIView(APIView):

    def get(self, request, *args, **kwargs):
        raise Exception('test exception')

class APIViewTests(TestCase):

    def setUp(self):
        self.test_view = TestAPIView.as_view()
        self.request = testing.DummyRequest()

    def test_implemented_method_dispatch(self):
        resp = self.test_view(self.request)
        expected = {'method': 'GET'}
        assert resp.status_code == 200
        assert resp.body == expected

    def test_method_not_allowed(self):
        self.request.method = 'PUT'
        resp = self.test_view(self.request)
        assert resp.status_code == 405

    def test_initkwargs(self):
        view = TestInitKwargsAPIView.as_view(name='test_api_view')
        resp = view(self.request)
        print resp.body
        expected = {'name': 'test_api_view'}
        assert resp.body == expected

    def test_raise_exception(self):
        view = TestExceptionAPIView.as_view()
        self.assertRaises(Exception, view, self.request)

    def test_options_request(self):
        self.request.method = 'OPTIONS'
        resp = self.test_view(self.request)
        assert resp.headers.get('Allow') == "GET, POST, OPTIONS"