from altaircms.models import DBSession
from .models import (
    Asset, 
    ImageAsset, 
    FlashAsset, 
    MovieAsset
    )
from . import forms
import sqlalchemy as sa
from altaircms.asset import get_storepath
import os
from altaircms.security import RootFactory

class AssetResource(RootFactory):
    DBSession = DBSession
    def __init__(self, request):
        self.request = request

    def get_assets(self, asset_type=None):
        if asset_type:
            if asset_type == "image":
                return ImageAsset.query.order_by(sa.desc(Asset.id))
            elif asset_type == "flash":
                return FlashAsset.query.order_by(sa.desc(Asset.id))
            elif asset_type == "movie":
                return MovieAsset.query.order_by(sa.desc(Asset.id))
        else:
            return Asset.query.order_by(sa.desc(Asset.id))

    def get_asset(self, id_):
        return Asset.query.filter(Asset.id==id_).one()

    def get_form_list(self):
        return (forms.ImageAssetForm(), 
                forms.MovieAssetForm(), 
                forms.FlashAssetForm())

    def get_form(self, asset_type):
        formclass = forms.get_confirm_asset_form_by_asset_type(asset_type)
        return formclass()

    def get_confirm_form(self, asset_type, data=None):
        formclass = forms.get_confirm_asset_form_by_asset_type(asset_type)
        return formclass(data)

    def get_asset_storepath(self):
        return get_storepath(self.request)

    def delete_asset_file(self, storepath, filename):
        filepath = os.path.join(storepath, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
