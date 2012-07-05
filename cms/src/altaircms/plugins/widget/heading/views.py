from pyramid.view import view_config, view_defaults
from altaircms.auth.api import require_login
from . import forms
@view_defaults(custom_predicates=(require_login,))
class HeadingWidgetView(object):
    def __init__(self, request):
        self.request = request

    def _create_or_update(self):
        data = self.request.json_body["data"]
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

    @view_config(route_name="heading_widget_create", renderer="json", request_method="POST")
    def create(self):
        return self._create_or_update()

    @view_config(route_name="heading_widget_update", renderer="json", request_method="POST")
    def update(self):
        return self._create_or_update()

    @view_config(route_name="heading_widget_delete", renderer="json", request_method="POST")
    def delete(self):
        context = self.request.context
        widget = context.get_widget(self.request.json_body["pk"])
        context.delete(widget, flush=True)
        return {"status": "ok"}

    @view_config(route_name="heading_widget_dialog", renderer="altaircms.plugins.widget:heading/dialog.mako", request_method="GET")
    def dialog(self):
        context = self.request.context
        widget = context.get_widget(self.request.GET.get("pk"))
        form = forms.HeadingForm(**widget.to_dict())
        return {"widget": widget, "form": form}

@view_config(route_name="api_heading_title", renderer="json")
def api_heading_title(request):
    from altaircms.page.models import Page
    page = Page.query.filter_by(id=request.GET.get("page")).first()

    if page:
        return {"name": page.name}
    else:
        return {"name": ""}
