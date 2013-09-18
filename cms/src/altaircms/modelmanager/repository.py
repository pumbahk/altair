# -*- coding:utf-8 -*-
class AssetRepository(object):
    def __init__(self, request, Model, offset=5):
        self.request = request
        self.Model = Model
        self.offset = offset

    def list_of_asset(self, asset_id, i=1):
        if asset_id is None:
            return self.list_of_asset_any(i)
        return self.list_of_asset_with_selected(asset_id, i)

    def list_of_asset_any(self, i, j=0):
        qs = self.request.allowable(self.Model)
        if i > 1:
            qs = qs.offset(self.offset*(i-1)+j)
        return list(qs.limit(self.offset))
        
    def list_of_asset_with_selected(self, asset_id, i):
        if i > 1:
            return self.list_of_asset_any(i, -1)
        qs = self.request.allowable(self.Model)
        rest = list(qs.limit(self.offset-1))
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
