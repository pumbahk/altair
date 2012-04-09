from altaircms.models import DBSession
from .models import Asset
from . import treat
from . import forms
import sqlalchemy as sa
from datetime import date
from altaircms.asset import get_storepath
import os

class AssetResource(object):
    DBSession = DBSession
    def __init__(self, request):
        self.request = request

    def get_assets(self):
        return Asset.query.order_by(sa.desc(Asset.id))

    def get_asset(self, id_):
        return Asset.query.filter(Asset.id==id_).one()

    def get_form(self, asset_type=None, data=None):
        return forms.ImageAssetForm(formdata=data) 
        if asset_type == "image":
            return forms.ImageAssetForm()
        else:
            raise Exception

    def get_asset_storepath(self):
        return get_storepath(self.request)

    def write_asset_file(self, storepath, original_filename, buf):
        awriter = treat.AssetFileWriter(storepath)

        awriter._build_dirpath()
        filepath = awriter.get_writename(original_filename)

        bufstring = buf.read()
        awriter._write_file(filepath, bufstring)

        return treat.AssetCreator(size=len(bufstring), filepath=filepath)

    def delete_asset_file(self, storepath, filename):
        filepath = os.path.join(storepath, filename)
        if os.path.exists(filepath):
            os.remove(filepath)

        
    
