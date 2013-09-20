from pyramid.view import view_config, view_defaults
from altaircms.auth.api import require_login
from . import forms
from altaircms.formhelpers import AlignChoiceField
from webob.multidict import MultiDict
from pyramid.httpexceptions import (
    HTTPFound, 
    HTTPNotFound, 
    HTTPBadRequest
)
import logging
from altaircms import helpers
logger = logging.getLogger(__name__)

@view_defaults(custom_predicates=(require_login,))
class ImageWidgetView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

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
        context = self.context
        widget = context.get_widget(self.request.json_body["pk"])
        context.delete(widget, flush=True)
        return {"status": "ok"}

    @view_config(route_name="image_widget_dialog", renderer="altaircms.plugins.widget:image/dialog.html", request_method="GET")
    def dialog(self):
        service = self.context.fetch_service
        form = service.try_form(self.request.GET, FailureException=HTTPNotFound)
        widget = self.context.widget_repository.get_or_create(form.pk.data)
        assets = service.get_assets_list(widget, form.page.data) #pagination
        max_of_pages = service.max_of_pages(widget)

        params = widget.to_dict()
        params.update(widget.attributes or {})
        setting_form = forms.ImageInfoForm(**AlignChoiceField.normalize_params(params))
        return {"assets": assets, "form": setting_form, "widget": widget, "pk": form.pk.data, "max_of_pages": max_of_pages}

@view_defaults(custom_predicates=(require_login,))
class ImageWidgetAPIView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name="image_widget_fetch", renderer="altaircms.plugins.widget:image/fetch.html", request_method="GET")
    def fetch(self):
        service = self.context.fetch_service
        form = service.try_form(self.request.GET, FailureException=HTTPNotFound)
        widget = self.context.widget_repository.get_or_create(form.pk.data)
        assets = service.get_assets_list(widget, form.page.data) #pagination
        return {"assets": assets, "widget": widget, "pk": form.pk.data}

    @view_config(route_name="image_widget_search_first", renderer="altaircms.plugins.widget:image/scrollable.html", request_method="POST")
    def search_first(self):
        service = self.context.search_service
        form = service.try_form(self.request.POST, FailureException=HTTPBadRequest)
        widget = self.context.widget_repository.get_or_create(form.pk.data)
        assets = service.get_assets_list(widget, form.search_word.data, form.page.data) #pagination
        max_of_pages = service.max_of_pages(widget, form.search_word.data)
        return {"assets": assets, "widget": widget, "pk": form.pk.data, "max_of_pages": max_of_pages}

    @view_config(route_name="image_widget_search", renderer="altaircms.plugins.widget:image/fetch.html", request_method="GET")
    def search(self):
        service = self.context.search_service
        form = service.try_form(self.request.GET, FailureException=HTTPBadRequest)
        widget = self.context.widget_repository.get_or_create(form.pk.data)
        assets = service.get_assets_list(widget, form.search_word.data, form.page.data) #pagination
        return {"assets": assets, "widget": widget, "pk": form.pk.data}

    @view_config(route_name="image_widget_tag_search_first", renderer="altaircms.plugins.widget:image/scrollable.html", request_method="POST")
    def tag_search_first(self):
        service = self.context.tagsearch_service
        form = service.try_form(self.request.POST, FailureException=HTTPBadRequest)
        widget = self.context.widget_repository.get_or_create(form.pk.data)
        redirect_to = lambda : HTTPFound(location=self.request.route_url("asset_image_list"))
        assets = service.get_assets_list(widget, form.tags.data, redirect_to, form.page.data) #pagination
        max_of_pages = service.max_of_pages(widget, form.tags.data, redirect_to)
        return {"assets": assets, "widget": widget, "pk": form.pk.data, "max_of_pages": max_of_pages}

    @view_config(route_name="image_widget_tag_search", renderer="altaircms.plugins.widget:image/fetch.html", request_method="GET")
    def tag_search(self):
        service = self.context.tagsearch_service
        form = service.try_form(self.request.GET, FailureException=HTTPBadRequest)
        widget = self.context.widget_repository.get_or_create(form.pk.data)
        redirect_to = lambda : HTTPFound(location=self.request.route_url("asset_image_list"))
        assets = service.get_assets_list(widget, form.tags.data, redirect_to, form.page.data) #pagination
        return {"assets": assets, "widget": widget, "pk": form.pk.data}


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
