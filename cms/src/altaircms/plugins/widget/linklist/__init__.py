from altaircms.plugins.widget import widget_plugin_install
import os.path
DIR = os.path.dirname(os.path.abspath(__file__))

from .interfaces import IWFinder

def add_finder(config, finder, key=None):
    config.registry.registerUtility(config.maybe_dotted(finder), IWFinder, key)

def includeme(config):
    config.add_widgetname("linklist")
    from .models import LinklistWidget
    from .models import LinklistWidgetResource
    config.add_route("linklist_widget_create", "/widget/linklist/create", factory=LinklistWidgetResource)
    config.add_route("linklist_widget_delete", "/widget/linklist/delete", factory=LinklistWidgetResource)
    config.add_route("linklist_widget_update", "/widget/linklist/update", factory=LinklistWidgetResource)
    config.add_route("linklist_widget_dialog", "/widget/linklist/dialog", factory=LinklistWidgetResource)

    settings = {
        "model": LinklistWidget, 
        "name": LinklistWidget.type, 
        "jsfile": os.path.join(DIR, "lib.js"), 
        "cssfile": os.path.join(DIR, "lib.css"), 
        "imgdirectory": os.path.join(DIR, "img")
        }
    widget_plugin_install(config, settings)
    config.scan(".views")
    add_finder(config, ".api.near_the_end_events", key="nearTheEnd")
    add_finder(config, ".api.deal_start_this_week_events", key="thisWeek")
