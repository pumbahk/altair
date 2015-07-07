from altaircms.plugins.widget import widget_plugin_install
import os.path
DIR = os.path.dirname(os.path.abspath(__file__))

def includeme(config):
    config.add_widgetname("lotsreview")
    from .models import LotsreviewWidget
    from .models import LotsreviewWidgetResource
    config.add_route("lotsreview_widget_create", "/widget/lotsreview/create", factory=LotsreviewWidgetResource)
    config.add_route("lotsreview_widget_delete", "/widget/lotsreview/delete", factory=LotsreviewWidgetResource)
    config.add_route("lotsreview_widget_update", "/widget/lotsreview/update", factory=LotsreviewWidgetResource)
    config.add_route("lotsreview_widget_dialog", "/widget/lotsreview/dialog", factory=LotsreviewWidgetResource)

    settings = {
        "model": LotsreviewWidget,
        "name": LotsreviewWidget.type,
        "jsfile": os.path.join(DIR, "lib.js"), 
        "cssfile": os.path.join(DIR, "lib.css"), 
        "imgdirectory": os.path.join(DIR, "img")
        }
    widget_plugin_install(config, settings)
    config.scan(".views")
