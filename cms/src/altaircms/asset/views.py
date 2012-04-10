# coding: utf-8
import os
from altaircms.lib.viewhelpers import FlashMessage
from pyramid.exceptions import NotFound
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.view import view_defaults
from altaircms.lib.fanstatic_decorator import with_bootstrap
import altaircms.lib.treat.api as treat

@view_config(route_name="asset_list", renderer="altaircms:templates/asset/list.mako", 
             decorator=with_bootstrap)
def list(request):
    assets = request.context.get_assets()
    form_list = request.context.get_form_list()
    return {"assets": assets, "form_list": form_list}

@view_config(route_name="asset_view", renderer='altaircms:templates/asset/view.mako', 
             decorator=with_bootstrap, request_method='GET')
def view(request):
    if not "asset_id" in request.matchdict:
        return NotFound()
    asset = request.context.get_asset(request.matchdict["asset_id"])
    return {"asset": asset}

@view_defaults(route_name="asset_delete", permission="asset_delete", decorator=with_bootstrap)
class DeleteView(object):
    def __init__(self, request):
        self.request = request

    @view_config(request_method="GET", renderer="altaircms:templates/asset/delete_confirm.mako")
    def confirm(self):
        asset = self.request.context.get_asset(self.request.matchdict["asset_id"])
        return {"asset": asset}

    @view_config(request_method="POST", renderer="altaircms:templates/asset/delete_confirm.mako")
    def execute(self):
        # 削除処理
        context = self.request.context
        asset = context.get_asset(self.request.matchdict["asset_id"])
        storepath = context.get_asset_storepath()
        context.delete_asset_file(storepath, asset.filepath)
        asset = self.request.context.get_asset(self.request.matchdict["asset_id"])
        self.request.context.DBSession.delete(asset)
        FlashMessage.success("asset deleted", request=self.request)
        return HTTPFound(self.request.route_path("asset_list"))
    
@view_defaults(route_name="asset_create", permission="asset_create", decorator=with_bootstrap)
class CreateView(object):
    def __init__(self, request):
        self.request = request

    # @view_config(request_method="GET", renderer="altaircms:templates/asset/create_confirm.mako")
    # def confirm(self):
    #     form = self.request.context.get_form(data=self.request.GET)
    #     return {"form": form}

    @view_config(request_method="POST")
    def execute(self):
        context = self.request.context
        asset_type = self.request.matchdict["asset_type"]
        form = context.get_confirm_form(asset_type, data=self.request.POST)
        if form.validate():
            asset = treat.get_creator(form, "asset", request=self.request).create()
            self.request.context.DBSession.add(asset)
            FlashMessage.success("%s asset created" % asset_type, request=self.request)    
        else:
            FlashMessage.error(str(form.errors), request=self.request)    
        return HTTPFound(self.request.route_path("asset_list"))

@view_config(route_name="asset_display", permission="asset_read", request_method="GET")
def asset_display(request):
    """ display asset as image(image, flash, movie)
    """
    ## todo refactoring
    asset = request.context.get_asset(request.matchdict["asset_id"])

    attr = request.GET.get("filepath") or "filepath"
    filepath = getattr(asset, attr)
    storepath = request.context.get_asset_storepath()
    filepath = os.path.join(storepath, filepath)
    content_type = asset.mimetype if asset.mimetype else 'application/octet-stream'
    if os.path.exists(filepath):
        return Response(file(filepath).read(), content_type=content_type)
    else:
        return Response("", content_type=content_type)
