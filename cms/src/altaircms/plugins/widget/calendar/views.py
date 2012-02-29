from pyramid.view import view_config
from datetime import datetime
from . import demo

def _dict_to_object_params(data):
    params = {}
    params["calendar_type"] = data["calendar_type"]
    if data["from_date"] != u"":
        params["from_date"] = datetime.strptime(data["from_date"], "%Y/%m/%d").date()
    if data["to_date"] != u"":
        params["to_date"] = datetime.strptime(data["to_date"], "%Y/%m/%d").date()
    return params
    
class CalendarWidgetView(object):
    def __init__(self, request):
        self.request = request

    def _create_or_update(self):
        page_id = self.request.json_body["page_id"]
        context = self.request.context
        widget = context.get_widget(self.request.json_body.get("pk"))
        params = _dict_to_object_params(self.request.json_body["data"])
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

        form_class = self.request.context.get_select_form()
        form = form_class(**widget.to_dict())
        return {"form": form}

    @view_config(route_name="calendar_widget_dialog_demo", renderer="altaircms.plugins.widget:calendar/demo.mako", request_method="GET")
    def demo(self):
        calendar_type = self.request.matchdict["type"]
        demo_context = getattr(demo, calendar_type)()
        context = {"calendar_type": calendar_type}
        context.update(demo_context)
        return context

