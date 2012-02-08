import altaircms.asset.models as m

class AssetResource(object):
    def __init__(self, request):
        self.request = request

    def get_image_asset_query(self):
        return m.ImageAsset.query.all()


