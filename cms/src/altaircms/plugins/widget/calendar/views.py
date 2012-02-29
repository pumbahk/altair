from pyramid.view import view_config
from altaircms.fanstatic import with_fanstatic_jqueries
from . import demo

class CalendarWidgetView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name="calendar_widget_create", renderer="json", request_method="POST")        
    def create(self):
        return {}

    @view_config(route_name="calendar_widget_update", renderer="json", request_method="POST")        
    def update(self):
        return {}

    @view_config(route_name="calendar_widget_delete", renderer="json", request_method="POST")        
    def delete(self):
        return {}

    @view_config(route_name="calendar_widget_dialog", renderer="altaircms.plugins.widget:calendar/dialog.mako", request_method="GET", 
                 decorator=with_fanstatic_jqueries)
    def dialog(self):
        form = self.request.context.get_select_form()
        return {"form": form}

    @view_config(route_name="calendar_widget_dialog_demo", renderer="altaircms.plugins.widget:calendar/demo.mako", request_method="GET", 
                 decorator=with_fanstatic_jqueries)
    def demo(self):
        calendar_type = self.request.matchdict["type"]
        renderable = getattr(demo, calendar_type)()
        return {"renderable": renderable, 
                "calendar_type": calendar_type}
