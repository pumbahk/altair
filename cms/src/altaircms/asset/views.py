# coding: utf-8

import sqlalchemy as sa
import logging
logger = logging.getLogger(__name__)
from altaircms.helpers.viewhelpers import FlashMessage
from pyramid.httpexceptions import (
    HTTPFound
)

from pyramid.view import (
    view_config, 
    view_defaults
)
from altaircms.lib.fanstatic_decorator import with_bootstrap

from . import models
from . import forms
from altaircms.helpers.viewhelpers import get_endpoint
from altaircms.auth.api import get_or_404
from . import creation
from . import ValidationError

@view_defaults(permission="asset_create", decorator=with_bootstrap, route_name="asset_add")
class AssetAddView(object):
    def __init__(self, context, request):
        self.request = request
        self.context = context        

    @view_config(match_param="kind=image", renderer="altaircms:templates/asset/image/add.html", 
                 request_method="GET")
    def add_image_asset_input(self):
        private_tags = self.request.params.get("private_tags", "")
        form = forms.ImageAssetForm(private_tags=private_tags)
        return {"form": form}

@view_defaults(permission="asset_read", decorator=with_bootstrap)
class AssetListView(object):
    def __init__(self, context, request):
        self.request = request
        self.context = context

    @view_config(route_name="asset_list", renderer="altaircms:templates/asset/list.html", 
                 decorator=with_bootstrap)
    def all_asset_list(self):
        assets = self.request.allowable(models.Asset).order_by(sa.desc(models.Asset.updated_at), sa.desc(models.Asset.id))
        return {"assets": assets, 
                "image_asset_form": forms.ImageAssetForm(), 
                "movie_asset_form": forms.MovieAssetForm(), 
                "flash_asset_form": forms.FlashAssetForm()
                }

    @view_config(route_name="asset_image_list", renderer="altaircms:templates/asset/image/list.html", 
                 decorator=with_bootstrap)
    def image_asset_list(self):
        assets = self.request.allowable(models.ImageAsset).order_by(sa.desc(models.ImageAsset.updated_at), sa.desc(models.ImageAsset.id))
        form = forms.ImageAssetForm()
        search_form = forms.AssetSearchForm()
        return {"assets": assets, "form": form, "search_form": search_form}

    @view_config(route_name="asset_movie_list", renderer="altaircms:templates/asset/movie/list.html", 
                 decorator=with_bootstrap)
    def movie_asset_list(self):
        assets = self.request.allowable(models.MovieAsset).order_by(sa.desc(models.MovieAsset.updated_at), sa.desc(models.MovieAsset.id))
        form = forms.MovieAssetForm()
        search_form = forms.AssetSearchForm()
        return {"assets": assets, "form": form, "search_form": search_form}

    @view_config(route_name="asset_flash_list", renderer="altaircms:templates/asset/flash/list.html", 
                 decorator=with_bootstrap)
    def flash_asset_list(self):
        assets = self.request.allowable(models.FlashAsset).order_by(sa.desc(models.FlashAsset.updated_at), sa.desc(models.FlashAsset.id))
        form = forms.FlashAssetForm()
        search_form = forms.AssetSearchForm()
        return {"assets": assets, "form": form, "search_form": search_form}


@view_defaults(permission="asset_read", decorator=with_bootstrap)
class AssetDetailView(object):
    def __init__(self, context, request):
        self.request = request

    @view_config(route_name="asset_image_detail", renderer="altaircms:templates/asset/image/detail.html")
    def image_asset_detail(self):
        asset_id = self.request.matchdict["asset_id"]
        asset = get_or_404(self.request.allowable(models.ImageAsset), models.ImageAsset.id==asset_id)
        return {"asset": asset}

    @view_config(route_name="asset_movie_detail", renderer="altaircms:templates/asset/movie/detail.html")
    def movie_asset_detail(self):
        asset_id = self.request.matchdict["asset_id"]
        asset = get_or_404(self.request.allowable(models.MovieAsset), models.MovieAsset.id==asset_id)
        return {"asset": asset}

    @view_config(route_name="asset_flash_detail", renderer="altaircms:templates/asset/flash/detail.html")
    def flash_asset_detail(self):
        asset_id = self.request.matchdict["asset_id"]
        asset = get_or_404(self.request.allowable(models.FlashAsset), models.FlashAsset.id==asset_id)
        return {"asset": asset}

@view_defaults(permission="asset_update", decorator=with_bootstrap)
class AssetInputView(object):
    def __init__(self, context, request):
        self.request = request
        self.context = context

    @view_config(route_name="asset_image_input", renderer="altaircms:templates/asset/image/input.html")
    def image_asset_input(self):
        asset_id = self.request.matchdict["asset_id"]
        asset = get_or_404(self.request.allowable(models.ImageAsset), models.ImageAsset.id==asset_id)
        form = creation.Input(self.request).on_update(asset, forms.ImageAssetUpdateForm)
        return {"asset": asset, "form": form}

    @view_config(route_name="asset_movie_input", renderer="altaircms:templates/asset/movie/input.html")
    def movie_asset_input(self):
        asset_id = self.request.matchdict["asset_id"]
        asset = get_or_404(self.request.allowable(models.MovieAsset), models.MovieAsset.id==asset_id)
        form = creation.Input(self.request).on_update(asset, forms.MovieAssetUpdateForm)
        return {"asset": asset, "form": form}

    @view_config(route_name="asset_flash_input", renderer="altaircms:templates/asset/flash/input.html")
    def flash_asset_input(self):
        asset_id = self.request.matchdict["asset_id"]
        asset = get_or_404(self.request.allowable(models.FlashAsset), models.FlashAsset.id==asset_id)
        form = creation.Input(self.request).on_update(asset, forms.FlashAssetUpdateForm)
        return {"asset": asset, "form": form}

@view_defaults(permission="asset_update", decorator=with_bootstrap)
class AssetUpdateView(object):
    def __init__(self, context, request):
        self.request = request
        self.context = context

    @view_config(route_name="asset_image_update", request_method="POST")
    def update_image_asset(self):
        form = forms.ImageAssetUpdateForm(self.request.POST)
        asset_id = self.request.matchdict["asset_id"]
        asset = get_or_404(self.request.allowable(models.ImageAsset), models.ImageAsset.id==asset_id)

        try:
            updater = creation.ImageUpdater(self.request).update(asset, form.data, form=form)
            asset = updater.commit()
            FlashMessage.success("image asset updated", request=self.request)    
            return HTTPFound(self.request.route_path("asset_image_detail", asset_id=asset.id))
        except ValidationError, e:
            logger.info(repr(e))
            FlashMessage.error(e.message, request=self.request)    
            return HTTPFound(self.request.route_path("asset_image_input", asset_id=asset.id))
        except Exception, e:
            logger.exception(e.message.encode("utf-8"))
            FlashMessage.error(e.message, request=self.request)    
            return HTTPFound(self.request.route_path("asset_image_input", asset_id=asset.id))

    @view_config(route_name="asset_movie_update", request_method="POST")
    def update_movie_asset(self):
        form = forms.MovieAssetUpdateForm(self.request.POST)
        asset_id = self.request.matchdict["asset_id"]
        asset = get_or_404(self.request.allowable(models.MovieAsset), models.MovieAsset.id==asset_id)

        try:
            updater = creation.MovieUpdater(self.request).update(asset, form.data, form=form)
            asset = updater.commit()
            FlashMessage.success("movie asset updated", request=self.request)    
            return HTTPFound(self.request.route_path("asset_movie_detail", asset_id=asset.id))
        except ValidationError, e:
            logger.info(repr(e))
            FlashMessage.error(e.message, request=self.request)    
            return HTTPFound(self.request.route_path("asset_movie_input", asset_id=asset.id))
        except Exception, e:
            logger.exception(e.message.encode("utf-8"))
            FlashMessage.error(e.message, request=self.request)    
            return HTTPFound(self.request.route_path("asset_movie_input", asset_id=asset.id))

    @view_config(route_name="asset_flash_update", request_method="POST")
    def update_flash_asset(self):
        form = forms.FlashAssetUpdateForm(self.request.POST)
        asset_id = self.request.matchdict["asset_id"]
        asset = get_or_404(self.request.allowable(models.FlashAsset), models.FlashAsset.id==asset_id)

        try:
            updater = creation.FlashUpdater(self.request).update(asset, form.data, form=form)
            asset = updater.commit()
            FlashMessage.success("flash asset updated", request=self.request)    
            return HTTPFound(self.request.route_path("asset_flash_detail", asset_id=asset.id))
        except ValidationError, e:
            logger.info(repr(e))
            FlashMessage.error(e.message, request=self.request)    
            return HTTPFound(self.request.route_path("asset_flash_input", asset_id=asset.id))
        except Exception, e:
            logger.exception(e.message.encode("utf-8"))
            FlashMessage.error(e.message, request=self.request)    
            return HTTPFound(self.request.route_path("asset_flash_input", asset_id=asset.id))
        
@view_defaults(permission="asset_create", decorator=with_bootstrap)
class AssetCreateView(object):
    def __init__(self, context, request):
        self.request = request
        self.context = context        

    @view_config(route_name="asset_image_create", renderer="altaircms:templates/asset/image/list.html", 
                 request_method="POST")
    def create_image_asset(self):
        form = forms.ImageAssetForm(self.request.POST)

        try:
            creator = creation.ImageCreator(self.request).create(form.data, form=form)
            creator.commit()
            FlashMessage.success("image asset created", request=self.request)    
            return HTTPFound(get_endpoint(self.request) or  self.request.route_path("asset_image_list"))
        except ValidationError, e:
            FlashMessage.error(e.message, request=self.request)    
            assets = self.request.allowable(models.ImageAsset).order_by(sa.desc(models.ImageAsset.id))
            search_form = forms.AssetSearchForm()
            return {"assets": assets, "form": form, "search_form": search_form}
        except Exception, e:
            logger.exception(e.message.encode("utf-8"))
            FlashMessage.error(e.message, request=self.request)    
            assets = self.request.allowable(models.ImageAsset).order_by(sa.desc(models.ImageAsset.id))
            search_form = forms.AssetSearchForm()
            return {"assets": assets, "form": form, "search_form": search_form}

    @view_config(route_name="asset_movie_create", renderer="altaircms:templates/asset/movie/list.html", 
                 request_method="POST")
    def create_movie_asset(self):
        form = forms.MovieAssetForm(self.request.POST)

        try:
            creator = creation.MovieCreator(self.request).create(form.data, form=form)
            creator.commit()
            FlashMessage.success("movie asset created", request=self.request)    
            return HTTPFound(get_endpoint(self.request) or  self.request.route_path("asset_movie_list"))
        except ValidationError, e:
            FlashMessage.error(e.message, request=self.request)    
            assets = self.request.allowable(models.MovieAsset).order_by(sa.desc(models.MovieAsset.id))
            search_form = forms.AssetSearchForm()
            return {"assets": assets, "form": form, "search_form": search_form}
        except Exception, e:
            logger.exception(e.message.encode("utf-8"))
            FlashMessage.error(e.message, request=self.request)    
            assets = self.request.allowable(models.MovieAsset).order_by(sa.desc(models.MovieAsset.id))
            search_form = forms.AssetSearchForm()
            return {"assets": assets, "form": form, "search_form": search_form}

    @view_config(route_name="asset_flash_create", renderer="altaircms:templates/asset/flash/list.html", 
                 request_method="POST")
    def create_flash_asset(self):
        form = forms.FlashAssetForm(self.request.POST)

        try:
            creator = creation.FlashCreator(self.request).create(form.data, form=form)
            creator.commit()
            FlashMessage.success("flash asset created", request=self.request)    
            return HTTPFound(get_endpoint(self.request) or  self.request.route_path("asset_flash_list"))
        except ValidationError, e:
            FlashMessage.error(e.message, request=self.request)    
            assets = self.request.allowable(models.FlashAsset).order_by(sa.desc(models.FlashAsset.id))
            search_form = forms.AssetSearchForm()
            return {"assets": assets, "form": form, "search_form": search_form}
        except Exception, e:
            logger.exception(e.message.encode("utf-8"))
            FlashMessage.error(e.message, request=self.request)    
            assets = self.request.allowable(models.FlashAsset).order_by(sa.desc(models.FlashAsset.id))
            search_form = forms.AssetSearchForm()
            return {"assets": assets, "form": form, "search_form": search_form}


@view_defaults(route_name="asset_delete", permission="asset_delete",
               decorator=with_bootstrap)
class AssetDeleteView(object):
    def __init__(self, context, request):
        self.request = request
        self.context = context

    @view_config(route_name="asset_image_delete", request_method="GET", renderer="altaircms:templates/asset/image/delete_confirm.html")
    def image_delete_confirm(self):
        asset_id = self.request.matchdict["asset_id"]
        asset = get_or_404(self.request.allowable(models.ImageAsset), models.ImageAsset.id==asset_id)
        return {"asset": asset}
        
    @view_config(route_name="asset_image_delete", request_method="POST")
    def delete_image_asset(self):
        asset_id = self.request.matchdict["asset_id"]
        asset = get_or_404(self.request.allowable(models.ImageAsset), models.ImageAsset.id==asset_id)
        creation.Deleter(self.request).delete(asset)
        FlashMessage.success("asset deleted", request=self.request)
        return HTTPFound(self.request.route_path("asset_image_list"))
    
    @view_config(route_name="asset_movie_delete", request_method="GET", renderer="altaircms:templates/asset/movie/delete_confirm.html")
    def movie_delete_confirm(self):
        asset_id = self.request.matchdict["asset_id"]
        asset = get_or_404(self.request.allowable(models.MovieAsset), models.MovieAsset.id==asset_id)
        return {"asset": asset}

    @view_config(route_name="asset_movie_delete", request_method="POST")
    def delete_movie_asset(self):
        asset_id = self.request.matchdict["asset_id"]
        asset = get_or_404(self.request.allowable(models.MovieAsset), models.MovieAsset.id==asset_id)
        creation.Deleter(self.request).delete(asset)
        FlashMessage.success("asset deleted", request=self.request)
        return HTTPFound(self.request.route_path("asset_movie_list"))

    @view_config(route_name="asset_flash_delete", request_method="GET", renderer="altaircms:templates/asset/flash/delete_confirm.html")
    def flash_delete_confirm(self):
        asset_id = self.request.matchdict["asset_id"]
        asset = get_or_404(self.request.allowable(models.FlashAsset), models.FlashAsset.id==asset_id)
        return {"asset": asset}

    @view_config(route_name="asset_flash_delete", request_method="POST")
    def delete_flash_asset(self):
        asset_id = self.request.matchdict["asset_id"]
        asset = get_or_404(self.request.allowable(models.FlashAsset), models.FlashAsset.id==asset_id)
        creation.Deleter(self.request).delete(asset)
        FlashMessage.success("asset deleted", request=self.request)
        return HTTPFound(self.request.route_path("asset_flash_list"))

@view_config(route_name="asset_display", request_method="GET")
def asset_display(request):
    """ display asset as image(image, flash, movie)
    """
    ## todo refactoring
    asset_id = request.matchdict["asset_id"]
    asset = get_or_404(request.allowable(models.Asset), models.Asset.id==asset_id)
    return creation.Display(request).as_response(asset)

### asset search
@view_defaults(permission="asset_read", request_method="GET", 
               decorator=with_bootstrap)
class AssetSearchView(object):
    def __init__(self, context, request):
        self.request = request
        self.context = request

    @view_config(route_name="asset_search_image", renderer="altaircms:templates/asset/image/search.html")
    def image_asset_search(self):
        search_form = forms.AssetSearchForm(self.request.GET)
        try:
            assets = self.request.allowable(models.ImageAsset)
            search_result = creation.ImageSearcher(self.request).search(assets, search_form.data)
            return {"search_form": search_form, "search_result": search_result}
        except Exception, e:
            logger.exception(e.message.encode("utf-8"))
            HTTPFound(location=self.request.route_url("asset_image_list"))

    @view_config(route_name="asset_search_movie", renderer="altaircms:templates/asset/movie/search.html")
    def movie_asset_search(self):
        search_form = forms.AssetSearchForm(self.request.GET)
        try:
            search_result = creation.MovieSearcher(self.request).search(search_form.data, form=search_form)
            return {"search_form": search_form, "search_result": search_result}
        except Exception, e:
            logger.exception(e.message.encode("utf-8"))
            HTTPFound(location=self.request.route_url("asset_movie_list"))

    @view_config(route_name="asset_search_flash", renderer="altaircms:templates/asset/flash/search.html")
    def flash_asset_search(self):
        search_form = forms.AssetSearchForm(self.request.GET)
        try:
            search_result = creation.FlashSearcher(self.request).search(search_form.data, form=search_form)
            return {"search_form": search_form, "search_result": search_result}
        except Exception, e:
            logger.exception(e.message.encode("utf-8"))
            HTTPFound(location=self.request.route_url("asset_flash_list"))
