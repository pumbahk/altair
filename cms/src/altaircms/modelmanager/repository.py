# -*- coding:utf-8 -*-
from pyramid.decorator import reify
import logging
logger = logging.getLogger(__name__)
import copy

class LazyQuery(object):
    def __init__(self, fns=None):
        self.fns = fns or []

    def filter(self, *args, **kwargs):
        fns = self.fns[:]
        fns.append(lambda qs : qs.filter(*args, **kwargs))
        return self.__class__(fns)

    def filter_by(self, *args, **kwargs):
        fns = self.fns[:]
        fns.append(lambda qs : qs.filter_by(*args, **kwargs))
        return self.__class__(fns)

    def order_by(self, *args, **kwargs):
        fns = self.fns[:]
        fns.append(lambda qs : qs.order_by(*args, **kwargs))
        return self.__class__(fns)

    @classmethod
    def inject(cls, target_cls):
        @reify
        def lazy_query(self):
            return cls()

        def filter(self, *args, **kwargs):
            q = self.lazy_query.filter(*args, **kwargs)
            copied = copy.copy(self)
            copied.lazy_query = q
            return copied

        def filter_by(self, *args, **kwargs):
            q = self.lazy_query.filter_by(*args, **kwargs)
            copied = copy.copy(self)
            copied.lazy_query = q
            return copied

        def order_by(self, *args, **kwargs):
            q = self.lazy_query.order_by(*args, **kwargs)
            copied = copy.copy(self)
            copied.lazy_query = q
            return copied

        def filtered_query(self, qs):
            for fn in self.lazy_query.fns:
                qs = fn(qs)
            return qs

        target_cls.lazy_query = lazy_query
        target_cls.filter = filter
        target_cls.filter_by = filter_by
        target_cls.order_by = order_by
        target_cls.filtered_query = filtered_query
        return target_cls

@LazyQuery.inject
class AssetRepository(object):
    def __init__(self, request, Model, offset=5, qs=None):
        self.request = request
        self.Model = Model
        self.offset = offset
        self.qs = qs

    def count_of_asset(self, asset_id=None):
        qs = self.filtered_query(self._get_query())
        if asset_id is None:
            size = qs.count()
        else:
            size = qs.count() + 1

        if size % self.offset == 0:
            return size / self.offset
        else:
            return (size / self.offset) + 1
            
    def start_from(self, qs):
        copied = copy.copy(self)
        copied.qs = qs
        return copied

    def _get_query(self):
        return self.qs or self.request.allowable(self.Model)

    def list_of_asset(self, asset_id, i=0):
        if asset_id is None:
            return self.list_of_asset_any(i)
        return self.list_of_asset_with_selected(asset_id, i)

    def list_of_asset_any(self, i, j=0):
        qs = self.filtered_query(self._get_query())
        if i > 0:
            qs = qs.offset((self.offset*i)+j)
        return list(qs.limit(self.offset))

    def list_of_asset_with_selected(self, asset_id, i):
        if i > 0:
            return self.list_of_asset_any(i, -1)
        qs = self.filtered_query(self._get_query())
        rest = list(qs.limit(self.offset-1))
        one = self.request.allowable(self.Model).filter_by(id=asset_id).one() #hmm:
        r = [one]
        r.extend(rest)
        return r

class WidgetRepository(object):
    def __init__(self, request, Model):
        self.request = request
        self.Model = Model

    def get_or_create(self, pk):
        if pk is None or pk=="null":
            return self.Model()
        else:
            logger.info("%s -- %s",  self.Model, pk)
            return self.request.allowable(self.Model).get(pk)
