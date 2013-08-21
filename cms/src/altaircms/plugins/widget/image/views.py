from pyramid.view import view_config, view_defaults
from altaircms.auth.api import require_login
from altaircms.asset.models import ImageAsset
from altaircms.asset import creation
from altaircms.lib.itertools import group_by_n
from . import forms
from altaircms.formhelpers import AlignChoiceField
from webob.multidict import MultiDict
from pyramid.httpexceptions import (
    HTTPFound
)
import logging
from altaircms import helpers
import json
logger = logging.getLogger(__name__)

@view_defaults(custom_predicates=(require_login,))
class ImageWidgetView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.N = 4

    def _create_or_update(self):
        try:
            form = forms.ImageInfoForm(MultiDict(self.request.json_body["data"], page_id=self.request.json_body["page_id"]))
            if not form.validate():
                logger.warn(str(form.errors))
                r = self.request.json_body.copy()
                r.update(pk=None, asset_id=None)
                return r
            params = form.data
            widget = self.context.get_widget(self.request.json_body.get("pk"))
            params["asset_id"] = form.data.get("asset_id")
            if widget and params.get("asset_id") is None:
                params["asset_id"] = widget.asset_id
            widget = self.context.update_data(widget, **params)
            self.context.add(widget, flush=True)

            r = self.request.json_body.copy()
            r.update(pk=widget.id, asset_id=widget.asset_id)
            return r
        except Exception, e:
            logger.exception(str(e))
            r = self.request.json_body.copy()
            r.update(pk=None, asset_id=None)
            return r

    @view_config(route_name="image_widget_create", renderer="json", request_method="POST")        
    def create(self):
        return self._create_or_update()

    @view_config(route_name="image_widget_update", renderer="json", request_method="POST")        
    def update(self):
        return self._create_or_update()

    @view_config(route_name="image_widget_delete", renderer="json", request_method="POST")        
    def delete(self):
        context = self.request.context
        widget = context.get_widget(self.request.json_body["pk"])
        context.delete(widget, flush=True)
        return {"status": "ok"}

    @view_config(route_name="image_widget_dialog", renderer="altaircms.plugins.widget:image/dialog.html", request_method="GET")
    def dialog(self):
        assets = group_by_n(self.request.context.get_asset_query(), self.N)
        pk = self.request.GET.get("pk")
        widget = self.request.context.get_widget(pk)

        if widget.width == 0:
            widget.width = ""
        if widget.height == 0:
            widget.height = ""
        params = widget.to_dict()
        params.update(widget.attributes or {})      
        form = forms.ImageInfoForm(**AlignChoiceField.normalize_params(params))
        return {"assets": assets, "form": form, "widget": widget, "pk": pk}


    @view_config(route_name="image_widget_search", renderer="json", request_method="POST")
    def search(self):
        pk = self.request.POST['pk'] if self.request.POST['pk'] != "None" else None
        search_word = self.request.POST['search_word']

        assets = None
        if search_word:
            assets = group_by_n(self.request.context.search_asset(search_word), self.N)
        else:
            assets = group_by_n(self.request.context.get_asset_query(), self.N)

        assets_dict = create_search_result(self.request, assets)
        widget = self.request.context.get_widget(pk) if pk else None
        asset_id = widget.asset_id if widget else None

        return {
            'widget_asset_id': asset_id,
            'assets_data': assets_dict
        }

    @view_config(route_name="image_widget_tag_search", renderer="json", request_method="POST")
    def tag_search(self):
        pk = self.request.POST['pk'] if self.request.POST['pk'] != "None" else None
        tags = self.request.POST['tags']
        try:
            assets = self.request.allowable(ImageAsset)
            search_result = creation.ImageSearcher(self.request).search(assets, {'tags':tags})
        except Exception, e:
            logger.exception(e.message.encode("utf-8"))
            return HTTPFound(location=self.request.route_url("asset_image_list"))

        assets = group_by_n(search_result, self.N)

        assets_dict = create_search_result(self.request, assets)
        widget = self.request.context.get_widget(pk) if pk else None
        asset_id = widget.asset_id if widget else None

        return {
            'widget_asset_id': asset_id,
            'assets_data': assets_dict
        }

def create_search_result(request, assets):
    assets_dict = {}
    for groupNo, group in enumerate(assets):
        img_list = []
        for img in group:
            img_info = {
                "id":img.id ,
                "title":img.title ,
                "width":img.width ,
                "height":img.height ,
                "thumbnail_path":helpers.asset.rendering_object(request,img).thumbnail_path
            }
            img_list.append(img_info)
        assets_dict.update({groupNo:img_list})
    return assets_dict
