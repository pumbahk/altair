from pyramid.view import view_config, view_defaults
from altaircms.auth.api import require_login
from . import demo
from forms import CalendarSelectForm
from altaircms.page.models import Page    
from altaircms.auth.api import get_or_404

@view_defaults(custom_predicates=(require_login,))
class CalendarWidgetView(object):
    def __init__(self, request):
        self.request = request

    def _create_or_update(self):
        page_id = self.request.json_body["page_id"]
        context = self.request.context
        widget = context.get_widget(self.request.json_body.get("pk"))
        params = self.request.json_body["data"]
        widget = context.update_data(widget,page_id=page_id, **params)
        context.add(widget, flush=True)

        r = self.request.json_body.copy()
        r.update(pk=widget.id)
        return r

    @view_config(route_name="calendar_widget_create", renderer="json", request_method="POST")
    def create(self):
        return self._create_or_update()

    @view_config(route_name="calendar_widget_update", renderer="json", request_method="POST")
    def update(self):
        return self._create_or_update()

    @view_config(route_name="calendar_widget_delete", renderer="json", request_method="POST")        
    def delete(self):
        context = self.request.context
        widget = context.get_widget(self.request.json_body["pk"])
        context.delete(widget, flush=True)
        return {"status": "ok"}


    DEFAULT_CALENDAR_TYPE = "this_month"
    @view_config(route_name="calendar_widget_dialog", renderer="altaircms.plugins.widget:calendar/dialog.mako", request_method="GET")
    def dialog(self):
        context = self.request.context
        widget = context.get_widget(self.request.GET.get("pk"))
        page = get_or_404(self.request.allowable(Page), Page.id==self.request.GET["page"])
        params = widget.to_dict()
        form = CalendarSelectForm(sale_choice=widget.salessegment, **params)
        form.configure(self.request, page)
        return {"form": form}


    @view_config(route_name="calendar_widget_dialog_demo", renderer="altaircms.plugins.widget:calendar/demo.mako", request_method="GET")
    def demo(self):
        calendar_type = self.request.matchdict["type"]
        D = {"calendar_type": calendar_type}
        D.update(getattr(demo, calendar_type)())

        if "form_class" in D:
            context = self.request.context
            widget = context.get_widget(self.request.GET.get("pk"))
            return context.attach_form_from_widget(D, widget)
        return D
