# -*- coding:utf-8 -*-
from pyramid.decorator import reify

class LazyQuery(object):
    def __init__(self):
        self.fns = []

    def filter(self, *args, **kwargs):
        self.fns.append(lambda qs : qs.filter(*args, **kwargs))
        return self

    def filter_by(self, *args, **kwargs):
        self.fns.append(lambda qs : qs.filter_by(*args, **kwargs))
        return self

    @classmethod
    def inject(cls, target_cls):
        @reify
        def lazy_query(self):
            return cls()
        def filter(self, *args, **kwargs):
            self.lazy_query.filter(*args, **kwargs)
            return self
        def filter_by(self, *args, **kwargs):
            self.lazy_query.filter_by(*args, **kwargs)
            return self
        def filtered_query(self, qs):
            for fn in self.lazy_query.fns:
                qs = fn(qs)
            return qs

        target_cls.lazy_query = lazy_query
        target_cls.filter = filter
        target_cls.filter_by = filter_by
        target_cls.filtered_query = filtered_query
        return target_cls

@LazyQuery.inject
class AssetRepository(object):
    def __init__(self, request, Model, offset=5):
        self.request = request
        self.Model = Model
        self.offset = offset

    def list_of_asset(self, asset_id, i=0):
        if asset_id is None:
            return self.list_of_asset_any(i)
        return self.list_of_asset_with_selected(asset_id, i)

    def list_of_asset_any(self, i, j=0):
        qs = self.request.allowable(self.Model)
        if i > 0:
            qs = qs.offset((self.offset*i)+j)
        return list(self.filtered_query(qs).limit(self.offset))

    def list_of_asset_with_selected(self, asset_id, i):
        if i > 0:
            return self.list_of_asset_any(i, -1)
        qs = self.request.allowable(self.Model)
        rest = list(self.filtered_query(qs).limit(self.offset-1))
        r = [self.request.allowable(self.Model).get(asset_id)]
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
            return self.request.allowable(self.Model).get(pk)
