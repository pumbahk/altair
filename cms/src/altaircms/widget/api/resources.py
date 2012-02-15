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

class UsingWidgetMixin(object):
    from altaircms.widget.models import ImageWidget
    from altaircms.widget.models import TextWidget
    from altaircms.widget.models import DBSession
    def _get_or_create(self, model, widget_id):
        if widget_id is None:
            return model({})
        else:
            return DBSession.query(model).filter(model.id == widget_id).one()
        
    def get_image_widget(self, widget_id):
        return self._get_or_create(self.ImageWidget, widget_id)

    def get_freetext_widget(self, widget_id):
        return self._get_or_create(self.TextWidget, widget_id)

    def update_widget(self, widget, params):
        set_with_dict(widget, params)
        return widget

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
                     UsingLayoutMixin,
                     UsingWidgetMixin):
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
