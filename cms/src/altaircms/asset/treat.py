# -*- coding:utf-8 -*-
"""
CRUD asset model. this is util module.
if asset CRUD view is created,  this module will be obsolete.
"""
from datetime import date
import os
from uuid import uuid4

from pyramid.threadlocal import get_current_registry

from altaircms.asset.views import detect_mimetype
import Image
from altaircms.asset.models import ImageAsset
from altaircms.asset.models import MovieAsset
from altaircms.asset.models import FlashAsset

def get_storepath(request=None, registry=None):
    if request:
        return request.registry.settings['altaircms.asset.storepath']
    else:
        registry = get_current_registry()
        return registry.settings["altaircms.asset.storepath"]

class AssetCreator(object):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def create_asset_function(self, asset_type):
        if asset_type == "image":
            return self._image_asset
        elif asset_type == "movie":
            return self._movie_asset
        elif asset_type == "flash":
            return self._flash_asset
        else:
            raise Exception("not found asset_type")

    def _image_asset(self, data):
        self.kwargs.update(data)
        return ImageAsset(**self.kwargs)

    def _movie_asset(self, fname, data):
        data = self.kwargs.update(data)
        width, height = Image.open(fname).size
        return MovieAsset(width=width, height=height, **data)

    def _flash_asset(self, data):
        data = self.kwargs.update(data)
        return FlashAsset(**data)

class AssetFileWriter(object): ##
    def __init__(self, storepath):
        self.storepath = storepath

    def _build_dirpath(self):
        if not os.path.exists(self.storepath):
            os.makedirs(self.storepath)

    def get_writename(self, original_filename):
        return '%s.%s' % (uuid4(), original_filename[original_filename.rfind('.') + 1:])

    def _write_file(self, writename, buf):
        """ return size"""
        dst_file = open(os.path.join(self.storepath, writename), "w+b")
        dst_file.write(buf)
        dst_file.seek(0)

def create_asset(captured, request=None, cb=None):
    """captured["type"], captured["filename"], captured["fp"]
    """
    today = date.today().strftime('%Y-%m-%d')
    storepath = os.path.join(get_storepath(request),  today)
    # @TODO: S3に対応する
    if not os.path.exists(storepath):
        os.makedirs(storepath)
    original_filename = captured['uploadfile']['filename']
    filename = '%s.%s' % (uuid4(), original_filename[original_filename.rfind('.') + 1:])
    f = open(os.path.join(storepath, filename), 'wb')
    f.write(captured['uploadfile']['fp'].read())
    
    mimetype = detect_mimetype(filename)

    if captured['type'] == 'image':
        asset = ImageAsset(filepath=os.path.join(today, filename), mimetype=mimetype)
    elif captured['type'] == 'movie':
        asset = MovieAsset(filepath=os.path.join(today, filename), mimetype=mimetype)
    elif captured['type'] == 'flash':
        asset = FlashAsset(filepath=os.path.join(today, filename))

    if cb:
        cb(asset)
    else:
        return asset

