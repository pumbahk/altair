from pyramid.view import view_config
import json

class StructureView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name="structure_create", renderer="json", request_method="POST")
    def create(self):
        raise "create must not occur"

    @view_config(route_name="structure_update", renderer="json", request_method="POST")
    def update(self):
        request = self.request
        pk = request.json_body["page"]
        page = request.context.get_page(pk)
        page.structure = json.dumps(request.json_body["structure"])
        request.context.add(page, flush=True) ## flush?
        return "ok"

    # @view_config(route_name="structure", renderer="json", request_method="DELETE")
    # def delete(self):
    #     print "hor. lay"

    @view_config(route_name="structure_get", renderer="json", request_method="GET")
    def get(self):
        request = self.request
        pk = request.GET["page"]
        page = request.context.get_page(pk)
        if page.structure:
            return dict(loaded=json.loads(page.structure))
        else:
            return dict(loaded=None)

class FreetextWidgetView(object):
    def __init__(self, request):
        self.request = request

    def _create_or_update(self):
        freetext = self.request.json_body["data"]["freetext"]
        context = self.request.context
        widget = context.get_freetext_widget(self.request.json_body.get("pk"))
        widget = context.update_widget(widget, dict(text=freetext))
        context.add(widget, flush=True)

        r = self.request.json_body.copy()
        r.update(pk=widget.id)
        return r

    @view_config(route_name="freetext_widget_create", renderer="json", request_method="POST")
    def create(self):
        return self._create_or_update()

    @view_config(route_name="freetext_widget_update", renderer="json", request_method="POST")
    def update(self):
        return self._create_or_update()

    @view_config(route_name="freetext_widget_delete", renderer="json", request_method="POST")
    def delete(self):
        context = self.request.context
        widget = context.get_freetext_widget(self.request.json_body["pk"])
        context.delete(widget, flush=True)
        return {"status": "ok"}

    @view_config(route_name="freetext_widget_dialog", renderer="/sample/widget/freetext.mak", request_method="GET")
    def dialog(self):
        context = self.request.context
        widget = context.get_freetext_widget(self.request.GET.get("pk"))
        return {"widget": widget}

class ImageWidgetView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name="image_widget_create", renderer="json", request_method="POST")
    def create(self):
        asset_id = self.request.json_body["data"]["asset_id"]
        context = self.request.context
        asset = context.get_image_asset(asset_id);
        widget = context.get_image_widget(self.request.json_body.get("pk"))
        widget = context.update_widget(widget, dict(asset_id=asset_id))
        context.add(widget, flush=True)

        r = self.request.json_body.copy()
        r.update(pk=widget.id, asset_id=asset.id)
        return r

    @view_config(route_name="image_widget_update", renderer="json", request_method="POST")
    def update(self):
        asset_id = self.request.json_body["data"]["asset_id"]
        context = self.request.context
        asset = context.get_image_asset(asset_id);
        widget = context.get_image_widget(self.request.json_body.get("pk"))
        widget = context.update_widget(widget, dict(asset_id=asset_id))
        context.add(widget, flush=True)

        r = self.request.json_body.copy()
        r.update(pk=widget.id, asset_id=asset.id)
        return r

    @view_config(route_name="image_widget_delete", renderer="json", request_method="POST")
    def delete(self):
        context = self.request.context
        widget = context.get_image_widget(self.request.json_body["pk"])
        context.delete(widget, flush=True)
        return {"status": "ok"}

    @view_config(route_name="image_widget_dialog", renderer="/sample/widget/image.mak", request_method="GET")
    def dialog(self):
        image_assets = self.request.context.get_image_asset_query()
        return {"image_assets": image_assets}
