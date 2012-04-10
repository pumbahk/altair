from pyramid.view import view_config
from altaircms.lib.itertools import group_by_n


class ImageWidgetView(object):
    def __init__(self, request):
        self.request = request

    def _create_or_update(self):
        asset_id = self.request.json_body["data"]["asset_id"]
        nowrap = self.request.json_body["data"].get("nowrap")
        alt = self.request.json_body["data"].get("alt")
        href = self.request.json_body["data"].get("href")
        page_id = self.request.json_body["page_id"]
        context = self.request.context
        asset = context.get_asset(asset_id);
        widget = context.get_widget(self.request.json_body.get("pk"))
        widget = context.update_data(widget, page_id=page_id, asset_id=asset_id, nowrap=nowrap, alt=alt, href=href)
        context.add(widget, flush=True)

        r = self.request.json_body.copy()
        r.update(pk=widget.id, asset_id=asset.id)
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

    @view_config(route_name="image_widget_dialog", renderer="altaircms.plugins.widget:image/dialog.mako", request_method="GET")
    def dialog(self):
        N = 5
        assets = group_by_n(self.request.context.get_asset_query(), N)
        return {"assets": assets}
