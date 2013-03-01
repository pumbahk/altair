from altaircms.plugins.widget import widget_plugin_install
from zope.deprecation import deprecation
import os.path
DIR = os.path.dirname(os.path.abspath(__file__))

## fixme move to ini file
@deprecation.deprecate("this is deprecated class. define by [calendar] section in your organization settings.]")
class CalendarTemplatePathStore(object):
    obi = "ticketstar.calendar.html"
    term = "rakuten.calendar.html"
    tab = "ticketstar.tab-calendar.html"
    here = "altaircms.plugins.widget:calendar"
    @classmethod
    def path(cls, k):
        return os.path.join(cls.here, getattr(cls, k))

def includeme(config):
    config.add_widgetname("calendar")
    config.add_route("calendar_widget_create", "/widget/calendar/create", factory=".models.CalendarWidgetResource")
    config.add_route("calendar_widget_delete", "/widget/calendar/delete", factory=".models.CalendarWidgetResource")
    config.add_route("calendar_widget_update", "/widget/calendar/update", factory=".models.CalendarWidgetResource")
    config.add_route("calendar_widget_dialog", "/widget/calendar/dialog", factory=".models.CalendarWidgetResource")
    config.add_route("calendar_widget_dialog_demo", "/widget/calendar/dialog/demo/{type}", factory=".models.CalendarWidgetResource")

    api_impl = (config.maybe_dotted(".api.CalendarDataAPI")
                (config.registry.settings["altaircms.backend.url"], 
                 config.registry.settings["altaircms.backend.apikey"]))
    config.registry.registerUtility(api_impl, 
                                    config.maybe_dotted("altaircms.plugins.interfaces.IExternalAPI"), 
                                    api_impl.__class__.__name__)

    from .models import CalendarWidget
    settings = {
        "model": CalendarWidget, 
        "name": CalendarWidget.type, 
        "jsfile": os.path.join(DIR, "lib.js"), 
        "cssfile": os.path.join(DIR, "lib.css"), 
        # "imgdirectory": os.path.join(DIR, "img")
        }
    widget_plugin_install(config, settings)
    config.scan(".views")

