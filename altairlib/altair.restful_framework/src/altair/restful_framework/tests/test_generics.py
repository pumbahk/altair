# -*- coding: utf-8 -*-

from marshmallow import Schema, fields
from mock import Mock
from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.query import Query
from unittest import TestCase

from altair.restful_framework import generics

engine = create_engine('sqlite://')
Base = declarative_base()

def get_dbsession():
    Session = sessionmaker()
    Session.configure(bind=engine)
    return Session()

class Request(Base):
    __tablename__ = 'request'

    id = Column(Integer, primary_key=True)
    name = Column(String)


class RequestSerializer(Schema):
    id = fields.Integer()
    name = fields.String()

class RequestAPIView(generics.GenericAPIView):
    model = Request
    serializer_class = RequestSerializer
    pagination_class = Mock()

    def get_dbsession(self):
        return get_dbsession()

class RequestOverrideAPIView(generics.GenericAPIView):
    model = Request
    lookup_column = (Request, id)

    def get_dbsession(self):
        return get_dbsession()

    def get_query(self):
        if not self.dbsession:
            self.dbsession = self.get_dbsession()
        return self.dbsession.query(self.model)

    def get_serializer_class(self):
        return RequestSerializer

class GenericAPIViewTests(TestCase):

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(engine)
        cls.dbsession = get_dbsession()

        for i in range(2):
            cls.dbsession.add(
                Request(id=(i+1), name='test_request_{}'.format(i+1))
            )
        cls.dbsession.commit()

    @classmethod
    def tearDownClass(cls):
        cls.dbsession.close()

    def setUp(self):
        self.request = testing.DummyRequest
        self.view = RequestAPIView()
        self.view.request = self.request
        self.view_override = RequestOverrideAPIView()
        self.view_override.request = self.request

    def test_get_query_w_model(self):
        query = self.view.get_query()
        assert isinstance(query, Query)

    def test_get_query_w_override(self):
        query = self.view_override.get_query()
        assert isinstance(query, Query)

    def test_missing_model(self):
        view = generics.GenericAPIView()
        view.request = self.request
        self.assertRaises(AssertionError, view.get_query)

    def test_get_object(self):
        self.view.lookup_url_kwargs = {'id': 1}
        instance = self.view.get_object()
        assert isinstance(instance, Request)
        assert instance.id == 1
        assert instance.name == 'test_request_1'

    def test_get_object_override(self):
        self.view_override.lookup_url_kwargs = {'id': 1}
        instance = self.view_override.get_object()
        assert isinstance(instance, Request)
        assert instance.id == 1
        assert instance.name == 'test_request_1'

    def test_get_object_not_found(self):
        self.view.lookup_url_kwargs = {'id': 3}
        self.assertRaises(HTTPNotFound, self.view.get_object)

    def test_get_serializer(self):
        serializer = self.view.get_serializer()
        assert isinstance(serializer, RequestSerializer)
        assert serializer.context['request'] == self.request

    def test_get_serializer_override(self):
        serializer = self.view_override.get_serializer()
        assert isinstance(serializer, RequestSerializer)
        assert serializer.context['request'] == self.request

class ConcreteGenericAPIViewTests(TestCase):

    def test_create_api_view_post(self):
        class MockCreateAPIView(generics.CreateAPIView):
            def create(self, request, *args, **kwargs):
                self.called = True
                self.call_args = (request, args, kwargs)

        view = MockCreateAPIView()
        data = ('test request', ('test arg',), {'test_kwarg': 'test'})
        view.post('test request', 'test arg', test_kwarg='test')
        assert view.called is True
        assert view.call_args == data

    def test_list_api_view_get(self):
        class MockListAPIView(generics.ListAPIView):
            def list(self, request, *args, **kwargs):
                self.called = True
                self.call_args = (request, args, kwargs)

        view = MockListAPIView()
        data = ('test request', ('test arg',), {'test_kwarg': 'test'})
        view.get('test request', 'test arg', test_kwarg='test')
        assert view.called is True
        assert view.call_args == data

    def test_retrieve_api_view_get(self):
        class MockRetrieveAPIView(generics.RetrieveAPIView):
            def retrieve(self, request, *args, **kwargs):
                self.called = True
                self.call_args = (request, args, kwargs)

        view = MockRetrieveAPIView()
        data = ('test request', ('test arg',), {'test_kwarg': 'test'})
        view.get('test request', 'test arg', test_kwarg='test')
        assert view.called is True
        assert view.call_args == data

    def test_update_api_view_put(self):
        class MockUpdateAPIView(generics.UpdateAPIView):
            def update(self, request, *args, **kwargs):
                self.called = True
                self.call_args = (request, args, kwargs)

        view = MockUpdateAPIView()
        data = ('test request', ('test arg',), {'test_kwarg': 'test'})
        view.put('test request', 'test arg', test_kwarg='test')
        assert view.called is True
        assert view.call_args == data

    def test_destroy_api_view_delete(self):
        class MockDestroyAPIView(generics.DestroyAPIView):
            def delete(self, request, *args, **kwargs):
                self.called = True
                self.call_args = (request, args, kwargs)

        view = MockDestroyAPIView()
        data = ('test request', ('test arg',), {'test_kwarg': 'test'})
        view.delete('test request', 'test arg', test_kwarg='test')
        assert view.called is True
        assert view.call_args == data