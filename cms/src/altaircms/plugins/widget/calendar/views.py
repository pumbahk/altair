from pyramid.view import view_config

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

    @view_config(route_name="calendar_widget_dialog", renderer="altaircms.plugins.widget:calendar/dialog.mako", request_method="GET")
    def dialog(self):
        return {}
