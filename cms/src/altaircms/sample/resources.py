from altaircms.models import DBSession
from deform.form import Form

class UsingAssetMixin(object):
    import altaircms.asset.models as m
    def get_image_asset_query(self):
        return self.m.ImageAsset.query

class UsingLayoutMixin(object):
    import altaircms.layout.models as m
    def get_layout_template(self, layoutname):
        Layout = self.m.Layout
        return Layout.query.filter(Layout.title==layoutname).one()
    
class SampleResource(UsingAssetMixin, UsingLayoutMixin):
    def __init__(self, request):
        self.request = request
        
    def add(self, data):
        DBSession.add(data)

