from pyramid.view import view_config, view_defaults
from altaircms.auth.api import require_login
from . import forms

@view_defaults(custom_predicates=(require_login,))
class TopcontentWidgetView(object):
    def __init__(self, request):
        self.request = request

    def _create_or_update(self):
        data = self.request.json_body["data"]
        if data.get("subkind") == "None": #fixme
            data["subkind"] = None
        page_id = self.request.json_body["page_id"]
        context = self.request.context
        widget = context.get_widget(self.request.json_body.get("pk"))
        widget = context.update_data(widget,
                                     page_id=page_id, 
                                     **data)
        context.add(widget, flush=True)
        r = self.request.json_body.copy()
        r.update(pk=widget.id)
        return r

    @view_config(route_name="topcontent_widget_create", renderer="json", request_method="POST")
    def create(self):
        return self._create_or_update()

    @view_config(route_name="topcontent_widget_update", renderer="json", request_method="POST")
    def update(self):
        return self._create_or_update()

    @view_config(route_name="topcontent_widget_delete", renderer="json", request_method="POST")
    def delete(self):
        context = self.request.context
        widget = context.get_widget(self.request.json_body["pk"])
        context.delete(widget, flush=True)
        return {"status": "ok"}

    @view_config(route_name="topcontent_widget_dialog", renderer="altaircms.plugins.widget:topcontent/dialog.html", request_method="GET")
    def dialog(self):
        context = self.request.context
        widget = context.get_widget(self.request.GET.get("pk"))
        form = forms.TopcontentChoiceForm(**widget.to_dict())
        form.configure(self.request)
        # form.transform(widget.topcontent_type)
        return {"form": form}

    # @view_config(route_name="topcontent_widget_dialog_form", renderer="altaircms.plugins.widget:topcontent/form.html", request_method="GET")
    # def dialog_form(self):
    #     form = forms.TopcontentChoiceForm(self.request.GET)
    #     form.transform(self.request.GET["topcontent_type"])
    #     return {"form": form}
