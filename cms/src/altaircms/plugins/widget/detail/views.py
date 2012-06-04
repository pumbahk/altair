from pyramid.view import view_config
from . forms import DetailSelectForm

class DetailWidgetView(object):
    def __init__(self, request):
        self.request = request

    def _create_or_update(self):
        page_id = self.request.json_body["page_id"]
        kind = self.request.json_body["data"]["kind"]
        context = self.request.context
        widget = context.get_widget(self.request.json_body.get("pk"))
        widget = context.update_data(widget, page_id=page_id, kind=kind)
        context.add(widget, flush=True)

        r = self.request.json_body.copy()
        r.update(pk=widget.id)
        return r

    @view_config(route_name="detail_widget_create", renderer="json", request_method="POST")
    def create(self):
        return self._create_or_update()

    @view_config(route_name="detail_widget_update", renderer="json", request_method="POST")
    def update(self):
        return self._create_or_update()

    @view_config(route_name="detail_widget_delete", renderer="json", request_method="POST")
    def delete(self):
        context = self.request.context
        widget = context.get_widget(self.request.json_body["pk"])
        context.delete(widget, flush=True)
        return {"status": "ok"}

    @view_config(route_name="detail_widget_dialog", renderer="altaircms.plugins.widget:detail/dialog.mako", request_method="GET")
    def dialog(self):
        context = self.request.context
        D = {"form_class": DetailSelectForm}
        widget = context.get_widget(self.request.GET.get("pk"))
        return context.attach_form_from_widget(D, widget)
