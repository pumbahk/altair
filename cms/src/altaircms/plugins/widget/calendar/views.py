from pyramid.view import view_config
from . import demo

class CalendarWidgetView(object):
    def __init__(self, request):
        self.request = request

    def _create_or_update(self):
        calendar_type = self.request.json_body["data"]["calendar_type"]
        page_id = self.request.json_body["page_id"]
        context = self.request.context
        widget = context.get_widget(self.request.json_body.get("pk"))
        widget = context.update_data(widget, calendar_type=calendar_type, page_id=page_id)
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

        form_class = self.request.context.get_select_form()
        calendar_type = widget.calendar_type
        form = form_class(calendar_type=calendar_type)
        return {"form": form}

    @view_config(route_name="calendar_widget_dialog_demo", renderer="altaircms.plugins.widget:calendar/demo.mako", request_method="GET")
    def demo(self):
        calendar_type = self.request.matchdict["type"]
        demo_context = getattr(demo, calendar_type)()
        context = {"calendar_type": calendar_type}
        context.update(demo_context)
        return context

