# -*- coding:utf-8 -*-
from altaircms.models import DBSession

def set_with_dict(obj, D):
    for k, v in D.items():
        setattr(obj, k, v)
    return obj

class UsingAssetMixin(object):
    from altaircms.asset.models import ImageAsset
    def get_image_asset_query(self):
        return self.ImageAsset.query

    def get_image_asset(self, asset_id):
        return self.ImageAsset.query.filter(self.ImageAsset.id == asset_id).one()

class UsingPageMixin(object):
    from altaircms.page.models import Page
    def get_page(self, page_id):
        return self.Page.query.filter(self.Page.id == page_id).one()

class UsingLayoutMixin(object):
    from altaircms.layout.models import Layout
    def get_layout_query(self):
        return self.Layout.query

    def get_layout_template(self, layoutname):
        return self.Layout.query.filter(self.Layout.title==layoutname).one()
    
class WidgetResource(UsingAssetMixin,
                     UsingPageMixin, 
                     UsingLayoutMixin):
    def __init__(self, request):
        self.request = request
        
    def add(self, data, flush=False):
        DBSession.add(data)
        if flush:
            DBSession.flush()
        
    def delete(self, data, flush=False):
        DBSession.delete(data)
        if flush:
            DBSession.flush()
