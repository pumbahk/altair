# -*- coding:utf-8 -*-
"""
CRUD asset model. this is util module.
if asset CRUD view is created,  this module will be obsolete.
"""
from datetime import date
import os
from uuid import uuid4

from pyramid.threadlocal import get_current_registry

from altaircms.asset import detect_mimetype
import Image
from altaircms.asset.models import ImageAsset
from altaircms.asset.models import MovieAsset
from altaircms.asset.models import FlashAsset
from .swfrect import get_swf_rect, rect_to_size, in_pixel
from altaircms.lib.treat.decorators import creator_from_form
from altaircms.lib.treat.decorators import updater_from_form
from altaircms.tag.api import get_tagmanager

@updater_from_form(name="asset", use_request=True)
@creator_from_form(name="asset", use_request=True)
class AssetTagAdapter(object):
    def __init__(self, form, request=None):
        self.form = form
        self.request = request

    def _divide_data(self):
        params = dict(self.form.data)
        tags = [k.strip() for k in params.pop("tags").split(",")] ##
        private_tags = [k.strip() for k in params.pop("private_tags").split(",")] ##
        return tags, private_tags, params

    def _create_asset(self, params):
        original_filename = params["filepath"].filename
        storepath = get_storepath(self.request)

        ## write file
        awriter = AssetFileWriter(storepath)
        filepath = awriter.get_writename(original_filename)
        buf = params["filepath"].file
        bufstring = buf.read()
        awriter._write_file(filepath, bufstring)

        ## create asset
        creator = AssetCreator(storepath, filepath, len(bufstring))
        create = creator.create_asset_function(self.form.type)
        return create(dict(alt=params["alt"], mimetype=detect_mimetype(original_filename))) ## tag
        
    def create(self):
        tags, private_tags, params = self._divide_data()
        asset = self._create_asset(params)
        self.replace_tags(asset, tags, True)
        self.replace_tags(asset, private_tags, False)
        return asset

    def update(self, asset):
        tags, private_tags, params = self._divide_data()
        for k, v in params.iteritems():
            setattr(asset, k, v)
        self.replace_tags(asset, tags, True)
        self.replace_tags(asset, private_tags, False)
        return asset

    def replace_tags(self, asset, tags, public_status):
        manager = get_tagmanager(self.form.type+"_asset", request=self.request)
        manager.replace_tags(asset, tags, public_status)

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

def create_asset(captured, request=None):
    """captured["type"], captured["filename"], captured["fp"]
    """
    storepath = get_storepath(request)

    awriter = AssetFileWriter(storepath)
    original_filename = captured["uploadfile"]["filename"]
    filepath = awriter.get_writename(original_filename)
    bufstring = captured['uploadfile']['fp'].read()
    awriter._write_file(filepath, bufstring)

    creator = AssetCreator(storepath, filepath, len(bufstring))
    create = creator.create_asset_function(captured["type"])
    return create(dict(mimetype=detect_mimetype(filepath)))
    

