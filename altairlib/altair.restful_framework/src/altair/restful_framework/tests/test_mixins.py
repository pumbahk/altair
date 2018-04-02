# -*- coding: utf-8 -*-

import json

from marshmallow import ValidationError
from mock import Mock
from pyramid import testing
from pyramid.response import Response
from unittest import TestCase
from webob.multidict import MultiDict

from altair.restful_framework import mixins

class MockAPIView(object):

    def model_side_effect(**data):
        instance = Mock()

        for key, val in data.items():
            setattr(instance, key, val)

        return instance

    model = Mock(side_effect=model_side_effect)

    dataset = [
        {'name': 'test 1', 'id': 1},
        {'name': 'test 2', 'id': 2}
    ]

    def get_query(self):
        class MockQuery(list):
            def __init__(self, *args, **kwargs):
                super(MockQuery, self).__init__(*args, **kwargs)

            def all(self):
                return self

        ret = MockQuery()

        for data in self.dataset:
            instance = Mock()
            for key, val in data.items():
                setattr(instance, key, val)
            ret.append(instance)

        return ret

    def filter_query(self, query):
        return query

    def get_serializer(self, *args, **kwargs):
        def dump(data, many=False, **kwargs):
            if many:
                return [{'id': i.id, 'name': i.name} for i in data]

            return {'id': data.id, 'name': data.name}

        def load(data, partial=False):
            if not partial and data['id'] == 4:
                raise ValidationError(message={'id': ['Invalid Value.']})
            return data

        serializer = Mock()
        serializer.dump = Mock(side_effect=dump)
        serializer.load = Mock(side_effect=load)

        return serializer

    def paginate_query(self, data):
        return [data[0]]

    def get_paginated_response(self, data):
        return Response(json=data)

    def get_object(self):
        instance = Mock()

        for key, val in self.dataset[0].items():
            setattr(instance, key, val)

        return instance

class NoPageMockAPIView(MockAPIView):
    def paginate_query(self, data):
        return None


class ModelMixinUnitTests(TestCase):

    def setUp(self):
        self.request = testing.DummyRequest()

    def test_list_mixin(self):
        class MockListAPIView(mixins.ListModelMixin, MockAPIView):
            pass

        view = MockListAPIView()
        resp = view.list(self.request)
        assert resp.status_code == 200
        assert json.loads(resp.body) == [{"id": 1, "name": "test 1"}]

    def test_list_mixin_no_page(self):
        class MockListAPIView(mixins.ListModelMixin, NoPageMockAPIView):
            pass

        view = MockListAPIView()
        resp = view.list(self.request)
        assert resp.status_code == 200
        assert json.loads(resp.body) == [
            {"id": 1, "name": "test 1"}, {"id": 2, "name": "test 2"}
        ]

    def test_retrieve_mixin(self):
        class MockRetrieveAPIView(mixins.RetrieveModelMixin, MockAPIView):
            pass

        view = MockRetrieveAPIView()
        resp = view.retrieve(self.request)
        assert resp.status_code == 200
        assert json.loads(resp.body) == {"id": 1, "name": "test 1"}

    def test_create_mixin(self):
        class MockCreateAPIView(mixins.CreateModelMixin, MockAPIView):
            pass

        view = MockCreateAPIView()
        view.request = self.request
        self.request.POST = MultiDict({'id': 3, 'name': 'test 3'})
        resp = view.create(self.request)
        assert resp.status_code == 201
        assert json.loads(resp.body) == {"id": 3, "name": "test 3"}

    def test_bad_create_mixin(self):
        class MockCreateAPIView(mixins.CreateModelMixin, MockAPIView):
            pass

        view = MockCreateAPIView()
        view.request = self.request
        self.request.POST = MultiDict({'id': 4, 'name': 'test 4'})
        resp = view.create(self.request)
        assert resp.status_code == 400
        assert json.loads(resp.body) == {'id': ['Invalid Value.']}

    def test_update_mixin(self):
        class MockUpdateAPIView(mixins.UpdateModelMixin, MockAPIView):
            pass

        view = MockUpdateAPIView()
        view.request = self.request
        view.dbsession = Mock()
        self.request.POST = MultiDict({'id': 1, 'name': 'test 5'})
        resp = view.update(self.request)
        assert resp.status_code == 200
        assert json.loads(resp.body) == {'id': 1, 'name': 'test 5'}

    def test_bad_update_mixin(self):
        class MockUpdateAPIView(mixins.UpdateModelMixin, MockAPIView):
            pass

        view = MockUpdateAPIView()
        view.request = self.request
        view.dbsession = Mock()
        self.request.POST = MultiDict({'id': 4, 'name': 'test 4'})
        resp = view.update(self.request)
        assert resp.status_code == 400
        assert json.loads(resp.body) == {'id': ['Invalid Value.']}

    def test_destroy_mixin(self):
        class MockDestroyAPIView(mixins.DestroyModelMixin, MockAPIView):
            pass

        view = MockDestroyAPIView()
        view.request = self.request
        view.dbsession = Mock()
        resp = view.destroy(self.request)
        assert resp.status_code == 204
        assert view.dbsession.delete.call_count == 1