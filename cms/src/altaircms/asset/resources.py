# -*- coding:utf-8 -*-
import os
import sqlalchemy as sa


from altaircms.models import DBSession
from altaircms.security import RootFactory
from . import models
from . import helpers as h
from altaircms.tag.api import put_tags
from pyramid.decorator import reify
from . import forms
from altaircms.auth.api import get_or_404
from altaircms.subscribers import notify_model_create

def _setattrs(asset, params):
    for k, v in params.iteritems():
        if v:
            setattr(asset, k, v)

def add_operator_when_created(asset, request):
    user = request.user
    asset.created_by = user
    asset.updated_by = user
    return asset

def add_operator_when_updated(asset, request):
    asset.updated_by = request.user
    return asset

def query_filter_by_users(qs, data):
    created_by = data.get("created_by")
    if created_by:
        qs = qs.filter(models.Asset.created_by == created_by)

    updated_by = data.get("updated_by")
    if updated_by:
        qs = qs.filter(models.Asset.updated_by == updated_by)
    return qs

## pyramid 
def get_storepath(request):
    return request.registry.settings['altaircms.asset.storepath']

class AssetResource(RootFactory):
    forms = forms
    def add(self, o, flush=False):
        DBSession.add(o)
        if flush:
            DBSession.flush()

    def delete(self, o):
        DBSession.delete(o)

    @reify
    def storepath(self):
        return get_storepath(self.request)

    def display_asset(self, filepath): ## not found imageを表示した方が良い？
        if os.path.exists(filepath):
            return file(filepath).read()
        else:
            return ""

    def __init__(self, request):
        self.request = request

    def get_image_assets(self):
        return self.request.allowable(models.ImageAsset).order_by(sa.desc(models.ImageAsset.id))
    def get_movie_assets(self):
        return self.request.allowable(models.MovieAsset).order_by(sa.desc(models.MovieAsset.id))
    def get_flash_assets(self):
        return self.request.allowable(models.FlashAsset).order_by(sa.desc(models.FlashAsset.id))
    def get_assets_all(self):
        return self.request.allowable(models.Asset).order_by(sa.desc(models.Asset.id))

    def get_image_asset(self, id_):
        return get_or_404(self.request.allowable(models.ImageAsset), models.ImageAsset.id==id_)
    def get_movie_asset(self, id_):
        return get_or_404(self.request.allowable(models.MovieAsset), models.MovieAsset.id==id_)
    def get_flash_asset(self, id_):
        return get_or_404(self.request.allowable(models.FlashAsset), models.FlashAsset.id==id_)
    def get_asset(self, id_):
        return get_or_404(self.request.allowable(models.Asset), models.Asset.id==id_)

    def search_image_asset_by_query(self, data,
                                    _get_search_query=h.image_asset_query_from_search_params):
        qs = self.request.allowable(models.ImageAsset, qs=_get_search_query(data))
        return query_filter_by_users(qs, data)

    def search_movie_asset_by_query(self, data,
                                    _get_search_query=h.movie_asset_query_from_search_params):
        qs = self.request.allowable(models.MovieAsset, qs=_get_search_query(data))
        return query_filter_by_users(qs, data)

    def search_flash_asset_by_query(self, data,
                                    _get_search_query=h.flash_asset_query_from_search_params):
        qs = self.request.allowable(models.FlashAsset, qs=_get_search_query(data))
        return query_filter_by_users(qs, data)
    
    ## delete
    def delete_asset_file(self, assetfile, _delete_file=h.delete_file_if_exist):
        path = os.path.join(self.storepath, assetfile)
        _delete_file(path)

    ## create
    def create_image_asset(self, form,
                           _write_buf=h.write_buf,
                           _get_extra_status=h.get_image_status_extra, 
                           _put_tags=put_tags, 
                           _add_operator=add_operator_when_created):
        
        tags, private_tags, form_params =  h.divide_data(form.data)
        
        params = h.get_asset_params_from_form_data(form_params)
        params.update(_get_extra_status(form_params, form_params["filepath"].file))
        params["filepath"] = h.get_writename(form_params["filepath"].filename)

        params["size"] = _write_buf(self.storepath, params["filepath"], params["buf"])

        asset = models.ImageAsset.from_dict(params)
        _put_tags(asset, "image_asset", tags, private_tags, self.request)
        _add_operator(asset, self.request)
        notify_model_create(self.request, asset, params)
        return asset

    def create_movie_asset(self, form,
                           _write_buf=h.write_buf, 
                           _get_extra_status=h.get_movie_status_extra, 
                           _put_tags=put_tags, 
                           _add_operator=add_operator_when_created):
        tags, private_tags, form_params =  h.divide_data(form.data)

        params = h.get_asset_params_from_form_data(form_params)
        params.update(_get_extra_status(form_params, form_params["filepath"].file))
        params["filepath"] = h.get_writename(form_params["filepath"].filename)

        params["size"] = _write_buf(self.storepath, params["filepath"], params["buf"])

        asset = models.MovieAsset.from_dict(params)
        _put_tags(asset, "movie_asset", tags, private_tags, self.request)
        _add_operator(asset, self.request)
        notify_model_create(self.request, asset, params)
        return asset

    def create_flash_asset(self, form,
                           _write_buf=h.write_buf, 
                           _get_extra_status=h.get_flash_status_extra, 
                           _put_tags=put_tags, 
                           _add_operator=add_operator_when_created):
        tags, private_tags, form_params =  h.divide_data(form.data)

        params = h.get_asset_params_from_form_data(form_params)
        params.update(_get_extra_status(form_params, form_params["filepath"].file))
        params["filepath"] = h.get_writename(form_params["filepath"].filename)

        params["size"] = _write_buf(self.storepath, params["filepath"], params["buf"])

        asset = models.FlashAsset.from_dict(params)
        _put_tags(asset, "flash_asset", tags, private_tags, self.request)
        _add_operator(asset, self.request)
        notify_model_create(self.request, asset, params)
        return asset

    ## update
    def update_image_asset(self, asset, form,
                           _write_buf=h.write_buf,
                           _get_extra_status=h.get_image_status_extra, 
                           _put_tags=put_tags, 
                           _add_operator=add_operator_when_updated):
        tags, private_tags, form_params =  h.divide_data(form.data)

        if  form_params["filepath"] == u"":
            params = form_params
        else:
            params = h.get_asset_params_from_form_data(form_params)
            params.update(_get_extra_status(form_params, form_params["filepath"].file))
            params["filepath"] = h.get_writename(form_params["filepath"].filename)

            params["size"] = _write_buf(self.storepath, params["filepath"], params["buf"])

        _setattrs(asset, params)
        _put_tags(asset, "image_asset", tags, private_tags, self.request)
        _add_operator(asset, self.request)
        return asset


    def update_movie_asset(self, asset, form,
                           _write_buf=h.write_buf,
                           _get_extra_status=h.get_movie_status_extra, 
                           _put_tags=put_tags, 
                           _add_operator=add_operator_when_updated):

        tags, private_tags, form_params =  h.divide_data(form.data)

        if  form_params["filepath"] == u"":
            params = form_params
        else:
            params = h.get_asset_params_from_form_data(form_params)
            params.update(_get_extra_status(form_params, form_params["filepath"].file))
            params["filepath"] = h.get_writename(form_params["filepath"].filename)

            params["size"] = _write_buf(self.storepath, params["filepath"], params["buf"])

        _setattrs(asset, params)
        _put_tags(asset, "movie_asset", tags, private_tags, self.request)
        _add_operator(asset, self.request)
        return asset


    def update_flash_asset(self, asset, form,
                           _write_buf=h.write_buf,
                           _get_extra_status=h.get_flash_status_extra, 
                           _put_tags=put_tags, 
                           _add_operator=add_operator_when_updated):

        tags, private_tags, form_params =  h.divide_data(form.data)

        if  form_params["filepath"] == u"":
            params = form_params
        else:
            params = h.get_asset_params_from_form_data(form_params)
            params.update(_get_extra_status(form_params, form_params["filepath"].file))
            params["filepath"] = h.get_writename(form_params["filepath"].filename)

            params["size"] = _write_buf(self.storepath, params["filepath"], params["buf"])

        _setattrs(asset, params)
        _put_tags(asset, "flash_asset", tags, private_tags, self.request)
        _add_operator(asset, self.request)
        return asset
