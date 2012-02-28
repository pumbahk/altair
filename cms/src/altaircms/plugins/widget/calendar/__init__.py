from altaircms.plugins.widget import widget_plugin_install
import os.path
DIR = os.path.dirname(os.path.abspath(__file__))

def includeme(config):
    from .models import CalendarWidget
    from .models import CalendarWidgetResource
    config.add_route("calendar_widget_create", "/widget/calendar/create", factory=CalendarWidgetResource)
    config.add_route("calendar_widget_delete", "/widget/calendar/delete", factory=CalendarWidgetResource)
    config.add_route("calendar_widget_update", "/widget/calendar/update", factory=CalendarWidgetResource)
    config.add_route("calendar_widget_dialog", "/widget/calendar/dialog", factory=CalendarWidgetResource)

    settings = {
        "model": CalendarWidget, 
        "name": CalendarWidget.type, 
        "jsfile": os.path.join(DIR, "lib.js"), 
        "cssfile": os.path.join(DIR, "lib.css"), 
        # "imgdirectory": os.path.join(DIR, "img")
        }
    widget_plugin_install(config, settings)
