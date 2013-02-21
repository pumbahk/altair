from pyramid.view import view_config, view_defaults
from altaircms.auth.api import require_login, get_or_404
from altaircms.page.models import Page
from . import forms

@view_defaults(custom_predicates=(require_login,))
class TicketlistWidgetView(object):
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

    @view_config(route_name="ticketlist_widget_create", renderer="json", request_method="POST")
    def create(self):
        return self._create_or_update()

    @view_config(route_name="ticketlist_widget_update", renderer="json", request_method="POST")
    def update(self):
        return self._create_or_update()

    @view_config(route_name="ticketlist_widget_delete", renderer="json", request_method="POST")
    def delete(self):
        context = self.request.context
        widget = context.get_widget(self.request.json_body["pk"])
        context.delete(widget, flush=True)
        return {"status": "ok"}

    @view_config(route_name="ticketlist_widget_dialog", renderer="altaircms.plugins.widget:ticketlist/dialog.html", request_method="GET")
    def dialog(self):
        context = self.request.context
        widget = context.get_widget(self.request.GET.get("pk"))
        page = get_or_404(self.request.allowable(Page), Page.id==self.request.GET["page_id"])
        self.request.event_id = page.event_id
        form = forms.TicketlistChoiceForm(**widget.to_dict())
        return {"widget": widget, "form": form}
