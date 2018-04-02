#-*- coding: utf-8 -*-

from marshmallow import ValidationError
from pyramid.response import Response

class ListModelMixin(object):

    def list(self, request, *args, **kwargs):
        data = self.filter_query(self.get_query()).all()
        serializer = self.get_serializer()
        page = self.paginate_query(data)

        if page is not None:
            data = serializer.dump(page, many=True)
            return self.get_paginated_response(data)

        data = serializer.dump(data, many=True)
        return Response(json=data)

class RetrieveModelMixin(object):

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer()
        instance = self.get_object()
        data = serializer.dump(instance)

        return Response(json=data)

class CreateModelMixin(object):

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer()
        try:
            data = serializer.load(self.request.POST)
        except ValidationError as exc:
            return Response(json=exc.message, status=400)

        instance = self.perform_create(data)
        data = serializer.dump(instance)

        return Response(json=data, status=201)

    def perform_create(self, data):
        instance = self.model(**data)
        instance.save()
        return instance


class UpdateModelMixin(object):

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer()

        try:
            data = serializer.load(self.request.POST)
        except ValidationError as exc:
            return Response(json=exc.message, status=400)

        instance = self.perform_update(data, instance)
        data = serializer.dump(instance)

        return Response(json=data)

    def perform_update(self, data, instance):

        for key, val in data.items():
            setattr(instance, key, val)

        self.dbsession.merge(instance)
        self.dbsession.flush()

        return instance

class DestroyModelMixin(object):

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destory(instance)

        return Response(status=204)

    def perform_destory(self, instance):
        self.dbsession.delete(instance)