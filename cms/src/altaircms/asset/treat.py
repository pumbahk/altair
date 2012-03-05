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
from altaircms.models import DBSession
from altaircms.asset.models import ImageAsset
from altaircms.asset.models import MovieAsset
from altaircms.asset.models import FlashAsset

def get_storepath(request=None):
    if request:
        return request.registry.settings['asset.storepath']
    else:
        registry = get_current_registry()
        return registry.settings["asset.storepath"]

def create_asset(captured, cb=None):
    """captured["type"], captured["filename"], captured["fp"]
    """
    today = date.today().strftime('%Y-%m-%d')
    storepath = os.path.join(get_storepath)
    storepath = os.path.join(get_storepath(),  today)
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

