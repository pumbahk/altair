from altaircms.models import DBSession

def set_with_dict(obj, D):
    for k, v in D.items():
        setattr(obj, k, v)
    return obj

class UsingAssetMixin(object):
    import altaircms.asset.models as m
    def get_image_asset_query(self):
        return self.m.ImageAsset.query

    def get_image_asset(self, asset_id):
        return self.m.ImageAsset.query.filter(self.m.ImageAsset.id == asset_id).one()

class UsingWidgetMixin(object):
    def get_image_widget(self, widget_id):
        print widget_id
        if widget_id is None:
            return self.m.ImageAsset(widget_id)
        else:
            return self.m.ImageAsset.query.filter(self.m.ImageAsset.id == widget_id).one()

    def update_widget(self, widget, params):
        set_with_dict(widget, params)
        return widget
        
class UsingLayoutMixin(object):
    import altaircms.layout.models as m

    def get_layout_query(self):
        return self.m.Layout.query

    def get_layout_template(self, layoutname):
        Layout = self.m.Layout
        return Layout.query.filter(Layout.title==layoutname).one()

class UsingPageMixin(object):
    pass
    
class SampleResource(UsingAssetMixin, UsingLayoutMixin, UsingWidgetMixin):
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


