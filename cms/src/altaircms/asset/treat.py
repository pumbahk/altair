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
from .swfrect import get_swf_rect, rect_to_size, in_pixel

def get_storepath(request=None, registry=None):
    if request:
        return request.registry.settings['altaircms.asset.storepath']
    else:
        registry = get_current_registry()
        return registry.settings["altaircms.asset.storepath"]

class AssetCreator(object):
    def __init__(self, storepath, filepath, size):
        self.storepath = storepath
        self.filepath = filepath
        self.size = size
        self.kwargs = dict(filepath=filepath, size=size)

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
        width, height = Image.open(os.path.join(self.storepath, self.filepath)).size
        return ImageAsset(width=width, height=height, **self.kwargs)

    def _movie_asset(self, data):
        self.kwargs.update(data)
        return MovieAsset(**self.kwargs)

    def _flash_asset(self, data):
        self.kwargs.update(data)
        width, height = in_pixel(rect_to_size(get_swf_rect(os.path.join(self.storepath, self.filepath))))
        return FlashAsset(width=width, height=height, **self.kwargs)

class AssetFileWriter(object): ##
    def __init__(self, storepath):
        self.storepath = storepath

    def _build_dirpath(self, dirpath):
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

    def get_writename(self, original_filename):
        today = date.today().strftime('%Y-%m-%d')
        ext = original_filename[original_filename.rfind('.') + 1:]
        return '%s/%s.%s' % (today, uuid4(), ext)

    def _write_file(self, writename, buf):
        """ return size"""
        self._build_dirpath(self.storepath)
        write_filepath = os.path.join(self.storepath, writename)
        self._build_dirpath(os.path.dirname(write_filepath))

        with open(write_filepath, "w+b") as dst_file:
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

