# -*- coding:utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import os.path
from pyramid.response import Response
import uuid
from datetime import date

from . import SESSION_NAME
from . import ValidationError
from . import models
from ..models import DBSession
from ..filelib import get_adapts_filesession
from ..tag.api import tags_to_string, get_tagmanager, put_tags, tags_from_string
from ..tag.manager import QueryParser
from ..subscribers import notify_model_create
from .detect import ImageInfoDatector
from .detect import MovieInfoDatector
from .detect import FlashInfoDatector
from ..filelib import File
from .forms import normalize_filename

def get_asset_filesession(request):
    return get_adapts_filesession(request, name=SESSION_NAME)

try:
    import Image #PIL?
except  ImportError:
    from PIL import Image

## tag
def _extract_tags(params, k):
    if k not in params:
        return []
    return tags_from_string(params.pop(k))

def divide_data(params):
    tags = _extract_tags(params, "tags")
    private_tags = _extract_tags(params, "private_tags")
    return tags, private_tags, params


## file name
def get_uname(original_filename, gensym=lambda : uuid.uuid4().hex, gendate=date.today):
    today = gendate().strftime('%Y-%m-%d')
    ext = os.path.splitext(original_filename)[1]
    return os.path.join(today, gensym()) + ext

def uname_file_from_filestorage(filesession, filestorage):
    uname = get_uname(filestorage.filename)
    return File(name=uname, handler=filestorage.file)

def thumbnail_filename_from_mainfile(mainfile, ext=None):
    dirname, basename  = os.path.split(mainfile.name)
    if ext:
        noext = os.path.splitext(basename)[0]
        basename = ".".join((noext.rstrip("."), ext.lstrip(".")))
    return os.path.join(dirname,"thumb."+basename)

def thumbnail_file_from_mainfile(mainfile, filestorage):
    thumb_filename = thumbnail_filename_from_mainfile(mainfile, os.path.splitext(filestorage.filename)[1])
    return File(name=thumb_filename, handler=filestorage.file)

## form
def is_filled_filefield(filefield):
    return filefield != u""

## operator
def add_operator_when_created(asset, request):
    user = request.user
    asset.created_by = user
    asset.updated_by = user
    return asset

def add_operator_when_updated(asset, request):
    asset.updated_by = request.user
    return asset


## search
def query_filter_by_users(qs, data):
    created_by = data.get("created_by")
    if created_by:
        qs = qs.filter(models.Asset.created_by == created_by)

    updated_by = data.get("updated_by")
    if updated_by:
        qs = qs.filter(models.Asset.updated_by == updated_by)
    return qs


class Deleter(object):
    def __init__(self, request):
        self.request = request
        self.filesession = get_asset_filesession(self.request)

    def confirm(self, asset):
        try:
            self.filesession.delete(asset.filepath)
            self.filesession.delete(asset.thumbnail_path)
            return True
        except Exception, e:
            logger.exception(str(e))
            return False

    def delete(self, asset):
        if self.confirm(asset):
            ## moveit
            self.filesession.commit([asset])
            DBSession.delete(asset)


class Display(object):
    def __init__(self, request):
        self.request = request

    def as_response(self, asset):
        filesession = get_asset_filesession(self.request)
        filepath = filesession.abspath(asset.filepath)
        content_type = asset.mimetype if asset.mimetype else 'application/octet-stream'
        if os.path.exists(filepath):
            data =  file(filepath).read()
        else:
            data =  "" ## not found imageを表示した方が良い？
        return Response(data, content_type=content_type)


class Input(object):
    def __init__(self, request):
        self.request = request
        
    def on_update(self, asset, formclass):
        params = asset.to_dict()
        params["tags"] = tags_to_string(asset.public_tags)
        params["private_tags"] = tags_to_string(asset.private_tags)
        return formclass(**params)


class Creator(object):
    def __init__(self, request):
        self.request = request

    def create(self, params, form=None):
        if form and not form.validate():
            raise ValidationError(str(form.errors))

        def commit():
            return self.commit_create(params, form=form)
        return Committer(commit)

def thumbnail_image_from_io(io, size):
    io.seek(0)
    im = Image.open(io)
    im.thumbnail(size, Image.ANTIALIAS)
    io.seek(0)
    return im
    

class ImageCreator(Creator):
    size = 128, 128
    def commit_create(self, params, form=None):
        tags, private_tags, params =  divide_data(params)

        asset_data = {"title": params["title"]}
        extra_asset_data = ImageInfoDatector(self.request).detect(params["filepath"].file, params["filepath"].filename)

        ## file
        filesession = get_asset_filesession(self.request)
        mainimage_file = filesession.add(uname_file_from_filestorage(filesession, params["filepath"]))
        if params["thumbnail_path"] == u"":
            im = thumbnail_image_from_io(params["filepath"].file, self.size)
            thumbnail_file = filesession.add(File(name=thumbnail_filename_from_mainfile(mainimage_file, ext=".png"), 
                                                   handler=im,
                                                   save=lambda path, handler: im.save(path, "PNG") #todo: image type
                                                   )) #copy?
        else:
            thumbnail_file = filesession.add(thumbnail_file_from_mainfile(mainimage_file, params["thumbnail_path"]))

        ## asset
        asset = models.ImageAsset()
        asset_data.update(extra_asset_data)
        asset = models.ImageAsset(
            filepath=mainimage_file.name, 
            thumbnail_path=thumbnail_file.name, 
            **asset_data)

        put_tags(asset, "image_asset", tags, private_tags, self.request)
        add_operator_when_created(asset, self.request)
        notify_model_create(self.request, asset, asset_data)

        ## add
        DBSession.add(asset)
        filesession.commit([asset])
        return asset

class MovieCreator(Creator):
    def commit_create(self, params, form=None):
        tags, private_tags, params =  divide_data(params)

        asset_data = {"title": params["title"]}
        extra_asset_data = MovieInfoDatector(self.request).detect(params["filepath"].file, params["filepath"].filename)

        ## file
        filesession = get_asset_filesession(self.request)
        mainmovie_file = filesession.add(uname_file_from_filestorage(filesession, params["filepath"]))

        ## asset
        asset = models.MovieAsset()
        asset_data.update(extra_asset_data)
        asset = models.MovieAsset(
            filepath=mainmovie_file.name, 
            **asset_data)

        if is_filled_filefield(params["placeholder"]):
            thumbnail_file = filesession.add(thumbnail_file_from_mainfile(mainmovie_file, params["placeholder"]))
            asset.thumbnail_path = thumbnail_file.name

        put_tags(asset, "movie_asset", tags, private_tags, self.request)
        add_operator_when_created(asset, self.request)
        notify_model_create(self.request, asset, asset_data)

        ## add
        DBSession.add(asset)
        filesession.commit([asset])
        return asset

class FlashCreator(Creator):
    def commit_create(self, params, form=None):
        tags, private_tags, params =  divide_data(params)

        asset_data = {"title": params["title"]}
        extra_asset_data = FlashInfoDatector(self.request).detect(params["filepath"].file, params["filepath"].filename)

        ## file
        filesession = get_asset_filesession(self.request)
        mainflash_file = filesession.add(uname_file_from_filestorage(filesession, params["filepath"]))

        ## asset
        asset = models.FlashAsset()
        asset_data.update(extra_asset_data)
        asset = models.FlashAsset(
            filepath=mainflash_file.name, 
            **asset_data)

        if is_filled_filefield(params["placeholder"]):
            thumbnail_file = filesession.add(thumbnail_file_from_mainfile(mainflash_file, params["placeholder"]))
            asset.thumbnail_path = thumbnail_file.name

        put_tags(asset, "flash_asset", tags, private_tags, self.request)
        add_operator_when_created(asset, self.request)
        notify_model_create(self.request, asset, asset_data)

        ## add
        DBSession.add(asset)
        filesession.commit([asset])
        return asset

class Committer(object):
    def __init__(self, fn):
        self.fn = fn

    def commit(self):
        return self.fn()


class Updater(object):
    def __init__(self, request):
        self.request = request

    def update(self, asset, params, form=None):
        if form and not form.validate():
            raise ValidationError(str(form.errors))
        params = form.data
        if asset.filepath and hasattr(params["filepath"], "filename") and os.path.splitext(normalize_filename(params["filepath"].filename))[1] != os.path.splitext(asset.filepath)[1]:
            logger.warn("%s <-> %s" % (os.path.splitext(normalize_filename(params["filepath"].filename))[1] , os.path.splitext(asset.filepath)[1]))
            raise ValidationError(u"ファイルの拡張子が異なっています。変更できません。")

        def commit():
            asset.increment_version()
            return self.commit_update(asset, params, form=form)
        return Committer(commit)


def update_asset(asset, datalist):
    for vs in datalist:
        for k, v in vs.iteritems():
            setattr(asset, k, v)
    return asset


class ImageUpdater(Updater):
    size = 128, 128
    def commit_update(self, asset, params, form=None):
        tags, private_tags, params =  divide_data(params)
        datalist = []
        filesession = get_asset_filesession(self.request)
        if is_filled_filefield(params["filepath"]):
            extra_asset_data = ImageInfoDatector(self.request).detect(params["filepath"].file, params["filepath"].filename)
            datalist.append(extra_asset_data)
            mainimage_file = filesession.add(File(name=asset.filename_with_version(), handler=params["filepath"].file))
            datalist.append(dict(filepath=mainimage_file.name))
            if not is_filled_filefield(params["thumbnail_path"]):
                im = thumbnail_image_from_io(params["filepath"].file, self.size)
                thumbnail_name = thumbnail_filename_from_mainfile(mainimage_file, ext=".png")
                thumbnail_file = filesession.add(File(name=thumbnail_name, 
                                                      handler=im,
                                                      save=lambda path, handler: im.save(path, "PNG") #todo: image type
                                                      ))
                datalist.append(dict(thumbnail_path=thumbnail_file.name))

        if is_filled_filefield(params["thumbnail_path"]):
            thumbnail_file = filesession.add(File(name=asset.filename_with_version(asset.thumbnail_path), handler=params["thumbnail_path"].file))
            datalist.append(dict(thumbnail_path=thumbnail_file.name))

        datalist.append({k:v for k, v in params.iteritems() if v})
        asset = update_asset(asset, datalist)
        put_tags(asset, "image_asset", tags, private_tags, self.request)
        add_operator_when_updated(asset, self.request)

        ## add
        DBSession.add(asset)
        filesession.commit([asset])
        return asset

class MovieUpdater(Updater):
    def commit_update(self, asset, params, form=None):
        tags, private_tags, params =  divide_data(params)
        datalist = []
        filesession = get_asset_filesession(self.request)
        if is_filled_filefield(params["filepath"]):
            extra_asset_data = MovieInfoDatector(self.request).detect(params["filepath"].file, params["filepath"].filename)
            datalist.append(extra_asset_data)
            mainmovie_file = filesession.add(File(name=asset.filename_with_version(), handler=params["filepath"].file))
            datalist.append(dict(filepath=mainmovie_file.name))

        if is_filled_filefield(params["placeholder"]):
            placeholder = params["placeholder"]
            name = asset.filename_with_version(asset.thumbnail_path) or \
                thumbnail_filename_from_mainfile(File(name=asset.filepath, handler=None),  placeholder.filename)
            thumbnail_file = filesession.add(File(name=name, handler=placeholder.file))
            datalist.append(dict(thumbnail_path=thumbnail_file.name))

        datalist.append({k:v for k, v in params.iteritems() if v})
        asset = update_asset(asset, datalist)
        put_tags(asset, "movie_asset", tags, private_tags, self.request)
        add_operator_when_updated(asset, self.request)

        ## add
        DBSession.add(asset)
        filesession.commit([asset])
        return asset

class FlashUpdater(Updater):
    def commit_update(self, asset, params, form=None):
        tags, private_tags, params =  divide_data(params)
        datalist = []
        filesession = get_asset_filesession(self.request)

        if is_filled_filefield(params["filepath"]):
            extra_asset_data = FlashInfoDatector(self.request).detect(params["filepath"].file, params["filepath"].filename)
            datalist.append(extra_asset_data)
            mainflash_file = filesession.add(File(name=asset.filename_with_version(), handler=params["filepath"].file))
            datalist.append(dict(filepath=mainflash_file.name))

        if is_filled_filefield(params["placeholder"]):
            placeholder = params["placeholder"]
            name = asset.filename_with_version(asset.thumbnail_path) or \
                thumbnail_filename_from_mainfile(File(name=asset.filepath, handler=None),  placeholder.filename)
            thumbnail_file = filesession.add(File(name=name, handler=placeholder.file))
            datalist.append(dict(thumbnail_path=thumbnail_file.name))

        datalist.append({k:v for k, v in params.iteritems() if v})
        asset = update_asset(asset, datalist)
        put_tags(asset, "flash_asset", tags, private_tags, self.request)
        add_operator_when_updated(asset, self.request)

        ## add
        DBSession.add(asset)
        filesession.commit([asset])
        return asset
   
class ImageSearcher(object):
    def __init__(self, request):
        self.request = request

    def search(self, qs, data):
        qs = query_filter_by_users(qs, data)
        if not "tags" in data:
            return qs
        
        manager = get_tagmanager("image_asset")
        return QueryParser(data["tags"]).filter_by_manager(manager, qs, organization_id=self.request.organization.id)

class MovieSearcher(object):
    def __init__(self, request):
        self.request = request

    def search(self, qs, data):
        qs = query_filter_by_users(qs, data)
        if not "tags" in data:
            return qs
        
        manager = get_tagmanager("movie_asset")
        return QueryParser(data["tags"]).filter_by_manager(manager, qs, organization_id=self.request.organization.id)

class FlashSearcher(object):
    def __init__(self, request):
        self.request = request

    def search(self, qs, data):
        qs = query_filter_by_users(qs, data)
        if not "tags" in data:
            return qs
        
        manager = get_tagmanager("flash_asset")
        return QueryParser(data["tags"]).filter_by_manager(manager, qs, organization_id=self.request.organization.id)
