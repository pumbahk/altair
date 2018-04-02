# -*- coding: utf-8 -*-

from pyramid.httpexceptions import HTTPNotFound
from sqlahelper import get_session
from sqlalchemy.orm.exc import NoResultFound

from altair.restful_framework.settings import api_settings

from . import mixins
from .views import APIView


class GenericAPIView(APIView):
    pagination_class = api_settings.default_pagination_class
    model = None
    serializer_class = None
    filter_classes = ()
    lookup_field = 'id'
    dbsession = None

    def get_dbsession(self):
        return get_session()

    def get_query(self):
        assert self.model is not None, (
            "'{}' should include a `model` attribute, or override the `get_query` method."
                .format(self.__class__.__name__)
        )
        if self.dbsession is None:
            self.dbsession = self.get_dbsession()

        return self.dbsession.query(self.model)

    def get_object(self):
        query = self.filter_query(self.get_query())

        if isinstance(self.lookup_field, str):
            lookup_col = getattr(self.model, self.lookup_field)
            lookup_val = self.lookup_url_kwargs[self.lookup_field]
        else:
            assert isinstance(self.lookup_field, tuple), (
                "'{}' `lookup_field` attribute  should be a string or a tuple of (<model class>, `column`>"
                    .format(self.__class__.__name__)
            )

            lookup_col = getattr(self.lookup_field[0], self.lookup_field[1])
            lookup_val = self.lookup_url_kwargs[self.lookup_field[1]]

        try:
            instance = query.filter(lookup_col == lookup_val).one()
        except NoResultFound:
            raise HTTPNotFound()

        self.check_object_permission(self.request, instance)

        return instance

    def get_serializer_class(self):

        assert self.serializer_class is not None, (
            "'{}' should include a `serializer_class` attribute,"
            "or orverride the `get_serializer_class` method."
        )

        return self.serializer_class

    def get_serializer_context(self):

        return {'request': self.request}

    def get_serializer(self, *args, **kwargs):

        klass = self.get_serializer_class()
        kwargs['context'] = dict(
            self.get_serializer_context(),
            **kwargs
        )

        return klass(*args, **kwargs)

    def filter_query(self, query):
        """Filter the given query using the filter classes specified on the view if any are specified."""
        for filter_class in list(self.filter_classes):
            query = filter_class().filter_query(self.request, query, self)

        return query

    @property
    def paginator(self):
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()

        return self._paginator

    def paginate_query(self, query):
        if self.paginator is None:
            return None
        return self.paginator.paginate_query(query, self.request)

    def get_paginated_response(self, data):

        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

class CreateAPIView(mixins.CreateModelMixin, GenericAPIView):

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class UpdateAPIView(mixins.UpdateModelMixin, GenericAPIView):

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

class RetrieveAPIView(mixins.RetrieveModelMixin, GenericAPIView):

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

class DestroyAPIView(mixins.DestroyModelMixin, GenericAPIView):

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

class ListAPIView(mixins.ListModelMixin, GenericAPIView):

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

