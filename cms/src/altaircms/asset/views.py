# coding: utf-8
import os

from altaircms.lib.viewhelpers import FlashMessage
from pyramid.httpexceptions import (
    HTTPFound
)
from pyramid.response import Response
from pyramid.view import (
    view_config, 
    view_defaults
)
from altaircms.lib.fanstatic_decorator import with_bootstrap
from . import helpers as h

@view_defaults(permission="asset_read", decorator=with_bootstrap)
class AssetListView(object):
    def __init__(self, request):
        self.request = request
        self.context = request.context

    @view_config(route_name="asset_list", renderer="altaircms:templates/asset/list.mako", 
                 decorator=with_bootstrap)
    def all_asset_list(self):
        assets = self.request.context.get_assets_all()
        return {"assets": assets, 
                "image_asset_form": self.context.forms.ImageAssetForm(), 
                "movie_asset_form": self.context.forms.MovieAssetForm(), 
                "flash_asset_form": self.context.forms.FlashAssetForm()
                }

    @view_config(route_name="asset_image_list", renderer="altaircms:templates/asset/image/list.mako", 
                 decorator=with_bootstrap)
    def image_asset_list(self):
        assets = self.request.context.get_image_assets()
        form = self.context.forms.ImageAssetForm()
        search_form = self.request.context.forms.AssetSearchForm()
        return {"assets": assets, "form": form, "search_form": search_form}

    @view_config(route_name="asset_movie_list", renderer="altaircms:templates/asset/movie/list.mako", 
                 decorator=with_bootstrap)
    def movie_asset_list(self):
        assets = self.request.context.get_movie_assets()
        form = self.context.forms.MovieAssetForm()
        search_form = self.request.context.forms.AssetSearchForm()
        return {"assets": assets, "form": form, "search_form": search_form}

    @view_config(route_name="asset_flash_list", renderer="altaircms:templates/asset/flash/list.mako", 
                 decorator=with_bootstrap)
    def flash_asset_list(self):
        assets = self.request.context.get_flash_assets()
        form = self.context.forms.FlashAssetForm()
        search_form = self.request.context.forms.AssetSearchForm()
        return {"assets": assets, "form": form, "search_form": search_form}


@view_defaults(permission="asset_read", decorator=with_bootstrap)
class AssetDetailView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name="asset_image_detail", renderer="altaircms:templates/asset/image/detail.mako")
    def image_asset_detail(self):
        asset_id = self.request.matchdict["asset_id"]
        asset = self.request.context.get_image_asset(asset_id)
        return {"asset": asset}

    @view_config(route_name="asset_movie_detail", renderer="altaircms:templates/asset/movie/detail.mako")
    def movie_asset_detail(self):
        asset_id = self.request.matchdict["asset_id"]
        asset = self.request.context.get_movie_asset(asset_id)
        return {"asset": asset}

    @view_config(route_name="asset_flash_detail", renderer="altaircms:templates/asset/flash/detail.mako")
    def flash_asset_detail(self):
        asset_id = self.request.matchdict["asset_id"]
        asset = self.request.context.get_flash_asset(asset_id)
        return {"asset": asset}

@view_defaults(permission="asset_update", decorator=with_bootstrap)
class AssetInputView(object):
    def __init__(self, request):
        self.request = request
        self.context = request.context

    @view_config(route_name="asset_image_input", renderer="altaircms:templates/asset/image/input.mako")
    def image_asset_input(self):
        asset_id = self.request.matchdict["asset_id"]
        asset = self.request.context.get_image_asset(asset_id)

        params = h.get_form_params_from_asset(asset)
        form = self.context.forms.ImageAssetUpdateForm(**params)
        return {"asset": asset, "form": form}

    @view_config(route_name="asset_movie_input", renderer="altaircms:templates/asset/movie/input.mako")
    def movie_asset_input(self):
        asset_id = self.request.matchdict["asset_id"]
        asset = self.request.context.get_movie_asset(asset_id)

        params = h.get_form_params_from_asset(asset)
        form = self.context.forms.MovieAssetUpdateForm(**params)
        return {"asset": asset, "form": form}

    @view_config(route_name="asset_flash_input", renderer="altaircms:templates/asset/flash/input.mako")
    def flash_asset_input(self):
        asset_id = self.request.matchdict["asset_id"]
        asset = self.request.context.get_flash_asset(asset_id)

        params = h.get_form_params_from_asset(asset)
        form = self.context.forms.FlashAssetUpdateForm(**params)
        return {"asset": asset, "form": form}

@view_defaults(permission="asset_update", decorator=with_bootstrap)
class AssetUpdateView(object):
    def __init__(self, request):
        self.request = request
        self.context = request.context

    @view_config(route_name="asset_image_update", request_method="POST")
    def update_image_asset(self):
        form = self.context.forms.ImageAssetUpdateForm(self.request.POST)
        asset_id = self.request.matchdict["asset_id"]
        asset = self.request.context.get_image_asset(asset_id)

        if not form.validate():
            FlashMessage.error(str(form.errors), request=self.request)    
            return HTTPFound(self.request.route_path("asset_image_input", asset_id=asset.id))
        else:
            updated_asset = self.context.update_image_asset(asset, form)
            self.context.add(updated_asset)

            FlashMessage.success("image asset updated", request=self.request)    
            return HTTPFound(self.request.route_path("asset_image_detail", asset_id=updated_asset.id))

    @view_config(route_name="asset_movie_update", request_method="POST")
    def update_movie_asset(self):
        form = self.context.forms.MovieAssetUpdateForm(self.request.POST)
        asset_id = self.request.matchdict["asset_id"]
        asset = self.request.context.get_movie_asset(asset_id)

        if not form.validate():
            FlashMessage.error(str(form.errors), request=self.request)    
            return HTTPFound(self.request.route_path("asset_movie_input", asset_id=asset.id))
        else:

            updated_asset = self.context.update_movie_asset(asset, form)
            self.context.add(updated_asset)

            FlashMessage.success("movie asset updated", request=self.request)    
            return HTTPFound(self.request.route_path("asset_movie_detail", asset_id=updated_asset.id))

    @view_config(route_name="asset_flash_update", request_method="POST")
    def update_flash_asset(self):
        form = self.context.forms.FlashAssetUpdateForm(self.request.POST)
        asset_id = self.request.matchdict["asset_id"]
        asset = self.request.context.get_flash_asset(asset_id)

        if not form.validate():
            FlashMessage.error(str(form.errors), request=self.request)    
            return HTTPFound(self.request.route_path("asset_flash_input", asset_id=asset.id))
        else:

            updated_asset = self.context.update_flash_asset(asset, form)
            self.context.add(updated_asset)

            FlashMessage.success("flash asset updated", request=self.request)    
            return HTTPFound(self.request.route_path("asset_flash_detail", asset_id=updated_asset.id))
        
@view_defaults(permission="asset_create", decorator=with_bootstrap)
class AssetCreateView(object):
    def __init__(self, request):
        self.request = request
        self.context = request.context        

    @view_config(route_name="asset_image_create", renderer="altaircms:templates/asset/image/list.mako", 
                 request_method="POST")
    def create_image_asset(self):
        form = self.context.forms.ImageAssetForm(self.request.POST)

        if not form.validate():
            assets = self.request.context.get_image_assets()
            search_form = self.request.context.forms.AssetSearchForm()
            return {"assets": assets, "form": form, "search_form": search_form}
        else:
            asset = self.context.create_image_asset(form)
            self.context.add(asset)

            FlashMessage.success("image asset created", request=self.request)    
            return HTTPFound(self.request.route_path("asset_image_list"))

    @view_config(route_name="asset_movie_create", renderer="altaircms:templates/asset/movie/list.mako", 
                 request_method="POST")
    def create_movie_asset(self):
        form = self.context.forms.MovieAssetForm(self.request.POST)

        if not form.validate():
            assets = self.request.context.get_movie_assets()
            search_form = self.request.context.forms.AssetSearchForm()
            return {"assets": assets, "form": form, "search_form": search_form}
        else:
            asset = self.context.create_movie_asset(form)
            self.context.add(asset)

            FlashMessage.success("movie asset created", request=self.request)    
            return HTTPFound(self.request.route_path("asset_movie_list"))

    @view_config(route_name="asset_flash_create", renderer="altaircms:templates/asset/flash/list.mako", 
                 request_method="POST")
    def create_flash_asset(self):
        form = self.context.forms.FlashAssetForm(self.request.POST)

        if not form.validate():
            assets = self.request.context.get_flash_assets()
            search_form = self.request.context.forms.AssetSearchForm()
            return {"assets": assets, "form": form, "search_form": search_form}
        else:
            asset = self.context.create_flash_asset(form)
            self.context.add(asset)

            FlashMessage.success("flash asset created", request=self.request)    
            return HTTPFound(self.request.route_path("asset_flash_list"))

@view_defaults(route_name="asset_delete", permission="asset_delete",
               decorator=with_bootstrap)
class AssetDeleteView(object):
    def __init__(self, request):
        self.request = request
        self.context = request.context

    @view_config(route_name="asset_image_delete", request_method="GET", renderer="altaircms:templates/asset/image/delete_confirm.mako")
    def image_delete_confirm(self):
        asset = self.context.get_image_asset(self.request.matchdict["asset_id"])
        return {"asset": asset}
        
    @view_config(route_name="asset_image_delete", request_method="POST")
    def delete_image_asset(self):
        asset = self.context.get_image_asset(self.request.matchdict["asset_id"])

        self.context.delete_asset_file(asset.filepath)
        self.context.delete(asset)

        FlashMessage.success("asset deleted", request=self.request)
        return HTTPFound(self.request.route_path("asset_image_list"))
    
    @view_config(route_name="asset_movie_delete", request_method="GET", renderer="altaircms:templates/asset/movie/delete_confirm.mako")
    def movie_delete_confirm(self):
        asset = self.context.get_movie_asset(self.request.matchdict["asset_id"])
        return {"asset": asset}

    @view_config(route_name="asset_movie_delete", request_method="POST")
    def delete_movie_asset(self):
        asset = self.context.get_movie_asset(self.request.matchdict["asset_id"])

        self.context.delete_asset_file(asset.filepath)
        self.context.delete(asset)

        FlashMessage.success("asset deleted", request=self.request)
        return HTTPFound(self.request.route_path("asset_movie_list"))

    @view_config(route_name="asset_flash_delete", request_method="GET", renderer="altaircms:templates/asset/flash/delete_confirm.mako")
    def flash_delete_confirm(self):
        asset = self.context.get_flash_asset(self.request.matchdict["asset_id"])
        return {"asset": asset}

    @view_config(route_name="asset_flash_delete", request_method="POST")
    def delete_flash_asset(self):
        asset = self.context.get_flash_asset(self.request.matchdict["asset_id"])

        self.context.delete_asset_file(asset.filepath)
        self.context.delete(asset)

        FlashMessage.success("asset deleted", request=self.request)
        return HTTPFound(self.request.route_path("asset_flash_list"))

@view_config(route_name="asset_display", request_method="GET")
def asset_display(request):
    """ display asset as image(image, flash, movie)
    """
    ## todo refactoring
    asset = request.context.get_asset(request.matchdict["asset_id"])

    storepath = request.context.storepath
    filepath = os.path.join(storepath, asset.filepath)
    content_type = asset.mimetype if asset.mimetype else 'application/octet-stream'
    return Response(request.context.display_asset(filepath), content_type=content_type)

### asset search
@view_defaults(permission="asset_read", request_method="GET", 
               decorator=with_bootstrap)
class AssetSearchView(object):
    def __init__(self, request):
        self.request = request
        self.context = request.context 

    @view_config(route_name="asset_search_image", renderer="altaircms:templates/asset/image/search.mako")
    def image_asset_search(self):
        search_form = self.context.forms.AssetSearchForm(self.request.GET)
        if not search_form.validate():
            return HTTPFound(location=self.request.route_url("asset_image_list"))
        search_result = self.context.search_image_asset_by_query(search_form.data)
        return {"search_form": search_form, "search_result": search_result}

    @view_config(route_name="asset_search_movie", renderer="altaircms:templates/asset/movie/search.mako")
    def movie_asset_search(self):
        search_form = self.context.forms.AssetSearchForm(self.request.GET)
        if not search_form.validate():
            return HTTPFound(location=self.request.route_url("asset_movie_list"))
        search_result = self.context.search_movie_asset_by_query(search_form.data)
        return {"search_form": search_form, "search_result": search_result}

    @view_config(route_name="asset_search_flash", renderer="altaircms:templates/asset/flash/search.mako")
    def flash_asset_search(self):
        search_form = self.context.forms.AssetSearchForm(self.request.GET)
        if not search_form.validate():
            return HTTPFound(location=self.request.route_url("asset_flash_list"))
        search_result = self.context.search_flash_asset_by_query(search_form.data)
        return {"search_form": search_form, "search_result": search_result}

