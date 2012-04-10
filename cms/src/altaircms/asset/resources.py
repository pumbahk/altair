from altaircms.models import DBSession
from .models import Asset
from . import treat
from . import forms
import sqlalchemy as sa
from datetime import date
from altaircms.asset import get_storepath
import os
from altaircms.security import RootFactory

class AssetResource(RootFactory):
    DBSession = DBSession
    def __init__(self, request):
        self.request = request

    def get_assets(self):
        return Asset.query.order_by(sa.desc(Asset.id))

    def get_asset(self, id_):
        return Asset.query.filter(Asset.id==id_).one()

    def get_form_list(self):
        return (forms.ImageAssetForm(), 
                forms.MovieAssetForm(), 
                forms.FlashAssetForm())

    def get_confirm_form(self, asset_type, data=None):
        formclass = forms.get_confirm_asset_form_by_asset_type(asset_type)
        return formclass(data)

    def get_asset_storepath(self):
        return get_storepath(self.request)

    def write_asset_file(self, storepath, original_filename, buf):
        awriter = treat.AssetFileWriter(storepath)

        filepath = awriter.get_writename(original_filename)
        bufstring = buf.read()
        awriter._write_file(filepath, bufstring)

        return treat.AssetCreator(storepath, filepath, len(bufstring))

    def delete_asset_file(self, storepath, filename):
        filepath = os.path.join(storepath, filename)
        if os.path.exists(filepath):
            os.remove(filepath)

        
    
