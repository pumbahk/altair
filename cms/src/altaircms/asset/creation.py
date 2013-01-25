import logging
logger = logging.getLogger(__name__)

import os.path
from pyramid.response import Response

from . import SESSION_NAME
from ..models import DBSession
from ..filelib import get_filesession
from ..tag.api import tags_to_string

def get_asset_filesession(request):
    return get_filesession(request, name=SESSION_NAME)

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
            DBSession.delete(asset)
            ## moveit
            self.filesession.commit()

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
            raise Exception(str(form.errors))

        def commit():
            return self.commit_create(params, form=form)
        return Committer(commit)

class ImageCreator(Creator):
    def commit_create(self, params, form=None):
        asset = self.context.create_image_asset(form)
        self.context.add(asset)

class MovieCreator(Creator):
    def commit_create(self, params, form=None):
        asset = self.context.create_movie_asset(form)
        self.context.add(asset)

class FlashCreator(Creator):
    def commit_create(self, params, form=None):
        asset = self.context.create_flash_asset(form)
        self.context.add(asset)


class Committer(object):
    def __init__(self, fn):
        self.fn = fn

    def commit(self):
        return self.fn()

class Updater(object):
    def __init__(self, request):
        self.request = request

    def update(self, asset, params, form=None):
        if hasattr(params["filepath"], "filename") and os.path.splitext(params["filepath"].filename)[1] != os.path.splitext(asset.filepath)[1]:
            raise Exception(u"ファイルの拡張子が異なっています。変更できません。")

        if form and not form.validate():
            raise Exception(str(form.errors))

        def commit():
            return self.commit_update(asset, params, form=form)
        return Committer(commit)


class ImageUpdater(Updater):
    def commit_update(self, asset, params, form=None):
        return self.request.context.update_image_asset(asset, form)        

class MovieUpdater(Updater):
    def commit_update(self, asset, params, form=None):
        return self.request.context.update_movie_asset(asset, form)        

class FlashUpdater(Updater):
    def commit_update(self, asset, params, form=None):
        return self.request.context.update_flash_asset(asset, form)        
    
