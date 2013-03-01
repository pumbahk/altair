from pyramid.view import view_config, view_defaults
from altaircms.auth.api import require_login
from altaircms.lib.itertools import group_by_n
from . import forms

@view_defaults(custom_predicates=(require_login,))
class FlashWidgetView(object):
    def __init__(self, request):
        self.request = request

    def _create_or_update(self):
        asset_id = self.request.json_body["data"].get("asset_id")
        if asset_id is None:
            r = self.request.json_body.copy()
            r.update(pk=None, asset_id=None)
            return r

        alt = self.request.json_body["data"].get("alt")
        width = self.request.json_body["data"].get("width")
        height = self.request.json_body["data"].get("height")
        page_id = self.request.json_body["page_id"]
        context = self.request.context
        asset = context.get_asset(asset_id);
        widget = context.get_widget(self.request.json_body.get("pk"))
        widget = context.update_data(widget, page_id=page_id, asset_id=asset_id, asset=asset, alt=alt, width=width, height=height)
        context.add(widget, flush=True)

        r = self.request.json_body.copy()
        r.update(pk=widget.id, asset_id=asset.id)
        return r

    @view_config(route_name="flash_widget_create", renderer="json", request_method="POST")        
    def create(self):
        return self._create_or_update()

    @view_config(route_name="flash_widget_update", renderer="json", request_method="POST")        
    def update(self):
        return self._create_or_update()

    @view_config(route_name="flash_widget_delete", renderer="json", request_method="POST")        
    def delete(self):
        context = self.request.context
        widget = context.get_widget(self.request.json_body["pk"])
        context.delete(widget, flush=True)
        return {"status": "ok"}

    @view_config(route_name="flash_widget_dialog", renderer="altaircms.plugins.widget:flash/dialog.html", request_method="GET")
    def dialog(self):
        N = 5
        assets = group_by_n(self.request.context.get_asset_query(), N)
        widget = self.request.context.get_widget(self.request.GET.get("pk"))
        if widget.width == 0:
            widget.width = ""
        if widget.height == 0:
            widget.height = ""
        form = forms.FlashInfoForm(**widget.to_dict())
        return {"assets": assets, "form": form, "widget": widget}
