from altaircms.plugins.widget import widget_plugin_install
import os.path
DIR = os.path.dirname(os.path.abspath(__file__))

## fixme move to ini file
class CalendarTemplatePathStore(object):
    #obi = "rakuten.calendar.mako"
    obi = "ticketstar.calendar.mako"
    term = "rakuten.calendar.mako"
    # tab = "rakuten.tab-calendar.mako"
    tab = "ticketstar.tab-calendar.mako"
    here = "altaircms.plugins.widget:calendar"
    @classmethod
    def path(cls, k):
        return os.path.join(cls.here, getattr(cls, k))

def includeme(config):
    from .models import CalendarWidget
    from .models import CalendarWidgetResource
    config.add_route("calendar_widget_create", "/widget/calendar/create", factory=CalendarWidgetResource)
    config.add_route("calendar_widget_delete", "/widget/calendar/delete", factory=CalendarWidgetResource)
    config.add_route("calendar_widget_update", "/widget/calendar/update", factory=CalendarWidgetResource)
    config.add_route("calendar_widget_dialog", "/widget/calendar/dialog", factory=CalendarWidgetResource)
    config.add_route("calendar_widget_dialog_demo", "/widget/calendar/dialog/demo/{type}", factory=CalendarWidgetResource)

    settings = {
        "model": CalendarWidget, 
        "name": CalendarWidget.type, 
        "jsfile": os.path.join(DIR, "lib.js"), 
        "cssfile": os.path.join(DIR, "lib.css"), 
        # "imgdirectory": os.path.join(DIR, "img")
        }
    widget_plugin_install(config, settings)
    config.scan(".views")

